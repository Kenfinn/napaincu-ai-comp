#!/usr/bin/env python3
"""
Uji 72 jam: tarik pengumuman material (重大訊息) dari MOPS untuk beberapa emiten.

Skrip ini SENGAJA tidak mengasumsikan struktur tabel MOPS. Tugasnya menemukan apa
yang sebenarnya dikembalikan server, menyimpan bukti mentahnya, dan mencetak laporan
yang bisa dibaca manusia. Parser yang presisi ditulis belakangan, setelah kita tahu
bentuk aslinya.

Kenapa begitu: MOPS memblokir IP luar Taiwan dengan halaman HTML — dan tetap
mengembalikan HTTP 200. Jadi sebelum menulis pipeline, yang perlu dipastikan dulu
adalah "apakah dari jaringan ini datanya benar-benar sampai, dan bentuknya seperti apa".

Pakai:
    python3 scripts/spike_mops.py                      # 5 emiten bawaan, tahun berjalan
    python3 scripts/spike_mops.py --codes 2330 2317    # emiten tertentu
    python3 scripts/spike_mops.py --year 114           # tahun ROC lain (2025 = 114)
    python3 scripts/spike_mops.py --report             # ringkasan singkat untuk dibagikan

Keluaran:
    data/raw/<kode>_<waktu>.html   HTML mentah — ini bukti sumber, jangan dihapus
    data/parsed/<kode>.json        hasil ekstraksi + URL sumber + waktu pengambilan
    data/spike-report.json         ringkasan seluruh percobaan

Tanpa dependensi eksternal — cukup Python 3.9 ke atas.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

# Lima emiten dari sektor berbeda, semuanya kapitalisasi besar dengan laporan lengkap.
# 2881 sengaja dipilih karena multi-lini bisnis — berguna kalau SOTP jadi dikerjakan.
DEFAULT_CODES = [
    ("2330", "TSMC — semikonduktor"),
    ("2317", "Hon Hai — manufaktur elektronik"),
    ("2881", "Fubon Financial — keuangan, multi-lini"),
    ("1301", "Formosa Plastics — petrokimia"),
    ("2412", "Chunghwa Telecom — telekomunikasi"),
]

# Tiga domain melayani isi yang sama. Kalau satu gagal, coba berikutnya.
HOSTS = [
    "https://mops.twse.com.tw",
    "https://mopsov.twse.com.tw",
    "https://mopsc.twse.com.tw",
]

ENDPOINT = "/mops/web/ajax_t05st01"      # 重大訊息 per perusahaan

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 30
POLITE_DELAY = 2.0                        # detik antar request — jangan diturunkan

BLOCK_MARKERS = ("FOR SECURITY REASONS", "因為安全性考量")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
PARSED_DIR = os.path.join(ROOT, "data", "parsed")


# --------------------------------------------------------------------------
# Pengambilan
# --------------------------------------------------------------------------

def roc_year(gregorian: int | None = None) -> int:
    """Tahun kalender ROC (民國). 2026 -> 115."""
    return (gregorian or datetime.now().year) - 1911


def fetch(url: str, form: dict) -> tuple[int | None, str, str, str]:
    """POST form ke url. Mengembalikan (status, teks, encoding, catatan error)."""
    body = urllib.parse.urlencode(form).encode("ascii")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Referer": url.rsplit("/", 1)[0] + "/t05st01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as r:
            raw = r.read()
            enc = r.headers.get_content_charset() or ""
            for candidate in ([enc] if enc else []) + ["utf-8", "big5", "cp950"]:
                try:
                    return r.status, raw.decode(candidate), candidate, ""
                except (UnicodeDecodeError, LookupError):
                    continue
            return r.status, raw.decode("utf-8", "replace"), "utf-8/replace", ""
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:4000].decode("utf-8", "replace"), "", f"HTTPError {e.code}"
    except Exception as e:
        return None, "", "", f"{type(e).__name__}: {e}"


def is_blocked(text: str) -> bool:
    return any(m in text[:3000] for m in BLOCK_MARKERS)


# --------------------------------------------------------------------------
# Ekstraksi tabel — generik, tidak mengasumsikan kolom apa pun
# --------------------------------------------------------------------------

class TableHarvester(HTMLParser):
    """Kumpulkan semua <table> jadi list-of-rows-of-cells, apa adanya."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._tbl: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._tbl = []
        elif tag == "tr" and self._tbl is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._tbl is not None:
            if any(c for c in self._row):
                self._tbl.append(self._row)
            self._row = None
        elif tag == "table":
            if self._depth == 1 and self._tbl is not None:
                if self._tbl:
                    self.tables.append(self._tbl)
                self._tbl = None
            self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def harvest(text: str) -> list[list[list[str]]]:
    h = TableHarvester()
    try:
        h.feed(text)
    except Exception:
        pass                                   # HTML MOPS sering tidak rapi; ambil yang sempat terkumpul
    return h.tables


def pick_announcement_table(tables: list[list[list[str]]]) -> tuple[int, list[list[str]]] | None:
    """Tabel pengumuman adalah yang punya baris terbanyak dengan >= 3 kolom."""
    best, best_i = None, -1
    for i, t in enumerate(tables):
        wide = [r for r in t if len(r) >= 3]
        if len(wide) >= 2 and (best is None or len(wide) > len(best)):
            best, best_i = wide, i
    return (best_i, best) if best else None


# --------------------------------------------------------------------------
# Alur utama
# --------------------------------------------------------------------------

def probe_one(code: str, label: str, year: int, verbose: bool) -> dict:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result = {
        "code": code,
        "label": label,
        "roc_year": year,
        "fetched_at": stamp,
        "ok": False,
        "host_used": None,
        "status": None,
        "encoding": None,
        "bytes": 0,
        "tables_found": 0,
        "rows_found": 0,
        "raw_file": None,
        "note": "",
    }

    for host in HOSTS:
        url = host + ENDPOINT
        form = {"encodeURIComponent": "1", "step": "1", "firstin": "1",
                "off": "1", "keyword4": "", "code1": "", "TYPEK2": "",
                "checkbtn": "", "queryName": "co_id", "inpuType": "co_id",
                "TYPEK": "all", "co_id": code, "year": str(year)}

        status, text, enc, err = fetch(url, form)
        time.sleep(POLITE_DELAY)

        if err and status is None:
            result["note"] = f"{host}: {err}"
            if verbose:
                print(f"      {host} → {err}")
            continue

        if is_blocked(text):
            result["note"] = "DIBLOKIR — halaman security TWSE (tetap HTTP 200)"
            if verbose:
                print(f"      {host} → diblokir")
            continue

        # Berhasil sampai. Simpan bukti mentahnya lebih dulu, apa pun isinya.
        os.makedirs(RAW_DIR, exist_ok=True)
        fname = f"{code}_{stamp.replace(':', '').replace('-', '')}.html"
        path = os.path.join(RAW_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        tables = harvest(text)
        picked = pick_announcement_table(tables)

        result.update({
            "ok": bool(picked),
            "host_used": host,
            "status": status,
            "encoding": enc,
            "bytes": len(text.encode("utf-8")),
            "tables_found": len(tables),
            "rows_found": len(picked[1]) if picked else 0,
            "raw_file": os.path.relpath(path, ROOT),
            "source_url": url,
        })

        if picked:
            idx, rows = picked
            os.makedirs(PARSED_DIR, exist_ok=True)
            with open(os.path.join(PARSED_DIR, f"{code}.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "code": code,
                    "label": label,
                    "source_url": url,
                    "fetched_at": stamp,
                    "roc_year": year,
                    "table_index": idx,
                    "header_guess": rows[0],
                    "rows": rows[1:],
                }, f, ensure_ascii=False, indent=2)
            result["header_guess"] = rows[0]
            result["sample_row"] = rows[1] if len(rows) > 1 else []
        else:
            result["note"] = (
                f"terhubung, tapi tidak menemukan tabel pengumuman "
                f"({len(tables)} tabel ditemukan) — cek {result['raw_file']}"
            )
        return result

    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--codes", nargs="*", help="kode emiten, mis. 2330 2317")
    ap.add_argument("--year", type=int, default=None, help="tahun ROC (2026 = 115)")
    ap.add_argument("--report", action="store_true", help="cetak ringkasan singkat saja")
    ap.add_argument("-q", "--quiet", action="store_true", help="kurangi keluaran")
    args = ap.parse_args()

    year = args.year or roc_year()
    targets = ([(c, "") for c in args.codes] if args.codes else DEFAULT_CODES)
    verbose = not (args.quiet or args.report)

    print(f"Menarik 重大訊息 dari MOPS · tahun ROC {year} · {len(targets)} emiten\n")

    results = []
    for code, label in targets:
        print(f"  · {code} {label}".rstrip() + " … ", end="", flush=True)
        r = probe_one(code, label, year, verbose)
        results.append(r)
        if r["ok"]:
            print(f"OK — {r['rows_found']} baris")
            if verbose and r.get("header_guess"):
                print(f"      kolom  : {r['header_guess']}")
                print(f"      contoh : {r.get('sample_row', [])}")
                print(f"      mentah : {r['raw_file']}")
        else:
            print("GAGAL")
            print(f"      {r['note']}")

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    summary_path = os.path.join(ROOT, "data", "spike-report.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "roc_year": year,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    ok = [r for r in results if r["ok"]]
    total_rows = sum(r["rows_found"] for r in ok)
    blocked = [r for r in results if "DIBLOKIR" in r["note"]]

    print("\n" + "=" * 68)
    print(f"Hasil: {len(ok)}/{len(results)} emiten berhasil · {total_rows} baris pengumuman")
    print(f"Ringkasan tersimpan di {os.path.relpath(summary_path, ROOT)}")

    if blocked:
        print(f"\n{len(blocked)} emiten diblokir berdasarkan IP.")
        print("  Ini bukan kesalahan kode. Pastikan skrip dijalankan dari jaringan")
        print("  kampus di Taiwan, dan VPN ke luar negeri dimatikan.")

    if total_rows >= 20:
        print("\n>>> LOLOS. Target uji 72 jam tercapai (>= 20 pengumuman).")
        print("    Kabari tim, dan kunci track SYSTEX.")
    elif ok:
        print(f"\n>>> SEBAGIAN. {total_rows} baris terambil, target 20.")
        print("    Coba --year tahun sebelumnya, atau tambah emiten lain.")
    else:
        print("\n>>> BELUM LOLOS. Tidak ada data yang terambil.")
        print("    Cek dulu: jaringan kampus? VPN mati? Lalu jalankan probe_sources.py.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
