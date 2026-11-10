#!/usr/bin/env python3
"""CLI pembangun & pembanding DCF otomatis (Tugas B2).

Contoh pemakaian:
    python3 scripts/valuasi_otomatis.py 2330 --banding
    python3 scripts/valuasi_otomatis.py --acak 10 --seed 7
    python3 scripts/valuasi_otomatis.py 2330 --banding --acak 10 --seed 7 --simpan
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import config, pasar, valuasi_otomatis  # noqa: E402
from scripts import dcf  # noqa: E402


def _selisih_pct(otomatis: float | None, manual: float | None) -> str:
    if otomatis is None or manual is None:
        return "—"
    if manual == 0 and otomatis == 0:
        return "0.00%"
    if manual == 0:
        return "n/a (manual=0)"
    pct = (otomatis - manual) / abs(manual) * 100.0
    tanda = "+" if pct >= 0 else ""
    return f"{tanda}{pct:.2f}%"


def _fmt_angka(x: float | int | None, desimal: int = 1) -> str:
    if x is None:
        return "—"
    return f"{float(x):,.{desimal}f}"


def _fmt_pct(x: float | None, desimal: int = 2) -> str:
    if x is None:
        return "—"
    return f"{float(x) * 100.0:.{desimal}f}%"


def bandingkan_dengan_manual(kode: str = "2330") -> tuple[str, dict]:
    """Bandingkan hasil `valuasi_otomatis.bangun(kode)` dengan `valuation/inputs/{kode}.json`."""
    jalur_manual = Path(config.VALUATION_DIR) / f"{kode}.json"
    if not jalur_manual.exists():
        raise FileNotFoundError(f"Berkas manual tidak ditemukan: {jalur_manual}")

    manual = json.loads(jalur_manual.read_text(encoding="utf-8"))
    oto = valuasi_otomatis.bangun(kode)
    valuasi_otomatis.simpan_cache(kode, oto)

    g_m = manual.get("assumptions", {}).get("terminal_growth_ceiling")
    g_o = oto.get("assumptions", {}).get("terminal_growth_ceiling")
    r_m = dcf.compute(manual, forward_g=g_m)
    r_o = dcf.compute(oto, forward_g=g_o)

    baris_perbandingan: list[tuple[str, float | None, float | None, str, str]] = []

    def tambah(label: str, v_o: float | None, v_m: float | None, fmt: str = "num1", catatan: str = ""):
        baris_perbandingan.append((label, v_o, v_m, fmt, catatan))

    # Pasar
    tambah(
        "market.price_per_share (NTD)",
        oto["market"]["price_per_share"],
        manual["market"]["price_per_share"],
        "num2",
        f"oto {oto.get('as_of')} vs manual {manual.get('as_of')}",
    )
    tambah(
        "market.shares_issued_thousands",
        oto["market"]["shares_issued_thousands"],
        manual["market"]["shares_issued_thousands"],
        "num1",
        "TWSE OpenAPI t187ap03_L",
    )

    # Neraca
    bs_o = oto["balance_sheet"]
    bs_m = manual["balance_sheet"]
    tambah(
        f"balance_sheet.cash_and_equivalents ({bs_o['as_of']})",
        bs_o["cash_and_equivalents"],
        bs_m["cash_and_equivalents"],
        "num1",
        "CashAndCashEquivalents (identik)",
    )
    tambah(
        f"balance_sheet.short_term_investments ({bs_o['as_of']})",
        bs_o["short_term_investments"],
        bs_m["short_term_investments"],
        "num1",
        "AmortizedCost + FVOCI (identik)",
    )
    tambah(
        f"balance_sheet.short_term_borrowings ({bs_o['as_of']})",
        bs_o.get("short_term_borrowings", 0.0),
        bs_m.get("short_term_borrowings", 0.0),
        "num1",
        "ShorttermBorrowings FinMind (2330: 0)",
    )
    tambah(
        f"balance_sheet.current_portion_lt_debt ({bs_o['as_of']})",
        bs_o["current_portion_lt_debt"],
        bs_m["current_portion_lt_debt"],
        "num1",
        "FinMind gabung 一年內到期長期負債 ke OtherCurrentLiabilities",
    )
    tambah(
        f"balance_sheet.long_term_debt ({bs_o['as_of']})",
        bs_o["long_term_debt"],
        bs_m["long_term_debt"],
        "num1",
        "BondsPayable + LongtermBorrowings (identik)",
    )

    # Arus kas 3 tahun
    cf_o = oto["cash_flow"]
    cf_m = manual["cash_flow"]
    for th in sorted(set(cf_o["cfo_by_year"]) | set(cf_m["cfo_by_year"])):
        cat = "Perkiraan di berkas manual" if th in ("2023", "2024") else "Laporan tahunan penuh (31 Des)"
        tambah(
            f"cash_flow.cfo_by_year[{th}]",
            cf_o["cfo_by_year"].get(th),
            cf_m["cfo_by_year"].get(th),
            "num1",
            cat,
        )
        tambah(
            f"cash_flow.capex_by_year[{th}]",
            cf_o["capex_by_year"].get(th),
            cf_m["capex_by_year"].get(th),
            "num1",
            cat,
        )
        tambah(
            f"cash_flow.interest_expense_by_year[{th}]",
            cf_o["interest_expense_by_year"].get(th),
            cf_m["interest_expense_by_year"].get(th),
            "num1",
            cat,
        )

    # Pajak
    tambah(
        "tax.income_tax_expense",
        oto["tax"]["income_tax_expense"],
        manual["tax"]["income_tax_expense"],
        "num1",
        "Jumlah 4 kuartal TAX FinMind vs pembulatan manual",
    )
    tambah(
        "tax.pretax_income",
        oto["tax"]["pretax_income"],
        manual["tax"]["pretax_income"],
        "num1",
        "Jumlah 4 kuartal PreTaxIncome FinMind",
    )
    tambah(
        "effective_tax_rate",
        r_o["tax_rate"],
        r_m["tax_rate"],
        "pct2",
        "TAX / PreTaxIncome",
    )

    # WACC inputs & keluaran DCF
    tambah(
        "wacc_inputs.risk_free_rate",
        oto["wacc_inputs"]["risk_free_rate"],
        manual["wacc_inputs"]["risk_free_rate"],
        "pct2",
        "Obligasi pemerintah Taiwan 10Y",
    )
    tambah(
        "wacc_inputs.equity_risk_premium",
        oto["wacc_inputs"]["equity_risk_premium"],
        manual["wacc_inputs"]["equity_risk_premium"],
        "pct2",
        "Damodaran ERP Taiwan",
    )
    tambah(
        "wacc_inputs.beta",
        oto["wacc_inputs"]["beta"],
        manual["wacc_inputs"]["beta"],
        "num4",
        f"Regresi 2y mingguan bursa resmi ({oto.get('jumlah_pekan_beta')} pekan) vs manual",
    )
    tambah(
        "wacc_inputs.total_interest_expense",
        oto["wacc_inputs"]["total_interest_expense"],
        manual["wacc_inputs"]["total_interest_expense"],
        "num1",
        "InterestExpense FY terakhir",
    )
    tambah("DCF: market_cap", r_o["market_cap"], r_m["market_cap"], "num1", "Juta NTD")
    tambah("DCF: debt", r_o["debt"], r_m["debt"], "num1", "Juta NTD")
    tambah("DCF: cash", r_o["cash"], r_m["cash"], "num1", "Juta NTD")
    tambah("DCF: enterprise_value (EV)", r_o["ev"], r_m["ev"], "num1", "Juta NTD")
    tambah(f"DCF: FCFF {r_o['latest_year']} (fcff0)", r_o["fcff0"], r_m["fcff0"], "num1", "Juta NTD")
    tambah("DCF: FCFF 3y average", r_o["fcff_average"], r_m["fcff_average"], "num1", "Juta NTD")
    tambah("DCF: cost_of_equity (ke)", r_o["cost_of_equity"], r_m["cost_of_equity"], "pct2", "")
    tambah("DCF: cost_of_debt (kd pre-tax)", r_o["cost_of_debt"], r_m["cost_of_debt"], "pct2", "")
    tambah("DCF: WACC", r_o["wacc"], r_m["wacc"], "pct2", "")
    tambah("DCF: implied_growth (g tersirat)", r_o["implied_growth"], r_m["implied_growth"], "pct2", "")

    lines = [
        f"## Perbandingan Valuasi Otomatis vs Manual — {kode} ({oto.get('name')})",
        "",
        "| Field | Otomatis | Manual | Selisih % | Catatan |",
        "|---|---:|---:|---:|---|",
    ]
    ringkasan_json = []
    for label, v_o, v_m, fmt, cat in baris_perbandingan:
        if fmt == "pct2":
            s_o, s_m = _fmt_pct(v_o, 2), _fmt_pct(v_m, 2)
        elif fmt == "num2":
            s_o, s_m = _fmt_angka(v_o, 2), _fmt_angka(v_m, 2)
        elif fmt == "num4":
            s_o, s_m = _fmt_angka(v_o, 4), _fmt_angka(v_m, 4)
        else:
            s_o, s_m = _fmt_angka(v_o, 1), _fmt_angka(v_m, 1)
        sel = _selisih_pct(v_o, v_m)
        lines.append(f"| `{label}` | {s_o} | {s_m} | {sel} | {cat} |")
        ringkasan_json.append({
            "field": label,
            "otomatis": v_o,
            "manual": v_m,
            "selisih_pct": sel,
            "catatan": cat,
        })

    return "\n".join(lines), {"kode": kode, "otomatis": r_o, "manual": r_m, "baris": ringkasan_json}


def pilih_dan_bangun_acak(jumlah: int = 10, seed: int = 7, jeda: float = 0.25) -> tuple[str, list[dict]]:
    """Pilih `jumlah` emiten non-keuangan acak dari daftar bursa (TWSE & TPEx), bangun DCF otomatis."""
    harga_valid = {
        str(r.get("Code", "")).strip()
        for r in pasar._daftar("harga_twse", "harga")
        if pasar._f(r.get("ClosingPrice")) and pasar._f(r.get("ClosingPrice")) > 0
    } | {
        str(r.get("SecuritiesCompanyCode", "")).strip()
        for r in pasar._daftar("harga_tpex", "harga")
        if pasar._f(r.get("Close")) and pasar._f(r.get("Close")) > 0
    }

    kandidat_twse = sorted(
        str(r.get("公司代號") or "").strip()
        for r in pasar.daftar_profil("profil_twse")
        if len(str(r.get("公司代號") or "").strip()) == 4
        and str(r.get("公司代號") or "").strip().isdigit()
        and str(r.get("產業別") or "").strip() not in pasar.INDUSTRI_KEUANGAN
        and str(r.get("公司代號") or "").strip() in harga_valid
    )
    kandidat_tpex = sorted(
        str(r.get("SecuritiesCompanyCode") or r.get("公司代號") or "").strip()
        for r in pasar.daftar_profil("profil_tpex")
        if len(str(r.get("SecuritiesCompanyCode") or r.get("公司代號") or "").strip()) == 4
        and str(r.get("SecuritiesCompanyCode") or r.get("公司代號") or "").strip().isdigit()
        and str(r.get("SecuritiesIndustryCode") or r.get("產業別") or "").strip() not in pasar.INDUSTRI_KEUANGAN
        and str(r.get("SecuritiesCompanyCode") or r.get("公司代號") or "").strip() in harga_valid
    )

    rng = random.Random(seed)
    acak_twse = list(kandidat_twse)
    acak_tpex = list(kandidat_tpex)
    rng.shuffle(acak_twse)
    rng.shuffle(acak_tpex)

    # Selang-seling TWSE dan TPEx agar kedua bursa terwakili secara seimbang
    urutan_kandidat: list[str] = []
    for a, b in zip(acak_twse, acak_tpex):
        urutan_kandidat.append(a)
        urutan_kandidat.append(b)
    sisa = acak_twse[len(acak_tpex):] + acak_tpex[len(acak_twse):]
    urutan_kandidat.extend(sisa)

    hasil_ok: list[dict] = []
    hasil_dilewati: list[dict] = []

    for kode in urutan_kandidat:
        if len(hasil_ok) >= jumlah:
            break
        # Cek apakah sudah ada di cache disk supaya hemat kuota FinMind
        butuh_jaringan = not (Path(pasar.CACHE_DIR) / f"finmind_neraca_{kode}.json").exists()
        if butuh_jaringan and jeda > 0:
            time.sleep(jeda)

        d = valuasi_otomatis.bangun(kode)
        valuasi_otomatis.simpan_cache(kode, d)

        if valuasi_otomatis.layak_dcf(d):
            g_ceil = d.get("assumptions", {}).get("terminal_growth_ceiling")
            r = dcf.compute(d, forward_g=g_ceil)
            baris = {
                "kode": kode,
                "nama": d.get("name", kode),
                "bursa": d.get("bursa", "TWSE"),
                "tahun_fiskal": d.get("fiscal_year"),
                "harga": r["price_per_share"],
                "kapitalisasi": round(r["market_cap"], 1),
                "fcff0": round(r["fcff0"], 1),
                "wacc": r["wacc"],
                "beta": r["wacc_inputs"]["beta"],
                "beta_cadangan": bool(d.get("beta_cadangan")),
                "pekan_beta": d.get("jumlah_pekan_beta", 0),
                "g_tersirat": r["implied_growth"],
                "status": "ok",
                "catatan": "; ".join(p.get("teks", "") for p in (d.get("peringatan") or [])),
            }
            hasil_ok.append(baris)
        else:
            status_str = "tidak_berlaku" if d.get("tidak_berlaku") else "tidak_bisa_dihitung"
            hasil_dilewati.append({
                "kode": kode,
                "nama": d.get("name", kode),
                "bursa": d.get("bursa", "TWSE"),
                "status": status_str,
                "alasan": d.get("alasan", ""),
            })

    lines = [
        f"## Ringkasan {len(hasil_ok)} Emiten Non-Keuangan Acak (seed={seed})",
        "",
        "| # | Kode | Nama | Bursa | Harga (NTD) | Kap. Pasar (Juta NTD) | FCFF0 (Juta NTD) | WACC | Beta (Cadangan?) | g Tersirat | Status |",
        "|---:|---|---|---|---|---:|---:|---:|---|---:|---|",
    ]
    for idx, b in enumerate(hasil_ok, start=1):
        beta_str = (
            f"{b['beta']:.2f} (cadangan)"
            if b["beta_cadangan"]
            else f"{b['beta']:.4f} ({b['pekan_beta']}w)"
        )
        lines.append(
            f"| {idx} | `{b['kode']}` | {b['nama']} | {b['bursa']} | "
            f"{_fmt_angka(b['harga'], 2)} | {_fmt_angka(b['kapitalisasi'], 1)} | "
            f"{_fmt_angka(b['fcff0'], 1)} | {_fmt_pct(b['wacc'], 2)} | "
            f"{beta_str} | {_fmt_pct(b['g_tersirat'], 2)} | `{b['status']}` |"
        )

    if hasil_dilewati:
        lines.extend([
            "",
            "### Emiten Acak yang Ditandai `tidak_bisa_dihitung` Saat Penarikan Sampel",
            "",
            "| Kode | Nama | Bursa | Status | Alasan |",
            "|---|---|---|---|---|",
        ])
        for s in hasil_dilewati:
            lines.append(
                f"| `{s['kode']}` | {s['nama']} | {s['bursa']} | `{s['status']}` | {s['alasan']} |"
            )

    return "\n".join(lines), hasil_ok + hasil_dilewati


def cetak_satu(kode: str) -> str:
    d = valuasi_otomatis.bangun(kode)
    valuasi_otomatis.simpan_cache(kode, d)
    if d.get("tidak_berlaku"):
        return f"[{kode}] TIDAK BERLAKU ({d.get('bursa')}): {d.get('alasan')}"
    if d.get("tidak_bisa_dihitung"):
        return f"[{kode}] TIDAK BISA DIHITUNG ({d.get('bursa')}): {d.get('alasan')}"
    r = dcf.compute(d, forward_g=d.get("assumptions", {}).get("terminal_growth_ceiling"))
    return (
        f"[{kode}] {d.get('name')} ({d.get('bursa')}) · FY{d.get('fiscal_year')}\n"
        f"  Harga        : {r['price_per_share']:,.2f} NTD ({r['as_of']})\n"
        f"  Kapitalisasi : {r['market_cap']:,.1f} juta NTD\n"
        f"  Utang / Kas  : {r['debt']:,.1f} / {r['cash']:,.1f} juta NTD → EV {r['ev']:,.1f} juta NTD\n"
        f"  FCFF0        : {r['fcff0']:,.1f} juta NTD (rata-rata 3th: {r['fcff_average']:,.1f})\n"
        f"  Beta         : {r['wacc_inputs']['beta']} (cadangan={d.get('beta_cadangan')}, pekan={d.get('jumlah_pekan_beta')})\n"
        f"  WACC         : {r['wacc']*100:.2f}% (ke={r['cost_of_equity']*100:.2f}%, kd={r['cost_of_debt']*100:.2f}%, tax={r['tax_rate']*100:.2f}%)\n"
        f"  g tersirat   : {r['implied_growth']*100:.2f}% (batas={r['terminal_growth_ceiling']*100:.2f}%)\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CLI pembangun & pembanding DCF otomatis (Tugas B2)")
    parser.add_argument("kode", nargs="?", default="", help="Kode emiten (mis. 2330, 2454, 2881)")
    parser.add_argument("--banding", action="store_true", help="Bandingkan otomatis vs berkas manual")
    parser.add_argument("--acak", type=int, default=0, help="Pilih N emiten non-keuangan acak dari daftar bursa")
    parser.add_argument("--seed", type=int, default=7, help="Seed pemilihan acak (bawaan: 7)")
    parser.add_argument("--simpan", action="store_true", help="Simpan laporan ke eval/hasil/b2-<tanggal>.md")
    args = parser.parse_args(argv)

    bagian_md: list[str] = []
    tgl_str = dt.date.today().isoformat()

    if args.banding:
        kode_b = args.kode or "2330"
        md_b, _ = bandingkan_dengan_manual(kode_b)
        print(md_b)
        print()
        bagian_md.append(md_b)
    elif args.kode:
        teks = cetak_satu(args.kode)
        print(teks)
        bagian_md.append(f"```text\n{teks}\n```")

    if args.acak > 0:
        md_a, _ = pilih_dan_bangun_acak(jumlah=args.acak, seed=args.seed)
        print(md_a)
        print()
        bagian_md.append(md_a)

    if not bagian_md:
        # Bawaan bila dipanggil tanpa argumen: jalankan 2330 --banding
        md_b, _ = bandingkan_dengan_manual("2330")
        print(md_b)
        bagian_md.append(md_b)

    if args.simpan:
        # Bila --simpan dipanggil hanya dengan --acak, sertakan juga tabel perbandingan 2330
        if not args.banding:
            md_b, _ = bandingkan_dengan_manual("2330")
            bagian_md.insert(0, md_b)
        out_dir = ROOT / "eval" / "hasil"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"b2-{tgl_str}.md"
        kepala = [
            f"# Hasil Evaluasi B2 — Valuasi DCF Otomatis ({tgl_str})",
            "",
            f"- Dibangun pada: `{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            f"- Seed pemilihan acak: `{args.seed}`",
            "",
        ]
        out_path.write_text("\n".join(kepala + ["\n\n".join(bagian_md), ""]), encoding="utf-8")
        print(f"Disimpan ke: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
