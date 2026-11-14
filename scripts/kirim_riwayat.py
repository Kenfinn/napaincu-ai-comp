#!/usr/bin/env python3
"""Kirim riwayat pengumuman MOPS dari laptop (jaringan Taiwan) ke server FEAF.

Riwayat lama hanya bisa ditarik dari jaringan Taiwan, sedangkan server berjalan di
tempat lain. Skrip ini membaca data/parsed/details.json hasil fetch_details.py dan
mengirimnya ke /api/import. Server memvalidasi ulang, membuang data pribadi lagi,
dan menggabungkan tanpa duplikat — mengirim dua kali aman.

Pakai:
    python3 scripts/kirim_riwayat.py --server https://feaf.example.com
    python3 scripts/kirim_riwayat.py --server https://feaf.example.com --berkas data/parsed/details.json

Kode akses (SENTINEL_KODE_AKSES di server) ditanyakan tanpa tampil di layar, atau
diambil dari environment FEAF_KODE_AKSES. Jangan menulisnya di perintah.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_KIRIM = 300


def kirim(server: str, kode: str, potong: list[dict]) -> dict:
    req = urllib.request.Request(
        server.rstrip("/") + "/api/import",
        data=json.dumps(potong, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Access-Code": kode,
                 "User-Agent": "FEAF-kirim-riwayat/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", required=True, help="mis. https://feaf.example.com")
    ap.add_argument("--berkas", default=os.path.join(ROOT, "data", "parsed", "details.json"))
    a = ap.parse_args()

    if not os.path.exists(a.berkas):
        print(f"Belum ada {a.berkas}. Jalankan dulu spike_mops.py → parse_mops.py → fetch_details.py.")
        return 1
    with open(a.berkas, encoding="utf-8") as f:
        data = json.load(f)
    print(f"{len(data)} pengumuman di {os.path.relpath(a.berkas, ROOT)}")

    kode = os.environ.get("FEAF_KODE_AKSES") or getpass.getpass("Kode akses server: ")
    total = {"diterima": 0, "baru": 0, "ditolak": 0}
    for i in range(0, len(data), PER_KIRIM):
        potong = data[i:i + PER_KIRIM]
        try:
            h = kirim(a.server, kode, potong)
        except urllib.error.HTTPError as e:
            pesan = e.read().decode("utf-8", "replace")[:300]
            print(f"  GAGAL HTTP {e.code}: {pesan}")
            if e.code == 403:
                print("  Kode akses salah, atau SENTINEL_KODE_AKSES belum diisi di server.")
            return 1
        except Exception as e:                                     # noqa: BLE001
            print(f"  GAGAL: {type(e).__name__}: {e}")
            return 1
        for k in total:
            total[k] += h.get(k, 0)
        print(f"  {i + len(potong):>5}/{len(data)} · diterima {h['diterima']} · baru {h['baru']}"
              f" · ditolak {h['ditolak']}" + (f" · contoh: {h['contoh_tolak'][:2]}" if h["ditolak"] else ""))

    print(f"\nSelesai: {total['baru']} pengumuman baru masuk ke server "
          f"({total['diterima'] - total['baru']} sudah ada, {total['ditolak']} ditolak).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
