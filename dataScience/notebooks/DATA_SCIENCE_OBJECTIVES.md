# Tujuan Data Science Jivara

Dokumen ini menjelaskan tujuan utama pekerjaan Data Science pada proyek Jivara. Fokus Data Science adalah menyiapkan data yang dapat digunakan oleh AI Engineer dan Backend untuk membangun sistem deteksi makanan, analisis nutrisi, dan peringatan interaksi obat-makanan.

## Gambaran Umum

Pekerjaan Data Science pada proyek ini tidak hanya berfokus pada analisis data, tetapi juga pada pembuatan artefak data yang siap digunakan oleh sistem. Data yang diolah mencakup:

- Dataset image makanan dari Roboflow untuk computer vision.
- Dataset resep makanan untuk pemetaan makanan ke bahan penyusun.
- Dataset nutrisi makanan Indonesia.
- Dataset obat BPOM.
- Knowledge base interaksi obat-makanan.

Seluruh proses tersebut diarahkan untuk menjawab 5 pertanyaan bisnis utama berikut.

## 1. Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

Pertanyaan ini mewakili pekerjaan pada notebook `Image_Dataset_Pipeline_Roboflow.ipynb`.

Tujuannya adalah memastikan dataset gambar makanan dari Roboflow layak digunakan untuk training model YOLO. Dataset tidak langsung digunakan begitu saja, tetapi dianalisis dan divalidasi terlebih dahulu agar kualitas data lebih baik.

Proses yang dilakukan meliputi:

- Memuat anotasi gambar dari dataset Roboflow.
- Mengecek distribusi kelas makanan.
- Mengevaluasi kualitas anotasi bounding box.
- Memvalidasi file gambar agar tidak ada gambar corrupt atau missing.
- Mendeteksi gambar duplikat.
- Menangani masalah imbalance antar kelas.
- Mengonversi anotasi ke format YOLO.
- Mengekspor dataset final untuk AI Engineer.

Output utama dari proses ini adalah dataset export final di:

`data_output/for_ai_engineer/exports`

Folder tersebut menjadi artefak utama yang digunakan atau dikirim ke AI Engineer untuk proses training model computer vision.

## 2. Bagaimana memetakan hasil deteksi makanan dari model YOLO ke informasi bahan makanan dan nutrisi?

Pertanyaan ini menghubungkan pekerjaan pada notebook `Cookpad_Resep_Data_Processing.ipynb` dan `Master_Data_Preparation_Pipeline_v3.ipynb`.

Hasil deteksi model YOLO hanya berupa label makanan, misalnya `nasi-goreng`, `rendang-sapi`, atau `tumis-kangkung`. Agar label tersebut berguna bagi sistem kesehatan, label makanan perlu dihubungkan ke bahan penyusun dan informasi nutrisi.

Contoh alurnya:

`nasi-goreng` -> bahan seperti nasi, telur, bawang, minyak -> informasi nutrisi -> bahan yang berpotensi berinteraksi dengan obat.

Proses yang dilakukan meliputi:

- Membersihkan data resep makanan.
- Menggabungkan dataset resep dari beberapa sumber.
- Menstandarkan nama kelas makanan agar konsisten dengan kelas YOLO.
- Mengekstrak bahan makanan dari resep.
- Membuat mapping makanan ke bahan penyusun.
- Membuat reverse mapping dari bahan ke daftar makanan.
- Menghubungkan kelas makanan dengan katalog nutrisi.

Output penting dari proses ini antara lain:

- `data_output/for_ai_engineer/food_to_ingredient_kb.json`
- `data_output/for_ai_engineer/ingredient_to_food_kb.json`
- `data_output/processed/food_ingredient_mapping.csv`
- `data_output/processed/mapping_image_nutrition.csv`

Artefak ini membantu AI Engineer dan Backend memahami makanan hasil deteksi sebagai data yang lebih bermakna, bukan sekadar label gambar.

## 3. Bagaimana membangun katalog nutrisi makanan Indonesia yang siap digunakan oleh Backend dan AI?

Pertanyaan ini mewakili pekerjaan pada notebook `Master_Data_Preparation_Pipeline_v3.ipynb`.

Tujuannya adalah membangun katalog nutrisi makanan Indonesia dari `nutrition1.csv` agar dapat digunakan sebagai sumber data utama untuk lookup nutrisi.

Proses yang dilakukan meliputi:

- Memuat data nutrisi dari `nutrition1.csv`.
- Menghapus kolom yang tidak diperlukan.
- Menstandarkan nama kolom makanan.
- Membersihkan nama makanan.
- Menghapus duplikasi berdasarkan nama makanan.
- Membuat `food_id` sebagai identifier.
- Membuat `nutrition_key` sebagai key pencarian makanan.
- Menambahkan informasi sumber data.
- Menyiapkan fitur nutrisi utama seperti kalori, protein, lemak, dan karbohidrat.
- Melakukan validasi katalog nutrisi.

Output penting dari proses ini adalah:

- `data_output/processed/unified_nutrition_all_nutrition1.csv`
- `data_output/processed/nutrition1_food_catalog.csv`

Katalog nutrisi ini disiapkan agar Backend dapat melakukan lookup makanan secara konsisten berdasarkan hasil deteksi AI atau input pengguna.

## 4. Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?

Pertanyaan ini mewakili pekerjaan pada notebook `BPOM_Drug_Data_Processing.ipynb`.

Tujuannya adalah mengubah data obat BPOM yang masih mentah menjadi data yang lebih bersih, terstruktur, dan siap digunakan dalam sistem interaksi obat-makanan.

Proses yang dilakukan meliputi:

- Memuat data obat BPOM.
- Membersihkan teks pada kolom komposisi dan nama produk.
- Mengubah kolom tanggal ke format yang sesuai.
- Memisahkan informasi pendaftar menjadi perusahaan dan negara asal.
- Mengidentifikasi kategori obat berdasarkan nomor registrasi.
- Mengidentifikasi golongan obat.
- Mengidentifikasi asal obat.
- Mengekstrak zat aktif dari komposisi.
- Menghitung jumlah zat aktif.
- Menghitung durasi registrasi.
- Menandai status kedaluwarsa obat.
- Melakukan deduplikasi berdasarkan nomor registrasi.
- Membuat representasi satu komposisi untuk satu produk.

Output penting dari proses ini antara lain:

- `data_output/processed/obat_bpom_cleaned_full.csv`
- `data_output/processed/obat_bpom_cleaned_dedup.csv`
- `data_output/processed/obat_bpom_one_brand_per_composition.csv`
- `data_output/processed/lookup_zat_aktif.csv`
- `data_output/processed/lookup_perusahaan.csv`

Data obat yang sudah dibersihkan ini menjadi dasar untuk membuat lookup kategori obat dan sistem pengecekan interaksi obat-makanan.

## 5. Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

Pertanyaan ini merupakan tujuan integrasi utama dari seluruh pekerjaan Data Science.

Sistem Jivara membutuhkan alur data yang menyambungkan hasil deteksi makanan dari AI dengan data nutrisi dan data obat pengguna. Karena itu, Data Science perlu membangun knowledge base yang dapat menghubungkan:

- Makanan hasil deteksi computer vision.
- Bahan penyusun makanan.
- Informasi nutrisi makanan.
- Nama obat dan zat aktif.
- Kategori obat.
- Potensi interaksi obat-makanan.

Alur logika yang ingin dibangun adalah:

`gambar makanan` -> `kelas makanan YOLO` -> `bahan makanan` -> `nutrisi` -> `kategori obat` -> `interaksi obat-makanan`

Output penting dari proses ini antara lain:

- `data_output/processed/drug_food_interactions.csv`
- `data_output/processed/drug_name_complete_category_lookup.csv`
- `data_output/processed/drug_name_category_lookup.csv`
- `data_output/for_backend/obat_backend_perawat_one_composition_mapped.csv`
- `data_output/for_backend/obat_backend_perawat_one_composition_mapped.sql`

Knowledge base ini disiapkan agar Backend dapat melakukan pengecekan risiko interaksi obat-makanan berdasarkan makanan yang terdeteksi dan obat yang dikonsumsi pengguna.

Catatan implementasi saat ini:

- Rule interaksi aktif dibaca dari `data_output/processed/drug_food_interactions.csv`.
- Artefak tersebut dipadukan dengan `food_to_ingredient_kb.json` untuk memahami bahan pemicu pada makanan.

## Kesimpulan

Tujuan utama Data Science pada proyek Jivara adalah menyiapkan data yang bersih, terstruktur, tervalidasi, dan siap dipakai oleh AI Engineer maupun Backend.

Secara ringkas, pekerjaan Data Science mencakup:

- Menyiapkan dataset image makanan dari Roboflow untuk training YOLO.
- Menghubungkan hasil deteksi makanan dengan bahan makanan.
- Membangun katalog nutrisi makanan Indonesia.
- Membersihkan dan menstandarkan data obat BPOM.
- Membuat knowledge base interaksi obat-makanan.

Dengan pipeline ini, hasil deteksi makanan tidak hanya menjadi output visual, tetapi dapat digunakan sebagai input untuk analisis nutrisi dan peringatan interaksi obat-makanan dalam sistem Jivara.
