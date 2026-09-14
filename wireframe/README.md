# Wireframe — Sentinel Saham

Delapan layar lo-fi. Terpisah dari `design/` yang berisi versi hi-fi.

Canvas hidup: https://claude.ai/code/artifact/db367031-f58b-4273-93dc-973072e6dfa4

## Kenapa ada dua versi

Hi-fi menjawab **"kelihatannya seperti apa"**. Wireframe menjawab **"kenapa begitu"**.

Tiap layar di sini punya pita catatan bernomor di bawahnya. Catatan itu bukan label
("ini tombol") melainkan alasan — kenapa delta nilai wajar harus ada di kartu, kenapa
profil risiko tidak boleh disembunyikan di halaman Pengaturan, kenapa satu langkah
penolakan verifier adalah elemen terpenting di seluruh rancangan.

Dipakai untuk dua hal:

1. **Rapat tim.** Tanpa warna dan tipografi, orang berdebat soal struktur — dan itu
   perdebatan yang berguna. Ferry dan PDK bisa menolak susunan tanpa merasa sedang
   mengkritik selera.
2. **Dokumen 16 Oktober.** Penilaian tahap pertama adalah tinjauan dokumen, bukan uji
   sistem. Catatan bernomor ini adalah alasan rancangan yang tidak terbaca dari mockup.

## Isi

| Berkas | Layar | Ukuran |
|---|---|---|
| `Main.dc.html` | Feed peringatan | 1440×1040 |
| `DetailPeringatan.dc.html` | Detail + sitasi MOPS | 1440×840 |
| `Valuasi.dc.html` | Valuasi DCF | 1440×820 |
| `RiwayatNilaiWajar.dc.html` | Riwayat nilai wajar | 1440×900 |
| `TanyaJawab.dc.html` | Tanya jawab | 1440×860 |
| `Watchlist.dc.html` | Watchlist & profil risiko | 1440×780 |
| `JejakAudit.dc.html` | Jejak audit agent | 1440×900 |
| `NotifPonsel.dc.html` | Notifikasi ponsel | 390×1080 |

## Membaca wireframe ini

```
Kotak abu-abu          isinya belum diputuskan — teks, angka, atau data
Teks yang ditulis penuh kalimat yang memang harus persis seperti itu
Lingkaran oranye        penanda catatan, nomornya merujuk ke pita di bawah
Kotak bergaris putus    wadah atau tautan, bukan elemen padat
```

Satu-satunya warna adalah oranye penanda. Itu disengaja: begitu wireframe punya palet,
diskusi langsung melenceng ke warna.

## Yang sengaja belum dijawab

Tiga hal ada di catatan tempel canvas dan belum digambar — **keadaan kosong** (hari tanpa
satu pun peringatan), **keadaan error** (MOPS tidak bisa dijangkau), dan **berapa lama
riwayat disimpan**. Ketiganya perlu diputuskan sebelum layar dibangun, bukan sesudah.

## Membangun ulang

Artboard dihasilkan dari script Python supaya pola berulang (bar teks, kotak zona,
pita catatan) tidak ditulis ulang delapan kali:

```
python3 build_01_feed.py
python3 build_02_detail.py
python3 build_03_valuasi.py
python3 build_04_tanya_watchlist.py
python3 build_05_audit_ponsel.py
```

`build_common.py` memuat pembungkus dan pembuat pita catatan; `style_bersama.txt` memuat
satu blok gaya yang disisipkan ke tiap berkas.

Export untuk Figma dan deck:

```
node scripts/render_design.js wireframe
python3 scripts/build_figma_svg.py wireframe
```

Keduanya dijalankan dari akar repo. Hasilnya di `wireframe/export/` —
`Sentinel-Saham-wireframe.svg` adalah berkas yang diseret ke Figma.
