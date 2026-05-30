# Cookpad Image Scraping - Catatan Pendukung

Dokumen ini menjelaskan peran scraping image Cookpad sebagai proses pendukung eksperimen computer vision. Dokumentasi final dataset tetap mengacu pada:

`data_output/for_ai_engineer/exports`

## Tujuan

Scraping image Cookpad digunakan sebagai opsi untuk menambah variasi gambar makanan, terutama jika ada kelas makanan yang kurang seimbang pada dataset computer vision.

Pertanyaan bisnis terkait:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

## Posisi Dalam Project

Folder `Scraping/` bukan output final. Folder ini berisi data mentah, script, atau catatan pendukung untuk proses pengumpulan data.

Output final yang dipakai untuk AI Engineer tetap:

`data_output/for_ai_engineer/exports`

## Contoh Penggunaan Script

Jika scraping perlu dijalankan ulang:

```bash
python Scraping/scraper_cookpad_images.py
```

Atau dengan parameter khusus:

```bash
python Scraping/scraper_cookpad_images.py --categories "capcay,nasi goreng,pempek" --per-category 100
```

## Catatan Kualitas

Image hasil scraping tidak otomatis menjadi data final. Setiap gambar tambahan perlu melalui:

- Validasi ukuran dan kualitas image.
- Normalisasi nama kelas.
- Pengecekan duplikasi.
- Validasi label.
- Integrasi ke format YOLO.

Proses final tersebut dijelaskan pada notebook:

`notebooks/Image_Dataset_Pipeline_Roboflow.ipynb`
