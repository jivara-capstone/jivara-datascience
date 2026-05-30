# Drug Category Extension - Kortikosteroid

Dokumen ini menjelaskan penambahan kategori `kortikosteroid` pada rule interaksi obat-makanan.

## Tujuan

Kategori `kortikosteroid` ditambahkan karena beberapa zat aktif pada data BPOM perlu dipetakan ke kategori interaksi yang relevan dengan makanan tinggi gula dan natrium.

Pertanyaan bisnis terkait:

Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?

## Contoh Zat Aktif

- `METHYLPREDNISOLONE`
- `DEXAMETHASONE`

## Logika Rule

| Kondisi Bahan | Severity |
|---|---:|
| Mengandung bahan tinggi gula dan natrium | 4 |
| Mengandung bahan tinggi gula saja | 3 |
| Mengandung bahan tinggi natrium saja | 3 |
| Tidak mengandung bahan pemicu | 0 atau tidak ada interaksi |

Contoh bahan pemicu:

- gula pasir
- gula merah
- madu
- susu kental manis
- kecap asin

## Output Terkait

- `data_output/processed/drug_food_interactions.csv`
- `data_output/processed/drug_active_category_map_expanded.csv`
- `data_output/processed/drug_name_complete_category_lookup.csv`

## Catatan

Rule ini digunakan sebagai bagian dari knowledge base data. Untuk keputusan medis final, kategori dan severity tetap perlu review farmasis.
