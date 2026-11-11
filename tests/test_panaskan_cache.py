"""Pengujian V2: skrip pemanasan cache emiten besar untuk persiapan demo."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import panaskan_cache


class TestPanaskanCache(unittest.TestCase):
    """Pemeriksaan unit skrip panaskan_cache.py tanpa ketergantungan jaringan."""

    def test_kode_mengalahkan_top(self):
        """Argumen --kode harus mengabaikan --top dan mengambil kode yang diberikan."""
        kode_input = ["2330", "2454", "2317"]
        hasil = panaskan_cache.tentukan_daftar_kode(kode_input, top_n=10)
        self.assertEqual(hasil, ["2330", "2454", "2317"])

    def test_top_mengambil_n_teratas(self):
        """Bila tanpa --kode, fungsi mengambil N teratas dari TOP_30_TWSE."""
        hasil = panaskan_cache.tentukan_daftar_kode(None, top_n=5)
        self.assertEqual(len(hasil), 5)
        self.assertEqual(hasil, panaskan_cache.TOP_30_TWSE[:5])

    def test_urutan_kode_dipertahankan_dan_unik(self):
        """Urutan kode yang diberikan tidak berubah dan kode duplikat disaring."""
        kode_input = ["2454", "2330", "2454", "2317"]
        hasil = panaskan_cache.tentukan_daftar_kode(kode_input, top_n=5)
        self.assertEqual(hasil, ["2454", "2330", "2317"])

    def test_galat_satu_kode_tidak_menghentikan_yang_lain(self):
        """Galat pengecualian pada satu emiten tidak menghentikan pemrosesan emiten berikutnya."""
        def mock_panaskan(kode, paksa=False, jeda=0.0):
            if kode == "GAGAL":
                return {
                    "kode": kode,
                    "nama": "Gagal Inc",
                    "status_valuasi": "galat",
                    "beta": "—",
                    "durasi_detik": 0.05,
                    "galat": "koneksi terputus",
                }
            return {
                "kode": kode,
                "nama": f"Emiten {kode}",
                "status_valuasi": "ok",
                "beta": "resmi (1.05)",
                "durasi_detik": 0.1,
                "galat": "",
            }

        with patch("panaskan_cache.panaskan_satu", side_effect=mock_panaskan):
            daftar = ["2330", "GAGAL", "2454"]
            ringkasan = panaskan_cache.jalankan(daftar, jeda=0.0)

            self.assertEqual(len(ringkasan), 3)
            self.assertEqual(ringkasan[0]["status_valuasi"], "ok")
            self.assertEqual(ringkasan[1]["status_valuasi"], "galat")
            self.assertEqual(ringkasan[2]["status_valuasi"], "ok")

    def test_panaskan_satu_emiten_keuangan_tidak_berlaku(self):
        """Emiten sektor keuangan dicatat sebagai 'tidak berlaku (keuangan)' tanpa galat."""
        d_keu = {
            "code": "2881",
            "name": "Fubon Financial",
            "tidak_berlaku": True,
            "tidak_bisa_dihitung": False,
        }
        with patch("app.pasar.profil", return_value={"nama": "Fubon Financial", "keuangan": True}), \
             patch("app.pasar.harga", return_value={"tutup": 85.0}), \
             patch("app.valuasi_otomatis.ambil", return_value=d_keu):
            info = panaskan_cache.panaskan_satu("2881", jeda=0.0)
            self.assertEqual(info["status_valuasi"], "tidak berlaku (keuangan)")
            self.assertEqual(info["beta"], "tidak berlaku")


if __name__ == "__main__":
    unittest.main()
