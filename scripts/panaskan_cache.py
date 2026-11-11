#!/usr/bin/env python3
"""Pemanasan cache valuasi otomatis, profil, dan harga pasar untuk persiapan demo.

Menyiapkan data emiten-emiten terbesar agar saat juri membuka halaman saham atau
tab Valuation, seluruh data tampil instan dari cache disk lokal.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# 30 emiten terbesar TWSE berdasarkan kapitalisasi pasar (sumber: TWSE Market Capitalization ranking 2026 / bobot TAIEX)
TOP_30_TWSE = [
    "2330",  # TSMC / 台積電
    "2317",  # Hon Hai Precision (Foxconn) / 鴻海
    "2454",  # MediaTek / 聯發科
    "2308",  # Delta Electronics / 台達電
    "2382",  # Quanta Computer / 廣達
    "2881",  # Fubon Financial / 富邦金
    "2882",  # Cathay Financial / 國泰金
    "2412",  # Chunghwa Telecom / 中華電
    "2891",  # CTBC Financial / 中信金
    "2603",  # Evergreen Marine / 長榮
    "2357",  # Asustek / 華碩
    "3711",  # ASE Technology / 日月光投控
    "2886",  # Mega Financial / 兆豐金
    "2884",  # E.SUN Financial / 玉山金
    "2303",  # UMC / 聯電
    "3231",  # Wistron / 緯創
    "2892",  # First Financial / 第一金
    "2885",  # Yuanta Financial / 元大金
    "1301",  # Formosa Plastics / 台塑
    "1303",  # Nan Ya Plastics / 南亞
    "2002",  # China Steel / 中鋼
    "2880",  # Hua Nan Financial / 華南金
    "2887",  # Taishin Financial / 台新金
    "6669",  # Wiwynn / 緯穎
    "2379",  # Realtek / 瑞昱
    "3008",  # Largan Precision / 大立光
    "2890",  # Sinopac Financial / 永豐金
    "2345",  # Accton / 智邦
    "1216",  # Uni-President / 統一
    "2912",  # President Chain Store / 統一超
]


def tentukan_daftar_kode(kode_args: list[str] | None, top_n: int = 30) -> list[str]:
    """Pilih daftar kode: argumen --kode mengalahkan --top."""
    if kode_args:
        hasil = []
        for k in kode_args:
            k_bersih = str(k).strip()
            if k_bersih and k_bersih not in hasil:
                hasil.append(k_bersih)
        return hasil
    top_n = max(1, min(top_n, len(TOP_30_TWSE)))
    return TOP_30_TWSE[:top_n]


def panaskan_satu(kode: str, paksa: bool = False, jeda: float = 0.5) -> dict:
    """Panaskan profil, harga, dan valuasi otomatis (termasuk menunggu beta resmi)."""
    from app import pasar, valuasi_otomatis
    t0 = time.monotonic()
    hasil = {
        "kode": kode,
        "nama": kode,
        "status_valuasi": "ok",
        "beta": "—",
        "durasi_detik": 0.0,
        "galat": "",
    }

    try:
        prof = pasar.profil(kode) or {}
        hasil["nama"] = prof.get("nama_en") or prof.get("nama") or kode
    except Exception as e:
        hasil["galat"] += f"profil: {e}; "

    try:
        hrg = pasar.harga(kode) or {}
        if not hasil["nama"] or hasil["nama"] == kode:
            hasil["nama"] = hrg.get("nama") or kode
    except Exception as e:
        hasil["galat"] += f"harga: {e}; "

    try:
        d = valuasi_otomatis.ambil(kode, paksa=paksa)
        if d.get("tidak_berlaku"):
            hasil["status_valuasi"] = "tidak berlaku (keuangan)"
            hasil["beta"] = "tidak berlaku"
        elif d.get("tidak_bisa_dihitung"):
            hasil["status_valuasi"] = "tidak bisa dihitung"
            hasil["beta"] = "—"
        else:
            # Tunggu jika beta masih sementara agar demo memperoleh beta resmi
            if d.get("beta_sementara"):
                t = valuasi_otomatis.pemicu_hitung_beta_latar(kode, d.get("bursa", "TWSE"))
                if t and t.is_alive():
                    t.join(timeout=180.0)
                d = valuasi_otomatis.baca_cache(kode, terima_basi=True) or d

            b_val = d.get("wacc_inputs", {}).get("beta", d.get("beta", 1.0))
            if d.get("beta_sementara"):
                hasil["beta"] = f"sementara ({b_val:.2f})"
            elif d.get("beta_cadangan"):
                hasil["beta"] = f"cadangan ({b_val:.2f})"
            else:
                hasil["beta"] = f"resmi ({b_val:.2f})"
            hasil["status_valuasi"] = "ok"
    except Exception as e:
        hasil["status_valuasi"] = "galat"
        hasil["galat"] += f"valuasi: {e}; "

    hasil["durasi_detik"] = round(time.monotonic() - t0, 2)
    if jeda > 0:
        time.sleep(jeda)
    return hasil


def jalankan(daftar_kode: list[str], paksa: bool = False, jeda: float = 0.5) -> list[dict]:
    """Jalankan pemanasan untuk sekumpulan kode secara berurutan."""
    print(f"\nMemulai pemanasan cache untuk {len(daftar_kode)} emiten...")
    print(f"{'Kode':<6} | {'Nama Emiten':<24} | {'Status Valuasi':<22} | {'Beta':<16} | {'Waktu':<8}")
    print("-" * 84)

    ringkasan = []
    for kode in daftar_kode:
        info = panaskan_satu(kode, paksa=paksa, jeda=jeda)
        ringkasan.append(info)
        nama_tampil = info["nama"][:22]
        durasi_str = f"{info['durasi_detik']:.2f}s"
        print(f"{info['kode']:<6} | {nama_tampil:<24} | {info['status_valuasi']:<22} | {info['beta']:<16} | {durasi_str:<8}")

    print("-" * 84)
    total_sukses = sum(1 for r in ringkasan if r["status_valuasi"] in ("ok", "tidak berlaku (keuangan)"))
    total_galat = sum(1 for r in ringkasan if r["status_valuasi"] == "galat")
    total_waktu = sum(r["durasi_detik"] for r in ringkasan)
    print(f"Selesai: {len(ringkasan)} diproses ({total_sukses} sukses, {total_galat} galat) dalam {total_waktu:.1f} detik.\n")
    return ringkasan


def main():
    parser = argparse.ArgumentParser(description="Pemanasan cache valuasi dan harga saham untuk demo.")
    parser.add_argument("--top", type=int, default=30, help="Jumlah emiten terbesar yang dipanaskan (bawaan: 30).")
    parser.add_argument("--kode", nargs="+", help="Daftar kode emiten spesifik (mengalahkan --top).")
    parser.add_argument("--data-dir", help="Lokasi folder penyimpanan cache data (SENTINEL_DATA_DIR).")
    parser.add_argument("--paksa", action="store_true", help="Paksa bangun ulang meski cache segar sudah ada.")
    parser.add_argument("--jeda", type=float, default=0.5, help="Jeda antar permintaan emiten (detik).")
    args = parser.parse_args()

    if args.data_dir:
        os.environ["SENTINEL_DATA_DIR"] = os.path.abspath(args.data_dir)
        from app import config, harga_resmi, valuasi_otomatis
        config.DATA_DIR = os.environ["SENTINEL_DATA_DIR"]
        valuasi_otomatis.CACHE_DIR = os.path.join(config.DATA_DIR, "valuasi_otomatis")

    daftar_kode = tentukan_daftar_kode(args.kode, top_n=args.top)
    jalankan(daftar_kode, paksa=args.paksa, jeda=args.jeda)


if __name__ == "__main__":
    main()
