"""Data pasar & laporan keuangan per saham — untuk halaman saham (Stream, Key Stats, Financials).

Sumber, semuanya bisa dijangkau dari luar Taiwan (diuji 8–9 Nov 2026):

    Harga harian      TWSE  /exchangeReport/STOCK_DAY_ALL      TPEx /tpex_mainboard_quotes
    PER, PBR, yield   TWSE  /exchangeReport/BWIBBU_ALL         TPEx /tpex_mainboard_peratio_analysis
    Profil emiten     TWSE  /opendata/t187ap03_L               TPEx /mopsfin_t187ap03_O
    Laporan keuangan  FinMind (agregator data MOPS): laba rugi, neraca, arus kas per kuartal

Tiga sifat data FinMind yang menentukan cara tabel disusun:

    Laba rugi   nilai per KUARTAL tunggal            → tahunan = jumlah 4 kuartal
    Arus kas    KUMULATIF sejak awal tahun           → kuartal = selisih dengan kuartal sebelumnya
    Neraca      posisi pada tanggal laporan          → tahunan = posisi akhir tahun

Semua respons di-cache di DATA_DIR/pasar supaya kuota FinMind (300/jam tanpa token)
tidak habis, dan halaman tetap tampil dari cache saat sumber sedang tidak bisa dijangkau.
Data pribadi di profil (juru bicara, akuntan, direksi) dibuang sebelum disimpan.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime

from . import config
from .tarik import Diblokir, _ambil_json

CACHE_DIR = os.path.join(config.DATA_DIR, "pasar")
FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"
FINMIND_TOKEN = os.environ.get("FINMIND_TOKEN", "")
UA = "FEAF-InvestmentAssistant/0.3"

SUMBER_PASAR = {
    "harga_twse": "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
    "harga_tpex": "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes",
    "rasio_twse": "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL",
    "rasio_tpex": "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis",
    "profil_twse": "https://openapi.twse.com.tw/v1/opendata/t187ap03_L",
    "profil_tpex": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O",
}
TTL = {"harga": 1800, "rasio": 1800, "profil": 86400, "keuangan": 43200}

LAPORAN = {
    "lr": "TaiwanStockFinancialStatements",
    "neraca": "TaiwanStockBalanceSheet",
    "arus": "TaiwanStockCashFlowsStatement",
}

# Baris yang ditampilkan, berurutan. (kunci FinMind, tebal?)
BARIS = {
    "lr": [("Revenue", True), ("CostOfGoodsSold", False), ("GrossProfit", True),
           ("OperatingExpenses", False), ("OperatingIncome", True),
           ("TotalNonoperatingIncomeAndExpense", False), ("PreTaxIncome", True), ("TAX", False),
           ("IncomeAfterTaxes", True), ("EquityAttributableToOwnersOfParent", False),
           ("OtherComprehensiveIncome", False), ("TotalConsolidatedProfitForThePeriod", True),
           ("EPS", True)],
    "neraca": [("CashAndCashEquivalents", False), ("AccountsReceivableNet", False),
               ("Inventories", False), ("CurrentAssets", True), ("PropertyPlantAndEquipment", False),
               ("NoncurrentAssets", True), ("TotalAssets", True), ("AccountsPayable", False),
               ("CurrentLiabilities", True), ("BondsPayable", False), ("LongtermBorrowings", False),
               ("NoncurrentLiabilities", True), ("Liabilities", True), ("CapitalStock", False),
               ("RetainedEarnings", False), ("EquityAttributableToOwnersOfParent", False),
               ("Equity", True)],
    "arus": [("NetIncomeBeforeTax", False), ("Depreciation", False), ("AmortizationExpense", False),
             ("CashFlowsFromOperatingActivities", True), ("PropertyAndPlantAndEquipment", False),
             ("CashProvidedByInvestingActivities", True), ("CashFlowsProvidedFromFinancingActivities", True),
             ("FreeCashFlow", True), ("CashBalancesIncrease", False), ("CashBalancesEndOfPeriod", False)],
}
# Pos yang bukan dalam NTD (tidak dibagi sejuta saat ditampilkan).
BUKAN_UANG = {"EPS"}

# Kode industri TWSE (產業別) → nama. Dipakai juga untuk menandai sektor keuangan,
# tempat DCF berbasis arus kas bebas tidak berlaku.
INDUSTRI = {
    "01": "水泥工業", "02": "食品工業", "03": "塑膠工業", "04": "紡織纖維", "05": "電機機械",
    "06": "電器電纜", "08": "玻璃陶瓷", "09": "造紙工業", "10": "鋼鐵工業", "11": "橡膠工業",
    "12": "汽車工業", "14": "建材營造", "15": "航運業", "16": "觀光餐旅", "17": "金融保險",
    "18": "貿易百貨", "20": "其他", "21": "化學工業", "22": "生技醫療", "23": "油電燃氣",
    "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業", "27": "通信網路業",
    "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業", "31": "其他電子業",
}
INDUSTRI_KEUANGAN = {"17"}

# Kolom profil yang TIDAK disimpan: nama orang dan kontak pribadi.
PROFIL_DIBUANG = ("董事長", "總經理", "發言人", "發言人職稱", "代理發言人", "簽證會計師1",
                  "簽證會計師2", "電子郵件信箱", "ChairmanOfTheBoard", "GeneralManager",
                  "Spokesman", "SpokesmanTitle", "DeputySpokesman")


# --------------------------------------------------------------------------- cache

def _path(nama: str) -> str:
    return os.path.join(CACHE_DIR, f"{nama}.json")


def _baca_cache(nama: str) -> tuple[object | None, float | None]:
    p = _path(nama)
    if not os.path.exists(p):
        return None, None
    with open(p, encoding="utf-8") as f:
        isi = json.load(f)
    return isi.get("data"), isi.get("waktu")


def _tulis_cache(nama: str, data) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = _path(nama) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"waktu": time.time(), "data": data}, f, ensure_ascii=False)
    os.replace(tmp, _path(nama))


def _dengan_cache(nama: str, ttl: int, ambil):
    """Kembalikan (data, info). Cache segar dipakai; kalau sumber gagal, cache lama tetap dipakai."""
    data, waktu = _baca_cache(nama)
    if data is not None and waktu and time.time() - waktu < ttl:
        return data, {"dari_cache": True, "waktu": waktu, "galat": None}
    try:
        baru = ambil()
        _tulis_cache(nama, baru)
        return baru, {"dari_cache": False, "waktu": time.time(), "galat": None}
    except Exception as e:                            # noqa: BLE001 — dicatat ke layar
        galat = "diblokir" if isinstance(e, Diblokir) else f"{type(e).__name__}: {e}"
        tgl = datetime.fromtimestamp(waktu).strftime("%Y-%m-%d %H:%M") if waktu else None
        return data, {"dari_cache": data is not None, "waktu": waktu, "tgl": tgl, "galat": galat}


# --------------------------------------------------------------------------- ambil

def _daftar(nama: str, ttl_jenis: str) -> list[dict]:
    data, _ = _dengan_cache(nama, TTL[ttl_jenis], lambda: _ambil_json(SUMBER_PASAR[nama]))
    return data or []


def _f(x) -> float | None:
    try:
        return float(str(x).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _roc(s: str) -> str | None:
    s = "".join(c for c in str(s or "") if c.isdigit())
    if len(s) not in (6, 7):
        return None
    return f"{int(s[:-4]) + 1911:04d}-{s[-4:-2]}-{s[-2:]}"


def harga(kode: str) -> dict | None:
    for r in _daftar("harga_twse", "harga"):
        if r.get("Code") == kode:
            tutup, ubah = _f(r.get("ClosingPrice")), _f(r.get("Change"))
            return _harga(kode, r.get("Name"), "TWSE", _roc(r.get("Date")), tutup, ubah,
                          _f(r.get("OpeningPrice")), _f(r.get("HighestPrice")),
                          _f(r.get("LowestPrice")), _f(r.get("TradeVolume")))
    for r in _daftar("harga_tpex", "harga"):
        if r.get("SecuritiesCompanyCode") == kode:
            return _harga(kode, r.get("CompanyName"), "TPEx", _roc(r.get("Date")), _f(r.get("Close")),
                          _f(r.get("Change")), _f(r.get("Open")), _f(r.get("High")),
                          _f(r.get("Low")), _f(r.get("TradingShares")))
    return None


def _harga(kode, nama, bursa, tgl, tutup, ubah, buka, tinggi, rendah, vol) -> dict:
    sebelum = (tutup - ubah) if (tutup is not None and ubah is not None) else None
    return {"kode": kode, "nama": nama, "bursa": bursa, "tanggal": tgl, "tutup": tutup,
            "ubah": ubah, "ubah_pct": (ubah / sebelum) if sebelum else None,
            "buka": buka, "tinggi": tinggi, "rendah": rendah, "volume": vol}


def rasio(kode: str) -> dict | None:
    for r in _daftar("rasio_twse", "rasio"):
        if r.get("Code") == kode:
            return {"per": _f(r.get("PEratio")), "pbr": _f(r.get("PBratio")),
                    "yield": _f(r.get("DividendYield")), "tanggal": _roc(r.get("Date"))}
    for r in _daftar("rasio_tpex", "rasio"):
        if r.get("SecuritiesCompanyCode") == kode:
            return {"per": _f(r.get("PriceEarningRatio")), "pbr": _f(r.get("PriceBookRatio")),
                    "yield": _f(r.get("YieldRatio")), "tanggal": _roc(r.get("Date"))}
    return None


def _bersihkan_profil(rows: list[dict]) -> list[dict]:
    return [{k: v for k, v in r.items() if k.strip() not in PROFIL_DIBUANG} for r in rows]


def daftar_profil(nama: str = "profil_twse") -> list[dict]:
    data, _ = _dengan_cache(nama, TTL["profil"],
                            lambda: _bersihkan_profil(_ambil_json(SUMBER_PASAR[nama])))
    return data or []


def per_industri(kode: str) -> dict | None:
    """Median PER emiten satu industri di TWSE — pembanding yang bersumber dari bursa sendiri.

    Hanya PER positif yang dihitung (PER negatif/kosong berarti rugi atau tidak tersedia).
    """
    ind = {str(r.get("公司代號", "")).strip(): str(r.get("產業別", "")).strip()
           for r in daftar_profil("profil_twse")}
    sendiri = ind.get(kode)
    if not sendiri:
        return None
    nilai = []
    for r in _daftar("rasio_twse", "rasio"):
        k = str(r.get("Code", "")).strip()
        v = _f(r.get("PEratio"))
        if ind.get(k) == sendiri and v and v > 0:
            nilai.append(v)
    if len(nilai) < 5:
        return None
    nilai.sort()
    n = len(nilai)
    median = nilai[n // 2] if n % 2 else (nilai[n // 2 - 1] + nilai[n // 2]) / 2
    return {"industri_kode": sendiri, "industri": INDUSTRI.get(sendiri, sendiri),
            "median": median, "jumlah": n}


def profil(kode: str) -> dict | None:
    for nama in ("profil_twse", "profil_tpex"):
        data, _ = _dengan_cache(nama, TTL["profil"],
                                lambda n=nama: _bersihkan_profil(_ambil_json(SUMBER_PASAR[n])))
        for r in data or []:
            if str(r.get("公司代號") or r.get("SecuritiesCompanyCode") or "").strip() == kode:
                ind = str(r.get("產業別") or r.get("SecuritiesIndustryCode") or "").strip()
                return {
                    "nama_lengkap": r.get("公司名稱") or r.get("CompanyName"),
                    "nama": r.get("公司簡稱") or r.get("CompanyAbbreviation"),
                    "nama_en": r.get("英文簡稱") or r.get("SymbolEnglish"),
                    "industri_kode": ind,
                    "industri": INDUSTRI.get(ind, ind or None),
                    "keuangan": ind in INDUSTRI_KEUANGAN,
                    "berdiri": _tgl8(r.get("成立日期") or r.get("DateOfIncorporation")),
                    "tercatat": _tgl8(r.get("上市日期") or r.get("DateOfListing")),
                    "modal": _f(r.get("實收資本額") or r.get("Paidin.Capital.NTDollars")),
                    "alamat": r.get("住址") or r.get("Address"),
                    "situs": r.get("網址") or r.get("WebAddress"),
                    "bursa": "TWSE" if nama == "profil_twse" else "TPEx",
                }
    return None


def _tgl8(s) -> str | None:
    s = "".join(c for c in str(s or "") if c.isdigit())
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 else None


def _finmind(dataset: str, kode: str, mulai: str) -> list[dict]:
    q = urllib.parse.urlencode({"dataset": dataset, "data_id": kode, "start_date": mulai})
    h = {"User-Agent": UA, "Accept": "application/json"}
    if FINMIND_TOKEN:
        h["Authorization"] = f"Bearer {FINMIND_TOKEN}"
    req = urllib.request.Request(f"{FINMIND_URL}?{q}", headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        isi = json.loads(r.read().decode("utf-8"))
    if isi.get("status") != 200:
        raise RuntimeError(f"FinMind {isi.get('status')}: {isi.get('msg')}")
    return isi.get("data") or []


def keuangan_mentah(kode: str, lap: str) -> tuple[list[dict], dict]:
    mulai = f"{datetime.now().year - 6}-01-01"
    return _dengan_cache(f"finmind_{lap}_{kode}", TTL["keuangan"],
                         lambda: _finmind(LAPORAN[lap], kode, mulai))


# --------------------------------------------------------------------------- tabel

def _seri(rows: list[dict]) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """{kunci: {tanggal: nilai}}, {kunci: nama asli 中文}. Baris *_per (persen dari total) diabaikan."""
    seri: dict[str, dict[str, float]] = {}
    nama: dict[str, str] = {}
    for r in rows:
        k = r.get("type")
        if not k or k.endswith("_per") or r.get("value") is None:
            continue
        seri.setdefault(k, {})[r["date"]] = float(r["value"])
        nama.setdefault(k, r.get("origin_name") or k)
    return seri, nama


def _arus_per_kuartal(seri: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """Arus kas MOPS kumulatif sejak awal tahun → nilai per kuartal tunggal.

    Saldo (awal/akhir periode) bukan arus, jadi tidak diselisihkan.
    """
    saldo = {"CashBalancesBeginningOfPeriod", "CashBalancesEndOfPeriod"}
    hasil = {}
    for k, per_tgl in seri.items():
        if k in saldo:
            hasil[k] = dict(per_tgl)
            continue
        out = {}
        for tgl, v in per_tgl.items():
            th, bl = tgl[:4], tgl[5:7]
            sebelumnya = {"06": "03-31", "09": "06-30", "12": "09-30"}.get(bl)
            if sebelumnya is None:                        # Q1 = kumulatif itu sendiri
                out[tgl] = v
            elif f"{th}-{sebelumnya}" in per_tgl:
                out[tgl] = v - per_tgl[f"{th}-{sebelumnya}"]
        hasil[k] = out
    return hasil


def _tambah_fcf(seri: dict[str, dict[str, float]]) -> None:
    """Arus kas bebas = arus kas operasi + belanja aset tetap (yang tercatat negatif)."""
    cfo = seri.get("CashFlowsFromOperatingActivities", {})
    capex = seri.get("PropertyAndPlantAndEquipment", {})
    seri["FreeCashFlow"] = {t: cfo[t] + capex[t] for t in cfo if t in capex}


def _label_periode(tgl: str, tahunan: bool) -> str:
    th, bl = tgl[:4], tgl[5:7]
    return th if tahunan else f"Q{int(bl) // 3} {th}"


def tabel(kode: str, lap: str, periode: str = "q", mode: str = "nilai", maks: int | None = None) -> dict:
    """Susun tabel Financials. periode: q (kuartal) | y (tahun). mode: nilai | yoy."""
    rows, info = keuangan_mentah(kode, lap)
    seri, nama = _seri(rows or [])
    if lap == "arus":
        seri_kuartal = _arus_per_kuartal(seri)
    else:
        seri_kuartal = seri

    tahunan = periode == "y"
    if tahunan:
        if lap == "lr":
            # Tahunan = jumlah 4 kuartal. EPS juga dijumlah (EPS kuartalan bersifat aditif
            # dalam satu tahun buku karena basis saham hampir sama; ditandai sebagai aproksimasi).
            seri_tampil: dict[str, dict[str, float]] = {}
            for k, per in seri.items():
                per_th: dict[str, list[float]] = {}
                for tgl, v in per.items():
                    per_th.setdefault(tgl[:4], []).append(v)
                seri_tampil[k] = {f"{th}-12-31": sum(vs) for th, vs in per_th.items() if len(vs) == 4}
        else:
            # Neraca: posisi akhir tahun. Arus kas: kumulatif Q4 = setahun penuh.
            seri_tampil = {k: {t: v for t, v in per.items() if t[5:] == "12-31"} for k, per in seri.items()}
    else:
        seri_tampil = seri_kuartal

    if lap == "arus":
        _tambah_fcf(seri_tampil)
        nama["FreeCashFlow"] = "自由現金流量（營業活動現金流量 − 取得不動產、廠房及設備）"

    semua_tgl = sorted({t for per in seri_tampil.values() for t in per}, reverse=True)
    maks = maks or (6 if tahunan else 12)
    kolom = semua_tgl[:maks]

    def lalu(tgl: str) -> str:
        return f"{int(tgl[:4]) - 1}{tgl[4:]}"

    baris = []
    for k, tebal in BARIS[lap]:
        per = seri_tampil.get(k)
        if not per:
            continue
        sel = []
        for t in kolom:
            v = per.get(t)
            if mode == "yoy":
                p = per.get(lalu(t))
                sel.append(None if v is None or not p else (v - p) / abs(p))
            else:
                sel.append(None if v is None else (v if k in BUKAN_UANG else v / 1e6))
        baris.append({"kunci": k, "nama_zh": nama.get(k, k), "tebal": tebal,
                      "uang": k not in BUKAN_UANG, "sel": sel, "turunan": k == "FreeCashFlow"})

    # Kolom tanpa satu angka pun (mis. YoY tahun pertama, tanpa pembanding) tidak ditampilkan.
    isi = [i for i in range(len(kolom)) if any(b["sel"][i] is not None for b in baris)]
    kolom = [kolom[i] for i in isi]
    for b in baris:
        b["sel"] = [b["sel"][i] for i in isi]

    return {
        "kolom": [{"tgl": t, "label": _label_periode(t, tahunan)} for t in kolom],
        "baris": baris,
        "lap": lap, "periode": periode, "mode": mode,
        "info": info,
        "ada": bool(baris),
    }


def statistik(kode: str) -> dict:
    """Key Stats: harga & rasio bursa, plus angka TTM dari laporan keuangan."""
    h, r = harga(kode), rasio(kode)
    lr_rows, info_lr = keuangan_mentah(kode, "lr")
    nr_rows, _ = keuangan_mentah(kode, "neraca")
    lr, _n = _seri(lr_rows or [])
    nr, _n2 = _seri(nr_rows or [])

    def ttm(k):
        per = lr.get(k, {})
        tgl = sorted(per, reverse=True)[:4]
        return sum(per[t] for t in tgl) if len(tgl) == 4 else None, (tgl[0] if tgl else None)

    pend, akhir = ttm("Revenue")
    laba_kotor, _ = ttm("GrossProfit")
    laba_usaha, _ = ttm("OperatingIncome")
    laba_bersih, _ = ttm("EquityAttributableToOwnersOfParent")
    eps, _ = ttm("EPS")
    ekuitas_per = nr.get("EquityAttributableToOwnersOfParent") or nr.get("Equity") or {}
    ekuitas = ekuitas_per.get(max(ekuitas_per)) if ekuitas_per else None
    saham_per = nr.get("OrdinaryShare") or nr.get("CapitalStock") or {}
    # Nominal saham biasa di Taiwan NT$10 per lembar.
    lembar = (saham_per[max(saham_per)] / 10) if saham_per else None

    def bagi(a, b):
        return a / b if a is not None and b else None

    return {
        "harga": h, "rasio": r,
        "ttm_sampai": akhir,
        "pendapatan_ttm": pend, "laba_bersih_ttm": laba_bersih, "eps_ttm": eps,
        "margin_kotor": bagi(laba_kotor, pend), "margin_usaha": bagi(laba_usaha, pend),
        "margin_bersih": bagi(laba_bersih, pend),
        "roe": bagi(laba_bersih, ekuitas),
        "lembar": lembar,
        "kapitalisasi": (h["tutup"] * lembar) if (h and h.get("tutup") and lembar) else None,
        "info_keuangan": info_lr,
    }
