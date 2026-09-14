# Desain UI — Sentinel Saham

Delapan layar hi-fi untuk agen pemantau saham Taiwan.

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

File `Sentinel Saham — AAIC 2026` sudah dibuat di Figma (key `ZTux17Ef8AZGb4yHUumizI`)
tapi **masih kosong** — koneksi Figma terputus sebelum sempat menggambar dan sampai
sekarang belum pulih, jadi export otomatis dari sesi ini tidak bisa dilakukan.

Jalur praktis untuk sekarang: export PNG/PDF dari canvas hidup di atas dan pakai itu
sebagai acuan tim. Kalau koneksi Figma pulih, layar-layar ini bisa dibangun ulang di sana
sebagai layer asli — bentuk akhirnya sudah terkunci di berkas `.dc.html` ini, jadi tidak
ada keputusan desain yang perlu diulang.

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
