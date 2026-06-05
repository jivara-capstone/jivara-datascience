# Roboflow Cleanup Candidate Report

Dokumen ini menjelaskan hasil audit kandidat cleanup untuk dataset Roboflow. File di folder ini dipakai sebagai dokumentasi pendukung proses cleaning image pada notebook `Image_Dataset_Pipeline_Roboflow.ipynb`.

## Tujuan

Audit cleanup membantu menjawab pertanyaan bisnis:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

## File Dalam Folder Ini

| File | Fungsi |
|---|---|
| `image_quality_metrics.csv` | Metrik kualitas image. |
| `image_quality_candidates.csv` | Kandidat image yang perlu direview karena blur, kontras, brightness, resolusi, atau label. |
| `exact_duplicate_candidates.csv` | Kandidat exact duplicate. |
| `near_duplicate_pairs.csv` | Pasangan image yang mirip secara perceptual hash. |
| `quality_review_sheet.jpg` | Sheet visual untuk review kandidat kualitas. |
| `near_duplicate_review_sheet.jpg` | Sheet visual untuk review kandidat near duplicate. |

## Cara Membaca

- File ini tidak berarti semua kandidat wajib dihapus.
- Kandidat cleanup harus direview visual terlebih dahulu.
- Validation dan test hanya dibersihkan jika gambar benar-benar salah, corrupt, duplikat, atau bbox salah.
- Train boleh dibersihkan lebih agresif untuk mengurangi noise dan overfitting.

## Output Final

Dataset final yang dipakai untuk handoff tetap berada di:

`data_output/for_ai_engineer/exports`
