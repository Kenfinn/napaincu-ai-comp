"""Ringkasan analisis satu saham — "what do you think of stock X?".

Bentuknya: hasil analisis per aspek, lalu kesimpulan dan apa yang perlu dicek investor.
**Bukan label beli/jual.** Brief hal. 9: saran beli/jual otomatis di Taiwan wajib lewat
perusahaan berizin FSC, jadi produk ini menawarkan riset dan peringatan, keputusan
tetap di tangan investor.

Pembagian kerja sama dengan agent pengumuman:

    Penilaian   KODE   — setiap aspek dinilai dengan aturan tertulis di bawah, dari angka
                         yang bisa ditelusuri (bursa, laporan keuangan, DCF, pengumuman)
    Narasi      MODEL  — Gemini hanya merangkai paragraf dari fakta yang sudah dihitung
    Pemeriksa   KODE   — paragraf ditolak bila memuat angka yang tidak ada di fakta, atau
                         kata beli/jual. Bila ditolak, yang tampil versi template.

AMBANG di bawah adalah aturan kerja sementara. Anggota tim keuangan wajib memverifikasinya sebelum
dipakai di deck (sama seperti daftar pasal di agent/screen.py).
"""

from __future__ import annotations

import json
import os
import re
import sys

from . import config, i18n, pasar, store
from .agent import llm

AMBANG = {
    "per_tinggi": 1.3,      # PER > 1,3 × median industri → mahal dibanding sesama
    "per_rendah": 0.8,      # PER < 0,8 × median industri → lebih murah dari sesama
    "tumbuh_kuat": 0.10,    # pendapatan tahunan YoY > 10 %
    "roe_kuat": 0.15,       # ROE TTM ≥ 15 %
    "roe_lemah": 0.08,      # ROE TTM < 8 %
    "utang_tinggi": 0.60,   # total liabilitas / total aset > 60 %
    "utang_rendah": 0.40,
}

PROFIL_RISIKO = ("konservatif", "moderat", "agresif")

# Kata yang tidak boleh muncul di narasi model (lintas tiga bahasa).
KATA_TERLARANG = ("beli", "jual", "buy", "sell", "買進", "買入", "賣出", "建議買", "建議賣",
                  "target price", "harga target", "目標價", "strong buy", "akumulasi")


def _pct(x: float, bahasa: str, d: int = 1) -> str:
    return f"{i18n.angka(x * 100, bahasa, d)}%"


def _n(x: float, bahasa: str, d: int = 0) -> str:
    return i18n.angka(x, bahasa, d)


def _fakta(aspek: str, arah: int, kunci: str, bahasa: str, tab: str, **param) -> dict:
    return {"aspek": aspek, "arah": arah, "kunci": kunci, "tab": tab,
            "teks": i18n.t(kunci, bahasa, **param)}


def _baris_terakhir(tb: dict, kunci: str) -> tuple[str | None, float | None]:
    for b in tb.get("baris", []):
        if b["kunci"] == kunci:
            for kol, v in zip(tb["kolom"], b["sel"]):
                if v is not None:
                    return kol["label"], v
    return None, None


def susun(kode: str, bahasa: str, risiko: str = "moderat", hasil_agent: list[dict] | None = None) -> dict:
    bahasa = i18n.normal(bahasa)
    risiko = risiko if risiko in PROFIL_RISIKO else "moderat"
    fakta: list[dict] = []

    s = pasar.statistik(kode)
    p = pasar.profil(kode)
    keuangan = bool(p and p.get("keuangan"))
    if keuangan:
        fakta.append(_fakta("sektor", 0, "rk.sektor_keuangan", bahasa, "profil"))

    # 1 — valuasi DCF (hanya emiten yang punya berkas valuasi)
    d = store.muat_valuasi(kode)
    if d is not None and not keuangan:
        if os.path.join(config.ROOT, "scripts") not in sys.path:
            sys.path.insert(0, os.path.join(config.ROOT, "scripts"))
        import copy
        import dcf
        # "Harga sekarang" berarti harga penutupan terakhir dari bursa, bukan harga di
        # berkas valuasi (yang bisa berumur berbulan-bulan). Input lain tetap dari berkas.
        d = copy.deepcopy(d)
        h = s.get("harga") or {}
        if h.get("tutup"):
            d.setdefault("market", {})["price_per_share"] = h["tutup"]
        r = dcf.compute(d, forward_g=d.get("assumptions", {}).get("terminal_growth_ceiling"))
        g, batas = r.get("implied_growth"), r.get("terminal_growth_ceiling")
        if g is not None and batas is not None:
            if g > batas:
                fakta.append(_fakta("valuasi", -1, "rk.dcf.tinggi", bahasa, "valuasi",
                                    g=_pct(g, bahasa), batas=_pct(batas, bahasa)))
            else:
                fakta.append(_fakta("valuasi", 1, "rk.dcf.wajar", bahasa, "valuasi",
                                    g=_pct(g, bahasa), batas=_pct(batas, bahasa)))

    # 2 — PER dibanding median industri di bursa
    per = (s.get("rasio") or {}).get("per")
    ind = pasar.per_industri(kode)
    if per and ind:
        rasio = per / ind["median"]
        nama_ind = i18n.t(f"ind.{ind['industri_kode']}", bahasa)
        prm = dict(per=_n(per, bahasa, 2), median=_n(ind["median"], bahasa, 2),
                   n=ind["jumlah"], industri=ind["industri"] if nama_ind.startswith("⟦") else nama_ind)
        if rasio > AMBANG["per_tinggi"]:
            fakta.append(_fakta("valuasi_relatif", -1, "rk.per.tinggi", bahasa, "stats", **prm))
        elif rasio < AMBANG["per_rendah"]:
            fakta.append(_fakta("valuasi_relatif", 1, "rk.per.rendah", bahasa, "stats", **prm))
        else:
            fakta.append(_fakta("valuasi_relatif", 0, "rk.per.sejalan", bahasa, "stats", **prm))

    # 3 — pertumbuhan pendapatan
    th, yoy_th = _baris_terakhir(pasar.tabel(kode, "lr", "y", "yoy"), "Revenue")
    q, yoy_q = _baris_terakhir(pasar.tabel(kode, "lr", "q", "yoy"), "Revenue")
    if yoy_th is not None:
        prm = dict(th=th, yoy=_pct(yoy_th, bahasa),
                   q=q or "—", yoy_q=_pct(yoy_q, bahasa) if yoy_q is not None else "—")
        if yoy_th > AMBANG["tumbuh_kuat"]:
            fakta.append(_fakta("pertumbuhan", 1, "rk.tumbuh.kuat", bahasa, "keu", **prm))
        elif yoy_th >= 0:
            fakta.append(_fakta("pertumbuhan", 0, "rk.tumbuh.sedang", bahasa, "keu", **prm))
        else:
            fakta.append(_fakta("pertumbuhan", -1, "rk.tumbuh.turun", bahasa, "keu", **prm))

    # 4 — profitabilitas
    roe, mb = s.get("roe"), s.get("margin_bersih")
    if roe is not None:
        prm = dict(roe=_pct(roe, bahasa), mb=_pct(mb, bahasa) if mb is not None else "—")
        if roe >= AMBANG["roe_kuat"]:
            fakta.append(_fakta("profitabilitas", 1, "rk.roe.kuat", bahasa, "stats", **prm))
        elif roe < AMBANG["roe_lemah"]:
            fakta.append(_fakta("profitabilitas", -1, "rk.roe.lemah", bahasa, "stats", **prm))
        else:
            fakta.append(_fakta("profitabilitas", 0, "rk.roe.sedang", bahasa, "stats", **prm))

    # 5 — struktur utang (tidak berlaku untuk sektor keuangan)
    if not keuangan:
        nr = pasar.tabel(kode, "neraca", "q")
        _, liab = _baris_terakhir(nr, "Liabilities")
        kol, aset = _baris_terakhir(nr, "TotalAssets")
        if liab is not None and aset:
            rasio = liab / aset
            prm = dict(rasio=_pct(rasio, bahasa), q=kol)
            if rasio > AMBANG["utang_tinggi"]:
                fakta.append(_fakta("utang", -1, "rk.utang.tinggi", bahasa, "keu", **prm))
            elif rasio < AMBANG["utang_rendah"]:
                fakta.append(_fakta("utang", 1, "rk.utang.rendah", bahasa, "keu", **prm))
            else:
                fakta.append(_fakta("utang", 0, "rk.utang.sedang", bahasa, "keu", **prm))

    # 6 — arus kas bebas tahunan terakhir
    th_f, fcf = _baris_terakhir(pasar.tabel(kode, "arus", "y"), "FreeCashFlow")
    if fcf is not None and not keuangan:
        prm = dict(th=th_f, fcf=_n(fcf, bahasa))
        fakta.append(_fakta("arus_kas", 1 if fcf > 0 else -1,
                            "rk.fcf.positif" if fcf > 0 else "rk.fcf.negatif", bahasa, "keu", **prm))

    # 7 — pengumuman yang diproses agent
    milik = [h for h in (hasil_agent or []) if (h.get("emiten") or {}).get("kode") == kode
             and not h.get("contoh")]
    terbit = [h for h in milik if h["status"] == "terbit"]
    tunggu = [h for h in milik if h["status"] in ("ditahan", "ditolak")]
    if terbit:
        h = max(terbit, key=lambda x: x.get("tanggal") or "")
        fakta.append(_fakta("pengumuman", 0, "rk.umum.terbit", bahasa, "stream",
                            n=len(terbit), tgl=h.get("tanggal"), judul=h.get("judul") or ""))
    if tunggu:
        fakta.append(_fakta("pengumuman", 0, "rk.umum.tunggu", bahasa, "stream", n=len(tunggu)))
    if not terbit and not tunggu:
        fakta.append(_fakta("pengumuman", 0, "rk.umum.kosong", bahasa, "stream"))

    # --- kesimpulan ------------------------------------------------------------
    kuat = [f for f in fakta if f["arah"] > 0]
    awas = [f for f in fakta if f["arah"] < 0]
    if len(kuat) >= 2 and not awas:
        kes = "rk.k.positif"
    elif kuat and awas:
        kes = "rk.k.campuran"
    elif len(awas) >= 2 and not kuat:
        kes = "rk.k.waspada"
    else:
        kes = "rk.k.terbatas"

    batas_awas = {"konservatif": 1, "moderat": 2, "agresif": 3}[risiko]
    cocok = "rk.p.hati" if len(awas) >= batas_awas else "rk.p.aman"
    cek = [i18n.t(f"rk.cek.{f['aspek']}", bahasa) for f in awas
           if not i18n.t(f"rk.cek.{f['aspek']}", bahasa).startswith("⟦")]

    hasil = {
        "kode": kode, "bahasa": bahasa, "risiko": risiko,
        "fakta": fakta, "kuat": kuat, "awas": awas,
        "kesimpulan": i18n.t(kes, bahasa, kuat=len(kuat), awas=len(awas)),
        "kecocokan": i18n.t(cocok, bahasa, profil=i18n.t(f"rk.risiko.{risiko}", bahasa)),
        "cek": cek,
        "ada_data": len([f for f in fakta if f["aspek"] != "pengumuman"]) > 0,
    }
    hasil["narasi"] = narasi(hasil)
    return hasil


# --------------------------------------------------------------------------- narasi model

INSTRUKSI_NARASI = """Tulis ringkasan analisis saham dalam bahasa: {bahasa}.

Gunakan HANYA fakta di blok <dokumen>. Jangan menambah angka baru, jangan membulatkan
ulang angka, jangan menyebut harga target. DILARANG memberi saran membeli atau menjual
dalam bentuk apa pun. Akhiri dengan mengingatkan bahwa keputusan ada di tangan investor.

3 sampai 5 kalimat. Balas JSON: {{"ringkasan": "<teks>"}}"""

NAMA_BAHASA = {"en": "English", "zh": "繁體中文 (Taiwan)", "id": "Bahasa Indonesia"}


def _angka_dalam(teks: str, bahasa: str) -> set[str]:
    """Semua angka di teks, dinormalkan (tanpa pemisah ribuan, titik sebagai desimal)."""
    keluar = set()
    for m in re.findall(r"\d[\d.,]*\d|\d", teks):
        if bahasa == "id":
            m = m.replace(".", "").replace(",", ".")
        else:
            m = m.replace(",", "")
        try:
            keluar.add(f"{float(m):.4f}")
        except ValueError:
            pass
    return keluar


def periksa_narasi(teks: str, hasil: dict) -> tuple[bool, str]:
    rendah = teks.lower()
    for k in KATA_TERLARANG:
        if k.lower() in rendah:
            return False, f"memuat kata terlarang: {k}"
    sumber = " ".join([f["teks"] for f in hasil["fakta"]] + [hasil["kesimpulan"], hasil["kecocokan"], hasil["kode"]])
    boleh = _angka_dalam(sumber, hasil["bahasa"])
    asing = _angka_dalam(teks, hasil["bahasa"]) - boleh
    if asing:
        return False, f"angka tidak ada di fakta: {sorted(asing)[:3]}"
    return True, "ok"


def narasi(hasil: dict) -> dict:
    """Paragraf dari model bila tersedia dan lolos pemeriksaan; selain itu template."""
    if not hasil["ada_data"] or not llm.tersedia():
        return {"sumber": "template", "teks": None, "alasan_kode": "rk.alasan.tanpa_model", "alasan": ""}
    dokumen = json.dumps({
        "kode": hasil["kode"],
        "fakta": [f["teks"] for f in hasil["fakta"]],
        "kesimpulan": hasil["kesimpulan"],
        "kecocokan_profil": hasil["kecocokan"],
    }, ensure_ascii=False, indent=1)
    try:
        jawab, meta = llm.tanya(INSTRUKSI_NARASI.format(bahasa=NAMA_BAHASA[hasil["bahasa"]]), dokumen)
    except llm.GagalModel as e:
        return {"sumber": "template", "teks": None, "alasan_kode": "rk.alasan.gagal", "alasan": str(e)[:200]}
    teks = str(jawab.get("ringkasan") or "").strip()
    ok, alasan = periksa_narasi(teks, hasil) if teks else (False, "jawaban kosong")
    if not ok:
        return {"sumber": "template", "teks": None, "alasan_kode": "rk.alasan.ditolak", "alasan": alasan}
    return {"sumber": "model", "teks": teks, "model": meta.get("model"), "cache": bool(meta.get("cache"))}
