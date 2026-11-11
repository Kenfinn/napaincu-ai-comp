"""D4: metrik operasional dan evaluasi chatbot di scripts/evaluasi.py. Tanpa jaringan."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))


class TestOperasional(unittest.TestCase):
    def setUp(self):
        import evaluasi
        from app import config, gold
        self.ev, self.config = evaluasi, config
        self._tmp = tempfile.TemporaryDirectory()
        shutil.copy(os.path.join(ROOT, "tests", "data", "openapi_pasal_sampel.json"),
                    os.path.join(self._tmp.name, "20261110T000000Z-twse.json"))
        self.data = gold.muat_arsip(self._tmp.name)
        self._kunci = config.API_KEY
        config.API_KEY = ""

    def tearDown(self):
        self.config.API_KEY = self._kunci
        self._tmp.cleanup()

    def test_metrik_lengkap_dan_konsisten(self):
        with self.ev._Terisolasi():
            hasil = [self.ev._pipeline(d) for d in self.data]
        m = self.ev.operasional(hasil, (0.3, 2.5))
        self.assertEqual(m["dokumen"], len(self.data))
        self.assertEqual(sum(m["state"].values()), m["dokumen"])
        self.assertEqual(sum(m["kategori"].values()), m["dokumen"])
        for k in ("rata", "median", "p95", "maks"):
            self.assertIn(k, m["latensi_ms"])
        self.assertLessEqual(m["latensi_ms"]["median"], m["latensi_ms"]["maks"])
        self.assertEqual(m["biaya_usd_perkiraan_berbayar"], 0.0)          # tanpa model, tanpa token
        self.assertIn("arsip.saringan_pasal", m["kategori"])                # pasal 12 dilewati
        # Hanya jalur valuasi (pasal 20) yang memakai penyari; jalur sinyal tidak memanggil model.
        self.assertGreaterEqual(m["jatuh_ke_cadangan"].get("tanpa kunci API", 0), 1)
        self.assertLessEqual(m["jatuh_ke_cadangan"].get("tanpa kunci API", 0), m["lolos_saringan"])
        teks = self.ev.laporan_operasional(m, "uji", "penalar aturan")
        self.assertIn("Intervensi manusia", teks)

    def test_terisolasi_tidak_menulis_ke_data_aplikasi(self):
        from app import review, umpan_balik
        asli = (self.config.TRACE_DIR, umpan_balik.FILE, review.KEPUTUSAN_FILE)
        with self.ev._Terisolasi():
            self.assertNotEqual(umpan_balik.FILE, asli[1])
        self.assertEqual((self.config.TRACE_DIR, umpan_balik.FILE, review.KEPUTUSAN_FILE), asli)

    def test_kategori_verifikasi_memuat_kode_cek(self):
        h = {"status": "ditahan", "muatan": {"tahan": {"jenis": "verifikasi"},
                                             "ditolak": [{"gagal_kode": ["cek.mu", "cek.konversi"]}]}}
        self.assertEqual(self.ev.kategori(h), "tahan.verifikasi:cek.konversi+cek.mu")


class TestEvaluasiChat(unittest.TestCase):
    def setUp(self):
        import evaluasi
        from app import chat, config, main, pasar
        self.ev, self.config, self.pasar, self.main, self.chat = evaluasi, config, pasar, main, chat
        self._tmp = tempfile.TemporaryDirectory()
        self._asli = (pasar.CACHE_DIR, pasar._finmind, pasar._ambil_json, config.API_KEY,
                      config.DATA_DIR, config.PARSED_DIR)
        pasar.CACHE_DIR = os.path.join(self._tmp.name, "pasar")
        config.DATA_DIR = self._tmp.name
        config.PARSED_DIR = os.path.join(self._tmp.name, "parsed")
        config.API_KEY = ""

        def tanpa_jaringan(*_a, **_k):
            raise ConnectionError("tes tanpa jaringan")
        pasar._finmind = pasar._ambil_json = tanpa_jaringan
        with open(os.path.join(ROOT, "tests", "data", "pasar_sampel.json"), encoding="utf-8") as f:
            for nama, data in json.load(f).items():
                pasar._tulis_cache(nama, data)
        main._cache = None

    def tearDown(self):
        (self.pasar.CACHE_DIR, self.pasar._finmind, self.pasar._ambil_json, self.config.API_KEY,
         self.config.DATA_DIR, self.config.PARSED_DIR) = self._asli
        self.main._cache = None
        self._tmp.cleanup()

    def test_set_uji_bawaan_terbaca_dan_seimbang(self):
        kasus = self.ev.muat_chat_uji(self.ev.CHAT_UJI_DEFAULT)
        self.assertGreaterEqual(len(kasus), 20)
        self.assertEqual({k["bahasa"] for k in kasus}, {"en", "zh", "id"})
        self.assertTrue(any(k["harap"].startswith("tolak") for k in kasus))

    def test_nilai_chat_2330(self):
        kasus = [{"pertanyaan": "What is the latest price of 2330?", "bahasa": "en", "harap": "jawab"},
                 {"pertanyaan": "Will 2330 go up tomorrow?", "bahasa": "en", "harap": "tolak:prediksi"},
                 {"pertanyaan": "2330 的營收和每股盈餘？", "bahasa": "zh", "harap": "jawab"}]
        m = self.ev.nilai_chat(kasus)
        self.assertEqual(m["tepat"], 3, m["rincian"])
        self.assertEqual(m["kata_terlarang_terbit"], 0)
        self.assertIn("Tepat (semua kasus)", self.ev.laporan_chat(m))


if __name__ == "__main__":
    unittest.main()
