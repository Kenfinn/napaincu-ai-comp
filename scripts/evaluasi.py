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

from app import config, store                              # noqa: E402
from app.agent import extract, pipeline, screen            # noqa: E402

GOLD_DEFAULT = os.path.join(ROOT, "eval", "gold.csv")
HASIL_DIR = os.path.join(ROOT, "eval", "hasil")

# Selisih relatif yang masih dianggap angka yang sama. Kecil dengan sengaja: yang dicari
# adalah salah satuan (×1000) atau salah butir, bukan pembulatan.
TOLERANSI = 0.005

MODE_SEMUA = ("aturan", "model", "tanpa-pemeriksa")


# --------------------------------------------------------------------------- gold set

def muat_gold(path: str) -> dict[str, dict]:
    """source_url → {"harus_terbit": bool, "angka": [(input, nilai)], "kode": ..., ...}"""
    gold: dict[str, dict] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for no, baris in enumerate(csv.DictReader(f), start=2):
            url = (baris.get("source_url") or "").strip()
            if not url:
                continue
            ya = (baris.get("harus_terbit") or "").strip().lower()
            if not ya:
                continue                # kandidat yang belum dilabeli — dilewati, bukan galat
            if ya not in ("ya", "tidak"):
                raise ValueError(f"{path}:{no}: harus_terbit harus 'ya' atau 'tidak', bukan {ya!r}")
            g = gold.setdefault(url, {
                "kode": (baris.get("kode") or "").strip(),
                "harus_terbit": ya == "ya",
                "angka": [],
                "pelabel": set(),
            })
            if (ya == "ya") != g["harus_terbit"]:
                raise ValueError(f"{path}:{no}: harus_terbit bertentangan dengan baris lain untuk URL yang sama")
            g["pelabel"].add((baris.get("pelabel") or "").strip())
            if ya == "ya":
                inp = (baris.get("input") or "").strip()
                nilai = (baris.get("nilai_juta_ntd") or "").replace(",", "").strip()
                if inp == "risiko":
                    # Sinyal risiko (pasal 22/23/1/3/40): yang dinilai keputusan terbit/tahan,
                    # bukan satu angka input DCF.
                    g["risiko"] = True
                    continue
                if not inp or not nilai:
                    raise ValueError(f"{path}:{no}: harus_terbit=ya wajib mengisi input dan nilai_juta_ntd"
                                     " (kecuali input=risiko)")
                g["angka"].append((inp, float(nilai)))
    return gold


def _sama(a: float, b: float) -> bool:
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) <= TOLERANSI


# --------------------------------------------------------------------------- mode

def _tanpa_pemeriksa(detail: dict) -> dict:
    """Saringan + penyari, tanpa tahap pemeriksa. Apa pun yang tertarik dianggap terbit."""
    s = screen.saring(detail)
    if not s["lolos"]:
        return {"status": "dilewati", "terbit": [], "meta": {}}
    temuan, meta = extract.sari(detail, s["input_mungkin"])
    angka = [(t["input"], t["nilai_juta_ntd"]) for t in temuan if t.get("nilai_juta_ntd") is not None]
    # Tanpa pemeriksa, angka yang tidak bisa dikonversi tetap "terbit" dalam bentuk
    # mentah — itulah yang dilakukan LLM polos. Dicatat sebagai angka tak terbandingkan.
    mentah = [(t["input"], None) for t in temuan if t.get("nilai_juta_ntd") is None]
    return {"status": "terbit" if (angka or mentah) else "ditahan",
            "terbit": angka + mentah, "meta": meta}


def _pipeline(detail: dict) -> dict:
    h = pipeline.jalankan(detail, store.muat_valuasi(detail.get("code", "")))
    terbit = []
    if h["status"] == "terbit":
        for d in (h.get("muatan") or {}).get("diterima", []):
            terbit.append((d["temuan"]["input"], d["temuan"]["nilai_juta_ntd"]))
    r = h["ringkasan"]
    return {"status": h["status"], "terbit": terbit, "meta": r}


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
    n = len(hasil)
    tepat = terbit_benar = salah_terbit = terlewat = ditahan = 0
    harus_ya = sum(1 for h in hasil if gold[h["source_url"]]["harus_terbit"])
    rincian = []
    for h in hasil:
        g = gold[h["source_url"]]
        terbit = h["status"] == "terbit"
        tepat += terbit == g["harus_terbit"]
        ditahan += h["status"] == "ditahan"

        salah = [(i, v) for i, v in h["terbit"]
                 if v is None or not any(i == gi and _sama(v, gv) for gi, gv in g["angka"])]
        benar = [(i, v) for i, v in h["terbit"] if (i, v) not in salah]
        if salah:
            salah_terbit += 1
        if g["harus_terbit"]:
            if benar and not salah:
                terbit_benar += 1
            else:
                terlewat += 1
        rincian.append({"id": h["id"], "status": h["status"], "harus_terbit": g["harus_terbit"],
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
        "latensi_median_ms": int(statistics.median(latensi)) if latensi else 0,
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
    row("Token masuk / keluar", lambda x: f"{x['token_masuk']} / {x['token_keluar']}")
    row("Retry", lambda x: str(x["retry"]))
    row("Jatuh ke penalar aturan", lambda x: str(x["jatuh_ke_cadangan"]))
    row("Latensi median per dokumen", lambda x: f"{x['latensi_median_ms']} ms")
    if menit_manual is not None:
        row(f"Waktu manual setara (@{menit_manual:g} menit/dokumen)",
            lambda x: f"{x['dokumen'] * menit_manual:g} menit")

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
    a = ap.parse_args(argv)

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
    if hilang:
        print(f"Peringatan: {len(hilang)} baris gold tidak ditemukan di data ({sumber}).", file=sys.stderr)
    if not data:
        print("Tidak ada dokumen berlabel di data yang tersedia.", file=sys.stderr)
        return 1

    penyari = config.MODEL if config.API_KEY else "penalar aturan"
    label_mode = {"aturan": "penalar aturan", "model": config.MODEL,
                  "tanpa-pemeriksa": penyari}

    # Jejak evaluasi tidak dicampur dengan jejak aplikasi.
    trace_asli = config.TRACE_DIR
    with tempfile.TemporaryDirectory() as tmp:
        config.TRACE_DIR = tmp
        try:
            m_per_mode = {m: nilai(jalankan_mode(m, data), gold) for m in mode}
        finally:
            config.TRACE_DIR = trace_asli

    teks = laporan(m_per_mode, sumber, a.gold, label_mode, tak_berlabel, a.menit_manual)
    print(teks)
    if a.simpan:
        os.makedirs(HASIL_DIR, exist_ok=True)
        cap = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        with open(os.path.join(HASIL_DIR, f"evaluasi-{cap}.md"), "w", encoding="utf-8") as f:
            f.write(teks)
        with open(os.path.join(HASIL_DIR, f"evaluasi-{cap}.json"), "w", encoding="utf-8") as f:
            json.dump({"sumber": sumber, "mode": label_mode, "metrik": m_per_mode},
                      f, ensure_ascii=False, indent=2)
        print(f"Tersimpan di {os.path.relpath(HASIL_DIR, ROOT)}/evaluasi-{cap}.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
