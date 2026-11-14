# Laporan Antigravity 6 — Animasi Halus (v1.3)

Penambahan lapisan gerak dan interaksi mikro CSS murni + JavaScript vanilla tanpa pustaka eksternal untuk rilis demo 21 November, dijalankan berurutan `A1` -> `A2` -> `A3`. Seluruh perubahan bekerja secara progresif: halaman tetap tampil dan berfungsi penuh tanpa JavaScript maupun pada browser tanpa dukungan View Transitions lintas dokumen, serta mematuhi `@media (prefers-reduced-motion: reduce)`.

Ringkasan commit:
- `9aa0eb8` — `UI: A1 transisi halaman, loading, panel chat`
- `d1abd14` — `UI: A2 interaksi kecil`
- A3 — `Docs: A3 laporan animasi` (dokumen ini + media di `docs/ui/animasi/`)

---

## Ringkasan perubahan per poin (A1 & A2)

### A1.1 Transisi antarhalaman (View Transitions lintas dokumen)
- `app/static/app.css` baris `44–50`: definisi token `--gerak-cepat`, `--gerak-sedang`, `--gerak-halaman`, `--kurva-masuk`, dan `--kurva-keluar` pada `:root`.
- `app/static/app.css` baris `56–83`: `@view-transition { navigation: auto; }`, pemberian nama unik `view-transition-name` untuk `.rail` (`rail`), `.bilah-atas` (`bilah-atas`), dan `main.isi` (`isi`). Animasi keluar `@keyframes feaf-isi-keluar` memudarkan konten utama dan menggeser 6 px ke atas, sementara `@keyframes feaf-isi-masuk` memudarkan masuk dari 8 px di bawah. `::view-transition-group`/`old`/`new` untuk `rail` dan `bilah-atas` memakai `animation: none` agar bilah navigasi diam saat berpindah halaman.

### A1.2 Status loading
- **A1.2a Form aksi dan tautan segarkan:**
  - `app/static/app.css` baris `114–132`: `@keyframes feaf-putar` dan gaya `.tombol.sedang-memuat` / `.chip.sedang-memuat` (lingkaran 14 px di pseudo-elemen `::before` dengan `border-top-color: currentColor`).
  - `app/static/ui.js` baris `371–437`: fungsi `tandaiMemuat()` dan `bersihkanMemuat()`, listener `submit` untuk form `POST` (mengecualikan `.cp-form` dan event yang dibatalkan), penanganan klik ganda via `data-sedang-kirim`, penundaan `disabled = true` satu giliran lewat `window.setTimeout(..., 0)`, dukungan tautan `a[href*="segarkan=1"]`, dan listener `pageshow` untuk melepas status loading saat kembali lewat bfcache.
- **A1.2b Indikator mengetik & masuk gelembung Tanya FEAF:**
  - `app/static/chat.css` baris `390–451`: `.cp-sr-only` untuk teks pembaca layar, `@keyframes cp-ketik` dengan tiga titik `.cp-mengetik span` bergiliran (`animation-delay` 150 ms dan 300 ms), serta `@keyframes cp-pesan-masuk` / `.cp-pesan-masuk` (fade + `translateY(6px)` ke `0`).
  - `app/static/chat.js` baris `157–160`, `186–204`, `253–254`, `273`: mengganti placeholder teks memuat dengan gelembung asisten `role="status"` berisi `.cp-mengetik` (3 `<span>`) + teks `.cp-sr-only`, serta menambahkan `.cp-pesan-masuk` pada pesan yang baru dikirim atau diterima tanpa mengubah logika fetch, riwayat `sessionStorage`, atau tanda tangan.

### A1.3 Panel Tanya FEAF & laci navigasi ponsel
- `app/static/chat.css` baris `45–110`: transisi `.cp-latar` (`opacity 0 -> 1`) dan `.cp-panel` (geser kanan `translateX(100%) -> 0` di desktop, geser bawah `translateY(16px) -> 0` di lebar `< 640px`), kelas `.cp-buka`, dan `.cp-tanpa-animasi`.
- `app/static/chat.js` baris `329–462`: `bukaPanel(fokusInput, langsung)` melepas `hidden`, memaksa layout reflow, lalu memasang `cp-buka` pada frame berikutnya; `tutupPanel(fokusFab)` melepas `cp-buka`, menunggu `transitionend` milik `panel` dengan cadangan `setTimeout` 300 ms, baru memasang `hidden` dan mengembalikan fokus ke `#cp-fab`. Pembukaan ulang otomatis lintas halaman (`feaf_chat_buka="1"`, baris `459–461`) memanggil `bukaPanel(false, true)` memakai `.cp-tanpa-animasi` sehingga panel terbuka langsung tanpa bergeser ulang. Pembatalan frame/timer rapi bila tombol diklik cepat beruntun.
- `app/static/app.css` baris `299–303`, `397–398`: mengganti `display: none/block` pada `.latar-laci` menjadi transisi `opacity`, `visibility`, dan `pointer-events` berdurasi `--gerak-sedang`, sekaligus menyamakan transisi `.rail` di bawah 900 px ke `var(--gerak-sedang)`.

### A1.4 Reduced motion
- `app/static/app.css` baris `756–786`: `@media (prefers-reduced-motion: reduce)` menonaktifkan `@view-transition { navigation: none; }`, memangkas durasi animasi dan transisi ke `0.01ms !important`, menghentikan animasi `::view-transition-*`, spinner `.sedang-memuat::before`, `.pita`, `.lipat`, dan garis tab, serta mematikan `transform` pada `:active`/`:hover`.
- `app/static/chat.css` baris `453–470`: blok `@media (prefers-reduced-motion: reduce)` menonaktifkan transisi/animasi panel dan pesan (`.cp-panel`, `.cp-pesan-masuk`) serta mendiamkan tiga titik `.cp-mengetik span` pada `opacity: 0.75`.

### A2.1 Kartu klikable
- `app/static/app.css` baris `152–156` (`a.kartu`), baris `563–574` (`.kartu-filter`), dan baris `631–637` (`a.kartu-ringkas`): hover mengangkat kartu `translateY(-2px)` dengan bayangan `var(--bayang-2)` berdurasi `--gerak-cepat`. Kartu `.kartu` yang tidak dapat diklik tidak diberi animasi hover.

### A2.2 Tombol dan chip filter
- `app/static/app.css` baris `86–102` (`.tombol`) dan baris `166–182` (`.chip`): transisi halus warna latar, warna teks, tepi, dan skala; `:active` menggunakan `transform: scale(.97)`; state `:disabled:active`, `[aria-disabled="true"]:active`, dan `.sedang-memuat:active` dikunci ke `transform: none`.

### A2.3 Tab saham
- `app/static/app.css` baris `225–257` dan `488–496`: mendukung `.tab a` dan `.tab-saham a` (kelas aktual pada `app/templates/saham.html`). Pseudo-elemen `::after` menampilkan garis abu-abu 2 px dari tengah (`transform-origin: center`) saat hover. Tab aktif (`.on` atau `[aria-current="page"]`) menampilkan garis 3 px `var(--navy)` lewat `@keyframes feaf-garis-tab-masuk` serta `view-transition-name: garis-tab` dengan `::view-transition-group(garis-tab)` berdurasi `--gerak-sedang`. Hanya satu tab aktif per halaman yang membawa nama transisi tersebut.

### A2.4 Filter feed dan review
- `app/static/app.css` baris `742–754`: transisi `opacity` 120 ms pada `.baris[data-status]`, `.kelompok-tanggal`, `[data-sebab-review]`, dan `#feed-kosong-filter` lewat kelas `.sedang-sembunyi`. Aturan global `[hidden] { display: none !important; }` pada baris `54` dipertahankan.
- `app/static/ui.js` baris `24–63` (`aturTampilFilter`), baris `120–160` (`terapkanFilterFeed`), baris `202` (`terapkanFilterFeed(true)` saat inisialisasi), dan baris `215–217` (filter review): baris yang disembunyikan memudar keluar selama 120 ms (timer `130ms`) sebelum diberi `hidden = true`; baris yang ditampilkan dilepas `hidden`-nya lalu memudar masuk. Visibilitas `.kelompok-tanggal` dihitung dari status kecocokan logis baris (`_feafCocok`) agar sinkron dengan animasi keluar. Setiap elemen menyimpan handle timer/frame sendiri sehingga klik chip cepat beruntun membatalkan timer lama dan tidak meninggalkan baris setengah transparan.

### A2.5 Lipatan `<details class="lipat">`
- `app/static/app.css` baris `265–276`: `.lipat > summary::before` menjadi `inline-block` dengan `transition: transform var(--gerak-cepat) var(--kurva-masuk)` dan berputar `rotate(90deg)` saat `[open]`. Isi di dalam `.lipat[open] > :not(summary)` memudar masuk + geser 4 px ke bawah lewat `@keyframes feaf-lipat-masuk` tanpa menganimasikan tinggi.

### A2.6 Dropdown saran pencarian & tooltip ⓘ
- `app/static/app.css` baris `190–216`: `.info::after` mempertahankan `display: none` pada aturan dasar, memakai variabel `--info-x` agar varian tengah, rata kanan, dan ponsel (`<= 600px`) berbagi satu aturan `@starting-style` + `transition-behavior: allow-discrete` (`opacity` + `translateY(-4px -> 0)`).
- `app/static/app.css` baris `372–380` dan `app/static/ui.js` baris `236–331`: `.daftar-saran` muncul lewat `bukaSaran()` (kelas `.terbuka`: fade + `translateY(-4px -> 0)`) dan ditutup lewat `tutupSaran()` (fade keluar `150ms` dengan penundaan pengosongan HTML `160ms` yang dibatalkan bila dibuka ulang cepat).

### A2.7 Pita pesan
- `app/static/app.css` baris `352–359`: `@keyframes feaf-pita-masuk` menjalankan fade + geser dari atas `-6px` ke `0` sekali saat halaman dimuat.

### Tes & skrip QA
- `tests/test_ui.py` baris `240–276`: `test_animasi_a1_css_js_dan_form_check` memeriksa keberadaan `@view-transition`, `prefers-reduced-motion`, `--gerak-sedang`, `pageshow`, serta rute `/` dan `/watchlist` 3 bahasa (`action="/check"`). `test_animasi_a2_tombol_active_dan_lipat` memeriksa `.tombol:active`, transisi `.lipat > summary::before` (bukan `none`), `view-transition-name: garis-tab`, dan `[hidden] { display: none !important; }`.
- `scripts/qa_responsif.py` baris `285–326`: `_cek_panel_chat` menunggu 400 ms sesudah buka/tutup `#cp-panel`, memastikan atribut `hidden` dan `scrollWidth <= vw + 1` pada semua lebar.

---

## Durasi dan kurva yang digunakan

| Elemen / Kategori | Token / Nilai | Keterangan |
|---|---|---|
| Interaksi cepat (hover kartu, active tombol/chip, dropdown, tooltip, lipatan, garis keluar, tutup panel chat) | `--gerak-cepat: 150ms` | Penutupan `.daftar-saran` memakai cadangan `setTimeout` `160ms`; fade filter feed/review memakai `120ms` (`setTimeout` `130ms`) |
| Gerak sedang (buka panel Tanya FEAF, laci ponsel & `.latar-laci`, pita pesan, garis tab aktif, gelembung pesan masuk) | `--gerak-sedang: 220ms` | Penutupan `#cp-panel` memakai `transitionend` + cadangan `300ms` |
| Transisi halaman konten utama (`::view-transition-new(isi)`) | `--gerak-halaman: 280ms` | `::view-transition-old(isi)` `150ms` (`--gerak-cepat`) |
| Kurva masuk / keluar | `cubic-bezier(.2, .8, .2, 1)` / `ease-in` | `--kurva-masuk` dan `--kurva-keluar` |
| Spinner tombol `.sedang-memuat` | `700ms linear infinite` | Berhenti (`animation: none`) saat reduced motion |
| Indikator mengetik `.cp-mengetik` | `900ms ease-in-out infinite` | Stagger `150ms` & `300ms`; diam (`opacity: 0.75`) saat reduced motion |
| Mode `@media (prefers-reduced-motion: reduce)` | `0.01ms` / `none` | `@view-transition { navigation: none; }` + nonaktif transform/animasi |

---

## Hasil tes otomatis dan skrip QA (setelah perubahan akhir)

1. `python3 -m unittest discover -s tests`:
   ```text
   Ran 309 tests in 14.291s
   OK
   ```
2. `python3 scripts/qa_halaman.py`:
   ```text
   Ringkasan QA: 84/84 kombinasi halaman x bahasa lolos (Gagal: 0).
   ```
3. `python3 scripts/qa_responsif.py --lebar 390 768 1024 1440`:
   ```text
   QA responsif LOLOS (15 rute x 3 bahasa x 4 lebar = 0 temuan).
   ```

---

## Hasil verifikasi browser (Chrome, Reduced Motion, Firefox)

Pengujian alur lengkap A3 dijalankan secara terotomasi terhadap server lokal mode fixture (`_siapkan_server_luring()` di `scripts/qa_responsif.py`) pada biner browser nyata `/usr/bin/google-chrome` (Playwright) dan `/snap/firefox/current/usr/lib/firefox/firefox` (`Mozilla Firefox 157.0.1`, Selenium + WebDriver BiDi):

- **Chrome `1440 px` & `390 px` dalam 3 bahasa (`en`, `zh`, `id`):** seluruh alur Feed -> klik filter chip -> submit `Check now` (`sedang-memuat` & `aria-busy="true"` teramati saat submit) -> Watchlist (dropdown `.daftar-saran.terbuka` muncul lalu hilang bersih) -> Saham `2330` enam tab (`view-transition-name: garis-tab` unik per halaman, lipatan `<details class="lipat">` berputar di tab `valuasi`) -> Valuasi `2330` -> Review (filter cepat bersih) -> buka panel Tanya FEAF, kirim pertanyaan (`.cp-mengetik` tampil lalu digantikan balasan) -> pindah ke Watchlist dengan panel tetap terbuka (`transform` langsung `none`/`matrix(1,0,0,1,0,0)` tanpa animasi ulang) -> `Esc` menutup panel (dan laci ponsel `.rail.buka` di `390 px`) **lulus tanpa JS error dan `overflow=False`**.
- **Chrome `prefers-reduced-motion: reduce` (`1440 px`, `en`):** `matchMedia('(prefers-reduced-motion: reduce)').matches === true`, animasi `.pita` (`none`), durasi transisi panel `<= 0.001s`, `.cp-mengetik span` diam (`animationName=none`), serta filter feed, pembukaan/penutupan panel chat, dan pertanyaan Tanya FEAF tetap berfungsi normal.
- **Mozilla Firefox `157.0.1` (`1440 px` & `390 px`):** 5 rute (`/`, `/watchlist`, `/saham/2330?tab=valuasi`, `/valuasi/2330`, `/review?lang=id`) tampil normal tanpa View Transitions lintas dokumen, 0 galat konsol/JS pada listener BiDi, 0 horizontal overflow, serta panel chat `#cp-panel`, filter feed, dan `<details class="lipat">` bekerja normal.

### Media A3 (`docs/ui/animasi/`)
- **GIF alur interaktif:** `docs/ui/animasi/alur-animasi.gif` (`960x600`, durasi `11.7 s` <= `20 s`, 130 frame sumber, `2.4 MB`).
- **Tangkapan layar sesudah (`1440` dan `390`, 3 bahasa) untuk feed & panel chat terbuka:**
  - `docs/ui/animasi/feed-en-1440.png`, `docs/ui/animasi/feed-en-390.png`
  - `docs/ui/animasi/feed-zh-1440.png`, `docs/ui/animasi/feed-zh-390.png`
  - `docs/ui/animasi/feed-id-1440.png`, `docs/ui/animasi/feed-id-390.png`
  - `docs/ui/animasi/chat-panel-en-1440.png`, `docs/ui/animasi/chat-panel-en-390.png`
  - `docs/ui/animasi/chat-panel-zh-1440.png`, `docs/ui/animasi/chat-panel-zh-390.png`
  - `docs/ui/animasi/chat-panel-id-1440.png`, `docs/ui/animasi/chat-panel-id-390.png`

---

## Masalah yang ditemukan dan keputusan yang diambil

1. **Kelas tab saham di templat berbeda dari dokumen rencana (`saham.html`):** halaman saham memakai `<nav class="tab-saham lengket">`, bukan `.tab`. Solusinya, aturan garis bawah `::after` dan `view-transition-name: garis-tab` diterapkan pada `.tab a` sekaligus `.tab-saham a` tanpa mengubah markup HTML.
2. **Struktur anak `<details class="lipat">` bervariasi (`peringatan.html`, `_sinyal.html`):** sebagian lipatan tidak memakai `<div class="isi-lipat">`. Animasi `@keyframes feaf-lipat-masuk` dipasang pada `.lipat[open] > :not(summary)` agar berlaku seragam di semua templat.
3. **Menjaga tes regresi CSS (`tests/test_ui.py` & `tests/test_qa_perbaikan.py`):** tes mewajibkan `.info::after` mempertahankan `display: none` di aturan dasar dan `[hidden] { display: none !important; }` tetap utuh. Tooltip `.info::after` memakai `@starting-style` + `allow-discrete` tanpa mengubah `display: none`, sedangkan filter feed/review dan `.daftar-saran` memakai transisi `opacity` + timer penutupan yang dibatalkan bila ada interaksi susulan agar tidak pernah tertinggal dalam kondisi setengah transparan.
4. **Tombol submitter `name`/`value` pada form `POST /review`:** menonaktifkan `<button name="keputusan">` secara sinkron saat event `submit` menggugurkan pasangan `name`/`value` dari form data. Penonaktifan ditunda ke giliran berikutnya via `window.setTimeout(..., 0)` di `app/static/ui.js`.
5. **Pengujian penutupan panel `#cp-panel` (`scripts/qa_responsif.py`) & penangkapan video GIF:** jeda 120 ms pada `_cek_panel_chat` terlalu pendek untuk animasi tutup panel 150 ms, sehingga diperpanjang ke 400 ms. Selain itu, karena biner `ffmpeg` bawaan cache Playwright tidak terpasang di lingkungan uji, perekaman GIF alur A3.2 memakai Chrome CDP `Page.startScreencast` yang dirangkai memakai `/usr/bin/ffmpeg`.

---

## Hal yang sengaja tidak dikerjakan

- Animasi properti tinggi (`height` / `max-height`) pada `<details class="lipat">` agar terhindar dari layout reflow; rotasi ikon `▸` dan fade/geser 4 px sudah cukup jelas.
- Polyfill View Transitions untuk Firefox atau browser lama.
- Perubahan logika bisnis, backend Python (`app/main.py`, `app/chat.py`, `app/api_docs.py`, `app/agent/**`), riwayat `sessionStorage` chat, maupun penambahan dependensi JS/CSS eksternal.
- Animasi gerak pada kartu non-klikable `.kartu` dan tombol `disabled`, serta animasi berulang terus-menerus selain spinner `.sedang-memuat` dan titik mengetik `.cp-mengetik`.
