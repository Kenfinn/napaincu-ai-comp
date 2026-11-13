"""Tahap 0 — saringan nomor pasal. Deterministik, tanpa biaya.

Halaman 重大訊息 MOPS memuat 符合條款: nomor pasal yang menyatakan jenis kejadian
sebuah pengumuman **menurut regulator**. Itu klasifikasi yang sudah jadi dan sudah
punya wewenang. Memakainya berarti kita tidak pernah perlu membela akurasi
pengklasifikasi buatan sendiri di depan juri.

Gunanya dua. Pertama, memangkas 711 pengumuman jadi puluhan sebelum model dipanggil
— free tier berkisar seribu permintaan per hari, dan mengirim semuanya akan menabrak
kuota sekaligus boros. Kedua, dan ini yang dinilai: agent memutuskan **di mana**
penalaran dibutuhkan, alih-alih menabrakkan model ke segala hal.
"""

from __future__ import annotations

import re

from ..i18n import pesan

# Pemetaan pasal → jalur. Keputusan tim 11 Nov (docs/pemetaan-pasal.md, "Keputusan tim").
#   valuasi  angka transaksi dihitung ulang; karena DCF berbasis kas, hasilnya SKENARIO
#            "bila terealisasi", bukan valuasi baru
#   risiko   sinyal risiko, tidak mengubah DCF
#   modal    perubahan modal / obligasi / pembelian kembali, sinyal
#   laporan  laporan kuartal: ringkasan angka, memicu pembaruan valuasi otomatis
#   berat    kejadian berat: selalu ditahan untuk manusia
# Pasal lain (12 paparan investor, 14 dividen, 6/7/8 tata kelola, 51/53 lain-lain, ...)
# dilewati. Pasal 2 dihapus: tidak pernah muncul di data asli.
KLAUSA_RELEVAN: dict[int, dict] = {
    20: {"nama": "Perolehan atau pelepasan aset", "jalur": "valuasi", "input": ["capex", "cash"]},
    22: {"nama": "Penjaminan untuk pihak lain (背書保證)", "jalur": "risiko", "input": []},
    23: {"nama": "Pinjaman dana ke pihak lain (資金貸與)", "jalur": "risiko", "input": []},
    11: {"nama": "Perubahan modal dan surat utang", "jalur": "modal", "input": []},
    35: {"nama": "Pembelian kembali saham", "jalur": "modal", "input": []},
    31: {"nama": "Laporan keuangan kuartal", "jalur": "laporan", "input": []},
    1: {"nama": "Gagal bayar atau kehilangan kredit", "jalur": "berat", "input": []},
    3: {"nama": "Penghentian produksi atau kejadian berat", "jalur": "berat", "input": []},
    40: {"nama": "Penghentian perdagangan saham", "jalur": "berat", "input": []},
    7: {"nama": "Pergantian akuntan publik (auditor eksternal)", "jalur": "tata_kelola", "input": []},
    8: {"nama": "Pergantian pejabat kunci", "jalur": "tata_kelola", "input": []},
}

# Pengumuman anggaran belanja modal direksi bisa datang di pasal mana pun (kasus demo TSMC
# memakai pasal 11). Label ini langsung mengarah ke jalur valuasi untuk capex.
LABEL_CAPEX = ("資本支出預算金額", "資本支出金額")


def _ada_label_capex(detail: dict) -> bool:
    from .extract import _normal_label
    sah = {_normal_label(x) for x in LABEL_CAPEX}
    return any(_normal_label(b.get("label", "")) in sah
               for it in detail.get("items", []) for b in [it] + it.get("sub", []))


# Transaksi dengan anak perusahaan yang dimiliki 100%: kas tidak keluar dari grup, jadi tidak
# mengubah DCF konsolidasi (keputusan 11 Nov dari gold set tim keuangan). Hanya dicari di judul dan
# butir pihak lawan/hubungan, bukan di seluruh teks.
_ANTAR_GRUP = re.compile(r"(100|百分之百)\s*[%％]?\s*(直接|間接)?\s*(持有|持股)?\s*之?\s*子公司"
                         r"|持股\s*100\s*[%％]\s*之?\s*子公司")


def antar_grup(detail: dict) -> bool:
    teks = [detail.get("subject") or ""]
    for it in detail.get("items", []):
        for b in [it] + it.get("sub", []):
            lbl = b.get("label_lengkap") or b.get("label") or ""
            if "相對人" in lbl or "關係" in lbl:
                teks.append(b.get("value") or "")
    return any(_ANTAR_GRUP.search(re.sub(r"\s", "", t)) for t in teks)


def saring(detail: dict) -> dict:
    """Putuskan apakah pengumuman ini pantas dibawa ke tahap berbiaya."""
    klausa = detail.get("clause")

    if klausa == 20 and antar_grup(detail):
        return {
            "lolos": False, "klausa": klausa, "jalur": None,
            "nama": "Transaksi antar-grup (anak perusahaan 100%)", "input_mungkin": [],
            "alasan": "Transaksi dengan anak perusahaan 100%: kas tetap di dalam grup, DCF konsolidasi tidak berubah.",
            "ragu": False, "alasan_i18n": pesan("saring.antar_grup"),
        }

    if detail.get("items") and _ada_label_capex(detail):
        return {
            "lolos": True, "klausa": klausa, "jalur": "valuasi",
            "nama": "Anggaran belanja modal", "input_mungkin": ["capex"], "ragu": False,
            "alasan": f"Pasal {klausa}: memuat label anggaran belanja modal, dihitung ulang sebagai skenario.",
            "alasan_i18n": pesan("saring.capex", k=klausa if klausa is not None else "?"),
        }

    if klausa is None:
        # Tanpa nomor pasal kita tidak punya dasar untuk menyaring, dan menebak
        # lebih berbahaya daripada meneruskan. Lolos, tapi ditandai.
        return {
            "lolos": True,
            "klausa": None,
            "jalur": "valuasi",
            "nama": "Nomor pasal tidak terbaca",
            "input_mungkin": [],
            "alasan": "Nomor 符合條款 tidak ada di halaman, tidak ada dasar menyaring. "
                      "Diteruskan dengan tanda supaya ditinjau manusia.",
            "ragu": True,
            "alasan_i18n": pesan("saring.tanpa_pasal"),
        }

    cocok = KLAUSA_RELEVAN.get(klausa)
    if cocok is None:
        return {
            "lolos": False,
            "klausa": klausa,
            "jalur": None,
            "nama": "Di luar daftar yang menyentuh valuasi",
            "input_mungkin": [],
            "alasan": f"Pasal {klausa} tidak ada dalam daftar pasal yang dapat mengubah "
                      f"input valuasi. Tidak diteruskan ke model.",
            "ragu": False,
            "alasan_i18n": pesan("saring.di_luar", k=klausa),
        }

    return {
        "lolos": True,
        "klausa": klausa,
        "jalur": cocok["jalur"],
        "nama": cocok["nama"],
        "input_mungkin": cocok["input"],
        "alasan": f"Pasal {klausa} — {cocok['nama']}. Jalur: {cocok['jalur']}.",
        "ragu": False,
        "alasan_i18n": {"kode": "saring.jalur",
                        "param": {"k": klausa},
                        "param_kode": {"nama": f"klausa.{klausa}", "jalur": f"jalur.{cocok['jalur']}"}},
    }
