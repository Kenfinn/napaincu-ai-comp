#!/usr/bin/env python3
"""Statistik nomor pasal (符合條款) dari pengumuman asli — bahan verifikasi daftar pasal.

Membaca arsip mentah OpenAPI (data/raw/openapi/*.json, ditulis penarik setiap kali
memeriksa) atau berkas yang disebut, membuang duplikat, lalu mencetak tabel Markdown:
jumlah per pasal di TWSE dan TPEx, contoh judul, label butir yang memuat jumlah uang,
dan keputusan saringan saat ini.

Pakai:
    python3 scripts/statistik_pasal.py                         # arsip di data/raw/openapi
    python3 scripts/statistik_pasal.py twse.json tpex.json     # berkas tertentu
    python3 scripts/statistik_pasal.py --contoh 5 > pasal.md
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import config, tarik            # noqa: E402
from app.agent import screen             # noqa: E402

UANG = re.compile(r"金額|價格|價款|餘額|總額|限額|股利|額度|營業收入|淨利|總資產|總負債|權益")


def _muat(berkas: list[str]) -> list[dict]:
    rek, lihat = [], set()
    for p in berkas:
        sumber = "tpex" if "tpex" in os.path.basename(p) else "twse"
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for r in data if isinstance(data, list) else []:
            d = tarik.normalkan(r, sumber, "arsip")
            k = tarik._kunci(d)
            if k not in lihat:
                lihat.add(k)
                rek.append(d)
    return rek


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("berkas", nargs="*")
    ap.add_argument("--contoh", type=int, default=3)
    a = ap.parse_args()
    berkas = a.berkas or sorted(glob.glob(os.path.join(config.DATA_DIR, "raw", "openapi", "*.json")))
    rek = _muat(berkas)
    if not rek:
        print("Tidak ada data. Jalankan penarik dulu, atau sebutkan berkasnya.", file=sys.stderr)
        return 1

    per = collections.defaultdict(list)
    for d in rek:
        per[d["clause"]].append(d)
    tanggal = sorted({d["date"] for d in rek if d["date"]})
    print(f"Dari {len(rek)} pengumuman unik ({tanggal[0]} s.d. {tanggal[-1]}), "
          f"{len(berkas)} berkas arsip.\n")
    print("| Pasal | TWSE | TPEx | Saringan sekarang | Contoh judul | Label butir berisi jumlah |")
    print("|---|---|---|---|---|---|")
    for k, ds in sorted(per.items(), key=lambda kv: -len(kv[1])):
        tw = sum(1 for d in ds if d["pasar"] == "sii")
        tp = len(ds) - tw
        s = screen.saring({"clause": k})
        sekarang = "lolos → " + ", ".join(s["input_mungkin"]) if s["lolos"] else "dilewati"
        judul = " · ".join(dict.fromkeys(d["subject"][:30] for d in ds))
        judul = " · ".join(list(dict.fromkeys(d["subject"][:30] for d in ds))[:a.contoh])
        label = collections.Counter()
        for d in ds:
            for b in d["items"]:
                for x in [b] + b.get("sub", []):
                    if UANG.search(x["label"]):
                        label[x["label"][:26] + (f" ({x['satuan_label']})" if x.get("satuan_label") else "")] += 1
        lab = " · ".join(f"{lbl}" for lbl, _ in label.most_common(4)) or "—"
        print(f"| {k} | {tw} | {tp} | {sekarang} | {judul} | {lab} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
