"""Sitasi resmi laporan keuangan ke MOPS (Market Observation Post System, TWSE/TPEx).

MOPS adalah repositori resmi keterbukaan informasi pasar modal Taiwan.
Fungsi di modul ini menghasilkan tautan langsung ke laporan keuangan asli
emiten (neraca, laba rugi, arus kas) berdasarkan kode emiten, tahun, dan kuartal.
"""

from __future__ import annotations

PROGRAM_MOPS: dict[str, str] = {
    "neraca": "t164sb03",
    "lr": "t164sb04",
    "arus": "t164sb05",
}

CADANGAN_MOPS = "https://mops.twse.com.tw/mops/#/web/{prog}"


def program_untuk_jenis(jenis: str) -> str:
    """Konversi jenis laporan ke kode program MOPS (t164sb03, t164sb04, t164sb05)."""
    j = (jenis or "neraca").lower().strip()
    if j in ("neraca", "balance_sheet", "bs"):
        return "t164sb03"
    if j in ("lr", "income_statement", "is", "pnl", "laba_rugi"):
        return "t164sb04"
    if j in ("arus", "cash_flow", "cf", "cashflow"):
        return "t164sb05"
    return PROGRAM_MOPS.get(j, "t164sb03")


def mops_laporan(
    kode: str,
    tahun_iso: int | str,
    kuartal: int | str | None = None,
    jenis: str = "neraca",
) -> str:
    """Hasilkan URL ajax MOPS untuk laporan keuangan resmi emiten.

    Parameter:
    - kode: Kode emiten (mis. '2330')
    - tahun_iso: Tahun Masehi (mis. 2025 atau '2025-12-31')
    - kuartal: Kuartal 1..4 atau 'Q1'..'Q4' (bila None, diparsing dari tahun_iso)
    - jenis: 'neraca', 'lr', atau 'arus'
    """
    kode_bersih = str(kode).strip().upper()
    prog = program_untuk_jenis(jenis)

    if kuartal is None and "-" in str(tahun_iso):
        parts = str(tahun_iso).split("-")
        th = int(parts[0])
        bl = int(parts[1]) if len(parts) > 1 else 12
        qq = max(1, min(4, bl // 3)) if bl > 0 else 4
    else:
        th = int(str(tahun_iso)[:4])
        if kuartal is None:
            qq = 4
        else:
            q_str = str(kuartal).strip().upper().lstrip("Q")
            qq = int(q_str) if q_str.isdigit() else 4

    roc = th - 1911
    season = f"{qq:02d}"

    return (
        f"https://mopsov.twse.com.tw/mops/web/ajax_{prog}"
        f"?encodeURIComponent=1&step=1&firstin=1&off=1"
        f"&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false"
        f"&co_id={kode_bersih}&year={roc}&season={season}"
    )


def mops_cadangan(jenis: str = "neraca") -> str:
    """Hasilkan URL portal pencarian umum MOPS untuk program terkait sebagai cadangan."""
    prog = program_untuk_jenis(jenis)
    return CADANGAN_MOPS.format(prog=prog)
