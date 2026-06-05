# Roboflow Data Readiness Plan

Dokumen ini menjelaskan kesiapan dataset Roboflow untuk handoff ke AI Engineer. Dokumen ini diselaraskan dengan output final:

`data_output/for_ai_engineer/exports`

## Pertanyaan Bisnis

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

## Status Dataset

Dataset final sudah tersedia dalam format YOLO dan memiliki struktur:

```text
data_output/for_ai_engineer/exports/
  data.yaml
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  yolo11_roboflow_cleaned_dataset.zip
```

Jumlah kelas: 29.

Jumlah file export final:

| Split | Images | Labels |
|---|---:|---:|
| train | 4,915 | 4,915 |
| val | 978 | 978 |
| test | 562 | 562 |

## Validasi Yang Dilakukan Di Notebook

Notebook `Image_Dataset_Pipeline_Roboflow.ipynb` melakukan:

- Load anotasi Roboflow.
- Analisis distribusi kelas.
- Analisis kualitas bounding box.
- Validasi integritas image.
- Deteksi exact duplicate.
- Deteksi data imbalance.
- Cleanup dan quarantine untuk data bermasalah.
- Konversi anotasi ke YOLO.
- Export dataset final.

## Dokumen Audit Pendukung

| Dokumen | Fungsi |
|---|---|
| `data_output/docs/dataset_report_roboflow.md` | Ringkasan dataset final. |
| `data_output/docs/roboflow_validation_contact_sheets/index.md` | Visual audit contact sheets. |
| `data_output/docs/roboflow_cleanup_candidates/README.md` | Daftar kandidat cleanup image. |

## Rekomendasi Untuk AI Engineer

1. Gunakan folder `data_output/for_ai_engineer/exports` atau file zip di dalamnya sebagai dataset training.
2. Pastikan path pada `data.yaml` sesuai dengan environment training.
3. Jalankan baseline training terlebih dahulu sebelum eksperimen panjang.
4. Evaluasi metrik per kelas, terutama kelas makanan lokal yang relevan secara produk.
5. Jangan memakai folder intermediate jika hanya ingin training dari handoff final.

## Catatan

Folder seperti `data_output/yolo_roboflow_only`, `data_output/roboflow_augmented_raw`, dan folder augmentasi lain dapat dianggap sebagai artefak proses. Untuk submit dan handoff, folder export final lebih penting.
