"""Impor arsip OpenAPI mentah ke details.json tanpa duplikasi."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Pastikan root proyek ada di sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import config, tarik


def impor() -> dict[str, int]:
    folder = Path(config.DATA_DIR) / "raw" / "openapi"
    berkas_list = sorted(folder.glob("*.json")) if folder.exists() else []

    total_rekaman = 0
    kumpul: list[dict] = []
    for b in berkas_list:
        nama = b.name.lower()
        if "twse" in nama:
            sumber = "twse"
        elif "tpex" in nama:
            sumber = "tpex"
        else:
            continue
        try:
            with open(b, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Gagal membaca {b}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        total_rekaman += len(data)
        for r in data:
            if isinstance(r, dict):
                kumpul.append(tarik.normalkan(r, sumber, "arsip"))

    baru = tarik.gabung(kumpul) if kumpul else 0
    duplikat = total_rekaman - baru
    hasil = {
        "berkas": len(berkas_list),
        "rekaman": total_rekaman,
        "baru": baru,
        "duplikat": duplikat,
    }
    print(f"Selesai: {hasil['berkas']} berkas, {hasil['rekaman']} rekaman, {hasil['baru']} baru, {hasil['duplikat']} duplikat.")
    return hasil


if __name__ == "__main__":
    impor()
