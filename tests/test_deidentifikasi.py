"""Pastikan tidak ada nama pribadi anggota tim di kode aplikasi dan README."""

from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KATA = ("afin" + "zaki", "fer" + "ry", "pat" + "rice", "pd" + "k")
LARANGAN = re.compile(r"\b(?:" + "|".join(_KATA) + r")\b", re.IGNORECASE)
EKSTENSI_TEKS = {".py", ".html", ".css", ".js", ".md", ".txt", ".json", ".svg"}


def _berkas_diperiksa() -> list[str]:
    hasil = [os.path.join(ROOT, "README.md")]
    for akar, _, berkas in os.walk(os.path.join(ROOT, "app")):
        if "__pycache__" in akar:
            continue
        for nama in berkas:
            if os.path.splitext(nama)[1].lower() in EKSTENSI_TEKS:
                hasil.append(os.path.join(akar, nama))
    return sorted(hasil)


class TestDeidentifikasi(unittest.TestCase):
    def test_tanpa_nama_anggota_di_app_dan_readme(self):
        temuan: list[str] = []
        for path in _berkas_diperiksa():
            with open(path, encoding="utf-8") as f:
                for no, baris in enumerate(f, start=1):
                    m = LARANGAN.search(baris)
                    if m:
                        rel = os.path.relpath(path, ROOT)
                        temuan.append(f"{rel}:{no} ({m.group(0)})")
        self.assertEqual(temuan, [], f"Ditemukan nama terlarang: {temuan}")


if __name__ == "__main__":
    unittest.main()
