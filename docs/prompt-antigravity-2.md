# Prompt Antigravity putaran 2 (R1, R2, R3, D-a, D-b, D-c, B3, R4)

Untuk Afinzaki: salin seluruh isi kotak di bawah ke Antigravity, dengan folder repo ini
sebagai workspace. Prompt ini ditulis supaya bisa dijalankan dengan effort rendah: setiap
item punya langkah, berkas, dan pemeriksa yang pasti. Cara mengecek hasilnya ada di
bagian paling bawah berkas ini.

---

````text
# 0. Persiapan (wajib, urut)

Kamu melanjutkan proyek FEAF (Agentic AI Investment Assistant, NAPAI AAIC 2026, track
SYSTEX). Claude juga bekerja di repo ini, di branch `main`, pada waktu yang sama.

0.1 Pasang dua skill, lalu pakai sepanjang tugas:
    - anti-slop untuk menulis kode dan UI: `agy plugin install https://github.com/miqdadbadjuber/anti-slop`
      Pakai mode "during". Arah tampilan ada di DESIGN.md di akar repo; baca sebelum
      menyentuh template atau CSS. Jangan membuat gaya baru.
    - humanizer untuk menulis laporan dan dokumen: `npx skills add blader/humanizer`
      (kalau perintah itu gagal, salin SKILL.md dari https://github.com/blader/humanizer
      ke folder skill Antigravity). Panggil /humanizer pada setiap berkas .md yang kamu
      tulis, sebelum commit.
    Kalau salah satu skill tidak bisa dipasang, lanjutkan tugas dan tulis hal itu di laporan.

0.2 Baca berkas ini, urut: docs/rencana-dan-status.md, docs/konteks-sesi.md,
    DESIGN.md, docs/prompt-antigravity.md (aturan putaran 1 tetap berlaku),
    docs/valuasi-otomatis.md, app/valuasi_otomatis.py, app/store.py, app/main.py,
    app/tarik.py (fungsi periksa_sekarang), app/agent/llm.py (fungsi tanya).

0.3 Jalankan:
        git pull --rebase origin main
        python3 -m unittest discover -s tests
    Hasil harus "OK" dengan 107 tes. Kalau tidak, BERHENTI dan tulis di laporan.

# 1. Aturan kerja

- Kerjakan item urut sesuai nomor di bagian 3. Satu item = satu commit (atau lebih),
  pesan commit berbahasa Indonesia dengan ID item di depan, contoh "R1: beta dari harga
  resmi TWSE/TPEx".
- Sebelum setiap push: `git pull --rebase origin main`, jalankan semua tes, baru
  `git push origin main`. Jangan push --force. Jangan buat PR.
- Item dianggap selesai hanya bila SEMUA pemeriksanya lulus. Kalau sebuah pemeriksa gagal
  dua kali setelah kamu perbaiki, berhenti di item itu, tulis sebabnya di laporan, lalu
  lanjut ke item berikutnya yang tidak bergantung padanya.
- Dilarang: menghapus tes, melewati tes (skip), melonggarkan assert supaya lulus, atau
  mengubah tes lama kecuali di tempat yang disebut eksplisit di item.
- Tidak ada API key, token, kata sandi, atau data pribadi di kode, tes, dokumen, atau
  commit. Nama pejabat emiten, juru bicara, akuntan, email pribadi termasuk data pribadi.
- Tes tidak boleh menyentuh jaringan. Simpan sampel kecil di tests/data/ dan patch fungsi
  ambil. Cek dengan menjalankan tes saat Wi-Fi mati.
- Semua teks yang tampil wajib tiga bahasa lewat app/i18n.py (English, 繁體中文,
  Bahasa Indonesia), placeholder sama di ketiganya. Kunci BARU jangan ditulis di
  app/i18n.py: taruh di berkas sendiri app/teks/<nama>.py berisi
  `T = {"kunci": ("English", "中文", "Indonesia"), ...}` (dimuat otomatis, lihat
  app/teks/__init__.py). Satu-satunya perubahan di app/i18n.py adalah mengganti teks
  kunci rk.p.hati dan rk.p.aman (R2).
- Tidak ada label beli/jual. Merah = naik, hijau = turun.
- Jeda antar-permintaan ke situs bursa minimal 2 detik (TWSE memblokir IP yang terlalu
  sering). Jangan diturunkan.

# 2. Pembagian berkas putaran ini

Milikmu: app/harga_resmi.py (baru), app/valuasi_otomatis.py, scripts/valuasi_otomatis.py,
app/store.py, app/config.py (tambah setelan baru saja), app/tarik.py (hanya fungsi
periksa_sekarang), app/agent/llm.py (hanya jatah panggilan per jalan, lihat D-a), scripts/dcf.py (hanya satu
baris di D-c),
app/main.py (bagian yang disebut di item), semua template KECUALI app/templates/chat.html,
app/static/app.css (hanya menambah di akhir), scripts/impor_arsip.py (baru),
scripts/cek_finmind_resmi.py (baru), app/teks/antigravity.py (baru, teks tiga bahasa),
tests/test_putaran2.py (baru), tests/data/* (sampel
baru), docs/pengungkapan-pihak-ketiga.md (baru), docs/laporan-antigravity-2.md (baru),
baris status R1, R2, R3, D-a, D-b, D-c, B3, R4 di docs/rencana-dan-status.md.

Milik Claude, jangan disentuh: app/chat.py, app/templates/chat.html, tests/test_chat.py,
scripts/evaluasi.py, docs/diagram*, app/agent/ selain llm.py, app/umpan_balik.py,
app/review.py, app/ringkasan.py KECUALI teks kunci rk.p.* di i18n (R2), README.md.
Satu baris `app.include_router(...)` di akhir app/main.py juga milik Claude.

tests/test_agent.py hanya boleh diubah di dua tempat yang disebut di item D-a dan D-b.

# 3. Item

## R1. Beta dari harga harian resmi TWSE/TPEx (Yahoo dihapus)

Kenapa: keputusan tim, supaya tidak bergantung pada pihak ketiga. Endpoint Yahoo tidak
resmi dan menolak permintaan (HTTP 429) dari sebagian jaringan.

Sumber resmi (sudah dicek bisa diakses dari luar Taiwan, 10 Nov):
- Saham TWSE, satu bulan per permintaan:
  https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date=YYYYMM01&stockNo={kode}&response=json
  Kunci "data": baris [日期 (ROC, "114/10/01"), 成交股數, 成交金額, 開盤價, 最高價,
  最低價, 收盤價, 漲跌價差, 成交筆數, 註記]. Harga penutupan = indeks 6.
- Indeks TAIEX, satu bulan per permintaan:
  https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date=YYYYMM01&response=json
  Baris [日期, 開盤指數, 最高指數, 最低指數, 收盤指數]. Penutupan = indeks 4.
- Saham TPEx, satu bulan per permintaan:
  https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={kode}&date=YYYY/MM/01&response=json
  Kunci "tables"[0]["data"]: [日期, 成交張數, 成交仟元, 開盤, 最高, 最低, 收盤, 漲跌, 筆數].
  Penutupan = indeks 6.
Angka memakai koma ribuan; hapus koma. Tanggal ROC: tahun + 1911.

Langkah:
1. Buat app/harga_resmi.py:
   - `harian(kode: str, bursa: str, bulan: str) -> list[tuple[str, float]]`
     (bulan "YYYYMM", hasil [(tanggal ISO, close)]). bursa "TWSE" atau "TPEx".
   - `taiex(bulan: str) -> list[tuple[str, float]]`.
   - Cache per bulan di `DATA_DIR/harga_harian/{bursa}-{kode}-{YYYYMM}.json` dan
     `DATA_DIR/harga_harian/TAIEX-{YYYYMM}.json`. Bulan yang sudah lewat disimpan
     permanen (tidak pernah diambil ulang). Bulan berjalan TTL 12 jam.
   - Jeda 2 detik antar-permintaan jaringan (tidak berlaku untuk cache).
   - Galat jaringan atau JSON rusak: kembalikan [] dan catat sebab; jangan melempar
     ke pemanggil.
   - Tentukan bursa dari `pasar.harga(kode)["bursa"]` (TWSE/TPEx).
2. Di app/valuasi_otomatis.py ganti sumber beta:
   - Ambil 25 bulan terakhir (2 tahun + bulan berjalan) untuk saham dan TAIEX.
   - Return mingguan: ambil harga penutupan hari bursa TERAKHIR tiap minggu ISO
     (tahun, minggu) untuk saham dan indeks, cocokkan minggu yang ada di keduanya,
     return = close_t / close_{t-1} − 1.
   - beta = kovarians(saham, indeks) / varians(indeks) (pakai rumus sampel n−1 di keduanya).
   - Kurang dari 52 pasangan minggu, atau sumber gagal: beta 1,0, `beta_cadangan: true`,
     dan alasan (kode i18n).
   - `sources.beta` berisi URL endpoint resmi yang dipakai + jumlah minggu + rentang tanggal.
   - Hapus semua pemakaian Yahoo (YAHOO_CHART_URL dan fungsinya). Hapus
     tests/data/yahoo_sampel.json bila tidak dipakai lagi; sesuaikan tes B2 di
     tests/test_valuasi_otomatis.py supaya memakai sampel harga resmi.
3. Simpan sampel kecil untuk tes: tests/data/harga_resmi_sampel.json berisi 3 bulan
   STOCK_DAY 2330, 3 bulan MI_5MINS_HIST, dan 3 bulan tradingStock 6488 (respons asli
   dipotong seperlunya).

Pemeriksa R1 (semua wajib lulus):
- Tes baru di tests/test_putaran2.py:
  - `test_r1_urai_twse_tpex_taiex`: urai sampel tiga sumber → tanggal ISO benar, close
    float, koma dibuang.
  - `test_r1_beta_dari_deret_buatan`: deret indeks acak (seed tetap) dan saham =
    1,5 × return indeks → beta 1,50 ± 0,01.
  - `test_r1_beta_cadangan_bila_kurang_52_minggu`: 30 minggu → beta 1,0, cadangan true.
  - `test_r1_cache_bulan_lalu_tidak_diambil_ulang`: panggil dua kali, fungsi ambil
    (dipatch) hanya terpanggil sekali untuk bulan lalu.
  - `test_r1_tanpa_yahoo`: `grep` isi app/ dan scripts/ tidak memuat "yahoo" (huruf kecil).
- QA manual: `python3 scripts/valuasi_otomatis.py 2330 --banding` → beta bukan cadangan,
  jumlah minggu ≥ 100; tulis nilai beta dan jumlah minggu di laporan.
- QA manual: satu emiten TPEx (mis. 6488) → beta bukan cadangan.

## R2. Penafian di semua halaman analisis

Kenapa: saran investasi otomatis di Taiwan wajib izin FSC. Penafian sekarang hanya ada
di tab Ringkasan (app/templates/saham.html baris dengan `t('rk.disclaimer')`).

Langkah:
1. Buat app/templates/_penafian.html berisi satu `<div class="pita fixture">` dengan
   `t('rk.disclaimer')`.
2. Sertakan (`{% include "_penafian.html" %}`) di: saham.html untuk SEMUA tab (di bawah
   baris tab, satu kali; hapus yang lama di tab Ringkasan supaya tidak dobel),
   peringatan.html (di bawah judul), valuasi.html (di bawah judul), feed.html (di bawah
   kartu ringkasan jumlah).
3. Ubah teks kunci `rk.p.hati` dan `rk.p.aman` di app/i18n.py (ketiga bahasa) supaya
   tidak berbunyi seperti penilaian kesesuaian investasi:
   - rk.p.hati: EN "Points to watch for a {profil} profile: see the items marked above."
     / 中文 "{profil}型投資人可留意：上方標示的項目。" / ID "Hal yang perlu diperhatikan
     untuk profil {profil}: lihat butir yang ditandai di atas."
   - rk.p.aman: EN "For a {profil} profile, none of the items above crosses the
     watch-out thresholds set by the team." / 中文 "以{profil}型投資人而言，上方項目皆未超過團隊
     設定的留意門檻。" / ID "Untuk profil {profil}, tidak ada butir di atas yang melewati
     ambang perhatian yang ditetapkan tim."
   Jangan ubah kunci lain.

Pemeriksa R2:
- Tes `test_r2_penafian_di_semua_halaman_analisis`: untuk lang en, zh, id, GET
  /, /peringatan/{id pertama}, /saham/2330?tab=X untuk X di ringkasan, stream, stats,
  keu, valuasi, profil, dan /valuasi/2330 → teks penafian bahasa itu muncul TEPAT
  satu kali dan tidak ada "⟦". Patch jaringan seperti TestHalamanSaham di
  tests/test_agent.py (pakai tests/data/pasar_sampel.json).
- Tes `test_r2_tanpa_kata_kesesuaian`: teks rk.p.hati dan rk.p.aman ketiga bahasa tidak
  memuat "aman"/"safe"/"安全"/"cocok"/"suitable"/"適合".

## R3. Kunci akses untuk halaman baca

Kenapa: situs saat ini bisa dibaca siapa pun yang tahu alamatnya. Pilihan ini membuat
semua halaman meminta kode akses, untuk dinyalakan selama lomba.

Langkah:
1. app/config.py: `KUNCI_BACA = os.environ.get("SENTINEL_KUNCI_BACA", "0") == "1"`.
   Hanya berlaku bila `KODE_AKSES` tidak kosong; bila kosong, cetak peringatan sekali
   saat start dan abaikan.
2. app/main.py: middleware HTTP. Bila KUNCI_BACA aktif dan cookie akses tidak cocok
   (pakai fungsi `_boleh_ubah` yang sudah ada), kembalikan halaman HTML status 401
   (template baru app/templates/kunci.html, gaya mengikuti DESIGN.md) berisi form GET ke
   /akses dengan satu isian `kode`. Jalur yang TETAP terbuka: /akses, /sehat,
   /static/*, /bahasa/*, dan /api/impor (punya pemeriksaan sendiri). Selain itu,
   termasuk /docs, /openapi.json, dan semua /api/*, terkunci. Untuk /api/* kembalikan
   JSON 401 `{"galat": "perlu kode akses"}`.
3. Setelah /akses berhasil, arahkan ke "/" (bukan /watchlist).
4. Tambah baris di docs/deploy-dokploy.md: cara menyalakan SENTINEL_KUNCI_BACA=1 dan
   tautan yang dibagikan ke juri (`https://<domain>/akses?kode=<kode>`).

Pemeriksa R3:
- Tes `test_r3_mati_secara_bawaan`: tanpa setelan, GET / → 200.
- Tes `test_r3_terkunci_tanpa_kode`: KUNCI_BACA aktif + KODE_AKSES "uji" → GET / 401
  dan memuat form; GET /api/peringatan → 401 JSON; GET /docs → 401; GET /sehat → 200;
  GET /static/app.css → 200.
- Tes `test_r3_terbuka_dengan_kode`: GET /akses?kode=uji lalu GET / → 200.
- Tes `test_r3_abaikan_bila_kode_kosong`: KUNCI_BACA aktif + KODE_AKSES "" → GET / 200.
- Tes `test_r3_halaman_kunci_tiga_bahasa`: /?lang=zh saat terkunci → tidak ada "⟦".
- Kembalikan config ke nilai semula di tearDown.

## D-a. Proses pengumuman semua emiten

Kenapa: server hanya memproses emiten di watchlist (5 kode), jadi dari 578 pengumuman
asli per hari hanya 4 yang dianalisis. Analisis, evaluasi, dan chatbot butuh semuanya.

Langkah:
1. app/config.py: `PROSES_SEMUA = os.environ.get("SENTINEL_PROSES_SEMUA", "1") == "1"`
   dan `MODEL_MAKS_PER_JALAN = int(os.environ.get("SENTINEL_MODEL_MAKS_PER_JALAN", "40"))`.
2. app/tarik.py `periksa_sekarang(watchlist=None)`: bila argumen `watchlist` None dan
   PROSES_SEMUA aktif, gabungkan SEMUA rekaman dari kedua sumber (bukan hanya watchlist).
   Bila `watchlist` diberikan eksplisit (seperti di tes lama), perilaku lama tetap: hanya
   kode itu. Field status `cocok_watchlist` tetap menghitung yang cocok watchlist; tambah
   field `disimpan` = jumlah rekaman yang digabung.
3. scripts/impor_arsip.py (baru): baca semua berkas `DATA_DIR/raw/openapi/*.json` (arsip
   yang ditulis penarik setiap kali memeriksa; nama berkas memuat "twse" atau "tpex"),
   normalkan dengan `tarik.normalkan(rek, sumber, "arsip")`, lalu `tarik.gabung(...)`.
   Cetak: jumlah berkas, rekaman, baru, duplikat. Bisa dijalankan berulang tanpa
   menggandakan data (gabung sudah dedup).
4. Jatah panggilan model per jalan, supaya satu kali proses tidak menghabiskan kuota
   Gemini atau membuat request menggantung:
   - app/agent/llm.py: tambah `mulai_jalan(maks: int)` yang mengatur penghitung modul
     (`_jatah_sisa`), dan di `tanya()` SETELAH cek cache dan SEBELUM `_tanya_model`:
     bila `_jatah_sisa` tidak None dan ≤ 0 → `raise GagalModel("jatah panggilan model per
     jalan habis")`; bila memanggil model, kurangi 1. Jawaban dari cache tidak mengurangi.
     Bawaan `_jatah_sisa = None` (tanpa batas), jadi perilaku lama dan tes lama tidak berubah.
   - app/main.py `hasil()`: panggil `llm.mulai_jalan(config.MODEL_MAKS_PER_JALAN)` sebelum
     `pipeline.jalankan_semua()`.
   - Pengumuman yang kena batas otomatis turun ke penalar aturan dengan sebab tercatat di
     jejak (ini sudah ditangani extract.sari). Jalan berikutnya memakai model untuk yang
     belum ada di cache.
5. app/main.py `hasil(segarkan=True)` tidak boleh menahan halaman lain selama memproses:
   hitung daftar baru di luar `_kunci_cache` (pakai lock terpisah `_kunci_jalan` supaya
   dua proses tidak jalan bersamaan), lalu ganti `_cache` sekaligus. Saat pertama kali
   (`_cache` None) boleh menunggu seperti sekarang.
6. Tampilan:
   - Feed `/`: bawaan tetap watchlist. Tambah tautan "Semua emiten" → `/?lingkup=semua`
     yang menampilkan semua hasil, dibatasi 300 terbaru, dengan teks jumlah total.
   - `/review`: bawaan hanya emiten watchlist; `/review?lingkup=semua` untuk semua.
     Lencana jumlah di menu (`jml_review`) menghitung watchlist saja.
   - Kunci i18n baru untuk "Watchlist"/"Semua emiten"/"menampilkan {n} dari {total}".
7. tests/test_agent.py: di `TestPenarikDinamis` TIDAK perlu diubah bila langkah 2
   menjaga perilaku untuk argumen eksplisit. Jangan ubah.

Pemeriksa D-a:
- Tes `test_da_semua_emiten_disimpan`: patch ambil dengan tests/data/openapi_pasal_sampel.json
  (7 rekaman, emiten berbeda), watchlist berisi satu kode → `periksa_sekarang()` tanpa
  argumen menyimpan 7; jalankan lagi → baru 0.
- Tes `test_da_argumen_eksplisit_tetap_watchlist`: `periksa_sekarang(["2420"])` hanya
  menyimpan 2420.
- Tes `test_da_jatah_model`: patch `llm._tanya_model` menghitung panggilan dan
  `config.API_KEY`="uji"; `llm.mulai_jalan(2)`; tiga pengumuman berbeda lewat
  `extract.sari` → `_tanya_model` terpanggil 2 kali, yang ketiga memakai penalar aturan
  dengan `sebab_cadangan` memuat "jatah"; setelah tes `_jatah_sisa` dikembalikan None.
- Tes `test_da_halaman_lingkup`: `/?lingkup=semua` dan `/review?lingkup=semua` → 200 di
  tiga bahasa, tanpa "⟦".
- QA manual: jalankan `python3 scripts/impor_arsip.py` di data lokal, lalu server; tulis
  di laporan jumlah pengumuman, jumlah per state (PUBLISHED/HELD/ARCHIVED), dan berapa
  detik satu kali proses ulang.

## D-b. 2330 memakai valuasi otomatis, berkas manual hanya asumsi

Kenapa: berkas valuation/inputs/2330.json memuat PERKIRAAN untuk arus kas 2023–2024 dan
harga 14 Sep. Valuasi otomatis sudah berisi angka asli.

Langkah:
1. app/store.py `muat_valuasi(kode)`:
   - Ada cache otomatis yang layak (`valuasi_otomatis.layak_dcf`) DAN ada berkas manual →
     pakai data otomatis, lalu TIMPA hanya: `assumptions` (seluruh blok), dan dari
     `wacc_inputs` hanya `risk_free_rate` dan `equity_risk_premium`, serta field neraca
     yang di data otomatis bertanda tidak tersedia (lihat D-c). Tambahkan
     `"asumsi_dari": "manual"` dan daftar field yang ditimpa di `"ditimpa_manual"`.
   - Tidak ada cache otomatis → berkas manual apa adanya (seperti sekarang). Ini menjaga
     aplikasi tetap jalan tanpa jaringan.
   - Tanpa berkas manual → seperti sekarang (cache otomatis saja).
2. Tab Valuation dan /valuasi/{kode}: tampilkan lencana "Automatic + team assumptions"
   bila `asumsi_dari` manual, dan daftar `ditimpa_manual`.
3. Ubah `sources.cash_flow` di 2330.json menjadi kalimat yang jujur: angka arus kas
   dipakai hanya bila valuasi otomatis tidak tersedia, dan 2023–2024 adalah perkiraan.
   Jangan ubah angkanya.
4. tests/test_agent.py: tambahkan di AWAL berkas (setelah import) satu blok
   `setUpModule()` / `tearDownModule()` yang mengarahkan direktori cache valuasi otomatis
   ke folder sementara, supaya tes lama selalu memakai berkas manual dan hasilnya tidak
   bergantung pada isi data/ di laptop. Beri komentar `# D-b (Antigravity)`. Itu
   satu-satunya perubahan di berkas ini.

Pemeriksa D-b:
- Tes `test_db_otomatis_menang_asumsi_manual`: siapkan cache otomatis 2330 buatan di
  folder sementara → `muat_valuasi("2330")` memakai cfo/capex otomatis, tetapi
  `assumptions.terminal_growth_ceiling` dan `risk_free_rate` dari berkas manual;
  `asumsi_dari` = "manual".
- Tes `test_db_tanpa_cache_pakai_manual`: tanpa cache → hasil sama dengan berkas manual.
- Semua 107 tes lama tetap lulus.
- QA manual: buka /saham/2330?tab=valuasi dalam tiga bahasa; tulis di laporan g tersirat
  dan WACC sebelum dan sesudah D-b.

## D-c. Utang jangka panjang yang jatuh tempo setahun

Kenapa: valuasi otomatis membaca `current_portion_lt_debt` = 0 karena FinMind
menggabungkannya ke OtherCurrentLiabilities (其他流動負債). Utang 2330 jadi 13% terlalu
rendah. OpenAPI TWSE t187ap07_L_ci hanya memberi neraca ringkas (流動負債 total), jadi
angka ini tidak tersedia dari sumber yang bisa diakses dari luar Taiwan.

Langkah:
1. app/valuasi_otomatis.py: isi field neraca baru `short_term_borrowings` dari
   `ShorttermBorrowings` (短期借款) FinMind kuartal terakhir (0 bila tidak ada; untuk 2330
   nilainya 0). Lalu ubah SATU baris di scripts/dcf.py fungsi `net_debt` menjadi:
   `debt = bs["current_portion_lt_debt"] + bs["long_term_debt"] + bs.get("short_term_borrowings", 0.0)`
   Hanya baris itu yang boleh diubah di dcf.py. Berkas manual tanpa field itu tetap
   menghasilkan angka yang sama (tes paritas lama harus tetap lulus).
2. Bila bagian lancar utang jangka panjang tidak tersedia: tandai
   `"tidak_tersedia": ["current_portion_lt_debt"]` dan peringatan i18n
   "Current portion of long-term debt is not published separately by FinMind; debt may be
   understated." (tiga bahasa), tampil di tab Valuation.
3. Dengan D-b, berkas manual 2330 mengisi field yang `tidak_tersedia` itu (136.926,5).
4. docs/valuasi-otomatis.md: tambah satu paragraf yang menjelaskan ini, dengan angka 2330.

Pemeriksa D-c:
- Tes `test_dc_pinjaman_jangka_pendek_masuk_utang`: sampel neraca buatan dengan
  ShorttermBorrowings → utang naik sebesar itu.
- Tes `test_dc_tanda_tidak_tersedia`: sampel tanpa bagian lancar → `tidak_tersedia`
  memuat current_portion_lt_debt dan peringatan muncul di halaman (tiga bahasa).
- Tes `test_dc_manual_mengisi_yang_kosong`: dengan D-b, utang total 2330 = otomatis +
  136.926,5 (selisih dari berkas manual < 1%).
- QA manual: `python3 scripts/valuasi_otomatis.py 2330 --banding` → baris debt selisih
  < 1% setelah digabung manual; tempel tabelnya di laporan.

## B3. Sitasi MOPS untuk angka laporan keuangan

Kenapa: aturan lomba meminta sitasi ke sumber asli (MOPS/TWSE), bukan ke agregator.

Langkah:
1. app/valuasi_otomatis.py (atau modul baru app/sitasi.py, milikmu): fungsi
   `mops_laporan(kode, tahun_iso, kuartal, jenis)` → URL MOPS. jenis: "neraca" →
   t164sb03, "lr" → t164sb04, "arus" → t164sb05. Tahun ROC = tahun − 1911, kuartal
   "01".."04". Bentuk URL:
   https://mopsov.twse.com.tw/mops/web/ajax_{prog}?encodeURIComponent=1&step=1&firstin=1&off=1&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false&co_id={kode}&year={roc}&season={qq}
   Simpan juga URL halaman pencarian umum https://mops.twse.com.tw/mops/#/web/{prog}
   sebagai cadangan.
2. Tab Financials (`tab == 'keu'` di saham.html): setiap judul kolom periode diberi
   tautan "MOPS ↗" ke laporan periode itu; di bawah tabel tulis "Data: FinMind (salinan
   dari MOPS). Sumber resmi: MOPS, tautan per kolom." (kunci i18n baru).
3. `sources` valuasi otomatis untuk neraca, arus kas, dan pajak memuat URL MOPS periode
   yang dipakai.
4. scripts/cek_finmind_resmi.py (baru): bandingkan angka FinMind dengan OpenAPI resmi
   TWSE `https://openapi.twse.com.tw/v1/opendata/t187ap06_L_ci` (laba rugi, ribuan NTD)
   dan `t187ap07_L_ci` (neraca, ribuan NTD) untuk kuartal yang sama. Kolom yang
   dibandingkan: 營業收入, 稅前淨利（淨損）, 資產總計, 負債總計, 權益總計. Perhatikan:
   t187ap06 berisi angka kumulatif sejak awal tahun, FinMind laba rugi per kuartal
   tunggal (jumlahkan kuartal tahun itu). Endpoint ini hanya memuat industri umum; emiten
   di luarnya dilewati dengan keterangan. Cetak tabel per emiten dan selisih %. Opsi
   `--acak 10 --seed 7` dan `--simpan` (eval/hasil/b3-cek-<tanggal>.md).
5. Uji tautan MOPS: kalau laptop ini di jaringan Taiwan, buka 3 tautan (2330 neraca
   2025Q4, 2317 laba rugi 2026Q2, 6488 arus kas 2025Q4) dengan curl atau browser, dan
   tulis di laporan apakah halaman memuat tabel laporan. Kalau tidak di Taiwan, tulis
   "belum diuji, perlu jaringan Taiwan".

Pemeriksa B3:
- Tes `test_b3_url_mops`: 2330, 2025, Q4, neraca → URL memuat ajax_t164sb03, co_id=2330,
  year=114, season=04.
- Tes `test_b3_tautan_di_tab_keuangan`: GET /saham/2330?tab=keu (jaringan dipatch, sampel
  FinMind) → setiap kolom periode punya tautan mopsov; tiga bahasa tanpa "⟦".
- Tes `test_b3_cek_resmi_kumulatif`: sampel buatan t187ap06 kumulatif Q2 vs dua kuartal
  FinMind → selisih 0%.
- QA manual: `python3 scripts/cek_finmind_resmi.py --acak 10 --seed 7 --simpan`; minimal
  10 angka dibandingkan; tulis berapa yang selisih ≤ 0,5% dan jelaskan yang lebih.

## R4. Draf pengungkapan pihak ketiga dan alat AI

Kenapa: Pasal 13 aturan lomba mewajibkan pengungkapan sumber, tujuan, dan lingkup
pemakaian open source, model, dataset, API, dan generative AI.

Langkah: tulis docs/pengungkapan-pihak-ketiga.md (pakai /humanizer) berisi tabel:
Nama · Jenis (alat AI pembuat kode, model di aplikasi, data, pustaka, skill) · Untuk apa ·
Lingkup (data apa yang dikirim/diterima) · Lisensi atau syarat pakai (dengan tautan) ·
Sudah diverifikasi? (ya/belum).
Isi minimal: Claude Code (Anthropic), Antigravity (Google), Gemini API (nama model dari
config.MODEL, free tier, hanya teks pengumuman publik dan angka publik yang dikirim),
FinMind API, TWSE OpenAPI, TPEx OpenAPI, situs TWSE/TPEx untuk harga historis (R1), MOPS
(hanya dari laptop Taiwan), Damodaran (ERP), sumber imbal hasil obligasi Taiwan 10 tahun
(lihat sources di 2330.json), setiap pustaka di requirements.txt dengan lisensinya,
Playwright dan Mermaid (alat pembuat diagram, tidak ikut di aplikasi), skill humanizer
dan anti-slop (MIT).
Untuk setiap lisensi/syarat pakai, buka halaman resminya dan kutip kalimat yang relevan.
Bila tidak menemukan, tulis "belum diverifikasi". Jangan menebak.
Tambahkan bagian "Pembagian kerja tim" berupa tabel KOSONG (Bagian · Dikerjakan oleh ·
Peran AI) untuk diisi tim. Jangan mengisinya sendiri.
Tambahkan bagian "Catatan data pribadi": cache profil TPEx di server sempat menyimpan nama
pejabat dan email sampai perbaikan 10 Nov (commit e4572d6); tidak ditampilkan ke publik;
dibersihkan otomatis saat dibaca setelah deploy.

Pemeriksa R4:
- Tes `test_r4_semua_pustaka_tercantum`: setiap nama paket di requirements.txt muncul di
  docs/pengungkapan-pihak-ketiga.md.
- Tes `test_r4_tabel_tim_kosong`: bagian "Pembagian kerja tim" ada dan baris isinya kosong.
- QA: jalankan /humanizer pada berkas itu, catat di laporan bahwa sudah.

# 4. Pemeriksaan akhir (sebelum laporan)

1. `python3 -m unittest discover -s tests` → OK, catat jumlah tes (107 + tes barumu).
2. Ulangi dengan Wi-Fi mati → tetap OK.
3. `git grep -nE "AIza|FINMIND_TOKEN=|發言人電話|yahoo"` → kosong (kecuali kata "yahoo" di
   docs/pengungkapan-pihak-ketiga.md bila menjelaskan bahwa Yahoo tidak dipakai lagi).
4. `uvicorn app.main:app --reload`, buka dalam EN, 中文, ID: /, /?lingkup=semua, /review,
   /ambang, /saham/2330 semua tab, /saham/6488?tab=valuasi, /saham/2881?tab=valuasi,
   /valuasi/2330. Tidak ada 500, tidak ada "⟦", penafian tampil satu kali per halaman.
5. Jalankan sekali dengan SENTINEL_KUNCI_BACA=1 SENTINEL_KODE_AKSES=uji dan cek R3.
6. Perbarui baris status R1, R2, R3, D-a, D-b, D-c, B3, R4 di docs/rencana-dan-status.md
   (✅ atau tulis apa yang belum).
7. `git pull --rebase origin main`, tes lagi, `git push origin main`.

# 5. Laporan (wajib)

Tulis docs/laporan-antigravity-2.md, lalu jalankan /humanizer pada berkas itu sebelum
commit. Bahasa Indonesia, kalimat pendek. Isi, urut:
1. Ringkasan satu paragraf: item yang lulus, yang tidak.
2. Tabel item: ID · Status (lulus/gagal/sebagian) · Commit (hash) · Tes yang ditambah ·
   Hasil QA manual (angka).
3. Hasil tes: perintah, jumlah tes, keluaran baris terakhir. Hasil dengan Wi-Fi mati.
4. Angka QA: beta 2330 + jumlah minggu, beta 6488; tabel banding 2330 setelah D-b dan
   D-c; jumlah pengumuman dan per state setelah D-a, waktu satu kali proses; hasil
   cek FinMind vs resmi (B3); hasil uji tautan MOPS.
5. Berkas yang diubah per item (daftar path).
6. Yang menyimpang dari prompt ini dan alasannya. Kalau tidak ada, tulis "tidak ada".
7. Temuan untuk Claude: bug atau keanehan di berkas yang bukan milikmu (path, baris,
   gejala, usulan). Jangan diperbaiki sendiri.
8. Yang belum selesai.
Jangan menulis "semua lulus" bila ada pemeriksa yang gagal atau dilewati.
````

---

## Cara Afinzaki mengecek hasilnya

1. Ambil kode terbaru dan jalankan tes. Harus "OK", jumlahnya lebih dari 107.

   ```bash
   git pull origin main
   ```

   ```bash
   python3 -m unittest discover -s tests
   ```

2. Buka `docs/laporan-antigravity-2.md`. Tabel item harus berisi hash commit dan angka QA
   untuk setiap item. Item yang tertulis "gagal" atau "sebagian" kirim ke Claude.
3. Cek tiga angka penting:
   - beta 2330 bukan cadangan dan dihitung dari sekitar 100 minggu;
   - selisih utang 2330 di tabel banding di bawah 1%;
   - jumlah pengumuman setelah D-a ratusan, bukan 4.
4. Buka situs lokal (`uvicorn app.main:app --reload`) dalam tiga bahasa. Halaman analisis
   punya penafian kuning, tab Financials punya tautan "MOPS ↗" di setiap kolom.
5. Kirim laporan itu ke Claude untuk dikoreksi. Claude mencocokkan isinya dengan kode
   sebelum kamu deploy.

Tanda bahaya: tes lama dihapus atau dilonggarkan; perubahan di `app/agent/` selain
`llm.py`; perubahan di `tests/test_agent.py` selain blok `setUpModule`; ada kunci API di
berkas.
