"""Pembangun input DCF otomatis untuk emiten non-keuangan TWSE & TPEx (Tugas B2).

Menyusun struktur input dengan skema yang sama persis dengan `valuation/inputs/2330.json`
supaya `scripts/dcf.py::compute()` dan `app/agent/recompute.py` dapat dipakai langsung
tanpa perubahan.

Sumber data (semua gratis, dapat diaudit):
- Harga penutupan: OpenAPI TWSE (`STOCK_DAY_ALL`) / TPEx (`tpex_mainboard_daily_close_quotes`)
  lewat `app.pasar.harga(kode)`.
- Profil & lembar saham beredar: OpenAPI TWSE/TPEx (`t187ap03_L` / `mopsfin_t187ap03_O`)
  lewat `app.pasar.profil(kode)`, dengan cadangan `CapitalStock / 10` dari neraca.
- Neraca, laporan arus kas (3 tahun fiskal penuh terakhir), dan laba rugi (pajak 4 kuartal):
  FinMind (`TaiwanStockBalanceSheet`, `TaiwanStockCashFlowsStatement`,
  `TaiwanStockFinancialStatements`) lewat `app.pasar.keuangan_mentah(kode, ...)`.
- Beta: regresi return mingguan 2 tahun saham terhadap TAIEX (`^TWII`) dari
  Yahoo Finance chart API (`v8/finance/chart/{simbol}?range=2y&interval=1wk`).
  Bila pasangan mingguan < 52 atau gagal ambil, jatuh ke beta cadangan 1,0 dengan alasan.

Semua nilai uang dalam **juta NTD** (nilai FinMind dalam NTD dibagi `1e6`).
Hasil disimpan di `DATA_DIR/valuasi_otomatis/{kode}.json` (TTL 12 jam) dan tidak pernah
menimpa berkas manual di `valuation/inputs/{kode}.json`.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from app import config, i18n, pasar
from scripts import dcf

log = logging.getLogger(__name__)

CACHE_DIR: Path = Path(config.DATA_DIR) / "valuasi_otomatis"
TTL_VALUASI = 12 * 3600  # 12 jam
TTL_BETA = 7 * 86400     # 7 hari untuk deret harga mingguan 2 tahun

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{simbol}?range=2y&interval=1wk"
SIMBOL_INDEKS = "^TWII"
MIN_MINGGU_BETA = 52

# Parameter WACC pasar Taiwan — sama persis dengan valuation/inputs/2330.json
RISK_FREE_RATE = 0.0194
EQUITY_RISK_PREMIUM = 0.0501
TERMINAL_GROWTH_CEILING = 0.035

SUMBER_RF = (
    "Imbal hasil obligasi pemerintah Taiwan 10 tahun (~1,94%) — "
    "https://ca.investing.com/rates-bonds/taiwan-10-year-bond-yield-historical-data"
)
SUMBER_ERP = (
    "Damodaran country equity risk premium, Taiwan (~5,01%) — "
    "https://pages.stern.nyu.edu/adamodar/New_Home_Page/datafile/ctryprem.html"
)
SUMBER_G_CEILING = (
    "Proyeksi pertumbuhan PDB nominal jangka panjang Taiwan (~3,5%, DGBAS / IMF WEO)"
)


def _sekarang_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normal_tanggal_harga(tgl: str | None) -> str:
    """Ubah tanggal ROC '1150410' atau '115/04/10' menjadi '2026-04-10'."""
    s = (tgl or "").strip().replace("/", "").replace("-", "")
    if len(s) == 7 and s.isdigit():
        th = int(s[:3]) + 1911
        return f"{th:04d}-{s[3:5]}-{s[5:7]}"
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return (tgl or "").strip() or dt.date.today().isoformat()


def _ambil_yahoo_chart(simbol: str) -> dict:
    """Ambil JSON chart mingguan 2 tahun dari Yahoo Finance."""
    simbol_aman = urllib.parse.quote(simbol, safe="")
    url = YAHOO_CHART_URL.format(simbol=simbol_aman)
    req = urllib.request.Request(url, headers={"User-Agent": pasar.UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _seri_mingguan_yahoo(simbol: str) -> list[dict]:
    """Kembalikan daftar [{'pekan': 'YYYY-Www', 'tutup': float}] terurut dari Yahoo Finance."""
    kunci_cache = "yahoo_1wk_2y_" + simbol.replace("^", "IDX_").replace(".", "_")

    def _tarik():
        mentah = _ambil_yahoo_chart(simbol)
        hasil = ((mentah or {}).get("chart") or {}).get("result") or []
        if not hasil:
            return []
        r0 = hasil[0]
        ts_list = r0.get("timestamp") or []
        ind = r0.get("indicators") or {}
        adj_list = ((ind.get("adjclose") or [{}])[0]).get("adjclose") if ind.get("adjclose") else None
        close_list = ((ind.get("quote") or [{}])[0]).get("close") if ind.get("quote") else None
        seri_harga = adj_list if adj_list else (close_list or [])

        per_pekan: dict[str, float] = {}
        for ts, h in zip(ts_list, seri_harga):
            if ts is None or h is None:
                continue
            try:
                val = float(h)
            except (TypeError, ValueError):
                continue
            if val <= 0:
                continue
            tgl = dt.datetime.fromtimestamp(int(ts), tz=dt.timezone.utc).date()
            iso_th, iso_mg, _ = tgl.isocalendar()
            per_pekan[f"{iso_th:04d}-W{iso_mg:02d}"] = val

        return [{"pekan": k, "tutup": per_pekan[k]} for k in sorted(per_pekan)]

    data, _ = pasar._dengan_cache(kunci_cache, TTL_BETA, _tarik)
    return data if isinstance(data, list) else []


def _return_per_pekan(seri: list[dict]) -> dict[str, float]:
    """Hitung return mingguan (P_t / P_{t-1} - 1) dari deret harga mingguan terurut."""
    ret: dict[str, float] = {}
    for i in range(1, len(seri)):
        p0 = seri[i - 1].get("tutup")
        p1 = seri[i].get("tutup")
        pekan = seri[i].get("pekan")
        if p0 and p1 and p0 > 0 and pekan:
            ret[pekan] = (p1 - p0) / p0
    return ret


def hitung_beta(kode: str, bursa: str = "TWSE") -> dict:
    """Hitung beta 2 tahun mingguan saham terhadap TAIEX (^TWII).

    beta = cov(r_s, r_m) / var(r_m) pada pekan yang sama.
    Bila pasangan pekan < 52, gagal ambil, atau var(r_m) == 0 → beta 1,0 dengan
    `beta_cadangan: True` dan alasan 3 bahasa.
    """
    akhiran = ".TWO" if (bursa or "").upper() == "TPEX" else ".TW"
    simbol_saham = f"{kode}{akhiran}"
    url_saham = YAHOO_CHART_URL.format(simbol=simbol_saham)
    url_indeks = YAHOO_CHART_URL.format(simbol="%5ETWII")

    seri_s = _seri_mingguan_yahoo(simbol_saham)
    seri_m = _seri_mingguan_yahoo(SIMBOL_INDEKS)

    if not seri_s or not seri_m:
        alasan = i18n.pesan("va.beta.gagal_ambil")
        return {
            "beta": 1.0,
            "beta_cadangan": True,
            "jumlah_pekan": 0,
            "simbol": simbol_saham,
            "url_saham": url_saham,
            "url_indeks": url_indeks,
            "alasan": alasan["teks"],
            "alasan_i18n": alasan,
        }

    ret_s = _return_per_pekan(seri_s)
    ret_m = _return_per_pekan(seri_m)
    pekan_sama = sorted(set(ret_s) & set(ret_m))
    n = len(pekan_sama)

    if n < MIN_MINGGU_BETA:
        alasan = i18n.pesan("va.beta.kurang_data", n=n)
        return {
            "beta": 1.0,
            "beta_cadangan": True,
            "jumlah_pekan": n,
            "simbol": simbol_saham,
            "url_saham": url_saham,
            "url_indeks": url_indeks,
            "alasan": alasan["teks"],
            "alasan_i18n": alasan,
        }

    xs = [ret_s[p] for p in pekan_sama]
    xm = [ret_m[p] for p in pekan_sama]
    rata_s = sum(xs) / n
    rata_m = sum(xm) / n
    cov = sum((s - rata_s) * (m - rata_m) for s, m in zip(xs, xm))
    var_m = sum((m - rata_m) ** 2 for m in xm)

    if var_m <= 1e-18:
        alasan = i18n.pesan("va.beta.varians_nol")
        return {
            "beta": 1.0,
            "beta_cadangan": True,
            "jumlah_pekan": n,
            "simbol": simbol_saham,
            "url_saham": url_saham,
            "url_indeks": url_indeks,
            "alasan": alasan["teks"],
            "alasan_i18n": alasan,
        }

    beta_hitung = round(cov / var_m, 4)
    # Jaga agar beta ekstrem negatif atau tidak masuk akal tetap tercatat apa adanya
    # kecuali <= 0 (beta <= 0 tidak bermakna untuk biaya ekuitas CAPM perusahaan operasi).
    if beta_hitung <= 0:
        alasan = i18n.pesan("va.beta.varians_nol")
        return {
            "beta": 1.0,
            "beta_cadangan": True,
            "jumlah_pekan": n,
            "simbol": simbol_saham,
            "url_saham": url_saham,
            "url_indeks": url_indeks,
            "alasan": alasan["teks"],
            "alasan_i18n": alasan,
        }

    return {
        "beta": beta_hitung,
        "beta_cadangan": False,
        "jumlah_pekan": n,
        "pekan_awal": pekan_sama[0],
        "pekan_akhir": pekan_sama[-1],
        "simbol": simbol_saham,
        "url_saham": url_saham,
        "url_indeks": url_indeks,
        "alasan": "",
        "alasan_i18n": None,
    }


def _kelompok_per_tanggal(
    baris_atau_tuple: list[dict] | tuple[list[dict] | None, dict] | None,
) -> tuple[dict[str, dict[str, float]], dict[str, list[dict]]]:
    """Kelompokkan baris FinMind menjadi ({tanggal: {type: value}}, {tanggal: [baris_mentah]})."""
    if isinstance(baris_atau_tuple, tuple):
        baris = baris_atau_tuple[0] or []
    else:
        baris = baris_atau_tuple or []
    per_tgl: dict[str, dict[str, float]] = {}
    mentah_tgl: dict[str, list[dict]] = {}
    for b in baris:
        if not isinstance(b, dict):
            continue
        tgl = b.get("date")
        pos = b.get("type")
        val = b.get("value")
        if not tgl or not pos or val is None:
            continue
        try:
            angka = float(val)
        except (TypeError, ValueError):
            continue
        per_tgl.setdefault(tgl, {})[pos] = angka
        mentah_tgl.setdefault(tgl, []).append(b)
    return per_tgl, mentah_tgl


def _cari_utang_lancar_neraca(pos_tgl: dict[str, float], baris_tgl: list[dict]) -> tuple[float, list[str], bool]:
    """Cari bagian lancar utang jangka panjang & pinjaman jangka pendek dari neraca FinMind.

    Mengembalikan (nilai_ntd, daftar_pos_dipakai, ada_bagian_lancar_eksplisit).
    Catatan: FinMind TaiwanStockBalanceSheet menggabungkan `一年內到期長期負債`
    ke dalam `OtherCurrentLiabilities` (`其他流動負債`), namun beberapa emiten
    melaporkan `ShorttermBorrowings` (`短期借款`) atau pos `LongtermLiabilitiesCurrentPortion`.
    """
    pos_utang_pendek = (
        "LongtermLiabilitiesCurrentPortion",
        "CurrentPortionOfLongtermLiabilities",
        "LongTermLiabilitiesCurrentPortion",
        "ShorttermBorrowings",
        "ShortTermBorrowings",
        "ShorttermNotesAndBillsPayable",
    )
    dipakai: list[str] = []
    total = 0.0
    ada_eksplisit = False

    for k in pos_utang_pendek:
        if k in pos_tgl and pos_tgl[k] is not None:
            total += float(pos_tgl[k])
            dipakai.append(k)
            if "Long" in k or "CurrentPortion" in k:
                ada_eksplisit = True

    for b in baris_tgl:
        t = b.get("type") or ""
        orig = b.get("origin_name") or ""
        if t not in dipakai and ("一年內到期" in orig or "一年或一營業週期內到期" in orig):
            try:
                total += float(b.get("value") or 0.0)
                dipakai.append(f"{t}({orig})")
                ada_eksplisit = True
            except (TypeError, ValueError):
                pass

    return total, dipakai, ada_eksplisit


def _status_tidak_berlaku(kode: str, nama: str, bursa: str, industri: str, dibangun: str) -> dict:
    label_ind = i18n.t(f"ind.{industri}", "id") if industri else "Keuangan"
    alasan = i18n.pesan("va.otomatis.keuangan", industri=label_ind)
    return {
        "code": kode,
        "name": nama or kode,
        "bursa": bursa,
        "otomatis": True,
        "dibangun": dibangun,
        "tidak_berlaku": True,
        "tidak_bisa_dihitung": False,
        "alasan": alasan["teks"],
        "alasan_i18n": alasan,
        "peringatan": [],
        "sources": {
            "profile": f"TWSE/TPEx OpenAPI profile (industry code {industri or '17'}: financials & insurance)",
        },
    }


def _status_tidak_bisa(
    kode: str,
    nama: str,
    bursa: str,
    dibangun: str,
    alasan: dict,
    peringatan: list[dict] | None = None,
    sources: dict | None = None,
) -> dict:
    return {
        "code": kode,
        "name": nama or kode,
        "bursa": bursa,
        "otomatis": True,
        "dibangun": dibangun,
        "tidak_berlaku": False,
        "tidak_bisa_dihitung": True,
        "alasan": alasan["teks"],
        "alasan_i18n": alasan,
        "peringatan": peringatan or [],
        "sources": sources or {},
    }


def bangun(kode: str) -> dict:
    """Bangun input DCF otomatis untuk `kode` dengan skema identik `valuation/inputs/2330.json`.

    - Emiten keuangan (industri 17) → `{"tidak_berlaku": True, "alasan": ..., ...}`
    - Data kurang / FCFF <= 0 / EV <= 0 → `{"tidak_bisa_dihitung": True, "alasan": ..., ...}`
    - Berhasil → dict siap masuk `dcf.compute(d)` dan `recompute.hitung_ulang(...)`.
    """
    kode = (kode or "").strip()
    dibangun = _sekarang_iso()
    peringatan: list[dict] = []

    prof = pasar.profil(kode) or {}
    hrg = pasar.harga(kode) or {}

    nama = prof.get("nama_en") or prof.get("nama_asing") or prof.get("nama") or hrg.get("nama") or kode
    bursa = prof.get("bursa") or hrg.get("bursa") or "TWSE"
    industri = str(prof.get("industri_kode") or prof.get("industri") or "").strip()

    # 1. Cek emiten keuangan (industri 17 TWSE/TPEx)
    if prof.get("keuangan") or industri == "17":
        return _status_tidak_berlaku(kode, nama, bursa, industri or "17", dibangun)

    # 2. Harga penutupan
    harga_tutup = hrg.get("tutup")
    if harga_tutup is None or float(harga_tutup) <= 0:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.tanpa_harga", kode=kode),
        )
    harga_tutup = float(harga_tutup)
    tgl_harga = _normal_tanggal_harga(hrg.get("tanggal"))
    url_harga = pasar.SUMBER_PASAR["harga_tpex"] if bursa == "TPEx" else pasar.SUMBER_PASAR["harga_twse"]

    # 3. Ambil laporan keuangan mentah FinMind
    neraca_mentah = pasar.keuangan_mentah(kode, "neraca")
    arus_mentah = pasar.keuangan_mentah(kode, "arus")
    lr_mentah = pasar.keuangan_mentah(kode, "lr")

    neraca_tgl, neraca_baris_tgl = _kelompok_per_tanggal(neraca_mentah)
    arus_tgl, _ = _kelompok_per_tanggal(arus_mentah)
    lr_tgl, _ = _kelompok_per_tanggal(lr_mentah)

    if not neraca_tgl:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.tanpa_neraca", kode=kode),
        )

    # 4. Arus kas 3 tahun fiskal penuh terakhir (kumulatif YTD → nilai per 31 Des)
    tahun_arus_penuh = sorted(
        tgl for tgl, pos in arus_tgl.items()
        if tgl.endswith("-12-31")
        and pos.get("CashFlowsFromOperatingActivities") is not None
        and pos.get("PropertyAndPlantAndEquipment") is not None
    )
    if len(tahun_arus_penuh) < 3:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.kurang_3_tahun", n=len(tahun_arus_penuh)),
        )

    tiga_tgl = tahun_arus_penuh[-3:]
    tahun_fiskal = int(tiga_tgl[-1][:4])

    cfo_by_year: dict[str, float] = {}
    capex_by_year: dict[str, float] = {}
    interest_by_year: dict[str, float] = {}
    pos_bunga_dipakai: list[str] = []
    pakai_bayar_bunga = False
    pakai_bunga_nol = False

    for tgl in tiga_tgl:
        th = tgl[:4]
        pos = arus_tgl[tgl]
        cfo_by_year[th] = round(float(pos["CashFlowsFromOperatingActivities"]) / 1e6, 1)
        capex_by_year[th] = round(abs(float(pos["PropertyAndPlantAndEquipment"])) / 1e6, 1)
        if pos.get("InterestExpense") is not None:
            interest_by_year[th] = round(abs(float(pos["InterestExpense"])) / 1e6, 1)
            pos_bunga_dipakai.append(f"{th}:InterestExpense")
        elif pos.get("PayTheInterest") is not None:
            interest_by_year[th] = round(abs(float(pos["PayTheInterest"])) / 1e6, 1)
            pos_bunga_dipakai.append(f"{th}:PayTheInterest")
            pakai_bayar_bunga = True
        else:
            interest_by_year[th] = 0.0
            pos_bunga_dipakai.append(f"{th}:0(absent)")
            pakai_bunga_nol = True

    if pakai_bayar_bunga:
        peringatan.append(i18n.pesan("va.warn.bunga_pakai_bayar"))
    if pakai_bunga_nol:
        peringatan.append(i18n.pesan("va.warn.bunga_nol"))

    # 5. Neraca: gunakan akhir tahun fiskal `{tahun_fiskal}-12-31` bila tersedia supaya
    # selaras dengan periode tahunan laporan arus kas & pajak (serta identik 100% dengan
    # berkas manual 2330.json), atau jatuh ke kuartal neraca terakhir bila belum ada.
    tgl_neraca_target = f"{tahun_fiskal}-12-31"
    if tgl_neraca_target in neraca_tgl:
        tgl_neraca = tgl_neraca_target
    else:
        tgl_neraca = max(neraca_tgl)

    pos_n = neraca_tgl[tgl_neraca]
    baris_n = neraca_baris_tgl.get(tgl_neraca, [])

    # Jumlah saham (ribuan lembar): utamakan profil bursa, cadangan CapitalStock / 10 / 1000
    lembar_profil = prof.get("lembar")
    sumber_saham = ""
    if lembar_profil and int(lembar_profil) > 0:
        issued_shares_thousands = round(float(lembar_profil) / 1000.0, 3)
        if issued_shares_thousands.is_integer():
            issued_shares_thousands = int(issued_shares_thousands)
        url_prof = pasar.SUMBER_PASAR["profil_tpex"] if bursa == "TPEx" else pasar.SUMBER_PASAR["profil_twse"]
        sumber_saham = (
            f"{bursa} OpenAPI company profile ({url_prof}), "
            f"issued common shares {int(lembar_profil):,} shares ÷ 1,000"
        )
    else:
        cap_stock = pos_n.get("CapitalStock") or pos_n.get(max(neraca_tgl), {}).get("CapitalStock") if isinstance(pos_n.get("CapitalStock"), (int, float)) else pos_n.get("CapitalStock")
        if not cap_stock or float(cap_stock) <= 0:
            # Cek juga kuartal paling akhir bila di tgl_neraca tidak ada CapitalStock
            cap_stock = neraca_tgl[max(neraca_tgl)].get("CapitalStock")
        if not cap_stock or float(cap_stock) <= 0:
            return _status_tidak_bisa(
                kode, nama, bursa, dibangun,
                i18n.pesan("va.otomatis.tanpa_saham", kode=kode),
                peringatan=peringatan,
            )
        issued_shares_thousands = round(float(cap_stock) / 10.0 / 1000.0, 3)
        if issued_shares_thousands.is_integer():
            issued_shares_thousands = int(issued_shares_thousands)
        peringatan.append(i18n.pesan("va.warn.saham_neraca"))
        sumber_saham = (
            f"FinMind TaiwanStockBalanceSheet ({tgl_neraca}) CapitalStock "
            f"NT${float(cap_stock):,.0f} ÷ NT$10 par value ÷ 1,000"
        )

    kas_ntd = float(pos_n.get("CashAndCashEquivalents") or 0.0)
    cash_and_equivalents = round(kas_ntd / 1e6, 1)

    # Short-term investments: FinancialAssetsAtAmortizedCost + FinancialAssetsAtFairvalueThroughOtherComprehensiveIncome
    sti_pos: list[str] = []
    sti_ntd = 0.0
    for k_sti in (
        "FinancialAssetsAtAmortizedCost",
        "FinancialAssetsAtFairvalueThroughOtherComprehensiveIncome",
    ):
        if pos_n.get(k_sti) is not None:
            sti_ntd += float(pos_n[k_sti])
            sti_pos.append(k_sti)
    short_term_investments = round(sti_ntd / 1e6, 1)

    # Utang jangka panjang: BondsPayable + LongtermBorrowings
    lt_pos: list[str] = []
    lt_ntd = 0.0
    for k_lt in ("BondsPayable", "LongtermBorrowings"):
        if pos_n.get(k_lt) is not None:
            lt_ntd += float(pos_n[k_lt])
            lt_pos.append(k_lt)
    long_term_debt = round(lt_ntd / 1e6, 1)

    # Bagian lancar utang jangka panjang / pinjaman jangka pendek
    cp_ntd, cp_pos, ada_cp_eksplisit = _cari_utang_lancar_neraca(pos_n, baris_n)
    current_portion_lt_debt = round(cp_ntd / 1e6, 1)
    if not ada_cp_eksplisit:
        peringatan.append(i18n.pesan("va.warn.utang_lancar_gabung"))

    # 6. Pajak: jumlah 4 kuartal tahun fiskal terakhir dari laporan laba rugi tunggal
    kuartal_lr = sorted(
        tgl for tgl in lr_tgl
        if tgl.startswith(f"{tahun_fiskal}-")
    )
    if not kuartal_lr:
        # Cadangan: pakai 4 kuartal terakhir yang ada
        kuartal_lr = sorted(lr_tgl)[-4:]

    pajak_mentah_ntd = sum(float(lr_tgl[q].get("TAX") or 0.0) for q in kuartal_lr)
    pretax_mentah_ntd = sum(
        float(
            lr_tgl[q].get("PreTaxIncome")
            if lr_tgl[q].get("PreTaxIncome") is not None
            else (lr_tgl[q].get("NetIncomeBeforeTax") or 0.0)
        )
        for q in kuartal_lr
    )
    tax_raw_m = round(pajak_mentah_ntd / 1e6, 1)
    pretax_raw_m = round(pretax_mentah_ntd / 1e6, 1)

    if pretax_raw_m <= 0 or tax_raw_m < 0 or tax_raw_m >= pretax_raw_m:
        income_tax_expense = 0.0
        pretax_income = round(max(abs(pretax_raw_m), 1.0), 1)
        peringatan.append(i18n.pesan("va.warn.pajak_tidak_normal", tahun=str(tahun_fiskal)))
    else:
        income_tax_expense = tax_raw_m
        pretax_income = pretax_raw_m

    # 7. Beta dari harga mingguan 2 tahun vs TAIEX
    info_beta = hitung_beta(kode, bursa=bursa)
    beta_val = info_beta["beta"]
    beta_cadangan = bool(info_beta["beta_cadangan"])

    # 8. Penanganan emiten tanpa utang (agar dcf.py tidak ZeroDivisionError pada rd = interest / debt)
    bunga_terakhir = interest_by_year[str(tahun_fiskal)]
    total_utang = current_portion_lt_debt + long_term_debt
    tanpa_utang = total_utang <= 0
    if tanpa_utang:
        long_term_debt_input = 1e-6  # 1 NTD dalam juta NTD → rd = 0%, wd ≈ 0%, we ≈ 100%
        total_interest_input = 0.0
        peringatan.append(i18n.pesan("va.warn.tanpa_utang"))
    else:
        long_term_debt_input = long_term_debt
        total_interest_input = bunga_terakhir

    # 9. Susun dict input sesuai skema valuation/inputs/2330.json
    catatan_beta = (
        f"Yahoo Finance 2y weekly regression ({info_beta['simbol']} vs ^TWII, "
        f"{info_beta['jumlah_pekan']} weeks: {info_beta.get('pekan_awal', '')}..{info_beta.get('pekan_akhir', '')}) — "
        f"{info_beta['url_saham']} & {info_beta['url_indeks']}"
        if not beta_cadangan
        else (
            f"Fallback beta 1.0 ({info_beta['alasan']}) — "
            f"{info_beta['url_saham']} vs {info_beta['url_indeks']}"
        )
    )
    sources = {
        "price_per_share": (
            f"{bursa} OpenAPI daily closing quote ({url_harga}), "
            f"closing price NT${harga_tutup:,.2f} on {tgl_harga}"
        ),
        "shares_issued_thousands": sumber_saham,
        "balance_sheet": (
            f"FinMind TaiwanStockBalanceSheet ({pasar.FINMIND_URL}, stock_id={kode}, date={tgl_neraca}): "
            f"CashAndCashEquivalents={cash_and_equivalents:,.1f}M; "
            f"short_term_investments ({'+'.join(sti_pos) or 'none'})={short_term_investments:,.1f}M; "
            f"long_term_debt ({'+'.join(lt_pos) or 'none'})={long_term_debt:,.1f}M; "
            f"current_portion_lt_debt ({'+'.join(cp_pos) or 'folded into OtherCurrentLiabilities in FinMind'})="
            f"{current_portion_lt_debt:,.1f}M"
        ),
        "cash_flow": (
            f"FinMind TaiwanStockCashFlowsStatement ({pasar.FINMIND_URL}, stock_id={kode}, "
            f"dates={', '.join(tiga_tgl)}, cumulative YTD as of Dec 31): "
            f"cfo=CashFlowsFromOperatingActivities, capex=abs(PropertyAndPlantAndEquipment), "
            f"interest=({', '.join(pos_bunga_dipakai)})"
        ),
        "tax": (
            f"FinMind TaiwanStockFinancialStatements ({pasar.FINMIND_URL}, stock_id={kode}, "
            f"sum of {len(kuartal_lr)} single quarters in FY{tahun_fiskal}: {', '.join(kuartal_lr)}): "
            f"TAX={tax_raw_m:,.1f}M, PreTaxIncome={pretax_raw_m:,.1f}M"
        ),
        "risk_free_rate": SUMBER_RF,
        "beta": catatan_beta,
        "equity_risk_premium": SUMBER_ERP,
        "terminal_growth_ceiling": SUMBER_G_CEILING,
    }

    d = {
        "code": kode,
        "name": nama,
        "bursa": bursa,
        "currency": "TWD",
        "unit": "juta NTD kecuali disebut lain",
        "as_of": tgl_harga,
        "fiscal_year": tahun_fiskal,
        "otomatis": True,
        "dibangun": dibangun,
        "tidak_berlaku": False,
        "tidak_bisa_dihitung": False,
        "beta_cadangan": beta_cadangan,
        "alasan_beta": info_beta["alasan"],
        "alasan_beta_i18n": info_beta["alasan_i18n"],
        "jumlah_pekan_beta": info_beta["jumlah_pekan"],
        "peringatan": peringatan,
        "market": {
            "price_per_share": harga_tutup,
            "shares_issued_thousands": issued_shares_thousands,
        },
        "balance_sheet": {
            "as_of": tgl_neraca,
            "cash_and_equivalents": cash_and_equivalents,
            "short_term_investments": short_term_investments,
            "current_portion_lt_debt": current_portion_lt_debt,
            "current_portion_leases": 0.0,
            "long_term_debt": long_term_debt_input,
        },
        "cash_flow": {
            "cfo_by_year": cfo_by_year,
            "capex_by_year": capex_by_year,
            "interest_expense_by_year": interest_by_year,
        },
        "tax": {
            "income_tax_expense": income_tax_expense,
            "pretax_income": pretax_income,
        },
        "wacc_inputs": {
            "risk_free_rate": RISK_FREE_RATE,
            "beta": beta_val,
            "equity_risk_premium": EQUITY_RISK_PREMIUM,
            "total_interest_expense": total_interest_input,
            # Metadata tambahan agar ikut terbawa ke r["wacc_inputs"] saat dcf.compute(d) dipanggil
            "otomatis": True,
            "dibangun": dibangun,
            "beta_cadangan": beta_cadangan,
            "alasan_beta": info_beta["alasan"],
            "alasan_beta_i18n": info_beta["alasan_i18n"],
            "jumlah_pekan_beta": info_beta["jumlah_pekan"],
            "peringatan": peringatan,
        },
        "assumptions": {
            "include_leases_in_debt": False,
            "fcff_basis": "latest",
            "terminal_growth_ceiling": TERMINAL_GROWTH_CEILING,
        },
        "sources": sources,
    }

    # 10. Validasi FCFF0 > 0 dan EV > 0 sebelum diserahkan ke dcf.compute()
    tax_rate = income_tax_expense / pretax_income
    th_str = str(tahun_fiskal)
    fcff0 = (
        cfo_by_year[th_str]
        - capex_by_year[th_str]
        + interest_by_year[th_str] * (1.0 - tax_rate)
    )
    if fcff0 <= 0:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.fcff_negatif", tahun=th_str, fcff=round(fcff0, 1)),
            peringatan=peringatan,
            sources=sources,
        )

    market_cap = harga_tutup * (issued_shares_thousands / 1000.0)
    ev = market_cap + total_utang - (cash_and_equivalents + short_term_investments)
    if ev <= 0:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.ev_negatif", ev=round(ev, 1)),
            peringatan=peringatan,
            sources=sources,
        )

    # Pastikan dcf.compute(d) berhasil dan implied_growth bermakna
    try:
        hasil_dcf = dcf.compute(d)
    except Exception as e:
        log.warning("dcf.compute gagal untuk %s: %s", kode, e)
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.fcff_negatif", tahun=th_str, fcff=round(fcff0, 1)),
            peringatan=peringatan,
            sources=sources,
        )

    if hasil_dcf.get("implied_growth") is None:
        return _status_tidak_bisa(
            kode, nama, bursa, dibangun,
            i18n.pesan("va.otomatis.fcff_negatif", tahun=th_str, fcff=round(fcff0, 1)),
            peringatan=peringatan,
            sources=sources,
        )

    return d


# --- Cache di DATA_DIR/valuasi_otomatis/{kode}.json ----------------------------


def _jalur_cache(kode: str) -> Path:
    return CACHE_DIR / f"{kode}.json"


def baca_cache(kode: str, terima_basi: bool = True) -> dict | None:
    """Baca cache valuasi otomatis dari disk TANPA menyentuh jaringan."""
    f = _jalur_cache(kode)
    if not f.exists():
        return None
    if not terima_basi:
        umur = time.time() - f.stat().st_mtime
        if umur >= TTL_VALUASI:
            return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def simpan_cache(kode: str, data: dict) -> Path:
    """Simpan hasil `bangun(kode)` ke `DATA_DIR/valuasi_otomatis/{kode}.json`."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    f = _jalur_cache(kode)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def layak_dcf(data: dict | None) -> bool:
    """Apakah dict valuasi layak dipakai menghitung DCF (bukan tidak_berlaku/tidak_bisa_dihitung)."""
    if not isinstance(data, dict):
        return False
    if data.get("tidak_berlaku") or data.get("tidak_bisa_dihitung"):
        return False
    return "market" in data and "balance_sheet" in data and "cash_flow" in data


def dari_cache_untuk_pipeline(kode: str) -> dict | None:
    """Dipanggil oleh `store.muat_valuasi(kode)`: baca cache otomatis TANPA jaringan.

    Mengembalikan `None` bila belum ada cache atau berstatus `tidak_berlaku` /
    `tidak_bisa_dihitung`, supaya pipeline tetap menahan dengan `tanpa_valuasi`.
    """
    d = baca_cache(kode, terima_basi=True)
    return d if layak_dcf(d) else None


def ambil(kode: str, paksa: bool = False) -> dict:
    """Ambil valuasi otomatis untuk tab Valuation: pakai cache segar (< 12 jam) atau bangun baru."""
    if not paksa:
        segar = baca_cache(kode, terima_basi=False)
        if segar is not None:
            return segar
    try:
        baru = bangun(kode)
        simpan_cache(kode, baru)
        return baru
    except Exception as e:
        log.warning("valuasi_otomatis.ambil(%s) gagal: %s", kode, e)
        lama = baca_cache(kode, terima_basi=True)
        if lama is not None:
            return lama
        return _status_tidak_bisa(
            kode, kode, "TWSE", _sekarang_iso(),
            i18n.pesan("va.otomatis.tanpa_neraca", kode=kode),
        )


def segarkan(kode: str) -> dict:
    """Bangun ulang valuasi otomatis untuk `kode` (mis. saat pengumuman pasal 31 terbit)."""
    return ambil(kode, paksa=True)


def panaskan(daftar_kode: list[str], jeda: float = 0.3) -> dict[str, str]:
    """Panaskan cache valuasi otomatis untuk daftar kode emiten yang belum punya berkas manual.

    Berjalan sopan dengan jeda antar emiten yang benar-benar memanggil pembangun;
    galat dicatat tanpa menghentikan proses server.
    """
    ringkasan: dict[str, str] = {}
    perlu_jeda = False
    for kode in daftar_kode:
        kode = (kode or "").strip()
        if not kode:
            continue
        # Lewati bila berkas manual ada (berkas manual selalu menang)
        if (Path(config.VALUATION_DIR) / f"{kode}.json").exists():
            ringkasan[kode] = "manual"
            continue
        segar = baca_cache(kode, terima_basi=False)
        if segar is not None:
            if segar.get("tidak_berlaku"):
                ringkasan[kode] = "tidak_berlaku"
            elif segar.get("tidak_bisa_dihitung"):
                ringkasan[kode] = "tidak_bisa_dihitung"
            else:
                ringkasan[kode] = "cache_ok"
            continue

        if perlu_jeda and jeda > 0:
            time.sleep(jeda)
        try:
            d = bangun(kode)
            simpan_cache(kode, d)
            perlu_jeda = True
            if d.get("tidak_berlaku"):
                ringkasan[kode] = "tidak_berlaku"
            elif d.get("tidak_bisa_dihitung"):
                ringkasan[kode] = "tidak_bisa_dihitung"
            else:
                ringkasan[kode] = "ok"
        except Exception as e:
            log.warning("Gagal memanaskan valuasi otomatis %s: %s", kode, e)
            ringkasan[kode] = f"galat: {e}"
    return ringkasan
