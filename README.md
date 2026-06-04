# Project Capstone : Jivara Data Science

### Data Preparation Pipeline for Nutrition, Drug, and Food Interaction Intelligence

---

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![YOLO](https://img.shields.io/badge/YOLO-Computer_Vision-111827?style=flat-square)](https://github.com/ultralytics/ultralytics)
[![Roboflow](https://img.shields.io/badge/Roboflow-Dataset-6706CE?style=flat-square)](https://roboflow.com/)

---

## Ringkasan Proyek

Jivara Data Science adalah bagian dari proyek capstone Jivara yang berfokus pada persiapan data untuk kebutuhan AI dan backend. Pipeline ini menggabungkan proses pengolahan dataset makanan, nutrisi, resep, obat BPOM, serta interaksi obat-makanan menjadi aset data yang siap dipakai untuk pelatihan model computer vision, knowledge base, dan integrasi aplikasi.

Seluruh pekerjaan Data Science berada di direktori [`dataScience/`](./dataScience/), mulai dari data mentah, notebook eksperimen, hasil pemrosesan, dokumentasi, hingga artefak handoff untuk AI Engineer dan backend.

---

## Fitur Utama

### **Pipeline Data Science**
- **Persiapan Dataset Deteksi Makanan:** Menyiapkan dataset gambar makanan Indonesia untuk training model computer vision berbasis YOLO.
- **Pengolahan Nutrisi Makanan:** Membersihkan dan menyatukan katalog nutrisi makanan agar siap dipakai oleh sistem AI dan backend.
- **Pemrosesan Data Obat BPOM:** Membersihkan, standarisasi, dan pemetaan data obat untuk mendukung analisis interaksi obat-makanan.
- **Knowledge Base Interaksi:** Menghubungkan makanan, bahan, nutrisi, obat, dan kategori interaksi ke dalam dataset terstruktur.
- **Dokumentasi dan Handoff:** Menyediakan data dictionary, audit dataset, handoff notes, dan file output siap integrasi.

### **Dashboard Analisis**
- **Dashboard Streamlit:** Visualisasi dan eksplorasi hasil olahan data melalui modul nutrisi resep, obat BPOM, dan interaksi obat-makanan.

---

## Struktur Repositori

Fokus utama repositori ini untuk kebutuhan Data Science ada di:

- `/dataScience` - ([Lihat README Data Science](./dataScience/README.md))
- `/dataScience/notebooks` - Notebook pipeline utama dan objective Data Science
- `/dataScience/data_output` - Output final, dokumen, dan artefak handoff
- `/dataScience/dashboard` - Dashboard Streamlit untuk eksplorasi hasil data

---

## Persiapan (Prerequisites)

Sebelum memulai, pastikan Anda telah menginstal:
- [Python](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)
- [Jupyter Notebook / JupyterLab](https://jupyter.org/)
- [Streamlit](https://streamlit.io/)

---

## Memulai Proyek Secara Lokal

### 1. Masuk ke Folder Data Science

```bash
cd dataScience
```

### 2. Install Dependency Root Proyek

Jika Anda menggunakan `requirements.txt` dari root repository:

```bash
pip install -r ../requirements.txt
```

### 3. Buka Notebook Pipeline

Notebook utama untuk pipeline persiapan data:

```bash
jupyter notebook notebooks/Master_Data_Preparation_Pipeline_v3.ipynb
```

Notebook lain yang tersedia:

- [`dataScience/notebooks/Image_Dataset_Pipeline_Roboflow.ipynb`](./dataScience/notebooks/Image_Dataset_Pipeline_Roboflow.ipynb)
- [`dataScience/notebooks/BPOM_Drug_Data_Processing.ipynb`](./dataScience/notebooks/BPOM_Drug_Data_Processing.ipynb)
- [`dataScience/notebooks/Cookpad_Resep_Data_Processing.ipynb`](./dataScience/notebooks/Cookpad_Resep_Data_Processing.ipynb)

### 4. Jalankan Dashboard Streamlit

```bash
python -m streamlit run dataScience\dashboard\dashboard.py
```

---

## Output Penting

Beberapa output penting yang dapat langsung digunakan:

- [`dataScience/data_output/docs/data_dictionary.md`](./dataScience/data_output/docs/data_dictionary.md)
- [`dataScience/data_output/docs/handoff_notes.md`](./dataScience/data_output/docs/handoff_notes.md)
- [`dataScience/data_output/docs/dataset_report_roboflow.md`](./dataScience/data_output/docs/dataset_report_roboflow.md)
- [`dataScience/data_output/for_ai_engineer/exports`](./dataScience/data_output/for_ai_engineer/exports)
- [`dataScience/data_output/for_backend/drug_food_kb_final_v3.json`](./dataScience/data_output/for_backend/drug_food_kb_final_v3.json)

---

## Dokumentasi Tambahan

- [README Data Science](./dataScience/README.md)
- [Objective Data Science](./dataScience/notebooks/DATA_SCIENCE_OBJECTIVES.md)
- [README Dokumentasi Output](./dataScience/data_output/docs/README.md)
- [README Dashboard](./dataScience/dashboard/README_DASHBOARD.md)

---

## License

Jivara - Copyright (c) 2026. All Rights Reserved.

---

<p align="center">
 <b>Jivara Data Science Team</b>
</p>
