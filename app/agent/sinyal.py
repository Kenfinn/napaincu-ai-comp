"""Jalur sinyal (B1): pasal yang tidak mengubah DCF, tapi perlu diketahui investor.

Keputusan tim (docs/pemetaan-pasal.md, "Keputusan tim"):
    22, 23   penjaminan / pinjaman dana ke pihak lain → sinyal risiko, per penerima
    11, 35   perubahan modal, obligasi, pembelian kembali → sinyal; DCF berbasis kas
    31       laporan keuangan kuartal → ringkasan angka; memicu pembaruan valuasi
    1, 3, 40 gagal bayar, penghentian produksi, suspensi → selalu ke manusia
    7        pergantian auditor eksternal → sinyal tata kelola (tim keuangan 11 Nov)
    8        pergantian pejabat kunci → sinyal tata kelola (tim keuangan 11 Nov)

Pasal 7 dan 8 memuat nama orang (akuntan, pejabat). Butir yang labelnya memuat 姓名
tidak pernah dikutip, dan teks bebas 異動原因 tidak diambil karena bisa memuat nama.

Semua angka diurai oleh KODE dari butir pengumuman, tidak oleh model, dan setiap angka
membawa kutipan "label: isi" yang kemudian dicek ulang ada di dokumen. Satuan (仟元)
dibaca dari label. Hasilnya dalam juta NTD dan pecahan (0,54 = 54%).
"""

from __future__ import annotations

import re

from . import extract

ANGKA = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


# Angka akuntansi negatif ditulis dalam kurung: "(339,123)" = rugi 339.123. Sebelum 11 Nov
# ini terbaca positif, sehingga 29 dari 177 laporan kuartal rugi tampil sebagai laba
# (ditemukan tim keuangan di gold set, kasus 6535).
KURUNG = re.compile(r"^\s*[（(]\s*(\d[\d,]*(?:\.\d+)?)\s*[)）]")


def _f(s: str | None) -> float | None:
    m = KURUNG.match(s or "")
    if m:
        try:
            return -float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    m = ANGKA.search(s or "")
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def _ke_juta(nilai: float | None, label: str, isi: str = "") -> float | None:
    """Ke juta NTD memakai satuan di label atau isi; tanpa satuan → None (tidak ditebak)."""
    if nilai is None:
        return None
    tok, pengali = extract._satuan_dari(label)
    if tok is None:
        tok, pengali = extract._satuan_dari(isi)
    return None if pengali is None else nilai * pengali


def _butir(detail: dict):
    for it in detail.get("items", []):
        yield it
        for s in it.get("sub", []):
            yield s


def _cari(detail: dict, *wajib: str, kecuali: tuple[str, ...] = ()) -> dict | None:
    for b in _butir(detail):
        lab = b.get("label_lengkap") or b.get("label") or ""
        if all(w in lab for w in wajib) and not any(k in lab for k in kecuali):
            return b
    return None


def _kutip(b: dict | None) -> dict | None:
    if not b:
        return None
    return {"butir_no": b.get("no"), "label": b.get("label_lengkap") or b.get("label"), "isi": b.get("value", "")}


# --------------------------------------------------------------------------- 22 / 23
_TERKAIT = re.compile(r"子公司|母公司|關係企業|關係人|關聯|聯屬|集團|持股|孫公司|100%")


def _penerima(teks: str) -> list[dict]:
    """Urai '(1)公司名稱:A (2)...(1)公司名稱:B ...' menjadi satu dict per penerima."""
    keluar = []
    # Labelnya bervariasi: "(1)公司名稱:" atau "(1)接受資金貸與之公司名稱:".
    for seg in re.split(r"\(1\)\s*[^:：()]{0,12}公司名稱", teks or "")[1:]:
        bagian = re.split(r"\((\d)\)", "(1)公司名稱" + seg)
        pasang = {}
        for no, isi in zip(bagian[1::2], bagian[2::2]):
            if re.search(r"[:：]", isi):
                lab, val = re.split(r"[:：]", isi, maxsplit=1)
                pasang[lab.strip()] = val.strip()
        def ambil(*kata):
            return next((v for k, v in pasang.items() if all(w in k for w in kata)), None)
        hub = ambil("關係") or ""
        limit = ambil("之限額")
        saldo = ambil("迄事實發生日", "餘額")
        baru = ambil("本次新增", "金額")
        pakai = ambil("實際動支")
        r = {
            "nama": (ambil("公司名稱") or "")[:80],
            "hubungan": hub[:80],
            "terkait": bool(_TERKAIT.search(hub)),
            "limit_juta": _ke_juta(_f(limit), "仟元") if limit else None,
            "saldo_juta": _ke_juta(_f(saldo), "仟元") if saldo else None,
            "baru_juta": _ke_juta(_f(baru), "仟元") if baru else None,
            "dipakai_juta": _ke_juta(_f(pakai), "仟元") if pakai else None,
            "mentah": {"limit": limit, "saldo": saldo, "baru": baru, "dipakai": pakai},
        }
        if r["limit_juta"] and r["saldo_juta"] is not None:
            r["pemakaian_limit"] = r["saldo_juta"] / r["limit_juta"]
        keluar.append(r)
    return keluar


def urai_penjaminan(detail: dict, pasal: int) -> dict:
    kata = "背書保證" if pasal == 22 else "資金貸與"
    jenis = "penjaminan" if pasal == 22 else "pinjaman"
    b_total = _cari(detail, kata, "總限額")
    b_saldo = _cari(detail, "迄事實發生日為止", "餘額", kecuali=("比率", "合計"))
    b_rasio = _cari(detail, "淨值之", "比率", kecuali=("合計",))
    b_gab = _cari(detail, "合計", "比率")
    b_pen = next((it for it in detail.get("items", [])
                  if re.search(r"\(1\)[^:：()]{0,12}公司名稱", re.sub(r"\s", "", it.get("value", "")))), None)
    total = _ke_juta(_f(b_total.get("value")), b_total.get("label_lengkap") or "") if b_total else None
    saldo = _ke_juta(_f(b_saldo.get("value")), b_saldo.get("label_lengkap") or "") if b_saldo else None
    rasio = _f(b_rasio.get("value")) if b_rasio else None
    gab = _f(b_gab.get("value")) if b_gab else None
    penerima = _penerima(b_pen.get("value", "")) if b_pen else []
    return {
        "jenis": jenis, "pasal": pasal,
        "total_limit_juta": total, "saldo_total_juta": saldo,
        "rasio_ekuitas": rasio / 100 if rasio is not None else None,
        "rasio_gabungan": gab / 100 if gab is not None else None,
        "pemakaian_limit": (saldo / total) if (saldo is not None and total) else None,
        "penerima": penerima,
        "pihak_luar": any(not p["terkait"] for p in penerima),
        "kutipan": [k for k in map(_kutip, (b_total, b_saldo, b_rasio, b_gab)) if k],
    }


# --------------------------------------------------------------------------- 11 / 35
def _subjenis_modal(detail: dict) -> str:
    j = detail.get("subject") or ""
    if detail.get("clause") == 35 or "買回" in j:
        return "beli_kembali"
    if "庫藏股" in j and ("註銷" in j or "減資" in j):
        return "treasuri"
    if "彌補虧損" in j:
        return "tutup_rugi"
    if "現金減資" in j:
        return "kas_kembali"
    if "限制員工權利新股" in j and ("收回" in j or "註銷" in j):
        return "rsa_batal"
    if "公司債" in j and "轉換普通股" not in j and "增資基準日" not in j:
        return "obligasi"
    if any(k in j for k in ("增資", "私募", "認股權", "轉換普通股", "發行新股")):
        return "saham_baru"
    return "lain"


_SATUAN_SAHAM = {"仟股": 1_000, "千股": 1_000, "萬股": 10_000, "張": 1_000, "股": 1}


def _lembar(isi: str) -> float | None:
    """Jumlah saham pertama yang tertulis, dalam lembar: "120,000仟股" = 120 juta lembar."""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(仟股|千股|萬股|張|股)", isi or "")
    if not m:
        return None
    return float(m.group(1).replace(",", "")) * _SATUAN_SAHAM[m.group(2)]


def urai_modal(detail: dict, skala: dict | None) -> dict:
    sub = _subjenis_modal(detail)
    kutipan = []
    lembar = None          # perubahan jumlah saham (lembar), + naik / - turun
    persen = None          # pecahan dari saham beredar, bila tertulis
    nilai_juta = None
    if sub in ("treasuri", "rsa_batal", "kas_kembali", "tutup_rugi"):
        b = _cari(detail, "消除股份")
        if b:
            kutipan.append(_kutip(b))
            v = _f(b.get("value"))
            lembar = -v if v is not None else None
        b = _cari(detail, "減資比率")
        if b:
            kutipan.append(_kutip(b))
            v = _f(b.get("value"))
            persen = v / 100 if v is not None else None
        b = _cari(detail, "減資金額")
        if b:
            kutipan.append(_kutip(b))
            nilai_juta = _ke_juta(_f(b.get("value")), b.get("label_lengkap") or "", b.get("value", ""))
    elif sub == "saham_baru":
        b = (_cari(detail, "發行總金額及股數") or _cari(detail, "發行股數") or _cari(detail, "私募股數")
             or _cari(detail, "認股權行使", "新股總數") or _cari(detail, "新股總數"))
        if b:
            kutipan.append(_kutip(b))
            isi = b.get("value", "")
            lembar = _lembar(isi)
            uang = [float(x.replace(",", "")) for x in re.findall(r"新[台臺]幣\s*([\d,]+(?:\.\d+)?)\s*元", isi)]
            nilai_juta = sum(uang) / 1e6 if uang else None
    elif sub == "obligasi":
        b = _cari(detail, "發行總額") or _cari(detail, "總額")
        if b:
            kutipan.append(_kutip(b))
            p = extract._pilih_angka(b.get("value", ""))
            if p and p[1] in extract.SATUAN:
                nilai_juta = float(p[0].replace(",", "")) * extract.SATUAN[p[1]]
    elif sub == "beli_kembali":
        b = _cari(detail, "買回", "總金額") or _cari(detail, "買回", "金額")
        if b:
            kutipan.append(_kutip(b))
            nilai_juta = _ke_juta(_f(b.get("value")), b.get("label_lengkap") or "", b.get("value", ""))
        b = _cari(detail, "買回", "股數") or _cari(detail, "買回股份", "數量")
        if b:
            kutipan.append(_kutip(b))
            v = _f(b.get("value"))
            lembar = -v if v is not None else None
    beredar = (skala or {}).get("lembar")
    if persen is None and lembar is not None and beredar:
        persen = abs(lembar) / beredar
    kap = (skala or {}).get("juta_ntd")
    return {
        "jenis": "modal", "pasal": detail.get("clause"), "subjenis": sub,
        "lembar_berubah": lembar, "persen_saham": abs(persen) if persen is not None else None,
        "nilai_juta": nilai_juta,
        "persen_kapitalisasi": (nilai_juta / kap) if (nilai_juta and kap) else None,
        "dilusi_potensial": sub == "obligasi" and "轉換" in (detail.get("subject") or ""),
        "dcf_berubah": False,
        "kutipan": [k for k in kutipan if k],
    }


# --------------------------------------------------------------------------- 31
_LAPORAN = (
    ("pendapatan_juta", ("營業收入",), ()),
    ("laba_usaha_juta", ("營業利益",), ()),
    ("laba_sebelum_pajak_juta", ("稅前",), ()),
    ("laba_bersih_juta", ("本期淨利",), ("歸屬",)),
    ("laba_induk_juta", ("歸屬於母公司業主淨利",), ()),
    ("aset_juta", ("期末總資產",), ()),
    ("liabilitas_juta", ("期末總負債",), ()),
    ("ekuitas_juta", ("期末歸屬於母公司業主之權益",), ()),
)


def urai_laporan(detail: dict) -> dict:
    hasil: dict = {"jenis": "laporan", "pasal": 31, "kutipan": []}
    for kunci, wajib, kecuali in _LAPORAN:
        b = _cari(detail, *wajib, kecuali=kecuali)
        hasil[kunci] = _ke_juta(_f(b.get("value")), b.get("label_lengkap") or "") if b else None
        if b:
            hasil["kutipan"].append(_kutip(b))
    b = _cari(detail, "基本每股盈餘")
    hasil["eps"] = _f(b.get("value")) if b else None
    if b:
        hasil["kutipan"].append(_kutip(b))
    b = _cari(detail, "報導期間")
    hasil["periode"] = (b.get("value") or "").strip()[:40] if b else None
    a, l, p = hasil.get("aset_juta"), hasil.get("liabilitas_juta"), hasil.get("pendapatan_juta")
    hasil["rasio_utang"] = (l / a) if (a and l is not None) else None
    hasil["margin_bersih"] = (hasil["laba_induk_juta"] / p) if (p and hasil.get("laba_induk_juta") is not None) else None
    hasil["memicu_valuasi"] = True
    return hasil


# --------------------------------------------------------------------------- 1 / 3 / 40
def urai_berat(detail: dict) -> dict:
    """Kejadian berat. Butir nama (公司名稱(或負責人姓名)) sengaja TIDAK diambil: bisa nama orang."""
    hasil = {"jenis": "berat", "pasal": detail.get("clause"), "kutipan": [], "nilai_juta": None}
    b = _cari(detail, "喪失債信之金額")
    if b:
        hasil["kutipan"].append(_kutip(b))
        hasil["nilai_juta"] = _ke_juta(_f(b.get("value")), b.get("label_lengkap") or "", b.get("value", "") + "元")
    b = _cari(detail, "喪失債信之日期") or _cari(detail, "事實發生日")
    if b:
        hasil["kutipan"].append(_kutip(b))
    return hasil


# --------------------------------------------------------------------------- 7 / 8
_TIDAK = ("無", "不適用", "否", "沒有", "none", "n/a")


def _kosong(v: str | None) -> bool:
    v = (v or "").strip().strip("。.").lower()
    return not v or any(v.startswith(t) for t in _TIDAK)


def urai_auditor(detail: dict) -> dict:
    """Pasal 7: kantor akuntan sama (rotasi) atau berganti; auditor mundur; beda pendapat."""
    hasil = {"jenis": "auditor", "pasal": detail.get("clause"), "kutipan": [],
             "ganti_kantor": None, "auditor_mundur": False, "beda_pendapat": False}
    lama = _cari(detail, "舊會計師事務所")
    baru = _cari(detail, "新會計師事務所")
    for b in (lama, baru, _cari(detail, "變更會計師之原因")):
        if b:
            hasil["kutipan"].append(_kutip(b))
    if lama and baru:
        hasil["ganti_kantor"] = (lama.get("value") or "").strip() != (baru.get("value") or "").strip()
    elif "事務所" in (detail.get("subject") or "") and "內部輪調" not in (detail.get("subject") or ""):
        hasil["ganti_kantor"] = True
    hasil["kantor_lama"] = (lama or {}).get("value")
    hasil["kantor_baru"] = (baru or {}).get("value")
    siapa = _cari(detail, "主動終止委任")
    if siapa and "會計師主動" in (siapa.get("value") or ""):
        hasil["auditor_mundur"] = True
        hasil["kutipan"].append(_kutip(siapa))
    beda = _cari(detail, "有無不同意見")
    if beda and not _kosong(beda.get("value")):
        hasil["beda_pendapat"] = True
        hasil["kutipan"].append(_kutip(beda))
    return hasil


# Jabatan yang langsung menyentuh angka laporan atau arah perusahaan.
JABATAN_KUNCI = ("財務長", "財務主管", "會計主管", "內部稽核主管", "稽核主管", "執行長", "總經理",
                 "總裁", "營運長", "董事長")
_KELUAR = ("辭職", "資遣", "解任", "死亡", "逝世")


def urai_pejabat(detail: dict) -> dict:
    """Pasal 8: jabatan apa, jenis perubahan, berlaku kapan. Tanpa nama orang."""
    hasil = {"jenis": "pejabat", "pasal": detail.get("clause"), "kutipan": [],
             "jabatan": None, "perubahan": None, "kunci": False, "keluar": False,
             "anak_perusahaan": (detail.get("subject") or "").startswith("代")}
    jab = _cari(detail, "人員變動別")
    if jab:
        hasil["jabatan"] = (jab.get("value") or "").strip() or None
        hasil["kutipan"].append(_kutip(jab))
    ub = _cari(detail, "異動情形")
    if ub:
        hasil["perubahan"] = (ub.get("value") or "").strip() or None
        hasil["kutipan"].append(_kutip(ub))
    eff = _cari(detail, "生效日期")
    if eff:
        hasil["berlaku"] = eff.get("value")
        hasil["kutipan"].append(_kutip(eff))
    # 副總經理 (wakil) bukan 總經理 (direktur utama): buang dulu sebelum dicocokkan.
    teks_jab = (hasil["jabatan"] or detail.get("subject") or "").replace("副總經理", "")
    hasil["kunci"] = any(k in teks_jab for k in JABATAN_KUNCI)
    hasil["keluar"] = any(k in (hasil["perubahan"] or "") for k in _KELUAR)
    return hasil


def periksa_kutipan(sinyal: dict, dokumen: str) -> list[dict]:
    """Setiap kutipan wajib ada di dokumen (isi persis). Gagal = bug pengurai, bukan keraguan."""
    keluar = []
    for k in sinyal.get("kutipan", []):
        ok = bool(k.get("isi")) and k["isi"].strip() in dokumen
        keluar.append({"butir_no": k.get("butir_no"), "lolos": ok})
    return keluar
