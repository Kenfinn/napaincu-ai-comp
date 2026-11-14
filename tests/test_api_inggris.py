"""Path API berbahasa Inggris (v1.2.0) dan alias lama yang tetap jalan."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import config, main, tarik

# path baru -> path lama (GET, tanpa jaringan)
PASANGAN_GET = {
    "/health": "/sehat",
    "/api/alerts": "/api/peringatan",
    "/api/thresholds": "/api/ambang",
    "/api/search?q=2330": "/api/cari?q=2330",
    "/api/traces/2330-2026-09-18-1": "/api/jejak/2330-2026-09-18-1",
}

LAMA = ("/sehat", "/periksa", "/api/peringatan", "/api/jejak", "/api/valuasi", "/api/saham",
        "/api/ambang", "/api/cari", "/api/impor", "/api/tanya")


class TestApiInggris(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(main.app)

    def test_path_baru_dan_lama_memberi_status_sama(self):
        with mock.patch("app.pasar.harga_dari_cache", return_value=None):
            for baru, lama in PASANGAN_GET.items():
                rb, rl = self.c.get(baru), self.c.get(lama)
                self.assertEqual(rb.status_code, rl.status_code, baru)
                self.assertIn(rb.status_code, (200, 404), baru)

    def test_health_ok(self):
        r = self.c.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("versi", r.json())

    def test_openapi_hanya_path_inggris(self):
        paths = self.c.get("/openapi.json").json()["paths"]
        for p in ("/health", "/check", "/api/alerts", "/api/traces/{id}", "/api/valuation/{code}",
                  "/api/stocks/{code}/financials", "/api/review", "/api/thresholds",
                  "/api/watchlist", "/api/search", "/api/ask", "/api/ask/traces/{id}",
                  "/api/import"):
            self.assertIn(p, paths)
        for p in paths:
            lama = any(p == x or p.startswith(x + "/") for x in LAMA)
            self.assertFalse(lama, f"path lama tampil di /docs: {p}")
        # halaman HTML tidak masuk dokumentasi API
        for p in ("/", "/watchlist", "/review", "/ambang", "/tanya"):
            self.assertNotIn(p, paths)

    def test_ringkasan_openapi_berbahasa_inggris(self):
        spec = self.c.get("/openapi.json").json()
        teks = " ".join(op.get("summary", "") for item in spec["paths"].values() for op in item.values())
        for kata in ("pengumuman", "Daftar", "Tarik", "Ambang", "Keluaran", "Cari emiten"):
            self.assertNotIn(kata, teks)
        self.assertNotIn("pemantau", spec["info"]["description"])

    def test_halaman_memakai_path_baru(self):
        with mock.patch("app.pasar.harga_dari_cache", return_value=None):
            r = self.c.get("/watchlist")
        self.assertIn('action="/check"', r.text)
        self.assertNotIn('action="/periksa"', r.text)
        js = open(os.path.join(config.ROOT, "app", "static", "chat.js"), encoding="utf-8").read()
        self.assertIn('"/api/ask"', js)
        self.assertNotIn('"/api/tanya"', js)


class TestImportHeaderInggris(unittest.TestCase):
    def setUp(self):
        self._asli = (config.KODE_AKSES, config.DATA_DIR, config.PARSED_DIR, tarik.WATCHLIST_FILE)
        self._tmp = tempfile.TemporaryDirectory()
        config.KODE_AKSES = "rahasia-uji"
        self.c = TestClient(main.app)

    def tearDown(self):
        config.KODE_AKSES = self._asli[0]
        self._tmp.cleanup()

    def test_header_x_access_code_dan_lama_diterima(self):
        for h in ({"X-Access-Code": "rahasia-uji"}, {"X-Kode-Akses": "rahasia-uji"}):
            for path in ("/api/import", "/api/impor"):
                r = self.c.post(path, json=[], headers=h)
                self.assertEqual(r.status_code, 200, (path, h))
                self.assertEqual(r.json()["baru"], 0)

    def test_kode_salah_ditolak_dengan_pesan_inggris(self):
        r = self.c.post("/api/import", json=[], headers={"X-Access-Code": "salah"})
        self.assertEqual(r.status_code, 403)
        self.assertIn("Wrong access code", r.json()["detail"])


class TestAskFieldInggris(unittest.TestCase):
    def test_field_question_dan_language_diteruskan(self):
        c = TestClient(main.app)
        tangkap = {}

        def palsu(pertanyaan, bahasa, **kw):
            tangkap.update(pertanyaan=pertanyaan, bahasa=bahasa, **kw)
            return {k: None for k in ("id", "jalur", "jawaban", "sumber", "tautan", "tanda", "periksa",
                                      "ditolak", "durasi_ms", "panggilan_model", "panggilan_alat")}

        with mock.patch("app.chat.tanya", side_effect=palsu):
            r = c.post("/api/ask", json={"question": "What is 2330?", "language": "zh"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(tangkap["pertanyaan"], "What is 2330?")
        self.assertEqual(tangkap["bahasa"], "zh")


if __name__ == "__main__":
    unittest.main()
