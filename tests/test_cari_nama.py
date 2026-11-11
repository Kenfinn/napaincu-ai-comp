"""Tes unit untuk fitur pencarian emiten berdasarkan kode atau nama (S1).

Semua tes berjalan offline tanpa akses jaringan.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from app import indeks_nama
from app.main import app

SAMPEL_INDEKS = [
    {"kode": "2330", "nama": "台積電", "nama_en": "TSMC", "bursa": "TWSE"},
    {"kode": "2454", "nama": "聯發科", "nama_en": "MediaTek", "bursa": "TWSE"},
    {"kode": "2317", "nama": "鴻海", "nama_en": "HON HAI", "bursa": "TWSE"},
    {"kode": "6488", "nama": "環球晶", "nama_en": "GWC", "bursa": "TPEx"},
    {"kode": "2881", "nama": "富邦金", "nama_en": "Fubon Financial", "bursa": "TWSE"},
    {"kode": "2882", "nama": "國泰金", "nama_en": "CATHAY FHC", "bursa": "TWSE"},
    {"kode": "2303", "nama": "聯電", "nama_en": "UMC", "bursa": "TWSE"},
]


class TestCariNama(unittest.TestCase):
    """Pengujian logika pencarian dan kepatuhan privasi (S1)."""

    def setUp(self):
        self.client = TestClient(app, follow_redirects=False)

    def test_pencarian_sampel_kecil(self):
        """Memverifikasi seluruh kasus uji dari dokumen prompt:
        TSMC → 2330, 台積電 → 2330, tsmc → 2330, '台積' → memuat 2330, 2330 → 2330, 'zzz' → kosong.
        """
        # TSMC → 2330
        h = indeks_nama.cari("TSMC", indeks=SAMPEL_INDEKS)
        self.assertTrue(len(h) > 0)
        self.assertEqual(h[0]["kode"], "2330")

        # 台積電 → 2330
        h = indeks_nama.cari("台積電", indeks=SAMPEL_INDEKS)
        self.assertTrue(len(h) > 0)
        self.assertEqual(h[0]["kode"], "2330")

        # tsmc (huruf kecil) → 2330
        h = indeks_nama.cari("tsmc", indeks=SAMPEL_INDEKS)
        self.assertTrue(len(h) > 0)
        self.assertEqual(h[0]["kode"], "2330")

        # "台積" (awalan) → daftar memuat 2330
        h = indeks_nama.cari("台積", indeks=SAMPEL_INDEKS)
        kodes = [x["kode"] for x in h]
        self.assertIn("2330", kodes)

        # 2330 (kode persis) → 2330
        h = indeks_nama.cari("2330", indeks=SAMPEL_INDEKS)
        self.assertTrue(len(h) > 0)
        self.assertEqual(h[0]["kode"], "2330")

        # "zzz" → kosong
        h = indeks_nama.cari("zzz", indeks=SAMPEL_INDEKS)
        self.assertEqual(len(h), 0)

    def test_alias_populer_lainnya(self):
        """Memverifikasi alias populer: MediaTek, Hon Hai, Foxconn, Fubon, GlobalWafers."""
        # MediaTek → 2454
        h = indeks_nama.cari("MediaTek", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "2454")

        # Foxconn (alias tertulis) → 2317
        h = indeks_nama.cari("Foxconn", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "2317")

        # Hon Hai → 2317
        h = indeks_nama.cari("Hon Hai", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "2317")

        # 鴻海 → 2317
        h = indeks_nama.cari("鴻海", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "2317")

        # Fubon → 2881
        h = indeks_nama.cari("Fubon", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "2881")

        # 環球晶 & 6488
        h = indeks_nama.cari("環球晶", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "6488")
        h = indeks_nama.cari("GlobalWafers", indeks=SAMPEL_INDEKS)
        self.assertEqual(h[0]["kode"], "6488")

    def test_tidak_ada_data_pribadi_di_indeks(self):
        """Dilarang menyimpan nama pejabat, direktur, juru bicara, telepon, atau email."""
        baris_kotor = [
            {
                "公司代號": "2330",
                "公司簡稱": "台積電",
                "英文簡稱": "TSMC",
                "董事長": "張忠謀",
                "總經理": "魏哲家",
                "發言人": "黃仁昭",
                "發言人職稱": "副總經理",
                "電話": "03-5636688",
                "電子郵件": "spokesperson@tsmc.com",
            }
        ]
        ekstrak = indeks_nama._ekstrak_twse(baris_kotor)
        self.assertEqual(len(ekstrak), 1)
        item = ekstrak[0]
        self.assertEqual(set(item.keys()), {"kode", "nama", "nama_en", "bursa"})
        self.assertNotIn("董事長", item)
        self.assertNotIn("發言人", item)
        self.assertNotIn("電子郵件", item)

        # Cek saat ditulis ke berkas JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "indeks_nama.json")
            with patch("app.indeks_nama._ambil_url_json", return_value=baris_kotor):
                indeks_nama.bangun_indeks(paksa=True, berkas=target, data_dir=tmpdir)

            with open(target, encoding="utf-8") as f:
                konten = f.read()

            self.assertNotIn("張忠謀", konten)
            self.assertNotIn("魏哲家", konten)
            self.assertNotIn("董事長", konten)
            self.assertNotIn("發言人", konten)
            self.assertNotIn("spokesperson", konten)

    def test_apakah_cocok_persis(self):
        """Verifikasi deteksi kecocokan persis untuk pengalihan instan."""
        item_2330 = {"kode": "2330", "nama": "台積電", "nama_en": "TSMC"}
        self.assertTrue(indeks_nama.apakah_cocok_persis("2330", item_2330))
        self.assertTrue(indeks_nama.apakah_cocok_persis("tsmc", item_2330))
        self.assertTrue(indeks_nama.apakah_cocok_persis("TSMC", item_2330))
        self.assertTrue(indeks_nama.apakah_cocok_persis("台積電", item_2330))
        # Awalan saja bukan cocok persis
        self.assertFalse(indeks_nama.apakah_cocok_persis("台積", item_2330))

    def test_fallback_kode_angka_tanpa_indeks(self):
        """Jika indeks kosong atau jaringan gagal, kode angka tetap jalan."""
        h = indeks_nama.cari("2330", indeks=[])
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["kode"], "2330")

        # Tapi teks bukan kode tidak menghasilkan apa pun
        h2 = indeks_nama.cari("TSMC", indeks=[])
        self.assertEqual(len(h2), 0)

    def test_api_cari(self):
        """Endpoint /api/cari mengembalikan JSON daftar hasil."""
        with patch("app.indeks_nama.muat_indeks", return_value=SAMPEL_INDEKS):
            r = self.client.get("/api/cari?q=TSMC")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertTrue(len(data) > 0)
            self.assertEqual(data[0]["kode"], "2330")

            r_kosong = self.client.get("/api/cari?q=")
            self.assertEqual(r_kosong.status_code, 200)
            self.assertEqual(r_kosong.json(), [])

    def test_rute_saham_pencarian_alihan_dan_daftar(self):
        """Pengujian rute /saham: cocok persis redirect 303, banyak hasil render template, tidak ada hasil redirect pesan."""
        with patch("app.indeks_nama.muat_indeks", return_value=SAMPEL_INDEKS):
            # 1. Cocok persis TSMC → redirect 303 ke /saham/2330
            r = self.client.get("/saham?kode=TSMC")
            self.assertEqual(r.status_code, 303)
            self.assertEqual(r.headers["location"], "/saham/2330")

            # 2. Cocok kode 2330 → redirect 303 ke /saham/2330
            r = self.client.get("/saham?kode=2330")
            self.assertEqual(r.status_code, 303)
            self.assertEqual(r.headers["location"], "/saham/2330")

            # 3. Kueri kosong → redirect ke /watchlist
            r = self.client.get("/saham?kode=")
            self.assertEqual(r.status_code, 303)
            self.assertEqual(r.headers["location"], "/watchlist")

            # 4. Kueri tidak ditemukan "zzz" → redirect dengan pesan tidak ditemukan
            r = self.client.get("/saham?kode=zzz")
            self.assertEqual(r.status_code, 303)
            self.assertIn("pesan=", r.headers["location"])
            self.assertIn("sh.tidak_ditemukan", r.headers["location"])

            # 5. Banyak hasil (mis. "金") → render daftar cari_hasil.html
            r = self.client.get("/saham?kode=金")
            self.assertEqual(r.status_code, 200)
            self.assertIn("2881", r.text)
            self.assertIn("2882", r.text)
