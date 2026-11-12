"""Tes isolasi pemutus model per thread (QA-2)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import config, pasar, ringkasan  # noqa: E402
from app.agent import llm  # noqa: E402


class TestPemutusThread(unittest.TestCase):
    """Pemutus jatah dan batas waktu model hanya berlaku di thread yang menjalankan pipeline."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._asli = (
            llm.CACHE_DIR,
            llm._panggil_gemini,
            config.API_KEY,
            config.RETRY_MAKS,
            config.MODEL_CADANGAN,
            pasar.CACHE_DIR,
            pasar._finmind,
            pasar._ambil_json,
        )
        llm.CACHE_DIR = os.path.join(self._tmp.name, "cache_llm")
        config.API_KEY = "kunci-uji"
        config.RETRY_MAKS = 0
        config.MODEL_CADANGAN = []
        llm.selesai_jalan()

        pasar.CACHE_DIR = os.path.join(self._tmp.name, "cache_pasar")

        def tanpa_jaringan(*_a, **_k):
            raise ConnectionError("tes tanpa jaringan")

        pasar._finmind = tanpa_jaringan
        pasar._ambil_json = tanpa_jaringan
        with open(os.path.join(ROOT, "tests", "data", "pasar_sampel.json"), encoding="utf-8") as f:
            sampel = json.load(f)
        for nama, data in sampel.items():
            pasar._tulis_cache(nama, data)

        llm._panggil_gemini = lambda instruksi, dokumen: (
            {"temuan": []},
            {"token_masuk": 10, "token_keluar": 5, "biaya_usd": 0.0},
        )

    def tearDown(self):
        llm.selesai_jalan()
        (
            llm.CACHE_DIR,
            llm._panggil_gemini,
            config.API_KEY,
            config.RETRY_MAKS,
            config.MODEL_CADANGAN,
            pasar.CACHE_DIR,
            pasar._finmind,
            pasar._ambil_json,
        ) = self._asli
        self._tmp.cleanup()

    def test_a_setelah_jalan_nol_selesai_thread_sama_berhasil(self):
        """Thread A: with llm.jalan(0): llm.tanya -> GagalModel. Setelah blok selesai, berhasil."""
        with llm.jalan(0):
            with self.assertRaises(llm.GagalModel):
                llm.tanya("instruksi-a", "dokumen-a1")

        jawab, meta = llm.tanya("instruksi-a", "dokumen-a2")
        self.assertEqual(jawab, {"temuan": []})
        self.assertFalse(meta.get("cache"))

    def test_b_saat_thread_a_dalam_jalan_nol_thread_b_berhasil(self):
        """Saat thread A masih di dalam with llm.jalan(0), llm.tanya dari thread B berhasil."""
        siap = threading.Event()
        lanjut = threading.Event()
        hasil_b: dict = {}

        def kerja_a():
            with llm.jalan(0):
                siap.set()
                lanjut.wait(timeout=5)
                with self.assertRaises(llm.GagalModel):
                    llm.tanya("instruksi-b", "dokumen-a")

        def kerja_b():
            siap.wait(timeout=5)
            try:
                jawab, _ = llm.tanya("instruksi-b", "dokumen-b")
                hasil_b["ok"] = jawab == {"temuan": []}
            except Exception as e:  # noqa: BLE001
                hasil_b["galat"] = str(e)
            finally:
                lanjut.set()

        ta = threading.Thread(target=kerja_a)
        tb = threading.Thread(target=kerja_b)
        ta.start()
        tb.start()
        ta.join(timeout=5)
        tb.join(timeout=5)
        self.assertTrue(hasil_b.get("ok"), f"Thread B gagal: {hasil_b}")

    def test_c_batas_waktu_habis_tidak_memblokir_thread_lain(self):
        """Setelah with llm.jalan(40) yang dimulai >90 detik lalu, panggilan dari thread lain tetap berhasil."""
        t0 = 1000.0
        with patch.object(time, "monotonic", side_effect=[t0, t0 + 95.0, t0 + 96.0, t0 + 97.0, t0 + 98.0]):
            with llm.jalan(40):
                with self.assertRaises(llm.GagalModel) as ctx:
                    llm.tanya("instruksi-c", "dokumen-c1")
                self.assertIn("batas waktu", str(ctx.exception))

        hasil_lain: dict = {}

        def panggil_thread_lain():
            jawab, _ = llm.tanya("instruksi-c", "dokumen-c2")
            hasil_lain["ok"] = jawab == {"temuan": []}

        t = threading.Thread(target=panggil_thread_lain)
        t.start()
        t.join(timeout=5)
        self.assertTrue(hasil_lain.get("ok"))

    def test_d_ringkasan_agresif_memakai_narasi_model(self):
        """ringkasan.susun('2330', 'en', 'agresif', ...) dengan model di-mock -> sumber == 'model'."""
        llm._panggil_gemini = lambda instruksi, dokumen: (
            {"ringkasan": "Revenue grew 31.6% in 2025, and return on equity is 34.8%. The investor makes the decision."},
            {"token_masuk": 20, "token_keluar": 15, "biaya_usd": 0.0},
        )
        with llm.jalan(0):
            pass
        rk = ringkasan.susun("2330", "en", "agresif", [])
        self.assertEqual(rk["narasi"]["sumber"], "model")
        self.assertIn("31.6%", rk["narasi"]["teks"])


if __name__ == "__main__":
    unittest.main()
