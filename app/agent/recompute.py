"""Tahap 3 — penghitung. Deterministik, tanpa model.

Memanggil `scripts/dcf.py` lewat `compute()`, bukan menghitung ulang sendiri. Kalau
aplikasi web punya aritmetika sendiri, angka di layar dan angka di kertas kerja akan
berbeda diam-diam — dan itu baru ketahuan waktu juri mencocokkan.

CARA MEMBACA ANGKANYA — penting, dan sengaja dibatasi.

Reverse DCF tidak menghasilkan nilai intrinsik. Yang dihasilkannya adalah
**pertumbuhan abadi yang sedang diasumsikan pasar**. Jadi yang bergerak ketika sebuah
pengumuman mengubah input bukan "nilai wajar menurut kami", melainkan g tersirat: pada
harga pasar yang sama, pasar kini harus mengasumsikan pertumbuhan sekian.

Nilai wajar tetap ditampilkan, tapi sebagai **skenario dengan asumsi yang disebutkan**
— pada batas pertumbuhan abadi (PDB nominal jangka panjang), nilai wajarnya sekian.
Itu bukan ramalan, dan tidak boleh disajikan sebagai ramalan.
"""

from __future__ import annotations

import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "scripts"))
import dcf                                              # noqa: E402

# Bagaimana tiap input valuasi disentuh oleh angka baru, dan apa artinya.
# Semantiknya "ganti", bukan "tambah": pengumuman anggaran menyatakan tingkat
# belanja, jadi yang dijawab adalah "kalau tingkat ini berlanjut, bagaimana".
PENERAPAN = {
    "capex": {
        "jalur": ("cash_flow", "capex_by_year"),
        "tahun_terakhir": True,
        "arti": "Mengganti belanja modal tahun terakhir — skenario bila tingkat ini berlanjut",
    },
    "cash": {
        "jalur": ("balance_sheet", "cash_and_equivalents"),
        "tahun_terakhir": False,
        "arti": "Mengganti saldo kas dan setara kas",
    },
    "debt": {
        "jalur": ("balance_sheet", "long_term_debt"),
        "tahun_terakhir": False,
        "arti": "Mengganti utang jangka panjang",
    },
}


def nilai_sekarang(d: dict, input_nama: str) -> float | None:
    aturan = PENERAPAN.get(input_nama)
    if not aturan:
        return None
    bagian, kunci = aturan["jalur"]
    simpul = d.get(bagian, {}).get(kunci)
    if aturan["tahun_terakhir"]:
        if not isinstance(simpul, dict) or not simpul:
            return None
        return simpul[max(simpul)]
    return simpul if isinstance(simpul, (int, float)) else None


def terapkan(d: dict, input_nama: str, nilai: float) -> tuple[dict, str]:
    """Salin input valuasi dan terapkan satu angka baru."""
    aturan = PENERAPAN[input_nama]
    baru = copy.deepcopy(d)
    bagian, kunci = aturan["jalur"]
    if aturan["tahun_terakhir"]:
        seri = baru[bagian][kunci]
        seri[max(seri)] = nilai
    else:
        baru[bagian][kunci] = nilai
    return baru, aturan["arti"]


def hitung_ulang(d: dict, input_nama: str, nilai: float) -> dict:
    """Hitung sebelum dan sesudah, lalu bandingkan.

    `g_skenario` memakai batas pertumbuhan abadi dari berkas input, supaya asumsi
    di balik angka nilai wajar selalu disebutkan bersama angkanya.
    """
    g_skenario = d.get("assumptions", {}).get("terminal_growth_ceiling")

    sebelum = dcf.compute(d, forward_g=g_skenario)
    d_baru, arti = terapkan(d, input_nama, nilai)
    sesudah = dcf.compute(d_baru, forward_g=g_skenario)

    def wajar(r):
        f = r.get("forward") or {}
        return f.get("fair_value")

    return {
        "input": input_nama,
        "arti": arti,
        "arti_i18n": {"kode": f"arti.{input_nama}", "param": {}},
        "nilai_lama": nilai_sekarang(d, input_nama),
        "nilai_baru": nilai,
        "g_skenario": g_skenario,
        "sebelum": sebelum,
        "sesudah": sesudah,
        "delta": {
            "fcff0": sesudah["fcff0"] - sebelum["fcff0"],
            "g_tersirat": sesudah["implied_growth"] - sebelum["implied_growth"],
            "nilai_wajar": (None if (wajar(sebelum) is None or wajar(sesudah) is None)
                            else wajar(sesudah) - wajar(sebelum)),
        },
        "melampaui_batas": {
            "sebelum": sebelum["exceeds_ceiling"],
            "sesudah": sesudah["exceeds_ceiling"],
        },
    }
