"""Paket gold set untuk tim keuangan: Excel kandidat + isi lengkap pengumuman, tanpa nama orang.

    SENTINEL_DATA_DIR=<folder data> python3 scripts/buat_paket_gold.py --keluar docs/untuk-tim/gold-set-FEAF.xlsx

Lembar "Label" berisi satu baris per pengumuman dengan kolom isian berpilihan (dropdown).
Lembar "Isi pengumuman" memuat semua butir tiap pengumuman, supaya pelabel tidak perlu
membuka MOPS. Butir yang bisa memuat nama orang tidak ikut (aturan sama dengan app/gold.py).

Setelah diisi, ubah kembali ke CSV untuk evaluasi:
    python3 scripts/buat_paket_gold.py --ke-csv <berkas.xlsx> --keluar eval/gold.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import gold, store  # noqa: E402

KOLOM_ISI = ["keputusan", "tingkat", "input", "nilai_juta_ntd", "butir_no", "menit", "pelabel", "catatan"]
PILIHAN = {
    "keputusan": ["terbit", "tahan", "arsip"],
    "tingkat": ["info", "perhatian", "serius"],
    "input": ["capex", "cash", "debt", "risiko", "modal", "laporan", "berat", "tata_kelola"],
}
NAMA_PASAL = {
    20: "Perolehan/pelepasan aset", 22: "Penjaminan (背書保證)", 23: "Pinjaman dana (資金貸與)",
    11: "Perubahan modal/obligasi", 35: "Pembelian kembali saham", 31: "Laporan kuartal",
    1: "Gagal bayar", 3: "Penghentian produksi", 40: "Suspensi perdagangan",
    7: "Ganti auditor eksternal", 8: "Ganti pejabat", 6: "Ganti direksi badan hukum",
}


def _butir_aman(d: dict) -> list[tuple[str, str, str]]:
    pasal_orang = d.get("clause") in gold.PASAL_ORANG
    keluar = []
    for b in d.get("items", []):
        for x in [b] + b.get("sub", []):
            lbl = x.get("label_lengkap") or x.get("label") or ""
            if "姓名" in lbl or "姓名" in (b.get("label") or ""):
                continue
            if pasal_orang and not any(a in lbl for a in gold.LABEL_AMAN_ORANG):
                continue
            sat = f" ({x['satuan_label']})" if x.get("satuan_label") else ""
            keluar.append((str(x.get("no", "")), lbl + sat, x.get("value") or ""))
    return keluar


def buat_xlsx(rek: list[dict], keluar: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Label"
    kepala = ["no", "kode", "nama", "tanggal", "pasal", "jenis pasal", "judul", "ringkasan_butir"] + KOLOM_ISI + ["source_url"]
    ws.append(kepala)
    for i, d in enumerate(rek, start=1):
        ws.append([i, d.get("code"), d.get("name"), d.get("date"), d.get("clause"),
                   NAMA_PASAL.get(d.get("clause"), "Lain-lain"), d.get("subject"), gold._ringkas(d)]
                  + [""] * len(KOLOM_ISI) + [d.get("source_url", "")])
    isi_fill = PatternFill("solid", fgColor="FFF6DD")
    kepala_fill = PatternFill("solid", fgColor="E8ECF3")
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = kepala_fill
    awal = kepala.index("keputusan") + 1
    for baris in ws.iter_rows(min_row=2, min_col=awal, max_col=awal + len(KOLOM_ISI) - 1):
        for c in baris:
            c.fill = isi_fill
    for baris in ws.iter_rows(min_row=2):
        for c in baris:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    lebar = {"no": 5, "kode": 7, "nama": 10, "tanggal": 11, "pasal": 6, "jenis pasal": 18, "judul": 45,
             "ringkasan_butir": 60, "keputusan": 11, "tingkat": 11, "input": 12, "nilai_juta_ntd": 14,
             "butir_no": 9, "menit": 7, "pelabel": 8, "catatan": 35, "source_url": 20}
    from openpyxl.utils import get_column_letter
    for j, k in enumerate(kepala, start=1):
        ws.column_dimensions[get_column_letter(j)].width = lebar.get(k, 12)
    ws.column_dimensions[get_column_letter(len(kepala))].hidden = True
    ws.freeze_panes = "C2"
    n = len(rek) + 1
    for k, opsi in PILIHAN.items():
        col = get_column_letter(kepala.index(k) + 1)
        dv = DataValidation(type="list", formula1='"' + ",".join(opsi) + '"', allow_blank=True)
        dv.add(f"{col}2:{col}{n}")
        ws.add_data_validation(dv)

    ws2 = wb.create_sheet("Isi pengumuman")
    ws2.append(["no", "kode", "judul", "butir", "label", "isi"])
    for c in ws2[1]:
        c.font = Font(bold=True)
        c.fill = kepala_fill
    for i, d in enumerate(rek, start=1):
        for no, lbl, isi in _butir_aman(d):
            ws2.append([i, d.get("code"), d.get("subject"), no, lbl, isi])
    for col, w in zip("ABCDEF", (5, 7, 40, 6, 40, 80)):
        ws2.column_dimensions[col].width = w
    for baris in ws2.iter_rows(min_row=2):
        for c in baris:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws2.freeze_panes = "D2"
    wb.save(keluar)


def ke_csv(xlsx: str, keluar: str) -> int:
    """Lembar Label → format eval/gold.csv (baris yang belum diisi keputusan dilewati)."""
    from openpyxl import load_workbook
    ws = load_workbook(xlsx, read_only=True)["Label"]
    baris = list(ws.iter_rows(values_only=True))
    kepala = [str(k) for k in baris[0]]
    kol = ["source_url", "kode", "harus_terbit", "keputusan", "tingkat", "input", "nilai_juta_ntd",
           "butir_no", "pelabel", "catatan"]
    n = 0
    with open(keluar, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kol + ["menit"])
        w.writeheader()
        for r in baris[1:]:
            d = {k: ("" if v is None else str(v).strip()) for k, v in zip(kepala, r)}
            if not d.get("keputusan"):
                continue
            w.writerow({k: d.get(k, "") for k in kol + ["menit"]})
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--per-jalur", type=int, default=7)
    ap.add_argument("--ke-csv", default=None, help="ubah xlsx yang sudah diisi ke CSV gold")
    ap.add_argument("--snapshot", action="store_true",
                    help="tulis salinan pengumuman gold (tanpa butir nama) untuk eval/gold_dokumen.json")
    ap.add_argument("--gold", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    "eval", "gold.csv"))
    a = ap.parse_args()
    if a.snapshot:
        import json
        with open(a.gold, encoding="utf-8") as f:
            url = {r["source_url"] for r in csv.DictReader(f)}
        detail, _ = store.muat_detail()
        rek = [gold.untuk_snapshot(d) for d in detail if d.get("source_url") in url]
        rek.sort(key=lambda d: d["source_url"])
        from app import pasar
        kap = {}
        for k in sorted({d.get("code", "") for d in rek}):
            v = pasar.kapitalisasi_dari_cache(k)
            if v:
                kap[k] = v
        with open(a.keluar, "w", encoding="utf-8") as f:
            json.dump({"catatan": "Salinan pengumuman gold set (butir nama dibuang) dan kapitalisasi pasar "
                                  "saat evaluasi resmi, supaya hasil bisa diulang tanpa data server.",
                       "kapitalisasi": kap, "pengumuman": rek}, f, ensure_ascii=False, indent=1)
        print(f"{len(rek)} pengumuman → {a.keluar}")
        return
    if a.ke_csv:
        print(f"{ke_csv(a.ke_csv, a.keluar)} baris berlabel → {a.keluar}")
        return
    detail, _ = store.muat_detail()
    rek = gold.pilih(detail, per_jalur=a.per_jalur)
    rek.sort(key=lambda d: (gold.jalur_pengumuman(d), d.get("code", "")))
    buat_xlsx(rek, a.keluar)
    print(f"{len(rek)} pengumuman → {a.keluar}")


if __name__ == "__main__":
    main()
