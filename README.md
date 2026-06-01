DsJivara: Data Preparation Pipeline
Dokumentasi ini ditujukan bagi AI Engineer untuk memahami struktur data, alur pipeline, dan cara penggunaan dataset dalam proyek DsJivara (Capstone Project).

Gambaran Proyek
DsJivara adalah sistem cerdas yang mengintegrasikan deteksi makanan, analisis nutrisi, dan penalaran farmakologis (interaksi obat dan makanan). Pipeline ini bertanggung jawab untuk membersihkan, menggabungkan, dan menyiapkan data mentah menjadi dataset yang siap digunakan untuk pelatihan model AI (seperti YOLOv11) dan integrasi sistem backend.

Tujuan Data Science
Pekerjaan Data Science pada proyek ini diarahkan untuk menjawab 5 pertanyaan bisnis utama:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?
Bagaimana memetakan hasil deteksi makanan dari model YOLO ke informasi bahan makanan dan nutrisi?
Bagaimana membangun katalog nutrisi makanan Indonesia yang siap digunakan oleh Backend dan AI?
Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?
Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?
Penjelasan lengkap mengenai tujuan, proses, input, dan output Data Science tersedia di:

notebooks/DATA_SCIENCE_OBJECTIVES.md

Index dokumentasi output tersedia di:

data_output/docs/README.md

Struktur Direktori
Berikut adalah penjelasan mengenai struktur folder dalam proyek ini:

data_mentah/: Berisi dataset asli sebelum diproses.
makanan_indonesia/: Dataset lama/Kaggle. Untuk training deteksi makanan terbaru, jangan dipakai karena kualitas dan distribusi kelasnya tidak stabil.
nutrition1.csv: Data nutrisi makanan Indonesia yang digunakan pada pipeline v3.
indonesian_food_drug_interactions.json: Basis pengetahuan interaksi obat dan makanan Indonesia.
data_output/: Hasil akhir dari pipeline pemrosesan data.
for_ai_engineer/: Folder khusus berisi file pendukung untuk integrasi model.
exports/: Hasil export akhir dataset computer vision yang digunakan atau dikirim ke AI Engineer.
for_backend/: Folder khusus berisi knowledge base dan lookup untuk integrasi backend.
processed/: Dataset tabular hasil cleaning dan transformasi.
docs/: Dokumentasi pendukung seperti data dictionary, laporan dataset, dan handoff notes.
notebooks/:
Image_Dataset_Pipeline_Roboflow.ipynb: Pipeline dataset image Roboflow dan export final computer vision.
BPOM_Drug_Data_Processing.ipynb: Pipeline cleaning dan standarisasi data obat BPOM.
Cookpad_Resep_Data_Processing.ipynb: Pipeline resep dan mapping makanan ke bahan.
Master_Data_Preparation_Pipeline_v3.ipynb: Pipeline katalog nutrisi dan knowledge base v3.
DATA_SCIENCE_OBJECTIVES.md: Ringkasan tujuan dan pertanyaan bisnis utama Data Science.
Skrip Utilitas:
scripts/: Berisi skrip pendukung untuk audit, cleaning, integrasi image, dan pembuatan lookup.
Cara Menjalankan Pipeline Deteksi Makanan
Fokus training deteksi makanan menggunakan hasil export akhir dari notebook Image_Dataset_Pipeline_Roboflow.ipynb.

Artefak final yang digunakan untuk handoff computer vision berada di:

data_output/for_ai_engineer/exports
Folder kerja YOLO lain di dalam data_output/ diperlakukan sebagai artefak intermediate atau hasil proses pipeline, bukan output utama handoff.

Detail Dataset (YOLOv11)
Dataset deteksi makanan disiapkan dari image Roboflow melalui proses validasi anotasi, pengecekan distribusi kelas, deteksi duplikasi, balancing, konversi format YOLO, dan export akhir.

Ringkasan audit dataset tersedia di:

data_output/docs/dataset_report_roboflow.md

🛠️ Kontak & Kontribusi
Jika terdapat kendala teknis atau pertanyaan mengenai pemetaan data, silakan hubungi tim Data Science atau buat issue di repositori ini.
