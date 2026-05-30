# System Evaluation Metrics - Jivara

Dokumen ini menjelaskan metrik evaluasi yang relevan dengan 5 pertanyaan bisnis utama Data Science Jivara. Fokusnya adalah memastikan artefak data yang dibuat dapat dinilai secara objektif sebelum digunakan oleh AI Engineer dan Backend.

## 1. Evaluasi Dataset Computer Vision

Pertanyaan bisnis:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

Metrik yang digunakan:

| Metrik | Tujuan |
|---|---|
| Jumlah kelas | Memastikan kelas makanan target tersedia dalam dataset. |
| Jumlah image per split | Memastikan train, validation, dan test tersedia. |
| Distribusi kelas | Mengukur imbalance antar kelas. |
| Validitas bounding box | Memastikan anotasi tidak keluar batas gambar atau bernilai tidak valid. |
| Duplikasi image | Mengurangi risiko data leakage dan overfitting. |
| Visual spot-check | Memastikan label dan bounding box sesuai objek makanan. |

Artefak terkait:

- `data_output/for_ai_engineer/exports`
- `data_output/docs/dataset_report_roboflow.md`
- `data_output/docs/roboflow_data_readiness_plan.md`

Target praktis:

- Dataset memiliki struktur YOLO yang valid.
- Tidak ada file image/label utama yang hilang pada export final.
- Kelas mayoritas dan minoritas terdokumentasi.
- Validation dan test dipertahankan sebagai evaluasi yang representatif.

## 2. Evaluasi Mapping Makanan ke Bahan dan Nutrisi

Pertanyaan bisnis:

Bagaimana memetakan hasil deteksi makanan dari model YOLO ke informasi bahan makanan dan nutrisi?

Metrik yang digunakan:

| Metrik | Tujuan |
|---|---|
| Jumlah kelas makanan yang memiliki mapping bahan | Mengukur coverage knowledge base bahan. |
| Jumlah unique ingredient | Mengukur kekayaan bahan yang dapat dianalisis. |
| Noise ingredient | Mengecek apakah hasil ekstraksi masih berisi satuan, instruksi masak, atau label section. |
| Coverage mapping image-nutrition | Mengukur apakah kelas makanan dapat dihubungkan ke katalog nutrisi. |

Artefak terkait:

- `data_output/for_ai_engineer/food_to_ingredient_kb.json`
- `data_output/for_ai_engineer/ingredient_to_food_kb.json`
- `data_output/processed/food_ingredient_mapping.csv`
- `data_output/processed/mapping_image_nutrition.csv`

Target praktis:

- Setiap kelas makanan utama memiliki daftar bahan yang masuk akal.
- Mapping bahan tidak didominasi noise seperti satuan, instruksi, atau judul section.
- Mapping dapat digunakan sebagai jembatan dari output YOLO ke rule interaksi obat.

## 3. Evaluasi Katalog Nutrisi

Pertanyaan bisnis:

Bagaimana membangun katalog nutrisi makanan Indonesia yang siap digunakan oleh Backend dan AI?

Metrik yang digunakan:

| Metrik | Tujuan |
|---|---|
| Jumlah entri nutrisi | Mengukur cakupan katalog. |
| Duplikasi `nutrition_key` | Memastikan key lookup unik. |
| Missing value pada makronutrien utama | Memastikan data nutrisi dapat digunakan backend. |
| Zero value pada makronutrien utama | Mengidentifikasi nilai yang perlu dicek. |

Artefak terkait:

- `data_output/processed/unified_nutrition_all_nutrition1.csv`
- `data_output/processed/nutrition1_food_catalog.csv`

Target praktis:

- Setiap makanan memiliki `food_id` dan `nutrition_key`.
- Makronutrien utama tersedia untuk analisis dasar.
- Katalog dapat digunakan untuk lookup nutrisi oleh backend.

## 4. Evaluasi Data Obat BPOM

Pertanyaan bisnis:

Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?

Metrik yang digunakan:

| Metrik | Tujuan |
|---|---|
| Jumlah baris sebelum dan sesudah deduplikasi | Mengukur dampak cleaning dan deduplication. |
| Jumlah nomor registrasi unik | Memastikan identitas obat lebih bersih. |
| Jumlah zat aktif yang berhasil diekstrak | Mengukur keberhasilan parsing komposisi. |
| Jumlah obat yang berhasil dipetakan ke kategori | Mengukur coverage sistem lookup obat. |
| Match rate kategori obat | Mengukur seberapa banyak obat bisa digunakan untuk rule interaksi. |

Artefak terkait:

- `data_output/processed/obat_bpom_cleaned_full.csv`
- `data_output/processed/obat_bpom_cleaned_dedup.csv`
- `data_output/processed/obat_bpom_one_brand_per_composition_with_drug_category.csv`
- `data_output/processed/drug_name_complete_category_lookup.csv`

Target praktis:

- Komposisi obat dapat dibaca dan diparsing.
- Data obat dapat dicari berdasarkan nama produk.
- Zat aktif dapat dipetakan ke kategori interaksi jika tersedia.

## 5. Evaluasi Knowledge Base Interaksi Obat-Makanan

Pertanyaan bisnis:

Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

Metrik yang digunakan:

| Metrik | Tujuan |
|---|---|
| Jumlah rule interaksi | Mengukur cakupan knowledge base. |
| Jumlah kategori obat | Mengukur variasi kategori farmakologi. |
| Distribusi severity | Mengukur tingkat risiko interaksi. |
| Jumlah makanan dengan interaksi | Mengukur coverage makanan yang memiliki potensi risiko. |
| Jumlah obat matched dan unmatched | Mengukur batasan lookup obat. |

Artefak terkait:

- `data_output/processed/drug_food_interactions.csv`
- `data_output/processed/drug_name_complete_category_lookup.csv`
- `data_output/for_ai_engineer/food_to_ingredient_kb.json`
- `data_output/for_ai_engineer/ingredient_to_food_kb.json`

Target praktis:

- Rule interaksi dapat dicari berdasarkan makanan dan kategori obat.
- Severity dapat digunakan backend untuk menentukan level warning.
- Obat yang belum match diberi status yang jelas agar tidak menimbulkan klaim klinis berlebihan.

## Catatan Implementasi Produk

Metrik seperti precision, recall, mAP, false negative rate, adherence rate, CTR, dan A/B Testing tetap relevan untuk evaluasi produk akhir. Namun metrik tersebut berada pada tahap AI/model deployment dan product evaluation, bukan seluruhnya pada tahap data preparation notebook.

Notebook Data Science saat ini terutama membuktikan kesiapan data, kualitas dataset, dan ketersediaan artefak untuk AI Engineer serta Backend.
