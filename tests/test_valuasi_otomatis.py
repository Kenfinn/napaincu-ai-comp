"""Tes unit pembangun DCF otomatis (Tugas B2) — seluruhnya berjalan tanpa jaringan."""

from __future__ import annotations

import calendar
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from app import config, harga_resmi, i18n, main, pasar, store, valuasi_otomatis
from app.agent import pipeline
from scripts import dcf

DATA_TES = Path(__file__).resolve().parent / "data"
PASAR_SAMPEL = json.loads((DATA_TES / "pasar_sampel.json").read_text(encoding="utf-8"))
HARGA_RESMI_SAMPEL = json.loads((DATA_TES / "harga_resmi_sampel.json").read_text(encoding="utf-8"))
MANUAL_2330 = json.loads((Path(config.VALUATION_DIR) / "2330.json").read_text(encoding="utf-8"))


class _LingkunganOfflineMixin:
    """Arahkan semua direktori cache & jejak ke folder sementara dan blokir jaringan."""

    def setUp(self) -> None:
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

        self.pasar_cache = self.tmp_path / "pasar"
        self.pasar_cache.mkdir(parents=True, exist_ok=True)
        self.va_cache = self.tmp_path / "valuasi_otomatis"
        self.va_cache.mkdir(parents=True, exist_ok=True)
        self.val_dir = self.tmp_path / "valuation_inputs"
        self.val_dir.mkdir(parents=True, exist_ok=True)
        self.trace_dir = self.tmp_path / "traces"
        self.trace_dir.mkdir(parents=True, exist_ok=True)

        # Tulis sampel 2330 manual ke folder valuation sementara
        (self.val_dir / "2330.json").write_text(
            json.dumps(MANUAL_2330, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.parsed_dir = self.tmp_path / "parsed"
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self._patches = [
            mock.patch.object(pasar, "CACHE_DIR", str(self.pasar_cache)),
            mock.patch.object(valuasi_otomatis, "CACHE_DIR", self.va_cache),
            mock.patch.object(config, "VALUATION_DIR", str(self.val_dir)),
            mock.patch.object(config, "TRACE_DIR", str(self.trace_dir)),
            mock.patch.object(config, "PARSED_DIR", str(self.parsed_dir)),
            mock.patch.object(
                pasar,
                "_ambil_json",
                side_effect=AssertionError("Tes tidak boleh memanggil jaringan (_ambil_json)"),
            ),
            mock.patch.object(
                pasar,
                "_finmind",
                side_effect=AssertionError("Tes tidak boleh memanggil jaringan (_finmind)"),
            ),
            mock.patch.object(
                harga_resmi,
                "_ambil_json",
                side_effect=AssertionError("Tes tidak boleh memanggil jaringan (_ambil_json harga_resmi)"),
            ),
            mock.patch.object(
                harga_resmi,
                "harian",
                side_effect=self._mock_harian,
            ),
            mock.patch.object(
                harga_resmi,
                "taiex",
                side_effect=self._mock_taiex,
            ),
        ]
        for p in self._patches:
            p.start()
        main._cache = None

        # Tulis sampel pasar & FinMind ke cache sementara memakai format pasar._tulis_cache
        for kunci, isi in PASAR_SAMPEL.items():
            pasar._tulis_cache(kunci, copy.deepcopy(isi))
        # Tambahkan emiten keuangan 2881 ke profil_twse sampel untuk uji sektor keuangan
        prof_twse = copy.deepcopy(PASAR_SAMPEL["profil_twse"])
        prof_twse.append({
            "公司代號": "2881",
            "公司名稱": "富邦金融控股股份有限公司",
            "公司簡稱": "富邦金",
            "英文簡稱": "Fubon Financial",
            "產業別": "17",
            "成立日期": "20011219",
            "上市日期": "20011219",
            "實收資本額": "146149000000",
            "已發行普通股數或TDR原股發行股數": "13000000000",
        })
        pasar._tulis_cache("profil_twse", prof_twse)

    def tearDown(self) -> None:
        main._cache = None
        for p in reversed(self._patches):
            p.stop()
        self._tmp.cleanup()
        super().tearDown()

    def _mock_harian(self, kode: str, bursa: str = "", bulan: str = "") -> list[tuple[str, float]]:
        sample_months = ["202408", "202409", "202410"]
        src_bln = sample_months[int(bulan) % 3] if str(bulan).isdigit() else "202408"
        bursa_norm = (bursa or "TWSE").upper()
        key = "tpex_6488" if bursa_norm == "TPEX" or str(kode) == "6488" else "twse_2330"
        raw = HARGA_RESMI_SAMPEL[key][src_bln]
        parsed = harga_resmi.urai_tpex(raw) if key == "tpex_6488" else harga_resmi.urai_twse(raw)
        out = []
        th, bl = int(bulan[:4]), int(bulan[4:])
        max_d = calendar.monthrange(th, bl)[1]
        for iso, val in parsed:
            day = min(int(iso.split("-")[2]), max_d)
            new_iso = f"{th:04d}-{bl:02d}-{day:02d}"
            scale = 1.0 + 0.003 * ((int(bulan) % 7) - 3)
            out.append((new_iso, round(val * scale, 2)))
        return out

    def _mock_taiex(self, bulan: str = "") -> list[tuple[str, float]]:
        sample_months = ["202408", "202409", "202410"]
        src_bln = sample_months[int(bulan) % 3] if str(bulan).isdigit() else "202408"
        raw = HARGA_RESMI_SAMPEL["taiex"][src_bln]
        parsed = harga_resmi.urai_taiex(raw)
        out = []
        th, bl = int(bulan[:4]), int(bulan[4:])
        max_d = calendar.monthrange(th, bl)[1]
        for iso, val in parsed:
            day = min(int(iso.split("-")[2]), max_d)
            new_iso = f"{th:04d}-{bl:02d}-{day:02d}"
            scale = 1.0 + 0.002 * ((int(bulan) % 5) - 2)
            out.append((new_iso, round(val * scale, 2)))
        return out

    def _salin_keuangan_sampel(self, kode_target: str) -> None:
        """Salin laporan FinMind 2330 ke `kode_target` di cache sementara."""
        for jenis in ("neraca", "arus", "lr"):
            data_2330, _ = pasar._baca_cache(f"finmind_{jenis}_2330")
            pasar._tulis_cache(f"finmind_{jenis}_{kode_target}", copy.deepcopy(data_2330))


class TestValuasiOtomatis(_LingkunganOfflineMixin, unittest.TestCase):
    """Uji unit pembangun DCF otomatis (Tugas B2)."""

    def test_pemetaan_field_2330_identik_dengan_manual(self):
        """Neraca dan arus kas 2025 dari sampel FinMind 2330 cocok (<1% selisih) dengan berkas manual."""
        d = valuasi_otomatis.bangun("2330")
        self.assertTrue(d["otomatis"])
        self.assertFalse(d["tidak_berlaku"])
        self.assertFalse(d["tidak_bisa_dihitung"])
        self.assertEqual(d["fiscal_year"], 2025)

        bs_o = d["balance_sheet"]
        bs_m = MANUAL_2330["balance_sheet"]
        self.assertAlmostEqual(bs_o["cash_and_equivalents"], 2767856.4, places=1)
        self.assertAlmostEqual(bs_o["cash_and_equivalents"], bs_m["cash_and_equivalents"], places=1)
        self.assertAlmostEqual(bs_o["short_term_investments"], 300638.2, places=1)
        self.assertAlmostEqual(bs_o["short_term_investments"], bs_m["short_term_investments"], places=1)
        self.assertAlmostEqual(bs_o["long_term_debt"], 896062.0, places=1)
        self.assertAlmostEqual(bs_o["long_term_debt"], bs_m["long_term_debt"], places=1)

        cf_o = d["cash_flow"]
        cf_m = MANUAL_2330["cash_flow"]
        # Selisih CFO 2025 & Capex 2025 terhadap manual harus < 1%
        selisih_cfo_2025 = abs(cf_o["cfo_by_year"]["2025"] - cf_m["cfo_by_year"]["2025"]) / cf_m["cfo_by_year"]["2025"]
        selisih_capex_2025 = abs(cf_o["capex_by_year"]["2025"] - cf_m["capex_by_year"]["2025"]) / cf_m["capex_by_year"]["2025"]
        selisih_bunga_2025 = abs(cf_o["interest_expense_by_year"]["2025"] - cf_m["interest_expense_by_year"]["2025"]) / cf_m["interest_expense_by_year"]["2025"]
        self.assertLess(selisih_cfo_2025, 0.01)
        self.assertLess(selisih_capex_2025, 0.01)
        self.assertLess(selisih_bunga_2025, 0.01)

        # Pastikan dcf.compute(d) berjalan mulus dan FCFF 2025 selisih < 1%
        r_o = dcf.compute(d, forward_g=d["assumptions"]["terminal_growth_ceiling"])
        r_m = dcf.compute(MANUAL_2330, forward_g=MANUAL_2330["assumptions"]["terminal_growth_ceiling"])
        selisih_fcff0 = abs(r_o["fcff0"] - r_m["fcff0"]) / r_m["fcff0"]
        self.assertLess(selisih_fcff0, 0.01)
        self.assertEqual(r_o["incomplete_sources"], [])

    def test_perhitungan_beta_dari_sampel_deret_harga(self):
        """hitung_beta menghitung cov(rs, rm) / var(rm) dengan tepat dari deret harga resmi."""
        info = valuasi_otomatis.hitung_beta("2330", bursa="TWSE")
        self.assertFalse(info["beta_cadangan"])
        self.assertGreaterEqual(info["jumlah_pekan"], 52)
        self.assertIn("2330", info["simbol"])
        self.assertGreater(info["beta"], 0.5)
        self.assertLess(info["beta"], 3.0)

        # Emiten TPEx memakai pasar TPEx
        info_tpex = valuasi_otomatis.hitung_beta("6488", bursa="TPEx")
        self.assertIn("6488", info_tpex["simbol"])
        self.assertFalse(info_tpex["beta_cadangan"])

    def test_beta_cadangan_bila_kurang_52_minggu_atau_gagal(self):
        """Kurang dari 52 pasangan minggu atau gagal ambil → beta 1,0 dan beta_cadangan=True."""
        daftar_2bln = ["202408", "202409"]
        with mock.patch.object(
            valuasi_otomatis,
            "_daftar_25_bulan",
            return_value=daftar_2bln,
        ):
            info_pendek = valuasi_otomatis.hitung_beta("2454", bursa="TWSE")
            self.assertTrue(info_pendek["beta_cadangan"])
            self.assertEqual(info_pendek["beta"], 1.0)
            self.assertEqual(info_pendek["alasan_i18n"]["kode"], "va.beta.kurang_data")

        with mock.patch.object(
            harga_resmi,
            "harian",
            return_value=[],
        ):
            info_gagal = valuasi_otomatis.hitung_beta("2317", bursa="TWSE")
            self.assertTrue(info_gagal["beta_cadangan"])
            self.assertEqual(info_gagal["beta"], 1.0)
            self.assertEqual(info_gagal["alasan_i18n"]["kode"], "va.beta.gagal_ambil")

    def test_emiten_keuangan_ditandai_tidak_berlaku(self):
        """Emiten keuangan (mis. 2881 Fubon Financial, industri 17) ditandai tidak_berlaku tanpa angka DCF."""
        d = valuasi_otomatis.bangun("2881")
        self.assertTrue(d["otomatis"])
        self.assertTrue(d["tidak_berlaku"])
        self.assertFalse(d.get("tidak_bisa_dihitung"))
        self.assertNotIn("market", d)
        self.assertEqual(d["alasan_i18n"]["kode"], "va.otomatis.keuangan")

        valuasi_otomatis.simpan_cache("2881", d)
        # Pipeline harus menerima None dari store.muat_valuasi untuk emiten tidak_berlaku
        self.assertIsNone(store.muat_valuasi("2881"))

    def test_fcff_negatif_tidak_menghasilkan_angka_palsu(self):
        """Bila FCFF tahun terakhir <= 0, kembalikan tidak_bisa_dihitung dengan alasan jelas."""
        self._salin_keuangan_sampel("2454")
        arus_data, _ = pasar._baca_cache("finmind_arus_2454")
        for b in arus_data:
            if b.get("date") == "2025-12-31" and b.get("type") == "CashFlowsFromOperatingActivities":
                b["value"] = -500_000_000_000  # CFO negatif besar sehingga FCFF0 < 0
        pasar._tulis_cache("finmind_arus_2454", arus_data)

        d = valuasi_otomatis.bangun("2454")
        self.assertTrue(d["otomatis"])
        self.assertFalse(d["tidak_berlaku"])
        self.assertTrue(d["tidak_bisa_dihitung"])
        self.assertNotIn("market", d)
        self.assertEqual(d["alasan_i18n"]["kode"], "va.otomatis.fcff_negatif")

        valuasi_otomatis.simpan_cache("2454", d)
        self.assertIsNone(store.muat_valuasi("2454"))

    def test_kurang_dari_3_tahun_tidak_bisa_dihitung(self):
        """Kurang dari 3 tahun fiskal penuh di laporan arus kas → tidak_bisa_dihitung."""
        self._salin_keuangan_sampel("2454")
        arus_data, _ = pasar._baca_cache("finmind_arus_2454")
        arus_2th = [b for b in arus_data if not str(b.get("date", "")).startswith("2023-")]
        pasar._tulis_cache("finmind_arus_2454", arus_2th)

        d = valuasi_otomatis.bangun("2454")
        self.assertTrue(d["tidak_bisa_dihitung"])
        self.assertEqual(d["alasan_i18n"]["kode"], "va.otomatis.kurang_3_tahun")

    def test_berkas_manual_selalu_menang_dan_store_tanpa_jaringan(self):
        """store.muat_valuasi memadukan otomatis + asumsi manual bila ada cache, manual murni bila tanpa cache, dan tidak pernah memanggil bangun()."""
        oto_2330 = valuasi_otomatis.bangun("2330")
        valuasi_otomatis.simpan_cache("2330", oto_2330)

        # Ada cache + ada manual → otomatis dengan asumsi manual (D-b)
        hasil_2330 = store.muat_valuasi("2330")
        self.assertIsNotNone(hasil_2330)
        self.assertEqual(hasil_2330.get("asumsi_dari"), "manual")
        self.assertEqual(hasil_2330["assumptions"]["terminal_growth_ceiling"], MANUAL_2330["assumptions"]["terminal_growth_ceiling"])

        # Tanpa cache otomatis → berkas manual apa adanya
        with tempfile.TemporaryDirectory() as tmp_kosong:
            asli = valuasi_otomatis.CACHE_DIR
            try:
                valuasi_otomatis.CACHE_DIR = Path(tmp_kosong)
                murni = store.muat_valuasi("2330")
                self.assertIsNotNone(murni)
                self.assertFalse(murni.get("otomatis", False))
                self.assertEqual(murni["market"]["price_per_share"], MANUAL_2330["market"]["price_per_share"])
            finally:
                valuasi_otomatis.CACHE_DIR = asli

        # Untuk emiten yang belum ada di cache otomatis, store.muat_valuasi harus mengembalikan None
        # tanpa memanggil valuasi_otomatis.bangun
        with mock.patch.object(
            valuasi_otomatis,
            "bangun",
            side_effect=AssertionError("store.muat_valuasi tidak boleh memanggil bangun()"),
        ):
            self.assertIsNone(store.muat_valuasi("2454"))

    def test_pengumuman_emiten_non_2330_sampai_ke_verified(self):
        """Pengumuman pasal 20 untuk emiten non-2330 dengan cache otomatis mencapai state VERIFIED."""
        self._salin_keuangan_sampel("2454")
        d_2454 = valuasi_otomatis.bangun("2454")
        self.assertTrue(valuasi_otomatis.layak_dcf(d_2454))
        valuasi_otomatis.simpan_cache("2454", d_2454)

        pengumuman_2454 = {
            "code": "2454",
            "name": "MediaTek",
            "date": "2026-11-10",
            "time": "17:30:00",
            "seq_no": "1",
            "clause": 20,
            "regulation": "第20款",
            "subject": "取得不動產、廠房及設備供營業使用",
            "spoken_at": "2026-11-10 17:30:00",
            "source_url": "https://mops.twse.com.tw/mops/web/t05st01?test=2454",
            "items": [
                {"no": 1, "label": "標的物之名稱及性質", "value": "無塵室及晶圓測試設備"},
                {"no": 2, "label": "事實發生日", "value": "115/11/10"},
                {"no": 3, "label": "交易數量、每單位價格及交易總金額", "value": "交易總金額：新台幣 500,000,000,000 元"},
                {"no": 4, "label": "交易相對人及其與公司之關係", "value": "非關係人"},
                {"no": 5, "label": "取得或處分之具體目的或用途", "value": "供研發與生產使用"},
            ],
        }
        val_2454 = store.muat_valuasi("2454")
        self.assertIsNotNone(val_2454)
        self.assertTrue(val_2454["otomatis"])

        jejak = pipeline.jalankan(pengumuman_2454, val_2454)
        states = [l["state"] for l in jejak["jejak"]]
        self.assertIn("VERIFIED · sumber", states)
        self.assertIn("VERIFIED · hitungan", states)
        self.assertEqual(jejak["state"], "PUBLISHED")
        self.assertEqual(jejak["status"], "terbit")
        self.assertEqual(len(jejak["muatan"]["diterima"]), 1)

    def test_tab_valuasi_web_tiga_bahasa(self):
        """Tab Valuation di /saham/{kode}?tab=valuasi menampilkan lencana & status dalam 3 bahasa."""
        self._salin_keuangan_sampel("2454")
        valuasi_otomatis.panaskan(["2330", "2454", "2881"], jeda=0)

        klien = TestClient(main.app)
        for bhs, label_oto, label_oto_asumsi, label_na in (
            ("en", "Automatic", "Automatic + team assumptions", "Not applicable"),
            ("zh", "自動計算", "自動＋團隊假設", "不適用"),
            ("id", "Otomatis", "Otomatis + asumsi tim", "Tidak berlaku"),
        ):
            r_man = klien.get(f"/saham/2330?tab=valuasi&lang={bhs}")
            self.assertEqual(r_man.status_code, 200)
            self.assertIn(label_oto_asumsi, r_man.text)
            self.assertNotIn("⟦", r_man.text)

            r_oto = klien.get(f"/saham/2454?tab=valuasi&lang={bhs}")
            self.assertEqual(r_oto.status_code, 200)
            self.assertIn(label_oto, r_oto.text)
            self.assertIn("FinMind", r_oto.text)
            self.assertNotIn("⟦", r_oto.text)

            r_lembar = klien.get(f"/valuasi/2454?lang={bhs}")
            self.assertEqual(r_lembar.status_code, 200)
            self.assertIn(label_oto, r_lembar.text)
            self.assertNotIn("⟦", r_lembar.text)

            r_na = klien.get(f"/saham/2881?tab=valuasi&lang={bhs}")
            self.assertEqual(r_na.status_code, 200)
            self.assertIn(label_na, r_na.text)
            self.assertNotIn("⟦", r_na.text)


if __name__ == "__main__":
    unittest.main()
