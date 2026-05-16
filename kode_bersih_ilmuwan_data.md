# Kode Bersih untuk Ilmuwan Data

> **Sumber:** Ella Bor — 25 April 2021  
> **Topik:** Praktik terbaik penulisan kode bersih untuk data scientist  
> **Kategori:** Software Engineering, Data Science, Best Practices

---

## Ringkasan

Kode bersih bukan sekadar estetika — ini tentang keterbacaan, pemeliharaan, dan keandalan. Ilmuwan data seringkali memulai proyek sebagai eksplorasi cepat, lalu kode tersebut masuk ke produksi tanpa pernah di-refactor. Panduan ini memberikan strategi praktis untuk mengelola kualitas kode di seluruh siklus hidup proyek.

---

## 1. Sesuaikan Kualitas Kode dengan Level Draf

Kualitas kode tidak harus seragam — sesuaikan dengan tahap dan tujuan kode tersebut.

### Tiga Tingkatan Kualitas Kode

| Level | Nama | Deskripsi | Kapan Digunakan |
|-------|------|-----------|-----------------|
| 1 | **Sangat Berantakan** | Tidak ada struktur, nama variabel singkat (`df`), semua dalam satu skrip | Eksplorasi awal, POC, mencoba algoritma baru |
| 2 | **Relatif Mudah Dibaca** | Nama variabel bermakna, terbagi dalam fungsi/kelas, titik awal refactoring | Pengembangan umum, iterasi menuju produksi |
| 3 | **Terbaik di Kelasnya** | Kode produksi, bebas bug semaksimal mungkin, mudah dipelihara | Kode yang akan dirilis ke produksi |

### Panduan Penggunaan Level

- **Algoritma berisiko rendah, cara sudah jelas** → Mulai dari Level 2–3
- **POC, algoritma berisiko tinggi, eksplorasi sekali pakai** → Mulai dari Level 1, naik ke Level 2 seiring perkembangan
- **Tujuan lain** → Mulai dari Level 2, naik ke Level 3 sebelum rilis

> ⚠️ **Aturan terpenting:** Jangan pernah meninggalkan kode berantakan. Lakukan refactoring sebelum melanjutkan, selagi konteks masih segar di kepala.

---

## 2. Aturan Pramuka

**"Selalu tinggalkan tempat perkemahan lebih bersih daripada saat kamu menemukannya."**

Dalam konteks kode:

- **Kerja tim:** Jangan ragu mengubah kode orang lain. Jika ada kode buruk yang perlu diperbaiki — perbaiki. Itu adalah tanggung jawab Anda.
- **Kerja sendiri:** Terus lakukan refactoring saat memeriksa kembali kode Anda.
- **Dengan pengujian:** Lebih mudah dan aman melakukan refactoring ketika ada test coverage yang baik.
- **Tanpa pengujian:** Kurangnya pengujian bukan alasan untuk tidak refactoring — tulis beberapa tes dahulu, lalu refactor.

---

## 3. Sederhanakan Saja (Keep It Simple)

> "Saat menulis kode, gunakan separuh sel otak yang Anda gunakan untuk membaca kode."

Membaca kode jauh lebih sulit dari menulisnya. Selalu tanyakan: **"Bisakah ini ditulis lebih sederhana?"**

---

## 4. Konvensi Penamaan

Menulis kode adalah seperti menceritakan sebuah kisah. Nama yang baik menciptakan ekspektasi yang tepat.

### Dua Faktor Ekspektasi dari Sebuah Nama

1. **Makna semantik** — Apa yang "dijanjikan" nama tersebut? (`load_training_set()` seharusnya memuat data, bukan memfilter null)
2. **Format penulisan** — Apakah konsisten dengan konvensi yang berlaku? (konstanta dengan huruf kapital, dll.)

### Variabel Konstan

```python
# ❌ Buruk
threshold = 0.8

# ✅ Baik
CLASSIFICATION_THRESHOLD = 0.8
```

- Tulis dengan **huruf kapital penuh**
- Beri nama deskriptif
- Letakkan di bagian atas file atau di file konfigurasi eksternal

### Nama Variabel

```python
# ❌ Buruk
df, lr, student_list

# ✅ Baik
train_set, learning_rate, students
```

- Deskriptif, mudah diucapkan, mudah dicari
- Gunakan **jamak** untuk array/list (bukan `student_list`, tapi `students`)
- Gunakan **kata penuh**, bukan singkatan (`learning_rate` bukan `lr`)
- Lebih baik panjang daripada ambigu

### Nama Kelas

```python
# ✅ Baik
class Classifier:
class DataHandler:

# ❌ Hindari
class Manager:
class Processor:
```

- Gunakan **kata benda atau frasa kata benda**
- Hindari nama terlalu umum

### Nama Fungsi

```python
# ❌ Buruk
def load():
def process():

# ✅ Baik
def load_training_data():
def evaluate_model():
def _load_training_data():  # hanya untuk penggunaan internal kelas
```

- Mengandung **kata kerja atau frasa kata kerja**
- Spesifik dan deskriptif
- Awali dengan `_` untuk fungsi internal kelas

---

## 5. Panduan Penulisan Fungsi

### Aturan Utama

- **Kecil:** Maksimal ~20 baris per fungsi
- **Satu tujuan:** Setiap fungsi hanya melakukan **satu hal dan hanya satu hal**
- **Tidak ada efek samping:** Jangan ubah apa pun yang tidak seharusnya diubah
- **DRY (Don't Repeat Yourself):** Pisahkan logika yang berulang menjadi fungsi tersendiri

### Argumen dan Parameter

```python
# ✅ Selalu tuliskan nama parameter saat memanggil fungsi
train_model(learning_rate=0.01, epochs=100, batch_size=32)

# Usahakan maksimal 3 parameter
```

### Kondisi yang Kompleks

```python
# ❌ Buruk
if timer.has_expired() and timer.is_recurrent():
    ...

# ✅ Baik
if should_be_deleted(timer):
    ...

# ❌ Hindari kondisi negatif
if not follow_up_needed():
    ...

# ✅ Lebih baik
if follow_up_not_needed():
    ...
```

---

## 6. Pemformatan Kode

Pemformatan memiliki dua tujuan:
1. **Komunikasi non-verbal** — Tata letak menyampaikan hubungan antar elemen
2. **Fokus** — Kode yang rapi secara visual membebaskan pikiran untuk fokus pada isi

### Panduan Pemformatan

- Setiap baris kode hanya melakukan **satu hal**
- Gunakan **baris kosong** sebagai pemisah konsep (tapi bijak)
- Kode yang saling terkait harus **berdekatan secara vertikal**
- Deklarasikan variabel **di dekat tempat penggunaannya**

### Prinsip Kepala Surat Kabar (Newspaper Principle)

> Bagian atas file = fungsi dan konsep tingkat tinggi  
> Bagian bawah file = detail implementasi dan fungsi tingkat rendah

Seperti membaca koran: judul → subjudul → isi detail.

---

## 7. Prinsip "Less is More"

### Kode yang Ringkas

- Semakin pendek kode, semakin cepat dipahami (tanpa mengorbankan kejelasan)
- Hapus **kode yang dikomentari** — tidak ada yang akan kehilangan kode tersebut
- Hindari baris baru yang tidak perlu

### Tentang Komentar

> **Kode yang bersih tidak membutuhkan komentar.**

**Mengapa menghindari komentar?**
- Kode seharusnya menjelaskan dirinya sendiri >90% waktu
- Komentar sering tidak diperbarui saat kode berubah
- Komentar menambah kekacauan visual

**Kapan komentar boleh digunakan?**
- Hanya untuk menjelaskan **MENGAPA**, bukan **BAGAIMANA**
- Pastikan penting, tidak sepele, tidak berlebihan
- Tulis sesingkat mungkin
- Hapus komentar usang seiring perubahan kode
- **Jangan komentari kode — hapus saja**

```python
# ❌ Komentar buruk (menjelaskan BAGAIMANA — sudah jelas dari kode)
# Mengalikan learning rate dengan 0.1
lr = lr * 0.1

# ✅ Komentar baik (menjelaskan MENGAPA — tidak terlihat dari kode)
# Menurunkan learning rate karena loss mulai osilasi setelah epoch 50
lr = lr * 0.1
```

---

## Ringkasan Checklist Kode Bersih

### Umum
- [ ] Kualitas kode sesuai dengan tahap proyek (eksplorasi vs produksi)
- [ ] Tidak ada kode berantakan yang ditinggalkan tanpa refactoring
- [ ] Kode semudah mungkin (selalu tanya: "bisa lebih sederhana?")

### Penamaan
- [ ] Variabel konstanta ditulis KAPITAL dan deskriptif
- [ ] Nama variabel deskriptif, tidak disingkat, menggunakan jamak untuk koleksi
- [ ] Nama kelas adalah kata benda
- [ ] Nama fungsi mengandung kata kerja dan spesifik

### Fungsi
- [ ] Setiap fungsi ≤ 20 baris
- [ ] Setiap fungsi hanya melakukan satu hal
- [ ] Tidak ada efek samping
- [ ] Maksimal 3 parameter
- [ ] Nama parameter ditulis saat pemanggilan fungsi

### Format & Komentar
- [ ] Konsep tingkat tinggi di atas, detail di bawah (newspaper principle)
- [ ] Tidak ada komentar yang menjelaskan BAGAIMANA (hanya MENGAPA jika perlu)
- [ ] Tidak ada kode yang dikomentari — hapus saja
- [ ] Terminologi konsisten di seluruh codebase

---

## Referensi

- **"Clean Code: A Handbook of Agile Software Craftsmanship"** — Robert C. "Uncle Bob" Martin
- *7±2 Alasan Mengapa Psikologi Akan Membantu Anda Menulis Kode yang Lebih Baik* — Moran Weber & Jonathan Avinor
- [Python Clean Code: 6 Best Practices](https://towardsdatascience.com/python-clean-code-6-best-practices-to-make-your-python-functions-more-readable-7ea4c6171d60)
