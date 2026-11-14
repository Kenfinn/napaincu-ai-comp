# Laporan QA Menyeluruh — FEAF (AAIC 2026)

- **Tanggal audit awal**: 2026-11-13 (posisi baseline commit `ca04367` + perubahan kerja pada `app/main.py`, `app/store.py`, `tests/test_valuasi_otomatis.py`)
- **Tanggal verifikasi pasca-perbaikan**: 2026-11-13
- **Kesimpulan kesiapan**: **Siap rilis/submisi dari sisi kode & pengujian** — seluruh temuan Kritis (`K-1`), Tinggi (`T-1`, `T-2`), Menengah (`M-1` s.d. `M-6`), serta blocker de-identifikasi/versi/pengabaian Git & Docker pada Bagian 4 telah diperbaiki dan terverifikasi lulus (`293` unit test pada data lokal maupun `SENTINEL_DATA_DIR` bersih, `84/84` QA halaman tanpa peringatan, QA responsif `0` temuan, evaluasi & uji serangan lulus, serta verifikasi interaktif Playwright Chrome untuk `T-1`, `M-1`, dan `T-2`). Sisa pekerjaan tinggal catatan prioritas rendah (`R-1` s.d. `R-3`, opsional) serta mengeluarkan/tidak menyertakan berkas lokal untracked (termasuk `"API KEY .txt"`) bila membuat arsip submisi manual di luar `git`.

---

## 1. Batasan & Ruang Lingkup Eksekusi

Pengujian dilakukan pada lingkungan tanpa API key model (`SENTINEL_API_KEY` dan `GEMINI_API_KEY` kosong):

1. Seluruh evaluasi pipeline dan chatbot berjalan di jalur **penalar aturan + templat deterministik** (`--tanpa-model`), bukan panggilan langsung ke Gemini API.
2. Pemeriksaan HTML & interaktif peramban dijalankan lewat `FastAPI TestClient` dan **Playwright headless Google Chrome** terhadap salinan terisolasi `data/` maupun `SENTINEL_DATA_DIR` kosong (dengan `SENTINEL_SERTAKAN_CONTOH=1`).
3. Uji integrasi langsung `POST /api/impor` ke server live eksternal dan uji build image Docker penuh tidak dijalankan pada sesi ini (`docker` CLI `29.1.3` terpasang).

---

## 2. Matriks Hasil Pengujian Terotomasi (Pasca-Perbaikan)

| Pemeriksaan | Lingkup & Kondisi | Hasil | Detail Hasil |
|---|---|---|---|
| **Unit test (data lokal)** | `python3 -m unittest discover -s tests -v` | **Lulus** | `Ran 293 tests in 6.946s`, `OK` (mencakup 14 uji regresi baru di `tests/test_qa_perbaikan.py`) |
| **Unit test (data bersih)** | `SENTINEL_DATA_DIR` kosong | **Lulus** | `Ran 293 tests in 11.859s`, `OK` |
| **Kompilasi bytecode** | `python3 -m compileall -q app scripts tests` | **Lulus** | Exit code `0` |
| **Evaluasi Gold + Fixture** | `scripts/evaluasi.py` (50 dokumen berlabel: fixture + 46 `eval/gold_dokumen.json`) | **Lulus** | `0/50 (0%)` angka salah (`tanpa-pemeriksa`: `4/50 (8%)`); `49/50 (98%)` terbit/tidak; `46/50 (92%)` keputusan 3 arah (`4749-2026-11-09-172344` ditahan, 3 `arsip` ditahan); akurasi field input `2/2 (100%)` & nilai `2/2 (100%)`; tingkat sinyal moderat `29/29 (100%)` |
| **Evaluasi Operasional** | `scripts/evaluasi.py --operasional` (4 fixture) | **Lulus** | 3 lolos saringan pasal: `2` `PUBLISHED`, `1` `HELD` (`tahan.verifikasi:cek.besaran+cek.konversi+cek.mu`), `1` `ARCHIVED` (`arsip.saringan_pasal`), latensi `0/0/0/0 ms`; intervensi `1` (`25.0%` total / `33.3%` lolos saringan) |
| **Uji Serangan Deterministik** | `scripts/uji_serangan.py` (ambang `0,40`) | **Lulus** | `72` skenario, **`0` `terbit_salah`** |
| **Tanya FEAF (`--chat`)** | `scripts/evaluasi.py --chat` | **Lulus** | `52/52 (100%)` total (`25/25` bersumber, `27/27` tolak), `0` kata rekomendasi lolos |
| **Tanya FEAF Multi-Giliran** | `scripts/evaluasi.py --chat-percakapan` | **Lulus** | `36/36 (100%)` giliran, `12/12` skenario, `0` kata rekomendasi lolos |
| **QA Responsif Playwright** | `scripts/qa_responsif.py --lebar 390 768 1024 1440` | **Lulus** | `15 rute x 3 bahasa x 4 lebar = 0 temuan` |
| **QA Halaman (`data/` lokal)** | `scripts/qa_halaman.py --verbose` | **Lulus** | `84/84` kombinasi lolos (`Gagal: 0`), `0` peringatan |
| **QA Halaman (`DATA_DIR` bersih)** | `SENTINEL_DATA_DIR` kosong + `SENTINEL_SERTAKAN_CONTOH=1` | **Lulus** | `84/84` kombinasi lolos (`Gagal: 0`), `0` peringatan |
| **Kamus i18n (`app.i18n._T`)** | Inspeksi Python pasca-edit | **Lulus** | `887` kunci valid (bertambah `jj.sebab.tanpa_kunci`) |
| **Uji & Grep De-identifikasi** | `tests.test_deidentifikasi` + `rg -in` | **Lulus** | `1` test (`0.027s`, `OK`; kini memindai `eval/` termasuk `.csv`); `rg` ke `README.md`, `eval/`, `app/` = `0` kecocokan |

### Verifikasi Interaktif Playwright & Pengujian Keamanan

- **Verifikasi interaktif pasca-perbaikan (`T-1`, `M-1`, `T-2` via Playwright Chrome)**:
  - **`T-1` (`/`, 1 `.kelompok-tanggal` campuran)**: awalnya baris `dilewati` tersembunyi (`hidden=True`, `display="none"`, `offsetHeight=0`); klik filter `terbit` dan `ditahan` menampilkan hanya baris sesuai status (`display="flex"`, `offsetHeight > 0`) dan menyembunyikan baris lain (`display="none"`, `offsetHeight=0`) tanpa overflow horizontal.
  - **`M-1` (`/review`)**: chip `"Semua"` memakai `.chip.on` (`rgb(22, 50, 79)`), dan saat chip `"verifikasi"` diklik, latar navy berpindah ke `"verifikasi"` sedangkan `"Semua"` kembali normal (`rgb(255, 255, 255)`).
  - **`T-2` (`SENTINEL_KUNCI_BACA=1`, `SENTINEL_KODE_AKSES=rahasia-qa`)**: `GET /` membalas `401` tanpa `.rail`, `cp-panel`, maupun `"2330"`; `POST /akses` dengan kode salah mengembalikan `303` ke `GET /?pesan=...` (`401`) dengan banner `.pita.err` tanpa membocorkan kode di URL; `POST /akses` dengan kode benar membuka akses (`303` -> `200`, sidebar `.rail` & `"2330"` tampil) dan menyetel cookie `akses` berupa digest HMAC 64 karakter hex (`!= "rahasia-qa"`).
- **Verifikasi Playwright & keamanan baseline awal (pra-perbaikan)**:
  - **Alur Tanya FEAF (`#cp-panel` & `/tanya`)**: klik `#cp-fab` membuka panel; klik chip saran mengisi `.cp-daftar`; kirim pertanyaan lanjutan memperbarui `sessionStorage` (`feaf_chat`, `feaf_chat_buka="1"`); navigasi ke `/watchlist` menjaga panel tetap terbuka dan riwayat utuh; tombol `Recap` (`.cp-aksi-recap`) dan `New` (`.cp-aksi-baru`) berfungsi sesuai rancangan; pengiriman form `POST /tanya` mengarahkan ke `/tanya?id=...` dan menampilkan hasil `2330`.
  - **Navigasi & Laci Ponsel (`390×844`)**: overflow horizontal `0px` pada `/`, `/saham/2330`, `/saham/2330?tab=keu`, `/saham?kode=台`, `/saham?kode=Corp`, `/review`, `/watchlist`, `/valuasi/2330`, `/tanya`; tombol menu ponsel menambahkan `body.laci-terbuka`.
  - **Autocomplete & Bahasa**: ketik `"233"` pada `input[data-cari-saran]` memunculkan 8 saran `.daftar-saran` (`hidden: false`, `display: block`); klik tautan `/bahasa/zh` mengganti `h1` menjadi `警示` dan menyetel cookie `bahasa=zh`.
  - **Log Konsol Peramban**: `0` uncaught `pageerror`, tetapi muncul 1 `console.error` (`404 Not Found`) di setiap sesi baru karena `GET /favicon.ico` belum dilayani (lihat `R-3`).
  - **Autentikasi & Pengalihan Terbuka**: saat `SENTINEL_KODE_AKSES` diset dan `KUNCI_BACA=0`, mutasi (`POST /review/*`, `POST /umpan-balik/*`, `POST /ambang/*`, `POST /periksa`, `POST /watchlist/*`, `GET /ekspor/kandidat-gold.csv`, `POST /api/impor`) mengembalikan `303`/`403`; redirect `?lanjut=//evil.example/x` dan `?kembali=https://evil.example/x` tertahan aman ke `/` atau `/watchlist`.
  - **Auto-Valuasi (`data/valuasi_otomatis/`)**: `store.emiten_tervaluasi()` mengembalikan `40` emiten; sampel `/valuasi/{1216,1303,1467,1560,1586}` & `/api/valuasi/...` mengembalikan `200`, emiten non-layak (`/valuasi/{1301,1525}`) mengembalikan `404`.

---

## 3. Daftar Temuan Bug & Celah Terverifikasi

### Prioritas Kritis

#### K-1. Crash `HTTP 500` pada `/saham/{kode}?tab=keu` saat data keuangan tidak tersedia — **Status: Diperbaiki**
- **Lokasi**: `app/templates/saham.html:249-258`, `app/sitasi.py` (`mops_laporan`, `mops_cadangan`)
- **Gejala & Akar Masalah (audit awal)**:
  Saat tabel laporan keuangan belum tersedia (`tb.ada == False`), `saham.html:255` merender tautan cadangan dengan memanggil `mops_laporan(kode_saham, None, None, lap)`. Di `app/sitasi.py`, cabang `else` menjalankan `th = int(str(tahun_iso)[:4])`, sehingga `tahun_iso=None` melempar `ValueError: invalid literal for int() with base 10: 'None'`, padahal `mops_cadangan` sudah tersedia.
- **Perbaikan & Verifikasi**:
  `app/templates/saham.html:255` diganti memanggil `mops_cadangan(lap)`, dan `app/sitasi.py` `mops_laporan()` kini menjaga nilai `tahun_iso` (`None`, kosong, `"None"`, atau non-numerik) agar langsung jatuh ke `mops_cadangan(laporan)`. Terverifikasi melalui `scripts/qa_halaman.py` pada `SENTINEL_DATA_DIR` kosong (`84/84`, `0` gagal) dan `tests/test_qa_perbaikan.py` (`TestSitasiFallback`).

---

### Prioritas Tinggi

#### T-1. Filter status & jenis di Feed `/` tidak menyembunyikan baris pada grup tanggal campuran — **Status: Diperbaiki**
- **Lokasi**: `app/static/app.css:48`, `app/static/ui.js:73-78`
- **Gejala & Akar Masalah (audit awal)**:
  `ui.js:73` menyembunyikan baris memakai `b.hidden = !ok;`, namun `app/static/app.css` mendeklarasikan `.baris { display: flex; ... }` tanpa aturan global `[hidden] { display: none !important; }`, sehingga saat satu tanggal memiliki status campuran, baris berstatus `[hidden]` tetap tampil sebagai `display: flex`.
- **Perbaikan & Verifikasi**:
  Menambahkan aturan global `[hidden] { display: none !important; }` di `app/static/app.css:48`. Terverifikasi pada pengujian regresi `TestCssDanUiReview.test_css_memiliki_aturan_hidden_global` serta uji Playwright Chromium interaktif pada grup `.kelompok-tanggal` campuran (`terbit`, `ditahan`, `dilewati` terfilter rapi dengan `display: "none"` dan `offsetHeight: 0`).

#### T-2. Respons `HTTP 401` mode baca-terkunci membocorkan daftar watchlist & sidebar, serta cookie `akses` kurang kuat — **Status: Diperbaiki**
- **Lokasi**: `app/main.py` (`_token_akses`, `_baca_pesan`, `_konteks_kunci`, `_boleh_ubah`, `kunci_baca_middleware`, `_proses_akses`, `akses`, `akses_post`), `app/templates/kunci.html`
- **Gejala & Akar Masalah (audit awal)**:
  Pada mode `SENTINEL_KUNCI_BACA=1`, respons `401` memanggil `konteks()` penuh sehingga HTML `401` tetap membawa sidebar, `#cp-panel`, dan kode saham watchlist; selain itu `POST /akses` mengembalikan `405` dan cookie `akses` menyimpan `config.KODE_AKSES` mentah.
- **Perbaikan & Verifikasi**:
  1. `app/templates/kunci.html` diubah menjadi halaman mandiri minimal (tanpa mewarisi `base.html`) memakai `_konteks_kunci()`, sehingga respons `401` tidak memuat `.rail`, `#cp-panel`, maupun data watchlist.
  2. Mendukung `POST /akses` (`@app.post("/akses")`) bersama form `method="post"` di `kunci.html`, dan mengganti nilai cookie `akses` menjadi digest HMAC-SHA256 via `_token_akses()` yang diverifikasi dengan `hmac.compare_digest()`.
  Terverifikasi melalui `TestR3KunciBaca` (`tests/test_putaran2.py`), `TestKunciBacaKeamanan` (`tests/test_qa_perbaikan.py`), serta alur Playwright penuh (GET `401` bersih, POST salah -> `303`/`401` `.pita.err`, POST benar -> `200` + cookie HMAC 64 karakter hex).

---

### Prioritas Menengah

#### M-1. Chip filter `"Semua"` di `/review` tetap aktif menyala ganda — **Status: Diperbaiki**
- **Lokasi**: `app/templates/review.html:29`, `app/static/app.css`, `app/static/ui.js:156-160`
- **Gejala & Akar Masalah (audit awal)**:
  `review.html:29` memakai `class="chip aktif"`, sedangkan `ui.js:156-160` hanya men-toggle `.on`, sehingga tombol `"Semua"` tetap berlatar navy ganda saat chip lain dipilih.
- **Perbaikan & Verifikasi**:
  Mengganti `class="chip aktif"` menjadi `class="chip on"` di `app/templates/review.html:29`. Terverifikasi lewat `TestCssDanUiReview` dan klik interaktif Playwright Chrome di `/review` (chip `"Semua"` melepas latar `rgb(22, 50, 79)` ke putih saat `"verifikasi"` dipilih).

#### M-2. Handler `async def` chatbot memblokir event loop & mutasi global/cache tanpa penguncian aman — **Status: Diperbaiki**
- **Lokasi**: `app/chat.py` (`kirim_tanya`, `api_tanya`, memanggil `llm.tandai_404`), `app/agent/llm.py` (`_kunci_model`, `_lokal`, `tandai_404`, `_tanya_model`, `_tulis_cache`), `app/review.py` (`_kunci_berkas`, `simpan`)
- **Gejala & Akar Masalah (audit awal)**:
  `kirim_tanya` dan `api_tanya` memanggil `tanya()` (I/O jaringan sinkron + sleep) langsung pada event loop `async def`; fallback model menulis variabel global `_model_sementara` tanpa isolasi thread; serta penulisan cache/review memakai berkas `.tmp` statis tanpa kunci konkurensi.
- **Perbaikan & Verifikasi**:
  1. `kirim_tanya` dan `api_tanya` kini menjalankan `await asyncio.to_thread(tanya, ...)`.
  2. `app/agent/llm.py` memakai `_kunci_model = threading.RLock()`, `_lokal = threading.local()` untuk `model_sementara`, fungsi `tandai_404(model)`, serta file sementara unik PID+TID pada `_tulis_cache` sambil menjaga kompatibilitas API `model_dipakai()` dan `_panggil_gemini(instruksi, dokumen)`.
  3. `app/review.py` memakai `_kunci_berkas = threading.Lock()` dan file sementara unik PID+TID pada `simpan()`.
  Terverifikasi lewat `TestKonkurensiDanPemeriksa` (uji `review.simpan` 16 thread, `llm._tulis_cache` 12 thread, verifikasi worker thread pada `POST /api/tanya`) serta `tests/test_agent.py` & `tests/test_pemutus_thread.py`.

#### M-3. Pemeriksa kata terlarang di `ringkasan.py` salah memblokir kata netral — **Status: Diperbaiki**
- **Lokasi**: `app/ringkasan.py` (`_muat_kata_terlarang`, `periksa_narasi`)
- **Gejala & Akar Masalah (audit awal)**:
  Pencocokan substring `k.lower() in teks.lower()` memblokir kata netral seperti `pembelian`, `buyback`, dan `selling`.
- **Perbaikan & Verifikasi**:
  Mengekstrak `_muat_kata_terlarang()` memakai regex batas kata ASCII dengan pengecualian netral `buyback`/`beli kembali` selaras `chat.TERLARANG`, sembari mempertahankan pemeriksaan kata CJK dan daftar `KATA_TERLARANG`. Terverifikasi lewat `TestKonkurensiDanPemeriksa.test_ringkasan_izinkan_buyback_dan_pembelian`.

#### M-4. Kolom harga di `/watchlist` selalu menampilkan `—` — **Status: Diperbaiki**
- **Lokasi**: `app/main.py` (`watchlist`), `app/templates/watchlist.html:68-77`
- **Gejala & Akar Masalah (audit awal)**:
  Handler `watchlist()` tidak mengisi kunci `"harga"`, sehingga templat `watchlist.html` selalu menampilkan `—`.
- **Perbaikan & Verifikasi**:
  `watchlist()` di `app/main.py` kini mengisi `"harga": harga_cache.get("tutup")` dari satu pemanggilan `pasar.harga_dari_cache(k)` per emiten. Terverifikasi melalui `TestTampilanDanCookie.test_watchlist_memuat_harga_cache`.

#### M-5. Label alasan fallback `"tidak ada kunci API"` bocor dalam bahasa Indonesia ke UI EN/ZH — **Status: Diperbaiki**
- **Lokasi**: `app/i18n.py` (`jj.sebab.tanpa_kunci`), `app/main.py` (filter Jinja `sebab_bahasa`), `app/templates/jejak.html:54`, `scripts/qa_halaman.py`
- **Gejala & Akar Masalah (audit awal)**:
  String mentah `"tidak ada kunci API"` tampil langsung pada `/jejak/{id}?bahasa=en` maupun `zh`, memicu peringatan kebocoran kata Indonesia di `scripts/qa_halaman.py`.
- **Perbaikan & Verifikasi**:
  Menambahkan kunci `"jj.sebab.tanpa_kunci"` pada `app/i18n.py` (`"no API key set"` / `"未設定 API 金鑰"` / `"tidak ada kunci API"`), mendaftarkan filter `sebab_bahasa` di `app/main.py`, dan menerapkannya pada `app/templates/jejak.html:54` (tanpa mengubah payload JSON `/api/jejak/{id}`); sekaligus memperketat `scripts/qa_halaman.py` agar pemindaian kebocoran kata Indonesia pada HTML hanya berjalan bila `content-type` adalah HTML. Hasil `qa_halaman.py`: `84/84` dengan `0` peringatan.

#### M-6. Inkonsistensi templat, lencana duplikat, nilai `0`, & cookie profil risiko — **Status: Diperbaiki**
- **Header & pembungkus tabel `cari_hasil.html`**: `app/templates/cari_hasil.html` kini membungkus tabel di dalam `<div class="tabel-geser">`, memakai `{{ t('pf.en') }}` dan `{{ t('pf.bursa') }}`, serta mengganti `var(--latar-2)` yang tidak terdefinisi ke `var(--netral-100)`.
- **Lencana `HELD` di `/review`**: pil duplikat `<span class="lencana l-dilewati mono">HELD</span>` pada `app/templates/review.html:50-53` diganti menjadi label meta mono redup agar tidak menjadi lencana ganda sambil tetap mempertahankan teks status `"HELD"` sesuai kontrak `tests/test_agent.py`.
- **Nilai finansial `0` di `saham.html`**: `app/templates/saham.html:165, 175-176` diubah ke pemeriksaan eksplisit `is not none` agar angka `0` tetap tampil.
- **Cookie `risiko` tidak konsisten**: helper bersama `_simpan_cookie_risiko()` ditambahkan di `app/main.py` untuk menyimpan pilihan `?risiko=` ke cookie pada rute `/ambang` dan `/valuasi/{kode}` (catatan koreksi dari temuan awal: rute `/peringatan/{pengenal}` sebenarnya sudah menyetel cookie `risiko`, sedangkan yang belum sebelumnya adalah `/ambang` dan `/valuasi/{kode}`). Terverifikasi lewat `TestCssDanUiReview` dan `TestTampilanDanCookie`.

---

### Prioritas Rendah & Catatan Desain

#### R-1. Endpoint `POST /api/tanya` dan `POST /tanya` terbuka ketika `KUNCI_BACA=0` — **Status: Catatan Tetap (Prioritas Rendah)**
- **Lokasi**: `app/chat.py` (`kirim_tanya`, `api_tanya`)
- **Keterangan**: Saat `SENTINEL_KODE_AKSES` diset dengan `KUNCI_BACA=0`, seluruh mutasi data terkunci, tetapi `POST /api/tanya` (`200`) dan `POST /tanya` (`303`) masih bisa dipanggil publik tanpa cookie akses (meski dibatasi `MAX_PER_HOUR=60` untuk panggilan model Gemini dan menulis ke `DATA_DIR/traces_chat/`). Dokumentasikan perilaku ini atau batasi juga jika kuota API ingin dijaga ketat.

#### R-2. Pemotongan riwayat chat 1500 karakter sebelum verifikasi ulang HMAC — **Status: Catatan Tetap (Prioritas Rendah)**
- **Lokasi**: `app/chat.py` (`_bersihkan_riwayat`, `_teks_asisten_sah`)
- **Keterangan**: `_bersihkan_riwayat` memverifikasi HMAC terhadap `teks_asli`, lalu menyimpan versi terpotong `teks = teks_asli.strip()[:1500]`. Ketika panjang jawaban asisten suatu saat melampaui 1500 karakter, pemeriksaan HMAC ulang di `_teks_asisten_sah` terhadap `teks` hasil potongan akan gagal dan membuang angka referensi giliran tersebut.

#### R-3. Console `404` karena `/favicon.ico` belum tersedia — **Status: Catatan Tetap (Prioritas Rendah)**
- **Lokasi**: `app/templates/base.html`, `app/main.py`
- **Keterangan**: Setiap pembukaan sesi baru di Chrome/Playwright memunculkan 1 error konsol `404 Not Found` untuk `/favicon.ico`. Opsional untuk menambahkan `<link rel="icon" ...>` SVG data-URI ringan di `base.html` atau route `/favicon.ico`.

---

## 4. Temuan Kebersihan Rilis & De-identifikasi (Blocker Submisi)

1. **De-identifikasi di luar `app/` — Status: Diperbaiki**:
   - Seluruh `46` baris berisi inisial anotator pada `eval/gold.csv` telah diganti menjadi `,Analis 1,`.
   - `tests/test_deidentifikasi.py` diperluas agar turut memindai folder `eval/` (termasuk `.csv`).
   - URL repositori GitHub yang memuat nama pengguna anggota tim pada `README.md` (baris `31`, `60`, dan `89`) telah dinetralkan menjadi `<repository-url> napaincu-ai-comp`.
   - Verifikasi `rg -in` dengan pola nama anggota tim, nama pengguna GitHub, dan inisial anotator ke `README.md eval/ app/` menghasilkan `0` kecocokan.
2. **Berkas API key & artefak lokal untracked di root — Status: Diamankan via `.gitignore` / `.dockerignore` (berkas tetap dipertahankan di disk)**:
   - `"API KEY .txt"` dan `scripts/result.json` telah ditambahkan ke `.gitignore` dan `.dockerignore` agar tidak ikut ter-commit atau masuk ke Docker build context.
   - Atas permintaan/batasan kerja, `"API KEY .txt"` maupun berkas lokal untracked lain (`Panduan-Gold-Set-FEAF.pdf`, `Rapat-Perdana-AAIC-2026.pdf`, `Rapat-Perdana-AAIC-2026.pptx`, `gold-set-FEAF.xlsx`, `gold-set-FEAF(1).xlsx`, `scripts/result.json`, `.agents/`, `skills-lock.json`, `docs/feaf_snapshot/`, `docs/draf-slide-tambahan.md`) **tidak dihapus dari disk**; pastikan berkas-berkas tersebut tidak ikut terkemas bila Anda membuat arsip `.zip`/tarball secara manual di luar `git`.
3. **Sinkronisasi versi & angka unit test — Status: Diperbaiki**:
   - `app/versi.py`, `CHANGELOG.md`, dan `README.md` telah disinkronkan ke versi `1.1.0`.
   - `README.md:149` diperbarui menjadi `293 tests` sesuai hasil `unittest discover -s tests -v`.

---

## 5. Ringkasan Status Tindak Lanjut

1. **Selesai (`K-1`, `T-1`, `T-2`, `M-1` s.d. `M-6`, Bagian 4)**: seluruh bug terverifikasi dan blocker kode/de-identifikasi telah diperbaiki, ditambah 14 uji regresi di `tests/test_qa_perbaikan.py`, dan lolos verifikasi penuh (`293` unit test pada data lokal maupun `SENTINEL_DATA_DIR` kosong, `qa_halaman.py` `84/84` dengan `0` peringatan di kedua kondisi, `qa_responsif.py` `0` temuan, `evaluasi.py`, `uji_serangan.py`, serta cek interaktif Playwright).
2. **Opsional (`R-1` s.d. `R-3`)**: tiga catatan desain prioritas rendah tetap dibiarkan sesuai cakupan saat ini dan tidak menghambat kesiapan rilis.
3. **Tindakan lokal sebelum pengemasan manual**: tinjau `git status`/`git diff` sebelum commit dan jangan sertakan `"API KEY .txt"` maupun berkas untracked non-repositori apabila membuat arsip submisi di luar `git`.
