# Roboflow Validation Visual Audit

Dokumen ini menjelaskan fungsi folder visual audit untuk dataset Roboflow.

## Tujuan

Visual audit digunakan untuk mengecek apakah gambar dan bounding box sudah sesuai dengan label makanan. Audit ini mendukung pertanyaan bisnis:

Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?

## Isi Folder

Folder ini berisi:

- Contact sheet per kelas makanan.
- `class_balance_summary.csv`
- `exact_duplicate_images.csv`

Contact sheet membantu reviewer melihat contoh image validation dengan bounding box. Red boxes menandai target class, sedangkan yellow boxes dapat menandai label lain pada image yang sama.

## Hubungan Dengan Output Final

Dokumen audit ini adalah pendukung proses validasi. Output final yang digunakan untuk handoff AI Engineer tetap:

`data_output/for_ai_engineer/exports`

## Catatan

Jika jumlah file pada contact sheet berbeda dari export final, gunakan `dataset_report_roboflow.md` sebagai ringkasan final. Contact sheet tetap berguna sebagai bukti proses visual review dataset.
