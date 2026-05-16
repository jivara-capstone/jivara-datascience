# DsJivara: Data Preparation Pipeline

Dokumentasi ini ditujukan bagi **AI Engineer** untuk memahami struktur data, alur pipeline, dan cara penggunaan dataset dalam proyek DsJivara (Capstone Project).

## 📌 Gambaran Proyek
DsJivara adalah sistem cerdas yang mengintegrasikan deteksi makanan, analisis nutrisi, dan penalaran farmakologis (interaksi obat dan makanan). Pipeline ini bertanggung jawab untuk membersihkan, menggabungkan, dan menyiapkan data mentah menjadi dataset yang siap digunakan untuk pelatihan model AI (seperti YOLOv11) dan integrasi sistem backend.

## 📂 Struktur Direktori
Berikut adalah penjelasan mengenai struktur folder dalam proyek ini:

*   **`data_mentah/`**: Berisi dataset asli sebelum diproses.
    *   `makanan_indonesia/`: Gambar mentah untuk training.
    *   `nutrition.csv` & `nutrition1.csv`: Data nutrisi makanan.
    *   `indonesian_food_drug_interactions.json`: Basis pengetahuan interaksi obat dan makanan Indonesia.
*   **`data_output/`**: Hasil akhir dari pipeline pemrosesan data.
    *   `for_ai_engineer/`: Folder khusus berisi file yang dibutuhkan untuk training model.
    *   `classes.yaml`: Definisi kelas (35 jenis makanan Indonesia) untuk YOLO.
*   **`notebooks/`**: 
    *   `Master_Data_Preparation_Pipeline.ipynb`: Notebook utama yang menjalankan seluruh alur preprocessing.
*   **Skrip Utilitas**:
    *   `fix_paths.py`: Memperbaiki path dataset agar kompatibel dengan lingkungan training.
    *   `run_notebook_runner.py`: Menjalankan pipeline secara otomatis dari terminal.

## 🚀 Cara Menjalankan Pipeline
Untuk memperbarui data atau menjalankan ulang pemrosesan, ikuti langkah berikut:

1. Pastikan semua dependensi Python sudah terinstal.
2. Jalankan notebook utama di folder `notebooks/` atau gunakan skrip otomatis:
   ```bash
   python run_notebook_runner.py
   ```
3. Periksa folder `data_output/` untuk melihat hasil pemrosesan terbaru.

## 📊 Detail Dataset (YOLOv11)
Dataset deteksi makanan mencakup **35 kelas makanan Indonesia**, termasuk:
- Masakan Utama: Rendang, Rawon Surabaya, Gudeg, Mie Aceh, dll.
- Sate: Sate Ayam Madura, Sate Lilit, Sate Maranggi.
- Jajanan/Minuman: Bika Ambon, Cendol, Bir Pletok, dll.

Detail lengkap kelas dapat dilihat pada file [classes.yaml](file:///d:/Dicoding%20Academy/Capstone%20Project/data_output/for_ai_engineer/classes.yaml).

## 🛠️ Kontak & Kontribusi
Jika terdapat kendala teknis atau pertanyaan mengenai pemetaan data, silakan hubungi tim Data Science atau buat *issue* di repositori ini.
