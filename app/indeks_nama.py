"""Indeks pencarian emiten berdasarkan kode angka atau nama (Zh/En/Alias).

Sumber resmi:
- TWSE OpenAPI: https://openapi.twse.com.tw/v1/opendata/t187ap03_L
- TPEx OpenAPI: https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O

Data disimpan di DATA_DIR/indeks_nama.json selama 7 hari.
HANYA menyimpan 4 kolom: kode, nama, nama_en, bursa.
Data pribadi pejabat/direksi dari profil bursa TIDAK disimpan.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import unicodedata
import urllib.request
from typing import Any

from . import config

log = logging.getLogger("indeks_nama")

BERKAS_INDEKS = os.path.join(config.DATA_DIR, "indeks_nama.json")
TTL_DETIK = 7 * 86400  # 7 hari

SUMBER_TWSE = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
SUMBER_TPEX = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"
UA = "FEAF-InvestmentAssistant/0.3"

# Kunci yang diizinkan untuk disimpan dalam indeks (daftar izin ketat)
KOLOM_DISETUJUI = frozenset(("kode", "nama", "nama_en", "bursa"))

# Pola kode saham bursa Taiwan: 4-6 digit angka
POLA_KODE_ANGKA = re.compile(r"^\d{4,6}$")

# Alias populer yang ditulis tangan untuk perusahaan besar Taiwan yang sering
# dicari pengguna dengan singkatan atau nama dagang umum (bukan nama resmi bursa).
ALIAS_POPULER: dict[str, list[str]] = {
    "2330": ["TSMC", "Taiwan Semiconductor", "台積電"],
    "2454": ["MediaTek", "MTK", "聯發科"],
    "2317": ["Foxconn", "Hon Hai", "鴻海", "富士康"],
    "2303": ["UMC", "United Microelectronics", "聯電"],
    "3711": ["ASE", "ASE Technology", "ASEH", "日月光", "日月光投控"],
    "2308": ["Delta", "Delta Electronics", "台達電"],
    "2382": ["Quanta", "Quanta Computer", "廣達"],
    "2881": ["Fubon", "Fubon Financial", "富邦", "富邦金", "富邦金控"],
    "2882": ["Cathay", "Cathay Financial", "國泰", "國泰金", "國泰金控"],
    "2891": ["CTBC", "CTBC Holding", "中信", "中信金", "中國信託"],
    "6488": ["GlobalWafers", "環球晶", "GW", "GWC"],
}


def _normal(s: Any) -> str:
    """Normalisasi string pencarian: NFKC, hapus spasi/tanda baca, huruf kecil."""
    if not s:
        return ""
    teks = unicodedata.normalize("NFKC", str(s))
    for c in " \t\r\n-_./(),'\"`\u3000\uff08\uff09":
        teks = teks.replace(c, "")
    return teks.lower()


def _ambil_url_json(url: str, timeout: int = 15) -> list[dict] | None:
    """Ambil JSON dari URL OpenAPI secara aman."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            konten = r.read().decode("utf-8-sig", "replace")
            data = json.loads(konten)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                return data["data"]
            return None
    except Exception as e:
        log.warning("Gagal ambil JSON dari %s: %s", url, e)
        return None


def _ekstrak_twse(baris_twse: list[dict]) -> list[dict]:
    """Saring baris profil TWSE menjadi 4 kolom aman."""
    hasil: list[dict] = []
    for r in baris_twse:
        if not isinstance(r, dict):
            continue
        kode = str(r.get("公司代號") or "").strip()
        nama = str(r.get("公司簡稱") or "").strip()
        nama_en = str(r.get("英文簡稱") or "").strip() or None
        if kode and nama:
            hasil.append({
                "kode": kode,
                "nama": nama,
                "nama_en": nama_en,
                "bursa": "TWSE",
            })
    return hasil


def _ekstrak_tpex(baris_tpex: list[dict]) -> list[dict]:
    """Saring baris profil TPEx menjadi 4 kolom aman."""
    hasil: list[dict] = []
    for r in baris_tpex:
        if not isinstance(r, dict):
            continue
        kode = str(r.get("SecuritiesCompanyCode") or "").strip()
        nama = str(r.get("CompanyAbbreviation") or "").strip()
        en = r.get("SymbolEnglish") or r.get("Symbol")
        nama_en = str(en).strip() if en else None
        if kode and nama:
            hasil.append({
                "kode": kode,
                "nama": nama,
                "nama_en": nama_en,
                "bursa": "TPEx",
            })
    return hasil


def _muat_dari_cache_pasar(data_dir: str) -> list[dict]:
    """Cadangan bila OpenAPI tidak dapat dijangkau: baca dari profil_twse.json & profil_tpex.json."""
    hasil: list[dict] = []
    twse_p = os.path.join(data_dir, "pasar", "profil_twse.json")
    if os.path.exists(twse_p):
        try:
            with open(twse_p, encoding="utf-8") as f:
                d = json.load(f)
                rows = d.get("data", []) if isinstance(d, dict) else d
                hasil.extend(_ekstrak_twse(rows))
        except Exception:
            pass

    tpex_p = os.path.join(data_dir, "pasar", "profil_tpex.json")
    if os.path.exists(tpex_p):
        try:
            with open(tpex_p, encoding="utf-8") as f:
                d = json.load(f)
                rows = d.get("data", []) if isinstance(d, dict) else d
                hasil.extend(_ekstrak_tpex(rows))
        except Exception:
            pass

    return hasil


_CACHE_MEMORI: dict[str, Any] = {"waktu": 0.0, "data": []}


def bangun_indeks(
    paksa: bool = False,
    berkas: str | None = None,
    data_dir: str | None = None,
) -> list[dict]:
    """Bangun atau muat indeks nama emiten.

    Jika cache berkas valid (<7 hari) dan tidak paksa, muat dari berkas.
    Jika tidak, ambil dari OpenAPI TWSE & TPEx, simpan hanya 4 kolom aman.
    """
    target_berkas = berkas or (os.path.join(data_dir, "indeks_nama.json") if data_dir else BERKAS_INDEKS)
    parent_dir = os.path.dirname(target_berkas) or "."
    data_dir_efektif = data_dir or (os.path.dirname(target_berkas) if os.path.dirname(target_berkas) else config.DATA_DIR)

    sekarang = time.time()
    if not paksa and os.path.exists(target_berkas):
        try:
            mtime = os.path.getmtime(target_berkas)
            if sekarang - mtime < TTL_DETIK:
                with open(target_berkas, encoding="utf-8") as f:
                    isi = json.load(f)
                    emiten = isi.get("emiten", [])
                    if isinstance(emiten, list) and emiten:
                        _CACHE_MEMORI["waktu"] = mtime
                        _CACHE_MEMORI["data"] = emiten
                        return emiten
        except Exception as e:
            log.warning("Gagal membaca berkas indeks %s: %s", target_berkas, e)

    # Ambil dari OpenAPI resmi
    daftar: list[dict] = []
    twse_raw = _ambil_url_json(SUMBER_TWSE)
    if twse_raw:
        daftar.extend(_ekstrak_twse(twse_raw))

    tpex_raw = _ambil_url_json(SUMBER_TPEX)
    if tpex_raw:
        daftar.extend(_ekstrak_tpex(tpex_raw))

    # Jika jaringan gagal / kosong, coba cadangan dari cache pasar lokal
    if not daftar:
        daftar = _muat_dari_cache_pasar(data_dir_efektif)

    if not daftar:
        # Jika tetap kosong dan ada cache lama yang kedaluwarsa, gunakan daripada kosong
        if os.path.exists(target_berkas):
            try:
                with open(target_berkas, encoding="utf-8") as f:
                    isi = json.load(f)
                    return isi.get("emiten", [])
            except Exception:
                pass
        return []

    # Dedup berdasarkan kode
    unik: dict[str, dict] = {}
    for item in daftar:
        k = item["kode"]
        if k not in unik:
            # Pastikan hanya menyimpan 4 kolom aman
            unik[k] = {col: item.get(col) for col in KOLOM_DISETUJUI}

    hasil_bersih = list(unik.values())

    # Tulis ke berkas cache
    try:
        os.makedirs(parent_dir, exist_ok=True)
        tmp = f"{target_berkas}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"waktu": sekarang, "emiten": hasil_bersih}, f, ensure_ascii=False, indent=2)
        os.replace(tmp, target_berkas)
    except Exception as e:
        log.warning("Gagal menulis cache indeks %s: %s", target_berkas, e)

    _CACHE_MEMORI["waktu"] = sekarang
    _CACHE_MEMORI["data"] = hasil_bersih
    return hasil_bersih


def muat_indeks(berkas: str | None = None, data_dir: str | None = None) -> list[dict]:
    """Muat indeks emiten, memanfaatkan memori atau berkas."""
    sekarang = time.time()
    if _CACHE_MEMORI["data"] and (sekarang - _CACHE_MEMORI["waktu"] < 300) and berkas is None:
        return _CACHE_MEMORI["data"]
    return bangun_indeks(berkas=berkas, data_dir=data_dir)


def apakah_cocok_persis(q: str, item: dict) -> bool:
    """Periksa apakah kueri q cocok persis dengan kode, nama, nama_en, atau alias item."""
    qn = _normal(q)
    if not qn:
        return False
    if q.strip().upper() == str(item.get("kode", "")).strip().upper():
        return True
    if qn == _normal(item.get("nama")):
        return True
    if item.get("nama_en") and qn == _normal(item.get("nama_en")):
        return True
    for a in ALIAS_POPULER.get(item.get("kode", ""), []):
        if qn == _normal(a):
            return True
    return False


def cari(
    q: str,
    limit: int = 10,
    indeks: list[dict] | None = None,
) -> list[dict]:
    """Cari emiten berdasarkan kode, nama, nama Inggris, atau alias.

    Urutan prioritas:
    1. Cocok persis kode
    2. Cocok persis nama / nama_en / alias
    3. Cocok awalan (prefix) kode / nama / nama_en / alias
    4. Mengandung (substring) di kode / nama / nama_en / alias

    Mengembalikan maksimal `limit` hasil berurutan.
    """
    q_mentah = q.strip()
    if not q_mentah:
        return []

    daftar = indeks if indeks is not None else muat_indeks()
    qn = _normal(q_mentah)
    q_kode = q_mentah.upper()

    koleksi: list[dict] = []
    sudah: set[str] = set()

    def tambah(item: dict) -> bool:
        k = item["kode"]
        if k not in sudah:
            sudah.add(k)
            koleksi.append(item)
            if len(koleksi) >= limit:
                return True
        return False

    b1_kode_persis: list[dict] = []
    b2_nama_persis: list[dict] = []
    b3_awalan: list[dict] = []
    b4_mengandung: list[dict] = []

    for r in daftar:
        kd = str(r.get("kode", "")).strip().upper()
        nm = str(r.get("nama", "")).strip()
        ne = str(r.get("nama_en", "") or "").strip()
        aliases = ALIAS_POPULER.get(kd, [])

        nm_n = _normal(nm)
        ne_n = _normal(ne)
        al_n = [_normal(a) for a in aliases]

        # 1. Cocok persis kode
        if kd == q_kode:
            b1_kode_persis.append(r)
            continue

        # 2. Cocok persis nama / nama_en / alias
        # 2a. Langsung tanpa perlu menghapus tanda baca (mis. 'TSMC' vs 'T.S.M.C.') atau alias populer
        if (
            q_mentah.upper() in (nm.upper(), ne.upper())
            or any(q_mentah.upper() == a.upper() for a in aliases)
        ):
            b2_nama_persis.insert(0 if aliases else len(b2_nama_persis), r)
            continue

        if (qn and qn == nm_n) or (ne_n and qn == ne_n) or any(qn == a for a in al_n):
            b2_nama_persis.append(r)
            continue

        # 3. Cocok awalan (prefix)
        if (
            kd.startswith(q_kode)
            or (nm_n and nm_n.startswith(qn))
            or (ne_n and ne_n.startswith(qn))
            or any(a.startswith(qn) for a in al_n)
        ):
            b3_awalan.append(r)
            continue

        # 4. Mengandung (substring)
        if (
            (q_kode in kd)
            or (nm_n and qn in nm_n)
            or (ne_n and qn in ne_n)
            or any(qn in a for a in al_n)
        ):
            b4_mengandung.append(r)

    # Gabungkan sesuai urutan prioritas
    for kumpulan in (b1_kode_persis, b2_nama_persis, b3_awalan, b4_mengandung):
        for item in kumpulan:
            if tambah(item):
                break
        if len(koleksi) >= limit:
            break

    # 5. Jika indeks kosong/jaringan gagal dan kueri adalah kode angka yang sah:
    # tetap kembalikan kode tersebut agar pencarian angka tidak lumpuh
    if not koleksi and POLA_KODE_ANGKA.match(q_mentah):
        koleksi.append({
            "kode": q_kode,
            "nama": q_kode,
            "nama_en": q_kode,
            "bursa": "TWSE",
        })

    return koleksi
