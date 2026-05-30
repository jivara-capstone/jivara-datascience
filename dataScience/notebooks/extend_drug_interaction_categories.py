"""
Extend drug-food interaction categories.

Tujuan:
- Menambahkan drug_category baru ke drug_food_interactions.csv.
- Menjaga bentuk tabel tetap konsisten: setiap food_class harus punya satu baris
  untuk setiap drug_category.
- Mendokumentasikan alasan penambahan kategori dan ringkasan hasilnya.

Kategori baru:
- kortikosteroid
- dopaminergik_parkinson
- diuretik_hemat_kalium

Alasan:
- Beberapa zat aktif kortikosteroid muncul tinggi pada unmatched output
  generate_drug_product_category_mapping.py, misalnya METHYLPREDNISOLONE dan
  DEXAMETHASONE.
- Secara klinis, kortikosteroid dapat memperburuk hiperglikemia dan retensi
  cairan/tekanan darah. Karena ingredient mapping makanan di project ini punya
  bahan gula dan kecap asin, kategori ini bisa diberi aturan interaksi yang
  deterministik.
- Levodopa/carbidopa masih belum terpetakan dan punya interaksi dengan makanan
  tinggi protein yang ingredient-nya sudah ada di JSON.
- Spironolactone masih belum terpetakan dan punya risiko dengan bahan tinggi
  kalium yang ingredient-nya sudah ada di JSON.

Catatan penting:
- Ini bukan pengganti validasi farmakologi klinis. Output dibuat sebagai basis
  awal dataset dan tetap perlu review domain expert bila dipakai untuk advice
  medis.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data_output" / "processed"
DOCS_DIR = ROOT / "data_output" / "docs"
AI_ENGINEER_DIR = ROOT / "data_output" / "for_ai_engineer"

FOOD_INGREDIENT_MAPPING_PATH = PROCESSED_DIR / "food_ingredient_mapping.csv"
FOOD_TO_INGREDIENT_JSON_PATH = AI_ENGINEER_DIR / "food_to_ingredient_kb.json"
INTERACTIONS_PATH = PROCESSED_DIR / "drug_food_interactions.csv"
REPORT_PATH = DOCS_DIR / "drug_category_extension_added_categories.md"

NEW_CATEGORIES = {
    "kortikosteroid",
    "dopaminergik_parkinson",
    "diuretik_hemat_kalium",
}
SOURCE_LABEL = "deterministic extension from BPOM active ingredient gap analysis"

SUGAR_INGREDIENTS = {
    "gula pasir",
    "gula merah",
    "gula aren",
    "gula jawa",
    "gula halus",
    "madu",
    "honey",
    "susu kental manis",
    "kental manis",
}
SODIUM_INGREDIENTS = {
    "kecap asin",
}
HIGH_PROTEIN_INGREDIENTS = {
    "ayam",
    "ayam fillet",
    "bakso",
    "bakso sapi",
    "dada ayam",
    "dada ayam fillet",
    "daging ayam",
    "daging giling",
    "daging sapi",
    "ebi",
    "ebi sangrai",
    "ikan mas",
    "kacang tanah",
    "kacang tanah goreng",
    "keju",
    "keju cheddar",
    "keju mozzarella",
    "sosis",
    "susu bubuk",
    "susu cair",
    "susu cair dingin",
    "susu full cream / uht",
    "susu kental manis",
    "tahu",
    "tahu goreng",
    "tahu kuning",
    "tahu putih",
    "telur",
    "telur puyuh",
    "telur rebus",
    "tempe",
    "tempe goreng",
    "udang",
}
HIGH_POTASSIUM_INGREDIENTS = {
    "air kelapa muda",
    "bayam",
    "kangkung",
    "kangkung rebus",
    "kentang",
    "kentang agak besar",
    "kentang ukuran sedang",
    "kiwi",
    "labu kuning",
    "pisang",
    "pisang kepok",
    "tomat",
    "tomat ukuran besar",
    "ubi jalar",
}


@dataclass(frozen=True)
class InteractionDecision:
    has_interaction: int
    severity: int
    interaction_type: str
    mechanism: str
    matched_ingredients: str


def split_ingredients(value: object) -> list[str]:
    if pd.isna(value):
        return []

    return [
        ingredient.strip().lower()
        for ingredient in str(value).split(",")
        if ingredient.strip()
    ]


def load_food_ingredient_mapping() -> pd.DataFrame:
    if FOOD_TO_INGREDIENT_JSON_PATH.exists():
        with FOOD_TO_INGREDIENT_JSON_PATH.open(encoding="utf-8") as file_handle:
            payload = json.load(file_handle)

        rows = [
            {
                "Kelas_YOLO": food_class,
                "ingredients": [ingredient.lower() for ingredient in ingredients],
            }
            for food_class, ingredients in payload["food_to_ingredients"].items()
        ]
        return pd.DataFrame(rows)

    food_ingredient_mapping = pd.read_csv(FOOD_INGREDIENT_MAPPING_PATH)
    food_ingredient_mapping["ingredients"] = food_ingredient_mapping["Bahan_Penyusun"].apply(split_ingredients)
    return food_ingredient_mapping[["Kelas_YOLO", "ingredients"]]


def decide_kortikosteroid_interaction(ingredients: list[str]) -> InteractionDecision:
    matched_sugar = sorted(set(ingredients).intersection(SUGAR_INGREDIENTS))
    matched_sodium = sorted(set(ingredients).intersection(SODIUM_INGREDIENTS))
    matched = matched_sugar + matched_sodium

    if matched_sugar and matched_sodium:
        return InteractionDecision(
            has_interaction=1,
            severity=4,
            interaction_type="pharmacodynamic",
            mechanism=(
                "Gula tinggi dapat memperburuk hiperglikemia terkait kortikosteroid, "
                "sedangkan natrium tinggi dapat memperburuk retensi cairan dan tekanan darah."
            ),
            matched_ingredients="|".join(matched),
        )

    if matched_sugar:
        return InteractionDecision(
            has_interaction=1,
            severity=3,
            interaction_type="pharmacodynamic",
            mechanism=(
                "Gula tinggi dapat memperburuk hiperglikemia yang dapat muncul saat "
                "menggunakan kortikosteroid."
            ),
            matched_ingredients="|".join(matched_sugar),
        )

    if matched_sodium:
        return InteractionDecision(
            has_interaction=1,
            severity=3,
            interaction_type="pharmacodynamic",
            mechanism=(
                "Natrium tinggi dapat memperburuk retensi cairan dan peningkatan tekanan "
                "darah yang dapat terjadi pada penggunaan kortikosteroid."
            ),
            matched_ingredients="|".join(matched_sodium),
        )

    return InteractionDecision(
        has_interaction=0,
        severity=0,
        interaction_type="",
        mechanism="",
        matched_ingredients="",
    )


def decide_dopaminergik_parkinson_interaction(ingredients: list[str]) -> InteractionDecision:
    matched_protein = sorted(set(ingredients).intersection(HIGH_PROTEIN_INGREDIENTS))

    if matched_protein:
        return InteractionDecision(
            has_interaction=1,
            severity=3,
            interaction_type="pharmacokinetic",
            mechanism=(
                "Makanan tinggi protein dapat mengganggu absorpsi dan transport levodopa, "
                "sehingga efek obat Parkinson dapat berkurang."
            ),
            matched_ingredients="|".join(matched_protein),
        )

    return InteractionDecision(
        has_interaction=0,
        severity=0,
        interaction_type="",
        mechanism="",
        matched_ingredients="",
    )


def decide_diuretik_hemat_kalium_interaction(ingredients: list[str]) -> InteractionDecision:
    matched_potassium = sorted(set(ingredients).intersection(HIGH_POTASSIUM_INGREDIENTS))

    if matched_potassium:
        return InteractionDecision(
            has_interaction=1,
            severity=4,
            interaction_type="pharmacodynamic",
            mechanism=(
                "Bahan tinggi kalium dapat meningkatkan risiko hiperkalemia pada penggunaan "
                "diuretik hemat kalium seperti spironolactone."
            ),
            matched_ingredients="|".join(matched_potassium),
        )

    return InteractionDecision(
        has_interaction=0,
        severity=0,
        interaction_type="",
        mechanism="",
        matched_ingredients="",
    )


CATEGORY_DECISION_FUNCTIONS = {
    "kortikosteroid": decide_kortikosteroid_interaction,
    "dopaminergik_parkinson": decide_dopaminergik_parkinson_interaction,
    "diuretik_hemat_kalium": decide_diuretik_hemat_kalium_interaction,
}


def build_new_category_rows(food_ingredient_mapping: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for record in food_ingredient_mapping.to_dict("records"):
        ingredients = record["ingredients"]

        for category, decision_function in CATEGORY_DECISION_FUNCTIONS.items():
            decision = decision_function(ingredients)
            rows.append(
                {
                    "food_class": record["Kelas_YOLO"],
                    "drug_category": category,
                    "has_interaction": decision.has_interaction,
                    "severity": decision.severity,
                    "interaction_type": decision.interaction_type,
                    "mechanism": decision.mechanism,
                    "matched_ingredients": decision.matched_ingredients,
                    "source": SOURCE_LABEL,
                }
            )

    return pd.DataFrame(rows)


def update_interaction_table(interactions: pd.DataFrame, new_rows: pd.DataFrame) -> pd.DataFrame:
    base_interactions = interactions[~interactions["drug_category"].isin(NEW_CATEGORIES)].copy()
    updated_interactions = pd.concat([base_interactions, new_rows], ignore_index=True)

    return (
        updated_interactions
        .sort_values(["food_class", "drug_category"])
        .reset_index(drop=True)
    )


def validate_interaction_grid(interactions: pd.DataFrame) -> None:
    category_count = interactions["drug_category"].nunique()
    expected_rows_per_food = category_count
    rows_per_food = interactions.groupby("food_class")["drug_category"].nunique()

    invalid_foods = rows_per_food[rows_per_food != expected_rows_per_food]
    if not invalid_foods.empty:
        raise ValueError(
            "Setiap food_class harus punya baris untuk semua drug_category. "
            f"Food invalid: {invalid_foods.to_dict()}"
        )

    duplicate_rows = interactions.duplicated(subset=["food_class", "drug_category"]).sum()
    if duplicate_rows:
        raise ValueError(f"Ditemukan duplikasi food_class + drug_category: {duplicate_rows}")


def write_report(updated_interactions: pd.DataFrame, new_rows: pd.DataFrame) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    interacted_rows = new_rows[new_rows["has_interaction"] == 1].copy()
    category_summary = (
        new_rows
        .groupby("drug_category")
        .agg(
            total_rows=("food_class", "count"),
            food_with_interaction=("has_interaction", "sum"),
        )
        .assign(food_without_interaction=lambda data: data["total_rows"] - data["food_with_interaction"])
    )

    matched_ingredient_summary = {}
    for category, category_rows in interacted_rows.groupby("drug_category"):
        matched_ingredient_summary[category] = (
            category_rows["matched_ingredients"]
            .str.split("|")
            .explode()
            .loc[lambda series: series.ne("")]
            .value_counts()
        )

    matched_ingredient_text = []
    for category in sorted(CATEGORY_DECISION_FUNCTIONS):
        values = matched_ingredient_summary.get(category, pd.Series(dtype="int64"))
        summary = values.to_string() if not values.empty else "Tidak ada bahan pemicu."
        matched_ingredient_text.append(f"### {category}\n\n{summary}")

    report = f"""# Dokumentasi Penambahan Drug Category Baru

## Ringkasan

Kategori berikut ditambahkan/di-refresh di `drug_food_interactions.csv` dan
aturan zat aktifnya ditambahkan ke `generate_drug_product_category_mapping.py`:

{chr(10).join(f'- `{category}`' for category in sorted(CATEGORY_DECISION_FUNCTIONS))}

## Alasan Penambahan

- `kortikosteroid`: zat aktif seperti `METHYLPREDNISOLONE` dan `DEXAMETHASONE`
  muncul besar pada data yang sebelumnya belum terpetakan.
- `dopaminergik_parkinson`: zat aktif `LEVODOPA`/`CARBIDOPA` ada di unmatched
  dan bahan tinggi protein tersedia di JSON ingredient.
- `diuretik_hemat_kalium`: zat aktif `SPIRONOLACTONE` ada di unmatched dan bahan
  tinggi kalium tersedia di JSON ingredient.

## Aturan Interaksi Makanan

- `kortikosteroid`
  - Bahan tinggi gula: `{', '.join(sorted(SUGAR_INGREDIENTS))}`
  - Bahan tinggi natrium: `{', '.join(sorted(SODIUM_INGREDIENTS))}`
  - Gula + natrium: `severity = 4`
  - Hanya gula atau hanya natrium: `severity = 3`
- `dopaminergik_parkinson`
  - Bahan tinggi protein dari JSON: `{', '.join(sorted(HIGH_PROTEIN_INGREDIENTS))}`
  - Jika ada bahan tinggi protein: `severity = 3`
- `diuretik_hemat_kalium`
  - Bahan tinggi kalium dari JSON: `{', '.join(sorted(HIGH_POTASSIUM_INGREDIENTS))}`
  - Jika ada bahan tinggi kalium: `severity = 4`

## Hasil Update

- Total food class: {updated_interactions['food_class'].nunique():,}
- Total drug category: {updated_interactions['drug_category'].nunique():,}
- Total baris interaction table: {len(updated_interactions):,}
- Baris kategori baru/refresh: {len(new_rows):,}

## Summary per Kategori

{category_summary.to_string()}

## Top Matched Ingredients per Kategori

{chr(10).join(matched_ingredient_text)}

## Output yang Diubah

- `data_output/processed/drug_food_interactions.csv`
- `data_output/processed/drug_active_category_map.csv`
- `data_output/processed/drug_product_category_mapping.csv`
- `data_output/processed/drug_product_category_mapping_unmatched.csv`
- `data_output/processed/drug_name_category_lookup.csv`

## Catatan

Ini adalah rule-based extension untuk dataset. Hasilnya perlu review domain
expert sebelum dipakai sebagai rekomendasi klinis.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    food_ingredient_mapping = load_food_ingredient_mapping()
    interactions = pd.read_csv(INTERACTIONS_PATH)

    new_rows = build_new_category_rows(food_ingredient_mapping)
    updated_interactions = update_interaction_table(interactions, new_rows)
    validate_interaction_grid(updated_interactions)

    updated_interactions.to_csv(INTERACTIONS_PATH, index=False)
    write_report(updated_interactions, new_rows)

    print(f"Updated: {INTERACTIONS_PATH}")
    print(f"Report:  {REPORT_PATH}")
    print(f"Rows added/replaced for {len(CATEGORY_DECISION_FUNCTIONS)} categories: {len(new_rows):,}")
    print(f"Categories now: {updated_interactions['drug_category'].nunique():,}")
    print(f"Total rows now: {len(updated_interactions):,}")
    print("\nNew category interaction summary:")
    print(
        new_rows
        .groupby("drug_category")["has_interaction"]
        .value_counts()
        .rename(index={0: "no", 1: "yes"})
        .to_string()
    )


if __name__ == "__main__":
    main()
