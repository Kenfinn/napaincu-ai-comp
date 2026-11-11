"""Kandidat gold set dari arsip mentah penarik — supaya pelabelan tidak menunggu laptop Taiwan.

Penarik menyimpan SELURUH respons OpenAPI setiap kali memeriksa (data/raw/openapi), bukan
hanya emiten di watchlist. Arsip itu berisi ratusan pengumuman semua emiten per hari, jadi
cukup untuk memilih 30–50 kasus uji yang seimbang:

    - beberapa per jalur sinyal B1 (valuasi, risiko, modal, laporan, berat, tata_kelola, dilewati)
    - emiten dibuat beragam, pemilihan acak dengan seed tetap supaya bisa diulang
"""

from __future__ import annotations

import csv
import glob
import io
import os
import random

from . import config, tarik
from .agent import screen

ARSIP_DIR = os.path.join(config.DATA_DIR, "raw", "openapi")

JALUR_SEMUA = ("valuasi", "risiko", "modal", "laporan", "berat", "tata_kelola", "dilewati")

# Daftar pasal historis untuk rujukan dan kompatibilitas
PASAL_RELEVAN = (31, 20, 11, 35, 10, 22, 23, 1, 3, 40, 28, 26, 51, 53)
PASAL_NEGATIF = (12, 14, 6, 8, 17, 43)

KOLOM = [
    "source_url", "kode", "nama", "tanggal", "pasal", "judul", "ringkasan_butir",
    "harus_terbit", "keputusan", "tingkat", "input", "nilai_juta_ntd", "butir_no", "pelabel", "catatan"
]


def jalur_pengumuman(d: dict) -> str:
    """Tentukan jalur sinyal suatu pengumuman."""
    s = screen.saring(d)
    if not s.get("lolos"):
        return "dilewati"
    return s.get("jalur") or "dilewati"


def muat_arsip(folder: str | None = None) -> list[dict]:
    """Semua pengumuman unik dari arsip mentah, sudah dinormalkan seperti data aplikasi."""
    rek, lihat = [], set()
    for p in sorted(glob.glob(os.path.join(folder or ARSIP_DIR, "*.json"))):
        sumber = "tpex" if p.endswith("-tpex.json") else "twse"
        try:
            with open(p, encoding="utf-8") as f:
                data = __import__("json").load(f)
        except (OSError, ValueError):
            continue
        for r in data if isinstance(data, list) else []:
            d = tarik.normalkan(r, sumber, "arsip")
            k = tarik._kunci(d)
            if k not in lihat and d["code"]:
                lihat.add(k)
                rek.append(d)
    return rek


def _ringkas(d: dict, maks: int = 6) -> str:
    """Butir yang memuat angka, ringkas, supaya pelabel tidak perlu membuka MOPS untuk kasus mudah.
    
    Nama orang (butir dengan label memuat 姓名) tidak pernah dimasukkan demi privasi.
    """
    keluar = []
    for b in d.get("items", []):
        for x in [b] + b.get("sub", []):
            lbl = x.get("label") or ""
            induk_lbl = b.get("label") or ""
            if "姓名" in lbl or "姓名" in induk_lbl:
                continue
            v = x.get("value") or ""
            if any(c.isdigit() for c in v) and len(keluar) < maks:
                sat = f"({x['satuan_label']})" if x.get("satuan_label") else ""
                keluar.append(f"{x.get('no')}. {lbl[:28]}{sat}: {v[:60]}")
    return " | ".join(keluar)


def pilih(
    rek: list[dict],
    per_jalur: int = 4,
    per_pasal: int | None = None,
    negatif_per_pasal: int | None = None,
    seed: int = 11,
) -> list[dict]:
    """Pilih sampel seimbang per jalur (valuasi, risiko, modal, laporan, berat, tata_kelola, dilewati)."""
    acak = random.Random(seed)
    per: dict[str, list[dict]] = {j: [] for j in JALUR_SEMUA}
    for d in rek:
        j = jalur_pengumuman(d)
        if j in per:
            per[j].append(d)
        else:
            per["dilewati"].append(d)

    target = per_pasal if per_pasal is not None else per_jalur
    target = max(1, target)

    hasil = []
    for j in JALUR_SEMUA:
        calon = per.get(j, [])[:]
        acak.shuffle(calon)
        dipakai_emiten: set[str] = set()
        count = 0
        for d in calon:
            if count >= target:
                break
            if d.get("code") in dipakai_emiten and len(calon) > target:
                continue
            dipakai_emiten.add(d.get("code", ""))
            hasil.append(d)
            count += 1
    return hasil


def csv_kandidat(rek: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=KOLOM)
    w.writeheader()
    for d in rek:
        w.writerow({
            "source_url": d.get("source_url", ""),
            "kode": d.get("code", ""),
            "nama": d.get("name", ""),
            "tanggal": d.get("date", ""),
            "pasal": d.get("clause", ""),
            "judul": d.get("subject", ""),
            "ringkasan_butir": _ringkas(d),
            "harus_terbit": "",
            "keputusan": "",
            "tingkat": "",
            "input": "",
            "nilai_juta_ntd": "",
            "butir_no": "",
            "pelabel": "",
            "catatan": "",
        })
    return buf.getvalue()
