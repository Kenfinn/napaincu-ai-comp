# Panduan Gold Set untuk Ferry & Patrice

Daftar soal ujian ini dipakai untuk menguji agent FEAF. Kalian membaca pengumuman MOPS asli dan menulis jawaban yang benar. Agent lalu dijalankan pada pengumuman yang sama, dan `scripts/evaluasi.py` membandingkan keputusan serta angkanya.

Target: 30–50 pengumuman. Tenggat: 12 Nov siang.

---

## 1. Format Berkas (eval/gold.csv)

Buka `eval/gold.csv` di Excel atau Google Sheets, lalu simpan kembali sebagai CSV UTF-8.

| Kolom | Isi | Keterangan |
|---|---|---|
| `source_url` | URL lengkap MOPS | Kunci pencocokan data |
| `kode` | Kode emiten | Contoh: 2330 |
| `harus_terbit` | ya / tidak | Kompatibilitas mundur. ya = terbit, tidak = arsip |
| `keputusan` | terbit / tahan / arsip | Keputusan 3 arah untuk pengumuman |
| `tingkat` | info / perhatian / serius | Label tampilan untuk profil risiko moderat |
| `input` | capex, debt, cash, risiko, modal, laporan, berat, tata_kelola | Jalur kejadian |
| `nilai_juta_ntd` | Angka numerik dalam juta NTD | Wajib untuk capex/debt/cash bila terbit |
| `butir_no` | Nomor butir sumber di MOPS | Tempat angka atau kutipan ditemukan |
| `pelabel` | Inisial pelabel | FR (Ferry) atau PDK (Patrice) |
| `catatan` | Penjelasan singkat | Catatan alasan atau konversi |

Aturan pengisian:
- Kolom `keputusan` wajib diisi salah satu: `terbit`, `tahan`, atau `arsip`.
- Jika kolom `harus_terbit` juga diisi, nilainya tidak boleh bertentangan (`ya` harus `terbit`, `tidak` harus `arsip`).
- Untuk keputusan `terbit` pada jalur valuasi (`capex`, `debt`, `cash`), kolom `nilai_juta_ntd` wajib diisi angka.
- Untuk sinyal (`risiko`, `modal`, `laporan`, `berat`, `tata_kelola`), kolom `nilai_juta_ntd` bersifat opsional.

---

## 2. Panduan Pengisian Per Jalur

| Jalur | Pasal MOPS | Contoh Judul Pengumuman | Keputusan | Input | Tingkat |
|---|---|---|---|---|---|
| Valuasi | 20 (atau 11 belanja modal) | 公告本公司董事會決議資本支出預算案 | terbit | capex / cash / debt | kosong |
| Risiko | 22 (penjaminan), 23 (pinjaman) | 公告本公司為子公司提供背書保證達標準 | terbit / tahan | risiko | info / perhatian / serius |
| Modal | 11 (modal/obligasi), 35 (buyback) | 公告本公司董事會決議買回庫藏股 | terbit / arsip | modal | info / perhatian |
| Laporan | 31 (keuangan kuartal) | 公告本公司115年第3季合併財務報告 | terbit | laporan | info / perhatian |
| Berat | 1 (gagal bayar), 3 (setop operasi), 40 (suspensi) | 公告本公司發生存款不足退票情事 | tahan | berat | serius |
| Tata Kelola | 7 (auditor), 8 (pejabat kunci) | 公告本公司更換會計師事務所及簽證會計師 | terbit / tahan | tata_kelola | info / perhatian / serius |
| Dilewati | 12 (paparan investor), 14 (dividen), 17, 43, 51 | 召開法人說明會公告 | arsip | kosong | kosong |

Penjelasan keputusan per jalur:
1. **Valuasi (Pasal 20 atau belanja modal):** Masuk skenario DCF. Tulis `keputusan=terbit`, `input=capex` atau `cash`, dan isi `nilai_juta_ntd`.
2. **Risiko (Pasal 22 dan 23):** Jika rasio ekuitas atau batas limit sangat tinggi (≥80%), tulis `keputusan=tahan` (perlu verifikasi manusia) dan `tingkat=serius`. Bila wajar, tulis `keputusan=terbit` dan `tingkat=info` atau `perhatian`.
3. **Modal (Pasal 11 dan 35):** Jika berupa pembatalan saham treasuri biasa, tulis `keputusan=arsip`. Jika emisi saham baru material, tulis `keputusan=terbit` dan `tingkat=perhatian`.
4. **Laporan (Pasal 31):** Laporan kuartal selalu `keputusan=terbit`. Jika laba positif, `tingkat=info`. Jika merugi, `tingkat=perhatian`.
5. **Berat (Pasal 1, 3, 40):** Kejadian berat tidak boleh langsung terbit tanpa review manusia. Tulis `keputusan=tahan`, `input=berat`, `tingkat=serius`.
6. **Tata Kelola (Pasal 7 dan 8):** Jika auditor mundur atau ada perselisihan pendapat, tulis `keputusan=tahan`, `tingkat=serius`. Jika sekadar rotasi berkala, tulis `keputusan=terbit`, `tingkat=info`.
7. **Dilewati:** Pengumuman rutin yang tidak menyentuh risiko material ditulis `keputusan=arsip`. Kolom input dan tingkat dikosongkan.

---

## 3. Konversi Satuan ke Juta NTD

Semua angka di kolom `nilai_juta_ntd` wajib diseragamkan ke juta NTD:
- 仟元 (ribu NTD): bagi 1.000. Contoh: 1.480.000.000 仟元 menjadi 1480000.
- 百萬元 (juta NTD): angka tetap.
- 億元 (ratus juta NTD): kali 100. Contoh: 15 億元 menjadi 1500.
- 元 (satuan NTD): bagi 1.000.000.

Jika angka tertulis dalam mata uang asing (USD, EUR, JPY) tanpa padanan NTD di pengumuman, tulis `keputusan=tahan` dan beri catatan "mata uang asing". Model valuasi tidak mengasumsikan kurs sepihak.

---

## 4. Cara Tercepat: Mengunduh Kandidat dari Server

Server menyimpan pengumuman asli sejak 11 Nov untuk seluruh emiten. Buka tautan akses lebih dulu (`/akses?kode=...`), lalu unduh berkas CSV:

```text
https://feaf.afinzaki.my.id/ekspor/kandidat-gold.csv
```

Berkas memuat baris kandidat yang sudah diseimbangkan per jalur (termasuk kasus yang harus diarsipkan). Kolom `ringkasan_butir` sudah disaring dan aman dari data pribadi nama pejabat. Kalian cukup mengisi kolom `keputusan`, `tingkat`, `input`, `nilai_juta_ntd`, `butir_no`, `pelabel`, dan `catatan`.

---

## 5. Pemeriksaan Akhir Sebelum Dikirim

Kirimkan `eval/gold.csv` yang sudah diisi ke Afinzaki. Evaluasi dijalankan dengan perintah:

```bash
python3 scripts/evaluasi.py --simpan
```

Hasil metrik dan matriks kebingungan 3 arah akan diperbarui otomatis ke laporan evaluasi.
