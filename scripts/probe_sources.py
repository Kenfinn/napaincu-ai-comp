#!/usr/bin/env python3
"""
Probe ketersediaan sumber data MOPS / TWSE / TPEx dari jaringan tempat skrip ini dijalankan.

Dipakai untuk uji 72 jam: sebelum menulis pipeline, pastikan dulu sumber mana yang
benar-benar bisa diakses dari jaringan kalian.

Kenapa skrip ini tidak cuma mengecek status code:
    TWSE dan TPEx memblokir IP luar Taiwan / datacenter dengan halaman HTML berisi
    "FOR SECURITY REASONS, THIS PAGE CAN NOT BE ACCESSED" — tetapi mengembalikan
    HTTP 200. Pipeline yang hanya membaca status code akan mencatatnya sebagai sukses
    dan menyimpan sampah. Jadi setiap probe di sini memvalidasi BENTUK respons.

Pakai:
    python3 scripts/probe_sources.py
    python3 scripts/probe_sources.py --json     # keluaran mesin, untuk dicatat di lampiran deck

Tidak butuh dependensi eksternal — hanya pustaka standar.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Callable

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 25

# Penanda halaman blokir TWSE. Muncul dengan HTTP 200, jadi harus dideteksi dari isi.
BLOCK_MARKERS = ("FOR SECURITY REASONS", "因為安全性考量")


@dataclass
class Result:
    name: str
    url: str
    ok: bool
    status: int | None
    bytes: int
    detail: str


def fetch(url: str, data: bytes | None = None) -> tuple[int | None, bytes, str]:
    """Ambil URL. Mengembalikan (status, body, catatan error)."""
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
            **({"Content-Type": "application/x-www-form-urlencoded"} if data else {}),
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, r.read(), ""
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:4000], f"HTTPError {e.code}"
    except Exception as e:  # timeout, DNS, TLS, koneksi ditolak
        return None, b"", f"{type(e).__name__}: {e}"


def looks_blocked(body: bytes) -> bool:
    head = body[:2000].decode("utf-8", "ignore")
    return any(m in head for m in BLOCK_MARKERS)


def probe(name: str, url: str, check: Callable[[bytes], str], data: bytes | None = None) -> Result:
    status, body, err = fetch(url, data)

    if err and status is None:
        if "CERTIFICATE_VERIFY_FAILED" in err:
            return Result(name, url, False, None, 0,
                          "kegagalan TLS di mesin ini (trust store lokal / proxy), "
                          "bukan blokir dari server — coba dari mesin lain sebelum menyimpulkan")
        return Result(name, url, False, None, 0, f"tidak tersambung — {err}")
    if looks_blocked(body):
        return Result(name, url, False, status, len(body),
                      "DIBLOKIR dari IP ini (halaman security TWSE, tetap HTTP 200) "
                      "— coba dari jaringan kampus di Taiwan")
    detail = check(body)
    return Result(name, url, detail.startswith("ok"), status, len(body), detail)


# ---------- validator bentuk respons ----------

def expect_json_list(min_items: int = 1) -> Callable[[bytes], str]:
    def _c(body: bytes) -> str:
        try:
            d = json.loads(body)
        except Exception:
            return f"bukan JSON (kemungkinan HTML) — {len(body)} byte"
        items = d if isinstance(d, list) else d.get("data", d)
        if isinstance(items, list) and len(items) >= min_items:
            return f"ok — {len(items)} baris, contoh kunci: {list(items[0])[:5]}"
        return f"JSON valid tapi bentuknya tak terduga: {str(d)[:120]}"
    return _c


def expect_html_table(body: bytes) -> str:
    text = body.decode("utf-8", "ignore")
    n = text.lower().count("<table")
    if n:
        return f"ok — {n} tabel HTML ditemukan ({len(body)} byte), siap di-parse"
    return f"tidak ada <table> dalam respons ({len(body)} byte)"


# ---------- daftar sumber ----------

PROBES: list[tuple[str, Callable[[], Result]]] = [
    ("TWSE OpenAPI — harga harian semua saham", lambda: probe(
        "TWSE OpenAPI — harga harian semua saham",
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
        expect_json_list(100))),

    ("TWSE OpenAPI — daftar endpoint (swagger)", lambda: probe(
        "TWSE OpenAPI — daftar endpoint (swagger)",
        "https://openapi.twse.com.tw/v1/swagger.json",
        lambda b: ("ok — " + str(len(json.loads(b).get("paths", {}))) + " endpoint tersedia")
        if b[:1] == b"{" else "bukan JSON — kemungkinan diblokir")),

    ("TPEx OpenAPI — harga penutupan OTC", lambda: probe(
        "TPEx OpenAPI — harga penutupan OTC",
        "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes",
        expect_json_list(50))),

    ("MOPS — halaman indeks", lambda: probe(
        "MOPS — halaman indeks",
        "https://mops.twse.com.tw/mops/web/index",
        lambda b: "ok — halaman termuat" if len(b) > 2000 else f"respons terlalu pendek ({len(b)} byte)")),

    ("MOPS — laba rugi komprehensif (ajax_t163sb04)", lambda: probe(
        "MOPS — laba rugi komprehensif (ajax_t163sb04)",
        "https://mops.twse.com.tw/mops/web/ajax_t163sb04",
        expect_html_table,
        data=b"encodeURIComponent=1&step=1&firstin=1&off=1&TYPEK=sii&year=114&season=2")),

    ("FinMind — daftar saham Taiwan (agregator)", lambda: probe(
        "FinMind — daftar saham Taiwan (agregator)",
        "https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockInfo",
        expect_json_list(100))),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="keluarkan hasil sebagai JSON")
    args = ap.parse_args()

    results: list[Result] = []
    if not args.json:
        print("Menguji akses sumber data dari jaringan ini…\n")

    for label, run in PROBES:
        if not args.json:
            print(f"  · {label} … ", end="", flush=True)
        r = run()
        results.append(r)
        if not args.json:
            print("OK" if r.ok else "GAGAL")
            print(f"      {r.detail}")
        time.sleep(0.6)  # sopan: jangan membanjiri server publik

    if args.json:
        print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
        return 0

    ok = [r for r in results if r.ok]
    print(f"\n{'='*68}\nHasil: {len(ok)} dari {len(results)} sumber bisa diakses dari jaringan ini.")

    blocked = [r for r in results if "DIBLOKIR" in r.detail]
    if blocked:
        print("\nDiblokir berdasarkan IP (bukan kesalahan kode kalian):")
        for r in blocked:
            print(f"  - {r.name}")
        print("\n  Jalankan ulang dari jaringan kampus di Taiwan sebelum menyimpulkan")
        print("  bahwa sumbernya tidak bisa dipakai. Kalau dari kampus pun tetap gagal,")
        print("  barulah pertimbangkan pindah track.")

    if not ok:
        print("\nTidak ada sumber yang bisa diakses. Periksa koneksi atau proxy dulu.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
