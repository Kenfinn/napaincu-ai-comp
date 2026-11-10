"""Tes unit untuk tugas Putaran 2 (R1, R2, R3, D-a, D-c, D-b, B3, R4).

Seluruh tes berjalan tanpa akses jaringan luar.
"""

from __future__ import annotations

import copy
import html
import json
import random
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from app import config, harga_resmi, i18n, main, pasar, valuasi_otomatis

DATA_TES = Path(__file__).resolve().parent / "data"
HARGA_RESMI_SAMPEL = json.loads((DATA_TES / "harga_resmi_sampel.json").read_text(encoding="utf-8"))


class TestR1BetaHargaResmi(unittest.TestCase):
    """Pemeriksa untuk item R1: beta dari harga harian resmi TWSE/TPEx."""

    def test_r1_urai_twse_tpex_taiex(self):
        """Urai sampel tiga sumber: tanggal ISO benar, close float, koma dibuang."""
        # 1. TWSE STOCK_DAY (2330)
        mentah_twse = HARGA_RESMI_SAMPEL["twse_2330"]["202408"]
        hasil_twse = harga_resmi.urai_twse(mentah_twse)
        self.assertGreater(len(hasil_twse), 0)
        self.assertEqual(hasil_twse[0], ("2024-08-01", 960.0))
        for iso, close in hasil_twse:
            self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}$", iso), f"Format tanggal bukan ISO: {iso}")
            self.assertIsInstance(close, float)
            self.assertGreater(close, 0.0)

        # 2. TAIEX MI_5MINS_HIST
        mentah_taiex = HARGA_RESMI_SAMPEL["taiex"]["202408"]
        hasil_taiex = harga_resmi.urai_taiex(mentah_taiex)
        self.assertGreater(len(hasil_taiex), 0)
        self.assertEqual(hasil_taiex[0], ("2024-08-01", 22642.1))
        for iso, close in hasil_taiex:
            self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}$", iso), f"Format tanggal bukan ISO: {iso}")
            self.assertIsInstance(close, float)
            self.assertGreater(close, 0.0)

        # 3. TPEx tradingStock (6488)
        mentah_tpex = HARGA_RESMI_SAMPEL["tpex_6488"]["202408"]
        hasil_tpex = harga_resmi.urai_tpex(mentah_tpex)
        self.assertGreater(len(hasil_tpex), 0)
        self.assertEqual(hasil_tpex[0], ("2024-08-01", 512.0))
        for iso, close in hasil_tpex:
            self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}$", iso), f"Format tanggal bukan ISO: {iso}")
            self.assertIsInstance(close, float)
            self.assertGreater(close, 0.0)

    def test_r1_beta_dari_deret_buatan(self):
        """Deret indeks acak (seed tetap) dan saham = 1,5 × return indeks menghasilkan beta 1,50 ± 0,01."""
        rng = random.Random(42)
        pekan_list = [f"2024-W{i:02d}" for i in range(1, 55)]
        ret_m = {p: rng.uniform(-0.04, 0.04) for p in pekan_list}
        ret_s = {p: 1.5 * ret_m[p] for p in pekan_list}

        info = valuasi_otomatis.hitung_beta_dari_return(
            ret_s, ret_m, simbol="UJI", url_saham="http://contoh/saham", url_indeks="http://contoh/indeks"
        )
        self.assertFalse(info["beta_cadangan"])
        self.assertEqual(info["jumlah_pekan"], len(pekan_list))
        self.assertAlmostEqual(info["beta"], 1.50, delta=0.01)

    def test_r1_beta_cadangan_bila_kurang_52_minggu(self):
        """30 minggu return mingguan menghasilkan beta cadangan 1,0."""
        rng = random.Random(123)
        pekan_list = [f"2024-W{i:02d}" for i in range(1, 31)]
        ret_m = {p: rng.uniform(-0.03, 0.03) for p in pekan_list}
        ret_s = {p: 1.2 * ret_m[p] for p in pekan_list}

        info = valuasi_otomatis.hitung_beta_dari_return(
            ret_s, ret_m, simbol="PENDEK", url_saham="http://contoh/saham", url_indeks="http://contoh/indeks"
        )
        self.assertTrue(info["beta_cadangan"])
        self.assertEqual(info["beta"], 1.0)
        self.assertEqual(info["jumlah_pekan"], 30)
        self.assertEqual(info["alasan_i18n"]["kode"], "va.beta.kurang_data")

    def test_r1_cache_bulan_lalu_tidak_diambil_ulang(self):
        """Panggil harga_resmi.harian dua kali, fungsi ambil jaringan hanya terpanggil sekali untuk bulan lalu."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(config, "DATA_DIR", tmpdir):
                with mock.patch.object(harga_resmi, "_ambil_json") as mock_ambil:
                    mock_ambil.return_value = HARGA_RESMI_SAMPEL["twse_2330"]["202408"]
                    # Panggilan pertama: cache miss -> panggil _ambil_json
                    res1 = harga_resmi.harian("2330", "TWSE", "202408")
                    self.assertEqual(mock_ambil.call_count, 1)
                    self.assertGreater(len(res1), 0)

                    # Panggilan kedua: cache hit -> tidak memanggil _ambil_json lagi
                    res2 = harga_resmi.harian("2330", "TWSE", "202408")
                    self.assertEqual(mock_ambil.call_count, 1)
                    self.assertEqual(res1, res2)

    def test_r1_tanpa_yahoo(self):
        """Seluruh kode di app/ dan scripts/ tidak memuat 'yahoo' (huruf kecil)."""
        root = Path(config.ROOT)
        pelanggaran = []
        for folder in ("app", "scripts"):
            dir_target = root / folder
            for p in dir_target.rglob("*.py"):
                teks = p.read_text(encoding="utf-8")
                if "yahoo" in teks.lower():
                    pelanggaran.append(str(p.relative_to(root)))
        self.assertEqual(
            pelanggaran,
            [],
            f"Ketergantungan/kata 'yahoo' masih ditemukan di berkas: {pelanggaran}",
        )


class TestR2Penafian(unittest.TestCase):
    """Pemeriksa untuk item R2: penafian di semua halaman analisis."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.pasar_cache = self.tmp_path / "pasar"
        self.pasar_cache.mkdir(parents=True, exist_ok=True)
        self.val_dir = self.tmp_path / "valuation"
        self.val_dir.mkdir(parents=True, exist_ok=True)
        self.trace_dir = self.tmp_path / "traces"
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_dir = self.tmp_path / "parsed"
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

        # Salin manual 2330
        manual = json.loads((Path(config.VALUATION_DIR) / "2330.json").read_text(encoding="utf-8"))
        (self.val_dir / "2330.json").write_text(json.dumps(manual), encoding="utf-8")

        self._patches = [
            mock.patch.object(pasar, "CACHE_DIR", str(self.pasar_cache)),
            mock.patch.object(config, "VALUATION_DIR", str(self.val_dir)),
            mock.patch.object(config, "TRACE_DIR", str(self.trace_dir)),
            mock.patch.object(config, "PARSED_DIR", str(self.parsed_dir)),
            mock.patch.object(pasar, "_ambil_json", side_effect=AssertionError("tanpa jaringan")),
            mock.patch.object(pasar, "_finmind", side_effect=AssertionError("tanpa jaringan")),
            mock.patch.object(harga_resmi, "_ambil_json", side_effect=AssertionError("tanpa jaringan")),
        ]
        for p in self._patches:
            p.start()

        pasar_sampel = json.loads((DATA_TES / "pasar_sampel.json").read_text(encoding="utf-8"))
        for k, v in pasar_sampel.items():
            pasar._tulis_cache(k, copy.deepcopy(v))

        main._cache = None
        self.c = TestClient(main.app)

    def tearDown(self):
        main._cache = None
        for p in reversed(self._patches):
            p.stop()
        self._tmp.cleanup()

    def test_r2_penafian_di_semua_halaman_analisis(self):
        """Untuk lang en, zh, id: /, /peringatan/{id}, /saham/2330?tab=X (semua tab), /valuasi/2330 memuat penafian tepat 1x tanpa '⟦'."""
        daftar = main.hasil()
        self.assertGreater(len(daftar), 0)
        id_pertama = daftar[0]["id"]

        urls = [
            "/",
            f"/peringatan/{id_pertama}",
            "/saham/2330?tab=ringkasan",
            "/saham/2330?tab=stream",
            "/saham/2330?tab=stats",
            "/saham/2330?tab=keu",
            "/saham/2330?tab=valuasi",
            "/saham/2330?tab=profil",
            "/valuasi/2330",
        ]

        for lang in ("en", "zh", "id"):
            teks_penafian = i18n.t("rk.disclaimer", lang)
            for u in urls:
                sep = "&" if "?" in u else "?"
                target = f"{u}{sep}lang={lang}"
                resp = self.c.get(target)
                self.assertEqual(resp.status_code, 200, f"Status bukan 200 untuk {target}")
                unescaped = html.unescape(resp.text)
                cnt = unescaped.count(teks_penafian)
                self.assertEqual(cnt, 1, f"Penafian tidak muncul tepat 1x (muncul {cnt}x) di {target}")
                self.assertNotIn("⟦", resp.text, f"Ada string tak terterjemahkan di {target}")

    def test_r2_tanpa_kata_kesesuaian(self):
        """Teks rk.p.hati dan rk.p.aman ketiga bahasa tidak memuat kata penilaian kesesuaian."""
        kata_terlarang = ("aman", "safe", "安全", "cocok", "suitable", "適合")
        for k in ("rk.p.hati", "rk.p.aman"):
            for lang in ("en", "zh", "id"):
                teks = i18n.t(k, lang).lower()
                for kt in kata_terlarang:
                    self.assertNotIn(
                        kt.lower(),
                        teks,
                        f"Kata terlarang '{kt}' ditemukan di kunci '{k}' bahasa '{lang}': {teks}",
                    )


class TestR3KunciBaca(unittest.TestCase):
    """Pemeriksa untuk item R3: kunci akses untuk halaman baca."""

    def setUp(self):
        self._asli_kunci_baca = config.KUNCI_BACA
        self._asli_kode_akses = config.KODE_AKSES

    def tearDown(self):
        config.KUNCI_BACA = self._asli_kunci_baca
        config.KODE_AKSES = self._asli_kode_akses

    def test_r3_mati_secara_bawaan(self):
        """Tanpa setelan KUNCI_BACA, GET / menghasilkan 200."""
        config.KUNCI_BACA = False
        config.KODE_AKSES = ""
        c = TestClient(main.app)
        r = c.get("/")
        self.assertEqual(r.status_code, 200)

    def test_r3_terkunci_tanpa_kode(self):
        """KUNCI_BACA aktif + KODE_AKSES 'uji': / 401 & form, /api/* 401 JSON, /docs 401, /sehat 200, /static/* 200."""
        config.KUNCI_BACA = True
        config.KODE_AKSES = "uji"
        c = TestClient(main.app)

        # GET / -> 401 dan memuat form kode
        r_feed = c.get("/")
        self.assertEqual(r_feed.status_code, 401)
        self.assertIn("<form", r_feed.text)
        self.assertIn('name="kode"', r_feed.text)

        # GET /api/peringatan -> 401 JSON
        r_api = c.get("/api/peringatan")
        self.assertEqual(r_api.status_code, 401)
        self.assertEqual(r_api.json(), {"galat": "perlu kode akses"})

        # GET /docs -> 401
        r_docs = c.get("/docs")
        self.assertEqual(r_docs.status_code, 401)

        # GET /sehat -> 200
        r_sehat = c.get("/sehat")
        self.assertEqual(r_sehat.status_code, 200)

        # GET /static/app.css -> 200
        r_css = c.get("/static/app.css")
        self.assertEqual(r_css.status_code, 200)

    def test_r3_terbuka_dengan_kode(self):
        """GET /akses?kode=uji lalu GET / menghasilkan 200."""
        config.KUNCI_BACA = True
        config.KODE_AKSES = "uji"
        c = TestClient(main.app)

        r_akses = c.get("/akses?kode=uji")
        self.assertEqual(r_akses.status_code, 200)

        r_feed = c.get("/")
        self.assertEqual(r_feed.status_code, 200)

    def test_r3_abaikan_bila_kode_kosong(self):
        """KUNCI_BACA aktif + KODE_AKSES '' menghasilkan GET / 200 (diabaikan karena kode kosong)."""
        config.KUNCI_BACA = True
        config.KODE_AKSES = ""
        c = TestClient(main.app)
        r = c.get("/")
        self.assertEqual(r.status_code, 200)

    def test_r3_halaman_kunci_tiga_bahasa(self):
        """/?lang=zh, /?lang=en, /?lang=id saat terkunci menghasilkan 401 dan tidak ada penanda tak terterjemahkan '⟦'."""
        config.KUNCI_BACA = True
        config.KODE_AKSES = "uji"
        c = TestClient(main.app)

        for lang in ("en", "zh", "id"):
            r = c.get(f"/?lang={lang}")
            self.assertEqual(r.status_code, 401)
            self.assertNotIn("⟦", r.text, f"Penanda tak terterjemahkan ditemukan di bahasa {lang}")


