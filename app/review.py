"""Antrean review manusia (HELD FOR REVIEW, brief hal. 7) dan keputusan atasnya.

Keputusan disimpan terpisah dari hasil pipeline, lalu diterapkan setiap kali pipeline
berjalan. Jadi memproses ulang pengumuman tidak menghapus keputusan manusia, dan
keputusan selalu tampil sebagai langkah terakhir di jejak audit.

Aturan persetujuan (keputusan tim, 10 Nov):
    Boleh disetujui untuk terbit  → hanya kasus RAGU: mata uang asing, besaran di luar
                                     pita, belum ada model valuasi, nomor pasal tidak terbaca
    Boleh disetujui untuk lanjut   → keyakinan triase rendah: persetujuan meneruskan kasus
                                     ke pemeriksa, BUKAN langsung menerbitkannya
    Hanya boleh diarsipkan         → kutipan atau angka tidak ada di dokumen, label butir
                                     tidak sah, satuan tidak dikenali, sirkularitas rusak
                                     (tanda halusinasi atau bug, bukan keraguan)
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone

from . import config

KEPUTUSAN_FILE = os.path.join(config.DATA_DIR, "keputusan_review.json")
KEPUTUSAN_SAH = ("setujui", "arsipkan")
_kunci_berkas = threading.Lock()

# Pemeriksaan yang kegagalannya berarti "ragu", bukan "salah".
CEK_RAGU = {"cek.mu", "cek.konversi", "cek.besaran"}


def baca() -> dict[str, dict]:
    if not os.path.exists(KEPUTUSAN_FILE):
        return {}
    with open(KEPUTUSAN_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _kunci(pengenal: str, jenis: str | None) -> str:
    return f"{pengenal}#{jenis}" if jenis else pengenal


def untuk(pengenal: str, jenis: str | None, semua: dict | None = None) -> dict | None:
    """Keputusan atas satu kasus untuk SATU jenis penahanan.

    Satu pengumuman bisa ditahan dua kali dengan sebab berbeda: keyakinan rendah di
    triase, lalu (setelah disetujui lanjut) mata uang asing di pemeriksa. Persetujuan
    pertama tidak boleh ikut menyetujui yang kedua, jadi keputusan disimpan per jenis.
    Keputusan lama tanpa jenis (sebelum 11 Nov) tetap berlaku untuk jenis apa pun.
    """
    semua = semua if semua is not None else baca()
    return semua.get(_kunci(pengenal, jenis)) or (
        semua.get(pengenal) if not (semua.get(pengenal) or {}).get("jenis") else None)


def simpan(pengenal: str, keputusan: str, catatan: str, jenis: str | None = None) -> dict:
    if keputusan not in KEPUTUSAN_SAH:
        raise ValueError(f"keputusan tidak dikenal: {keputusan}")
    with _kunci_berkas:
        semua = baca()
        entri = {"id": pengenal, "jenis": jenis, "keputusan": keputusan, "catatan": catatan.strip()[:500],
                 "waktu": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        semua[_kunci(pengenal, jenis)] = entri
        os.makedirs(os.path.dirname(KEPUTUSAN_FILE), exist_ok=True)
        tmp = f"{KEPUTUSAN_FILE}.{os.getpid()}.{threading.get_ident()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(semua, f, ensure_ascii=False, indent=2)
        os.replace(tmp, KEPUTUSAN_FILE)
    return entri


def boleh_setujui_temuan(gagal_kode: list[str]) -> bool:
    """Temuan yang gagal pemeriksa boleh disetujui hanya bila semua kegagalannya 'ragu'."""
    return bool(gagal_kode) and set(gagal_kode) <= CEK_RAGU
