# Dokumentasi Valuasi DCF Otomatis (Tugas B2)

Dokumen ini menjelaskan arsitektur, pemetaan sumber data, perbandingan terhadap kertas kerja manual `2330`, hasil evaluasi 10 emiten non-keuangan acak lintas bursa (TWSE & TPEx), serta catatan teknis untuk pengembangan paralel.

---

## 1. Tujuan & Arsitektur

Sebelum Tugas B2, hanya `2330` (TSMC) yang memiliki berkas input valuasi manual (`valuation/inputs/2330.json`). Akibatnya:
- Pengumuman pasal 20/11/22 untuk emiten selain `2330` berakhir ditahan (`HELD`) dengan alasan `tanpa_valuasi`.
- Tab **Valuation** pada halaman saham (`/saham/{kode}?tab=valuasi`) kosong untuk seluruh emiten selain `2330`.

Modul [`app/valuasi_otomatis.py`](../app/valuasi_otomatis.py) dan CLI [`scripts/valuasi_otomatis.py`](../scripts/valuasi_otomatis.py) membangun struktur input DCF dengan **skema yang sama persis** dengan `valuation/inputs/2330.json` sehingga [`scripts/dcf.py`](../scripts/dcf.py) (`compute()`) dan [`app/agent/recompute.py`](../app/agent/recompute.py) (`hitung_ulang()`) dapat langsung dipakai tanpa mengubah satu baris pun di mesin aritmetika DCF.

### Alur Penyimpanan & Prioritas Sumber
1. **Berkas manual selalu menang**: `app/store.py::muat_valuasi(kode)` memeriksa `valuation/inputs/{kode}.json` terlebih dahulu. Bila ada, berkas manual dikembalikan apa adanya.
2. **Cache otomatis tanpa jaringan di jalur pipeline**: bila berkas manual tidak ada, `store.muat_valuasi(kode)` memanggil `valuasi_otomatis.dari_cache_untuk_pipeline(kode)` yang hanya membaca `DATA_DIR/valuasi_otomatis/{kode}.json` dari disk (tidak pernah memanggil internet supaya pipeline tetap deterministik dan cepat).
3. **Pemanasan terjadwal**: `_pemantau()` dan rute `POST /periksa` di `app/main.py` memanggil `valuasi_otomatis.panaskan(tarik.baca_watchlist())` sebelum `hasil(segarkan=True)` dengan jeda sopan dan TTL cache 12 jam.
4. **Penyegaran saat laporan keuangan baru**: fungsi `valuasi_otomatis.segarkan(kode)` disediakan agar pemantau pengumuman pasal 31 (publikasi laporan keuangan baru) dapat langsung membangun ulang cache valuasi emiten terkait.

---

## 2. Pemetaan Field & Sumber Data

Seluruh nilai moneter disimpan dalam **juta NTD** (nilai FinMind dalam NTD dibagi $10^6$):

| Bagian | Field `2330.json` | Sumber Otomatis | Rumus / Aturan |
|---|---|---|---|
| `market` | `price_per_share` | `pasar.harga(kode)["tutup"]` | Harga penutupan harian OpenAPI TWSE (`STOCK_DAY_ALL`) / TPEx (`tpex_mainboard_quotes`) |
| `market` | `shares_issued_thousands` | `pasar.profil(kode)["lembar"]` | Lembar saham biasa beredar dibagi $1.000$; cadangan `CapitalStock / 10 / 1000` (nominal NT\$10) bila profil bursa kosong |
| `balance_sheet` | `cash_and_equivalents` | FinMind `TaiwanStockBalanceSheet` | `CashAndCashEquivalents / 1e6` pada akhir tahun fiskal (`{fiscal_year}-12-31`, atau kuartal terakhir bila belum ada) |
| `balance_sheet` | `short_term_investments` | FinMind `TaiwanStockBalanceSheet` | `(FinancialAssetsAtAmortizedCost + FinancialAssetsAtFairvalueThroughOtherComprehensiveIncome) / 1e6` |
| `balance_sheet` | `current_portion_lt_debt` | FinMind `TaiwanStockBalanceSheet` | `LongtermLiabilitiesCurrentPortion` / pos `origin_name` mengandung `一年內到期` + `ShorttermBorrowings` (lihat catatan di bagian 3) |
| `balance_sheet` | `long_term_debt` | FinMind `TaiwanStockBalanceSheet` | `(BondsPayable + LongtermBorrowings) / 1e6` |
| `cash_flow` | `cfo_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `CashFlowsFromOperatingActivities / 1e6` untuk 3 tahun fiskal penuh terakhir (`-12-31`, karena arus kas FinMind bersifat kumulatif YTD sejak awal tahun) |
| `cash_flow` | `capex_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `abs(PropertyAndPlantAndEquipment) / 1e6` untuk 3 tahun fiskal penuh terakhir (`-12-31`) |
| `cash_flow` | `interest_expense_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `abs(InterestExpense) / 1e6`, atau jatuh ke `abs(PayTheInterest) / 1e6` bila `InterestExpense` tidak ada (dicatat di `sources` dan `peringatan`) |
| `tax` | `income_tax_expense`, `pretax_income` | FinMind `TaiwanStockFinancialStatements` | Jumlah 4 kuartal tunggal tahun fiskal terakhir: `sum(TAX) / 1e6` dan `sum(PreTaxIncome) / 1e6` |
| `wacc_inputs` | `risk_free_rate`, `equity_risk_premium` | Konstanta pasar Taiwan (`2330.json`) | $r_f = 1{,}94\%$ (obligasi pemerintah Taiwan 10Y), $\text{ERP} = 5{,}01\%$ (Damodaran Taiwan) |
| `wacc_inputs` | `beta` | Yahoo Finance chart API (`2y`, `1wk`) | $\beta = \frac{\text{Cov}(r_s, r_m)}{\text{Var}(r_m)}$ antara return mingguan `{kode}.TW`/`.TWO` dan TAIEX (`^TWII`). Bila $< 52$ pasangan pekan atau gagal ambil → $\beta = 1{,}0$ (`beta_cadangan: true`) |
| `wacc_inputs` | `total_interest_expense` | Laporan arus kas tahun terakhir | Beban bunga tahun fiskal terakhir |

### Penanganan Kasus Khusus (Gagal-Tertutup, Tanpa Menebak)
- **Emiten sektor keuangan** (`pasar.profil(kode)["keuangan"] == True`, kode industri `17` di TWSE maupun TPEx, mis. `2881` Fubon Financial, `2891` CTBC Financial): tidak dihitung dengan model DCF berbasis FCFF. `bangun(kode)` mengembalikan `{"tidak_berlaku": True, "alasan": ...}` dan tab Valuation menampilkan lencana **Not applicable / 不適用 / Tidak berlaku** beserta penjelasannya dalam 3 bahasa.
- **Data tidak cukup atau FCFF negatif**: bila laporan arus kas memiliki kurang dari 3 tahun fiskal penuh, harga/jumlah saham tidak tersedia, $\text{FCFF}_0 \le 0$, atau $\text{EV} \le 0$, `bangun(kode)` mengembalikan `{"tidak_bisa_dihitung": True, "alasan": ...}` tanpa menebak angka.

---

## 3. Perbandingan `2330` Otomatis vs Manual (`--banding`)

Hasil menjalankan `python3 scripts/valuasi_otomatis.py 2330 --banding`:

| Field | Otomatis | Manual (`2330.json`) | Selisih % | Penjelasan |
|---|---:|---:|---:|---|
| `market.price_per_share (NTD)` | 2,235.00 | 2,380.00 | -6.09% | Harga tanggal perdagangan terbaru (`2026-11-09`) vs tanggal berkas manual (`2026-09-14`) |
| `market.shares_issued_thousands` | 25,932,370.1 | 25,932,524.0 | -0.00% | OpenAPI TWSE `t187ap03_L` (selisih < 0,001%) |
| `balance_sheet.cash_and_equivalents (2025-12-31)` | **2,767,856.4** | **2,767,856.4** | **+0.00%** | **Identik persis** (`CashAndCashEquivalents`) |
| `balance_sheet.short_term_investments (2025-12-31)` | **300,638.2** | **300,638.2** | **+0.00%** | **Identik persis** (`FinancialAssetsAtAmortizedCost` 124.945,5 + `FVOCI` 175.692,7) |
| `balance_sheet.current_portion_lt_debt (2025-12-31)` | 0.0 | 136,926.5 | -100.00% | Dataset `TaiwanStockBalanceSheet` FinMind menggabungkan `一年內到期長期負債` ke `OtherCurrentLiabilities` |
| `balance_sheet.long_term_debt (2025-12-31)` | **896,062.0** | **896,062.0** | **+0.00%** | **Identik persis** (`BondsPayable` 856.227,5 + `LongtermBorrowings` 39.834,5) |
| `cash_flow.cfo_by_year[2023]` | 1,241,967.3 | 1,600,000.0 | -22.38% | Berkas manual memakai angka **perkiraan** bulat (lihat di bawah) |
| `cash_flow.capex_by_year[2023]` | 949,816.8 | 1,313,000.0 | -27.66% | Berkas manual memakai angka **perkiraan** bulat |
| `cash_flow.interest_expense_by_year[2023]` | 11,999.4 | 12,000.0 | -0.01% | Pembulatan di berkas manual |
| `cash_flow.cfo_by_year[2024]` | 1,826,177.1 | 2,000,000.0 | -8.69% | Berkas manual memakai angka **perkiraan** bulat |
| `cash_flow.capex_by_year[2024]` | 956,006.5 | 1,140,000.0 | -16.14% | Berkas manual memakai angka **perkiraan** bulat |
| `cash_flow.interest_expense_by_year[2024]` | 10,495.3 | 12,000.0 | -12.54% | Berkas manual memakai angka **perkiraan** bulat |
| `cash_flow.cfo_by_year[2025]` | **2,274,975.6** | **2,274,980.0** | **-0.00%** | Laporan tahunan penuh 2025 (selisih pembulatan 0,0002%) |
| `cash_flow.capex_by_year[2025]` | **1,272,410.5** | **1,272,400.0** | **+0.00%** | Laporan tahunan penuh 2025 (selisih pembulatan 0,0008%) |
| `cash_flow.interest_expense_by_year[2025]` | **12,370.4** | **12,300.0** | **+0.57%** | `InterestExpense` 2025 FinMind vs pembulatan manual (< 1%) |
| `tax.income_tax_expense` | 326,266.1 | 346,500.0 | -5.84% | Jumlah 4 kuartal `TAX` 2025 FinMind |
| `tax.pretax_income` | **2,041,662.8** | **2,041,600.0** | **+0.00%** | Jumlah 4 kuartal `PreTaxIncome` 2025 FinMind |
| `DCF: FCFF 2025 (fcff0)` | **1,012,958.7** | **1,012,792.4** | **+0.02%** | Selisih hanya **+0,02%** (< 1%) |
| `DCF: FCFF 3y average` | **731,393.2** | **726,573.1** | **+0.66%** | Selisih hanya **+0,66%** (< 1%) |
| `wacc_inputs.beta` | 1.0122 | 1.2500 | -19.02% | Regresi mingguan 2 tahun (103 pekan vs `^TWII`) vs beta 5Y bulanan Yahoo di berkas manual |
| `DCF: WACC` | 6.92% | 8.09% | -14.48% | Dipengaruhi perbedaan $\beta$ (2Y mingguan 1,0122 vs 5Y bulanan 1,25) |
| `DCF: implied_growth (g tersirat)` | 5.02% | 6.29% | -20.27% | Keduanya sama-sama di atas batas pertumbuhan abadi 3,50% (`exceeds_ceiling = True`) |

### Penjelasan Selisih 2023–2024 dan Penanganan Utang Lancar (Item D-c)
1. **Arus kas 2023 dan 2024**: pada `valuation/inputs/2330.json`, catatan `sources.cash_flow` secara eksplisit menyebutkan: *"Angka 2023-2024 disetel agar FCFF cocok dengan hitungan tangan PDK (297 dan 870 bio) — PERKIRAAN, wajib diganti angka asli"*. Meskipun CFO dan Capex 2023–2024 di berkas manual merupakan angka perkiraan bulat (`1.600.000` / `1.313.000` dan `2.000.000` / `1.140.000`), selisih $\text{CFO} - \text{Capex}$ dari angka audit asli FinMind menghasilkan FCFF 2023 sebesar `302,2` miliar NTD (vs `297,0` miliar manual) dan FCFF 2024 sebesar `879,0` miliar NTD (vs `870,0` miliar manual), sehingga rata-rata FCFF 3 tahun hanya berselisih **+0,66%**.
2. **`current_portion_lt_debt` dan `short_term_borrowings` (D-c)**: dataset `TaiwanStockBalanceSheet` di FinMind tidak menyajikan pos `一年內到期長期負債` secara terpisah, melainkan menggabungkannya ke dalam `OtherCurrentLiabilities` (`其他流動負債`). Pada `2330` (TSMC), laporan audit resmi MOPS mencatat bagian lancar utang jangka panjang sebesar NT\$136.926,5 juta. Tanpa pos ini, utang otomatis `2330` tercatat sebesar NT\$896.062,0 juta (`BondsPayable` + `LongtermBorrowings`), atau sekitar 13,25% lebih rendah daripada utang berbobot bunga sebenarnya (NT\$1.032.988,5 juta). Pos pinjaman bank jangka pendek (`ShorttermBorrowings` / `短期借款`) kini dipisah ke field `short_term_borrowings` (untuk `2330` bernilai 0,0) dan dihitung di `scripts/dcf.py` (`debt = current_portion_lt_debt + long_term_debt + short_term_borrowings`). Bila pos bagian lancar utang jangka panjang tidak tersedia secara terpisah, sistem menandai field tersebut di daftar `"tidak_tersedia": ["current_portion_lt_debt"]` dan menampilkan peringatan tiga bahasa di tab Valuation. Pada integrasi D-b, kertas kerja manual mengisi field yang tidak tersedia ini.

---


## 4. Evaluasi 10 Emiten Non-Keuangan Acak (`--acak 10 --seed 7`)

Hasil menjalankan `python3 scripts/valuasi_otomatis.py --acak 10 --seed 7 --simpan` (tersimpan di [`eval/hasil/b2-2026-11-10.md`](../eval/hasil/b2-2026-11-10.md)):

| # | Kode | Nama | Bursa | Harga (NTD) | Kap. Pasar (Juta NTD) | FCFF0 (Juta NTD) | WACC | Beta (Cadangan?) | g Tersirat | Status |
|---:|---|---|---|---|---:|---:|---:|---|---:|---|
| 1 | `3416` | Winmate | TWSE | 152.00 | 12,846.7 | 467.8 | 6.85% | 0.9663 (103w) | 2.74% | `ok` |
| 2 | `9939` | HON CHUAN | TWSE | 118.00 | 34,902.8 | 2,865.5 | 2.15% | 0.0472 (103w) | -4.12% | `ok` |
| 3 | `4506` | GFC | TPEx | 115.50 | 20,444.9 | 1,508.2 | 2.37% | 0.0861 (103w) | -5.95% | `ok` |
| 4 | `6811` | AEB | TPEx | 240.00 | 9,947.8 | 581.3 | 6.54% | 0.9174 (103w) | 0.07% | `ok` |
| 5 | `3346` | Laster Tech | TWSE | 18.50 | 2,242.7 | 252.9 | 3.58% | 1.0259 (103w) | -2.63% | `ok` |
| 6 | `8433` | BON FAME | TPEx | 49.10 | 2,676.2 | 8.5 | 3.26% | 0.1941 (103w) | 2.83% | `ok` |
| 7 | `1708` | SESODA | TWSE | 46.00 | 11,454.1 | 1,280.7 | 4.20% | 0.4519 (103w) | -5.61% | `ok` |
| 8 | `1560` | KINIK | TWSE | 735.00 | 110,462.8 | 895.3 | 9.25% | 1.4897 (103w) | 8.38% | `ok` |
| 9 | `5285` | Jih Lin | TWSE | 72.30 | 7,377.6 | 347.5 | 6.03% | 0.9697 (103w) | 1.25% | `ok` |
| 10 | `6173` | P.D.C. | TPEx | 208.00 | 33,473.0 | 769.4 | 12.04% | 2.0159 (103w) | 9.44% | `ok` |

Selain itu, emiten yang kebetulan memiliki $\text{FCFF}_0 \le 0$ pada tahun fiskal 2025 ketika sampel ditarik (seperti `6945`, `3049`, `1587`, `8068`, `6223`, `3234`) ditandai secara jujur sebagai `tidak_bisa_dihitung` beserta nilai $\text{FCFF}_{2025}$-nya tanpa menghasilkan angka pertumbuhan semu.

---

## 5. Temuan untuk Claude

Sesuai aturan pembagian berkas, berkas di luar kepemilikan B2/D3 tidak diubah. Berikut temuan pada berkas bersama yang sudah ditangani di sisi `app/valuasi_otomatis.py`, beserta usulan perbaikan bila Claude ingin memperketat berkas intinya:

1. **`scripts/dcf.py` baris 141 (`rd = w["total_interest_expense"] / debt`)**
   - **Gejala**: Memunculkan `ZeroDivisionError: float division by zero` untuk emiten bebas utang berbunga (`current_portion_lt_debt + long_term_debt == 0`, misalnya `2305` 全友 atau `1732` 毛寶).
   - **Penanganan saat ini di `app/valuasi_otomatis.py`**: Bila total utang berbunga $= 0$, `long_term_debt` diisi $10^{-6}$ juta NTD ($1\text{ NTD}$) dan `total_interest_expense = 0.0` dengan catatan peringatan `va.warn.tanpa_utang`, sehingga $r_d = 0\%$, $w_e \approx 100\%$, dan $\text{WACC} = r_e$.
   - **Usulan untuk `scripts/dcf.py`**: Ubah baris 141 menjadi `rd = (w["total_interest_expense"] / debt) if debt > 0 else 0.0`.

2. **`scripts/dcf.py` baris 66 (`tax["income_tax_expense"] / tax["pretax_income"]`)**
   - **Gejala**: Memunculkan `ZeroDivisionError` bila `pretax_income == 0`, atau menghasilkan tarif pajak efektif negatif / $>100\%$ bila emiten merugi sebelum pajak (`pretax_income < 0`, misalnya `1467` 南緯).
   - **Penanganan saat ini di `app/valuasi_otomatis.py`**: Bila `pretax_income <= 0`, `income_tax_expense < 0`, atau `income_tax_expense >= pretax_income`, perisai pajak efektif disetel ke $0\%$ (`income_tax_expense = 0.0`, `pretax_income = max(abs(pretax_raw), 1.0)`) dan diberi peringatan `va.warn.pajak_tidak_normal`.
   - **Usulan untuk `scripts/dcf.py`**: Batasi `effective_tax_rate` di rentang $[0, 1]$ dan tangani `pretax_income <= 0` dengan mengembalikan `0.0`.

3. **`scripts/dcf.py` baris 99 & 167 (`implied_growth` dan `circularity.drift_pct`)**
   - **Gejala**: Bila $\text{EV} \le 0$ (kas melebihi kapitalisasi pasar ditambah utang) atau $\text{FCFF}_0 \le 0$, `ev_from_growth()` dapat mengembalikan `None` sehingga `abs(back - ev)` di baris 167 memunculkan `TypeError`.
   - **Penanganan saat ini di `app/valuasi_otomatis.py`**: `bangun(kode)` memeriksa $\text{FCFF}_0 > 0$ dan $\text{EV} > 0$ terlebih dahulu dan mengembalikan status `tidak_bisa_dihitung` dengan pesan tiga bahasa sebelum memanggil `dcf.compute()`.

4. **`app/main.py` baris 234 (`watchlist()`)**
   - **Gejala**: `tervaluasi = set(store.emiten_tervaluasi())` hanya memeriksa berkas di `valuation/inputs/*.json`, sehingga kolom indikator valuasi di halaman `/watchlist` hanya menyala untuk `2330` walaupun cache valuasi otomatis di `DATA_DIR/valuasi_otomatis/` sudah terisi.
   - **Usulan untuk `app/store.py` / `app/main.py`**: Bila diinginkan agar lencana di `/watchlist` juga mencerminkan emiten yang sudah punya valuasi otomatis yang layak DCF, `store.emiten_tervaluasi()` dapat menggabungkan kode dari `VALUATION_DIR` dan `valuasi_otomatis.CACHE_DIR` yang `layak_dcf(d) == True`.
