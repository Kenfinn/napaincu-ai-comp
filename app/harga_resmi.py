"""Modul pengambil data harga harian resmi TWSE/TPEx dan indeks TAIEX.

Menggantikan ketergantungan pihak ketiga tidak resmi dengan endpoint resmi bursa:
- Saham TWSE: STOCK_DAY
- Saham TPEx: tradingStock
- Indeks TAIEX: MI_5MINS_HIST
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config, pasar

URL_TWSE_STOCK_DAY = (
    "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={bulan}01&stockNo={kode}&response=json"
)
URL_TAIEX_HIST = (
    "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={bulan}01&response=json"
)
URL_TPEX_TRADING_STOCK = (
    "https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={kode}&date={tahun}/{bulan}/01&response=json"
)

TTL_BULAN_BERJALAN = 12 * 3600  # 12 jam
JEDA_JARINGAN = 2.0

_kunci_jaringan = threading.Lock()
_waktu_terakhir_jaringan: float = 0.0


def _roc_ke_iso(roc_str: str) -> str | None:
    """Konversi tanggal kalender Minguo '113/10/01' atau '113-10-01' ke ISO '2024-10-01'."""
    if not roc_str or not isinstance(roc_str, str):
        return None
    pecah = re.split(r"[/.\-]", roc_str.strip())
    if len(pecah) != 3:
        return None
    try:
        th_roc, bln, tgl = int(pecah[0]), int(pecah[1]), int(pecah[2])
        th_masehi = th_roc + 1911
        return f"{th_masehi:04d}-{bln:02d}-{tgl:02d}"
    except (ValueError, TypeError):
        return None


def _bersihkan_angka(val: any) -> float | None:
    """Bersihkan koma ribuan dan parse ke float."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if float(val) > 0 else None
    s = str(val).replace(",", "").strip()
    if not s or s in ("--", "X", "null", "None"):
        return None
    try:
        f = float(s)
        return f if f > 0 else None
    except ValueError:
        return None


def _bulan_berjalan_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m")


def _dir_cache() -> Path:
    d = Path(config.DATA_DIR) / "harga_harian"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _baca_cache(nama_file: str, bulan: str) -> list[tuple[str, float]] | None:
    p = _dir_cache() / nama_file
    if not p.is_file():
        return None
    sekarang_bulan = _bulan_berjalan_utc()
    if bulan < sekarang_bulan:
        # Bulan yang sudah lewat disimpan permanen
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return [(str(x[0]), float(x[1])) for x in raw if len(x) >= 2]
        except Exception:
            return None
    else:
        # Bulan berjalan berumur maksimal 12 jam
        try:
            umur = time.time() - p.stat().st_mtime
            if umur < TTL_BULAN_BERJALAN:
                raw = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    return [(str(x[0]), float(x[1])) for x in raw if len(x) >= 2]
        except Exception:
            return None
    return None


def _simpan_cache(nama_file: str, data: list[tuple[str, float]]) -> None:
    p = _dir_cache() / nama_file
    try:
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[harga_resmi] gagal simpan cache {nama_file}: {e}", file=sys.stderr)


def _ambil_json(url: str) -> dict | None:
    """Ambil data JSON dari bursa dengan rate-limit minimal 2 detik."""
    global _waktu_terakhir_jaringan
    with _kunci_jaringan:
        now = time.monotonic()
        selisih = now - _waktu_terakhir_jaringan
        if selisih < JEDA_JARINGAN:
            time.sleep(JEDA_JARINGAN - selisih)
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": pasar.UA, "Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                teks = resp.read().decode("utf-8-sig", "replace")
            _waktu_terakhir_jaringan = time.monotonic()
            return json.loads(teks)
        except Exception as e:
            _waktu_terakhir_jaringan = time.monotonic()
            print(f"[harga_resmi] galat ambil {url}: {e}", file=sys.stderr)
            return None


def urai_twse(d: dict) -> list[tuple[str, float]]:
    """Urai isi respons STOCK_DAY TWSE menjadi [(tanggal_iso, close)]."""
    baris = (d or {}).get("data") or []
    hasil: list[tuple[str, float]] = []
    for r in baris:
        if not isinstance(r, list) or len(r) < 7:
            continue
        iso = _roc_ke_iso(r[0])
        close = _bersihkan_angka(r[6])
        if iso and close is not None:
            hasil.append((iso, close))
    hasil.sort(key=lambda x: x[0])
    return hasil


def urai_taiex(d: dict) -> list[tuple[str, float]]:
    """Urai isi respons MI_5MINS_HIST TAIEX menjadi [(tanggal_iso, close)]."""
    baris = (d or {}).get("data") or []
    hasil: list[tuple[str, float]] = []
    for r in baris:
        if not isinstance(r, list) or len(r) < 5:
            continue
        iso = _roc_ke_iso(r[0])
        close = _bersihkan_angka(r[4])
        if iso and close is not None:
            hasil.append((iso, close))
    hasil.sort(key=lambda x: x[0])
    return hasil


def urai_tpex(d: dict) -> list[tuple[str, float]]:
    """Urai isi respons tradingStock TPEx menjadi [(tanggal_iso, close)]."""
    tables = (d or {}).get("tables") or []
    baris = []
    if tables and isinstance(tables, list) and isinstance(tables[0], dict):
        baris = tables[0].get("data") or []
    if not baris:
        baris = (d or {}).get("data") or []
    hasil: list[tuple[str, float]] = []
    for r in baris:
        if not isinstance(r, list) or len(r) < 7:
            continue
        iso = _roc_ke_iso(r[0])
        close = _bersihkan_angka(r[6])
        if iso and close is not None:
            hasil.append((iso, close))
    hasil.sort(key=lambda x: x[0])
    return hasil


def harian(kode: str, bursa: str = "", bulan: str = "") -> list[tuple[str, float]]:
    """Ambil data harga penutupan harian saham satu bulan dari bursa resmi.

    Args:
        kode: kode emiten (mis. '2330')
        bursa: 'TWSE' atau 'TPEx'. Bila kosong, dicek dari pasar.harga(kode).
        bulan: 'YYYYMM' (mis. '202410')
    """
    kode = str(kode).strip().upper()
    bulan = str(bulan).strip()
    if len(bulan) != 6 or not bulan.isdigit():
        return []

    bursa_norm = (bursa or "").strip().upper()
    if bursa_norm not in ("TWSE", "TPEX"):
        try:
            h = pasar.harga(kode)
            bursa_norm = str(h.get("bursa") or "TWSE").upper()
        except Exception:
            bursa_norm = "TWSE"

    nama_bursa = "TWSE" if bursa_norm == "TWSE" else "TPEx"
    nama_cache = f"{nama_bursa}-{kode}-{bulan}.json"
    cached = _baca_cache(nama_cache, bulan)
    if cached is not None:
        return cached

    if nama_bursa == "TWSE":
        url = URL_TWSE_STOCK_DAY.format(bulan=bulan, kode=kode)
        d = _ambil_json(url)
        hasil = urai_twse(d) if d else []
    else:
        tahun_str = bulan[:4]
        bln_str = bulan[4:]
        url = URL_TPEX_TRADING_STOCK.format(kode=kode, tahun=tahun_str, bulan=bln_str)
        d = _ambil_json(url)
        hasil = urai_tpex(d) if d else []

    if hasil:
        _simpan_cache(nama_cache, hasil)
    return hasil


def taiex(bulan: str = "") -> list[tuple[str, float]]:
    """Ambil data indeks penutupan harian TAIEX satu bulan dari TWSE resmi.

    Args:
        bulan: 'YYYYMM' (mis. '202410')
    """
    bulan = str(bulan).strip()
    if len(bulan) != 6 or not bulan.isdigit():
        return []

    nama_cache = f"TAIEX-{bulan}.json"
    cached = _baca_cache(nama_cache, bulan)
    if cached is not None:
        return cached

    url = URL_TAIEX_HIST.format(bulan=bulan)
    d = _ambil_json(url)
    hasil = urai_taiex(d) if d else []
    if hasil:
        _simpan_cache(nama_cache, hasil)
    return hasil
