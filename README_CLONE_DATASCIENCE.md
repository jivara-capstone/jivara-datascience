# Panduan Clone Project Jivara untuk Path Data Science

Dokumen ini menjelaskan cara meng-clone repository `jivara` dan masuk ke area kerja Data Science.

## 1. Clone repository

```bash
git clone https://github.com/Lingard-cyber/jivara.git
```

## 2. Masuk ke folder project

```bash
cd jivara
```

## 3. Masuk ke path Data Science

```bash
cd dataScience
```

Setelah langkah ini, path kerja Data Science ada di:

```text
jivara/dataScience/
```

## 4. Struktur utama path Data Science

```text
dataScience/
├─ dashboard/
├─ notebooks/
├─ Scraping/
├─ data_output/
├─ data_mentah/
├─ README.md
└─ Aturan_penulisan_clean_code.md
```

## 5. Fungsi tiap folder

- `dashboard/`
  Berisi aplikasi Streamlit untuk visualisasi hasil project.

- `notebooks/`
  Berisi notebook dan script pipeline Data Science.

- `Scraping/`
  Berisi script pengambilan data mentah dari berbagai sumber.

- `data_output/`
  Berisi hasil olahan data, knowledge base, lookup, dan output analisis.

- `data_mentah/`
  Berisi data mentah sebelum preprocessing.

## 6. Menjalankan dashboard dari root project

Keluar dulu dari folder `dataScience` ke root:

```bash
cd ..
```

Lalu jalankan:

```bash
python -m streamlit run dataScience/dashboard/dashboard.py
```

## 7. Ringkasan alur kerja

```text
Clone repo -> masuk ke jivara/ -> masuk ke dataScience/ -> kerja di pipeline / dashboard / scraping
```

## 8. Repository dan deploy

- Repository GitHub:
  `https://github.com/Lingard-cyber/jivara.git`

- Streamlit app:
  `https://jivara-t94bpyvj8wv6d5ddarynro.streamlit.app/`
