#!/usr/bin/env python3
"""Skrip QA otomatis untuk memverifikasi seluruh halaman aplikasi dalam tiga bahasa (QA1).

Membuka seluruh halaman statis, halaman saham (6 tab), dan halaman peringatan dalam
tiga bahasa (en, zh, id) secara luring (tanpa jaringan).

Memverifikasi:
1. Status kode HTTP 200 (atau 401 bila halaman terkunci)
2. Tidak ada kunci terjemahan mentah (mis. va.*, sn.*, nav.*, dll.)
3. Tidak ada teks rusak: GANTI, TODO, None, nan, Traceback
4. Tidak ada label beli/jual di luar blok penafian resmi
5. Peringatan bila kata Indonesia umum bocor ke halaman en/zh
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unittest.mock
from typing import Any

from starlette.testclient import TestClient

# Pastikan folder root proyek masuk ke sys.path
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from app import config, pasar, store, tarik
from app.main import app

# Pola deteksi kunci terjemahan mentah
POLA_KUNCI_MENTAH = re.compile(
    r"\b((?:ui|sn|tg|akhir|va|rk|ch|sh|wl|nav|merek|tombol|msg|sumber|status|pita)\.[a-z0-9_.]+)\b"
)

# Pola teks rusak / placeholder yang tidak boleh tampil
KATA_RUSAK = ["GANTI", "TODO", "Traceback", "⟦"]
POLA_NONE_NAN = re.compile(r">\s*(None|nan|NaN)\s*<")

# Kata rekomendasi investasi terlarang di luar penafian
POLA_REKOMENDASI = re.compile(
    r"\b(buy|sell|strong buy|beli|jual|akumulasi)\b|買進|買入|賣出|建議買|建議賣|目標價",
    re.IGNORECASE,
)

# Kata bahasa Indonesia yang berpotensi bocor ke antarmuka EN dan ZH (sebagai peringatan)
KATA_BOCOR_ID = ["Sumber", "belum", "tidak", "dan", "untuk", "Imbal hasil"]

# Teks penafian resmi yang memuat kata beli/jual (dikecualikan dari pemeriksaan)
TEKS_PENAFIAN = [
    "This is research, not a buy or sell recommendation",
    "本頁為研究分析，並非買賣建議",
    "Ini riset, bukan rekomendasi beli atau jual",
    "Robo-advice in Taiwan requires an FSC licence",
    "在台灣提供自動化投資建議須取得金管會核准",
    "Saran investasi otomatis di Taiwan wajib berizin FSC",
    "not a sell signal",
    "not a buy signal",
    "bukan sinyal jual",
    "bukan sinyal beli",
    "非賣出建議",
    "非買進建議",
    "buy or sell",
    "beli atau jual",
    "買賣建議",
    "not a buy or sell recommendation",
    "bukan rekomendasi beli atau jual",
]


def _ekstrak_teks_bersih(html: str) -> str:
    """Bersihkan tag HTML, script, dan style untuk mendapatkan teks tampil."""
    # Hapus blok script dan style
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.I)
    # Hapus tag HTML
    h = re.sub(r"<[^>]+>", " ", h)
    # Normalkan entitas
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return h


def _hapus_blok_penafian(html: str) -> str:
    """Hapus seluruh blok penafian sebelum memindai kata rekomendasi terlarang."""
    # Hapus elemen class pita fixture / penafian (termasuk tag div bersarang)
    h = re.sub(r'<div class="pita fixture">[\s\S]*?</div>\s*</div>', " ", html, flags=re.I)
    h = re.sub(r'<div class="penafian">[\s\S]*?</div>\s*</div>', " ", h, flags=re.I)
    for p in TEKS_PENAFIAN:
        h = h.replace(p, " ")
    return h


def periksa_kunci_mentah(html: str) -> list[str]:
    """Cari kunci terjemahan yang tampil mentah pada teks tampilan."""
    teks = _ekstrak_teks_bersih(html)
    temu = POLA_KUNCI_MENTAH.findall(teks)
    # Filter false positives bila ada
    return sorted(set(temu))


def periksa_placeholder_rusak(html: str) -> list[str]:
    """Deteksi teks placeholder GANTI, TODO, None, nan, atau Traceback."""
    hasil: list[str] = []
    teks = _ekstrak_teks_bersih(html)
    for k in KATA_RUSAK:
        if k in teks:
            hasil.append(k)

    m = POLA_NONE_NAN.findall(html)
    if m:
        hasil.extend(sorted(set(m)))

    return hasil


def periksa_kata_rekomendasi(html: str) -> list[str]:
    """Deteksi label beli/jual di luar blok penafian resmi."""
    html_tanpa_penafian = _hapus_blok_penafian(html)
    teks = _ekstrak_teks_bersih(html_tanpa_penafian)
    temu = POLA_REKOMENDASI.findall(teks)
    return sorted({m.lower() for m in temu if m})


def periksa_kebocoran_bahasa(html: str, bahasa: str) -> list[str]:
    """Deteksi kebocoran kata Indonesia umum pada halaman EN atau ZH (peringatan)."""
    if bahasa not in ("en", "zh"):
        return []
    teks = _ekstrak_teks_bersih(html)
    # Nama field dan nilai enum di JSON mentah halaman jejak ("sumber": "valuasi") adalah
    # pengenal kode yang sama dengan /api/jejak, bukan teks antarmuka.
    import html as _html
    teks = _html.unescape(teks)
    teks = re.sub(r'"\w+"\s*:', ":", teks)
    teks = re.sub(r':\s*"[a-z_]+"', ":", teks)
    bocor: list[str] = []
    for kata in KATA_BOCOR_ID:
        # Gunakan boundary bila alfabet
        pola = rf"\b{re.escape(kata)}\b"
        if re.search(pola, teks, re.IGNORECASE):
            bocor.append(kata)
    return sorted(set(bocor))


def kumpulkan_halaman_uji() -> list[str]:
    """Kumpulkan daftar rute yang wajib diuji sesuai spesifikasi prompt."""
    rute: list[str] = [
        "/",
        "/watchlist",
        "/review",
        "/ambang",
        "/tanya",
        "/sehat",
        "/valuasi/2330",
    ]

    # Ambil 3 kode emiten watchlist (atau bawaan 2330, 2317, 2454)
    wl = tarik.baca_watchlist()
    kodes = (wl[:3] if len(wl) >= 3 else (wl + ["2330", "2317", "2454"])[:3])
    tabs = ["ringkasan", "stream", "stats", "keu", "valuasi", "profil"]
    for kd in kodes:
        for tb in tabs:
            rute.append(f"/saham/{kd}?tab={tb}")

    # Ambil contoh peringatan per jenis status & sinyal
    from app.main import hasil
    daftar_hasil = hasil()
    terbit_valuasi = None
    contoh_sinyal: dict[str, str] = {}
    contoh_tahan = None

    for d in daftar_hasil:
        pid = d.get("id")
        if not pid:
            continue
        # Contoh terbit valuasi
        if not terbit_valuasi and (d.get("jenis") == "valuasi" or d.get("status") in ("terbit", "PUBLISHED")):
            terbit_valuasi = pid
        # Contoh per jenis sinyal
        sn = d.get("jenis") or ((d.get("muatan") or {}).get("sinyal") or {}).get("jalur")
        if sn and sn not in contoh_sinyal:
            contoh_sinyal[sn] = pid
        # Contoh tahan
        if not contoh_tahan and (d.get("status") in ("tahan", "HELD") or d.get("state") == "HELD"):
            contoh_tahan = pid

    peringatan_ids: list[str] = []
    if terbit_valuasi:
        peringatan_ids.append(terbit_valuasi)
    for s_id in contoh_sinyal.values():
        if s_id not in peringatan_ids:
            peringatan_ids.append(s_id)
    if contoh_tahan and contoh_tahan not in peringatan_ids:
        peringatan_ids.append(contoh_tahan)

    if not peringatan_ids and daftar_hasil:
        peringatan_ids.append(daftar_hasil[0]["id"])

    for pid in peringatan_ids:
        rute.append(f"/peringatan/{pid}")
    if peringatan_ids:
        rute.append(f"/jejak/{peringatan_ids[0]}")

    return rute


def jalankan_qa(
    data_dir: str | None = None,
    verbose: bool = False,
) -> tuple[int, list[dict[str, Any]]]:
    """Jalankan pemindaian seluruh halaman x bahasa dengan TestClient."""
    if data_dir:
        config.DATA_DIR = os.path.abspath(data_dir)

    client = TestClient(app, follow_redirects=True)
    rute_uji = kumpulkan_halaman_uji()
    daftar_bahasa = ["en", "zh", "id"]

    total_uji = 0
    total_gagal = 0
    hasil_uji: list[dict[str, Any]] = []

    # Matikan akses jaringan dan thread latar belakang saat pemindaian QA
    with unittest.mock.patch("urllib.request.urlopen", side_effect=RuntimeError("Akses jaringan dilarang dalam QA")), \
         unittest.mock.patch("app.tarik._ambil_json", return_value=[]), \
         unittest.mock.patch("app.pasar._ambil_json", return_value=[]), \
         unittest.mock.patch("app.harga_resmi._ambil_json", return_value=None), \
         unittest.mock.patch("app.valuasi_otomatis.pemicu_hitung_beta_latar", return_value=None):

        for rute in rute_uji:
            for bhs in daftar_bahasa:
                total_uji += 1
                catatan_galat: list[str] = []
                catatan_peringatan: list[str] = []

                try:
                    resp = client.get(rute, cookies={"bahasa": bhs})
                    status = resp.status_code
                    html = resp.text

                    if status not in (200, 401):
                        catatan_galat.append(f"HTTP {status}")

                    # 1. Cek kunci terjemahan mentah
                    mentah = periksa_kunci_mentah(html)
                    if mentah:
                        catatan_galat.append(f"Kunci mentah: {', '.join(mentah[:3])}")

                    # 2. Cek teks rusak (GANTI, TODO, None, nan)
                    rusak = periksa_placeholder_rusak(html)
                    if rusak:
                        catatan_galat.append(f"Teks rusak: {', '.join(rusak)}")

                    # 3. Cek kata rekomendasi beli/jual di luar penafian
                    beli_jual = periksa_kata_rekomendasi(html)
                    if beli_jual:
                        catatan_galat.append(f"Kata rekomendasi: {', '.join(beli_jual)}")

                    # 4. Cek kebocoran bahasa Indonesia (peringatan)
                    bocor = periksa_kebocoran_bahasa(html, bhs)
                    if bocor:
                        catatan_peringatan.append(f"Bocor kata ID: {', '.join(bocor)}")

                except Exception as e:
                    catatan_galat.append(f"Eksepsi: {e}")

                sukses = len(catatan_galat) == 0
                if not sukses:
                    total_gagal += 1

                hasil_uji.append({
                    "rute": rute,
                    "bahasa": bhs,
                    "sukses": sukses,
                    "galat": catatan_galat,
                    "peringatan": catatan_peringatan,
                })

    return total_gagal, hasil_uji


def cetak_laporan_tabel(hasil_uji: list[dict[str, Any]]) -> str:
    """Format hasil QA ke bentuk tabel markdown yang ringkas."""
    garis: list[str] = [
        "| No | Rute Halaman | Bahasa | Status | Keterangan / Masalah |",
        "|---|---|---|---|---|",
    ]
    for i, h in enumerate(hasil_uji, 1):
        status_str = "✅ Lolos" if h["sukses"] else "❌ Gagal"
        sebab = []
        if h["galat"]:
            sebab.extend(h["galat"])
        if h["peringatan"]:
            sebab.append(f"⚠️ {'; '.join(h['peringatan'])}")
        ket = "; ".join(sebab) if sebab else "Bersih"
        garis.append(f"| {i} | `{h['rute']}` | {h['bahasa']} | {status_str} | {ket} |")

    return "\n".join(garis)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pemeriksaan QA Halaman Tiga Bahasa")
    parser.add_argument("--data-dir", default=config.DATA_DIR, help="Direktori data aplikasi")
    parser.add_argument("-v", "--verbose", action="store_true", help="Tampilkan rincian lengkap")
    args = parser.parse_args(argv)

    total_gagal, hasil_uji = jalankan_qa(data_dir=args.data_dir, verbose=args.verbose)
    tabel = cetak_laporan_tabel(hasil_uji)
    print(tabel)

    total = len(hasil_uji)
    total_lolos = total - total_gagal
    print(f"\nRingkasan QA: {total_lolos}/{total} kombinasi halaman x bahasa lolos (Gagal: {total_gagal}).")

    return 1 if total_gagal > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
