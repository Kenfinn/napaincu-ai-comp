"""Ambang sinyal per profil risiko (keputusan tim 11 Nov, docs/pemetaan-pasal.md).

Satu tempat untuk semua ambang B1. Ubah angka di sini tanpa menyentuh kode lain.

Cara pakai:
- Agent menghitung angka SEKALI (rasio, persen), sama untuk semua orang.
- Profil yang dipilih pengguna (cookie `risiko`, sama dengan tab Ringkasan) hanya
  menentukan label tampilan: serius, perlu diperhatikan, atau info.
- Keputusan server (HELD untuk manusia, ARCHIVED) memakai PROFIL_SERVER untuk ambang
  "serius", dan profil paling longgar ambangnya (konservatif) untuk materialitas, supaya
  tidak ada pengumuman yang diarsipkan padahal masih relevan bagi profil mana pun.

Angka moderat: jawaban Patrice. Konservatif dan agresif: usulan Claude, menunggu cek tim.
"""

from __future__ import annotations

PROFIL = ("konservatif", "moderat", "agresif")
PROFIL_SERVER = "moderat"

AMBANG: dict[str, dict[str, float | str]] = {
    "konservatif": {"ekuitas": 0.50, "limit": 0.70, "saham": 0.005, "uang": 0.01, "tutup_rugi": "perhatian",
                    "utang": 0.50, "pejabat_kunci": "perhatian"},
    "moderat":     {"ekuitas": 0.80, "limit": 0.80, "saham": 0.01, "uang": 0.02, "tutup_rugi": "perhatian",
                    "utang": 0.60, "pejabat_kunci": "info"},
    "agresif":     {"ekuitas": 1.00, "limit": 0.90, "saham": 0.02, "uang": 0.05, "tutup_rugi": "info",
                    "utang": 0.75, "pejabat_kunci": "info"},
}

URUT = {"info": 0, "perhatian": 1, "serius": 2}


def normal(profil: str | None) -> str:
    return profil if profil in AMBANG else PROFIL_SERVER


def materialitas_terendah() -> dict[str, float]:
    """Ambang materialitas paling longgar di antara semua profil (untuk keputusan arsip)."""
    return {k: min(float(AMBANG[p][k]) for p in PROFIL) for k in ("saham", "uang")}


def tingkat(sinyal: dict | None, profil: str | None) -> dict | None:
    """Label tampilan sinyal untuk satu profil: {"tingkat", "alasan": [(kode, param)]}."""
    if not sinyal:
        return None
    a = AMBANG[normal(profil)]
    jenis = sinyal.get("jenis")
    alasan: list[tuple[str, dict]] = []
    t = "info"

    if jenis in ("penjaminan", "pinjaman"):
        re_ = sinyal.get("rasio_ekuitas")
        pl = sinyal.get("pemakaian_limit")
        if re_ is not None and re_ >= a["ekuitas"]:
            t = "serius"
            alasan.append(("tg.ekuitas", {"nilai": round(re_ * 100, 2), "ambang": round(a["ekuitas"] * 100)}))
        if pl is not None and pl >= a["limit"]:
            t = "serius"
            alasan.append(("tg.limit", {"nilai": round(pl * 100, 1), "ambang": round(a["limit"] * 100)}))
        if sinyal.get("pihak_luar"):
            alasan.append(("tg.pihak_luar", {}))
            if t == "info":
                t = "perhatian"
        if not alasan:
            alasan.append(("tg.di_bawah", {"ekuitas": round(a["ekuitas"] * 100), "limit": round(a["limit"] * 100)}))
    elif jenis == "modal":
        sub = sinyal.get("subjenis")
        if sub == "tutup_rugi":
            t = str(a["tutup_rugi"])
            alasan.append(("tg.tutup_rugi", {}))
        elif sub in ("kas_kembali", "obligasi"):
            t = "perhatian"
            alasan.append((f"tg.{sub}", {}))
        else:
            ps, pk = sinyal.get("persen_saham"), sinyal.get("persen_kapitalisasi")
            if (ps is not None and ps >= a["saham"]) or (pk is not None and pk >= a["uang"]):
                t = "perhatian"
                alasan.append(("tg.material", {"saham": round(a["saham"] * 100, 2), "uang": round(a["uang"] * 100, 2)}))
            else:
                alasan.append(("tg.tak_material", {"saham": round(a["saham"] * 100, 2), "uang": round(a["uang"] * 100, 2)}))
    elif jenis == "laporan":
        if (sinyal.get("laba_induk_juta") or 0) < 0:
            t = "perhatian"
            alasan.append(("tg.rugi", {}))
        ru = sinyal.get("rasio_utang")
        if ru is not None and ru >= a["utang"]:
            t = "perhatian"
            alasan.append(("tg.utang", {"nilai": round(ru * 100, 1), "ambang": round(a["utang"] * 100)}))
    elif jenis == "auditor":
        # Pasal 7 (Patrice): ganti auditor eksternal jarang terjadi, jadi selalu diberi tahu.
        if sinyal.get("auditor_mundur") or sinyal.get("beda_pendapat"):
            t = "serius"
            if sinyal.get("auditor_mundur"):
                alasan.append(("tg.auditor_mundur", {}))
            if sinyal.get("beda_pendapat"):
                alasan.append(("tg.beda_pendapat", {}))
        elif sinyal.get("ganti_kantor"):
            t = "perhatian"
            alasan.append(("tg.ganti_kantor", {}))
        else:
            alasan.append(("tg.rotasi", {}))
    elif jenis == "pejabat":
        # Pasal 8 (Patrice: penting). Jabatan kunci yang keluar mendadak = perlu diperhatikan.
        if sinyal.get("kunci") and sinyal.get("keluar"):
            t = "perhatian"
            alasan.append(("tg.pejabat_keluar", {}))
        elif sinyal.get("kunci"):
            t = str(a["pejabat_kunci"])
            alasan.append(("tg.pejabat_kunci", {}))
        else:
            alasan.append(("tg.pejabat_lain", {}))
        if sinyal.get("anak_perusahaan"):
            alasan.append(("tg.anak_perusahaan", {}))
    elif jenis == "berat":
        t = "serius"
        alasan.append(("tg.berat", {}))
    return {"tingkat": t, "profil": normal(profil), "alasan": alasan}
