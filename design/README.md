# Desain UI — Sentinel Saham

Delapan layar hi-fi untuk agen pemantau saham Taiwan, plus dua diagram yang
diwajibkan Appendix 1 sebagai halaman deck 5 dan 6.

Kedua diagram sengaja digambar **sebelum** kode pipeline ditulis: diagram state
adalah spesifikasinya, bukan ilustrasi hasil jadi. Menggambarnya memaksa menjawab
apa yang terjadi saat API gagal, kapan agent berhenti sendiri, dan kapan manusia
dipanggil — pertanyaan yang kalau tidak dijawab di sini baru ketahuan saat demo.

Canvas hidup: https://claude.ai/code/artifact/9b0d25dd-2159-4ecc-89a2-82c0856b690d

## Isi

| Berkas | Layar | Ukuran |
|---|---|---|
| `Main.dc.html` | Feed peringatan | 1440×960 |
| `DetailPeringatan.dc.html` | Detail pengumuman + sitasi MOPS | 1440×960 |
| `Valuasi.dc.html` | Valuasi DCF, asumsi geser, sensitivitas | 1440×1080 |
| `RiwayatNilaiWajar.dc.html` | Riwayat nilai wajar vs harga pasar | 1440×980 |
| `TanyaJawab.dc.html` | Tanya jawab — tempat juri menguji | 1440×960 |
| `Watchlist.dc.html` | Watchlist & profil risiko | 1440×900 |
| `JejakAudit.dc.html` | Jejak audit agent | 1440×1000 |
| `NotifPonsel.dc.html` | Notifikasi ponsel | 390×844 |
| `AlurState.dc.html` | **Alur tugas & state agent — deck hal 5** | 1440×710 |
| `Arsitektur.dc.html` | **Arsitektur sistem, model, tool — deck hal 6** | 1440×820 |
| `canvas.json` | Tata letak canvas + catatan tempel | — |

## Keputusan desain yang mengikat

**Angka di layar valuasi adalah keluaran asli `scripts/dcf.py`** — EV 59,684 T, WACC 8,09%,
g tersirat 6,29%, dan seluruh tabel sensitivitas. Kalau kalkulatornya berubah, layar ini
harus ikut diperbarui supaya tetap cocok saat juri mencocokkan dengan kertas kerja.

**Merah = naik, hijau = turun**, mengikuti konvensi bursa Taiwan — kebalikan dari bursa
Barat. Dan merah/hijau hanya dipakai untuk pergerakan harga; label valuasi
(overvalued / wajar / undervalued) memakai warna netral supaya tidak tertukar dengan
arah harga.

**Hanya satu grafik yang dibangun: nilai wajar vs harga pasar.** Bukan candlestick — itu
ada di setiap aplikasi sekuritas, tidak bisa disitasi, dan tidak membuktikan apa pun
tentang agent kita. Garis nilai wajar sengaja berbentuk anak tangga karena memang hanya
dihitung ulang saat ada dokumen baru; tiap anak tangga bisa diklik ke dokumen MOPS-nya.

**Jejak audit adalah layar produk, bukan dokumen terpisah.** Di dalamnya ada satu langkah
di mana verifier menolak draf peringatan karena angkanya tidak ditemukan di dokumen
sumber — itu bukti paling langsung untuk kriteria Safety, Controllability & Governance.

**Data juru bicara ditampilkan sebagai dibuang.** Halaman MOPS memuat nama, jabatan, dan
telepon; layar detail menyatakan secara eksplisit bahwa ketiganya tidak disimpan, sesuai
Pasal 14.1 tentang minimisasi data pribadi.

## Token

```
Navy    #16324F   struktur, aksi utama
Amber   #A86A0B   perhatian (bukan bahaya)
Naik    #C6362C   merah — konvensi TW
Turun   #17795E   hijau — konvensi TW
Ground  #EEF0F2   Surface #FFFFFF   Ink #101418
Tipografi: Instrument Sans (UI) + IBM Plex Mono (angka)

Seri data grafik — BUKAN warna UI di atas:
Nilai wajar  #B5730C
Harga pasar  #2F74C0
```

Navy `#16324F` gagal uji sebagai warna seri data (terbaca abu-abu, chroma terlalu rendah),
jadi grafik memakai `#2F74C0` dan `#B5730C` — pasangan ini lolos seluruh pemeriksaan
keterbacaan termasuk simulasi buta warna. Navy tetap dipakai untuk struktur dan tombol.

## Membangun ulang canvas

Berkas `sentinel-saham-aaic-2026.html` sengaja tidak di-commit — 2,5 MB, dan seluruhnya
bisa dibuat ulang dari berkas di folder ini lewat skill `design`. Edit `.dc.html`, seed
ulang, lalu publikasikan ke URL yang sama.

## Status Figma

Koneksi Figma sudah pulih. File `Sentinel Saham — AAIC 2026` (key `ZTux17Ef8AZGb4yHUumizI`)
masih kosong dan menunggu diisi sebagai layer asli.

Catatan penting soal bentuk impor: berkas SVG gabungan di bawah menanam PNG sebagai
data URI, jadi **semua artboard masuk Figma sebagai gambar rata**, termasuk kedua
diagram. Untuk diagram, layer yang bisa diedit jauh lebih berguna — anggota tim keuangan perlu
mengoreksi label dan panah tanpa lewat build ulang. Itu dikerjakan lewat Figma MCP,
bukan lewat berkas SVG ini.

## Export untuk Figma / deck

```
node scripts/render_design.js
```

Menulis PNG 2x ke `design/export/`. Script ini menunggu Instrument Sans dan IBM Plex
Mono benar-benar termuat sebelum memotret — tanpa itu hasilnya jatuh ke font sistem dan
seluruh tata letak bergeser.

```
python3 scripts/build_figma_svg.py
```

Menggabungkan seluruh PNG jadi satu `design/export/Sentinel-Saham-figma.svg`, tersusun
sesuai `canvas.json`. **Ini berkas yang diseret ke Figma** — sekali import, seluruh papan
terbentuk lengkap dengan judul tiap layar.

`RiwayatNilaiWajar-chart.svg` adalah grafiknya saja, diekstrak sebagai SVG berdiri
sendiri. Ini satu-satunya berkas yang masuk ke Figma sebagai **layer asli** — garis jadi
vector path, angka sumbu jadi text layer yang bisa diedit. PNG yang lain masuk sebagai
gambar rata, bukan layer.

## Versi bahasa Inggris

`design/en/` berisi versi bahasa Inggris dari kesepuluh berkas di atas, dan PNG-nya ada di
`design/en/export/`. Versi inilah yang dipakai di Figma dan materi lomba. Buat ulang setelah
mengubah layar berbahasa Indonesia:

```bash
python3 scripts/design_en.py          # terjemahkan → design/en/*.dc.html
node scripts/render_design.js design/en
```

Teks baru yang belum ada di kamus `EN` di `scripts/design_en.py` dilaporkan saat skrip jalan.
