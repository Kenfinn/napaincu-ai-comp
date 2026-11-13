# Panduan gold set

Versi untuk tim keuangan ada di [`untuk-tim/Panduan-Gold-Set-FEAF.pdf`](./untuk-tim/Panduan-Gold-Set-FEAF.pdf)
(sumbernya `untuk-tim/gold-set.html`), dikirim bersama [`untuk-tim/gold-set-FEAF.xlsx`](./untuk-tim/gold-set-FEAF.xlsx).
Isinya: kolom yang diisi, aturan per jenis pengumuman yang sudah disepakati, konversi satuan,
contoh, dan kolom `menit` untuk baseline kerja manual.

Berkas ini catatan teknis untuk ketua tim dan Claude.

## Membuat paket

Excel berisi 46 pengumuman asli 9 Nov, sekitar 7 per jalur, dengan lembar "Isi pengumuman"
supaya pelabel tidak perlu MOPS atau kode akses. Nama orang tidak ikut: butir berlabel 姓名
dibuang, dan untuk pasal 1/6/7/8 hanya butir dari daftar izin (`app/gold.py`,
`LABEL_AMAN_ORANG`) yang diambil.

```bash
SENTINEL_DATA_DIR=<folder data> python3 scripts/buat_paket_gold.py --keluar docs/untuk-tim/gold-set-FEAF.xlsx
```

## Setelah Excel kembali

```bash
python3 scripts/buat_paket_gold.py --ke-csv <excel yang diisi> --keluar eval/gold.csv
python3 scripts/evaluasi.py --menit-manual <rata-rata kolom menit> --simpan
```

Baris tanpa `keputusan` dilewati. Kolom `keputusan` (terbit/tahan/arsip) dan `tingkat` dibaca
oleh `scripts/evaluasi.py` mode gold. Kolom lama `harus_terbit` tetap diterima (ya = terbit,
tidak = arsip).

Kandidat juga bisa diunduh dari server: `/ekspor/kandidat-gold.csv` (butuh kode akses).
