# Prompt Antigravity putaran 6: animasi halus (v1.3, untuk demo 21 Nov)

Untuk ketua tim. Tempel kotak **"Prompt pembuka"** di bawah ke Antigravity (satu agent, folder repo ini
sebagai workspace). Antigravity mengerjakan A1 → A2 → A3 berurutan dari berkas ini.

Sebelum ditinggal:
1. Laptop dicolok ke listrik, sleep dimatikan, Wi-Fi tersambung.
2. Di setelan Antigravity, izinkan perintah terminal dan sunting berkas tanpa persetujuan.
3. `git pull` dulu: v1.2.0 sudah di `main` (commit "Feat: v1.2.0 path API berbahasa Inggris…").

Setelah selesai: kirim `docs/laporan-antigravity-6.md` ke Claude. Claude mengaudit sebelum Deploy.

| No | Isi | Commit |
|---|---|---|
| A1 | Paket 1: transisi antarhalaman, status loading, panel Tanya FEAF bergeser, reduced motion | `UI: A1 transisi halaman, loading, panel chat` |
| A2 | Paket 2: interaksi kecil (kartu, tombol, tab, filter feed, lipatan, dropdown, tooltip) | `UI: A2 interaksi kecil` |
| A3 | QA tiga bahasa, foto layar, laporan | `Docs: A3 laporan animasi` |

```text
Baca docs/prompt-antigravity-6-animasi.md. Patuhi bagian "Aturan untuk semua item", lalu kerjakan
A1, A2, A3 berurutan. Setelah tiap item: jalankan tes dan QA yang disebut, commit dengan judul di
tabel, git pull --rebase origin main, push ke main. Tulis docs/laporan-antigravity-6.md di A3.
```

---

## Aturan untuk semua item

**Tujuan.** Aplikasi sekarang terasa "patah": setiap klik memuat ulang satu halaman penuh (kedip
putih), dan panel, filter, dropdown, tooltip muncul/hilang seketika lewat atribut `hidden`. Buat
perpindahan dan perubahan tampilan terasa halus **tanpa** membuat aplikasi terasa lambat. Demo final
dijalankan di perangkat juri, jadi semuanya harus jalan tanpa CDN, tanpa library, tanpa langkah build.

**Prinsip gerak.**
- Durasi 150–250 ms (maks 300 ms untuk transisi halaman). Easing `cubic-bezier(.2,.8,.2,1)` untuk
  masuk, `ease-in` untuk keluar. Simpan sebagai variabel CSS di `:root` di `app/static/app.css`:
  `--gerak-cepat: 150ms; --gerak-sedang: 220ms; --gerak-halaman: 280ms; --kurva-masuk: …; --kurva-keluar: …`.
- Animasikan **hanya `opacity` dan `transform`** (plus `background-color`/`color`/`box-shadow` untuk
  hover). Jangan animasikan `width`, `height`, `top`, `left`, `margin` (menyebabkan reflow dan luapan
  horizontal yang membuat `scripts/qa_responsif.py` gagal).
- Tidak ada animasi yang berulang terus-menerus kecuali spinner/indikator mengetik selama menunggu.
- **Wajib** blok `@media (prefers-reduced-motion: reduce)` di `app.css` dan `chat.css` yang mematikan
  semua transisi/animasi (durasi `0.01ms`, `animation: none`, `view-transition` dimatikan). Halaman
  harus tetap berfungsi penuh tanpa animasi.
- Tanpa JavaScript (atau browser lama), semua halaman tetap tampil dan berfungsi seperti sekarang.
  Animasi hanya lapisan tambahan.
- Fokus keyboard tetap terlihat (`:focus-visible`), target sentuh tetap ≥ 40 px, kontras tidak turun.

**Yang BOLEH diubah:**
- `app/static/app.css`, `app/static/ui.js`
- `app/static/chat.css`, `app/static/chat.js`: **hanya** untuk animasi panel dan indikator mengetik
  (A1.3, A1.2b). Jangan ubah logika kirim, riwayat, tanda tangan, sessionStorage, atau teks.
- `app/templates/*.html`: hanya menambah kelas/atribut `data-*` yang dibutuhkan animasi. Jangan
  ubah isi teks, struktur data, atau urutan include di `base.html` (baris include `_panel_chat.html`
  jangan dipindah).
- `app/teks/ui.py`: kunci teks baru (tiga bahasa: en, zh, id) bila perlu, mis. label "Memuat…".
- `scripts/qa_responsif.py`, `tests/test_ui.py`: menambah pemeriksaan.

**Yang TIDAK BOLEH diubah:** `app/main.py`, `app/chat.py`, `app/api_docs.py`, `app/agent/**`,
semua Python lain di `app/`, `tests/test_api_docs.py`, `tests/test_api_inggris.py`, README,
CHANGELOG, `app/versi.py`. (Claude sedang mengerjakan dokumentasi `/docs` di berkas-berkas itu; kalau
`git pull --rebase` bentrok di berkas tersebut, ambil versi `origin/main`.)

**Setelah setiap item:**
```bash
python3 -m unittest discover -s tests          # semua lulus
python3 scripts/qa_halaman.py                  # 84/84
SENTINEL_SERTAKAN_CONTOH=1 uvicorn app.main:app --port 8000 &   # untuk QA responsif
python3 scripts/qa_responsif.py --lebar 390 768 1024 1440       # 0 temuan
```

---

## A1 · Paket 1: transisi halaman, loading, panel chat, reduced motion

### A1.1 Transisi antarhalaman (View Transitions lintas dokumen)
1. Di `app.css` tambahkan:
   ```css
   @view-transition { navigation: auto; }
   ```
2. Beri nama elemen yang **tetap** antarhalaman supaya tidak ikut berkedip:
   `.rail { view-transition-name: rail; }`, bilah atas ponsel `view-transition-name: bilah-atas;`.
   Konten utama `main.isi { view-transition-name: isi; }`.
3. Animasi konten: `::view-transition-old(isi)` memudar keluar + geser 6 px ke atas
   (`--gerak-cepat`), `::view-transition-new(isi)` memudar masuk dari 8 px di bawah
   (`--gerak-halaman`, `--kurva-masuk`). `::view-transition-group(rail)` tanpa animasi
   (`animation: none`) supaya menu samping diam.
4. Jangan beri `view-transition-name` yang sama ke dua elemen di satu halaman (nama harus unik, kalau
   tidak transisi dibatalkan browser). Panel chat (`#cp-panel`) **tidak** diberi nama.
5. Browser yang tidak mendukung (Firefox) cukup memuat halaman seperti biasa. Jangan tambahkan
   polyfill.
6. Cek: Chrome → klik Feed → Watchlist → Saham → tab-tab saham → Review: tidak ada kedip putih,
   menu samping tidak bergerak, konten bergeser halus. Tombol Back browser juga halus.

### A1.2 Status loading
a. **Form yang memicu proses lama**: semua `<form method="post" action="/check">` (feed, watchlist)
   dan tautan **Re-run** (`/?segarkan=1`). Di `ui.js`: saat submit/klik, tombol mendapat kelas
   `sedang-memuat`, `aria-busy="true"`, dan dinonaktifkan (cegah klik ganda); teksnya tetap, ditambah
   spinner kecil CSS di kiri (`::before`, lingkaran 14 px berputar, `border-top-color: currentColor`).
   Halaman tujuan menggantikan halaman, jadi tidak perlu mengembalikan status, **kecuali** saat
   kembali lewat bfcache: tangani `pageshow` (`event.persisted`) untuk melepas `sedang-memuat`.
   Form tambah/hapus watchlist dan form review boleh diberi perilaku sama.
b. **Tanya FEAF menunggu jawaban** (`chat.js`, saat ini menulis "… Loading" di sekitar baris 186):
   ganti tampilan teks itu dengan gelembung asisten berisi indikator mengetik tiga titik
   (`.cp-mengetik` dengan tiga `<span>`, animasi naik-turun bergiliran 900 ms, `aria-label` = teks
   memuat yang sudah ada, `role="status"`). Teks memuat yang lama tetap ada untuk pembaca layar.
   Saat jawaban tiba, gelembung jawaban masuk dengan fade + geser 6 px. Halaman `/tanya` (form biasa)
   memakai spinner di tombol kirim seperti A1.2a.

### A1.3 Panel Tanya FEAF bergeser masuk
Saat ini `.cp-panel[hidden] { display: none !important; }` sehingga panel muncul seketika.
1. Buka: hapus `hidden`, lalu pada frame berikutnya tambahkan kelas `cp-buka`. Panel bergeser dari
   `translateX(100%)` ke `0` (`--gerak-sedang`, `--kurva-masuk`); latar `#cp-latar`/backdrop memudar
   dari 0 ke opasitas sekarang.
2. Tutup: lepas `cp-buka`, tunggu `transitionend` (dengan cadangan `setTimeout` 300 ms), baru pasang
   `hidden`. Fokus dikembalikan ke tombol bulat seperti sekarang.
3. Di ponsel (< 640 px, panel layar penuh) gunakan geser dari bawah (`translateY(16px)` + fade) atau
   dari kanan, pilih yang lebih halus; pastikan tidak ada luapan horizontal saat animasi.
4. Panel yang dibuka ulang otomatis saat pindah halaman (`feaf_chat_buka="1"`) **tidak** dianimasikan
   (langsung terbuka), supaya tidak bergeser setiap navigasi.
5. Laci menu ponsel sudah bergeser (`.rail` `transform .18s`): samakan durasinya ke `--gerak-sedang`
   dan buat `.latar-laci` memudar (ganti `display: none/block` dengan `opacity` + `visibility` +
   `pointer-events`).

### A1.4 Reduced motion
Blok `prefers-reduced-motion: reduce` sesuai aturan umum, termasuk:
`@view-transition { navigation: none; }`, spinner berhenti berputar (tetap terlihat sebagai
lingkaran statis), indikator mengetik diam (tiga titik statis).

### A1.5 Tes
Tambah ke `tests/test_ui.py`:
- `app.css` memuat `@view-transition`, `prefers-reduced-motion`, variabel `--gerak-sedang`.
- `chat.css` memuat `prefers-reduced-motion`.
- Halaman `/` dan `/watchlist` tiga bahasa tetap 200 dan tetap memuat `action="/check"`.
- `ui.js` memuat penanganan `pageshow`.
Tambah ke `scripts/qa_responsif.py` (Playwright): buka `/`, klik tombol bulat chat, tunggu 400 ms,
pastikan `#cp-panel` terlihat dan `scrollWidth <= innerWidth + 1` di 390 dan 1440 px; tutup, tunggu
400 ms, pastikan `#cp-panel` `hidden`.

Commit: `UI: A1 transisi halaman, loading, panel chat`.

---

## A2 · Paket 2: interaksi kecil

1. **Kartu** (`a.kartu`, kartu ringkasan yang bisa diklik): hover → `translateY(-2px)` + bayangan
   sedikit lebih dalam (`--gerak-cepat`). Kartu yang tidak bisa diklik tidak bergerak.
2. **Tombol** (`.tombol`, `.chip`): hover mengubah warna latar halus; `:active` →
   `transform: scale(.97)`. Tombol `disabled` tidak bergerak.
3. **Tab saham** (`.tab a`): garis bawah aktif bergeser ke tab yang diklik. Karena tiap tab adalah
   tautan (halaman dimuat ulang), cukup: garis bawah tab aktif muncul dengan `transform: scaleX()`
   dari 0 ke 1 (`transform-origin: center`) saat halaman masuk, dan hover tab menampilkan garis tipis
   abu-abu. Dengan View Transitions dari A1, beri garis aktif `view-transition-name: garis-tab` supaya
   bergeser antar-tab (hanya satu elemen bernama ini per halaman).
4. **Filter feed dan review** (`ui.js` baris ±73 dan ±154, saat ini `b.hidden = !ok`): baris yang
   disembunyikan memudar keluar (opacity → 0, 120 ms) lalu `hidden`; baris yang ditampilkan dibuka
   `hidden`-nya lalu memudar masuk. Grup tanggal yang kosong mengikuti. Pastikan aturan global
   `[hidden] { display: none !important; }` tetap ada dan tes `test_css_memiliki_aturan_hidden_global`
   tetap lulus. Hasil akhir filter harus identik dengan sekarang (uji: klik cepat beberapa chip
   berturut-turut tidak boleh meninggalkan baris setengah transparan).
5. **Lipatan `<details class="lipat">`** ("Detail teknis pemeriksaan"): tanda `▸` berputar 90° saat
   terbuka (`transition` pada `transform`; sekarang `transition: none`). Isi yang terbuka memudar masuk
   + geser 4 px. Jangan animasikan tinggi.
6. **Dropdown saran pencarian** (`.daftar-saran`, `ui.js` ±170–221) dan **tooltip ⓘ** (`.info.buka`):
   muncul dengan fade + `translateY(-4px → 0)` (`--gerak-cepat`), hilang dengan fade.
7. **Pita pesan** (`.pita` setelah aksi, mis. "Watchlist diperbarui"): masuk dengan fade + geser dari
   atas 6 px sekali saat halaman dimuat.

Tes tambahan di `tests/test_ui.py`: `app.css` memuat aturan `:active` untuk `.tombol` dan
`transition` untuk `.lipat > summary::before` (bukan `none`).

Commit: `UI: A2 interaksi kecil`.

---

## A3 · QA dan laporan

1. Jalankan semua pemeriksaan di "Setelah setiap item". Semua harus lulus.
2. Uji manual di Chrome (1440 px dan mode perangkat 390 px), tiga bahasa:
   Feed → filter chip → Check now (spinner) → Watchlist → Saham 2330 enam tab → Valuasi → Review →
   buka/tutup panel Tanya FEAF, kirim satu pertanyaan (indikator mengetik) → pindah halaman dengan
   panel terbuka (tidak bergeser ulang) → Esc menutup laci ponsel dan panel.
3. Uji ulang dengan **reduced motion** aktif (Chrome DevTools → Rendering → Emulate CSS
   prefers-reduced-motion: reduce): tidak ada gerakan, semua tetap berfungsi.
4. Uji di Firefox: tidak ada galat konsol, halaman tampil normal tanpa transisi antarhalaman.
5. Rekam satu GIF/video pendek (≤ 20 detik) alur di poin 2 ke `docs/ui/animasi/` dan foto layar
   sesudah (1440 dan 390, tiga bahasa) untuk feed dan panel chat terbuka.
6. Tulis `docs/laporan-antigravity-6.md`: apa yang diubah per poin A1/A2 (berkas + baris), durasi
   yang dipakai, hasil semua tes/QA (salin baris ringkasnya), hasil uji manual Chrome/Firefox/reduced
   motion, masalah yang ditemukan dan keputusan yang diambil, serta hal yang sengaja tidak dikerjakan.

Commit: `Docs: A3 laporan animasi`.

**Cek setelah deploy (oleh tim).** Buka `/` di laptop juri (Chrome): pindah halaman tanpa kedip putih,
tombol Check now menampilkan spinner, panel Tanya FEAF bergeser masuk.
