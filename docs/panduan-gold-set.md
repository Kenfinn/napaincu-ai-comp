# Panduan Gold Set — untuk Ferry & PDK

**Apa ini:** daftar "soal ujian" untuk agent. Kalian membaca pengumuman MOPS asli dan
menulis jawaban yang benar. Agent lalu dijalankan pada pengumuman yang sama, dan
`scripts/evaluasi.py` menghitung seberapa sering agent cocok dengan jawaban kalian.

**Kenapa wajib:** paket finalis (13 Nov) meminta metrik evaluasi Appendix 2, dan deck
hal. 9 sudah menjanjikan perbandingan dengan tiga baseline. Tanpa jawaban yang ditulis
manusia, tidak ada yang bisa dibandingkan. Ini juga syarat Level 2 validasi lapangan.

**Target:** 30–50 pengumuman. Tenggat **11 Nov malam**, supaya sempat dijalankan dan
dimasukkan ke README pada 12 Nov.

---

## Cara mengisi

Berkasnya `eval/gold.csv`. Buka di Excel atau Google Sheets, lalu simpan kembali sebagai
CSV (UTF-8). Empat baris pertama berpelabel `contoh` adalah data latihan. Biarkan, dan
tambahkan baris kalian di bawahnya.

| Kolom | Isi | Contoh |
|---|---|---|
| `source_url` | URL halaman MOPS pengumuman itu, disalin persis | `https://mopsov.twse.com.tw/...` |
| `kode` | Kode emiten | `2330` |
| `harus_terbit` | **ya** kalau pengumuman ini mengubah angka valuasi dan layak jadi peringatan. **tidak** kalau tidak | `ya` |
| `input` | Kalau `ya`: input mana yang berubah. `capex` (belanja modal), `debt` (utang/penjaminan), atau `cash` (kas masuk/keluar dari transaksi aset) | `capex` |
| `nilai_juta_ntd` | Kalau `ya`: angkanya dalam **juta NTD** | `1480000` |
| `butir_no` | Nomor butir di halaman MOPS tempat angka itu tertulis | `3` |
| `pelabel` | Inisial kalian | `FR` |
| `catatan` | Satu kalimat alasan, terutama kalau ragu | `仟元 → dibagi 1.000` |

**Konversi satuan:** 仟元 (ribu) dibagi 1.000 · 百萬元 (juta) tetap · 億元 dikali 100 ·
元 dibagi 1.000.000. Contoh: `新台幣 1,480,000,000 仟元` → `1480000`.

**Satu pengumuman, dua angka** (misalnya capex dan utang sekaligus): tulis dua baris
dengan `source_url` yang sama.

**Jumlah dalam mata uang asing (USD, JPY, …):** isi `harus_terbit = tidak`, dengan catatan
"mata uang asing". Agent sengaja menolaknya karena model valuasi kita tidak memuat kurs.

**Ragu?** Tulis tebakan terbaik di kolom yang ada, lalu tulis "RAGU: …" di `catatan`.
Jangan dilewati. Kasus yang sulit justru paling berguna.

## Cara tercepat: unduh kandidat dari server

Server menyimpan semua pengumuman asli sejak 8 Nov (semua emiten, bukan hanya watchlist).
Buka tautan akses dulu (`/akses?kode=...`), lalu unduh:

```
https://feaf.afinzaki.my.id/ekspor/kandidat-gold.csv
```

Isinya sekitar 50 pengumuman yang sudah dipilih seimbang per pasal (termasuk yang
seharusnya **tidak** terbit), dengan kolom `ringkasan_butir` berisi butir-butir yang
memuat angka. Kalian cukup mengisi kolom `harus_terbit`, `input`, `nilai_juta_ntd`,
`butir_no`, `pelabel`, `catatan`. Baris yang belum diisi dilewati saat evaluasi.

**Sebelum melabeli, putuskan dulu pemetaan pasal di `docs/pemetaan-pasal.md`**, karena
jawaban "harus terbit atau tidak" bergantung padanya. Untuk pasal 22/23 (sinyal risiko),
isi `harus_terbit=ya` dan `input=risiko`, tanpa `nilai_juta_ntd`.

## Memilih pengumuman sendiri

Data asli ada di laptop yang menjalankan `scripts/fetch_details.py` dari jaringan Taiwan
(`data/parsed/details.json`). Agar evaluasinya jujur:

- **Jangan hanya memilih yang mudah.** Kira-kira separuh `ya` dan separuh `tidak`.
- Ambil dari beberapa emiten, bukan hanya TSMC. Emiten tanpa berkas valuasi akan
  berakhir *ditahan*, dan itu tetap data yang berguna.
- Isi jawaban **sebelum** melihat apa yang dikeluarkan agent. Kalau sudah melihat
  hasilnya, jawabannya tidak lagi independen.

## Setelah selesai

Kirim `eval/gold.csv` ke Afinzaki. Ia menjalankan:

```bash
python3 scripts/evaluasi.py --menit-manual <rata-rata menit dari survei> --simpan
```

Hasilnya tersimpan di `eval/hasil/` dan langsung menjadi tabel metrik di README.
