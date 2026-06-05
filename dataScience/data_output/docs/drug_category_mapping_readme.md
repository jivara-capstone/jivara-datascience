# Drug Category Mapping Readme

Dokumen ini menjelaskan mapping nama obat BPOM ke `drug_category` yang digunakan untuk rule interaksi obat-makanan.

## Pertanyaan Bisnis

Dokumen ini mendukung pertanyaan bisnis:

Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?

Dan:

Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

## Konsep

`drug_category` adalah kategori farmakologi/terapi yang dipakai oleh rule interaksi obat-makanan. Kategori ini berbeda dari `Golongan_Obat` BPOM.

Contoh:

- `antidiabetes`
- `statin`
- `nsaid`
- `maoi`
- `kortikosteroid`
- `ccb`
- `ace_arb`

`Golongan_Obat` BPOM menjelaskan aspek regulatori seperti obat bebas atau obat keras, sedangkan `drug_category` dipakai untuk mencocokkan obat dengan potensi interaksi makanan.

## Alur Lookup Backend

1. Backend menerima input nama obat dari user.
2. Nama obat dinormalisasi.
3. Sistem mencari obat pada lookup kategori.
4. Sistem mengambil `primary_drug_category` atau `all_drug_categories`.
5. Kategori obat dicocokkan ke `drug_food_interactions.csv`.
6. Jika ada interaksi, backend menampilkan severity dan rekomendasi.

## Artefak Terkait

| File | Fungsi |
|---|---|
| `data_output/processed/drug_active_category_map.csv` | Kamus awal zat aktif ke kategori obat. |
| `data_output/processed/drug_active_category_map_expanded.csv` | Kamus zat aktif yang sudah diperluas. |
| `data_output/processed/drug_product_category_mapping.csv` | Mapping produk BPOM ke kategori obat. |
| `data_output/processed/drug_product_category_mapping_unmatched.csv` | Produk/zat aktif yang belum berhasil dipetakan. |
| `data_output/processed/drug_name_complete_category_lookup.csv` | Lookup lengkap nama obat ke kategori. |
| `data_output/processed/drug_name_category_lookup.csv` | Lookup ringkas nama obat ke kategori. |
| `data_output/processed/drug_food_interactions.csv` | Rule interaksi makanan dan kategori obat. |

## Status Data

Jumlah baris pada lookup lengkap:

- `drug_name_complete_category_lookup.csv`: 2,173 baris.

Jumlah rule interaksi:

- `drug_food_interactions.csv`: 1,037 baris.

## Catatan Kualitas

- Mapping berbasis zat aktif dari kolom komposisi.
- Obat yang belum memiliki kategori diberi status belum match/unknown.
- Rule ini adalah artefak data untuk sistem, bukan pengganti validasi farmasis.
- Untuk penggunaan klinis final, rule tetap perlu review domain expert.
