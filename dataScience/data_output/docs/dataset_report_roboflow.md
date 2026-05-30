# Dataset Report - Roboflow Food Detection

Generated from current Data Science handoff structure.

## Tujuan

Dokumen ini menjelaskan dataset computer vision yang disiapkan melalui notebook:

`notebooks/Image_Dataset_Pipeline_Roboflow.ipynb`

Pertanyaan bisnis yang dijawab:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

## Dataset Policy

Output final untuk AI Engineer adalah:

`data_output/for_ai_engineer/exports`

Folder lain seperti `data_output/yolo_roboflow_only`, `data_output/roboflow_augmented_raw`, atau folder augmentasi lain diperlakukan sebagai artefak proses/intermediate. Untuk handoff final, gunakan folder export di atas.

## Dataset Format

| Komponen | Keterangan |
|---|---|
| Format label | YOLO TXT |
| Koordinat bbox | Normalized `xywh` |
| Jumlah kelas | 29 |
| Config | `data_output/for_ai_engineer/exports/data.yaml` |
| Zip handoff | `data_output/for_ai_engineer/exports/yolo11_roboflow_cleaned_dataset.zip` |

## Split Distribution

Jumlah file pada export final:

| Split | Images | Labels |
|---|---:|---:|
| train | 4,915 | 4,915 |
| val | 978 | 978 |
| test | 562 | 562 |

## Class Mapping

Daftar kelas pada `data.yaml`:

| ID | Class Name |
|---:|---|
| 0 | Apel |
| 1 | Ayam Goreng |
| 2 | Bakso |
| 3 | Biskuit Choco Chips |
| 4 | Burger |
| 5 | Capcay |
| 6 | Donat |
| 7 | Ikan Goreng |
| 8 | Kentang Goreng |
| 9 | Kiwi |
| 10 | Mie Goreng |
| 11 | Nanas |
| 12 | Nasi Goreng |
| 13 | Nasi Putih |
| 14 | Nugget |
| 15 | Pempek |
| 16 | Pisang |
| 17 | Pizza |
| 18 | Rendang Sapi |
| 19 | Sate |
| 20 | Spaghetti |
| 21 | Steak |
| 22 | Stroberi |
| 23 | Tahu Goreng |
| 24 | Telur Goreng |
| 25 | Telur Rebus |
| 26 | Tempe Goreng |
| 27 | Terong Balado |
| 28 | Tumis Kangkung |

## Proses Data

Notebook Roboflow menjalankan proses berikut:

1. Load anotasi dari dataset Roboflow.
2. Analisis distribusi kelas dan bounding box.
3. Validasi file image.
4. Deteksi duplikasi image.
5. Cleaning bounding box tidak valid.
6. Penanganan imbalance kelas.
7. Konversi anotasi ke format YOLO.
8. Export dataset final untuk AI Engineer.

## Catatan Untuk Training

- Gunakan `data_output/for_ai_engineer/exports` sebagai sumber training.
- Jika path pada `data.yaml` perlu disesuaikan di environment AI Engineer, ubah bagian `path` setelah dataset dipindahkan.
- Pantau metrik per kelas, bukan hanya mAP keseluruhan.
- Kelas seperti `Capcay`, `Ayam Goreng`, dan `Rendang Sapi` tetap penting untuk diperhatikan karena relevan dengan konteks makanan lokal dan potensi integrasi medis.
