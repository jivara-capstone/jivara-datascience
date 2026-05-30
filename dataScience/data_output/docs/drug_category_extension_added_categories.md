# Drug Category Extension - Added Categories

Dokumen ini menjelaskan penambahan kategori obat pada rule interaksi obat-makanan. Dokumentasi ini mendukung proses knowledge base pada proyek Jivara.

## Tujuan

Penambahan kategori dilakukan agar data obat BPOM dapat lebih banyak terhubung dengan rule interaksi makanan.

Pertanyaan bisnis terkait:

Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

## Kategori Yang Ditambahkan atau Diperbarui

- `diuretik_hemat_kalium`
- `dopaminergik_parkinson`
- `kortikosteroid`

## Alasan Penambahan

| Kategori | Alasan |
|---|---|
| `kortikosteroid` | Zat aktif seperti `METHYLPREDNISOLONE` dan `DEXAMETHASONE` muncul pada data obat dan relevan dengan makanan tinggi gula/natrium. |
| `dopaminergik_parkinson` | Zat aktif seperti `LEVODOPA`/`CARBIDOPA` dapat dipengaruhi makanan tinggi protein. |
| `diuretik_hemat_kalium` | Zat aktif seperti `SPIRONOLACTONE` relevan dengan makanan tinggi kalium. |

## Ringkasan Rule

| Kategori | Bahan Pemicu | Severity Umum |
|---|---|---:|
| `kortikosteroid` | Gula tinggi dan/atau natrium tinggi | 3-4 |
| `dopaminergik_parkinson` | Bahan tinggi protein | 3 |
| `diuretik_hemat_kalium` | Bahan tinggi kalium | 4 |

## Artefak Yang Terkait

- `data_output/processed/drug_food_interactions.csv`
- `data_output/processed/drug_active_category_map_expanded.csv`
- `data_output/processed/drug_product_category_mapping.csv`
- `data_output/processed/drug_name_complete_category_lookup.csv`

## Catatan

Penambahan kategori ini berbasis rule curated dari bahan makanan dan zat aktif. Untuk penggunaan klinis final, rule tetap perlu validasi farmasis atau tenaga kesehatan.
