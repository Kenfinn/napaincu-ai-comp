"""Kandidat gold set dari arsip mentah penarik — supaya pelabelan tidak menunggu laptop Taiwan.

Penarik menyimpan SELURUH respons OpenAPI setiap kali memeriksa (data/raw/openapi), bukan
hanya emiten di watchlist. Arsip itu berisi ratusan pengumuman semua emiten per hari, jadi
cukup untuk memilih 30–50 kasus uji yang seimbang:

    - beberapa per pasal yang diusulkan relevan (docs/pemetaan-pasal.md)
    - beberapa pasal yang seharusnya DILEWATI, supaya gold set juga menguji "tidak terbit"
    - emiten dibuat beragam, pemilihan acak dengan seed tetap supaya bisa diulang
"""

from __future__ import annotations

import csv
import glob
import io
import os
import random

from . import config, tarik

ARSIP_DIR = os.path.join(config.DATA_DIR, "raw", "openapi")

PASAL_RELEVAN = (31, 20, 11, 35, 10, 22, 23, 1, 3, 40, 28, 26, 51, 53)
PASAL_NEGATIF = (12, 14, 6, 8, 17, 43)

KOLOM = ["source_url", "kode", "nama", "tanggal", "pasal", "judul", "ringkasan_butir",
         "harus_terbit", "input", "nilai_juta_ntd", "butir_no", "pelabel", "catatan"]


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
    """Butir yang memuat angka, ringkas, supaya pelabel tidak perlu membuka MOPS untuk kasus mudah."""
    keluar = []
    for b in d.get("items", []):
        for x in [b] + b.get("sub", []):
            v = x.get("value") or ""
            if any(c.isdigit() for c in v) and len(keluar) < maks:
                sat = f"({x['satuan_label']})" if x.get("satuan_label") else ""
                keluar.append(f"{x.get('no')}. {x['label'][:28]}{sat}: {v[:60]}")
    return " | ".join(keluar)


def pilih(rek: list[dict], per_pasal: int = 4, negatif_per_pasal: int = 2, seed: int = 11) -> list[dict]:
    acak = random.Random(seed)
    per: dict[int, list[dict]] = {}
    for d in rek:
        per.setdefault(d["clause"], []).append(d)
    hasil = []
    for pasal, n in [(p, per_pasal) for p in PASAL_RELEVAN] + [(p, negatif_per_pasal) for p in PASAL_NEGATIF]:
        calon = per.get(pasal, [])[:]
        acak.shuffle(calon)
        dipakai_emiten: set[str] = set()
        for d in calon:
            if len([h for h in hasil if h["clause"] == pasal]) >= n:
                break
            if d["code"] in dipakai_emiten:
                continue
            dipakai_emiten.add(d["code"])
            hasil.append(d)
    return hasil


def csv_kandidat(rek: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=KOLOM)
    w.writeheader()
    for d in rek:
        w.writerow({"source_url": d["source_url"], "kode": d["code"], "nama": d["name"],
                    "tanggal": d["date"], "pasal": d["clause"], "judul": d["subject"],
                    "ringkasan_butir": _ringkas(d)})
    return buf.getvalue()
