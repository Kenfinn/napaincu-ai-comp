"""Pemuat data — satu jalur kode untuk data asli maupun fixture.

Data asli MOPS hanya bisa ditarik dari jaringan Taiwan (lihat docs/akses-data.md),
jadi aplikasi ini harus tetap jalan di mesin mana pun: di laptop juri, di CI, dan di
komputer anggota tim yang belum sempat menjalankan penarikan.

Aturannya sederhana: kalau data/parsed/ ada isinya, itu yang dipakai. Kalau tidak,
jatuh ke data/fixtures/. Yang penting **kode yang membacanya sama persis** — kalau
fixture punya jalur baca sendiri, bug di jalur asli tidak akan pernah ketahuan sampai
hari demo.

Setiap muatan membawa penanda `sumber` supaya layar bisa menyatakan terus terang
mana yang sedang ditampilkan. Fixture yang menyamar jadi data asli adalah cara
tercepat kehilangan kepercayaan juri.
"""

from __future__ import annotations

import json
import os

from . import config


def _read(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _pick(nama: str) -> tuple[list[dict], str]:
    """Kembalikan (rekaman, sumber) — 'nyata' kalau data/parsed/ terisi."""
    nyata = _read(os.path.join(config.PARSED_DIR, nama))
    if nyata:
        return nyata, "nyata"
    return _read(os.path.join(config.FIXTURE_DIR, nama)), "fixture"


def muat_pengumuman() -> tuple[list[dict], str]:
    rows, sumber = _pick("announcements.json")
    rows.sort(key=lambda r: (r.get("date", ""), r.get("time", "")), reverse=True)
    return rows, sumber


def muat_detail() -> tuple[list[dict], str]:
    rows, sumber = _pick("details.json")
    if sumber == "nyata" and config.SERTAKAN_CONTOH:
        # Contoh ditandai `_fixture`, dan layar memberi label "contoh" — tidak pernah
        # tercampur diam-diam dengan data asli.
        rows = rows + _read(os.path.join(config.FIXTURE_DIR, "details.json"))
    return rows, sumber


def detail_untuk(source_url: str) -> dict | None:
    rows, _ = muat_detail()
    for r in rows:
        if r.get("source_url") == source_url:
            return r
    return None


def id_pengumuman(rec: dict) -> str:
    """Pengenal stabil untuk URL rute.

    MOPS tidak memberi satu kunci primer yang rapi, jadi kombinasi kode emiten,
    tanggal, dan nomor urut dipakai — ketiganya sudah ada di halaman sumbernya.
    """
    return f"{rec.get('code', '?')}-{rec.get('date', '?')}-{rec.get('seq_no', rec.get('time', '?'))}"


def muat_valuasi(kode: str) -> dict | None:
    path = os.path.join(config.VALUATION_DIR, f"{kode}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def emiten_tervaluasi() -> list[str]:
    if not os.path.isdir(config.VALUATION_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(config.VALUATION_DIR) if f.endswith(".json"))
