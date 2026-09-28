#!/usr/bin/env python3
"""
Ubah HTML mentah MOPS jadi catatan pengumuman yang bisa disitasi.

Jalan di berkas yang sudah tersimpan di data/raw/ — tidak menembak MOPS lagi sama
sekali. Jadi boleh dijalankan berkali-kali tanpa membebani server publik.

Struktur kolom yang ditangani (terkonfirmasi dari hasil tarikan 14 Sep):

    公司代號  公司名稱  發言日期  發言時間  主旨  [tombol 詳細資料]

Kolom terakhir tampak kosong kalau hanya teksnya yang diambil, karena isinya tombol.
Parameter di balik tombol itulah yang membuat tiap pengumuman punya alamat sendiri —
dan tanpa alamat itu, sitasi tidak bisa diverifikasi juri.

Pakai:
    python3 scripts/parse_mops.py
    python3 scripts/parse_mops.py --since 2026-06-01     # saring per tanggal
    python3 scripts/parse_mops.py --code 2330            # satu emiten saja

Keluaran:
    data/parsed/announcements.json   catatan lengkap, terbaru di atas
    data/parsed/announcements.csv    versi untuk dibuka di Excel

Tanpa dependensi eksternal.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
PARSED_DIR = os.path.join(ROOT, "data", "parsed")
REPORT = os.path.join(ROOT, "data", "spike-report.json")

DEFAULT_HOST = "https://mops.twse.com.tw"

# Header yang menandai tabel pengumuman. Dicocokkan longgar — MOPS kadang
# menyisipkan spasi atau kolom kosong tambahan.
HEADER_MARKERS = ("公司代號", "發言日期", "主旨")

# onclick MOPS berisi rentetan `namaField.value='isi';`
VALUE_ASSIGN = re.compile(r"(\w+)\.value\s*=\s*['\"]([^'\"]*)['\"]")


# --------------------------------------------------------------------------

class RowHarvester(HTMLParser):
    """Kumpulkan baris tabel beserta atribut tag di dalam tiap selnya.

    Teks saja tidak cukup: alamat tiap pengumuman hidup di dalam atribut
    onclick pada tombol 詳細資料, bukan di teks sel.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[tuple[list[str], list[dict]]] = []
        self._row_text: list[str] | None = None
        self._row_attrs: list[dict] | None = None
        self._cell: list[str] | None = None
        self._cell_attrs: dict | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row_text, self._row_attrs = [], []
        elif tag in ("td", "th") and self._row_text is not None:
            self._cell, self._cell_attrs = [], {}
        elif tag in ("a", "input", "button") and self._cell_attrs is not None:
            for k, v in attrs:
                if k in ("onclick", "href") and v:
                    self._cell_attrs[k] = v

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row_text.append(" ".join("".join(self._cell).split()))
            self._row_attrs.append(self._cell_attrs or {})
            self._cell = self._cell_attrs = None
        elif tag == "tr" and self._row_text is not None:
            if any(self._row_text):
                self.rows.append((self._row_text, self._row_attrs))
            self._row_text = self._row_attrs = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def roc_to_iso(roc: str) -> str | None:
    """'115/01/02' -> '2026-01-02'. Mengembalikan None kalau bentuknya lain."""
    m = re.match(r"^\s*(\d{2,3})/(\d{1,2})/(\d{1,2})\s*$", roc)
    if not m:
        return None
    y, mo, d = (int(g) for g in m.groups())
    try:
        return f"{y + 1911:04d}-{mo:02d}-{d:02d}"
    except ValueError:
        return None


def detail_url(host: str, params: dict) -> str | None:
    """Bangun alamat permanen satu pengumuman dari parameter tombolnya."""
    needed = ("seq_no", "spoke_date", "spoke_time")
    if not all(params.get(k) for k in needed):
        return None
    q = {"step": "2", "firstin": "1", "TYPEK": params.get("TYPEK", "all")}
    for k in ("co_id", "seq_no", "spoke_date", "spoke_time", "skey"):
        if params.get(k):
            q[k] = params[k]
    pairs = "&".join(f"{k}={v}" for k, v in q.items())
    return f"{host}/mops/web/ajax_t05st01?{pairs}"


def host_for(code: str, fallback: str = DEFAULT_HOST) -> str:
    """Host yang benar-benar melayani emiten ini, menurut laporan spike."""
    try:
        with open(REPORT, encoding="utf-8") as f:
            for r in json.load(f).get("results", []):
                if r.get("code") == code and r.get("host_used"):
                    return r["host_used"]
    except (OSError, ValueError, KeyError):
        pass
    return fallback


def is_header(cells: list[str]) -> bool:
    joined = "".join(cells)
    return sum(m in joined for m in HEADER_MARKERS) >= 2


# --------------------------------------------------------------------------

def parse_file(path: str) -> tuple[list[dict], dict]:
    with open(path, encoding="utf-8") as f:
        html = f.read()

    h = RowHarvester()
    try:
        h.feed(html)
    except Exception:
        pass                                # HTML MOPS tidak selalu rapi

    stat = {"rows_seen": len(h.rows), "kept": 0, "with_link": 0, "sample_cell": None}
    out: list[dict] = []
    fetched_at = datetime.fromtimestamp(os.path.getmtime(path), timezone.utc).isoformat(timespec="seconds")

    for cells, attrs in h.rows:
        if len(cells) < 5 or is_header(cells):
            continue
        code, name, d_roc, t, subject = (c.strip() for c in cells[:5])
        if not re.fullmatch(r"\d{4}[A-Z]?", code):
            continue                        # bukan baris data
        iso = roc_to_iso(d_roc)
        if not iso:
            continue

        params = {"co_id": code}
        for a in attrs:
            src = a.get("onclick") or a.get("href") or ""
            for k, v in VALUE_ASSIGN.findall(src):
                params[k] = v
            if stat["sample_cell"] is None and src:
                stat["sample_cell"] = src[:300]

        url = detail_url(host_for(code), params)
        if url:
            stat["with_link"] += 1

        out.append({
            "code": code,
            "name": name,
            "date": iso,
            "date_roc": d_roc,
            "time": t,
            "subject": subject,
            "detail_url": url,
            "fetched_at": fetched_at,
            "raw_file": os.path.relpath(path, ROOT),
        })
        stat["kept"] += 1

    return out, stat


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="hanya tanggal >= ini, format YYYY-MM-DD")
    ap.add_argument("--code", help="hanya satu kode emiten")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.html")))
    if not files:
        print(f"Tidak ada berkas di {os.path.relpath(RAW_DIR, ROOT)}.")
        print("Jalankan dulu: python3 scripts/spike_mops.py")
        return 1

    print(f"Membaca {len(files)} berkas dari data/raw/\n")

    records: list[dict] = []
    no_link_files: list[str] = []
    sample = None

    for path in files:
        rows, stat = parse_file(path)
        base = os.path.basename(path)
        print(f"  · {base}")
        print(f"      {stat['rows_seen']} baris tabel → {stat['kept']} pengumuman, "
              f"{stat['with_link']} punya alamat sendiri")
        if stat["kept"] and not stat["with_link"]:
            no_link_files.append(base)
            sample = sample or stat["sample_cell"]
        records.extend(rows)

    if args.code:
        records = [r for r in records if r["code"] == args.code]
    if args.since:
        records = [r for r in records if r["date"] >= args.since]

    # Terbaru di atas — urutan yang dibutuhkan agen pemantau.
    records.sort(key=lambda r: (r["date"], r["time"]), reverse=True)

    os.makedirs(PARSED_DIR, exist_ok=True)
    jpath = os.path.join(PARSED_DIR, "announcements.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    cpath = os.path.join(PARSED_DIR, "announcements.csv")
    with open(cpath, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]) if records else
                           ["code", "name", "date", "time", "subject", "detail_url"])
        w.writeheader()
        w.writerows(records)

    linked = sum(1 for r in records if r["detail_url"])
    codes = sorted({r["code"] for r in records})
    dates = [r["date"] for r in records]

    print("\n" + "=" * 68)
    print(f"{len(records)} pengumuman dari {len(codes)} emiten: {', '.join(codes)}")
    if dates:
        print(f"Rentang tanggal : {min(dates)} … {max(dates)}")
    print(f"Punya alamat sitasi : {linked}/{len(records)}")
    print(f"\nTersimpan di {os.path.relpath(jpath, ROOT)} dan {os.path.relpath(cpath, ROOT)}")

    if records:
        r = records[0]
        print(f"\nContoh catatan terbaru:")
        print(f"  {r['date']} {r['time']}  [{r['code']}] {r['name']}")
        print(f"  {r['subject'][:70]}")
        print(f"  {r['detail_url'] or '(alamat belum terbaca)'}")

    if no_link_files:
        print(f"\n{len(no_link_files)} berkas tidak menghasilkan alamat sitasi.")
        print("  Bentuk tombolnya berbeda dari dugaan. Kirim potongan ini supaya")
        print("  polanya bisa diperbaiki — teks pengumumannya sendiri sudah aman:")
        if sample:
            print(f"\n  {sample}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
