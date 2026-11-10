"""Umpan balik 👍/👎 → ambang triase per pasal (behavioral feedback → continuous optimization).

Satu set ambang untuk seluruh server (keputusan tim, 10 Nov: satu investor per server).
Ambang **diturunkan dari suara**, tidak ditambah-kurangi di tempat, sehingga mengganti
atau mencabut suara selalu menghasilkan ambang yang konsisten:

    ambang(pasal) = batas(DASAR + 0,05 × 👎 − 0,02 × 👍, 0,40, 0,90)

👎 berarti "peringatan seperti ini tidak berguna", dan menaikkan ambang lebih cepat
daripada 👍 menurunkannya: derau diredam cepat, tapi pemulihan dibuat hati-hati.
Batas atas 0,90 disengaja. Umpan balik tidak pernah bisa membungkam pengumuman yang
benar-benar material (skor maksimum 0,85 + zona ragu), paling jauh menahannya untuk
dilihat manusia.

Reset mengosongkan suara satu pasal (tetap tercatat di riwayat). Kunci membekukan
ambang pada nilainya saat itu; suara tetap dicatat, tapi tidak menggeser ambang
sampai kunci dibuka.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone

from . import config

FILE = os.path.join(config.DATA_DIR, "umpan_balik.json")
DASAR = config.TRIAGE_THRESHOLD
NAIK_PER_BAWAH = 0.05     # setiap 👎
TURUN_PER_ATAS = 0.02     # setiap 👍
BATAS = (0.40, 0.90)
SUARA_SAH = ("atas", "bawah")
RIWAYAT_MAKS = 500

_kunci_berkas = threading.Lock()


def _sekarang() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def kunci_pasal(klausa) -> str:
    return str(klausa) if klausa is not None else "?"


def _kosong() -> dict:
    return {"suara": {}, "pasal": {}, "riwayat": []}


def baca() -> dict:
    if not os.path.exists(FILE):
        return _kosong()
    try:
        with open(FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return _kosong()
    if not isinstance(data, dict):
        return _kosong()
    for k, v in _kosong().items():
        data.setdefault(k, v)
    return data


def _tulis(data: dict) -> None:
    data["riwayat"] = data["riwayat"][-RIWAYAT_MAKS:]
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, FILE)


def _batasi(x: float) -> float:
    return round(min(BATAS[1], max(BATAS[0], x)), 2)


def ambang(pasal: str, data: dict | None = None) -> dict:
    """Ambang yang berlaku untuk satu pasal, beserta asal-usulnya."""
    data = data if data is not None else baca()
    suara = [s for s in data["suara"].values() if s.get("pasal") == pasal]
    atas = sum(1 for s in suara if s.get("suara") == "atas")
    bawah = sum(1 for s in suara if s.get("suara") == "bawah")
    turunan = _batasi(DASAR + NAIK_PER_BAWAH * bawah - TURUN_PER_ATAS * atas)
    kunci = (data["pasal"].get(pasal) or {}).get("kunci")
    return {
        "pasal": pasal,
        "nilai": kunci["nilai"] if kunci else turunan,
        "turunan": turunan,
        "dasar": DASAR,
        "atas": atas,
        "bawah": bawah,
        "terkunci": bool(kunci),
        "kunci_sejak": kunci.get("waktu") if kunci else None,
        "reset_terakhir": (data["pasal"].get(pasal) or {}).get("reset"),
    }


def suara_untuk(pengenal: str, data: dict | None = None) -> str | None:
    data = data if data is not None else baca()
    return (data["suara"].get(pengenal) or {}).get("suara")


def beri_suara(pengenal: str, pasal: str, suara: str, skor: float | None = None,
               kode: str | None = None) -> dict:
    """Catat 👍 ('atas'), 👎 ('bawah'), atau cabut ('hapus'). Kembalikan ambang lama → baru."""
    if suara not in SUARA_SAH + ("hapus",):
        raise ValueError(f"suara tidak dikenal: {suara}")
    with _kunci_berkas:
        data = baca()
        lama = ambang(pasal, data)["nilai"]
        if suara == "hapus":
            data["suara"].pop(pengenal, None)
        else:
            data["suara"][pengenal] = {"suara": suara, "pasal": pasal, "skor": skor,
                                       "kode": kode, "waktu": _sekarang()}
        baru = ambang(pasal, data)["nilai"]
        data["riwayat"].append({"waktu": _sekarang(), "peristiwa": "suara", "pasal": pasal,
                                "id": pengenal, "suara": suara, "skor": skor,
                                "dari": lama, "ke": baru})
        _tulis(data)
    return {"dari": lama, "ke": baru}


def reset(pasal: str) -> dict:
    with _kunci_berkas:
        data = baca()
        lama = ambang(pasal, data)["nilai"]
        n = 0
        for k in [k for k, s in data["suara"].items() if s.get("pasal") == pasal]:
            data["suara"].pop(k)
            n += 1
        p = data["pasal"].setdefault(pasal, {})
        p["reset"] = _sekarang()
        p.pop("kunci", None)
        baru = ambang(pasal, data)["nilai"]
        data["riwayat"].append({"waktu": _sekarang(), "peristiwa": "reset", "pasal": pasal,
                                "dihapus": n, "dari": lama, "ke": baru})
        _tulis(data)
    return {"dari": lama, "ke": baru, "dihapus": n}


def kunci(pasal: str, nyala: bool) -> dict:
    with _kunci_berkas:
        data = baca()
        sekarang = ambang(pasal, data)
        p = data["pasal"].setdefault(pasal, {})
        if nyala:
            p["kunci"] = {"nilai": sekarang["nilai"], "waktu": _sekarang()}
        else:
            p.pop("kunci", None)
        baru = ambang(pasal, data)["nilai"]
        data["riwayat"].append({"waktu": _sekarang(), "peristiwa": "kunci" if nyala else "buka",
                                "pasal": pasal, "dari": sekarang["nilai"], "ke": baru})
        _tulis(data)
    return {"dari": sekarang["nilai"], "ke": baru}


def semua(pasal_terlihat: list[str] | None = None) -> dict:
    """Semua ambang (pasal yang punya suara/pengaturan + yang disebut) dan riwayatnya."""
    data = baca()
    daftar = set(pasal_terlihat or [])
    daftar |= {s.get("pasal") for s in data["suara"].values() if s.get("pasal")}
    daftar |= set(data["pasal"])

    def urut(p):
        return (0, int(p)) if p.isdigit() else (1, 0)
    return {
        "ambang": [ambang(p, data) for p in sorted(daftar, key=urut)],
        "riwayat": list(reversed(data["riwayat"]))[:100],
        "aturan": {"dasar": DASAR, "naik_per_bawah": NAIK_PER_BAWAH,
                   "turun_per_atas": TURUN_PER_ATAS, "batas": list(BATAS)},
    }
