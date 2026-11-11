"""Tes unit untuk keterlihatan dan tautan Tanya FEAF (C1a).

Semua tes berjalan offline tanpa akses jaringan.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from app.main import app


class TestC1aTautan(unittest.TestCase):
    """Pengujian keterlihatan Tanya FEAF di menu navigasi, halaman saham, dan form tanya."""

    def setUp(self):
        self.client = TestClient(app, follow_redirects=False)

    def test_menu_memuat_tanya_tiga_bahasa(self):
        """Menu samping kiri wajib memuat /tanya di antara Feed dan Review dalam 3 bahasa."""
        # 1. Bahasa Inggris
        r_en = self.client.get("/", cookies={"bahasa": "en"})
        self.assertEqual(r_en.status_code, 200)
        self.assertIn('href="/tanya"', r_en.text)
        self.assertIn("Ask FEAF", r_en.text)

        # 2. Bahasa Tradisional Mandarin
        r_zh = self.client.get("/", cookies={"bahasa": "zh"})
        self.assertEqual(r_zh.status_code, 200)
        self.assertIn('href="/tanya"', r_zh.text)
        self.assertIn("問 FEAF", r_zh.text)

        # 3. Bahasa Indonesia
        r_id = self.client.get("/", cookies={"bahasa": "id"})
        self.assertEqual(r_id.status_code, 200)
        self.assertIn('href="/tanya"', r_id.text)
        self.assertIn("Tanya FEAF", r_id.text)

    def test_halaman_saham_memuat_tautan_tanya(self):
        """Halaman saham wajib memuat tombol menuju /tanya?kode={kode} dalam 3 bahasa."""
        with patch("app.pasar.harga", return_value={"tutup": 1000.0, "ubah": 5.0, "ubah_pct": 0.5, "bursa": "TWSE", "tanggal": "2026/11/11"}):
            # English
            r_en = self.client.get("/saham/2330", cookies={"bahasa": "en"})
            self.assertEqual(r_en.status_code, 200)
            self.assertIn('href="/tanya?kode=2330"', r_en.text)
            self.assertIn("Ask about 2330", r_en.text)

            # Zh-TW
            r_zh = self.client.get("/saham/2330", cookies={"bahasa": "zh"})
            self.assertEqual(r_zh.status_code, 200)
            self.assertIn('href="/tanya?kode=2330"', r_zh.text)
            self.assertIn("詢問 2330", r_zh.text)

            # Indonesia
            r_id = self.client.get("/saham/2330", cookies={"bahasa": "id"})
            self.assertEqual(r_id.status_code, 200)
            self.assertIn('href="/tanya?kode=2330"', r_id.text)
            self.assertIn("Tanya tentang 2330", r_id.text)

    def test_halaman_tanya_dengan_parameter_kode(self):
        """Membuka /tanya?kode=2330 mengisi kotak pertanyaan dengan contoh pertanyaan sesuai bahasa."""
        # English
        r_en = self.client.get("/tanya?kode=2330", cookies={"bahasa": "en"})
        self.assertEqual(r_en.status_code, 200)
        self.assertIn("2330", r_en.text)
        self.assertIn('value="What changed recently for 2330?"', r_en.text)

        # Zh-TW
        r_zh = self.client.get("/tanya?kode=2330", cookies={"bahasa": "zh"})
        self.assertEqual(r_zh.status_code, 200)
        self.assertIn("2330 最近有什麼重大變化？", r_zh.text)

        # Indonesia
        r_id = self.client.get("/tanya?kode=2330", cookies={"bahasa": "id"})
        self.assertEqual(r_id.status_code, 200)
        self.assertIn("Apa yang berubah baru-baru ini untuk 2330?", r_id.text)

    def test_kode_tidak_sah_tidak_dipantulkan(self):
        """Karakter tidak sah seperti script tag dilarang dipantulkan langsung ke dalam kotak input."""
        r = self.client.get("/tanya?kode=<script>alert(1)</script>")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("<script>", r.text)
        self.assertNotIn("alert(1)", r.text)
        # Pastikan tidak ada tag skrip yang disisipkan
        self.assertNotIn('value="<script', r.text)
