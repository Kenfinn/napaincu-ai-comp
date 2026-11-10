"""Tests for Ask FEAF (app/chat.py). No network: market data comes from tests/data/pasar_sampel.json
and the model is a scripted fake."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _sampel():
    with open(os.path.join(ROOT, "tests", "data", "pasar_sampel.json"), encoding="utf-8") as f:
        return json.load(f)


class _Dasar(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from app import chat, config, main, pasar, tarik
        self.chat, self.config, self.main, self.pasar, self.tarik = chat, config, main, pasar, tarik
        self._tmp = tempfile.TemporaryDirectory()
        self._asli = (pasar.CACHE_DIR, pasar._finmind, pasar._ambil_json, config.PARSED_DIR,
                      config.TRACE_DIR, config.DATA_DIR, tarik.WATCHLIST_FILE, config.API_KEY,
                      chat._gemini, list(chat._jam))
        pasar.CACHE_DIR = os.path.join(self._tmp.name, "pasar")
        config.PARSED_DIR = os.path.join(self._tmp.name, "parsed")      # → fixture
        config.TRACE_DIR = os.path.join(self._tmp.name, "traces")
        config.DATA_DIR = self._tmp.name                                  # chat traces
        tarik.WATCHLIST_FILE = os.path.join(self._tmp.name, "watchlist.json")
        config.API_KEY = ""

        def tanpa_jaringan(*_a, **_k):
            raise ConnectionError("tes tanpa jaringan")
        pasar._finmind = tanpa_jaringan
        pasar._ambil_json = tanpa_jaringan
        for nama, data in _sampel().items():
            pasar._tulis_cache(nama, data)
        main._cache = None
        self.c = TestClient(main.app)

    def tearDown(self):
        (self.pasar.CACHE_DIR, self.pasar._finmind, self.pasar._ambil_json, self.config.PARSED_DIR,
         self.config.TRACE_DIR, self.config.DATA_DIR, self.tarik.WATCHLIST_FILE, self.config.API_KEY,
         self.chat._gemini, jam) = self._asli
        self.chat._jam[:] = jam
        self.main._cache = None
        self._tmp.cleanup()

    def harga_2330(self) -> float:
        return self.pasar.harga("2330")["tutup"]


class TestPenjaga(_Dasar):
    def test_tolak_prediksi_order_pribadi_tiga_bahasa(self):
        kasus = {
            "prediksi": ["Will 2330 go up tomorrow?", "Apakah 2330 akan naik?", "2330 會漲嗎", "target price 2330"],
            "order": ["Buy it for me: 2330", "belikan 2330 seribu lembar", "幫我下單 2330"],
            "pribadi": ["What is the spokesman's phone number of 2330?", "2330 發言人是誰", "alamat rumah direktur 2330"],
        }
        for jenis, daftar in kasus.items():
            for q in daftar:
                with self.subTest(q=q):
                    h = self.chat.tanya(q, "en")
                    self.assertEqual((h["jalur"], h["ditolak"]), ("tolak", jenis))
                    self.assertEqual(h["panggilan_alat"], 0, "ditolak sebelum alat dipanggil")

    def test_pertanyaan_fakta_tidak_ditolak(self):
        for q in ("What is the revenue of 2330?", "Apakah laba 2330 naik?", "Berapa penjualan 2330?"):
            with self.subTest(q=q):
                self.assertIsNone(self.chat.tanya(q, "id")["ditolak"])

    def test_tanpa_kode_minta_kode(self):
        self.assertEqual(self.chat.tanya("apa kabar", "id")["ditolak"], "tanpa_kode")


class TestJalurAturan(_Dasar):
    def test_harga_dari_data_asli_bersumber(self):
        h = self.chat.tanya("What is the latest price of 2330?", "en")
        self.assertEqual(h["jalur"], "template")
        self.assertIn("2,235", h["jawaban"]) if self.harga_2330() == 2235 else None
        self.assertIn(self.pasar.SUMBER_PASAR["harga_twse"], h["sumber"])
        self.assertTrue(h["periksa"]["lolos"])

    def test_laporan_keuangan_dan_statistik(self):
        h = self.chat.tanya("2330 的營收和每股盈餘？", "zh")
        self.assertIn("每股盈餘", h["jawaban"])
        self.assertTrue(h["periksa"]["lolos"], h["periksa"])
        self.assertTrue(any("FinMind" in s for s in h["sumber"]))

    def test_jejak_tersimpan(self):
        h = self.chat.tanya("Valuasi 2330", "id")
        r = self.c.get(f"/api/tanya/jejak/{h['id']}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([l["tahap"] for l in r.json()["langkah"]][:2], ["pertanyaan", "penjaga"])


class TestPemeriksa(_Dasar):
    def test_angka_harus_ada_di_hasil_alat(self):
        alat = [{"tutup": 2235.0, "ubah_pct": 4.68, "tgl": "2026-11-09", "teks": "本益比25.91倍"}]
        self.assertTrue(self.chat.periksa_jawaban("2330 closed at NT$2,235 (4.68%), P/E 25.91.", alat, "2330")["lolos"])
        self.assertTrue(self.chat.periksa_jawaban("2330 ditutup NT$2.235 (4,68%).", alat, "2330")["lolos"])
        x = self.chat.periksa_jawaban("2330 收盤 2,300 元，本益比25.91。", alat, "2330")
        self.assertFalse(x["lolos"])
        self.assertEqual(x["angka_tidak_ada"], ["2,300"])

    def test_angka_dempet_aksara_mandarin_tetap_diperiksa(self):
        x = self.chat.periksa_jawaban("本益比99.9倍", [{"per": 25.91}], "2330")
        self.assertEqual(x["angka_tidak_ada"], ["99.9"])

    def test_kata_rekomendasi_ditolak_tapi_penjualan_boleh(self):
        self.assertFalse(self.chat.periksa_jawaban("You should buy 2330.", [{"x": 2330}], "2330")["lolos"])
        self.assertFalse(self.chat.periksa_jawaban("建議買進 2330", [{"x": 2330}], "2330")["lolos"])
        self.assertTrue(self.chat.periksa_jawaban("Penjualan 2330 naik.", [{"x": 2330}], "2330")["lolos"])

    def test_persen_dari_pecahan(self):
        self.assertTrue(self.chat.periksa_jawaban("ROE 34.78%", [{"roe": 0.3478}], "x")["lolos"])


class TestJalurModel(_Dasar):
    """Model palsu yang skripnya ditentukan tes: memanggil alat, lalu menjawab."""

    def _pasang(self, jawaban_akhir: str, panggilan=({"name": "harga", "args": {"kode": "2330"}},), ulang=False):
        self.config.API_KEY = "uji"
        urutan = []

        def palsu(contents, bahasa):
            urutan.append(len(contents))
            sudah_alat = any("functionResponse" in p for c in contents for p in c.get("parts", []))
            if ulang or not sudah_alat:
                return {"parts": [{"functionCall": dict(c)} for c in panggilan]}, {"model": "palsu", "token_masuk": 10, "token_keluar": 5}
            return {"parts": [{"text": jawaban_akhir}]}, {"model": "palsu", "token_masuk": 20, "token_keluar": 8}
        self.chat._gemini = palsu
        return urutan

    def test_jawaban_model_dengan_angka_benar_diterima(self):
        p = self.harga_2330()
        self._pasang(f"2330 closed at NT${p:,.0f} on the latest trading day.")
        h = self.chat.tanya("Price of 2330?", "en")
        self.assertEqual(h["jalur"], "model")
        self.assertEqual(h["panggilan_model"], 2)
        self.assertEqual(h["panggilan_alat"], 1)
        self.assertEqual(h["token_masuk"], 30)

    def test_jawaban_model_dengan_angka_karangan_ditolak(self):
        self._pasang("2330 closed at NT$9,999 and will reach 12,000.")
        h = self.chat.tanya("Price of 2330?", "en")
        self.assertEqual(h["jalur"], "template_setelah_tolak")
        self.assertIn("9,999", h["periksa"]["angka_tidak_ada"])
        self.assertNotIn("9,999", h["jawaban"])
        self.assertIn("9,999", h["jawaban_model_ditolak"], "jawaban yang ditolak tetap tercatat di jejak")

    def test_jawaban_model_dengan_saran_beli_ditolak(self):
        p = self.harga_2330()
        self._pasang(f"At NT${p:,.0f}, you should buy 2330.")
        h = self.chat.tanya("Price of 2330?", "en")
        self.assertEqual(h["jalur"], "template_setelah_tolak")
        self.assertIn("buy", [k.lower() for k in h["periksa"]["kata_terlarang"]])

    def test_berhenti_setelah_lima_langkah(self):
        urutan = self._pasang("tidak pernah dipakai", ulang=True)
        h = self.chat.tanya("Price of 2330?", "en")
        self.assertEqual(len(urutan), self.chat.MAX_STEPS)
        self.assertIn("batas_langkah", [l["tahap"] for l in h["langkah"]])
        self.assertEqual(h["jalur"], "template")

    def test_model_gagal_turun_ke_template(self):
        self.config.API_KEY = "uji"

        def gagal(contents, bahasa):
            from app.agent import llm
            raise llm.GagalModel("HTTP 503")
        self.chat._gemini = gagal
        h = self.chat.tanya("Price of 2330?", "en")
        self.assertEqual(h["jalur"], "template")
        self.assertIn("model_gagal", [l["tahap"] for l in h["langkah"]])

    def test_kode_tidak_sah_dari_model_ditolak_alat(self):
        self._pasang("ok", panggilan=({"name": "harga", "args": {"kode": "../../etc"}},))
        h = self.chat.tanya("Price of 2330?", "en")
        alat = [l for l in h["langkah"] if l["tahap"] == "alat"][0]
        self.assertEqual(alat["hasil"], {"galat": "invalid stock code"})


class TestHalaman(_Dasar):
    def test_halaman_tiga_bahasa_dengan_penafian(self):
        for bhs, potongan in (("en", "not a buy or sell recommendation"), ("zh", "並非買賣建議"), ("id", "bukan rekomendasi")):
            r = self.c.post("/tanya", data={"pertanyaan": "Price of 2330?"}, params={"lang": bhs},
                            follow_redirects=False)
            self.assertEqual(r.status_code, 303)
            r = self.c.get(r.headers["location"], params={"lang": bhs})
            self.assertEqual(r.status_code, 200)
            self.assertNotIn("⟦", r.text)
            self.assertIn(potongan, r.text)

    def test_api_json(self):
        r = self.c.post("/api/tanya", json={"pertanyaan": "2330 會漲嗎", "bahasa": "zh"})
        self.assertEqual(r.json()["ditolak"], "prediksi")


if __name__ == "__main__":
    unittest.main()
