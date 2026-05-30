"""
Generate mapping from BPOM drug products to drug_food_interactions drug_category.

Input:
- data_output/processed/lookup_zat_aktif.csv
- data_output/processed/drug_food_interactions.csv

Output:
- data_output/processed/drug_active_category_map.csv
- data_output/processed/drug_product_category_mapping.csv
- data_output/processed/drug_product_category_mapping_unmatched.csv

The mapping is intentionally based on active ingredients, not BPOM regulatory
classes such as "Obat Keras" or "Obat Bebas".
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data_output" / "processed"

LOOKUP_ZAT_AKTIF_PATH = PROCESSED_DIR / "lookup_zat_aktif.csv"
INTERACTIONS_PATH = PROCESSED_DIR / "drug_food_interactions.csv"

ACTIVE_CATEGORY_MAP_PATH = PROCESSED_DIR / "drug_active_category_map.csv"
PRODUCT_CATEGORY_MAPPING_PATH = PROCESSED_DIR / "drug_product_category_mapping.csv"
UNMATCHED_PATH = PROCESSED_DIR / "drug_product_category_mapping_unmatched.csv"
NAME_CATEGORY_LOOKUP_PATH = PROCESSED_DIR / "drug_name_category_lookup.csv"

SOURCE_LABEL = "curated_rule"


ACTIVE_CATEGORY_RULES = [
    # Anticoagulants
    ("antikoagulan", "WARFARIN", "oral vitamin K antagonist"),
    ("antikoagulan", "RIVAROXABAN", "direct factor Xa inhibitor"),
    ("antikoagulan", "APIXABAN", "direct factor Xa inhibitor"),
    ("antikoagulan", "DABIGATRAN", "direct thrombin inhibitor"),
    ("antikoagulan", "HEPARIN", "heparin anticoagulant"),
    ("antikoagulan", "ENOXAPARIN", "low molecular weight heparin"),
    ("antikoagulan", "FONDAPARINUX", "factor Xa inhibitor"),

    # Antidiabetics
    ("antidiabetes", "METFORMIN", "biguanide antidiabetic"),
    ("antidiabetes", "INSULIN", "insulin antidiabetic"),
    ("antidiabetes", "GLIMEPIRIDE", "sulfonylurea antidiabetic"),
    ("antidiabetes", "GLICLAZIDE", "sulfonylurea antidiabetic"),
    ("antidiabetes", "GLIBENCLAMIDE", "sulfonylurea antidiabetic"),
    ("antidiabetes", "GLIPIZIDE", "sulfonylurea antidiabetic"),
    ("antidiabetes", "ACARBOSE", "alpha-glucosidase inhibitor"),
    ("antidiabetes", "EMPAGLIFLOZIN", "SGLT2 inhibitor"),
    ("antidiabetes", "DAPAGLIFLOZIN", "SGLT2 inhibitor"),
    ("antidiabetes", "SITAGLIPTIN", "DPP-4 inhibitor"),
    ("antidiabetes", "LINAGLIPTIN", "DPP-4 inhibitor"),
    ("antidiabetes", "PIOGLITAZONE", "thiazolidinedione antidiabetic"),

    # ACE inhibitors / ARBs
    ("ace_arb", "CAPTOPRIL", "ACE inhibitor"),
    ("ace_arb", "LISINOPRIL", "ACE inhibitor"),
    ("ace_arb", "RAMIPRIL", "ACE inhibitor"),
    ("ace_arb", "IMIDAPRIL", "ACE inhibitor"),
    ("ace_arb", "ENALAPRIL", "ACE inhibitor"),
    ("ace_arb", "VALSARTAN", "ARB"),
    ("ace_arb", "CANDESARTAN", "ARB"),
    ("ace_arb", "LOSARTAN", "ARB"),
    ("ace_arb", "TELMISARTAN", "ARB"),
    ("ace_arb", "IRBESARTAN", "ARB"),
    ("ace_arb", "OLMESARTAN", "ARB"),

    # Calcium channel blockers
    ("ccb", "AMLODIPINE", "calcium channel blocker"),
    ("ccb", "NIFEDIPINE", "calcium channel blocker"),
    ("ccb", "DILTIAZEM", "calcium channel blocker"),
    ("ccb", "VERAPAMIL", "calcium channel blocker"),
    ("ccb", "LERCANIDIPINE", "calcium channel blocker"),

    # Statins
    ("statin", "SIMVASTATIN", "HMG-CoA reductase inhibitor"),
    ("statin", "ATORVASTATIN", "HMG-CoA reductase inhibitor"),
    ("statin", "ROSUVASTATIN", "HMG-CoA reductase inhibitor"),
    ("statin", "PRAVASTATIN", "HMG-CoA reductase inhibitor"),
    ("statin", "PITAVASTATIN", "HMG-CoA reductase inhibitor"),
    ("statin", "FLUVASTATIN", "HMG-CoA reductase inhibitor"),

    # Tetracycline antibiotics
    ("antibiotik_tetrasiklin", "TETRACYCLINE", "tetracycline-class antibiotic"),
    ("antibiotik_tetrasiklin", "TETRASIKLIN", "tetracycline-class antibiotic"),
    ("antibiotik_tetrasiklin", "DOXYCYCLINE", "tetracycline-class antibiotic"),
    ("antibiotik_tetrasiklin", "DOKSISIKLIN", "tetracycline-class antibiotic"),
    ("antibiotik_tetrasiklin", "MINOCYCLINE", "tetracycline-class antibiotic"),

    # Fluoroquinolone antibiotics
    ("antibiotik_fluorokuinolon", "CIPROFLOXACIN", "fluoroquinolone antibiotic"),
    ("antibiotik_fluorokuinolon", "LEVOFLOXACIN", "fluoroquinolone antibiotic"),
    ("antibiotik_fluorokuinolon", "MOXIFLOXACIN", "fluoroquinolone antibiotic"),
    ("antibiotik_fluorokuinolon", "OFLOXACIN", "fluoroquinolone antibiotic"),
    ("antibiotik_fluorokuinolon", "NORFLOXACIN", "fluoroquinolone antibiotic"),

    # MAO inhibitors
    ("maoi", "SELEGILINE", "monoamine oxidase inhibitor"),
    ("maoi", "MOCLOBEMIDE", "monoamine oxidase inhibitor"),
    ("maoi", "PHENELZINE", "monoamine oxidase inhibitor"),

    # Thyroid drugs
    ("tiroid", "LEVOTHYROXINE", "thyroid hormone"),
    ("tiroid", "LEVOTIROKSIN", "thyroid hormone"),
    ("tiroid", "THIAMAZOLE", "antithyroid drug"),
    ("tiroid", "METHIMAZOLE", "antithyroid drug"),
    ("tiroid", "PROPYLTHIOURACIL", "antithyroid drug"),

    # NSAIDs
    ("nsaid", "IBUPROFEN", "NSAID"),
    ("nsaid", "DICLOFENAC", "NSAID"),
    ("nsaid", "MEFENAMIC", "NSAID"),
    ("nsaid", "KETOROLAC", "NSAID"),
    ("nsaid", "NAPROXEN", "NSAID"),
    ("nsaid", "ACETYLSALICYLIC", "NSAID/aspirin"),
    ("nsaid", "ASPIRIN", "NSAID/aspirin"),
    ("nsaid", "PIROXICAM", "NSAID"),
    ("nsaid", "MELOXICAM", "NSAID"),
    ("nsaid", "CELECOXIB", "NSAID"),
    ("nsaid", "ETORICOXIB", "NSAID"),
    ("nsaid", "DEXKETOPROFEN", "NSAID"),
    ("nsaid", "KETOPROFEN", "NSAID"),
    ("nsaid", "NABUMETONE", "NSAID"),

    # Anticonvulsants
    ("antikonvulsan", "PHENYTOIN", "anticonvulsant"),
    ("antikonvulsan", "FENITOIN", "anticonvulsant"),
    ("antikonvulsan", "CARBAMAZEPINE", "anticonvulsant"),
    ("antikonvulsan", "KARBAMAZEPIN", "anticonvulsant"),
    ("antikonvulsan", "VALPROATE", "anticonvulsant"),
    ("antikonvulsan", "VALPROIC", "anticonvulsant"),
    ("antikonvulsan", "LEVETIRACETAM", "anticonvulsant"),
    ("antikonvulsan", "LAMOTRIGINE", "anticonvulsant"),
    ("antikonvulsan", "TOPIRAMATE", "anticonvulsant"),
    ("antikonvulsan", "GABAPENTIN", "anticonvulsant"),
    ("antikonvulsan", "PREGABALIN", "anticonvulsant"),

    # Cardiac glycosides
    ("glikosida_jantung", "DIGOXIN", "cardiac glycoside"),

    # Xanthines
    ("xantin", "THEOPHYLLINE", "xanthine bronchodilator"),
    ("xantin", "TEOFILIN", "xanthine bronchodilator"),
    ("xantin", "AMINOPHYLLINE", "xanthine bronchodilator"),
    ("xantin", "AMINOFILIN", "xanthine bronchodilator"),
    ("xantin", "CAFFEINE", "xanthine stimulant"),
    ("xantin", "KAFEIN", "xanthine stimulant"),

    # Immunosuppressants
    ("imunosupresan", "TACROLIMUS", "immunosuppressant"),
    ("imunosupresan", "CYCLOSPORINE", "immunosuppressant"),
    ("imunosupresan", "CICLOSPORIN", "immunosuppressant"),
    ("imunosupresan", "SIROLIMUS", "immunosuppressant"),
    ("imunosupresan", "MYCOPHENOLATE", "immunosuppressant"),
    ("imunosupresan", "MIKOFENOLAT", "immunosuppressant"),
    ("imunosupresan", "AZATHIOPRINE", "immunosuppressant"),
    ("imunosupresan", "METHOTREXATE", "immunosuppressant"),

    # Corticosteroids
    ("kortikosteroid", "METHYLPREDNISOLONE", "systemic corticosteroid"),
    ("kortikosteroid", "METILPREDNISOLON", "systemic corticosteroid"),
    ("kortikosteroid", "DEXAMETHASONE", "systemic corticosteroid"),
    ("kortikosteroid", "DEKSAMETASON", "systemic corticosteroid"),
    ("kortikosteroid", "PREDNISONE", "systemic corticosteroid"),
    ("kortikosteroid", "PREDNISON", "systemic corticosteroid"),
    ("kortikosteroid", "PREDNISOLONE", "systemic corticosteroid"),
    ("kortikosteroid", "PREDNISOLON", "systemic corticosteroid"),
    ("kortikosteroid", "HYDROCORTISONE", "corticosteroid"),
    ("kortikosteroid", "HIDROKORTISON", "corticosteroid"),
    ("kortikosteroid", "BETAMETHASONE", "corticosteroid"),
    ("kortikosteroid", "BETAMETASON", "corticosteroid"),
    ("kortikosteroid", "TRIAMCINOLONE", "corticosteroid"),
    ("kortikosteroid", "TRIAMSINOLON", "corticosteroid"),
    ("kortikosteroid", "MOMETASONE", "corticosteroid"),
    ("kortikosteroid", "MOMETASON", "corticosteroid"),
    ("kortikosteroid", "FLUTICASONE", "corticosteroid"),
    ("kortikosteroid", "FLUTIKASON", "corticosteroid"),
    ("kortikosteroid", "BUDESONIDE", "corticosteroid"),
    ("kortikosteroid", "BUDESONID", "corticosteroid"),

    # Dopaminergic Parkinson drugs
    ("dopaminergik_parkinson", "LEVODOPA", "dopaminergic Parkinson therapy"),
    ("dopaminergik_parkinson", "CARBIDOPA", "dopaminergic Parkinson therapy adjunct"),
    ("dopaminergik_parkinson", "BENSERAZIDE", "dopaminergic Parkinson therapy adjunct"),

    # Potassium-sparing diuretics
    ("diuretik_hemat_kalium", "SPIRONOLACTONE", "potassium-sparing diuretic"),
    ("diuretik_hemat_kalium", "SPIRONOLAKTON", "potassium-sparing diuretic"),
    ("diuretik_hemat_kalium", "EPLERENONE", "potassium-sparing diuretic"),
    ("diuretik_hemat_kalium", "AMILORIDE", "potassium-sparing diuretic"),
    ("diuretik_hemat_kalium", "TRIAMTERENE", "potassium-sparing diuretic"),
]


def normalize_text(value: object) -> str:
    """Normalize BPOM text for deterministic substring matching."""
    if pd.isna(value):
        return ""

    text = str(value).upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_pattern(active_norm: str, pattern_norm: str) -> bool:
    """Match pattern as a token sequence, allowing salts after the active name."""
    if not active_norm or not pattern_norm:
        return False
    return re.search(rf"(?<![A-Z0-9]){re.escape(pattern_norm)}(?![A-Z0-9])", active_norm) is not None


def build_active_category_map(valid_categories: set[str]) -> pd.DataFrame:
    rows = []
    for category, pattern, notes in ACTIVE_CATEGORY_RULES:
        if category not in valid_categories:
            raise ValueError(f"Unknown drug_category in mapping rules: {category}")

        rows.append(
            {
                "drug_category": category,
                "zat_aktif_pattern": pattern,
                "zat_aktif_pattern_norm": normalize_text(pattern),
                "match_type": "token_substring",
                "source": SOURCE_LABEL,
                "notes": notes,
            }
        )

    return (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["drug_category", "zat_aktif_pattern_norm"])
        .sort_values(["drug_category", "zat_aktif_pattern"])
        .reset_index(drop=True)
    )


def build_product_mapping(lookup_df: pd.DataFrame, active_map: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    lookup = lookup_df.copy()
    lookup["Nama Produk"] = lookup["Nama Produk"].astype(str).str.strip()
    lookup["Zat_Aktif"] = lookup["Zat_Aktif"].fillna("").astype(str).str.strip()
    lookup["product_name_norm"] = lookup["Nama Produk"].apply(normalize_text)
    lookup["zat_aktif_norm"] = lookup["Zat_Aktif"].apply(normalize_text)

    matched_rows = []
    unmatched_rows = []

    for record in lookup.to_dict("records"):
        matches = []
        for rule in active_map.to_dict("records"):
            if contains_pattern(record["zat_aktif_norm"], rule["zat_aktif_pattern_norm"]):
                matches.append(rule)

        if matches:
            for rule in matches:
                matched_rows.append(
                    {
                        "Nomor Registrasi": record["Nomor Registrasi"],
                        "Nama Produk": record["Nama Produk"],
                        "product_name_norm": record["product_name_norm"],
                        "Zat_Aktif": record["Zat_Aktif"],
                        "zat_aktif_norm": record["zat_aktif_norm"],
                        "drug_category": rule["drug_category"],
                        "match_pattern": rule["zat_aktif_pattern"],
                        "match_type": rule["match_type"],
                        "source": rule["source"],
                    }
                )
        elif record["zat_aktif_norm"]:
            unmatched_rows.append(
                {
                    "Nomor Registrasi": record["Nomor Registrasi"],
                    "Nama Produk": record["Nama Produk"],
                    "product_name_norm": record["product_name_norm"],
                    "Zat_Aktif": record["Zat_Aktif"],
                    "zat_aktif_norm": record["zat_aktif_norm"],
                    "reason": "no_curated_drug_category_match",
                }
            )

    product_mapping = pd.DataFrame(matched_rows)
    if not product_mapping.empty:
        product_mapping = (
            product_mapping
            .drop_duplicates(
                subset=[
                    "Nomor Registrasi",
                    "Nama Produk",
                    "Zat_Aktif",
                    "drug_category",
                    "match_pattern",
                ]
            )
            .sort_values(["Nama Produk", "Nomor Registrasi", "drug_category", "match_pattern"])
            .reset_index(drop=True)
        )

    unmatched = pd.DataFrame(unmatched_rows)
    if not unmatched.empty:
        unmatched = (
            unmatched
            .drop_duplicates(subset=["Nomor Registrasi", "Nama Produk", "Zat_Aktif"])
            .sort_values(["Nama Produk", "Nomor Registrasi", "Zat_Aktif"])
            .reset_index(drop=True)
        )

    return product_mapping, unmatched


def build_name_category_lookup(product_mapping: pd.DataFrame, active_map: pd.DataFrame) -> pd.DataFrame:
    """Build backend-friendly lookup for product names and generic active aliases."""
    product_lookup = (
        product_mapping
        .groupby(["Nama Produk", "product_name_norm", "drug_category"], as_index=False)
        .agg(
            lookup_type=("Nama Produk", lambda _s: "product"),
            match_pattern=("match_pattern", lambda s: " | ".join(sorted(set(s)))),
            source=("source", "first"),
            nomor_registrasi=("Nomor Registrasi", lambda s: " | ".join(sorted(set(s)))),
            zat_aktif=("Zat_Aktif", lambda s: " | ".join(sorted(set(s)))),
        )
        .rename(columns={"Nama Produk": "lookup_name", "product_name_norm": "lookup_name_norm"})
    )

    active_lookup = active_map.rename(
        columns={
            "zat_aktif_pattern": "lookup_name",
            "zat_aktif_pattern_norm": "lookup_name_norm",
        }
    ).copy()
    active_lookup["lookup_type"] = "active_alias"
    active_lookup["match_pattern"] = active_lookup["lookup_name"]
    active_lookup["nomor_registrasi"] = ""
    active_lookup["zat_aktif"] = active_lookup["lookup_name"]
    active_lookup = active_lookup[
        [
            "lookup_name",
            "lookup_name_norm",
            "drug_category",
            "lookup_type",
            "match_pattern",
            "source",
            "nomor_registrasi",
            "zat_aktif",
        ]
    ]

    lookup = pd.concat(
        [
            product_lookup[
                [
                    "lookup_name",
                    "lookup_name_norm",
                    "drug_category",
                    "lookup_type",
                    "match_pattern",
                    "source",
                    "nomor_registrasi",
                    "zat_aktif",
                ]
            ],
            active_lookup,
        ],
        ignore_index=True,
    )

    return (
        lookup
        .drop_duplicates(subset=["lookup_name_norm", "drug_category", "lookup_type"])
        .sort_values(["lookup_name_norm", "lookup_type", "drug_category"])
        .reset_index(drop=True)
    )


def assert_expected_examples(product_mapping: pd.DataFrame) -> None:
    by_product = (
        product_mapping.groupby("product_name_norm")["drug_category"]
        .apply(set)
        .to_dict()
    )

    def categories_for_input(user_input: str) -> set[str]:
        """Resolve exact product name first, then generic active-name alias."""
        input_norm = normalize_text(user_input)
        product_categories = by_product.get(input_norm, set())
        if product_categories:
            return product_categories

        categories = set()
        for category, pattern, _notes in ACTIVE_CATEGORY_RULES:
            if contains_pattern(input_norm, normalize_text(pattern)):
                categories.add(category)
        return categories

    examples = {
        "ZOCOR": {"statin"},
        "SIMVASTATIN": {"statin"},
        "METFORMIN": {"antidiabetes"},
        "AMLODIPINE": {"ccb"},
        "WARFARIN": {"antikoagulan"},
        "METHYLPREDNISOLONE": {"kortikosteroid"},
        "DEXAMETHASONE": {"kortikosteroid"},
        "LEVODOPA": {"dopaminergik_parkinson"},
        "SPIRONOLACTONE": {"diuretik_hemat_kalium"},
    }

    for product_name, expected_categories in examples.items():
        categories = categories_for_input(product_name)
        if not expected_categories.issubset(categories):
            raise AssertionError(
                f"{product_name} expected {expected_categories}, got {categories or 'NO MATCH'}"
            )

    negative_examples = ["DUMIN", "PARACETAMOL"]
    for product_name in negative_examples:
        categories = categories_for_input(product_name)
        if categories:
            raise AssertionError(f"{product_name} should not match interaction categories, got {categories}")

    poldan = by_product.get(normalize_text("POLDAN MIG"), set())
    if not {"nsaid", "xantin"}.issubset(poldan):
        raise AssertionError(f"POLDAN MIG expected nsaid + xantin, got {poldan or 'NO MATCH'}")


def main() -> None:
    interactions = pd.read_csv(INTERACTIONS_PATH)
    valid_categories = set(interactions["drug_category"].dropna().unique())
    active_map = build_active_category_map(valid_categories)

    lookup = pd.read_csv(LOOKUP_ZAT_AKTIF_PATH)
    product_mapping, unmatched = build_product_mapping(lookup, active_map)
    name_lookup = build_name_category_lookup(product_mapping, active_map)

    assert_expected_examples(product_mapping)

    active_map.to_csv(ACTIVE_CATEGORY_MAP_PATH, index=False)
    product_mapping.to_csv(PRODUCT_CATEGORY_MAPPING_PATH, index=False)
    unmatched.to_csv(UNMATCHED_PATH, index=False)
    name_lookup.to_csv(NAME_CATEGORY_LOOKUP_PATH, index=False)

    unique_product_category = product_mapping.drop_duplicates(["Nama Produk", "drug_category"])
    combo_products = (
        product_mapping.groupby("Nama Produk")["drug_category"].nunique()
        .loc[lambda s: s > 1]
        .sort_values(ascending=False)
    )

    print(f"drug_active_category_map.csv: {len(active_map)} rules")
    print(f"drug_product_category_mapping.csv: {len(product_mapping)} rows")
    print(f"  unique products matched: {product_mapping['Nama Produk'].nunique()}")
    print(f"  unique product-category pairs: {len(unique_product_category)}")
    print(f"  products with >1 drug_category: {len(combo_products)}")
    print(f"drug_name_category_lookup.csv: {len(name_lookup)} rows")
    print(f"drug_product_category_mapping_unmatched.csv: {len(unmatched)} rows")
    print("\nMatched rows by drug_category:")
    print(product_mapping["drug_category"].value_counts().to_string())
    print("\nTop unmatched active ingredients:")
    if unmatched.empty:
        print("None")
    else:
        print(unmatched["Zat_Aktif"].value_counts().head(20).to_string())


if __name__ == "__main__":
    main()
