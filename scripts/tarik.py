#!/usr/bin/env python3
"""Tarik pengumuman material terbaru untuk watchlist — sama dengan tombol "Periksa sekarang".

Bisa dijalankan dari jaringan mana pun: sumbernya OpenAPI resmi TWSE/TPEx, bukan MOPS.

Pakai:
    python3 scripts/tarik.py                     # pakai watchlist di data/watchlist.json
    python3 scripts/tarik.py --kode 2330 2454    # sekali jalan, watchlist tidak diubah
    python3 scripts/tarik.py --ulang 600         # periksa tiap 600 detik sampai Ctrl+C

Keluaran:
    data/parsed/details.json     riwayat pengumuman, digabung tanpa duplikat
    data/raw/openapi/*.json      respons mentah tiap tarikan (bukti, tidak di-commit)
    data/status_tarik.json       hasil pemeriksaan terakhir
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import tarik  # noqa: E402

# Jangan lebih sering dari ini. OpenAPI publik, dan isinya hanya berubah beberapa
# kali per jam di hari bursa.
JEDA_MIN = 300


def sekali(kode: list[str] | None) -> bool:
    st = tarik.periksa_sekarang(kode)
    for nama, s in st["sumber"].items():
        if s["ok"]:
            print(f"  {nama.upper():5} OK   {s['jumlah']:>4} pengumuman · {s['cocok_watchlist']} di watchlist"
                  f" · data {s['tanggal_data']} · {s['durasi_ms']} ms")
        else:
            print(f"  {nama.upper():5} GAGAL {s['jenis']}: {s['pesan']}")
    print(f"  → {st['baru']} pengumuman baru disimpan "
          f"(watchlist: {', '.join(st['watchlist']) or 'kosong'})")
    return st["ok"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kode", nargs="+", help="kode emiten untuk tarikan ini saja")
    ap.add_argument("--ulang", type=int, help=f"ulangi tiap N detik (minimal {JEDA_MIN})")
    a = ap.parse_args()

    if not a.ulang:
        return 0 if sekali(a.kode) else 1

    jeda = max(a.ulang, JEDA_MIN)
    print(f"Memeriksa tiap {jeda} detik. Ctrl+C untuk berhenti.")
    try:
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S"))
            sekali(a.kode)
            time.sleep(jeda)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
