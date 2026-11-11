# Hasil gold set (11 Nov 2026)

Pelabel: Patrice, 46 pengumuman asli 9 Nov (sekitar 7 per jenis). Berkas jawaban:
`docs/untuk-tim/gold-set-FEAF-jawaban-patrice.xlsx`, versi CSV di `eval/gold.csv`.
Evaluasi dijalankan tanpa model (penalar aturan), dengan data pasar dari OpenAPI TWSE/TPEx.

## Angka resmi untuk deck dan README

Angka ini diambil **sebelum** agent disetel ulang dari jawaban Patrice. Ini angka yang jujur
untuk dilaporkan.

| Metrik | Agent FEAF | Tanpa pemeriksa |
|---|---|---|
| Angka salah yang terbit | 0/46 | 5/46 |
| Keputusan terbit/tahan/arsip sama dengan ahli | 41/46 (89%) | 15/46 (33%) |
| Tingkat sinyal sama dengan ahli (profil moderat) | 21/29 (72%) | 0/29 |
| Ditahan untuk manusia | 13/46 (28%) | 33/46 (72%) |

Laporan lengkap: `eval/hasil/evaluasi-20261111T084547Z.md`.

Baseline kerja manual dari Patrice: **20–30 menit per pengumuman** (dipakai 25). Untuk 46
pengumuman itu setara sekitar 1.150 menit kerja analis. Agent memprosesnya dalam hitungan
milidetik per pengumuman tanpa model.

## Yang ditemukan dari selisihnya

1. **Bug: rugi terbaca laba.** Laporan Taiwan menulis angka negatif dalam kurung, misalnya
   `(339,123)`. Pengurai membacanya positif, jadi 29 dari 177 laporan kuartal yang rugi
   tampil sebagai laba. Ditemukan Patrice lewat kasus 6535.
2. **Bug: jumlah saham dalam 仟股 tidak terbaca**, begitu juga label saham privat (私募股數)
   dan opsi karyawan (認股權行使…新股總數).
3. Ambang rasio utang laporan kuartal terlalu longgar: Patrice menandai 55–58%.
4. Pinjaman dana pasal 23 di 47% ekuitas ditandai Patrice. Batas regulasinya sekitar 40%.
5. Transaksi pasal 20 dengan anak perusahaan 100% diarsipkan Patrice: kas tidak keluar grup.

## Kalibrasi yang dipasang (disetujui Afinzaki, 11 Nov)

| | Perubahan | Berkas |
|---|---|---|
| Bug 1 | Angka dalam kurung = negatif | `app/agent/sinyal.py` (`_f`) |
| Bug 2 | Satuan 仟股/萬股/張, label saham privat dan opsi karyawan | `app/agent/sinyal.py` (`_lembar`) |
| a | Rasio utang: konservatif 40%, moderat 50%, agresif 65% (sebelumnya 50/60/75) | `app/ambang_profil.py` |
| b | Saham baru yang jumlahnya tidak terbaca = perlu diperhatikan | `app/ambang_profil.py` |
| c | Pinjaman dana ≥ 40% ekuitas = perlu diperhatikan, semua profil | `app/ambang_profil.py` |
| d | Pasal 20 dengan anak perusahaan 100% = arsip | `app/agent/screen.py` (`antar_grup`) |

Sesudah kalibrasi, pada 46 pengumuman yang sama: keputusan 43/46, tingkat 29/29
(`eval/hasil/evaluasi-20261111T090230Z.md`). **Ini angka di dalam sampel**, karena diuji
pada data yang dipakai untuk menyetel. Jangan dilaporkan sebagai akurasi. Untuk angka uji
yang bersih perlu 15–20 pengumuman baru yang dilabeli tanpa melihat hasil agent.

Sisa selisih: 4749 (beli tanah, Patrice: terbit) ditahan karena emiten belum punya model
valuasi; 2072 (akhir sewa dengan pihak terkait) dan 6830 (mesin anak perusahaan) ditahan,
Patrice mengarsipkan.

Dampak ke 578 pengumuman lokal: 79 laporan kuartal kini "perlu diperhatikan", 9 transaksi
antar-grup diarsipkan, yang ditahan turun dari 65 ke 49.

## Belum

- Evaluasi dengan Gemini di server (D5).
- Set uji baru 15–20 pengumuman untuk angka di luar sampel.
