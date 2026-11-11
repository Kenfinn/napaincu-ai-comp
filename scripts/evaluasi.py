"""Evaluasi Appendix 2 — jalankan gold set ke beberapa mode, keluarkan satu tabel.

Pertanyaannya bukan "seberapa sering agent benar", melainkan **berapa angka salah yang
lolos terbit**. Untuk agent keuangan, satu angka salah yang terbit lebih mahal daripada
sepuluh pengumuman yang ditahan untuk manusia.

Mode yang dibandingkan (deck hal. 9):

    aturan            pipeline lengkap, tahap 1–2 memakai penalar aturan (tanpa model)
    model             pipeline lengkap, tahap 1–2 memakai model (butuh GEMINI_API_KEY)
    tanpa-pemeriksa   saringan + penyari saja; apa pun yang tertarik langsung "terbit".
                      Mewakili "satu LLM tanpa verifier". Memakai model kalau ada kunci,
                      kalau tidak memakai penalar aturan — labelnya ikut tercetak.

Baseline manual tidak bisa dijalankan mesin. Angkanya (menit per pengumuman) datang dari
wawancara; berikan lewat --menit-manual supaya tabel memuat perkiraan waktu yang dihemat.

Gold set: eval/gold.csv, satu baris per (pengumuman, angka yang benar). Kolom:

    source_url      URL MOPS — kunci pencocok dengan data
    kode            kode emiten
    harus_terbit    ya | tidak — menurut penilaian anggota keuangan
    input           capex | debt | cash   (kosong kalau harus_terbit = tidak)
    nilai_juta_ntd  angka yang benar, dalam juta NTD
    butir_no        nomor butir sumber di halaman MOPS
    pelabel         siapa yang melabeli (inisial / "contoh" untuk fixture)
    catatan         alasan singkat

Jalankan:

    python3 scripts/evaluasi.py                       # mode yang tersedia, data yang ada
    python3 scripts/evaluasi.py --mode aturan model   # pilih mode
    python3 scripts/evaluasi.py --menit-manual 6 --simpan

Data dibaca lewat app.store, jadi sama dengan yang dipakai aplikasi: data/parsed/ kalau
ada, data/fixtures/ kalau tidak. Sumbernya tercetak di laporan.

Dua mode tambahan yang tidak butuh gold set (D4):

    --operasional   jalankan pipeline atas SEMUA pengumuman yang ada (tambah --arsip untuk
                    arsip mentah server) dan laporkan metrik operasi Appendix 2: sebaran
                    state, latensi rata-rata/median/p95/maks, token, panggilan model,
                    jawaban cache, retry, jatuh ke penalar aturan beserta sebabnya,
                    kategori error, tingkat intervensi manusia.
    --chat          jalankan set pertanyaan uji Tanya FEAF (eval/chat_uji.csv): ketepatan
                    menolak, jawaban bersumber, angka lolos pemeriksa, kata terlarang,
                    latensi, panggilan alat/model.

Biaya: free tier Gemini = 0. Untuk perkiraan tier berbayar beri --harga-token
"<USD per 1 juta token masuk>,<USD per 1 juta token keluar>" sesuai daftar harga resmi.

Ambang triase dan keputusan review memakai berkas sementara (ambang dasar, tanpa
keputusan manusia), supaya hasil bisa diulang dan tidak bergantung pada isi server.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import config, review, store, umpan_balik         # noqa: E402
from app.agent import extract, pipeline, screen            # noqa: E402
import collections                                         # noqa: E402

GOLD_DEFAULT = os.path.join(ROOT, "eval", "gold.csv")
CHAT_UJI_DEFAULT = os.path.join(ROOT, "eval", "chat_uji.csv")
HASIL_DIR = os.path.join(ROOT, "eval", "hasil")
# Salinan 46 pengumuman gold (tanpa butir nama) supaya evaluasi bisa diulang di mesin mana pun,
# termasuk server yang tidak menyimpan data 9 Nov. Dibuat dengan scripts/buat_paket_gold.py --snapshot.
GOLD_DOKUMEN = os.path.join(ROOT, "eval", "gold_dokumen.json")


def _pakai_kapitalisasi_salinan(kap: dict) -> None:
    """Kapitalisasi emiten gold diambil dari salinan (tanggal evaluasi resmi), bukan cache
    pasar mesin ini, supaya keputusan materialitas sama di mana pun evaluasi dijalankan."""
    from app import pasar
    asli = pasar.kapitalisasi_dari_cache
    pasar.kapitalisasi_dari_cache = lambda kode: kap.get(kode) or asli(kode)


def _folder_hasil() -> str:
    """eval/hasil/ bila bisa ditulis; di container (/app milik root) jatuh ke DATA_DIR/eval-hasil."""
    for d in (HASIL_DIR, os.path.join(config.DATA_DIR, "eval-hasil")):
        try:
            os.makedirs(d, exist_ok=True)
            if os.access(d, os.W_OK):
                return d
        except OSError:
            continue
    raise SystemExit("Tidak ada folder hasil yang bisa ditulis.")


def _tulis_hasil(nama: str, cap: str, teks: str, data: dict) -> None:
    d = _folder_hasil()
    with open(os.path.join(d, f"{nama}-{cap}.md"), "w", encoding="utf-8") as f:
        f.write(teks)
    with open(os.path.join(d, f"{nama}-{cap}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"Tersimpan di {os.path.join(d, f'{nama}-{cap}.md')}", file=sys.stderr)

# Selisih relatif yang masih dianggap angka yang sama. Kecil dengan sengaja: yang dicari
# adalah salah satuan (×1000) atau salah butir, bukan pembulatan.
TOLERANSI = 0.005

MODE_SEMUA = ("aturan", "model", "tanpa-pemeriksa")


# --------------------------------------------------------------------------- gold set

def muat_gold(path: str) -> dict[str, dict]:
    """source_url → {"harus_terbit": bool, "keputusan": str, "tingkat": str|None, "angka": [(input, nilai)], "kode": ..., ...}"""
    gold: dict[str, dict] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for no, baris in enumerate(csv.DictReader(f), start=2):
            url = (baris.get("source_url") or "").strip()
            if not url:
                continue
            ya = (baris.get("harus_terbit") or "").strip().lower()
            kep = (baris.get("keputusan") or "").strip().lower()
            tingkat = (baris.get("tingkat") or "").strip().lower()

            # Tangani baris format lama 13 kolom yang bergeser bila header baru bertambah
            if kep in ("capex", "debt", "cash", "risiko", "modal", "laporan", "berat", "tata_kelola"):
                baris["catatan"] = baris.get("pelabel") or ""
                baris["pelabel"] = baris.get("butir_no") or ""
                baris["butir_no"] = baris.get("nilai_juta_ntd") or ""
                baris["nilai_juta_ntd"] = baris.get("tingkat") or ""
                baris["input"] = kep
                kep = ""
                tingkat = ""

            if not ya and not kep:
                continue                # kandidat yang belum dilabeli — dilewati, bukan galat

            if ya and ya not in ("ya", "tidak"):
                raise ValueError(f"{path}:{no}: harus_terbit harus 'ya' atau 'tidak', bukan {ya!r}")
            if kep and kep not in ("terbit", "tahan", "arsip"):
                raise ValueError(f"{path}:{no}: keputusan harus 'terbit', 'tahan', atau 'arsip', bukan {kep!r}")

            # Rekonsiliasi harus_terbit dan keputusan
            if ya and kep:
                ya_mapped = "terbit" if ya == "ya" else "arsip"
                if kep != ya_mapped:
                    raise ValueError(f"{path}:{no}: harus_terbit ({ya!r}) bertentangan dengan keputusan ({kep!r})")
            elif ya and not kep:
                kep = "terbit" if ya == "ya" else "arsip"
            elif kep and not ya:
                ya = "ya" if kep == "terbit" else "tidak"

            if tingkat and tingkat not in ("info", "perhatian", "serius"):
                raise ValueError(f"{path}:{no}: tingkat harus 'info', 'perhatian', atau 'serius', bukan {tingkat!r}")

            inp = (baris.get("input") or "").strip().lower()
            nilai = (baris.get("nilai_juta_ntd") or "").replace(",", "").strip()

            if inp and inp not in ("capex", "debt", "cash", "risiko", "modal", "laporan", "berat", "tata_kelola"):
                raise ValueError(f"{path}:{no}: input {inp!r} tidak dikenal")

            if kep == "terbit":
                if inp in ("capex", "debt", "cash"):
                    if not nilai:
                        raise ValueError(f"{path}:{no}: keputusan=terbit wajib mengisi input dan nilai_juta_ntd")
                elif not inp:
                    raise ValueError(f"{path}:{no}: keputusan=terbit wajib mengisi input")

            g = gold.setdefault(url, {
                "kode": (baris.get("kode") or "").strip(),
                "harus_terbit": kep == "terbit",
                "keputusan": kep,
                "tingkat": tingkat or None,
                "input": inp or None,
                "angka": [],
                "pelabel": set(),
            })

            if kep != g["keputusan"]:
                raise ValueError(f"{path}:{no}: keputusan bertentangan dengan baris lain untuk URL yang sama")
            if tingkat and g.get("tingkat") and g["tingkat"] != tingkat:
                raise ValueError(f"{path}:{no}: tingkat bertentangan dengan baris lain untuk URL yang sama")

            if inp and not g.get("input"):
                g["input"] = inp
            g["pelabel"].add((baris.get("pelabel") or "").strip())
            if inp == "risiko":
                g["risiko"] = True
            elif inp in ("capex", "debt", "cash") and nilai:
                g["angka"].append((inp, float(nilai)))
            elif inp in ("modal", "laporan", "berat", "tata_kelola") and nilai:
                try:
                    g["angka"].append((inp, float(nilai)))
                except ValueError:
                    pass
    return gold


def status_ke_keputusan(st: str) -> str:
    """Konversi status sistem (terbit/ditahan/dilewati) ke keputusan gold (terbit/tahan/arsip)."""
    if st == "terbit":
        return "terbit"
    if st == "ditahan":
        return "tahan"
    if st == "dilewati":
        return "arsip"
    return st


def _sama(a: float, b: float) -> bool:
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) <= TOLERANSI


# --------------------------------------------------------------------------- mode

def _tanpa_pemeriksa(detail: dict) -> dict:
    """Saringan + penyari, tanpa tahap pemeriksa. Apa pun yang tertarik dianggap terbit."""
    s = screen.saring(detail)
    if not s["lolos"]:
        return {"status": "dilewati", "terbit": [], "meta": {}, "sinyal": None}
    temuan, meta = extract.sari(detail, s["input_mungkin"])
    angka = [(t["input"], t["nilai_juta_ntd"]) for t in temuan if t.get("nilai_juta_ntd") is not None]
    # Tanpa pemeriksa, angka yang tidak bisa dikonversi tetap "terbit" dalam bentuk
    # mentah — itulah yang dilakukan LLM polos. Dicatat sebagai angka tak terbandingkan.
    mentah = [(t["input"], None) for t in temuan if t.get("nilai_juta_ntd") is None]
    return {"status": "terbit" if (angka or mentah) else "ditahan",
            "terbit": angka + mentah, "meta": meta, "sinyal": None}


def _pipeline(detail: dict) -> dict:
    h = pipeline.jalankan(detail, store.muat_valuasi(detail.get("code", "")))
    terbit = []
    if h["status"] == "terbit":
        for d in (h.get("muatan") or {}).get("diterima", []):
            terbit.append((d["temuan"]["input"], d["temuan"]["nilai_juta_ntd"]))
    r = h["ringkasan"]
    return {
        "status": h["status"],
        "terbit": terbit,
        "meta": r,
        "state": h.get("state"),
        "kategori": kategori(h),
        "sebab_cadangan": _sebab_cadangan(h),
        "sinyal": (h.get("muatan") or {}).get("sinyal"),
    }


def kategori(h: dict) -> str:
    """Satu kategori akhir per pengumuman, untuk tabel kategori error/terminasi."""
    st = h.get("status")
    muatan = h.get("muatan") or {}
    if st == "terbit":
        return "terbit.manusia" if h.get("keputusan_manusia") else "terbit"
    if st == "dilewati":
        if (h.get("alasan_i18n") or {}).get("kode") == "akhir.di_bawah_ambang":
            return "arsip.di_bawah_ambang"
        if h.get("keputusan_manusia"):
            return "arsip.manusia"
        kode = (h.get("alasan_i18n") or {}).get("kode") or ""
        if kode.startswith("akhir.modal"):
            return "arsip." + kode.split(".", 1)[1]          # modal_treasuri, modal_kecil, modal_lain
        return "arsip.saringan_pasal"
    if st == "ditahan":
        jenis = (muatan.get("tahan") or {}).get("jenis", "lain")
        if jenis == "verifikasi":
            kode = sorted({k for d in muatan.get("ditolak", []) for k in d.get("gagal_kode", [])})
            return "tahan.verifikasi:" + "+".join(kode)
        return f"tahan.{jenis}"
    return st or "?"


def _sebab_cadangan(h: dict) -> str | None:
    for l in h.get("jejak", []):
        m = l.get("meta") or {}
        if m.get("cadangan"):
            sebab = str(m.get("sebab_cadangan") or "")
            return "tanpa kunci API" if "kunci" in sebab else (sebab.split(":")[0][:60] or "lain")
    return None


def jalankan_mode(mode: str, data: list[dict]) -> list[dict]:
    kunci_asli = config.API_KEY
    try:
        if mode == "aturan":
            config.API_KEY = ""
        elif mode == "model" and not kunci_asli:
            raise SystemExit("Mode 'model' butuh GEMINI_API_KEY di environment.")
        keluar = []
        for d in data:
            hasil = _tanpa_pemeriksa(d) if mode == "tanpa-pemeriksa" else _pipeline(d)
            hasil["source_url"] = d.get("source_url")
            hasil["id"] = store.id_pengumuman(d)
            keluar.append(hasil)
        return keluar
    finally:
        config.API_KEY = kunci_asli


# --------------------------------------------------------------------------- metrik

def nilai(hasil: list[dict], gold: dict[str, dict]) -> dict:
    from app import ambang_profil
    n = len(hasil)
    tepat = terbit_benar = salah_terbit = terlewat = ditahan = 0
    input_benar = input_total = 0
    # Metrik angka hanya untuk baris yang memuat angka input DCF (capex/cash/debt). Sinyal B1
    # dinilai lewat keputusan 3 arah dan tingkat, bukan lewat angka.
    harus_ya = sum(1 for h in hasil if gold[h["source_url"]]["harus_terbit"] and gold[h["source_url"]]["angka"])
    rincian = []

    keputusan_3arah_tepat = 0
    matriks_3x3 = {gk: {pk: 0 for pk in ("terbit", "tahan", "arsip")} for gk in ("terbit", "tahan", "arsip")}
    tingkat_cocok = 0
    tingkat_total = 0

    for h in hasil:
        g = gold[h["source_url"]]
        terbit = h["status"] == "terbit"
        tepat += terbit == g["harus_terbit"]
        ditahan += h["status"] == "ditahan"

        pred_kep = status_ke_keputusan(h["status"])
        gold_kep = g.get("keputusan") or ("terbit" if g["harus_terbit"] else "arsip")
        if pred_kep == gold_kep:
            keputusan_3arah_tepat += 1
        if gold_kep in matriks_3x3 and pred_kep in matriks_3x3[gold_kep]:
            matriks_3x3[gold_kep][pred_kep] += 1

        if g.get("tingkat"):
            tingkat_total += 1
            sinyal = h.get("sinyal")
            res_tingkat = ambang_profil.tingkat(sinyal, "moderat") if sinyal else None
            pred_tingkat = res_tingkat.get("tingkat") if res_tingkat else None
            if pred_tingkat == g["tingkat"]:
                tingkat_cocok += 1

        salah = [(i, v) for i, v in h["terbit"]
                 if v is None or not any(i == gi and _sama(v, gv) for gi, gv in g["angka"])]
        benar = [(i, v) for i, v in h["terbit"] if (i, v) not in salah]
        for i, _v in h["terbit"]:
            if g["angka"]:
                input_total += 1
                input_benar += any(i == gi for gi, _ in g["angka"])
        if salah:
            salah_terbit += 1
        if g["harus_terbit"] and g["angka"]:
            if benar and not salah:
                terbit_benar += 1
            else:
                terlewat += 1
        rincian.append({"id": h["id"], "status": h["status"], "harus_terbit": g["harus_terbit"],
                        "keputusan": gold_kep, "pred_keputusan": pred_kep,
                        "terbit": h["terbit"], "angka_salah": salah})

    meta = [h["meta"] for h in hasil]
    latensi = [m.get("durasi_total_ms", m.get("latensi_ms", 0)) for m in meta if m]
    return {
        "dokumen": n,
        "keputusan_tepat": tepat,
        "harus_terbit": harus_ya,
        "terbit_dengan_angka_benar": terbit_benar,
        "dokumen_dengan_angka_salah_terbit": salah_terbit,
        "terlewat": terlewat,
        "ditahan_untuk_manusia": ditahan,
        "panggilan_model": sum(m.get("panggilan_model", 0 if m.get("penyedia") in (None, "aturan") else 1)
                               for m in meta),
        "token_masuk": sum(m.get("token_masuk", 0) for m in meta),
        "token_keluar": sum(m.get("token_keluar", 0) for m in meta),
        "retry": sum(m.get("retry", 0) for m in meta),
        "jatuh_ke_cadangan": sum(1 for m in meta if m.get("pakai_cadangan") or m.get("cadangan")),
        "jawaban_cache": sum(m.get("jawaban_cache", 0) for m in meta),
        "token_pikir": sum(m.get("token_pikir", 0) for m in meta),
        "biaya_usd": round(sum(m.get("biaya_usd", 0) or 0 for m in meta), 6),
        "latensi_median_ms": int(statistics.median(latensi)) if latensi else 0,
        "latensi_rata_ms": int(statistics.mean(latensi)) if latensi else 0,
        "latensi_maks_ms": max(latensi) if latensi else 0,
        "akurasi_input": [input_benar, input_total],
        "akurasi_nilai": [sum(1 for r in rincian for i, v in r["terbit"] if (i, v) not in r["angka_salah"]),
                          sum(len(r["terbit"]) for r in rincian)],
        "keputusan_3arah_tepat": keputusan_3arah_tepat,
        "matriks_3x3": matriks_3x3,
        "kecocokan_tingkat": [tingkat_cocok, tingkat_total],
        "kategori": dict(collections.Counter(h.get("kategori", h["status"]) for h in hasil)),
        "rincian": rincian,
    }


def _persen(a: int, b: int) -> str:
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "—"


def laporan(m_per_mode: dict[str, dict], sumber: str, gold_path: str, label_mode: dict[str, str],
            tak_berlabel: int, menit_manual: float | None) -> str:
    mode = list(m_per_mode)
    baris = [
        "# Evaluasi Appendix 2",
        "",
        f"- Waktu: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Sumber data: **{sumber}**",
        f"- Gold set: `{os.path.relpath(gold_path, ROOT)}`",
        f"- Dokumen berlabel yang dievaluasi: {next(iter(m_per_mode.values()))['dokumen'] if m_per_mode else 0}"
        f" · tidak berlabel (dilewati): {tak_berlabel}",
        "",
        "| Metrik | " + " | ".join(f"{m} ({label_mode[m]})" for m in mode) + " |",
        "|---|" + "---|" * len(mode),
    ]

    def row(nama, f):
        baris.append(f"| {nama} | " + " | ".join(f(m_per_mode[m]) for m in mode) + " |")

    row("**Angka salah yang terbit** (makin kecil makin baik)",
        lambda x: _persen(x["dokumen_dengan_angka_salah_terbit"], x["dokumen"]))
    row("Keputusan terbit/tidak tepat", lambda x: _persen(x["keputusan_tepat"], x["dokumen"]))
    row("Terbit dengan angka benar", lambda x: _persen(x["terbit_dengan_angka_benar"], x["harus_terbit"]))
    row("Terlewat", lambda x: _persen(x["terlewat"], x["harus_terbit"]))
    row("Ditahan untuk manusia (tingkat intervensi)",
        lambda x: _persen(x["ditahan_untuk_manusia"], x["dokumen"]))
    row("Panggilan model", lambda x: str(x["panggilan_model"]))
    row("Jawaban model dari cache", lambda x: str(x.get("jawaban_cache", 0)))
    row("Token masuk / keluar / berpikir",
        lambda x: f"{x['token_masuk']} / {x['token_keluar']} / {x.get('token_pikir', 0)}")
    row("Biaya model (USD, tarif berbayar di app/agent/llm.py)", lambda x: f"{x.get('biaya_usd', 0):.4f}")
    row("Retry", lambda x: str(x["retry"]))
    row("Jatuh ke penalar aturan", lambda x: str(x["jatuh_ke_cadangan"]))
    row("Latensi median / rata-rata / maks per dokumen",
        lambda x: f"{x['latensi_median_ms']} / {x.get('latensi_rata_ms', 0)} / {x.get('latensi_maks_ms', 0)} ms")
    row("Akurasi field: jenis input (capex/debt/cash)", lambda x: _persen(*x.get("akurasi_input", [0, 0])))
    row("Akurasi field: nilai (±0,5%)", lambda x: _persen(*x.get("akurasi_nilai", [0, 0])))
    row("Akurasi keputusan 3 arah (terbit/tahan/arsip)",
        lambda x: _persen(x.get("keputusan_3arah_tepat", 0), x["dokumen"]))
    row("Kecocokan tingkat sinyal (moderat)",
        lambda x: _persen(*x.get("kecocokan_tingkat", [0, 0])))
    if menit_manual is not None:
        row(f"Waktu manual setara (@{menit_manual:g} menit/dokumen)",
            lambda x: f"{x['dokumen'] * menit_manual:g} menit")

    baris += ["", "## Matriks kebingungan keputusan 3 arah (Gold \\ Prediksi)", ""]
    for m in mode:
        mat = m_per_mode[m].get("matriks_3x3") or {}
        baris.append(f"### Mode: {m} ({label_mode[m]})")
        baris.append("")
        baris.append("| Gold \\ Prediksi | terbit | tahan | arsip |")
        baris.append("|---|---|---|---|")
        for gk in ("terbit", "tahan", "arsip"):
            r = mat.get(gk, {})
            baris.append(f"| {gk} | {r.get('terbit', 0)} | {r.get('tahan', 0)} | {r.get('arsip', 0)} |")
        baris.append("")

    baris += ["", "## Kasus yang salah atau terlewat", ""]
    ada = False
    for m in mode:
        for r in m_per_mode[m]["rincian"]:
            if r["angka_salah"] or (r["harus_terbit"] != (r["status"] == "terbit")):
                ada = True
                baris.append(f"- `{m}` · `{r['id']}` · status `{r['status']}`, "
                             f"harus terbit: {'ya' if r['harus_terbit'] else 'tidak'}"
                             + (f", angka salah: {r['angka_salah']}" if r["angka_salah"] else ""))
    if not ada:
        baris.append("Tidak ada.")
    return "\n".join(baris) + "\n"


# --------------------------------------------------------------------------- D4: operasional

def _pct(xs: list[int], p: float) -> int:
    if not xs:
        return 0
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


def operasional(hasil: list[dict], harga_token: tuple[float, float] | None = None) -> dict:
    """Metrik operasi Appendix 2 atas semua pengumuman, tanpa label."""
    meta = [h["meta"] for h in hasil]
    lat = [m.get("durasi_total_ms", 0) for m in meta]
    tin = sum(m.get("token_masuk", 0) for m in meta)
    tout = sum(m.get("token_keluar", 0) for m in meta)
    n = len(hasil)
    ditahan = sum(1 for h in hasil if h["status"] == "ditahan")
    sampai_model = sum(1 for h in hasil if h.get("kategori") != "arsip.saringan_pasal")
    biaya = None
    if harga_token:
        biaya = round(tin / 1e6 * harga_token[0] + tout / 1e6 * harga_token[1], 4)
    return {
        "dokumen": n,
        "state": dict(collections.Counter(h.get("state") or h["status"] for h in hasil)),
        "kategori": dict(collections.Counter(h.get("kategori", h["status"]) for h in hasil).most_common()),
        "latensi_ms": {"rata": int(statistics.mean(lat)) if lat else 0,
                       "median": int(statistics.median(lat)) if lat else 0,
                       "p95": _pct(lat, 0.95), "maks": max(lat) if lat else 0},
        "lolos_saringan": sampai_model,
        "panggilan_model": sum(m.get("panggilan_model", 0) for m in meta),
        "jawaban_cache": sum(m.get("jawaban_cache", 0) for m in meta),
        "token_masuk": tin, "token_keluar": tout,
        "biaya_usd_free_tier": round(sum(m.get("biaya_usd", 0.0) for m in meta), 4),
        "biaya_usd_perkiraan_berbayar": biaya,
        "retry": sum(m.get("retry", 0) for m in meta),
        "jatuh_ke_cadangan": dict(collections.Counter(h["sebab_cadangan"] for h in hasil if h.get("sebab_cadangan"))),
        "intervensi_manusia": {"ditahan": ditahan, "persen_dari_semua": round(100 * ditahan / n, 1) if n else 0,
                               "persen_dari_lolos_saringan": round(100 * ditahan / sampai_model, 1) if sampai_model else 0},
        "terbit": sum(1 for h in hasil if h["status"] == "terbit"),
    }


def laporan_operasional(m: dict, sumber: str, mode: str) -> str:
    b = [
        "# Evaluasi operasional (Appendix 2, tanpa gold set)", "",
        f"- Waktu: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Sumber data: **{sumber}** · penyari: **{mode}**",
        f"- Pengumuman: {m['dokumen']} · lolos saringan pasal: {m['lolos_saringan']}", "",
        "| Metrik | Nilai |", "|---|---|",
        f"| Terbit (PUBLISHED) | {m['terbit']} |",
        f"| Sebaran state | {', '.join(f'{k} {v}' for k, v in sorted(m['state'].items()))} |",
        f"| Latensi rata-rata / median / p95 / maks | {m['latensi_ms']['rata']} / {m['latensi_ms']['median']} / "
        f"{m['latensi_ms']['p95']} / {m['latensi_ms']['maks']} ms |",
        f"| Panggilan model / jawaban dari cache | {m['panggilan_model']} / {m['jawaban_cache']} |",
        f"| Token masuk / keluar | {m['token_masuk']} / {m['token_keluar']} |",
        f"| Biaya (free tier) | ${m['biaya_usd_free_tier']} |",
        f"| Biaya perkiraan tier berbayar | {('$' + str(m['biaya_usd_perkiraan_berbayar'])) if m['biaya_usd_perkiraan_berbayar'] is not None else '— (beri --harga-token)'} |",
        f"| Retry | {m['retry']} |",
        f"| Jatuh ke penalar aturan (sebab) | {', '.join(f'{k}: {v}' for k, v in m['jatuh_ke_cadangan'].items()) or '0'} |",
        f"| Intervensi manusia (HELD) | {m['intervensi_manusia']['ditahan']} = {m['intervensi_manusia']['persen_dari_semua']}% "
        f"dari semua, {m['intervensi_manusia']['persen_dari_lolos_saringan']}% dari yang lolos saringan |",
        "", "## Kategori akhir (terminasi dan jenis error)", "",
        "| Kategori | Jumlah |", "|---|---|",
    ]
    b += [f"| `{k}` | {v} |" for k, v in m["kategori"].items()]
    b += ["", "Arti kategori: `arsip.saringan_pasal` dilewati karena pasal di luar daftar; "
          "`arsip.di_bawah_ambang` keyakinan triase di bawah ambang; `tahan.tanpa_angka` tidak ada angka "
          "bersumber; `tahan.tanpa_valuasi` belum ada model valuasi; `tahan.keyakinan` keyakinan di zona ragu; "
          "`tahan.verifikasi:<cek>` pemeriksa menolak, dengan kode cek yang gagal; "
          "`tahan.risiko_serius` sinyal penjaminan/pinjaman di atas ambang moderat; `tahan.risiko_berat` "
          "pasal 1/3/40; `arsip.modal_*` perubahan modal tanpa dampak (treasuri), tidak material, atau tidak dikenali."]
    return "\n".join(b) + "\n"


# --------------------------------------------------------------------------- D4: chatbot

def muat_chat_uji(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if (r.get("pertanyaan") or "").strip()]


def nilai_chat(kasus: list[dict]) -> dict:
    from app import chat
    rinci = []
    for k in kasus:
        h = chat.tanya(k["pertanyaan"], (k.get("bahasa") or "en").strip())
        harap = (k.get("harap") or "jawab").strip()
        if harap.startswith("tolak"):
            jenis = harap.split(":", 1)[1] if ":" in harap else None
            tepat = h["jalur"] == "tolak" and (jenis is None or h["ditolak"] == jenis)
        else:
            tepat = h["jalur"] != "tolak" and bool(h["sumber"]) and bool((h.get("periksa") or {}).get("lolos"))
            # "jawab:<alat>[:<jenis>]": jawaban juga harus memakai alat itu (dan jenis pengumuman
            # itu). Tanpa ini, jawaban yang bersumber tetapi tidak menjawab pertanyaan ikut dihitung benar.
            bagian = harap.split(":")
            if tepat and len(bagian) > 1 and bagian[1]:
                dipakai = [l for l in h["langkah"] if l.get("tahap") == "alat" and l.get("alat") == bagian[1]]
                if len(bagian) > 2 and bagian[2]:
                    dipakai = [l for l in dipakai if (l.get("args") or {}).get("jenis") == bagian[2]]
                tepat = bool(dipakai)
        rinci.append({"pertanyaan": k["pertanyaan"], "bahasa": k.get("bahasa"), "harap": harap,
                      "jalur": h["jalur"], "ditolak": h["ditolak"], "tepat": tepat, "id": h["id"],
                      "durasi_ms": h["durasi_ms"], "panggilan_alat": h["panggilan_alat"],
                      "panggilan_model": h["panggilan_model"],
                      "kata_terlarang": (h.get("periksa") or {}).get("kata_terlarang", []) if h["jalur"] in ("model",) else [],
                      "jawaban": h["jawaban"][:300]})
    lat = [r["durasi_ms"] for r in rinci]
    jawab = [r for r in rinci if not r["harap"].startswith("tolak")]
    tolak = [r for r in rinci if r["harap"].startswith("tolak")]
    return {
        "kasus": len(rinci), "tepat": sum(r["tepat"] for r in rinci),
        "jawab_tepat": [sum(r["tepat"] for r in jawab), len(jawab)],
        "tolak_tepat": [sum(r["tepat"] for r in tolak), len(tolak)],
        "jalur": dict(collections.Counter(r["jalur"] for r in rinci)),
        "kata_terlarang_terbit": sum(len(r["kata_terlarang"]) for r in rinci),
        "latensi_ms": {"rata": int(statistics.mean(lat)) if lat else 0, "maks": max(lat) if lat else 0},
        "panggilan_alat": sum(r["panggilan_alat"] for r in rinci),
        "panggilan_model": sum(r["panggilan_model"] for r in rinci),
        "rincian": rinci,
    }


def laporan_chat(m: dict) -> str:
    b = ["# Evaluasi Tanya FEAF (chatbot)", "",
         f"- Waktu: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
         f"- Model: **{config.MODEL if config.API_KEY else 'tanpa model (jalur aturan)'}**", "",
         "| Metrik | Nilai |", "|---|---|",
         f"| Tepat (semua kasus) | {_persen(m['tepat'], m['kasus'])} |",
         f"| Pertanyaan data dijawab, bersumber, lolos pemeriksa | {_persen(*m['jawab_tepat'])} |",
         f"| Pertanyaan di luar lingkup ditolak dengan benar | {_persen(*m['tolak_tepat'])} |",
         f"| Kata rekomendasi yang lolos | {m['kata_terlarang_terbit']} |",
         f"| Jalur jawaban | {', '.join(f'{k} {v}' for k, v in m['jalur'].items())} |",
         f"| Latensi rata-rata / maks | {m['latensi_ms']['rata']} / {m['latensi_ms']['maks']} ms |",
         f"| Panggilan alat / model | {m['panggilan_alat']} / {m['panggilan_model']} |",
         "", "## Kasus yang tidak tepat", ""]
    salah = [r for r in m["rincian"] if not r["tepat"]]
    b += [f"- `{r['id']}` ({r['bahasa']}) \"{r['pertanyaan']}\": harap `{r['harap']}`, jalur `{r['jalur']}`"
          for r in salah] or ["Tidak ada."]
    return "\n".join(b) + "\n"


def _simpan_laporan(nama: str, teks: str, data: dict) -> None:
    _tulis_hasil(nama, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), teks, data)


class _Terisolasi:
    """Jejak, ambang 👍/👎, dan keputusan review ke folder sementara selama evaluasi."""

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._asli = (config.TRACE_DIR, umpan_balik.FILE, review.KEPUTUSAN_FILE)
        config.TRACE_DIR = os.path.join(self._tmp.name, "traces")
        umpan_balik.FILE = os.path.join(self._tmp.name, "umpan_balik.json")
        review.KEPUTUSAN_FILE = os.path.join(self._tmp.name, "keputusan.json")
        return self

    def __exit__(self, *_):
        config.TRACE_DIR, umpan_balik.FILE, review.KEPUTUSAN_FILE = self._asli
        self._tmp.cleanup()


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--gold", default=GOLD_DEFAULT)
    ap.add_argument("--arsip", action="store_true",
                    help="ambil pengumuman juga dari arsip mentah penarik (semua emiten), bukan hanya watchlist")
    ap.add_argument("--mode", nargs="+", choices=MODE_SEMUA)
    ap.add_argument("--menit-manual", type=float, default=None,
                    help="menit per pengumuman secara manual, dari wawancara")
    ap.add_argument("--simpan", action="store_true", help="tulis laporan ke eval/hasil/")
    ap.add_argument("--operasional", action="store_true", help="metrik operasi atas semua pengumuman, tanpa gold set")
    ap.add_argument("--chat", nargs="?", const=CHAT_UJI_DEFAULT, default=None,
                    help="evaluasi Tanya FEAF dengan set pertanyaan uji (bawaan eval/chat_uji.csv)")
    ap.add_argument("--arsip-dir", default=None,
                    help="folder arsip mentah OpenAPI selain DATA_DIR/raw/openapi (nama berkas memuat twse/tpex)")
    ap.add_argument("--tanpa-salinan", action="store_true",
                    help="jangan lengkapi baris gold yang hilang dari eval/gold_dokumen.json")
    ap.add_argument("--tanpa-cache", action="store_true",
                    help="abaikan jawaban model yang tersimpan, supaya latensi dan biaya terukur dari panggilan asli")
    ap.add_argument("--harga-token", default=None,
                    help="'<USD/1jt token masuk>,<USD/1jt token keluar>' untuk perkiraan biaya berbayar")
    a = ap.parse_args(argv)
    if a.tanpa_cache:
        import tempfile
        from app.agent import llm
        llm.CACHE_DIR = tempfile.mkdtemp(prefix="feaf-eval-cache-")
    harga_token = tuple(float(x) for x in a.harga_token.split(",")) if a.harga_token else None

    if a.chat:
        with _Terisolasi():
            m = nilai_chat(muat_chat_uji(a.chat))
        teks = laporan_chat(m)
        print(teks)
        if a.simpan:
            _simpan_laporan("chat", teks, m)
        return 0

    if a.operasional:
        semua, sumber = store.muat_detail()
        if a.arsip or a.arsip_dir:
            from app import gold as _gold
            ada = {d.get("source_url") for d in semua}
            arsip = _gold.muat_arsip(a.arsip_dir) if a.arsip_dir else _gold.muat_arsip()
            semua = [d for d in semua if not d.get("_fixture")] + [d for d in arsip if d["source_url"] not in ada]
            sumber = f"{sumber} + arsip"
        if not semua:
            print("Tidak ada pengumuman.", file=sys.stderr)
            return 1
        penyari = config.MODEL if config.API_KEY else "penalar aturan"
        with _Terisolasi():
            m = operasional([_pipeline(d) for d in semua], harga_token)
        teks = laporan_operasional(m, sumber, penyari)
        print(teks)
        if a.simpan:
            _simpan_laporan("operasional", teks, m)
        return 0

    mode = a.mode or [m for m in MODE_SEMUA if m != "model" or config.API_KEY]
    gold = muat_gold(a.gold)
    semua, sumber = store.muat_detail()
    if a.arsip:
        from app import gold as _gold
        ada = {d.get("source_url") for d in semua}
        semua = semua + [d for d in _gold.muat_arsip() if d["source_url"] not in ada]
        sumber = f"{sumber} + arsip"
    data = [d for d in semua if d.get("source_url") in gold]
    tak_berlabel = len(semua) - len(data)
    hilang = set(gold) - {d.get("source_url") for d in data}
    if hilang and os.path.exists(GOLD_DOKUMEN) and not a.tanpa_salinan:
        with open(GOLD_DOKUMEN, encoding="utf-8") as f:
            salinan = json.load(f)
        tambah = [d for d in salinan["pengumuman"] if d.get("source_url") in hilang]
        _pakai_kapitalisasi_salinan(salinan.get("kapitalisasi") or {})
        if tambah:
            data += tambah
            hilang -= {d["source_url"] for d in tambah}
            sumber = f"{sumber} + salinan gold ({len(tambah)} dari eval/gold_dokumen.json)"
    if hilang:
        print(f"Peringatan: {len(hilang)} baris gold tidak ditemukan di data ({sumber}).", file=sys.stderr)
    if not data:
        print("Tidak ada dokumen berlabel di data yang tersedia.", file=sys.stderr)
        return 1

    penyari = config.MODEL if config.API_KEY else "penalar aturan"
    label_mode = {"aturan": "penalar aturan", "model": config.MODEL,
                  "tanpa-pemeriksa": penyari}

    # Jejak, ambang, dan keputusan review evaluasi tidak dicampur dengan milik aplikasi.
    with _Terisolasi():
        m_per_mode = {m: nilai(jalankan_mode(m, data), gold) for m in mode}

    teks = laporan(m_per_mode, sumber, a.gold, label_mode, tak_berlabel, a.menit_manual)
    print(teks)
    if a.simpan:
        _tulis_hasil("evaluasi", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), teks,
                     {"sumber": sumber, "mode": label_mode, "metrik": m_per_mode})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
