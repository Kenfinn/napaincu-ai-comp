"""Penarik pengumuman dinamis — dari OpenAPI resmi bursa, bisa dijalankan dari mana saja.

MOPS memblokir jaringan di luar Taiwan, tapi bursa menerbitkan ulang pengumuman
material (重大訊息) hari berjalan lewat OpenAPI resmi yang **tidak** diblokir:

    TWSE (saham tercatat)  https://openapi.twse.com.tw/v1/opendata/t187ap04_L
    TPEx (saham OTC)       https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O

Isinya lengkap: pasal (符合條款), tanggal kejadian, dan seluruh butir 說明 — bahan yang
sama dengan halaman detail MOPS, dan tanpa data juru bicara.

Batasannya: endpoint itu hanya memuat pengumuman **terbaru**, bukan riwayat. Jadi
setiap tarikan disimpan dan digabung; riwayat terkumpul sendiri sejak hari pertama
aplikasi dipakai. Riwayat sebelum itu ditarik sekali dari jaringan Taiwan lewat
scripts/spike_mops.py + fetch_details.py, dan hasilnya digabung ke berkas yang sama.

Satu fungsi utama, `periksa_sekarang()`, dipakai tombol di web dan perintah CLI
(scripts/tarik.py). Tidak ada jalur kedua — bug di satu jalur tidak boleh tersembunyi
karena jalur lainnya yang dipakai saat uji.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from . import config

SUMBER = {
    "twse": {
        "nama": "TWSE OpenAPI t187ap04_L (上市公司每日重大訊息)",
        "url": "https://openapi.twse.com.tw/v1/opendata/t187ap04_L",
        "pasar": "sii",
    },
    "tpex": {
        "nama": "TPEx OpenAPI mopsfin_t187ap04_O (上櫃公司每日重大訊息)",
        "url": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O",
        "pasar": "otc",
    },
}

# Halaman MOPS yang bisa dibuka manusia untuk mencocokkan. OpenAPI tidak memberi
# alamat per pengumuman, jadi tautannya menuju halaman pencarian 重大訊息, dan layar
# menyebut kode + tanggal + jam yang dicari. Lebih jujur daripada mengarang alamat.
MOPS_CARI = "https://mops.twse.com.tw/mops/#/web/t05st01"

WATCHLIST_FILE = os.path.join(config.DATA_DIR, "watchlist.json")
STATUS_FILE = os.path.join(config.DATA_DIR, "status_tarik.json")
RAW_DIR = os.path.join(config.DATA_DIR, "raw", "openapi")
DETAIL_FILE = os.path.join(config.PARSED_DIR, "details.json")
LIST_FILE = os.path.join(config.PARSED_DIR, "announcements.json")

WATCHLIST_AWAL = ["2330", "2454", "2317", "2881", "1301"]

UA = "SentinelSaham/0.2 (+riset kompetisi; read-only)"
TIMEOUT = 30
RETRY = 2
BLOCK_MARKERS = ("FOR SECURITY REASONS", "因為安全性考量")

# Field yang tidak pernah disimpan, kalau suatu saat ikut muncul di endpoint.
PII_LABELS = ("發言人", "發言人職稱", "發言人電話", "代理發言人")


def _sekarang() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- watchlist

def baca_watchlist() -> list[str]:
    if not os.path.exists(WATCHLIST_FILE):
        return list(WATCHLIST_AWAL)
    with open(WATCHLIST_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return [str(k) for k in data.get("kode", [])]


def simpan_watchlist(kode: list[str]) -> list[str]:
    unik = list(dict.fromkeys(k.strip() for k in kode if k.strip()))
    os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"kode": unik, "diubah": _sekarang()}, f, ensure_ascii=False, indent=2)
    return unik


KODE_SAH = re.compile(r"^[0-9A-Z]{4,6}$")


def tambah_ke_watchlist(kode: str) -> tuple[bool, str]:
    kode = (kode or "").strip().upper()
    if not KODE_SAH.match(kode):
        return False, f"“{kode}” bukan bentuk kode saham Taiwan (4–6 angka/huruf)."
    sekarang = baca_watchlist()
    if kode in sekarang:
        return False, f"{kode} sudah ada di watchlist."
    simpan_watchlist(sekarang + [kode])
    return True, f"{kode} ditambahkan."


def hapus_dari_watchlist(kode: str) -> list[str]:
    return simpan_watchlist([k for k in baca_watchlist() if k != kode])


# --------------------------------------------------------------------------- ambil

class Diblokir(Exception):
    """Server mengembalikan halaman blokir (sering dengan HTTP 200)."""


class BentukSalah(Exception):
    """Respons bukan daftar pengumuman yang diharapkan."""


def _ambil_json(url: str) -> list[dict]:
    """GET + validasi bentuk. Status 200 saja tidak cukup — lihat docs/akses-data.md."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        teks = r.read().decode("utf-8-sig", "replace")
    if any(m in teks[:3000] for m in BLOCK_MARKERS):
        raise Diblokir("halaman blokir keamanan bursa")
    try:
        data = json.loads(teks)
    except json.JSONDecodeError as e:
        raise BentukSalah(f"bukan JSON: {e}") from e
    if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
        raise BentukSalah("bukan daftar objek")
    return data


def ambil(sumber: str) -> list[dict]:
    """Ambil satu sumber dengan percobaan ulang. Melempar exception terakhir kalau gagal."""
    url = SUMBER[sumber]["url"]
    galat: Exception | None = None
    for i in range(RETRY + 1):
        try:
            return _ambil_json(url)
        except Diblokir:
            raise                       # diulang pun hasilnya sama
        except (urllib.error.URLError, TimeoutError, ConnectionError, BentukSalah, OSError) as e:
            galat = e
            if i < RETRY:
                time.sleep(2 * (i + 1))
    assert galat is not None
    raise galat


# --------------------------------------------------------------------------- urai

def _roc_ke_iso(roc: str) -> str | None:
    """'1151107' atau '115/11/07' → '2026-11-07'."""
    s = re.sub(r"\D", "", roc or "")
    if len(s) not in (6, 7):
        return None
    y, m, d = int(s[:-4]), int(s[-4:-2]), int(s[-2:])
    try:
        return datetime(y + 1911, m, d).date().isoformat()
    except ValueError:
        return None


def _jam(t: str) -> str:
    """'70003' → '07:00:03'."""
    s = re.sub(r"\D", "", t or "").zfill(6)[-6:]
    return f"{s[:2]}:{s[2:4]}:{s[4:]}"


BUTIR = re.compile(r"(?m)^[ \t　]*(\d{1,2})\s*[.．、]\s*")


def urai_butir(teks: str) -> list[dict]:
    """Pecah 說明 menjadi butir bernomor.

    Hanya nomor yang **berurutan** (1, 2, 3, …) yang diakui sebagai awal butir. Tanpa
    syarat ini, baris tabel atau tanggal di dalam isi (mis. '12. ...' di tengah daftar
    rincian) akan memotong butir di tempat yang salah.
    """
    teks = (teks or "").replace("\r\n", "\n").replace("\r", "\n")
    posisi: list[tuple[int, int, int]] = []          # (nomor, awal_cocok, akhir_cocok)
    harap = 1
    for m in BUTIR.finditer(teks):
        n = int(m.group(1))
        if n == harap:
            posisi.append((n, m.start(), m.end()))
            harap += 1
    butir = []
    for i, (n, _, akhir) in enumerate(posisi):
        ujung = posisi[i + 1][1] if i + 1 < len(posisi) else len(teks)
        isi = teks[akhir:ujung]
        sep = re.search(r"[:：]", isi)
        label, nilai = (isi[:sep.start()], isi[sep.end():]) if sep else (isi, "")
        label_lengkap = " ".join(label.split())
        # Label resmi kadang membawa keterangan panjang dalam kurung, mis.
        # 其他應敘明事項(若事件發生或決議之主體…). Yang dicocokkan pemeriksa adalah intinya.
        inti = re.sub(r"[（(][^）)]*[)）]", "", label_lengkap).strip()
        butir.append({
            "no": n,
            "label": inti or label_lengkap,
            "label_lengkap": label_lengkap,
            "value": " ".join(nilai.split()),
        })
    return butir


def _pasal(raw: str) -> int | None:
    m = re.search(r"(\d+)", raw or "")
    return int(m.group(1)) if m else None


def normalkan(rec: dict, sumber: str, ditarik: str) -> dict:
    """Satu baris OpenAPI → bentuk detail yang dipakai pipeline (sama dengan fetch_details.py)."""
    # Nama kolom TWSE kadang berspasi ('主旨 '), TPEx sebagian berbahasa Inggris.
    r = {re.sub(r"\s+", "", k): v for k, v in rec.items()}
    kode = str(r.get("公司代號") or r.get("SecuritiesCompanyCode") or "").strip()
    nama = str(r.get("公司名稱") or r.get("CompanyName") or "").strip()
    tgl_roc = str(r.get("發言日期") or "")
    jam_raw = str(r.get("發言時間") or "")
    tanggal = _roc_ke_iso(tgl_roc)
    jam = _jam(jam_raw)
    subjek = " ".join(str(r.get("主旨") or "").split())
    klausa_raw = str(r.get("符合條款") or "").strip()
    isi = str(r.get("說明") or "")
    kunci = f"{kode}-{tanggal}-{jam.replace(':', '')}"
    return {
        "code": kode,
        "name": nama,
        "date": tanggal,
        "time": jam,
        "seq_no": jam.replace(":", ""),
        "subject": subjek,
        "clause_raw": klausa_raw,
        "clause": _pasal(klausa_raw),
        "fact_date": _roc_ke_iso(str(r.get("事實發生日") or "")),
        "announce_date": tanggal,
        "announce_time": jam,
        "items": urai_butir(isi),
        "body_chars": len(isi),
        "dropped_pii": [k for k in PII_LABELS if k in r],
        # Pengenal unik yang stabil. Bukan alamat yang bisa dibuka — OpenAPI tidak
        # memberi alamat per pengumuman, dan endpointnya hanya memuat hari berjalan.
        "source_url": f"{SUMBER[sumber]['url']}#{kunci}",
        "mops_url": MOPS_CARI,
        "sumber_data": SUMBER[sumber]["nama"],
        "pasar": SUMBER[sumber]["pasar"],
        "tanggal_terbit_data": _roc_ke_iso(str(r.get("出表日期") or r.get("Date") or "")),
        "fetched_at": ditarik,
    }


# --------------------------------------------------------------------------- simpan

def _baca_list(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _tulis_atomik(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _kunci(d: dict) -> tuple:
    return (d.get("code"), d.get("date"), d.get("time"), d.get("subject"))


def gabung(baru: list[dict]) -> int:
    """Gabungkan ke details.json tanpa duplikat. Mengembalikan jumlah yang benar-benar baru."""
    lama = _baca_list(DETAIL_FILE)
    ada = {_kunci(d) for d in lama}
    tambah = [d for d in baru if _kunci(d) not in ada]
    if not tambah and os.path.exists(DETAIL_FILE):
        return 0
    semua = lama + tambah
    semua.sort(key=lambda d: (d.get("date") or "", d.get("time") or ""), reverse=True)
    _tulis_atomik(DETAIL_FILE, semua)
    # Daftar ringkas untuk layar & skrip lain — diturunkan dari detail, satu sumber kebenaran.
    _tulis_atomik(LIST_FILE, [{
        "code": d["code"], "name": d["name"], "date": d["date"], "time": d["time"],
        "subject": d["subject"], "detail_url": d["source_url"],
    } for d in semua])
    return len(tambah)


def baca_status() -> dict | None:
    if not os.path.exists(STATUS_FILE):
        return None
    with open(STATUS_FILE, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- utama

def periksa_sekarang(watchlist: list[str] | None = None) -> dict:
    """Tarik pengumuman terbaru, saring ke watchlist, gabungkan ke riwayat.

    Tidak pernah melempar exception ke pemanggil: kegagalan satu sumber dicatat di
    status dan sumber lain tetap diproses. Aplikasi harus tetap bisa menampilkan data
    terakhir yang tersimpan walau jaringan sedang bermasalah.
    """
    wl = set(watchlist if watchlist is not None else baca_watchlist())
    ditarik = _sekarang()
    cap = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    status = {"waktu": ditarik, "watchlist": sorted(wl), "sumber": {}, "baru": 0,
              "cocok_watchlist": 0}
    kumpul: list[dict] = []

    for nama in SUMBER:
        t0 = time.monotonic()
        try:
            data = ambil(nama)
        except Diblokir as e:
            status["sumber"][nama] = {"ok": False, "jenis": "diblokir", "pesan": str(e)}
            continue
        except Exception as e:                       # noqa: BLE001 — dicatat, bukan ditelan
            status["sumber"][nama] = {"ok": False, "jenis": "galat",
                                      "pesan": f"{type(e).__name__}: {e}"}
            continue

        # Bukti mentah disimpan apa adanya, sebelum diolah. Tidak di-commit.
        os.makedirs(RAW_DIR, exist_ok=True)
        with open(os.path.join(RAW_DIR, f"{cap}-{nama}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        rec = [normalkan(r, nama, ditarik) for r in data]
        cocok = [d for d in rec if d["code"] in wl]
        kumpul += cocok
        status["sumber"][nama] = {
            "ok": True, "jumlah": len(rec), "cocok_watchlist": len(cocok),
            "tanggal_data": max((d["tanggal_terbit_data"] or "" for d in rec), default=None),
            "durasi_ms": int((time.monotonic() - t0) * 1000),
        }

    status["cocok_watchlist"] = len(kumpul)
    status["baru"] = gabung(kumpul) if kumpul else 0
    status["ok"] = any(s.get("ok") for s in status["sumber"].values())
    _tulis_atomik(STATUS_FILE, status)
    return status
