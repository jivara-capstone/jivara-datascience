# Data Dictionary - Jivara Data Science

Dokumen ini menjelaskan artefak data utama yang dihasilkan dari notebook Data Science Jivara. Kamus data ini disusun agar AI Engineer dan Backend dapat memahami fungsi setiap file output tanpa harus membaca seluruh notebook dari awal.

## Ringkasan Artefak Utama

| Area | File | Fungsi |
|---|---|---|
| Computer vision | `data_output/for_ai_engineer/exports/data.yaml` | Konfigurasi dataset YOLO final untuk training deteksi makanan. |
| Computer vision | `data_output/for_ai_engineer/exports/images/` | Folder image final hasil export untuk training, validation, dan test. |
| Computer vision | `data_output/for_ai_engineer/exports/labels/` | Folder label YOLO final dalam format `.txt`. |
| Resep dan bahan | `data_output/for_ai_engineer/food_to_ingredient_kb.json` | Mapping kelas makanan ke bahan penyusun. |
| Resep dan bahan | `data_output/for_ai_engineer/ingredient_to_food_kb.json` | Reverse mapping bahan ke daftar makanan. |
| Nutrisi | `data_output/processed/unified_nutrition_all_nutrition1.csv` | Katalog nutrisi lengkap dari `nutrition1.csv`. |
| Nutrisi | `data_output/processed/nutrition1_food_catalog.csv` | Lookup ringkas katalog makanan dan `nutrition_key`. |
| Obat BPOM | `data_output/processed/obat_bpom_cleaned_full.csv` | Data obat BPOM bersih tanpa deduplikasi utama. |
| Obat BPOM | `data_output/processed/obat_bpom_cleaned_dedup.csv` | Data obat BPOM setelah deduplikasi nomor registrasi. |
| Obat BPOM | `data_output/processed/obat_bpom_one_brand_per_composition_with_drug_category.csv` | Satu produk representatif per komposisi, sudah diperkaya kategori obat. |
| Backend | `data_output/for_backend/obat_backend_perawat_one_composition_mapped.csv` | Dataset obat siap backend/perawat. |
| Backend | `data_output/for_backend/obat_backend_perawat_one_composition_mapped.sql` | Versi SQL dari dataset obat siap backend/perawat. |
| Interaksi | `data_output/processed/drug_food_interactions.csv` | Rule interaksi makanan dan kategori obat. |
| Lookup obat | `data_output/processed/drug_name_complete_category_lookup.csv` | Lookup nama obat BPOM ke kategori interaksi. |

## 1. Dataset Computer Vision YOLO

Lokasi final:

`data_output/for_ai_engineer/exports`

Dataset ini berasal dari notebook `Image_Dataset_Pipeline_Roboflow.ipynb`. Dataset sudah melalui proses validasi anotasi, pengecekan distribusi kelas, deteksi duplikasi, cleaning, balancing, konversi ke format YOLO, dan export final.

Struktur utama:

| Path | Isi |
|---|---|
| `data.yaml` | Daftar 29 kelas makanan dan path split YOLO. |
| `images/train` | Image training. |
| `images/val` | Image validation. |
| `images/test` | Image testing. |
| `labels/train` | Label YOLO training. |
| `labels/val` | Label YOLO validation. |
| `labels/test` | Label YOLO testing. |
| `yolo11_roboflow_cleaned_dataset.zip` | Paket zip dataset final untuk handoff. |

Jumlah file pada export final:

| Split | Images | Labels |
|---|---:|---:|
| train | 4,915 | 4,915 |
| val | 978 | 978 |
| test | 562 | 562 |

Jumlah kelas: 29.

## 2. Katalog Nutrisi

File utama:

`data_output/processed/unified_nutrition_all_nutrition1.csv`

Jumlah baris: 1,346.

Kolom penting:

| Kolom | Keterangan |
|---|---|
| `food_id` | Identifier unik makanan. |
| `nutrition_key` | Key pencarian makanan untuk backend/AI. |
| `food_name` | Nama makanan. |
| `source` | Sumber data nutrisi, umumnya `nutrition1_indonesia`. |
| `calories` | Kalori makanan. |
| `proteins` | Kandungan protein. |
| `fat` | Kandungan lemak. |
| `carbohydrate` | Kandungan karbohidrat. |
| `weight_grams` | Basis berat porsi, default 100 gram. |

File lookup ringkas:

`data_output/processed/nutrition1_food_catalog.csv`

Jumlah baris: 1,346.

File ini digunakan ketika backend membutuhkan katalog makanan yang lebih ringan untuk pencarian.

## 3. Mapping Image ke Nutrisi

File:

`data_output/processed/mapping_image_nutrition.csv`

Jumlah baris: 61.

Fungsi file ini adalah menjadi penghubung antara kelas makanan hasil deteksi image dan nama makanan pada katalog nutrisi.

Kolom umum:

| Kolom | Keterangan |
|---|---|
| `image_category` | Nama kategori makanan dari sisi image/model. |
| `nutrition_food_name` | Nama makanan yang dihubungkan ke katalog nutrisi. |
| `status` | Status mapping. |
| `calories` | Nilai kalori referensi jika tersedia. |

## 4. Knowledge Base Bahan Makanan

File utama:

`data_output/for_ai_engineer/food_to_ingredient_kb.json`

Fungsi:

Mapping makanan ke bahan penyusun. Contoh alur:

`nasi-goreng` -> `nasi`, `telur`, `bawang`, `minyak`

File reverse mapping:

`data_output/for_ai_engineer/ingredient_to_food_kb.json`

Fungsi:

Mapping bahan ke daftar makanan yang mengandung bahan tersebut.

Kedua file ini menjawab kebutuhan untuk menghubungkan hasil deteksi YOLO dengan bahan makanan yang dapat dicek terhadap interaksi obat.

## 5. Data Obat BPOM

File utama:

`data_output/processed/obat_bpom_cleaned_full.csv`

Jumlah baris: 23,682.

File deduplikasi nomor registrasi:

`data_output/processed/obat_bpom_cleaned_dedup.csv`

Jumlah baris: 15,085.

File satu produk representatif per komposisi:

`data_output/processed/obat_bpom_one_brand_per_composition_with_drug_category.csv`

Jumlah baris: 2,173.

Kolom penting:

| Kolom | Keterangan |
|---|---|
| `Nomor Registrasi` | Nomor registrasi obat BPOM. |
| `Nama Produk` | Nama produk obat. |
| `Komposisi` | Komposisi obat. |
| `List_Zat_Aktif` | Daftar zat aktif hasil parsing. |
| `Perusahaan` | Perusahaan pendaftar/produsen. |
| `Negara_Asal` | Negara asal dari informasi pendaftar. |
| `Kategori_Obat` | Kategori berdasarkan prefix nomor registrasi. |
| `Golongan_Obat` | Golongan regulatori obat. |
| `Sudah_Kedaluwarsa` | Status masa berlaku obat. |

## 6. Lookup Kategori Obat

File:

`data_output/processed/drug_name_complete_category_lookup.csv`

Jumlah baris: 2,173.

Fungsi:

Menghubungkan nama produk obat BPOM dengan kategori obat yang digunakan pada rule interaksi makanan.

Kolom penting:

| Kolom | Keterangan |
|---|---|
| `nomor_registrasi` | Nomor registrasi BPOM. |
| `nama_produk` | Nama produk obat. |
| `komposisi` | Komposisi obat. |
| `list_zat_aktif` | Daftar zat aktif hasil parsing. |
| `primary_drug_category` | Kategori utama untuk interaksi obat-makanan. |
| `all_drug_categories` | Semua kategori obat yang cocok. |
| `matched` | Status apakah obat berhasil dipetakan. |

## 7. Rule Interaksi Obat-Makanan

File:

`data_output/processed/drug_food_interactions.csv`

Jumlah baris: 1,037.

Fungsi:

Menyimpan rule interaksi antara kelas makanan/bahan makanan dan kategori obat.

Kolom yang umum digunakan:

| Kolom | Keterangan |
|---|---|
| `food_class` | Kelas makanan. |
| `drug_category` | Kategori obat. |
| `has_interaction` | Penanda apakah ada interaksi. |
| `severity` | Tingkat keparahan interaksi. |
| `interaction` | Deskripsi interaksi. |
| `mechanism` | Penjelasan mekanisme jika tersedia. |
| `recommendation` | Rekomendasi penggunaan/waspada. |

## 8. Artefak Backend

File:

`data_output/for_backend/obat_backend_perawat_one_composition_mapped.csv`

Jumlah baris: 333.

File SQL:

`data_output/for_backend/obat_backend_perawat_one_composition_mapped.sql`

Fungsi:

Artefak ini disiapkan untuk kebutuhan integrasi backend/perawat, terutama daftar obat yang sudah dipetakan dalam bentuk yang lebih siap digunakan oleh aplikasi.

## Catatan Penggunaan

- Notebook adalah sumber utama proses Data Science.
- Folder `data_output/for_ai_engineer/exports` adalah output final computer vision.
- Folder `data_output/processed` berisi output tabular hasil cleaning dan feature engineering.
- Folder `data_output/for_ai_engineer` berisi knowledge base untuk AI Engineer.
- Folder `data_output/for_backend` berisi artefak yang paling siap untuk backend.
