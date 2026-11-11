"""Setelan aplikasi — semuanya dari environment, tidak ada yang ditulis di berkas.

Aturan lomba melarang kunci API, kata sandi, atau data pribadi masuk ke dokumen
maupun kode sumber yang dikumpulkan. Jadi kunci hanya dibaca dari environment
dan tidak pernah ikut tercetak di layar mana pun.
"""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data hasil tarikan bisa dipindah ke volume (mis. /data di Docker) supaya tidak hilang
# saat redeploy. Fixture tetap di repo — ia bagian dari kode, bukan data hasil jalan.
DATA_DIR = os.environ.get("SENTINEL_DATA_DIR") or os.path.join(ROOT, "data")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")
FIXTURE_DIR = os.path.join(ROOT, "data", "fixtures")
VALUATION_DIR = os.path.join(ROOT, "valuation", "inputs")
TRACE_DIR = os.path.join(DATA_DIR, "traces")

# Penyedia model. Gemini dipakai karena free tier-nya nyata dan konteksnya muat
# memuat pengumuman Mandarin panjang utuh. Penyedia lain tinggal ditukar lewat
# environment variable tanpa mengubah kode — lihat app/agent/llm.py.
#
# Kalau tidak ada kunci sama sekali, pipeline TETAP jalan memakai penalar berbasis
# aturan. Itu bukan sekadar cadangan: ia juga baseline yang diminta Appendix 2
# sebagai pembanding. Yang wajib: layar dan jejak audit selalu menyebut mana yang
# sedang dipakai — fixture atau model yang menyamar adalah cara tercepat
# kehilangan kepercayaan juri.
PENYEDIA = os.environ.get("SENTINEL_PENYEDIA", "gemini")
MODEL = os.environ.get("SENTINEL_MODEL", "gemini-3.6-flash")
# Model cadangan, dipisah koma, dicoba berurutan bila model utama sibuk (429/5xx) setelah
# percobaan ulang habis. Contoh: "gemini-3.5-flash,gemini-flash-latest".
MODEL_CADANGAN = [m.strip() for m in os.environ.get("SENTINEL_MODEL_CADANGAN", "gemini-3.5-flash").split(",") if m.strip()]
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Berapa kali panggilan model diulang sebelum turun ke penalar aturan.
RETRY_MAKS = int(os.environ.get("SENTINEL_RETRY", "2"))
TIMEOUT = int(os.environ.get("SENTINEL_TIMEOUT", "45"))

# Ambang keyakinan pemilah. Di bawah ini pengumuman tidak diteruskan ke
# penghitungan ulang, tapi tetap dicatat supaya bisa ditinjau manusia.
TRIAGE_THRESHOLD = float(os.environ.get("SENTINEL_TRIAGE_THRESHOLD", "0.55"))

# --- deploy ------------------------------------------------------------------
# Periksa pengumuman otomatis tiap N detik selama server menyala. 0 = mati (bawaan).
# Minimal 300 detik — OpenAPI bursa adalah layanan publik.
TARIK_OTOMATIS_DETIK = int(os.environ.get("SENTINEL_TARIK_OTOMATIS_DETIK", "0") or 0)

# Kalau diisi, tombol yang mengubah sesuatu (tambah/hapus watchlist, Periksa sekarang)
# hanya jalan setelah membuka /akses?kode=<isi ini> sekali. Halaman baca tetap terbuka.
KODE_AKSES = os.environ.get("SENTINEL_KODE_AKSES", "")

# Kunci baca: minta kode akses untuk semua halaman baca (untuk dinyalakan saat lomba).
# Bawaan mati (0). Hanya berlaku bila KODE_AKSES tidak kosong.
_raw_kunci_baca = os.environ.get("SENTINEL_KUNCI_BACA", "0") == "1"
if _raw_kunci_baca and not KODE_AKSES:
    import sys
    print(
        "[config] PERINGATAN: SENTINEL_KUNCI_BACA aktif tetapi SENTINEL_KODE_AKSES kosong. Kunci baca diabaikan.",
        file=sys.stderr,
    )
    KUNCI_BACA = False
else:
    KUNCI_BACA = _raw_kunci_baca

# Tampilkan empat kasus contoh berdampingan dengan data asli (ditandai "contoh"),
# supaya kasus injeksi, mata uang asing, dan terbit tetap bisa ditunjukkan.
SERTAKAN_CONTOH = os.environ.get("SENTINEL_SERTAKAN_CONTOH", "0") == "1"

# --- proses semua emiten & jatah model ---------------------------------------
PROSES_SEMUA = os.environ.get("SENTINEL_PROSES_SEMUA", "1") == "1"
MODEL_MAKS_PER_JALAN = int(os.environ.get("SENTINEL_MODEL_MAKS_PER_JALAN", "40"))
