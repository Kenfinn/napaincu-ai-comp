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
    debt = bs["current_portion_lt_debt"] + bs["long_term_debt"]
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

    with open(args.input, encoding="utf-8") as f:
        d = json.load(f)

    a = d["assumptions"]
    basis = args.fcff_basis or a.get("fcff_basis", "latest")

    # --- input -------------------------------------------------------------
    mcap = market_cap(d["market"]["price_per_share"],
                      d["market"]["shares_issued_thousands"])
    debt, cash, nd = net_debt(d["balance_sheet"], a.get("include_leases_in_debt", False))
    ev = enterprise_value(mcap, debt, cash)
    t = effective_tax_rate(d["tax"])

    series = fcff_series(d["cash_flow"], t)
    latest_year = max(series)
    fcff0 = series[latest_year] if basis == "latest" else sum(series.values()) / len(series)

    w = d["wacc_inputs"]
    re = w["risk_free_rate"] + w["beta"] * w["equity_risk_premium"]
    rd = w["total_interest_expense"] / debt
    wacc_val = wacc(mcap, debt, re, rd, t)

    print(f"\n{d['name']} ({d['code']}) · per {d['as_of']} · {d['unit']}")
    print("=" * 70)

    print("\nJEMBATAN NILAI PERUSAHAAN")
    print(f"  Kapitalisasi pasar     {fmt_t(mcap):>14}   "
          f"({d['market']['shares_issued_thousands']:,} rb lembar × {d['market']['price_per_share']:,})")
    print(f"  + Utang berbunga       {fmt_t(debt):>14}   "
          f"{'termasuk' if a.get('include_leases_in_debt') else 'tanpa'} lease")
    print(f"  − Kas & investasi jk pendek {fmt_t(cash):>9}")
    print(f"  = Nilai perusahaan     {fmt_t(ev):>14}")

    print("\nARUS KAS BEBAS (FCFF)")
    print(f"  Tarif pajak efektif    {t * 100:13.2f}%   "
          f"({d['tax']['income_tax_expense']:,.0f} / {d['tax']['pretax_income']:,.0f})")
    for y, v in series.items():
        mark = "  ← dipakai" if (basis == "latest" and y == latest_year) else ""
        print(f"  FCFF {y}              {v / 1000:13,.1f} bio{mark}")
    avg = sum(series.values()) / len(series)
    print(f"  Rata-rata {len(series)} tahun      {avg / 1000:13,.1f} bio"
          + ("  ← dipakai" if basis == "average" else ""))
    print(f"  Dasar perhitungan      {basis:>14}")

    print("\nBIAYA MODAL (WACC)")
    print(f"  Biaya ekuitas          {re * 100:13.2f}%   "
          f"= {w['risk_free_rate'] * 100:.2f}% + {w['beta']} × {w['equity_risk_premium'] * 100:.2f}%")
    print(f"  Biaya utang            {rd * 100:13.2f}%   "
          f"= {w['total_interest_expense']:,.0f} / {debt:,.0f}")
    print(f"  Bobot ekuitas          {mcap / (mcap + debt) * 100:13.2f}%")
    print(f"  WACC                   {wacc_val * 100:13.2f}%")

    # --- reverse -----------------------------------------------------------
    g = implied_growth(ev, fcff0, wacc_val)
    ceiling = a.get("terminal_growth_ceiling")

    print("\nREVERSE DCF — pertumbuhan yang diasumsikan pasar")
    print(f"  g tersirat             {g * 100:13.2f}%")

    back = ev_from_growth(fcff0, g, wacc_val)
    print(f"\n  Pemeriksaan sirkularitas:")
    print(f"    g dimasukkan kembali → EV {fmt_t(back)}, masukan {fmt_t(ev)}"
          f"  (selisih {abs(back - ev) / ev * 100:.4f}%)")
    print(f"    Harga per lembar hasilnya {equity_per_share(back, debt, cash, d['market']['shares_issued_thousands']):,.0f}"
          f" NTD, harga pasar {d['market']['price_per_share']:,} NTD")
    print(f"    Sama persis — itu identitas, bukan valuasi. Reverse DCF tidak bisa")
    print(f"    dipakai untuk menilai murah atau mahal.")

    if ceiling:
        print(f"\n  UJI KEWAJARAN")
        print(f"    Batas pertumbuhan abadi {ceiling * 100:11.2f}%   (PDB nominal jangka panjang)")
        if g > ceiling:
            print(f"    g tersirat {g * 100:.2f}% MELAMPAUI batas {ceiling * 100:.2f}%.")
            print(f"    Pasar memberi harga untuk pertumbuhan yang tidak bisa")
            print(f"    dipertahankan selamanya → indikasi OVERVALUED.")
        else:
            print(f"    g tersirat {g * 100:.2f}% masih di bawah batas {ceiling * 100:.2f}%.")
            print(f"    Asumsi pasar tidak melanggar batas perpetuitas.")

    # --- forward -----------------------------------------------------------
    if args.forward_g is not None:
        gf = args.forward_g
        evf = ev_from_growth(fcff0, gf, wacc_val)
        print(f"\nFORWARD DCF — dengan asumsi g = {gf * 100:.2f}%")
        if evf is None:
            print(f"  g >= WACC ({wacc_val * 100:.2f}%), rumus perpetuitas tidak berlaku.")
        else:
            px = equity_per_share(evf, debt, cash, d["market"]["shares_issued_thousands"])
            mkt = d["market"]["price_per_share"]
            gap = (px - mkt) / mkt * 100
            print(f"  Nilai perusahaan       {fmt_t(evf):>14}")
            print(f"  Nilai wajar per lembar {px:13,.0f} NTD")
            print(f"  Harga pasar            {mkt:13,.0f} NTD")
            print(f"  Selisih                {gap:12.1f}%   "
                  f"→ {'OVERVALUED' if gap < 0 else 'UNDERVALUED'}")

    # --- sensitivitas ------------------------------------------------------
    print("\nSENSITIVITAS — nilai wajar per lembar (NTD)")
    gs = [g - 0.01, g - 0.005, g, g + 0.005, g + 0.01] if not args.forward_g else \
         [args.forward_g - 0.01, args.forward_g - 0.005, args.forward_g,
          args.forward_g + 0.005, args.forward_g + 0.01]
    ws = [wacc_val - 0.01, wacc_val - 0.005, wacc_val, wacc_val + 0.005, wacc_val + 0.01]

    print("           " + "".join(f"{'g=' + format(x * 100, '.2f') + '%':>9}" for x in gs))
    for wv in ws:
        row = f"  WACC {wv * 100:5.2f}%"
        for gv in gs:
            e = ev_from_growth(fcff0, gv, wv)
            row += ("      —  " if e is None else
                    f"{equity_per_share(e, debt, cash, d['market']['shares_issued_thousands']):9,.0f}")
        print(row)

    print("\nASUMSI YANG DIPAKAI")
    for k, v in a.items():
        print(f"  {k:28} {v}")

    print("\nSUMBER")
    missing = []
    for k, v in d.get("sources", {}).items():
        flag = " ⚠" if ("GANTI" in v or "BELUM ADA" in v or "PERKIRAAN" in v) else ""
        if flag:
            missing.append(k)
        print(f"  {k:28} {v}{flag}")

    if missing:
        print(f"\n⚠ {len(missing)} sumber belum lengkap: {', '.join(missing)}")
        print("  Angka boleh dihitung, tapi belum boleh masuk deck sebelum tiap")
        print("  input punya URL yang bisa dibuka juri.")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
