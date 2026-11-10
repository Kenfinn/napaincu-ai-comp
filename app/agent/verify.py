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
from ..i18n import pesan

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


def _rb(x: float, desimal: int = 0) -> str:
    """Format angka gaya Indonesia: titik ribuan, koma desimal.

    Dipakai untuk angka HASIL HITUNGAN kita. Angka yang dikutip dari dokumen
    sengaja tidak diformat ulang — itu sitasi, dan sitasi harus apa adanya supaya
    juri bisa mencocokkannya huruf per huruf dengan halaman MOPS.
    """
    return f"{x:,.{desimal}f}".replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def _cek(nama: str, lolos: bool, alasan: str, kunci: str | None = None,
         kunci_alasan: str | None = None, **param) -> dict:
    """Satu pemeriksaan. `nama`/`alasan` Indonesia tetap disimpan untuk JSON mentah;
    kode + parameter dipakai layar untuk menampilkannya dalam tiga bahasa."""
    c = {"nama": nama, "lolos": lolos, "alasan": alasan}
    if kunci:
        c["nama_i18n"] = pesan(kunci)
        c["alasan_i18n"] = pesan(kunci_alasan or f"{kunci}.{'ok' if lolos else 'x'}", **param)
    return c


_SATUAN_RE = re.compile("|".join(re.escape(k) for k in sorted(extract.SATUAN, key=len, reverse=True)))


def _satuan_tertulis(teks: str) -> set[str]:
    """Token satuan di teks, dicocokkan dari yang terpanjang (仟元 tidak terhitung 元)."""
    return set(_SATUAN_RE.findall(teks or ""))


def _label_butir(detail: dict, temuan: dict) -> str:
    """Label lengkap butir yang dikutip (satuan sering hanya di label, mis. 餘額(仟元))."""
    for it in detail.get("items", []):
        for b in [it] + it.get("sub", []):
            if b.get("no") == temuan.get("butir_no") or (
                    temuan.get("label") and b.get("label") == temuan.get("label")):
                if extract.label_sah(b.get("label", ""), temuan.get("input")) or b.get("label") == temuan.get("label"):
                    return b.get("label_lengkap") or b.get("label", "")
    return ""


def sumber_terbukti(temuan: dict, detail: dict, dokumen: str | None = None) -> bool:
    """Tiga cek sumber pertama saja (label sah, kutipan ada, digit ada) — tanpa valuasi.

    Dipakai triase: materialitas hanya boleh dinilai dari angka yang bisa ditelusuri ke
    dokumen. Kalau tidak, angka karangan yang kecil akan mengarsipkan pengumuman penting
    sebelum pemeriksa sempat menolaknya, dan jejaknya menyebut sebab yang salah.
    """
    dokumen = dokumen if dokumen is not None else llm.dokumen_teks(detail)
    if not extract.label_sah((temuan.get("label") or "").strip(), temuan.get("input")):
        return False
    kutipan = (temuan.get("kutipan") or "").strip()
    isi = kutipan.split(":", 1)[-1].strip() if ":" in kutipan else kutipan
    digit = _angka_saja(temuan.get("nilai_mentah", ""))
    return bool(isi) and isi in dokumen and bool(digit) and digit in _angka_saja(dokumen)


def periksa(temuan: dict, detail: dict, d_valuasi: dict) -> list[dict]:
    """Pemeriksaan sebelum angka boleh menyentuh kalkulator."""
    dokumen = llm.dokumen_teks(detail)
    cek: list[dict] = []

    # 1 — label butir harus memang menyatakan jumlah untuk input yang diklaim.
    # Ini yang menangkap kutipan dari butir catatan seperti 其他應敘明事項, tempat
    # teks yang berusaha mengarahkan agent biasanya diselipkan.
    sah = extract.LABEL_SAH.get(temuan.get("input"), ())
    label = (temuan.get("label") or "").strip()
    sah_ok = extract.label_sah(label, temuan.get("input"))
    cek.append(_cek(
        "Label butir sah untuk input ini",
        sah_ok,
        f"Label '{label}' {'ada' if sah_ok else 'TIDAK ada'} dalam daftar label sah "
        f"untuk {temuan.get('input')}: {', '.join(sah) or '(kosong)'}",
        "cek.label", label=label, input=temuan.get("input"), sah=", ".join(sah) or "—"))

    # 2 — kalimat yang dikutip harus benar-benar ada di dokumen.
    kutipan = (temuan.get("kutipan") or "").strip()
    isi_kutipan = kutipan.split(":", 1)[-1].strip() if ":" in kutipan else kutipan
    ada_kutipan = bool(isi_kutipan) and isi_kutipan in dokumen
    cek.append(_cek(
        "Kutipan ditemukan di dokumen sumber",
        ada_kutipan,
        "Kutipan cocok dengan isi dokumen" if ada_kutipan
        else f"Kutipan '{isi_kutipan[:60]}' tidak ditemukan di dokumen — kemungkinan dikarang",
        "cek.kutipan", kutipan=isi_kutipan[:60]))

    # 3 — digit angkanya harus ada di dokumen. Koma diabaikan supaya
    # '1,480,000,000' dan '1480000000' dianggap sama.
    digit = _angka_saja(temuan.get("nilai_mentah", ""))
    ada_angka = bool(digit) and digit in _angka_saja(dokumen)
    cek.append(_cek(
        "Angka ditemukan di dokumen sumber",
        ada_angka,
        f"Angka {temuan.get('nilai_mentah')} ada di dokumen" if ada_angka
        else f"Angka {temuan.get('nilai_mentah')} TIDAK ada di dokumen — halusinasi",
        "cek.angka", angka=temuan.get("nilai_mentah")))

    # 4 — mata uang. Model valuasi seluruhnya NTD dan tidak memuat kurs.
    mu = temuan.get("mata_uang")
    mu_ok = mu in (None, "TWD")
    cek.append(_cek(
        "Mata uang didukung model",
        mu_ok,
        "NTD (diasumsikan, sesuai konvensi MOPS)" if mu is None
        else ("NTD" if mu_ok else
              f"Jumlah berdenominasi {mu}. Model valuasi tidak memuat kurs, "
              f"jadi angka ini tidak boleh dikonversi diam-diam."),
        "cek.mu", "cek.mu.asumsi" if mu is None else ("cek.mu.ok" if mu_ok else "cek.mu.x"), mu=mu))

    # 5 — satuan harus dikenali, DAN benar-benar tertulis di kutipan atau di label butir
    # yang dikutip. Tanpa syarat kedua, penyari yang tertipu bisa mengklaim 仟元 untuk
    # angka yang di dokumen tertulis 元 (selisih seribu kali) dan lolos cek ini.
    tok = temuan.get("satuan")
    tertulis = _satuan_tertulis(isi_kutipan) | _satuan_tertulis(_label_butir(detail, temuan))
    dikenali = tok in extract.SATUAN
    sat_ok = dikenali and tok in tertulis
    cek.append(_cek(
        "Satuan dikenali",
        sat_ok,
        f"Satuan '{tok}' dikenali (pengali {extract.SATUAN.get(tok)} ke juta NTD) dan tertulis di sumber"
        if sat_ok
        else (f"Satuan '{tok}' tidak tertulis di kutipan maupun label butir (tertulis: "
              f"{', '.join(sorted(tertulis)) or '—'})" if dikenali
              else f"Satuan '{tok}' tidak dikenali — tidak bisa dikonversi dengan aman"),
        "cek.satuan", "cek.satuan.ok" if sat_ok else ("cek.satuan.beda" if dikenali else "cek.satuan.x"),
        satuan=tok, pengali=str(extract.SATUAN.get(tok)), tertulis=", ".join(sorted(tertulis)) or "—"))

    # 6 — hasil konversi harus ada. Kalau None, salah satu di atas menggagalkannya.
    nilai = temuan.get("nilai_juta_ntd")
    cek.append(_cek(
        "Nilai terkonversi tersedia",
        nilai is not None,
        f"{_rb(nilai)} juta NTD" if nilai is not None
        else "Konversi tidak dilakukan — gagal-tertutup karena satuan atau mata uang",
        "cek.konversi", nilai=nilai))

    # 7 — besaran harus masuk akal dibanding nilai yang berlaku sekarang.
    lama = recompute.nilai_sekarang(d_valuasi, temuan.get("input"))
    if nilai is None or not lama:
        cek.append(_cek("Besaran masuk akal", False,
                        "Tidak bisa dinilai — nilai baru atau nilai lama tidak tersedia",
                        "cek.besaran", "cek.besaran.na"))
    else:
        rasio = nilai / lama
        wajar = PITA_BAWAH <= rasio <= PITA_ATAS
        cek.append(_cek(
            "Besaran masuk akal",
            wajar,
            f"{_rb(nilai)} berbanding {_rb(lama)} juta NTD = {_rb(rasio, 2)}× "
            f"({'dalam' if wajar else 'DI LUAR'} pita {_rb(PITA_BAWAH, 1)}–{_rb(PITA_ATAS, 1)}×)"
            + ("" if wajar else ". Satu pengumuman yang menggeser input sebesar ini "
                                "hampir pasti salah satuan atau salah butir."),
            "cek.besaran", nilai=nilai, lama=lama, rasio=round(rasio, 2),
            bawah=PITA_BAWAH, atas=PITA_ATAS))

    return cek


def periksa_hasil(hasil: dict) -> list[dict]:
    """Pemeriksaan setelah kalkulator jalan."""
    drift = hasil["sesudah"]["circularity"]["drift_pct"]
    utuh = drift < BATAS_DRIFT_PERSEN
    return [_cek(
        "Sirkularitas utuh",
        utuh,
        f"g dimasukkan kembali mengembalikan EV yang sama (selisih {drift:.2e}%)" if utuh
        else f"Selisih sirkularitas {drift:.2e}% di atas batas — ada bug aritmetika",
        "cek.sirkular", drift=f"{drift:.2e}")]


def vonis(cek: list[dict]) -> dict:
    gagal = [c for c in cek if not c["lolos"]]
    return {
        "lolos": not gagal,
        "jumlah_cek": len(cek),
        "jumlah_gagal": len(gagal),
        "sebab": [c["nama"] + " — " + c["alasan"] for c in gagal],
        "sebab_i18n": [{"nama": c.get("nama_i18n") or c["nama"],
                        "alasan": c.get("alasan_i18n") or c["alasan"]} for c in gagal],
    }
