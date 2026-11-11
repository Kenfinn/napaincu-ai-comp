"""Tahap 2 — penyari angka, beserta kalimat sumbernya.

Aturan yang tidak boleh dilanggar: **setiap angka wajib datang bersama kutipan
kalimat asalnya dan nomor butirnya.** Angka tanpa sumber tidak bisa diperiksa, dan
angka yang tidak bisa diperiksa tidak boleh menyentuh valuasi.

Penalar berbasis aturan di bawah bukan sekadar cadangan saat API mati. Ia juga
**baseline** yang diminta Appendix 2 sebagai pembanding terhadap proses berbasis
model — jadi ia sengaja ditulis serapi jalur utamanya.
"""

from __future__ import annotations

import re
import time

from . import llm

# Label butir MOPS yang sah menjadi sumber tiap input valuasi. Dipakai dua kali:
# di sini untuk mencari, dan di pemeriksa untuk menolak kutipan yang labelnya
# tidak nyambung dengan input yang diklaim.
LABEL_SAH: dict[str, tuple[str, ...]] = {
    "capex": ("資本支出預算金額", "資本支出金額", "交易金額", "取得資產之金額",
              # Label asli pasal 20 (取得或處分資產), dari pengumuman 9–10 Nov. Satu butir
              # memuat jumlah unit, harga satuan, DAN total; penyari mengambil totalnya.
              "交易單位數量、每單位價格及交易總金額", "交易數量、每單位價格及交易總金額",
              # Kontrak konstruksi/fasilitas (廠務工程, 新建工程) di pasal 20.
              "契約主要內容、限制條款及其他重要約定事項"),
    "debt":  ("借款金額", "背書保證金額", "資金貸與金額", "退票金額"),
    "cash":  ("交易金額", "價款", "處分金額",
              "交易單位數量、每單位價格及交易總金額", "交易數量、每單位價格及交易總金額"),
}

# Satuan mata uang di halaman MOPS → pengali ke JUTA NTD.
# 仟元 = ribu, 百萬元 = juta, 億元 = seratus juta.
SATUAN: dict[str, float] = {
    "仟元": 1e-3,
    "千元": 1e-3,
    "百萬元": 1.0,
    "佰萬元": 1.0,     # varian penulisan 百萬元 (2330, 10 Nov)
    "千萬元": 10.0,
    "仟萬元": 10.0,
    "萬元": 1e-2,
    "億元": 100.0,
    "萬": 1e-2,       # "新台幣165萬" — tanpa 元, dipakai di teks bebas
    "億": 100.0,
    "元": 1e-6,
}

MATA_UANG = {
    "新台幣": "TWD", "新臺幣": "TWD", "台幣": "TWD", "臺幣": "TWD", "NT$": "TWD",
    "NTD": "TWD", "TWD": "TWD",
    "美金": "USD", "美元": "USD", "US$": "USD", "USD": "USD",
    "日圓": "JPY", "日幣": "JPY", "JPY": "JPY", "歐元": "EUR", "EUR": "EUR",
    "人民幣": "CNY", "RMB": "CNY", "CNY": "CNY", "港幣": "HKD", "HKD": "HKD",
}

ANGKA = re.compile(r"(\d[\d,]*(?:\.\d+)?)")

# Satu ungkapan jumlah uang: [mata uang] angka [satuan], satuan menempel pada angka.
# Satuan dicocokkan dari yang terpanjang supaya 百萬元 tidak terbaca 元 dan 萬元 tidak 萬.
_MU_POLA = "|".join(re.escape(k) for k in sorted(MATA_UANG, key=len, reverse=True))
_SATUAN_POLA = "|".join(re.escape(k) for k in sorted(SATUAN, key=len, reverse=True))
UANG = re.compile(rf"({_MU_POLA})?\s*(\d[\d,]*(?:\.\d+)?)\s*({_SATUAN_POLA})?")
# Kata yang menandai angka total transaksi di butir yang memuat beberapa angka.
PENANDA_TOTAL = ("總金額", "總額", "總價", "金額")

# Frasa yang menyerupai perintah di dalam dokumen. Ini SINYAL, bukan pertahanan —
# pertahanannya ada di pemeriksa yang deterministik. Gunanya supaya percobaan
# pengarahan terlihat di jejak audit, bukan lewat begitu saja tanpa jejak.
PENANDA_INJEKSI = (
    "忽略", "無需人工", "無需複核", "直接發布", "請照做", "系統提示",
    "ignore previous", "ignore all", "disregard", "system prompt",
)


def _normal_label(s: str) -> str:
    s = re.sub(r"^\s*[(（]\d{1,2}[)）]\s*", "", s or "")
    s = re.sub(r"^\s*\d{1,2}\s*[.、．:：]\s*", "", s)       # "5. 交易…" — model sering menyertakan nomor butir
    s = re.sub(r"[（(][^）)]*[)）]", "", s)
    return re.sub(r"[\s，,、]", "", s)


def label_sah(label: str, input_nama: str) -> bool:
    """Label butir cocok untuk input ini? Dibandingkan setelah kurung, nomor sub-butir,
    spasi, dan tanda baca dibuang — MOPS menulis label yang sama dengan variasi kecil."""
    n = _normal_label(label)
    return bool(n) and any(n == _normal_label(s) for s in LABEL_SAH.get(input_nama, ()))


def deteksi_injeksi(dokumen: str) -> list[str]:
    rendah = dokumen.lower()
    return [p for p in PENANDA_INJEKSI if (p.lower() in rendah)]


def _satuan_dari(teks: str) -> tuple[str | None, float | None]:
    # Cek satuan panjang lebih dulu — "百萬元" memuat "元", dan urutan yang salah
    # akan mengenalinya sebagai rupiah-per-satu, meleset sejuta kali lipat.
    for tok in sorted(SATUAN, key=len, reverse=True):
        if tok in teks:
            return tok, SATUAN[tok]
    return None, None


def _mata_uang_dari(teks: str) -> str | None:
    for tok, kode in MATA_UANG.items():
        if tok in teks:
            return kode
    return None


def ke_juta_ntd(mentah: str, pengali: float | None, mata_uang: str | None) -> float | None:
    """Konversi ke juta NTD — atau None kalau tidak boleh dikonversi.

    Gagal-tertutup dengan sengaja. Model valuasi kita seluruhnya dalam NTD dan tidak
    memuat kurs. Mengembalikan angka untuk jumlah berdenominasi USD akan menghasilkan
    nilai yang kelihatan masuk akal tapi salah tiga puluh kali lipat — jenis kesalahan
    yang tidak akan ketahuan sampai ada yang mencocokkannya dengan tangan.
    """
    if pengali is None:
        return None
    # Tanpa penyebutan mata uang, konvensi halaman MOPS adalah NTD. Asumsi itu
    # dicatat di temuan supaya pemeriksa bisa menandainya.
    if mata_uang not in (None, "TWD"):
        return None
    try:
        return float(mentah.replace(",", "")) * pengali
    except ValueError:
        return None


def _ungkapan_uang(nilai: str) -> list[dict]:
    """Semua ungkapan jumlah uang di satu isi butir, berurutan."""
    keluar = []
    for m in UANG.finditer(nilai):
        mu, angka, tok = m.group(1), m.group(2), m.group(3)
        if not (mu or tok):
            continue            # angka telanjang: tanggal, jumlah unit, persen
        keluar.append({"awal": m.start(), "mentah": angka, "satuan": tok, "mu": mu})
    return keluar


_SATUAN_KURUNG = re.compile(rf"[（(]\s*({_SATUAN_POLA})\s*[)）]")


def _pilih_angka(nilai: str) -> tuple[str, str | None, str | None] | None:
    """Pilih angka yang dimaksud dari isi butir: (mentah, satuan, token mata uang).

    Pengumuman pasal 20 menulis jumlah unit, harga satuan, dan total dalam satu butir
    ("3台；每單位平均價格：新台幣36,187,653元，交易總金額為新台幣108,562,960元"). Yang
    menggeser valuasi adalah totalnya, jadi bila ada penanda total, HANYA angka sesudahnya
    yang dipertimbangkan. Satuan boleh menempel ("108,562,960元") atau ditulis dalam kurung
    sebelum angka ("交易總金額（元）：318,974,231"). Total yang ditulis dengan angka Mandarin
    (壹佰捌拾捌億元) tidak dikonversi: lebih aman tidak ada angka daripada angka salah.
    """
    for penanda in PENANDA_TOTAL:
        i = nilai.rfind(penanda)
        if i < 0:
            continue
        ekor = nilai[i + len(penanda):]
        m = next((x for x in UANG.finditer(ekor) if x.group(2)), None)
        if not m:
            return None
        depan = ekor[:m.start(2)]
        tok = m.group(3)
        if not tok:
            k = _SATUAN_KURUNG.search(depan)
            tok = k.group(1) if k else None
        mu = m.group(1) or next((t for t in sorted(MATA_UANG, key=len, reverse=True) if t in depan), None)
        return m.group(2), tok, mu
    kandidat = _ungkapan_uang(nilai)
    if kandidat:
        k = kandidat[0]
        return k["mentah"], k["satuan"], k["mu"]
    m = ANGKA.search(nilai)
    return (m.group(1), None, None) if m else None


def _sari_satu(butir: dict, input_nama: str) -> dict | None:
    nilai = butir.get("value", "") or ""
    pilih = _pilih_angka(nilai)
    if not pilih:
        return None
    mentah, tok, tok_mu = pilih
    pengali = SATUAN.get(tok) if tok else None
    if tok is None:
        # Satuan sering hanya tertulis di label, mis. 背書保證餘額(仟元): 4,644,640
        tok, pengali = _satuan_dari(butir.get("label_lengkap") or "")
    if tok is None:
        tok, pengali = _satuan_dari(nilai)
    mu = (MATA_UANG.get(tok_mu) if tok_mu else None) or _mata_uang_dari(nilai) \
        or _mata_uang_dari(butir.get("label_lengkap") or "")
    return {
        "input": input_nama,
        "nilai_mentah": mentah,
        "satuan": tok,
        "pengali_ke_juta": pengali,
        "mata_uang": mu,
        "mata_uang_diasumsikan": mu is None,
        "nilai_juta_ntd": ke_juta_ntd(mentah, pengali, mu),
        "kutipan": f"{butir.get('label', '')}: {nilai}",
        "butir_no": butir.get("no"),
        "label": butir.get("label", ""),
    }


# Penalar aturan memilih SATU input per butir. Angka transaksi yang sama tidak boleh
# dihitung dua kali sebagai belanja modal sekaligus kas. Judul pengumuman menentukan:
# 處分 (melepas) → kas masuk; 取得 (memperoleh) → belanja modal. Model memilah lebih
# halus (mis. produk investasi bukan belanja modal) — ini baseline, bukan pengganti.
def _urut_kandidat(detail: dict, kandidat: list[str]) -> list[str]:
    judul = detail.get("subject") or ""
    if "處分" in judul and "cash" in kandidat:
        return ["cash"] + [k for k in kandidat if k != "cash"]
    if "取得" in judul and "capex" in kandidat:
        return ["capex"] + [k for k in kandidat if k != "capex"]
    return list(kandidat)


def _sari_aturan(detail: dict, kandidat: list[str]) -> list[dict]:
    temuan, terpakai = [], set()
    semua = [b for it in detail.get("items", []) for b in [it] + it.get("sub", [])]
    for input_nama in _urut_kandidat(detail, kandidat):
        for butir in semua:
            kunci = (butir.get("no"), butir.get("label"))
            if kunci in terpakai:
                continue
            if label_sah(butir.get("label", ""), input_nama):
                hasil = _sari_satu(butir, input_nama)
                if hasil:
                    temuan.append(hasil)
                    terpakai.add(kunci)
                    break        # satu angka per input sudah cukup
    return temuan


INSTRUKSI = """Dari pengumuman di bawah, tarik angka keuangan yang mengubah input valuasi berikut: {kandidat}.

Untuk SETIAP angka yang ditemukan, wajib sertakan kalimat sumbernya persis seperti tertulis
dan nomor butirnya. Angka tanpa kutipan sumber akan ditolak sistem.

Hanya tarik angka dari butir yang labelnya memang menyatakan jumlah untuk input tersebut.
Jangan menarik angka dari butir yang isinya berupa catatan, tanggal, atau keterangan lain.

Bila satu butir memuat beberapa angka (jumlah unit, harga satuan, total), ambil TOTAL
transaksinya. Satu angka hanya untuk SATU input: perolehan mesin, gedung, atau hak guna
adalah capex; pelepasan aset adalah cash; pembelian produk investasi atau surat berharga
bukan capex. Satuan ditulis persis seperti di dokumen (仟元, 萬元, 萬, 億元, 元, ...).

Balas JSON: {{"temuan": [{{"input": "capex|debt|cash", "nilai_mentah": "1,234,567",
"satuan": "仟元|千元|百萬元|萬元|萬|億元|億|元", "mata_uang": "TWD|USD|...", "kutipan": "<label>: <isi persis>",
"butir_no": 3}}]}}

Kalau tidak ada angka yang sah, balas {{"temuan": []}}."""


def sari(detail: dict, kandidat: list[str]) -> tuple[list[dict], dict]:
    """Tarik angka. Coba model dulu; kalau gagal, turun ke penalar aturan."""
    mulai = time.monotonic()
    dokumen = llm.dokumen_teks(detail)

    if llm.tersedia():
        try:
            jawab, meta = llm.tanya(INSTRUKSI.format(kandidat=", ".join(kandidat)), dokumen)
            temuan = []
            for t in jawab.get("temuan", []):
                tok = t.get("satuan")
                pengali = SATUAN.get(tok) if tok else None
                mentah = str(t.get("nilai_mentah", ""))
                mu = t.get("mata_uang")
                temuan.append({
                    "input": t.get("input"),
                    "nilai_mentah": mentah,
                    "satuan": tok,
                    "pengali_ke_juta": pengali,
                    "mata_uang": mu,
                    "mata_uang_diasumsikan": mu is None,
                    "nilai_juta_ntd": ke_juta_ntd(mentah, pengali, mu),
                    "kutipan": t.get("kutipan", ""),
                    "butir_no": t.get("butir_no"),
                    "label": (t.get("kutipan", "").split(":", 1)[0] or "").strip(),
                })
            meta["injeksi_terdeteksi"] = deteksi_injeksi(dokumen)
            return temuan, meta
        except llm.GagalModel as e:
            meta = llm.meta_cadangan(mulai, str(e))
            temuan = _sari_aturan(detail, kandidat)
            meta["injeksi_terdeteksi"] = deteksi_injeksi(dokumen)
            return temuan, meta

    meta = llm.meta_cadangan(mulai, "tidak ada kunci API")
    temuan = _sari_aturan(detail, kandidat)
    meta["injeksi_terdeteksi"] = deteksi_injeksi(dokumen)
    return temuan, meta
