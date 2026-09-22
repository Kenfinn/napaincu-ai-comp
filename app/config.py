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

# Model dipakai kalau ANTHROPIC_API_KEY ada. Kalau tidak ada, pipeline tetap
# jalan memakai penalar berbasis aturan — lihat app/agent/llm.py. Yang penting:
# layar dan jejak audit selalu menyebutkan mana yang sedang dipakai.
MODEL = os.environ.get("SENTINEL_MODEL", "claude-sonnet-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY") or ""

# Ambang keyakinan pemilah. Di bawah ini pengumuman tidak diteruskan ke
# penghitungan ulang, tapi tetap dicatat supaya bisa ditinjau manusia.
TRIAGE_THRESHOLD = float(os.environ.get("SENTINEL_TRIAGE_THRESHOLD", "0.55"))
