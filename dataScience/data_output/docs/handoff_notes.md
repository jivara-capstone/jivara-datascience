# Handoff Notes - Jivara Data Science

Dokumen ini menjelaskan artefak final yang disiapkan oleh Data Science untuk AI Engineer dan Backend. Versi ini disesuaikan dengan notebook aktif dan 5 pertanyaan bisnis utama proyek Jivara.

## Ringkasan Tujuan

Pekerjaan Data Science menjawab 5 pertanyaan utama:

1. Menyiapkan dataset image makanan yang layak untuk training YOLO.
2. Memetakan hasil deteksi makanan ke bahan dan nutrisi.
3. Membangun katalog nutrisi makanan Indonesia.
4. Membersihkan dan menstandarkan data obat BPOM.
5. Membangun basis data/knowledge base interaksi makanan, bahan, nutrisi, dan obat.

## Untuk AI Engineer

### 1. Dataset Computer Vision

Gunakan artefak final berikut:

`data_output/for_ai_engineer/exports`

Isi utama:

- `data.yaml`
- `images/train`, `images/val`, `images/test`
- `labels/train`, `labels/val`, `labels/test`
- `yolo11_roboflow_cleaned_dataset.zip`

Dataset ini berasal dari notebook:

`notebooks/Image_Dataset_Pipeline_Roboflow.ipynb`

Catatan:

- Dataset final memiliki 29 kelas makanan.
- Dataset sudah dikonversi ke format YOLO.
- Folder YOLO lain di `data_output` diperlakukan sebagai artefak proses/intermediate, bukan handoff utama.

### 2. Knowledge Base Bahan Makanan

Gunakan file:

- `data_output/for_ai_engineer/food_to_ingredient_kb.json`
- `data_output/for_ai_engineer/ingredient_to_food_kb.json`
- `data_output/for_ai_engineer/drug_food_interactions.csv`

Fungsi:

- `food_to_ingredient_kb.json` menghubungkan kelas makanan ke bahan penyusun.
- `ingredient_to_food_kb.json` menghubungkan bahan ke daftar makanan.
- `drug_food_interactions.csv` dapat dipakai sebagai rule awal untuk mengecek relasi makanan dan kategori obat.

Notebook terkait:

- `notebooks/Cookpad_Resep_Data_Processing.ipynb`
- `notebooks/Master_Data_Preparation_Pipeline_v3.ipynb`

## Untuk Backend

### 1. Katalog Nutrisi

Gunakan file:

- `data_output/processed/unified_nutrition_all_nutrition1.csv`
- `data_output/processed/nutrition1_food_catalog.csv`

Fungsi:

- `unified_nutrition_all_nutrition1.csv` adalah katalog nutrisi lengkap dari `nutrition1.csv`.
- `nutrition1_food_catalog.csv` adalah lookup ringkas untuk pencarian makanan.

Jumlah entri nutrisi: 1,346.

### 2. Data Obat BPOM

Gunakan file:

- `data_output/processed/obat_bpom_cleaned_full.csv`
- `data_output/processed/obat_bpom_cleaned_dedup.csv`
- `data_output/processed/obat_bpom_one_brand_per_composition_with_drug_category.csv`

Fungsi:

- Data obat sudah dibersihkan dari HTML entity.
- Informasi pendaftar sudah diparsing menjadi perusahaan dan negara.
- Zat aktif sudah diekstrak dari komposisi.
- Data sudah memiliki kategori/golongan obat dan status masa berlaku.

### 3. Artefak Backend Siap Pakai

Gunakan file:

- `data_output/for_backend/obat_backend_perawat_one_composition_mapped.csv`
- `data_output/for_backend/obat_backend_perawat_one_composition_mapped.sql`

Jumlah baris CSV: 333.

File ini disiapkan untuk kebutuhan integrasi backend/perawat.

### 4. Lookup Obat ke Kategori Interaksi

Gunakan file:

- `data_output/processed/drug_name_complete_category_lookup.csv`
- `data_output/processed/drug_name_category_lookup.csv`

Panduan penggunaan:

`data_output/docs/DRUG_LOOKUP_GUIDE.md`

Alur backend yang disarankan:

1. Terima input nama obat dari user.
2. Normalisasi nama obat.
3. Cari kategori obat pada lookup.
4. Cocokkan kategori obat dengan makanan/bahan yang terdeteksi.
5. Ambil rule dari `drug_food_interactions.csv`.
6. Tampilkan status aman/peringatan berdasarkan severity.

## Dokumentasi Pendukung

| Dokumen | Fungsi |
|---|---|
| `data_output/docs/data_dictionary.md` | Kamus data output. |
| `data_output/docs/dataset_report_roboflow.md` | Ringkasan dataset computer vision. |
| `data_output/docs/roboflow_data_readiness_plan.md` | Catatan kesiapan dataset Roboflow. |
| `data_output/docs/drug_category_mapping_readme.md` | Penjelasan mapping obat ke kategori. |
| `data_output/docs/DRUG_LOOKUP_GUIDE.md` | Cara menggunakan lookup nama obat. |
| `notebooks/DATA_SCIENCE_OBJECTIVES.md` | Penjelasan tujuan Data Science dan pertanyaan bisnis. |

## Catatan Penting

- Output final computer vision adalah `data_output/for_ai_engineer/exports`.
- Output final nutrisi ada di `data_output/processed/unified_nutrition_all_nutrition1.csv`.
- Output obat siap backend ada di `data_output/for_backend`.
- Notebook tetap menjadi dokumentasi utama proses Data Science.
