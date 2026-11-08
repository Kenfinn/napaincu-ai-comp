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

from ..i18n import pesan

# PERINGATAN — pemetaan ini masih SEMENTARA.
#
# Nomor pasal di bawah adalah dugaan kerja, belum dicocokkan baris per baris dengan
# daftar resmi 重大訊息 dari regulator. Sebelum masuk deck, PDK atau Ferry wajib
# memverifikasinya terhadap sumber resmi dan mengisi kolom `sumber` di tiap entri.
# Angka yang salah di sini menyaring keluar pengumuman yang justru penting — dan
# kegagalan seperti itu tidak bersuara.
KLAUSA_RELEVAN: dict[int, dict] = {
    11: {
        "nama": "Keputusan dewan direksi atas belanja modal",
        "input": ["capex"],
        "sumber": "BELUM DIVERIFIKASI — cocokkan dengan daftar resmi 重大訊息",
    },
    20: {
        "nama": "Perolehan atau pelepasan aset",
        "input": ["capex", "cash"],
        "sumber": "BELUM DIVERIFIKASI — cocokkan dengan daftar resmi 重大訊息",
    },
    22: {
        "nama": "Pinjaman dana atau penjaminan signifikan",
        "input": ["debt"],
        "sumber": "BELUM DIVERIFIKASI — cocokkan dengan daftar resmi 重大訊息",
    },
    2: {
        "nama": "Cek kosong, gagal bayar, atau kesulitan keuangan",
        "input": ["debt", "cash"],
        "sumber": "BELUM DIVERIFIKASI — cocokkan dengan daftar resmi 重大訊息",
    },
}


def saring(detail: dict) -> dict:
    """Putuskan apakah pengumuman ini pantas dibawa ke tahap berbiaya."""
    klausa = detail.get("clause")

    if klausa is None:
        # Tanpa nomor pasal kita tidak punya dasar untuk menyaring, dan menebak
        # lebih berbahaya daripada meneruskan. Lolos, tapi ditandai.
        return {
            "lolos": True,
            "klausa": None,
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
        "nama": cocok["nama"],
        "input_mungkin": cocok["input"],
        "alasan": f"Pasal {klausa} — {cocok['nama']}. Dapat menyentuh: "
                  f"{', '.join(cocok['input'])}.",
        "ragu": False,
        "alasan_i18n": {"kode": "saring.cocok",
                        "param": {"k": klausa, "input": ", ".join(cocok["input"])},
                        "param_kode": {"nama": f"klausa.{klausa}"}},
    }
