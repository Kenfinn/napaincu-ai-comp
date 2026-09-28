"""Setelan aplikasi — semuanya dari environment, tidak ada yang ditulis di berkas.

Aturan lomba melarang kunci API, kata sandi, atau data pribadi masuk ke dokumen
maupun kode sumber yang dikumpulkan. Jadi kunci hanya dibaca dari environment
dan tidak pernah ikut tercetak di layar mana pun.
"""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(ROOT, "data")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")
FIXTURE_DIR = os.path.join(DATA_DIR, "fixtures")
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
MODEL = os.environ.get("SENTINEL_MODEL", "gemini-2.5-flash")
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Berapa kali panggilan model diulang sebelum turun ke penalar aturan.
RETRY_MAKS = int(os.environ.get("SENTINEL_RETRY", "2"))
TIMEOUT = int(os.environ.get("SENTINEL_TIMEOUT", "45"))

# Ambang keyakinan pemilah. Di bawah ini pengumuman tidak diteruskan ke
# penghitungan ulang, tapi tetap dicatat supaya bisa ditinjau manusia.
TRIAGE_THRESHOLD = float(os.environ.get("SENTINEL_TRIAGE_THRESHOLD", "0.55"))
