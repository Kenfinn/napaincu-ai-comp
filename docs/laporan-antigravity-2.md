# Laporan Antigravity Putaran 2

Laporan pelaksanaan tugas semalam P1 sampai P10 untuk FEAF (Agentic AI Investment Assistant, NAPAI AAIC 2026, track SYSTEX).

- Jam mulai: `2026-11-11T00:20:35+08:00`
- Hasil tes awal (langkah 2): `Ran 131 tests in 2.438s, OK` (131 tes lulus tanpa galat)
- Status pemasangan skill:
  - `anti-slop`: terpasang di `/home/afinzaki/.gemini/config/plugins/antislop`
  - `humanizer`: terpasang di `~/.agents/skills/humanizer`

---

## P1. Persiapan
- Status: ✅ Selesai
- Jam mulai: 00:20
- Jam selesai: 00:23
- Catatan: Repositori mutakhir ditarik, seluruh 131 tes lulus, koreksi Claude di `docs/pemahaman-antigravity.md` dipahami, kedua skill terpasang.

---

## P2. R1: Beta dari Harga Resmi TWSE/TPEx
- ID: R1
- Status: ✅ Selesai
- Commit: `88e5770`
- Jam mulai: 00:23
- Jam selesai: 00:40
- Tes yang ditambah dan hasilnya:
  - 5 tes baru di `tests/test_putaran2.py` (semua lulus):
    - `test_r1_urai_twse_tpex_taiex`: urai JSON resmi TWSE, TAIEX, dan TPEx menghasilkan tanggal ISO valid dan harga penutupan float tanpa tanda koma.
    - `test_r1_beta_dari_deret_buatan`: deret buatan dengan return saham = 1,5 × return pasar menghasilkan beta 1,50 (tepat).
    - `test_r1_beta_cadangan_bila_kurang_52_minggu`: data 30 minggu menghasilkan fallback beta 1,0 dengan bendera `beta_cadangan: True`.
    - `test_r1_cache_bulan_lalu_tidak_diambil_ulang`: panggilan kedua untuk bulan lampau membaca berkas cache lokal tanpa panggilan jaringan.
    - `test_r1_tanpa_yahoo`: pemindaian kode di `app/` dan `scripts/` memastikan tidak ada lagi kata atau pustaka Yahoo.
  - Penyesuaian tes lama di `tests/test_valuasi_otomatis.py` ke modul `harga_resmi`.
  - Total tes lulus: 136 tes (naik dari 131 tes).
- Angka QA manual:
  - 2330 (TSMC, TWSE):
    - Beta: 1.0272
    - Jumlah minggu: 104 pekan (rentang 2 tahun penuh)
    - Status: bukan cadangan (`beta_cadangan: False`)
  - 6488 (GlobalWafers, TPEx):
    - Beta: 2.3207
    - Jumlah minggu: 104 pekan
    - Status: bukan cadangan (`beta_cadangan: False`)
- Berkas yang diubah/dibuat/dihapus:
  - Baru: `app/harga_resmi.py`, `tests/test_putaran2.py`, `tests/data/harga_resmi_sampel.json`
  - Diubah: `app/valuasi_otomatis.py`, `app/i18n.py`, `scripts/valuasi_otomatis.py`, `tests/test_valuasi_otomatis.py`
  - Dihapus: `tests/data/yahoo_sampel.json`

---

## P3. R2: Penafian di Semua Halaman Analisis
- ID: R2
- Status: ✅ Selesai
- Commit: `0849027`
- Jam mulai: 00:40
- Jam selesai: 00:48
- Tes yang ditambah dan hasilnya:
  - 2 tes baru di `tests/test_putaran2.py` (keduanya lulus):
    - `test_r2_penafian_di_semua_halaman_analisis`: 9 halaman analisis diuji di 3 bahasa (`en`, `zh`, `id`). Penafian muncul tepat 1 kali pada masing-masing halaman dan tidak ada penanda teks tak terterjemahkan `⟦`.
    - `test_r2_tanpa_kata_kesesuaian`: teks `rk.p.hati` dan `rk.p.aman` pada ketiga bahasa dipastikan bersih dari kata penilaian kesesuaian (`aman`, `safe`, `安全`, `cocok`, `suitable`, `適合`).
  - Penyesuaian tes lama di `tests/test_agent.py::test_profil_konservatif_lebih_hati_hati`.
  - Total tes lulus: 138 tes (naik dari 136 tes).
- Angka QA manual:
  - 18 kombinasi `/saham/2330?tab=X&lang=Y` (6 tab x 3 bahasa) diverifikasi langsung lewat HTTP client: status 200 OK dan teks penafian muncul tepat 1 kali per halaman.
- Berkas yang diubah/dibuat:
  - Dibuat: `app/templates/_penafian.html`
  - Diubah: `app/templates/saham.html`, `app/templates/peringatan.html`, `app/templates/valuasi.html`, `app/templates/feed.html`, `app/i18n.py`, `tests/test_agent.py`, `tests/test_putaran2.py`
- Keputusan yang saya ambil sendiri:
  - Menyesuaikan kata kunci penegasan di `tests/test_agent.py::test_profil_konservatif_lebih_hati_hati` dari `"caution"` menjadi `"Points to watch"` agar selaras dengan redaksi baru `rk.p.hati` dari spesifikasi R2.

---

## P4. R3: Kunci Akses untuk Halaman Baca
- ID: R3
- Status: ✅ Selesai
- Commit: `e0b2c0d`
- Jam mulai: 00:48
- Jam selesai: 00:54
- Tes yang ditambah dan hasilnya:
  - 5 tes baru di `tests/test_putaran2.py` (semua lulus):
    - `test_r3_mati_secara_bawaan`: tanpa konfigurasi, akses baca bebas seperti semula (status 200).
    - `test_r3_terkunci_tanpa_kode`: KUNCI_BACA aktif mengunci `/` (401 form), `/docs` (401), dan `/api/*` (401 JSON galat), sementara `/sehat` dan `/static/*` tetap terbuka (200).
    - `test_r3_terbuka_dengan_kode`: cookie akses dari `/akses?kode=...` membuka seluruh halaman baca (200).
    - `test_r3_abaikan_bila_kode_kosong`: KUNCI_BACA aktif namun KODE_AKSES kosong diabaikan dengan aman (200).
    - `test_r3_halaman_kunci_tiga_bahasa`: halaman 401 tampil utuh dalam bahasa `en`, `zh`, dan `id` tanpa penanda tak terterjemahkan `⟦`.
  - Total tes lulus: 143 tes (naik dari 138 tes).
- Angka QA manual:
  - Eksekusi server dengan `SENTINEL_KUNCI_BACA=1 SENTINEL_KODE_AKSES=uji`:
    - GET `/` -> 401 (terkunci, form isian kode ditampilkan)
    - GET `/sehat` -> 200 (health check dokploy tetap berfungsi)
    - GET `/akses?kode=uji` -> 200 (diarahkan ke `/` dengan cookie akses)
    - GET `/` setelah auth -> 200 (halaman feed terbuka penuh)
- Berkas yang diubah/dibuat:
  - Dibuat: `app/teks/antigravity.py`, `app/templates/kunci.html`
  - Diubah: `app/config.py`, `app/main.py`, `docs/deploy-dokploy.md`, `tests/test_putaran2.py`

---

### D-a: Proses Pengumuman Semua Emiten
- Jam mulai: 00:55
- Jam selesai: 01:06
- Status: Selesai
- Commit: `6e731fc`
- Tes yang ditambah dan hasilnya:
  - 4 tes baru di `tests/test_putaran2.py` (semua lulus):
    - `test_da_semua_emiten_disimpan`: `periksa_sekarang()` tanpa argumen menyimpan seluruh rekaman (7 data sampel), menghitung `cocok_watchlist` sesuai emiten pantauan (1 data), dan eksekusi ulang menghasilkan 0 data baru.
    - `test_da_argumen_eksplisit_tetap_watchlist`: `periksa_sekarang(["2420"])` hanya menyaring dan menyimpan kode yang diminta secara eksplisit.
    - `test_da_jatah_model`: pembatasan kuota model berjalan dengan `mulai_jalan(2)`; dua panggilan model pertama dieksekusi, panggilan ketiga otomatis turun ke penalar aturan dengan `sebab_cadangan` berisi keterangan jatah habis.
    - `test_da_halaman_lingkup`: `/` dan `/review` dengan parameter `?lingkup=semua` merespons status 200 di tiga bahasa tanpa ada penanda tak terterjemahkan `⟦`.
  - Total tes lulus: 147 tes (naik dari 143 tes). Seluruh tes lama (`TestPenarikDinamis`, dll.) tetap lulus tanpa perubahan.
- Angka QA manual:
  - Eksekusi `python3 scripts/impor_arsip.py`: 0 berkas, 0 rekaman, 0 baru, 0 duplikat pada lingkungan awal.
  - Jumlah pengumuman: 4 pengumuman (fixture mode).
  - Rincian per state: 2 PUBLISHED (`terbit`), 1 HELD (`ditahan`), 1 ARCHIVED (`dilewati`).
  - Durasi pemrosesan ulang `main.hasil(segarkan=True)`: 0.0058 detik. Pipeline berjalan di luar `_kunci_cache` dengan lock terpisah `_kunci_jalan` sehingga permintaan baca tidak tertahan selama penghitungan ulang.
- Berkas yang diubah/dibuat:
  - Dibuat: `scripts/impor_arsip.py`
  - Diubah: `app/agent/llm.py`, `app/config.py`, `app/main.py`, `app/tarik.py`, `app/teks/antigravity.py`, `app/templates/feed.html`, `app/templates/review.html`, `tests/test_putaran2.py`

---

### D-c: Pinjaman Jangka Pendek dan Tanda Utang Lancar
- Jam mulai: 01:07
- Jam selesai: 01:17
- Status: Selesai
- Commit: `fb49d77`
- Tes yang ditambah dan hasilnya:
  - 2 tes baru di `tests/test_putaran2.py` (semua lulus):
    - `test_dc_pinjaman_jangka_pendek_masuk_utang`: memverifikasi bahwa `dcf.net_debt` menjumlahkan `short_term_borrowings` ke dalam total utang berbobot bunga (`debt`), bertambah tepat 35,0 juta NTD pada sampel neraca uji, dan bernilai sama bila field tersebut tidak ada.
    - `test_dc_tanda_tidak_tersedia`: sampel tanpa bagian lancar utang jangka panjang menandai `"tidak_tersedia": ["current_portion_lt_debt"]` dan menampilkan peringatan tiga bahasa di `/saham/2330?tab=valuasi` serta `/valuasi/2330` tanpa penanda tak terterjemahkan `⟦`.
  - `TestParitasKalkulator` dan seluruh tes lama tetap lulus. Total tes lulus: 151 tes.
- Angka QA manual:
  - Eksekusi `python3 scripts/valuasi_otomatis.py 2330 --banding`:
    - `balance_sheet.short_term_borrowings`: 0.0 vs 0.0 (0.00%)
    - `balance_sheet.current_portion_lt_debt`: 0.0 vs 136,926.5 (-100.00%, karena FinMind menggabungkan ke OtherCurrentLiabilities)
    - `DCF: debt`: 896,062.0 vs 1,032,988.5 (-13.26%)
    - Peringatan transparan muncul di tab Valuation dalam 3 bahasa. Pada P7 (D-b), field ini akan ditimpa kertas kerja manual.
- Berkas yang diubah:
  - Diubah: `scripts/dcf.py` (tepat 1 baris di `net_debt`), `app/valuasi_otomatis.py`, `app/teks/antigravity.py`, `app/main.py`, `app/templates/valuasi.html`, `scripts/valuasi_otomatis.py`, `docs/valuasi-otomatis.md`, `tests/test_putaran2.py`

---

### D-b: 2330 Memakai Valuasi Otomatis dengan Asumsi Tim
- Jam mulai: 01:19
- Jam selesai: 01:28
- Status: Selesai
- Commit: `c04ddee`
- Tes yang ditambah dan hasilnya:
  - 3 tes baru di `tests/test_putaran2.py` (semua lulus):
    - `test_db_otomatis_menang_asumsi_manual`: cache otomatis 2330 dipadukan dengan berkas manual; cfo dan capex memakai angka otomatis, tetapi parameter asumsi (`terminal_growth_ceiling`) dan `risk_free_rate` diambil dari berkas manual; `asumsi_dari` bernilai `"manual"`.
    - `test_db_tanpa_cache_pakai_manual`: bila cache otomatis tidak ada di disk, `store.muat_valuasi` mengembalikan berkas manual apa adanya tanpa galat.
    - `test_dc_manual_mengisi_yang_kosong`: field `current_portion_lt_debt` yang tidak tersedia di FinMind diisi oleh berkas manual, sehingga selisih utang total 2330 terhadap manual adalah 0,00% (jauh di bawah batas 1%).
  - Penyesuaian `test_berkas_manual_selalu_menang_dan_store_tanpa_jaringan` di `tests/test_valuasi_otomatis.py` untuk menguji penggabungan D-b saat cache ada dan isolasi berkas manual saat cache kosong.
  - Penambahan blok `setUpModule()` / `tearDownModule()` di `tests/test_agent.py` yang mengisolasi cache valuasi otomatis ke folder sementara selama pengujian agen.
  - Total tes lulus: 155 tes.
- Angka QA manual:
  - WACC 2330:
    - Manual murni: 8,09%
    - Otomatis murni: 7,00%
    - Gabungan (otomatis + asumsi tim): 6,98%
  - Pertumbuhan tersirat ($g_{\text{tersirat}}$) 2330:
    - Manual murni: 6,29%
    - Otomatis murni: 5,09%
    - Gabungan (otomatis + asumsi tim): 5,08%
  - Total utang ($debt$) 2330:
    - Otomatis murni (sebelum D-b): 896.062,0 juta NTD
    - Gabungan (sesudah D-b): 1.032.988,5 juta NTD (selisih 0,00% dari manual)
  - Tampilan UI: Lencana "Automatic + team assumptions" ("自動＋團隊假設" / "Otomatis + asumsi tim") tampil rapi di `/saham/2330?tab=valuasi` dan `/valuasi/2330` bersama daftar field yang ditimpa. Diuji dalam 3 bahasa (EN, ZH, ID) tanpa penanda `⟦`.
  - Tabel perbandingan dari `python3 scripts/valuasi_otomatis.py 2330 --banding`:

| Field | Otomatis | Manual | Selisih % | Catatan |
|---|---:|---:|---:|---|
| `market.price_per_share (NTD)` | 2.235,00 | 2.380,00 | -6,09% | oto 2026-11-09 vs manual 2026-09-14 |
| `market.shares_issued_thousands` | 25.932.370,1 | 25.932.524,0 | -0,00% | TWSE OpenAPI t187ap03_L |
| `balance_sheet.cash_and_equivalents (2025-12-31)` | 2.767.856,4 | 2.767.856,4 | +0,00% | CashAndCashEquivalents (identik) |
| `balance_sheet.short_term_investments (2025-12-31)` | 300.638,2 | 300.638,2 | +0,00% | AmortizedCost + FVOCI (identik) |
| `balance_sheet.short_term_borrowings (2025-12-31)` | 0,0 | 0,0 | 0,00% | ShorttermBorrowings FinMind (2330: 0) |
| `balance_sheet.current_portion_lt_debt (2025-12-31)` | 0,0 | 136.926,5 | -100,00% | FinMind gabung ke OtherCurrentLiabilities |
| `balance_sheet.long_term_debt (2025-12-31)` | 896.062,0 | 896.062,0 | +0,00% | BondsPayable + LongtermBorrowings (identik) |
| `cash_flow.cfo_by_year[2023]` | 1.241.967,3 | 1.600.000,0 | -22,38% | Perkiraan di berkas manual |
| `cash_flow.capex_by_year[2023]` | 949.816,8 | 1.313.000,0 | -27,66% | Perkiraan di berkas manual |
| `cash_flow.interest_expense_by_year[2023]` | 11.999,4 | 12.000,0 | -0,01% | Perkiraan di berkas manual |
| `cash_flow.cfo_by_year[2024]` | 1.826.177,1 | 2.000.000,0 | -8,69% | Perkiraan di berkas manual |
| `cash_flow.capex_by_year[2024]` | 956.006,5 | 1.140.000,0 | -16,14% | Perkiraan di berkas manual |
| `cash_flow.interest_expense_by_year[2024]` | 10.495,3 | 12.000,0 | -12,54% | Perkiraan di berkas manual |
| `cash_flow.cfo_by_year[2025]` | 2.274.975,6 | 2.274.980,0 | -0,00% | Laporan tahunan penuh (31 Des) |
| `cash_flow.capex_by_year[2025]` | 1.272.410,5 | 1.272.400,0 | +0,00% | Laporan tahunan penuh (31 Des) |
| `cash_flow.interest_expense_by_year[2025]` | 12.370,4 | 12.300,0 | +0,57% | Laporan tahunan penuh (31 Des) |
| `tax.income_tax_expense` | 326.266,1 | 346.500,0 | -5,84% | Jumlah 4 kuartal TAX FinMind vs pembulatan manual |
| `tax.pretax_income` | 2.041.662,8 | 2.041.600,0 | +0,00% | Jumlah 4 kuartal PreTaxIncome FinMind |
| `effective_tax_rate` | 15,98% | 16,97% | -5,84% | TAX / PreTaxIncome |
| `wacc_inputs.risk_free_rate` | 1,94% | 1,94% | +0,00% | Obligasi pemerintah Taiwan 10Y |
| `wacc_inputs.equity_risk_premium` | 5,01% | 5,01% | +0,00% | Damodaran ERP Taiwan |
| `wacc_inputs.beta` | 1,0272 | 1,2500 | -17,82% | Regresi 2y mingguan bursa resmi (104 pekan) vs manual |
| `wacc_inputs.total_interest_expense` | 12.370,4 | 19.980,0 | -38,09% | InterestExpense FY terakhir |
| `DCF: market_cap` | 57.958.847,1 | 61.719.407,1 | -6,09% | Juta NTD |
| `DCF: debt` | 896.062,0 | 1.032.988,5 | -13,26% | Juta NTD (setelah D-b menjadi 1.032.988,5) |
| `DCF: cash` | 3.068.494,6 | 3.068.494,6 | +0,00% | Juta NTD |
| `DCF: enterprise_value (EV)` | 55.786.414,5 | 59.683.901,0 | -6,53% | Juta NTD |
| `DCF: FCFF 2025 (fcff0)` | 1.012.958,7 | 1.012.792,4 | +0,02% | Juta NTD |
| `DCF: FCFF 3y average` | 731.393,2 | 726.573,1 | +0,66% | Juta NTD |
| `DCF: cost_of_equity (ke)` | 7,09% | 8,20% | -13,61% |  |
| `DCF: cost_of_debt (kd pre-tax)` | 1,38% | 1,93% | -28,63% |  |
| `DCF: WACC` | 7,00% | 8,09% | -13,56% | Setelah D-b: 6,98% |
| `DCF: implied_growth (g tersirat)` | 5,09% | 6,29% | -19,11% | Setelah D-b: 5,08% |
- Berkas yang diubah:
  - `app/main.py`
  - `app/store.py`
  - `app/teks/antigravity.py`
  - `app/templates/saham.html`
  - `app/templates/valuasi.html`
  - `app/valuasi_otomatis.py`
  - `tests/test_agent.py`
  - `tests/test_putaran2.py`
  - `tests/test_valuasi_otomatis.py`
  - `valuation/inputs/2330.json`






