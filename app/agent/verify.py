"""Tahap 4 — pemeriksa. Deterministik, dan satu-satunya yang boleh menolak.

Di sinilah letak pertahanan produk ini. Model boleh saja keliru, tertipu teks di dalam
dokumen, atau berhalusinasi angka. Yang tidak boleh terjadi adalah angka keliru
**terbit sebagai peringatan**. Jadi setiap klaim model diuji balik ke dokumen sumbernya
dengan aritmetika dan pencocokan teks — bukan dengan model kedua yang menilai model
pertama, karena dua model yang salah bersama tetap salah.

Tiap pemeriksaan mengembalikan alasan, lolos maupun gagal. Alasan itulah isi layar
jejak audit, dan bukti paling langsung untuk kriteria Safety.
"""

from __future__ import annotations

import re

from . import extract, llm, recompute

# Sebuah pengumuman tunggal yang mengubah input valuasi lebih dari sekian kali lipat
# hampir pasti kesalahan satuan atau salah tarik butir, bukan temuan nyata. Angka di
# luar pita ini tidak dibuang — ia ditolak terbit dan diteruskan ke manusia.
PITA_BAWAH = 0.2
PITA_ATAS = 3.0

# Sirkularitas: g hasil reverse dimasukkan kembali wajib mengembalikan EV yang sama.
# Selisih di atas ini berarti ada bug aritmetika, bukan temuan pasar.
BATAS_DRIFT_PERSEN = 1e-6


def _angka_saja(s: str) -> str:
    return re.sub(r"[^\d]", "", s or "")


def _cek(nama: str, lolos: bool, alasan: str) -> dict:
    return {"nama": nama, "lolos": lolos, "alasan": alasan}


def periksa(temuan: dict, detail: dict, d_valuasi: dict) -> list[dict]:
    """Pemeriksaan sebelum angka boleh menyentuh kalkulator."""
    dokumen = llm.dokumen_teks(detail)
    cek: list[dict] = []

    # 1 — label butir harus memang menyatakan jumlah untuk input yang diklaim.
    # Ini yang menangkap kutipan dari butir catatan seperti 其他應敘明事項, tempat
    # teks yang berusaha mengarahkan agent biasanya diselipkan.
    sah = extract.LABEL_SAH.get(temuan.get("input"), ())
    label = (temuan.get("label") or "").strip()
    cek.append(_cek(
        "Label butir sah untuk input ini",
        label in sah,
        f"Label '{label}' {'ada' if label in sah else 'TIDAK ada'} dalam daftar label sah "
        f"untuk {temuan.get('input')}: {', '.join(sah) or '(kosong)'}"))

    # 2 — kalimat yang dikutip harus benar-benar ada di dokumen.
    kutipan = (temuan.get("kutipan") or "").strip()
    isi_kutipan = kutipan.split(":", 1)[-1].strip() if ":" in kutipan else kutipan
    ada_kutipan = bool(isi_kutipan) and isi_kutipan in dokumen
    cek.append(_cek(
        "Kutipan ditemukan di dokumen sumber",
        ada_kutipan,
        "Kutipan cocok dengan isi dokumen" if ada_kutipan
        else f"Kutipan '{isi_kutipan[:60]}' tidak ditemukan di dokumen — kemungkinan dikarang"))

    # 3 — digit angkanya harus ada di dokumen. Koma diabaikan supaya
    # '1,480,000,000' dan '1480000000' dianggap sama.
    digit = _angka_saja(temuan.get("nilai_mentah", ""))
    ada_angka = bool(digit) and digit in _angka_saja(dokumen)
    cek.append(_cek(
        "Angka ditemukan di dokumen sumber",
        ada_angka,
        f"Angka {temuan.get('nilai_mentah')} ada di dokumen" if ada_angka
        else f"Angka {temuan.get('nilai_mentah')} TIDAK ada di dokumen — halusinasi"))

    # 4 — mata uang. Model valuasi seluruhnya NTD dan tidak memuat kurs.
    mu = temuan.get("mata_uang")
    mu_ok = mu in (None, "TWD")
    cek.append(_cek(
        "Mata uang didukung model",
        mu_ok,
        "NTD (diasumsikan, sesuai konvensi MOPS)" if mu is None
        else ("NTD" if mu_ok else
              f"Jumlah berdenominasi {mu}. Model valuasi tidak memuat kurs, "
              f"jadi angka ini tidak boleh dikonversi diam-diam.")))

    # 5 — satuan harus dikenali, karena selisihnya seribu kali lipat.
    tok = temuan.get("satuan")
    cek.append(_cek(
        "Satuan dikenali",
        tok in extract.SATUAN,
        f"Satuan '{tok}' dikenali (pengali {extract.SATUAN.get(tok)} ke juta NTD)"
        if tok in extract.SATUAN
        else f"Satuan '{tok}' tidak dikenali — tidak bisa dikonversi dengan aman"))

    # 6 — hasil konversi harus ada. Kalau None, salah satu di atas menggagalkannya.
    nilai = temuan.get("nilai_juta_ntd")
    cek.append(_cek(
        "Nilai terkonversi tersedia",
        nilai is not None,
        f"{nilai:,.0f} juta NTD" if nilai is not None
        else "Konversi tidak dilakukan — gagal-tertutup karena satuan atau mata uang"))

    # 7 — besaran harus masuk akal dibanding nilai yang berlaku sekarang.
    lama = recompute.nilai_sekarang(d_valuasi, temuan.get("input"))
    if nilai is None or not lama:
        cek.append(_cek("Besaran masuk akal", False,
                        "Tidak bisa dinilai — nilai baru atau nilai lama tidak tersedia"))
    else:
        rasio = nilai / lama
        wajar = PITA_BAWAH <= rasio <= PITA_ATAS
        cek.append(_cek(
            "Besaran masuk akal",
            wajar,
            f"{nilai:,.0f} berbanding {lama:,.0f} juta NTD = {rasio:.2f}× "
            f"({'dalam' if wajar else 'DI LUAR'} pita {PITA_BAWAH}–{PITA_ATAS}×)"
            + ("" if wajar else ". Satu pengumuman yang menggeser input sebesar ini "
                                "hampir pasti salah satuan atau salah butir.")))

    return cek


def periksa_hasil(hasil: dict) -> list[dict]:
    """Pemeriksaan setelah kalkulator jalan."""
    drift = hasil["sesudah"]["circularity"]["drift_pct"]
    utuh = drift < BATAS_DRIFT_PERSEN
    return [_cek(
        "Sirkularitas utuh",
        utuh,
        f"g dimasukkan kembali mengembalikan EV yang sama (selisih {drift:.2e}%)" if utuh
        else f"Selisih sirkularitas {drift:.2e}% di atas batas — ada bug aritmetika")]


def vonis(cek: list[dict]) -> dict:
    gagal = [c for c in cek if not c["lolos"]]
    return {
        "lolos": not gagal,
        "jumlah_cek": len(cek),
        "jumlah_gagal": len(gagal),
        "sebab": [c["nama"] + " — " + c["alasan"] for c in gagal],
    }
