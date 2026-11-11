"""Pengujian V1: tab Valuation cepat dan penanganan beta di latar belakang."""

import io
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import harga_resmi, i18n, valuasi_otomatis
from fastapi.testclient import TestClient
from app.main import app


class TestV1Cepat(unittest.TestCase):
    """Pemeriksaan fitur V1: pemuatan cepat, background thread, retry 307, dan 3 bahasa."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_bangun_cepat_dengan_beta_sementara(self):
        """Cache harga harian kosong membuat bangun() selesai < 1 detik dengan beta_sementara=True."""
        profil_mock = {
            "nama": "MediaTek",
            "nama_en": "MediaTek Inc.",
            "bursa": "TWSE",
            "industri": "24",
            "keuangan": False,
        }
        harga_mock = {
            "nama": "MediaTek",
            "bursa": "TWSE",
            "tutup": 1200.0,
            "tanggal": "1150410",
        }
        neraca_raw = [
            {"date": "2025-12-31", "type": "CapitalStock", "value": 16000000000},
            {"date": "2025-12-31", "type": "CashAndCashEquivalents", "value": 50000000000},
            {"date": "2025-12-31", "type": "BondsPayable", "value": 10000000000},
            {"date": "2025-12-31", "type": "LongtermLiabilitiesCurrentPortion", "value": 2000000000},
        ]
        cfo_raw = [
            {"date": "2023-12-31", "type": "CashFlowsFromOperatingActivities", "value": 60000000000},
            {"date": "2023-12-31", "type": "PropertyAndPlantAndEquipment", "value": -15000000000},
            {"date": "2023-12-31", "type": "InterestExpense", "value": 500000000},
            {"date": "2024-12-31", "type": "CashFlowsFromOperatingActivities", "value": 70000000000},
            {"date": "2024-12-31", "type": "PropertyAndPlantAndEquipment", "value": -16000000000},
            {"date": "2024-12-31", "type": "InterestExpense", "value": 500000000},
            {"date": "2025-12-31", "type": "CashFlowsFromOperatingActivities", "value": 80000000000},
            {"date": "2025-12-31", "type": "PropertyAndPlantAndEquipment", "value": -18000000000},
            {"date": "2025-12-31", "type": "InterestExpense", "value": 600000000},
        ]
        lr_raw = [
            {"date": "2025-03-31", "type": "TAX", "value": 2000000000},
            {"date": "2025-03-31", "type": "PreTaxIncome", "value": 15000000000},
            {"date": "2025-06-30", "type": "TAX", "value": 2000000000},
            {"date": "2025-06-30", "type": "PreTaxIncome", "value": 16000000000},
            {"date": "2025-09-30", "type": "TAX", "value": 2000000000},
            {"date": "2025-09-30", "type": "PreTaxIncome", "value": 17000000000},
            {"date": "2025-12-31", "type": "TAX", "value": 2000000000},
            {"date": "2025-12-31", "type": "PreTaxIncome", "value": 18000000000},
        ]

        def palsu_keu(kode, jenis):
            if jenis == "neraca":
                return neraca_raw, {"status": "ok"}
            if jenis == "arus":
                return cfo_raw, {"status": "ok"}
            if jenis == "lr":
                return lr_raw, {"status": "ok"}
            return [], {}

        with patch("app.pasar.profil", return_value=profil_mock), \
             patch("app.pasar.harga", return_value=harga_mock), \
             patch("app.pasar.keuangan_mentah", side_effect=palsu_keu), \
             patch("app.harga_resmi.punya_cache_lengkap", return_value=False):
            t0 = time.monotonic()
            d = valuasi_otomatis.bangun("2454", lewati_beta_latar=True)
            durasi = time.monotonic() - t0

            self.assertLess(durasi, 1.0)
            self.assertTrue(d.get("beta_sementara"))
            self.assertTrue(d.get("beta_cadangan"))
            self.assertEqual(d["wacc_inputs"]["beta"], 1.0)
            self.assertTrue(d["wacc_inputs"]["beta_sementara"])
            self.assertIn("beta 1.0 sementara", d["sources"]["beta"])

    def test_thread_latar_dipanggil_sekali_dua_permintaan_beruntun(self):
        """Dua permintaan berurutan untuk kode yang sama tidak memicu dua thread terpisah."""
        kunci = "2454_uji"
        with valuasi_otomatis._kunci_thread_beta:
            valuasi_otomatis._thread_aktif.pop(kunci, None)

        mulai_event = threading.Event()
        lanjut_event = threading.Event()

        def kerja_dummy(kode, bursa):
            mulai_event.set()
            lanjut_event.wait(timeout=2.0)

        with patch("app.valuasi_otomatis._pekerja_beta_latar", side_effect=kerja_dummy):
            t1 = valuasi_otomatis.pemicu_hitung_beta_latar(kunci, "TWSE")
            self.assertIsNotNone(t1)
            mulai_event.wait(timeout=1.0)

            t2 = valuasi_otomatis.pemicu_hitung_beta_latar(kunci, "TWSE")
            self.assertIs(t1, t2)
            lanjut_event.set()
            t1.join(timeout=1.0)

    def test_307_diulang_lalu_berhasil(self):
        """HTTP 307 dicoba ulang dengan jeda dan berhasil bila respons kemudian sukses."""
        resp_sukses = MagicMock()
        resp_sukses.read.return_value = b'{"stat": "OK", "data": [["113/01/02", "100", "100", "100", "100", "100", "100"]]}'
        resp_sukses.__enter__.return_value = resp_sukses
        resp_sukses.__exit__.return_value = False

        err_307 = urllib.error.HTTPError("http://test", 307, "Temporary Redirect", {}, io.BytesIO(b""))

        calls = [err_307, err_307, resp_sukses]

        def side_effect(*args, **kwargs):
            res = calls.pop(0)
            if isinstance(res, Exception):
                raise res
            return res

        tidur_list = []
        with patch("urllib.request.urlopen", side_effect=side_effect), \
             patch("time.sleep", side_effect=lambda s: tidur_list.append(s)):
            data = harga_resmi._ambil_json("http://test")
            self.assertIsNotNone(data)
            self.assertEqual(data.get("stat"), "OK")
            self.assertIn(5, tidur_list)
            self.assertIn(10, tidur_list)

    def test_307_tiga_kali_kembalikan_none(self):
        """HTTP 307 gagal 3 kali berturut-turut berakhir mengembalikan None."""
        err_307 = urllib.error.HTTPError("http://test", 307, "Temporary Redirect", {}, io.BytesIO(b""))

        tidur_list = []
        with patch("urllib.request.urlopen", side_effect=err_307), \
             patch("time.sleep", side_effect=lambda s: tidur_list.append(s)):
            data = harga_resmi._ambil_json("http://test")
            self.assertIsNone(data)
            self.assertIn(5, tidur_list)
            self.assertIn(10, tidur_list)
            self.assertIn(20, tidur_list)

    def test_pita_tampil_tiga_bahasa(self):
        """Pita pemberitahuan beta sementara tersedia dalam English, 繁體中文, dan Bahasa Indonesia."""
        en = i18n.t("va.beta_sementara_pita", "en")
        zh = i18n.t("va.beta_sementara_pita", "zh")
        id_ = i18n.t("va.beta_sementara_pita", "id")

        self.assertIn("Beta is being calculated", en)
        self.assertIn("Beta 正從官方每日收盤價計算中", zh)
        self.assertIn("Beta sedang dihitung dari harga resmi", id_)

        client = TestClient(app)
        d_sementara = {
            "code": "2454",
            "name": "MediaTek",
            "bursa": "TWSE",
            "unit": "juta NTD",
            "as_of": "2026-04-10",
            "otomatis": True,
            "beta_sementara": True,
            "beta_cadangan": True,
            "market": {"price_per_share": 1200.0, "shares_issued_thousands": 1600000},
            "balance_sheet": {
                "as_of": "2025-12-31",
                "cash_and_equivalents": 50000.0,
                "short_term_investments": 0.0,
                "short_term_borrowings": 0.0,
                "current_portion_lt_debt": 2000.0,
                "current_portion_leases": 0.0,
                "long_term_debt": 10000.0,
            },
            "cash_flow": {
                "cfo_by_year": {"2023": 60000.0, "2024": 70000.0, "2025": 80000.0},
                "capex_by_year": {"2023": 15000.0, "2024": 16000.0, "2025": 18000.0},
                "interest_expense_by_year": {"2023": 500.0, "2024": 500.0, "2025": 600.0},
            },
            "tax": {"income_tax_expense": 8000.0, "pretax_income": 66000.0},
            "wacc_inputs": {
                "risk_free_rate": 0.0194,
                "beta": 1.0,
                "beta_sementara": True,
                "beta_cadangan": True,
                "equity_risk_premium": 0.0501,
                "total_interest_expense": 600.0,
            },
            "assumptions": {"terminal_growth_ceiling": 0.035},
            "sources": {"beta": "beta 1.0 sementara"},
        }

        with patch("app.store.muat_valuasi", return_value=d_sementara), \
             patch("app.valuasi_otomatis.baca_cache", return_value=d_sementara), \
             patch("app.pasar.harga", return_value={"tutup": 1200.0, "ubah": 0.0, "ubah_pct": 0.0, "nama": "MediaTek"}):
            # Test bahasa Indonesia
            resp_id = client.get("/saham/2454?tab=valuasi", cookies={"bahasa": "id"})
            self.assertEqual(resp_id.status_code, 200)
            self.assertIn("Beta sedang dihitung dari harga resmi", resp_id.text)

            # Test bahasa Inggris
            resp_en = client.get("/saham/2454?tab=valuasi", cookies={"bahasa": "en"})
            self.assertEqual(resp_en.status_code, 200)
            self.assertIn("Beta is being calculated from official daily prices", resp_en.text)

            # Test bahasa Mandarin
            resp_zh = client.get("/saham/2454?tab=valuasi", cookies={"bahasa": "zh"})
            self.assertEqual(resp_zh.status_code, 200)
            self.assertIn("Beta 正從官方每日收盤價計算中", resp_zh.text)

    def test_tidak_ada_thread_kedua_untuk_kode_sama(self):
        """Memverifikasi bahwa pemicu_hitung_beta_latar tidak membuat thread kedua jika sudah ada thread berjalan."""
        kunci = "KODE_UJI_UNIK"
        thread_palsu = MagicMock()
        thread_palsu.is_alive.return_value = True

        with valuasi_otomatis._kunci_thread_beta:
            valuasi_otomatis._thread_aktif[kunci] = thread_palsu

        try:
            hasil = valuasi_otomatis.pemicu_hitung_beta_latar(kunci, "TWSE")
            self.assertIs(hasil, thread_palsu)
            self.assertEqual(len([k for k in valuasi_otomatis._thread_aktif if k == kunci]), 1)
        finally:
            with valuasi_otomatis._kunci_thread_beta:
                valuasi_otomatis._thread_aktif.pop(kunci, None)


if __name__ == "__main__":
    unittest.main()
