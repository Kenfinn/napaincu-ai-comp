# Desain UI — Sentinel Saham

Tujuh layar hi-fi untuk agen pemantau saham Taiwan.

Canvas hidup: https://claude.ai/code/artifact/9b0d25dd-2159-4ecc-89a2-82c0856b690d

## Isi

| Berkas | Layar | Ukuran |
|---|---|---|
| `Main.dc.html` | Feed peringatan | 1440×960 |
| `DetailPeringatan.dc.html` | Detail pengumuman + sitasi MOPS | 1440×960 |
| `Valuasi.dc.html` | Valuasi DCF, asumsi geser, sensitivitas | 1440×1080 |
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
```

## Membangun ulang canvas

Berkas `sentinel-saham-aaic-2026.html` sengaja tidak di-commit — 2,5 MB, dan seluruhnya
bisa dibuat ulang dari berkas di folder ini lewat skill `design`. Edit `.dc.html`, seed
ulang, lalu publikasikan ke URL yang sama.

## Status Figma

File `Sentinel Saham — AAIC 2026` sudah dibuat di Figma tapi masih kosong — koneksi
terputus sebelum sempat menggambar. Sementara ini, export PNG dari canvas cukup sebagai
acuan; kalau koneksi Figma pulih, layar-layar ini bisa dibangun ulang di sana sebagai
layer asli.
