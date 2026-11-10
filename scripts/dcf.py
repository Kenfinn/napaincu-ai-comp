#!/usr/bin/env python3
"""
Kalkulator DCF deterministik — reverse dan forward.

Bukan keluaran AI. Semua angka di sini hasil aritmetika dari input yang bersumber,
supaya tiap angka bisa ditelusuri juri sampai ke baris laporan keuangannya.

TEMUAN PENTING TENTANG REVERSE DCF

Reverse DCF TIDAK menghasilkan nilai intrinsik. Kalau g dicari dari EV pasar, lalu g
itu dimasukkan kembali ke rumus yang sama, hasilnya pasti EV pasar lagi — itu identitas
matematis, bukan valuasi. Skrip ini membuktikannya sendiri di bagian pemeriksaan.

Yang sebenarnya dihasilkan reverse DCF adalah **pertumbuhan abadi yang sedang
diasumsikan pasar**. Penilaian datang dari langkah berikutnya: masuk akal tidak angka
itu? Pertumbuhan abadi tidak boleh melebihi pertumbuhan PDB nominal jangka panjang —
kalau sebuah perusahaan tumbuh lebih cepat dari ekonominya selamanya, lama-lama dia
menjadi ekonominya.

Pakai:
    python3 scripts/dcf.py valuation/inputs/2330.json
    python3 scripts/dcf.py valuation/inputs/2330.json --fcff-basis average
    python3 scripts/dcf.py valuation/inputs/2330.json --forward-g 0.03

Tanpa dependensi eksternal.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

MILLION = 1.0                       # semua internal dalam juta NTD


# --------------------------------------------------------------------------
# Blok perhitungan — masing-masing kecil dan bisa diuji sendiri
# --------------------------------------------------------------------------

def market_cap(price: float, shares_thousands: float) -> float:
    """Kapitalisasi pasar dalam juta."""
    return price * shares_thousands * 1_000 / 1e6


def net_debt(bs: dict, include_leases: bool) -> tuple[float, float, float]:
    """Mengembalikan (utang, kas, utang bersih). Kas mencakup investasi jangka pendek."""
    debt = bs["current_portion_lt_debt"] + bs["long_term_debt"] + bs.get("short_term_borrowings", 0.0)
    if include_leases:
        debt += bs.get("current_portion_leases", 0.0)
    cash = bs["cash_and_equivalents"] + bs["short_term_investments"]
    return debt, cash, debt - cash


def enterprise_value(mcap: float, debt: float, cash: float) -> float:
    """EV = kapitalisasi pasar + utang − kas.

    Kas DAN investasi jangka pendek sama-sama dikurangkan. Menuliskan
    (kas − investasi jangka pendek) adalah kesalahan tanda yang mudah terlewat.
    """
    return mcap + debt - cash


def effective_tax_rate(tax: dict) -> float:
    return tax["income_tax_expense"] / tax["pretax_income"]


def fcff(cfo: float, capex: float, interest: float, tax_rate: float) -> float:
    """FCFF = CFO − CapEx + bunga × (1 − pajak).

    CapEx dimasukkan sebagai nilai positif; tandanya diurus di sini supaya
    konvensi tanda di laporan arus kas tidak menyelinap masuk.
    """
    return cfo - abs(capex) + interest * (1 - tax_rate)


def fcff_series(cf: dict, tax_rate: float) -> dict[str, float]:
    years = sorted(cf["cfo_by_year"])
    return {
        y: fcff(cf["cfo_by_year"][y], cf["capex_by_year"][y],
                cf["interest_expense_by_year"][y], tax_rate)
        for y in years
    }


def wacc(mcap: float, debt: float, re: float, rd: float, tax_rate: float) -> float:
    total = mcap + debt
    return mcap / total * re + debt / total * rd * (1 - tax_rate)


def implied_growth(ev: float, fcff0: float, w: float) -> float:
    """Balik rumus EV = FCFF0(1+g)/(WACC−g) untuk mencari g."""
    return (ev * w - fcff0) / (ev + fcff0)


def ev_from_growth(fcff0: float, g: float, w: float) -> float | None:
    """EV = FCFF0(1+g)/(WACC−g). None kalau g >= WACC (rumus tidak berlaku)."""
    return None if g >= w else fcff0 * (1 + g) / (w - g)


def equity_per_share(ev: float, debt: float, cash: float, shares_thousands: float) -> float:
    """Jembatan EV → ekuitas → per lembar.

    Membagi EV langsung dengan jumlah lembar adalah kesalahan: EV memuat utang
    dan sudah mengeluarkan kas, jadi itu bukan milik pemegang saham.
    """
    equity = ev - debt + cash
    return equity * 1e6 / (shares_thousands * 1_000)


# --------------------------------------------------------------------------
# Perhitungan sebagai data
# --------------------------------------------------------------------------

def compute(d: dict, basis: str | None = None,
            forward_g: float | None = None) -> dict:
    """Seluruh perhitungan untuk satu emiten, dikembalikan sebagai dict.

    Dipisahkan dari pencetakan supaya aplikasi web dan CLI memakai aritmetika
    yang sama persis. Kalau masing-masing menghitung sendiri, angka di layar
    dan angka di kertas kerja akan berbeda diam-diam — dan itu jenis kesalahan
    yang baru ketahuan waktu juri mencocokkan.
    """
    a = d["assumptions"]
    basis = basis or a.get("fcff_basis", "latest")

    mcap = market_cap(d["market"]["price_per_share"],
                      d["market"]["shares_issued_thousands"])
    debt, cash, nd = net_debt(d["balance_sheet"], a.get("include_leases_in_debt", False))
    ev = enterprise_value(mcap, debt, cash)
    t = effective_tax_rate(d["tax"])

    series = fcff_series(d["cash_flow"], t)
    latest_year = max(series)
    avg = sum(series.values()) / len(series)
    fcff0 = series[latest_year] if basis == "latest" else avg

    w = d["wacc_inputs"]
    re_ = w["risk_free_rate"] + w["beta"] * w["equity_risk_premium"]
    rd = w["total_interest_expense"] / debt
    wacc_val = wacc(mcap, debt, re_, rd, t)

    shares = d["market"]["shares_issued_thousands"]
    price = d["market"]["price_per_share"]
    g = implied_growth(ev, fcff0, wacc_val)
    ceiling = a.get("terminal_growth_ceiling")

    r: dict = {
        "code": d["code"], "name": d["name"], "as_of": d["as_of"], "unit": d["unit"],
        "basis": basis, "latest_year": latest_year,
        "market_cap": mcap, "debt": debt, "cash": cash, "net_debt": nd, "ev": ev,
        "tax_rate": t, "fcff_series": series, "fcff_average": avg, "fcff0": fcff0,
        "cost_of_equity": re_, "cost_of_debt": rd,
        "equity_weight": mcap / (mcap + debt), "wacc": wacc_val,
        "implied_growth": g, "terminal_growth_ceiling": ceiling,
        "price_per_share": price, "shares_issued_thousands": shares,
        "assumptions": a, "sources": d.get("sources", {}),
        "wacc_inputs": w, "tax_detail": d["tax"],
    }

    # g hasil reverse dimasukkan kembali wajib mengembalikan EV yang sama.
    # Selisih yang tidak nol berarti ada bug di aritmetikanya, bukan temuan pasar.
    back = ev_from_growth(fcff0, g, wacc_val)
    r["circularity"] = {
        "ev_back": back,
        "drift_pct": abs(back - ev) / ev * 100,
        "price_back": equity_per_share(back, debt, cash, shares),
    }

    r["exceeds_ceiling"] = bool(ceiling is not None and g > ceiling)

    if forward_g is not None:
        evf = ev_from_growth(fcff0, forward_g, wacc_val)
        fair = equity_per_share(evf, debt, cash, shares) if evf is not None else None
        r["forward"] = {
            "g": forward_g,
            "ev": evf,
            "fair_value": fair,
            "gap_pct": None if fair is None else (fair - price) / price * 100,
        }

    centre = forward_g if forward_g is not None else g
    gs = [centre - 0.01, centre - 0.005, centre, centre + 0.005, centre + 0.01]
    ws = [wacc_val - 0.01, wacc_val - 0.005, wacc_val, wacc_val + 0.005, wacc_val + 0.01]
    grid = []
    for wv in ws:
        row = []
        for gv in gs:
            e = ev_from_growth(fcff0, gv, wv)
            row.append(None if e is None else equity_per_share(e, debt, cash, shares))
        grid.append(row)
    r["sensitivity"] = {"g_axis": gs, "wacc_axis": ws, "grid": grid}

    # Sumber yang masih bertanda placeholder. Angka boleh dihitung, tapi belum
    # boleh masuk deck sebelum tiap input punya URL yang bisa dibuka juri.
    r["incomplete_sources"] = [
        k for k, v in d.get("sources", {}).items()
        if "GANTI" in v or "BELUM ADA" in v or "PERKIRAAN" in v
    ]
    return r


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------

def fmt_t(x: float) -> str:
    return f"{x / 1e6:,.3f} T"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="berkas JSON input, mis. valuation/inputs/2330.json")
    ap.add_argument("--fcff-basis", choices=["latest", "average"],
                    help="pakai FCFF tahun terakhir atau rata-rata (menimpa berkas input)")
    ap.add_argument("--forward-g", type=float,
                    help="hitung maju dengan g ini, mis. 0.03")
    args = ap.parse_args()

    d = load(args.input)
    r = compute(d, basis=args.fcff_basis, forward_g=args.forward_g)

    mcap, debt, cash, ev = r["market_cap"], r["debt"], r["cash"], r["ev"]
    t, wacc_val, g = r["tax_rate"], r["wacc"], r["implied_growth"]
    series, basis = r["fcff_series"], r["basis"]
    a, w = r["assumptions"], r["wacc_inputs"]
    shares = r["shares_issued_thousands"]

    print(f"\n{r['name']} ({r['code']}) · per {r['as_of']} · {r['unit']}")
    print("=" * 70)

    print("\nJEMBATAN NILAI PERUSAHAAN")
    print(f"  Kapitalisasi pasar     {fmt_t(mcap):>14}   "
          f"({shares:,} rb lembar × {r['price_per_share']:,})")
    print(f"  + Utang berbunga       {fmt_t(debt):>14}   "
          f"{'termasuk' if a.get('include_leases_in_debt') else 'tanpa'} lease")
    print(f"  − Kas & investasi jk pendek {fmt_t(cash):>9}")
    print(f"  = Nilai perusahaan     {fmt_t(ev):>14}")

    print("\nARUS KAS BEBAS (FCFF)")
    print(f"  Tarif pajak efektif    {t * 100:13.2f}%   "
          f"({r['tax_detail']['income_tax_expense']:,.0f} / {r['tax_detail']['pretax_income']:,.0f})")
    for y, v in series.items():
        mark = "  ← dipakai" if (basis == "latest" and y == r["latest_year"]) else ""
        print(f"  FCFF {y}              {v / 1000:13,.1f} bio{mark}")
    print(f"  Rata-rata {len(series)} tahun      {r['fcff_average'] / 1000:13,.1f} bio"
          + ("  ← dipakai" if basis == "average" else ""))
    print(f"  Dasar perhitungan      {basis:>14}")

    print("\nBIAYA MODAL (WACC)")
    print(f"  Biaya ekuitas          {r['cost_of_equity'] * 100:13.2f}%   "
          f"= {w['risk_free_rate'] * 100:.2f}% + {w['beta']} × {w['equity_risk_premium'] * 100:.2f}%")
    print(f"  Biaya utang            {r['cost_of_debt'] * 100:13.2f}%   "
          f"= {w['total_interest_expense']:,.0f} / {debt:,.0f}")
    print(f"  Bobot ekuitas          {r['equity_weight'] * 100:13.2f}%")
    print(f"  WACC                   {wacc_val * 100:13.2f}%")

    # --- reverse -----------------------------------------------------------
    c = r["circularity"]
    ceiling = r["terminal_growth_ceiling"]

    print("\nREVERSE DCF — pertumbuhan yang diasumsikan pasar")
    print(f"  g tersirat             {g * 100:13.2f}%")

    print(f"\n  Pemeriksaan sirkularitas:")
    print(f"    g dimasukkan kembali → EV {fmt_t(c['ev_back'])}, masukan {fmt_t(ev)}"
          f"  (selisih {c['drift_pct']:.4f}%)")
    print(f"    Harga per lembar hasilnya {c['price_back']:,.0f}"
          f" NTD, harga pasar {r['price_per_share']:,} NTD")
    print(f"    Sama persis — itu identitas, bukan valuasi. Reverse DCF tidak bisa")
    print(f"    dipakai untuk menilai murah atau mahal.")

    if ceiling:
        print(f"\n  UJI KEWAJARAN")
        print(f"    Batas pertumbuhan abadi {ceiling * 100:11.2f}%   (PDB nominal jangka panjang)")
        if r["exceeds_ceiling"]:
            print(f"    g tersirat {g * 100:.2f}% MELAMPAUI batas {ceiling * 100:.2f}%.")
            print(f"    Pasar memberi harga untuk pertumbuhan yang tidak bisa")
            print(f"    dipertahankan selamanya → indikasi OVERVALUED.")
        else:
            print(f"    g tersirat {g * 100:.2f}% masih di bawah batas {ceiling * 100:.2f}%.")
            print(f"    Asumsi pasar tidak melanggar batas perpetuitas.")

    # --- forward -----------------------------------------------------------
    if "forward" in r:
        f = r["forward"]
        print(f"\nFORWARD DCF — dengan asumsi g = {f['g'] * 100:.2f}%")
        if f["ev"] is None:
            print(f"  g >= WACC ({wacc_val * 100:.2f}%), rumus perpetuitas tidak berlaku.")
        else:
            print(f"  Nilai perusahaan       {fmt_t(f['ev']):>14}")
            print(f"  Nilai wajar per lembar {f['fair_value']:13,.0f} NTD")
            print(f"  Harga pasar            {r['price_per_share']:13,.0f} NTD")
            print(f"  Selisih                {f['gap_pct']:12.1f}%   "
                  f"→ {'OVERVALUED' if f['gap_pct'] < 0 else 'UNDERVALUED'}")

    # --- sensitivitas ------------------------------------------------------
    s = r["sensitivity"]
    print("\nSENSITIVITAS — nilai wajar per lembar (NTD)")
    print("           " + "".join(f"{'g=' + format(x * 100, '.2f') + '%':>9}" for x in s["g_axis"]))
    for wv, row in zip(s["wacc_axis"], s["grid"]):
        line = f"  WACC {wv * 100:5.2f}%"
        for cell in row:
            line += ("      —  " if cell is None else f"{cell:9,.0f}")
        print(line)

    print("\nASUMSI YANG DIPAKAI")
    for k, v in a.items():
        print(f"  {k:28} {v}")

    print("\nSUMBER")
    for k, v in r["sources"].items():
        flag = " ⚠" if k in r["incomplete_sources"] else ""
        print(f"  {k:28} {v}{flag}")

    missing = r["incomplete_sources"]
    if missing:
        print(f"\n⚠ {len(missing)} sumber belum lengkap: {', '.join(missing)}")
        print("  Angka boleh dihitung, tapi belum boleh masuk deck sebelum tiap")
        print("  input punya URL yang bisa dibuka juri.")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
