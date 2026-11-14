# Backlog QA manual (v1.1)

Temuan QA manual Afinzaki, dengan penyebab dan action plan untuk Antigravity (Gemini).
Kerjakan berurutan dari atas. Setiap item: kerjakan, jalankan `python3 -m unittest discover -s tests`
dan `python3 scripts/qa_halaman.py`, commit dengan judul yang disebut, `git pull --rebase`, push ke
`main`, lalu ubah status item di tabel ini.

**Cara menjalankan.** Tempel ke Antigravity:

```text
Baca docs/backlog-qa-manual.md. Kerjakan semua item berstatus "Belum" dari atas ke bawah, ikuti
action plan di tiap item, dan patuhi batas berkasnya. Setelah tiap item: tes, commit, git pull
--rebase, push, lalu ubah status item itu menjadi "Selesai (<hash commit>)" di tabel.
```

| No | Temuan | Status |
|---|---|---|
| QA-1 | Review feed: lencana jumlah, alasan teknis, arsip mendominasi, kotak cari, tombol, penafian | Selesai (`a565ac0`) |
| QA-2 | Narasi AI tab ringkasan tidak muncul untuk profil konservatif dan agresif | Selesai (`cadb9e0`) |
| QA-3 | Detail peringatan: kotak "Why it was held" sulit dibaca pemula (cek diulang, istilah teknis, lencana ganda) | Selesai (`da040df`) |
| QA-4 | De-identifikasi: nama anggota tim di kode, README, dan dokumen yang diserahkan | Selesai (`ddd5d2d`) |
| QA-5 | 4 tes gagal di mesin lain: tes chat/UI baru bergantung pada data lokal | Selesai (`4dbc425`) |
| QA-6 | Menu samping kurang lebar untuk isinya, tampilan tidak responsif di ponsel | Selesai (`3179254`) |
| QA-7 | QA menyeluruh v1.1.0 (`docs/laporan-qa.md`): K-1 crash tab keuangan kosong, T-1 filter feed `[hidden]`, T-2 halaman 401 bocor + cookie akses mentah, M-1..M-6 | Selesai (`6a0d36f`) |
| R-1 | `POST /api/tanya` dan `POST /tanya` terbuka saat `SENTINEL_KODE_AKSES` diset dan `KUNCI_BACA=0` | Belum (opsional) |
| R-2 | Riwayat chat dipotong 1500 karakter setelah verifikasi HMAC; pemeriksaan ulang gagal untuk jawaban panjang | Belum (opsional) |
| R-3 | `/favicon.ico` membalas 404 (error konsol di setiap sesi baru) | Belum (opsional) |

Rincian QA-7 dan R-1..R-3 (lokasi, akar masalah, verifikasi) ada di `docs/laporan-qa.md` bagian 3.

---

## QA-1 · Review tampilan feed

Dari foto layar feed setelah U2–U3 (12 Nov). Batas: hanya template, `app/static/app.css`,
`app/static/ui.js`, `app/teks/ui.py`. Jangan ubah Python lain.

1. Lencana jumlah di menu "Alerts" harus konsisten dengan kartu ringkasan (sekarang menu 1094,
   kartu 1/5/13). Tampilkan jumlah Held untuk lingkup yang sama, bukan total semua pengumuman.
2. Alasan di baris feed jangan teknis (contoh sekarang: "Magnitude plausible — 60,400 vs 1,272,410
   NT$ million = 0.05× (OUTSIDE the 0.20–3× band)…", "Confidence 0.45 is below the threshold 0.55 for
   clause 20 (0 👎, 0 👍)"). Buat kunci baru di `app/teks/ui.py` `ui.alasan_polos.<kode>` untuk kode
   alasan yang paling sering (lihat `alasan_i18n.kode`: cek.besaran, akhir.di_bawah_ambang,
   saring.di_luar, tahan.tanpa_angka, tahan.tanpa_valuasi, cek.mu, akhir.modal_kecil,
   saring.antar_grup, sinyal risiko serius) berisi satu kalimat polos tiga bahasa. Tampilkan itu di
   feed; alasan teknis asli hanya di halaman detail. Bila kode tidak dikenal, pakai alasan asli.
3. Bawaan feed hanya menampilkan Published dan Held; Archived disembunyikan dan bisa dibuka dengan
   klik kartu Archived atau chip "Tampilkan yang diarsip" (sisi klien).
4. Kotak cari: placeholder pendek ("Search code or name" / "搜尋代號或名稱" / "Cari kode atau nama"),
   huruf Instrument Sans, tidak terpotong.
5. Tombol Re-run dan Check now diberi penjelasan singkat (tooltip ⓘ atau teks kecil): Re-run =
   proses ulang data yang sudah ada, Check now = tarik pengumuman baru dari bursa. Re-run jadi
   tombol sekunder yang lebih kecil.
6. Penafian di feed dibuat satu baris dengan tautan "selengkapnya" yang membuka teks lengkap.
7. Foto layar ulang feed (tiga bahasa, 1440 dan 390) ke `docs/ui/sesudah/`.

Commit: `UI: QA-1 perbaikan review feed`.

## QA-2 · Narasi AI tidak muncul untuk konservatif dan agresif

**Gejala.** Di `/saham/<kode>?tab=ringkasan`, memilih Conservative atau Aggressive tidak
menampilkan kotak narasi AI. Moderate muncul.

**Penyebab (dipastikan dari kode).** Narasi dibuat Gemini dari fakta + kalimat kecocokan profil,
jadi tiap profil butuh panggilan baru; moderat muncul karena sudah ada di cache.
`app/agent/llm.py` `mulai_jalan(maks)` mengisi variabel GLOBAL `_jatah_sisa`, `_gagal_beruntun`,
`_mulai_jalan_t` untuk membatasi satu jalan pipeline (40 panggilan, 90 detik, 3 gagal beruntun),
dan tidak pernah dilepas setelah pipeline selesai. Setiap `llm.tanya()` berikutnya dari permintaan
web (`app/ringkasan.py` `narasi()`) ditolak pemutus ("batas waktu model per jalan habis", atau jatah
0 setelah `_hasil_awal_tanpa_model`). `narasi()` mengembalikan teks None dan `saham.html`
menyembunyikan kotak narasi tanpa alasan. Chat tidak terkena (memakai `chat._gemini`).

**Action plan.**
1. `app/agent/llm.py`: status pemutus jadi milik THREAD yang menjalankan pipeline. Pakai
   `threading.local()` untuk jatah_sisa, gagal_beruntun, mulai_jalan_t. Tambah `selesai_jalan()`
   yang mengosongkan ketiganya, dan context manager `jalan(maks)` yang memanggil `mulai_jalan` lalu
   `selesai_jalan` di `finally`. Panggilan dari thread lain tidak terkena jatah pipeline.
2. `app/main.py`: di tiga tempat yang memanggil `llm.mulai_jalan(...)` lalu
   `pipeline.jalankan_semua()` (`_hasil_awal_tanpa_model` dan dua cabang di `hasil()`), ganti dengan
   `with llm.jalan(...)`. Jangan ubah logika lain.
3. `app/templates/saham.html` tab ringkasan: bila `rk.narasi.teks` kosong tetapi
   `rk.narasi.alasan_kode` ada, tampilkan satu baris kecil abu-abu di tempat kotak narasi:
   `t(rk.narasi.alasan_kode)` (kunci `rk.alasan.tanpa_model` / `rk.alasan.gagal` /
   `rk.alasan.ditolak`; pastikan ada di tiga bahasa, tambahkan di `app/teks/ui.py` bila belum ada).
   Jangan tampilkan isi teknis `rk.narasi.alasan`.
4. Tes baru `tests/test_pemutus_thread.py` (tanpa jaringan, mock fungsi panggilan Gemini yang dipakai
   `llm.tanya`):
   a. Thread A: `with llm.jalan(0)`: `llm.tanya` → `GagalModel`. Setelah blok selesai, `llm.tanya`
      di thread yang sama berhasil.
   b. Saat thread A masih di dalam `with llm.jalan(0)`, `llm.tanya` dari thread B berhasil.
   c. Setelah `with llm.jalan(40)` yang dimulai >90 detik lalu (patch `time.monotonic`), panggilan
      dari thread lain tetap berhasil.
   d. `ringkasan.susun("2330", "en", "agresif", ...)` dengan model di-mock mengembalikan
      `{"ringkasan": "..."}` yang lolos `periksa_narasi` → `rk["narasi"]["sumber"] == "model"`.
   e. `tests/test_agent.py` `test_pemutus_setelah_tiga_gagal_beruntun` tetap lulus (sesuaikan hanya
      bila perlu memakai `llm.jalan`).
5. Tes semua + QA halaman harus lulus.

**Batas.** Jangan ubah `app/chat.py`, `app/agent/pipeline.py`, atau angka ambang mana pun.

Commit: `Fix: QA-2 pemutus model hanya di thread pipeline; narasi AI untuk semua profil`.

**Cek setelah deploy.** `/saham/2330?tab=ringkasan` → Conservative lalu Aggressive: kotak narasi
muncul (panggilan pertama ±5 detik). Ulangi di emiten lain. Bila tetap tidak muncul, baris
penjelasan sebab sekarang tampil; kirim isinya ke Claude.

## QA-3 · "Why it was held" sulit dibaca pemula

**Gejala** (`/peringatan/2330-2026-11-10-220514`, 補充…資本預算案之實際執行情形). Kotak "WHY IT WAS
HELD: A VERIFIER CHECK FAILED" berisi kalimat teknis yang sama empat kali ("Magnitude plausible —
60,400 vs 1,272,410 NT$ million = 0.05× (OUTSIDE the 0.20–3× band). A single filing that moves an
input this far is almost certainly a unit or item error; …"). Di kanan atas ada dua lencana untuk hal
yang sama: "Held for review" dan "HELD".

**Penyebab.** Template menampilkan `alasan` gabungan (satu kalimat per cek gagal per angka) apa
adanya. Tidak ada pengelompokan per jenis cek dan tidak ada versi bahasa awam. Lencana kedua adalah
`state` mesin (label teknis).

**Action plan** (batas: hanya `app/templates/peringatan.html`, `app/static/app.css`,
`app/teks/ui.py`; jangan ubah Python lain, jangan ubah logika pemeriksa):
1. Kotak "Kenapa ditahan" menampilkan **satu kalimat polos per jenis cek yang gagal** (kelompokkan
   menurut kode cek di `muatan.ditolak[].cek[]` yang `lolos == false`, pakai `nama_i18n.kode` /
   `alasan_i18n.kode` dan `alasan_i18n.param`), bukan per angka. Kunci baru di `app/teks/ui.py`,
   tiga bahasa, misalnya:
   - `ui.polos.cek.besaran.kecil`: "This filing lists {n} amount(s) of {min}–{maks} NT$ million, only
     {pmin}–{pmaks}% of the company's yearly {input} ({lama} NT$ million). One announcement rarely
     moves a company's yearly figure that much, so the agent did not use these amounts and asks an
     analyst to check them." (rasio < 0.2)
   - `ui.polos.cek.besaran.besar`: versi untuk rasio > 3 ("…{x} times the company's yearly {input}…
     likely a unit mistake…").
   - `ui.polos.cek.mu`: "The amount is in {mu}. FEAF does not convert currencies, so an analyst
     checks it."
   - `ui.polos.cek.satuan`, `ui.polos.cek.kutipan`, `ui.polos.cek.angka`, `ui.polos.cek.label`,
     `ui.polos.cek.konversi`: satu kalimat polos masing-masing.
   - Fallback: bila kode cek tidak dikenal, tampilkan `tr(nama_i18n)` saja (tanpa alasan teknis).
   Hitung `n`, `min`, `maks`, `pmin`, `pmaks` di template dari parameter cek (nilai baru, nilai lama,
   rasio) yang sudah ada; format angka dengan filter `rb`. Nama input (`capex`, `cash`, `debt`)
   lewat kunci yang sudah ada atau kunci baru `ui.input.<nama>`.
2. Di bawah kalimat polos: satu baris tindakan, "Yang bisa Anda lakukan: buka dokumen asli dan
   bandingkan angkanya, lalu setujui atau tolak di Review →" (tautan `/review`).
3. Kalimat teknis asli tetap ada tetapi dilipat: `<details>` "Detail teknis pemeriksaan (4)",
   satu baris per cek, tanpa pengulangan kalimat penjelasan yang sama (tampilkan penjelasan sekali,
   lalu daftar angkanya).
4. Lencana: tampilkan hanya lencana status ("Held for review"). Label `state` mesin ("HELD")
   dipindah ke bagian detail teknis / jejak audit.
5. Uji tiga bahasa dengan: kasus contoh besaran (pengumuman 2330 di atas atau fixture yang gagal
   `cek.besaran`), mata uang asing (fixture `2330-2026-09-19-4`), dan pengumuman terbit. Tambahkan
   ke `tests/test_ui.py`: halaman detail kasus besaran tidak memuat "OUTSIDE the 0.20" di luar
   `<details>`, dan memuat kalimat polos di tiga bahasa.
6. Foto layar sebelum/sesudah (tiga bahasa, 1440 dan 390) ke `docs/ui/`.

Commit: `UI: QA-3 alasan ditahan dalam bahasa polos`.

**Cek setelah deploy.** Buka pengumuman 2330 di atas: kotak berisi satu kalimat yang bisa dipahami
tanpa istilah teknis, satu lencana, detail teknis terlipat.

## QA-4 · De-identifikasi materi yang diserahkan

**Aturan.** FAQ final AAIC 2026 (A2): "all materials must be de-identified"; aturan umum melarang
data pribadi yang belum di-deidentifikasi di dokumen maupun kode.

**Temuan.** Nama depan anggota tim muncul di kode dan dokumen: "Afinzaki" (±23 berkas), "Ferry"
(±17), "Patrice" (±20), termasuk `README.md`, `app/ringkasan.py`, `app/agent/screen.py`,
`app/agent/sinyal.py`, `app/ambang_profil.py`, `app/teks/tata_kelola.py`, `design/README.md`.

**Action plan** (hanya teks: komentar, docstring, dokumen; jangan ubah logika atau angka):
1. Ganti nama dengan peran, konsisten di semua berkas yang **bukan** `docs/prompt-*`,
   `docs/laporan-antigravity-*`, `docs/konteks-sesi.md`, `docs/rekap.md`, `docs/rencana-*`
   (berkas kerja internal): "Afinzaki" → "team lead", "Ferry" / "Patrice" → "finance team member"
   / "the finance team" (Bahasa Indonesia: "ketua tim", "anggota tim keuangan"). Prioritas:
   `README.md`, `CHANGELOG.md`, `LICENSE`, semua `app/**`, `scripts/**`, `design/README.md`,
   `docs/laporan-evaluasi.md`, `docs/hasil-gold-set.md`, `docs/pemetaan-pasal.md`,
   `docs/pengungkapan-pihak-ketiga.md`, `docs/untuk-tim/*` (html; PDF/XLSX dibiarkan, catat di laporan).
2. Teks yang tampil di aplikasi (`app/teks/*.py`, template) tidak boleh memuat nama anggota tim.
3. `grep -rIn "Afinzaki\|Ferry\|Patrice" --exclude-dir=.git app scripts README.md CHANGELOG.md LICENSE design docs/laporan-evaluasi.md docs/hasil-gold-set.md docs/pemetaan-pasal.md docs/pengungkapan-pihak-ketiga.md`
   harus kosong. Tambah tes `tests/test_deidentifikasi.py` yang menjalankan pemeriksaan yang sama
   untuk `app/` dan `README.md`.
4. Tes semua + QA halaman lulus.

Commit: `Docs: QA-4 de-identifikasi nama anggota tim`.

## QA-5 · Tes bergantung pada data lokal mesin

**Gejala** (13 Nov, `python3 -m unittest discover -s tests` di mesin Claude, data lokal berbeda):
4 gagal, lulus di laptop Antigravity.
- `test_chat_percakapan.TestChatPercakapanC3.test_semua_alat_menu_dengan_data_fixture_dan_tanpa_mengubah_data_dir` (False is not true)
- `test_chat_percakapan.TestChatPercakapanC4.test_panel_hadir_di_semua_halaman_kecuali_tanya`
  (mengharapkan `data-kode="2330"`, halaman yang terbuka milik 3432 karena urutan data lokal)
- `test_chat_percakapan.TestChatPercakapanC6Evaluasi.test_evaluasi_percakapan_12_skenario_3_bahasa` (30 != 36)
- `test_ui.TestUI.test_alasan_ditahan_bahasa_polos` (404: id pengumuman yang dipakai tidak ada)

**Penyebab.** Tes memakai `config.DATA_DIR` asli (watchlist, `data/parsed`, cache) dan memilih
pengumuman "pertama" dari data yang ada, bukan fixture tetap.

**Action plan** (hanya berkas tes; jangan ubah kode aplikasi kecuali ada bug sungguhan):
1. Setiap kelas tes di `tests/test_chat_percakapan.py` dan `tests/test_ui.py` memakai DATA_DIR
   sementara (`tempfile.TemporaryDirectory`) yang hanya berisi fixture (`data/fixtures/`), dengan pola
   yang sama seperti `tests/test_agent.py` (setUpClass: simpan nilai config asli, arahkan
   `config.DATA_DIR`, `PARSED_DIR`, `TRACE_DIR`, `tarik.WATCHLIST_FILE`, cache valuasi/pasar ke folder
   sementara; reset `main._cache = None`; tearDownClass mengembalikan semuanya).
2. Id pengumuman dan kode saham di tes ditulis tetap dari fixture (mis. `2330-2026-09-18-1`), tidak
   diambil dari "data pertama".
3. Tidak ada tes yang menyentuh jaringan (patch `pasar`, FinMind, Gemini).
4. Bukti: jalankan tes dua kali, sekali dengan `SENTINEL_DATA_DIR` menunjuk folder kosong baru dan
   sekali dengan data lokal penuh; keduanya harus lulus semua.

Commit: `Test: QA-5 tes chat/UI terisolasi dari data lokal`.

## QA-6 · Menu samping kurang lebar dan tampilan ponsel

**Gejala** (QA manual Afinzaki, 13 Nov): menu samping terlalu sempit untuk isinya; tampilan tidak
responsif di ponsel.

**Kondisi kode.** `app/static/app.css`: `.rail { width: 240px }`; di bawah 900 px rail menjadi laci
(`.rail.buka`), plus beberapa media query per komponen. Belum ada pemeriksaan otomatis untuk
luapan horizontal.

**Action plan** (batas: `app/templates/base.html` kecuali baris include panel chat,
`app/static/app.css`, `app/static/ui.js`, `scripts/qa_halaman.py`, `tests/test_ui.py`):
1. Ambil foto layar semua halaman utama (/, /watchlist, /review, /ambang, /tanya,
   /peringatan/<terbit>, /peringatan/<ditahan>, /jejak/<id>, /saham/2330 enam tab, /valuasi/2330)
   di lebar 390, 768, 1024, 1440, tiga bahasa, ke `docs/ui/qa6-sebelum/`. Catat setiap masalah.
2. Menu samping desktop: lebar 264–280 px; nama emiten, label menu, dan teks status tidak terpotong
   atau bertumpuk di tiga bahasa (中文 dan Bahasa Indonesia paling panjang). Isi menu bisa digulir
   sendiri bila tinggi layar kecil; kotak status tetap terbaca.
3. Ponsel (< 900 px): bilah atas tetap terlihat; tombol ☰ membuka laci yang bisa ditutup dengan ✕,
   klik latar, dan tombol Esc; body tidak ikut tergulir saat laci terbuka; target sentuh ≥ 40 px.
4. Tidak boleh ada luapan horizontal halaman di 390 px: tabel lebar (keuangan, sensitivitas, ambang,
   watchlist) digeser di dalam kartunya (`overflow-x: auto`), tab saham bisa digeser, kartu
   ringkasan dan dua kolom menjadi satu kolom, tombol membungkus ke baris baru, teks panjang
   (judul pengumuman Mandarin, URL sumber) dibungkus.
5. Panel chat (milik putaran chat, jangan ubah berkasnya) tidak boleh tertutup elemen lain;
   cek di 390 px bahwa tombol bulat dan panel layar penuh tetap bisa dipakai.
6. Tambah pemeriksaan otomatis: skrip Playwright `scripts/qa_responsif.py` yang membuka halaman di
   atas pada 390 dan 1440 px dan gagal bila `document.documentElement.scrollWidth > innerWidth + 1`
   atau ada label menu yang terpotong (`scrollWidth > clientWidth` pada `.nav a`, `.daftar-saham a`).
   Jalankan dengan server lokal `SENTINEL_SERTAKAN_CONTOH=1`.
7. Foto layar sesudah ke `docs/ui/qa6-sesudah/`, tes + `qa_halaman.py` + `qa_responsif.py` lulus.

Commit: `UI: QA-6 menu lebih lebar dan tampilan ponsel responsif`.
