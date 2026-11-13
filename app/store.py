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

import copy
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
    from . import valuasi_otomatis

    path = os.path.join(config.VALUATION_DIR, f"{kode}.json")
    manual: dict | None = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                manual = json.load(f)
        except (OSError, ValueError):
            manual = None

    auto = valuasi_otomatis.dari_cache_untuk_pipeline(kode)

    if auto is not None and valuasi_otomatis.layak_dcf(auto) and manual is not None:
        gabung = copy.deepcopy(auto)
        ditimpa: list[str] = []

        if "assumptions" in manual:
            gabung["assumptions"] = copy.deepcopy(manual["assumptions"])
            ditimpa.append("assumptions")

        if "wacc_inputs" in manual:
            if "wacc_inputs" not in gabung:
                gabung["wacc_inputs"] = {}
            for k in ("risk_free_rate", "equity_risk_premium"):
                if k in manual["wacc_inputs"]:
                    gabung["wacc_inputs"][k] = manual["wacc_inputs"][k]
                    ditimpa.append(f"wacc_inputs.{k}")

        tidak_ada = list(auto.get("tidak_tersedia", []))
        bs_manual = manual.get("balance_sheet", {})
        bs_gabung = gabung.setdefault("balance_sheet", {})
        sisa_tidak_ada = []
        for fld in tidak_ada:
            if fld in bs_manual:
                bs_gabung[fld] = bs_manual[fld]
                ditimpa.append(f"balance_sheet.{fld}")
            else:
                sisa_tidak_ada.append(fld)
        gabung["tidak_tersedia"] = sisa_tidak_ada

        gabung["asumsi_dari"] = "manual"
        gabung["ditimpa_manual"] = ditimpa
        return gabung

    if manual is not None:
        return manual

    return auto


def emiten_tervaluasi() -> list[str]:
    from . import valuasi_otomatis

    kode: set[str] = set()
    if os.path.isdir(config.VALUATION_DIR):
        kode.update(f[:-5] for f in os.listdir(config.VALUATION_DIR) if f.endswith(".json"))

    cache_dir = str(valuasi_otomatis.CACHE_DIR)
    if os.path.isdir(cache_dir):
        for f in os.listdir(cache_dir):
            if not f.endswith(".json"):
                continue
            k = f[:-5]
            if k not in kode and valuasi_otomatis.dari_cache_untuk_pipeline(k) is not None:
                kode.add(k)
    return sorted(kode)
