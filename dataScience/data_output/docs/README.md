# Dokumentasi Data Science Jivara

Folder ini berisi dokumentasi pendukung untuk output Data Science Jivara. Semua dokumen disusun mengikuti 5 pertanyaan bisnis utama yang dijelaskan di:

`notebooks/DATA_SCIENCE_OBJECTIVES.md`

## Pertanyaan Bisnis Utama

1. Bagaimana menyiapkan dataset image makanan yang layak untuk training model computer vision YOLO?
2. Bagaimana memetakan hasil deteksi makanan dari model YOLO ke informasi bahan makanan dan nutrisi?
3. Bagaimana membangun katalog nutrisi makanan Indonesia yang siap digunakan oleh Backend dan AI?
4. Bagaimana membersihkan dan menstandarkan data obat BPOM agar dapat digunakan untuk sistem interaksi obat-makanan?
5. Bagaimana membangun knowledge base yang menghubungkan makanan, bahan, nutrisi, obat, dan interaksi obat-makanan?

## Index Dokumen

| Dokumen | Pertanyaan Terkait | Fungsi |
|---|---|---|
| `data_dictionary.md` | 1-5 | Kamus data untuk seluruh artefak utama. |
| `handoff_notes.md` | 1-5 | Ringkasan handoff untuk AI Engineer dan Backend. |
| `dataset_report_roboflow.md` | 1 | Ringkasan dataset computer vision final. |
| `roboflow_data_readiness_plan.md` | 1 | Catatan kesiapan dataset Roboflow untuk training. |
| `roboflow_validation_contact_sheets/index.md` | 1 | Dokumentasi visual audit image dan bounding box. |
| `roboflow_cleanup_candidates/README.md` | 1 | Dokumentasi kandidat cleanup image. |
| `DRUG_LOOKUP_GUIDE.md` | 4, 5 | Panduan lookup nama obat ke kategori interaksi. |
| `drug_category_mapping_readme.md` | 4, 5 | Penjelasan mapping obat BPOM ke kategori obat. |
| `drug_category_extension_added_categories.md` | 5 | Penjelasan kategori obat tambahan. |
| `drug_category_extension_kortikosteroid.md` | 5 | Penjelasan khusus kategori kortikosteroid. |
| `system_evaluation_metrics.md` | 1-5 | Metrik evaluasi untuk data preparation dan kesiapan sistem. |

## Artefak Final Yang Dirujuk

| Area | Lokasi |
|---|---|
| Dataset computer vision | `data_output/for_ai_engineer/exports` |
| Knowledge base bahan makanan | `data_output/for_ai_engineer/food_to_ingredient_kb.json` |
| Reverse ingredient mapping | `data_output/for_ai_engineer/ingredient_to_food_kb.json` |
| Katalog nutrisi | `data_output/processed/unified_nutrition_all_nutrition1.csv` |
| Lookup katalog nutrisi | `data_output/processed/nutrition1_food_catalog.csv` |
| Data obat BPOM bersih | `data_output/processed/obat_bpom_cleaned_full.csv` |
| Lookup obat ke kategori | `data_output/processed/drug_name_complete_category_lookup.csv` |
| Rule interaksi obat-makanan | `data_output/processed/drug_food_interactions.csv` |
| Artefak backend/perawat | `data_output/for_backend` |

## Catatan

Notebook tetap menjadi sumber utama proses teknis. Dokumen pada folder ini berfungsi sebagai ringkasan, kamus data, dan panduan handoff.
