#!/usr/bin/env python3
"""
Tarik isi lengkap pengumuman MOPS, bukan sekadar judulnya.

`parse_mops.py` menghasilkan daftar pengumuman beserta alamatnya. Skrip ini membuka
alamat-alamat itu dan mengambil isinya: nomor pasal, tanggal kejadian, dan butir-butir
bernomor yang labelnya sudah dibakukan regulator.

Dua hal yang disengaja:

1. TIDAK menarik semuanya. Pilih dengan --limit / --code / --since / --clause. Agen
   yang baik memutuskan mana yang layak dibuka — bukan membuka semuanya. Ini juga
   yang membedakannya dari scraper biasa.

2. TIDAK menyimpan data pribadi. Halaman MOPS memuat nama, jabatan, dan telepon juru
   bicara. Aturan lomba Pasal 14.1 mewajibkan minimisasi data pribadi, jadi ketiga
   field itu dibuang sebelum apa pun ditulis ke disk.

Pakai:
    python3 scripts/fetch_details.py --limit 10            # 10 terbaru
    python3 scripts/fetch_details.py --code 2881 --limit 5
    python3 scripts/fetch_details.py --since 2026-09-01
    python3 scripts/fetch_details.py --clause 24           # hanya pasal tertentu

Keluaran:
    data/parsed/details.json   isi pengumuman, siap jadi masukan analisis

Tanpa dependensi eksternal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
PARSED_DIR = os.path.join(ROOT, "data", "parsed")
LIST_FILE = os.path.join(PARSED_DIR, "announcements.json")
OUT_FILE = os.path.join(PARSED_DIR, "details.json")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
TIMEOUT = 30
POLITE_DELAY = 2.5                    # detik — jangan diturunkan

BLOCK_MARKERS = ("FOR SECURITY REASONS", "因為安全性考量")

# Label yang diambil. Sengaja tidak memuat 發言人 / 發言人職稱 / 發言人電話 —
# itu data pribadi, dan minimisasi data adalah kewajiban, bukan pilihan.
WANTED = {
    "序號": "seq_no",
    "發言日期": "announce_date_roc",
    "發言時間": "announce_time",
    "主旨": "subject",
    "符合條款": "clause_raw",
    "事實發生日": "fact_date_roc",
}
PII_LABELS = ("發言人", "發言人職稱", "發言人電話")

# Butir isi berbentuk "1.判決法院……:" lalu nilainya di baris berikutnya.
ITEM_SPLIT = re.compile(r"(?m)^\s*(\d{1,2})\.\s*")


class CellHarvester(HTMLParser):
    """Ambil seluruh sel tabel berurutan, apa adanya."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cells: list[str] = []
        self._buf: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th"):
            self._buf = []
        elif tag in ("br", "p", "div") and self._buf is not None:
            self._buf.append("\n")      # MOPS memisah baris dengan <br>, bukan <br/>

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._buf is not None:
            text = "".join(self._buf)
            text = re.sub(r"[ \t　]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            self.cells.append(text)
            self._buf = None

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)

    def handle_startendtag(self, tag, attrs):
        if tag == "br" and self._buf is not None:
            self._buf.append("\n")


def roc_to_iso(roc: str) -> str | None:
    m = re.search(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", roc or "")
    if not m:
        return None
    y, mo, d = (int(g) for g in m.groups())
    return f"{y + 1911:04d}-{mo:02d}-{d:02d}"


def clause_number(raw: str) -> int | None:
    """'第 24 款' -> 24. Nomor pasal inilah jenis kejadiannya, menurut regulator."""
    m = re.search(r"(\d+)", raw or "")
    return int(m.group(1)) if m else None


def split_items(body: str) -> list[dict]:
    """Pecah butir bernomor jadi pasangan label→isi — fungsi yang sama dengan penarik OpenAPI.

    Satu pengurai untuk dua sumber, supaya label butir (yang dicocokkan pemeriksa)
    tidak bergantung pada jalur data mana yang dipakai.
    """
    from app.tarik import urai_butir
    return urai_butir(body)


def _split_items_lama(body: str) -> list[dict]:
    """Pengurai lama — disimpan untuk pembanding, tidak dipakai."""
    parts = ITEM_SPLIT.split(body)
    items: list[dict] = []
    for i in range(1, len(parts) - 1, 2):
        no, chunk = parts[i], parts[i + 1].strip()
        sep = re.search(r"[:：]", chunk)
        label, value = (chunk[:sep.start()], chunk[sep.end():]) if sep else (chunk, "")
        items.append({
            "no": int(no),
            "label": " ".join(label.split()),
            "value": " ".join(value.split()),
        })
    return items


def parse_detail(html: str) -> dict:
    h = CellHarvester()
    try:
        h.feed(html)
    except Exception:
        pass

    cells = h.cells
    rec: dict = {"dropped_pii": []}

    # Halaman ini berpasangan label→nilai di sel-sel berurutan.
    for i, c in enumerate(cells[:-1]):
        key = c.strip()
        if key in WANTED:
            rec[WANTED[key]] = cells[i + 1].strip()
        elif key in PII_LABELS and key not in rec["dropped_pii"]:
            rec["dropped_pii"].append(key)      # dicatat dibuang, isinya tidak disimpan

    # Isi pengumuman = sel terpanjang yang memuat butir bernomor.
    body = ""
    for c in cells:
        if len(c) > len(body) and ITEM_SPLIT.search(c):
            body = c
    rec["items"] = split_items(body)
    rec["body_chars"] = len(body)

    rec["clause"] = clause_number(rec.get("clause_raw", ""))
    for src, dst in (("announce_date_roc", "announce_date"), ("fact_date_roc", "fact_date")):
        if rec.get(src):
            rec[dst] = roc_to_iso(rec[src])
    return rec


def fetch(url: str) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as r:
            raw = r.read()
            enc = r.headers.get_content_charset() or ""
            for cand in ([enc] if enc else []) + ["utf-8", "big5", "cp950"]:
                try:
                    return raw.decode(cand), ""
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as e:
        return "", f"HTTPError {e.code}"
    except Exception as e:
        return "", f"{type(e).__name__}: {e}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=10, help="berapa pengumuman (bawaan 10)")
    ap.add_argument("--code", help="satu emiten saja")
    ap.add_argument("--since", help="tanggal >= YYYY-MM-DD")
    ap.add_argument("--clause", type=int, help="hanya pasal tertentu, mis. 24")
    ap.add_argument("--all", action="store_true", help="abaikan --limit (hati-hati: lambat)")
    args = ap.parse_args()

    if not os.path.exists(LIST_FILE):
        print(f"Belum ada {os.path.relpath(LIST_FILE, ROOT)}.")
        print("Jalankan dulu: python3 scripts/parse_mops.py")
        return 1

    with open(LIST_FILE, encoding="utf-8") as f:
        listing = json.load(f)

    picked = [a for a in listing if a.get("detail_url")]
    if args.code:
        picked = [a for a in picked if a["code"] == args.code]
    if args.since:
        picked = [a for a in picked if a["date"] >= args.since]
    if not args.all:
        picked = picked[:args.limit]

    if not picked:
        print("Tidak ada pengumuman yang cocok dengan saringan itu.")
        return 1

    print(f"Menarik isi {len(picked)} pengumuman "
          f"(~{len(picked) * POLITE_DELAY / 60:.1f} menit)\n")

    out, failed, skipped = [], [], 0
    for i, a in enumerate(picked, 1):
        print(f"  [{i}/{len(picked)}] {a['date']} [{a['code']}] {a['subject'][:44]}… ",
              end="", flush=True)

        html, err = fetch(a["detail_url"])
        time.sleep(POLITE_DELAY)

        if err:
            print(f"GAGAL — {err}")
            failed.append({"url": a["detail_url"], "error": err})
            continue
        if any(m in html[:3000] for m in BLOCK_MARKERS):
            print("DIBLOKIR")
            failed.append({"url": a["detail_url"], "error": "diblokir"})
            continue

        rec = parse_detail(html)
        if args.clause and rec.get("clause") != args.clause:
            skipped += 1
            print(f"lewati (pasal {rec.get('clause')})")
            continue

        rec.update({
            "code": a["code"],
            "name": a["name"],
            "date": a["date"],
            "time": a["time"],
            "source_url": a["detail_url"],
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        out.append(rec)
        print(f"OK — pasal {rec.get('clause')}, {len(rec['items'])} butir")

    # Digabung, bukan ditimpa: menarik 2330 lalu 2454 dalam dua kali jalan tidak
    # menghapus hasil yang pertama. Duplikat (termasuk dari OpenAPI) dilewati.
    from app.tarik import gabung
    for r in out:
        r.setdefault("sumber_data", "MOPS t05st01 (ditarik dari jaringan Taiwan)")
    # Indeks ke berkas terpisah: announcements.json di laptop adalah daftar MOPS yang
    # menjadi masukan skrip ini, dan tidak boleh tertimpa.
    baru = gabung(out, OUT_FILE, os.path.join(PARSED_DIR, "details_index.json"))
    print(f"\n{baru} pengumuman baru digabung ke {os.path.relpath(OUT_FILE, ROOT)}")

    clauses: dict[int | None, int] = {}
    for r in out:
        clauses[r.get("clause")] = clauses.get(r.get("clause"), 0) + 1

    print("\n" + "=" * 68)
    print(f"{len(out)} pengumuman terambil isinya"
          + (f", {skipped} dilewati saringan pasal" if skipped else "")
          + (f", {len(failed)} gagal" if failed else ""))
    if clauses:
        ranked = sorted(clauses.items(), key=lambda kv: -kv[1])
        print("Sebaran pasal : " + ", ".join(f"第{k}款 ×{v}" for k, v in ranked))
    dropped = {p for r in out for p in r.get("dropped_pii", [])}
    if dropped:
        print(f"Data pribadi dibuang : {', '.join(sorted(dropped))} — tidak ditulis ke disk")
    print(f"\nTersimpan di {os.path.relpath(OUT_FILE, ROOT)}")

    if out:
        r = out[0]
        print(f"\nContoh:")
        print(f"  [{r['code']}] {r['name']} · {r['date']} · 第{r.get('clause')}款")
        print(f"  {r.get('subject', '')[:64]}")
        for it in r["items"][:3]:
            print(f"    {it['no']}. {it['label'][:38]} → {it['value'][:40]}")

    if not out and not skipped:
        print("\nTidak ada yang berhasil. Cek koneksi dan pastikan masih di jaringan kampus.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
