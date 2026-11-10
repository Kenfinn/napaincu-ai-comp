"""Tahap TRIAGED — skor keyakinan bahwa sebuah pengumuman layak menjadi peringatan.

Pertanyaannya bukan "angkanya benar?" (itu urusan pemeriksa), melainkan "apakah ini
cukup penting untuk mengganggu investor?". Pengumuman pasal 20 sebagian besar berupa
sewa kantor, mesin kecil, atau produk investasi bernilai remeh dibanding ukuran
perusahaan. Menerbitkan semuanya membuat peringatan yang penting tenggelam.

Skor dihitung **oleh kode, dari komponen yang bisa dijelaskan**, bukan diminta dari
model. Model tidak menilai keyakinannya sendiri: angka keyakinan yang dikarang model
tidak terkalibrasi dan tidak bisa diaudit. Setiap komponen tercatat di jejak bersama
nilainya, jadi juri dan investor bisa melihat persis kenapa sebuah pengumuman lolos
atau diarsipkan.

    dasar          pasal dikenal menyentuh valuasi 0,55 · nomor pasal tak terbaca 0,45
    angka          ada angka terbukti (kutipan & digit ada di dokumen)
                   yang bisa dikonversi ke juta NTD                     +0,10
    materialitas   jumlah terbesar ÷ kapitalisasi pasar
                     ≥ 2%      material                                +0,20
                     ≥ 0,5%    cukup material                          +0,10
                     ≥ 0,05%   kecil                                   −0,05
                     < 0,05%   remeh                                   −0,20
                   kapitalisasi tidak diketahui                         0 (dicatat)

Skor dibandingkan dengan ambang per pasal (app/umpan_balik.py) yang digeser oleh 👍/👎:

    skor ≥ ambang                 → lanjut ke pemeriksa
    ambang − 0,05 ≤ skor < ambang → HELD (keyakinan rendah), manusia memutuskan
    skor < ambang − 0,05          → ARCHIVED, dengan skor dan ambangnya sebagai alasan
"""

from __future__ import annotations

from ..i18n import pesan

DASAR = 0.55
DASAR_TANPA_PASAL = 0.45
BOBOT_ANGKA = 0.10
ZONA_RAGU = 0.05

# (rasio minimum terhadap kapitalisasi, bobot, kode pesan)
PITA_MATERIAL = (
    (0.02, 0.20, "tri.mat_besar"),
    (0.005, 0.10, "tri.mat_sedang"),
    (0.0005, -0.05, "tri.mat_kecil"),
    (0.0, -0.20, "tri.mat_remeh"),
)


def _komponen(kode: str, bobot: float, **param) -> dict:
    return {"kode": kode, "nilai": round(bobot, 2), "pesan": pesan(kode, **param)}


def skor(saring: dict, temuan: list[dict], skala: dict | None,
         terbukti: list[bool] | None = None) -> dict:
    """Skor keyakinan 0–1 beserta komponennya. Deterministik: masukan sama → skor sama.

    `terbukti[i]` = temuan ke-i lolos cek sumber (label, kutipan, digit). Hanya temuan
    terbukti yang dihitung untuk angka dan materialitas; sisanya urusan pemeriksa.
    """
    if terbukti is not None:
        temuan = [t for t, ok in zip(temuan, terbukti) if ok]
    komponen = []
    if saring.get("klausa") is None:
        komponen.append(_komponen("tri.dasar_ragu", DASAR_TANPA_PASAL))
    else:
        komponen.append(_komponen("tri.dasar", DASAR, k=saring["klausa"]))

    terkonversi = [t for t in temuan if t.get("nilai_juta_ntd") is not None]
    if terkonversi:
        komponen.append(_komponen("tri.angka", BOBOT_ANGKA, n=len(terkonversi)))
    else:
        komponen.append(_komponen("tri.angka_x", 0.0))

    nilai = max((t["nilai_juta_ntd"] for t in terkonversi), default=None)
    rasio = None
    if nilai is not None and skala and skala.get("juta_ntd"):
        rasio = nilai / skala["juta_ntd"]
        for batas, bobot, kode in PITA_MATERIAL:
            if rasio >= batas:
                pct = round(rasio * 100, 2) if rasio * 100 >= 0.01 else "<0.01"
                komponen.append(_komponen(kode, bobot, nilai=round(nilai, 2),
                                          kap=round(skala["juta_ntd"]), pct=pct))
                break
    else:
        komponen.append(_komponen("tri.mat_na", 0.0))

    total = min(0.99, max(0.01, sum(k["nilai"] for k in komponen)))
    return {"skor": round(total, 2), "komponen": komponen, "rasio_kapitalisasi": rasio,
            "nilai_terbesar": nilai, "skala": skala}


def putuskan(nilai_skor: float, ambang: float) -> str:
    """'lanjut', 'ragu' (HELD untuk manusia), atau 'arsip'."""
    # Pembulatan supaya 0,55 vs 0,55 tidak jatuh ke sisi yang salah karena galat float.
    s, a = round(nilai_skor, 4), round(ambang, 4)
    if s >= a:
        return "lanjut"
    if s >= round(a - ZONA_RAGU, 4):
        return "ragu"
    return "arsip"
