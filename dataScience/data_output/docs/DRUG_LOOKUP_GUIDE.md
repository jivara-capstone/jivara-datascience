# Drug Lookup Guide

Panduan ini menjelaskan cara menggunakan lookup nama obat ke kategori obat untuk sistem interaksi obat-makanan Jivara.

## Tujuan

File ini mendukung pertanyaan bisnis:

Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?

Dan:

Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

## Artefak Utama

| File | Fungsi |
|---|---|
| `data_output/processed/drug_name_complete_category_lookup.csv` | Lookup lengkap nama obat BPOM ke kategori interaksi. |
| `data_output/processed/drug_name_category_lookup.csv` | Lookup ringkas nama obat ke kategori. |
| `data_output/processed/drug_food_interactions.csv` | Rule interaksi makanan dan kategori obat. |
| `data_output/processed/obat_bpom_one_brand_per_composition_with_drug_category.csv` | Data produk obat representatif per komposisi dengan kategori. |

## Alur Penggunaan Backend

1. Terima input nama obat dari user.
2. Normalisasi input nama obat.
3. Cari nama obat pada lookup.
4. Ambil `primary_drug_category` atau `all_drug_categories`.
5. Ambil makanan atau bahan yang terdeteksi dari AI.
6. Cocokkan kategori obat dan makanan pada `drug_food_interactions.csv`.
7. Tampilkan hasil aman/peringatan berdasarkan `severity`.

Contoh alur:

```text
METFORMIN -> antidiabetes -> cek makanan terdeteksi -> ambil rule interaksi -> tampilkan warning jika ada
```

## Kolom Penting Lookup Lengkap

File:

`data_output/processed/drug_name_complete_category_lookup.csv`

Jumlah baris: 2,173.

| Kolom | Keterangan |
|---|---|
| `nomor_registrasi` | Nomor registrasi BPOM. |
| `nama_produk` | Nama produk obat. |
| `komposisi` | Komposisi obat. |
| `list_zat_aktif` | Daftar zat aktif hasil parsing. |
| `primary_drug_category` | Kategori utama untuk rule interaksi. |
| `all_drug_categories` | Semua kategori yang cocok. |
| `matched` | Status apakah obat berhasil dipetakan. |

## Contoh Query Python

```python
import pandas as pd

lookup = pd.read_csv("data_output/processed/drug_name_complete_category_lookup.csv")

drug_name = "METFORMIN"
matches = lookup[
    lookup["nama_produk"].str.contains(drug_name, case=False, na=False)
]

if matches.empty:
    result = {"status": "drug_not_found"}
else:
    row = matches.iloc[0]
    result = {
        "status": "matched" if row["matched"] else "category_not_mapped",
        "primary_category": row["primary_drug_category"],
        "all_categories": row["all_drug_categories"],
    }

print(result)
```

## Contoh Integrasi Rule Interaksi

```python
import pandas as pd

lookup = pd.read_csv("data_output/processed/drug_name_complete_category_lookup.csv")
interactions = pd.read_csv("data_output/processed/drug_food_interactions.csv")

def check_interaction(drug_name: str, food_class: str):
    drug_rows = lookup[
        lookup["nama_produk"].str.contains(drug_name, case=False, na=False)
    ]

    if drug_rows.empty:
        return {"status": "drug_not_found"}

    category = drug_rows.iloc[0]["primary_drug_category"]

    if pd.isna(category) or category == "UNKNOWN":
        return {"status": "category_not_mapped"}

    rule_rows = interactions[
        (interactions["food_class"] == food_class)
        & (interactions["drug_category"] == category)
    ]

    if rule_rows.empty:
        return {"status": "no_rule_found", "category": category}

    rule = rule_rows.iloc[0].to_dict()
    return {
        "status": "interaction_found" if rule.get("has_interaction") else "no_interaction",
        "category": category,
        "severity": rule.get("severity"),
        "recommendation": rule.get("recommendation"),
    }
```

## Catatan Limitasi

- Tidak semua obat BPOM berhasil dipetakan ke kategori interaksi.
- Obat yang belum match tidak boleh otomatis dianggap aman.
- Matching berbasis zat aktif dan rule curated, bukan diagnosis klinis.
- Untuk penggunaan medis final, rule harus direview oleh farmasis atau tenaga kesehatan.
