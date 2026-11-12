"""Tes unit untuk tugas Putaran 2 (R1, R2, R3, D-a, D-c, D-b, B3, R4).

Seluruh tes berjalan tanpa akses jaringan luar.
"""

from __future__ import annotations

import copy
import html
import json
import os
import random
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from app import config, harga_resmi, i18n, main, pasar, tarik, valuasi_otomatis
from app.agent import extract, llm

ROOT = Path(__file__).resolve().parent.parent
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


class TestDaSemuaEmiten(unittest.TestCase):
    """Pemeriksa untuk item D-a: proses pengumuman semua emiten."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._asli_tarik = {
            "WATCHLIST_FILE": tarik.WATCHLIST_FILE,
            "STATUS_FILE": tarik.STATUS_FILE,
            "RAW_DIR": tarik.RAW_DIR,
            "DETAIL_FILE": tarik.DETAIL_FILE,
            "LIST_FILE": tarik.LIST_FILE,
            "ambil": tarik.ambil,
        }
        for n in ("WATCHLIST_FILE", "STATUS_FILE", "RAW_DIR", "DETAIL_FILE", "LIST_FILE"):
            setattr(tarik, n, os.path.join(self.tmp.name, os.path.basename(getattr(tarik, n))))

        self._asli_config = {
            "PROSES_SEMUA": getattr(config, "PROSES_SEMUA", True),
            "API_KEY": config.API_KEY,
            "KUNCI_BACA": config.KUNCI_BACA,
            "KODE_AKSES": config.KODE_AKSES,
        }
        self._asli_llm_cache = llm.CACHE_DIR
        self._asli_tanya_model = llm._tanya_model

    def tearDown(self):
        for n, v in self._asli_tarik.items():
            setattr(tarik, n, v)
        for n, v in self._asli_config.items():
            setattr(config, n, v)
        llm.CACHE_DIR = self._asli_llm_cache
        llm._tanya_model = self._asli_tanya_model
        llm.selesai_jalan()
        self.tmp.cleanup()

    def test_da_semua_emiten_disimpan(self):
        """periksa_sekarang() tanpa argumen menyimpan semua 7 rekaman dari sampel, watchlist 1 kode, dijalankan lagi baru 0."""
        with open(os.path.join(ROOT, "tests", "data", "openapi_pasal_sampel.json"), encoding="utf-8") as f:
            sampel_7 = json.load(f)

        tarik.ambil = lambda s: sampel_7 if s == "twse" else []
        tarik.simpan_watchlist(["2420"])
        config.PROSES_SEMUA = True

        st = tarik.periksa_sekarang()
        self.assertTrue(st["ok"])
        self.assertEqual(st["disimpan"], 7)
        self.assertEqual(st["baru"], 7)
        self.assertEqual(st["cocok_watchlist"], 1)

        with open(tarik.DETAIL_FILE, encoding="utf-8") as f:
            tersimpan = json.load(f)
        self.assertEqual(len(tersimpan), 7)

        # Jalankan lagi -> baru 0
        st2 = tarik.periksa_sekarang()
        self.assertEqual(st2["baru"], 0)

    def test_da_argumen_eksplisit_tetap_watchlist(self):
        """periksa_sekarang(['2420']) hanya menyimpan rekaman dengan kode 2420."""
        with open(os.path.join(ROOT, "tests", "data", "openapi_pasal_sampel.json"), encoding="utf-8") as f:
            sampel_7 = json.load(f)

        tarik.ambil = lambda s: sampel_7 if s == "twse" else []
        config.PROSES_SEMUA = True

        st = tarik.periksa_sekarang(["2420"])
        self.assertTrue(st["ok"])
        self.assertEqual(st["disimpan"], 1)
        self.assertEqual(st["baru"], 1)

        with open(tarik.DETAIL_FILE, encoding="utf-8") as f:
            tersimpan = json.load(f)
        self.assertEqual(len(tersimpan), 1)
        self.assertEqual(tersimpan[0]["code"], "2420")

    def test_da_jatah_model(self):
        """_tanya_model dipanggil 2 kali saat jatah=2; yang ketiga turun ke aturan dengan sebab memuat 'jatah'."""
        config.API_KEY = "uji"
        llm.CACHE_DIR = os.path.join(self.tmp.name, "cache_model")
        panggilan = 0

        def tiru_tanya(instruksi, dokumen):
            nonlocal panggilan
            panggilan += 1
            return {"temuan": []}, {"token_masuk": 10, "token_keluar": 10}

        llm._tanya_model = tiru_tanya
        llm.mulai_jalan(2)

        det1 = {
            "code": "2330", "name": "TSMC", "date": "2026-09-19", "time": "14:00:00",
            "subject": "Capex 1", "clause": 11, "items": [{"no": 1, "label": "金額", "label_lengkap": "金額", "satuan_label": "", "value": "100 仟元"}],
        }
        det2 = {
            "code": "2454", "name": "Mediatek", "date": "2026-09-20", "time": "14:00:00",
            "subject": "Capex 2", "clause": 11, "items": [{"no": 1, "label": "金額", "label_lengkap": "金額", "satuan_label": "", "value": "200 仟元"}],
        }
        det3 = {
            "code": "2317", "name": "HonHai", "date": "2026-09-21", "time": "14:00:00",
            "subject": "Capex 3", "clause": 11, "items": [{"no": 1, "label": "金額", "label_lengkap": "金額", "satuan_label": "", "value": "300 仟元"}],
        }

        t1, m1 = extract.sari(det1, ["capex"])
        self.assertFalse(m1.get("cadangan"))

        t2, m2 = extract.sari(det2, ["capex"])
        self.assertFalse(m2.get("cadangan"))

        t3, m3 = extract.sari(det3, ["capex"])
        self.assertTrue(m3.get("cadangan"))
        self.assertIn("jatah", m3.get("sebab_cadangan", "").lower())
        self.assertEqual(panggilan, 2)

    def test_da_halaman_lingkup(self):
        """/?lingkup=semua dan /review?lingkup=semua -> 200 di tiga bahasa tanpa '⟦'."""
        config.KUNCI_BACA = False
        config.KODE_AKSES = ""
        c = TestClient(main.app)

        for lang in ("en", "zh", "id"):
            r_feed = c.get(f"/?lingkup=semua&lang={lang}")
            self.assertEqual(r_feed.status_code, 200, f"Gagal feed lang={lang}")
            self.assertNotIn("⟦", r_feed.text, f"Unrendered i18n di feed lang={lang}")

            r_rev = c.get(f"/review?lingkup=semua&lang={lang}")
            self.assertEqual(r_rev.status_code, 200, f"Gagal review lang={lang}")
            self.assertNotIn("⟦", r_rev.text, f"Unrendered i18n di review lang={lang}")


class TestDcUtangLancar(unittest.TestCase):
    """Pemeriksa untuk item D-c: pinjaman jangka pendek dan tanda utang lancar."""

    def test_dc_pinjaman_jangka_pendek_masuk_utang(self):
        """dcf.net_debt menghitung short_term_borrowings ke dalam utang total."""
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        if str(root / "scripts") not in sys.path:
            sys.path.insert(0, str(root / "scripts"))
        import dcf

        bs_tanpa_stb = {
            "current_portion_lt_debt": 50.0,
            "long_term_debt": 200.0,
            "cash_and_equivalents": 100.0,
            "short_term_investments": 20.0,
        }
        debt1, cash1, net1 = dcf.net_debt(bs_tanpa_stb, include_leases=False)
        self.assertEqual(debt1, 250.0)

        bs_dengan_stb = {
            "current_portion_lt_debt": 50.0,
            "long_term_debt": 200.0,
            "short_term_borrowings": 35.0,
            "cash_and_equivalents": 100.0,
            "short_term_investments": 20.0,
        }
        debt2, cash2, net2 = dcf.net_debt(bs_dengan_stb, include_leases=False)
        self.assertEqual(debt2, 285.0)
        self.assertEqual(debt2 - debt1, 35.0)

    def test_dc_tanda_tidak_tersedia(self):
        """Sampel tanpa bagian lancar -> tidak_tersedia memuat current_portion_lt_debt dan peringatan tampil di halaman 3 bahasa."""
        # 1. Uji fungsi _cari_utang_lancar_neraca langsung
        pos_kosong = {"BondsPayable": 500000.0}
        total_cp, dipakai, ada_eksplisit = valuasi_otomatis._cari_utang_lancar_neraca(pos_kosong, [])
        self.assertEqual(total_cp, 0.0)
        self.assertFalse(ada_eksplisit)

        # 2. Mock objek valuasi dengan tidak_tersedia dan peringatan
        with open(os.path.join(ROOT, "valuation", "inputs", "2330.json"), encoding="utf-8") as f:
            d_2330 = json.load(f)

        d_mock = copy.deepcopy(d_2330)
        d_mock["otomatis"] = True
        d_mock["tidak_tersedia"] = ["current_portion_lt_debt"]
        d_mock["balance_sheet"]["current_portion_lt_debt"] = 0.0
        d_mock["balance_sheet"]["short_term_borrowings"] = 0.0
        d_mock["peringatan"] = [i18n.pesan("va.warn.utang_lancar_tidak_tersedia")]

        self.assertIn("current_portion_lt_debt", d_mock["tidak_tersedia"])

        c = TestClient(main.app)
        with mock.patch("app.store.muat_valuasi", return_value=d_mock):
            with mock.patch("app.valuasi_otomatis.baca_cache", return_value=d_mock):
                for lang in ("en", "zh", "id"):
                    teks_harap = i18n.t("va.warn.utang_lancar_tidak_tersedia", lang)
                    r = c.get(f"/saham/2330?tab=valuasi&lang={lang}")
                    self.assertEqual(r.status_code, 200)
                    self.assertIn(teks_harap, r.text, f"Peringatan tidak muncul di tab valuasi lang={lang}")
                    self.assertNotIn("⟦", r.text)

                    r_val = c.get(f"/valuasi/2330?lang={lang}")
                    self.assertEqual(r_val.status_code, 200)
                    self.assertIn(teks_harap, r_val.text, f"Peringatan tidak muncul di /valuasi/2330 lang={lang}")
                    self.assertNotIn("⟦", r_val.text)


class TestDbValuasiOtomatisManual(unittest.TestCase):
    """Pemeriksa untuk item D-b: valuasi otomatis digabung asumsi manual."""

    def test_cache_skema_lama_dianggap_tidak_ada(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            asli_cache = valuasi_otomatis.CACHE_DIR
            try:
                valuasi_otomatis.CACHE_DIR = tmpdir
                with open(os.path.join(tmpdir, "2330.json"), "w", encoding="utf-8") as f:
                    json.dump({"code": "2330", "otomatis": True}, f)        # tanpa versi_skema
                self.assertIsNone(valuasi_otomatis.baca_cache("2330"))
                valuasi_otomatis.simpan_cache("2330", {"code": "2330", "otomatis": True})
                self.assertEqual(valuasi_otomatis.baca_cache("2330")["versi_skema"], valuasi_otomatis.VERSI_SKEMA)
            finally:
                valuasi_otomatis.CACHE_DIR = asli_cache

    def test_db_otomatis_menang_asumsi_manual(self):
        """Siapkan cache otomatis 2330 buatan di folder sementara -> muat_valuasi("2330") memakai cfo/capex otomatis, tetapi assumptions.terminal_growth_ceiling dan risk_free_rate dari berkas manual; asumsi_dari = "manual"."""
        import sys
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        from app import store

        with tempfile.TemporaryDirectory() as tmpdir:
            asli_cache = valuasi_otomatis.CACHE_DIR
            try:
                valuasi_otomatis.CACHE_DIR = tmpdir

                with open(os.path.join(ROOT, "valuation", "inputs", "2330.json"), encoding="utf-8") as f:
                    manual_asli = json.load(f)

                auto_palsu = {
                    "code": "2330",
                    "name": "TSMC Auto",
                    "as_of": "2026-11-10",
                    "otomatis": True,
                    "market": {
                        "price_per_share": 2200.0,
                        "shares_issued_thousands": 25932000.0,
                    },
                    "balance_sheet": {
                        "cash_and_equivalents": 2000000.0,
                        "short_term_investments": 100000.0,
                        "current_portion_lt_debt": 0.0,
                        "long_term_debt": 800000.0,
                        "short_term_borrowings": 0.0,
                    },
                    "tidak_tersedia": ["current_portion_lt_debt"],
                    "cash_flow": {
                        "cfo_by_year": {"2023": 1111111.0, "2024": 2222222.0, "2025": 3333333.0},
                        "capex_by_year": {"2023": 555555.0, "2024": 666666.0, "2025": 777777.0},
                        "interest_expense_by_year": {"2023": 10000.0, "2024": 10000.0, "2025": 10000.0},
                    },
                    "tax": {
                        "income_tax_expense": 300000.0,
                        "pretax_income": 2000000.0,
                    },
                    "wacc_inputs": {
                        "risk_free_rate": 0.05,
                        "beta": 1.10,
                        "equity_risk_premium": 0.08,
                        "total_interest_expense": 10000.0,
                    },
                    "assumptions": {
                        "include_leases_in_debt": True,
                        "terminal_growth_ceiling": 0.015,
                    },
                }
                valuasi_otomatis.simpan_cache("2330", auto_palsu)   # menulis versi_skema

                hasil = store.muat_valuasi("2330")
                self.assertIsNotNone(hasil)
                self.assertEqual(hasil.get("asumsi_dari"), "manual")
                self.assertIn("assumptions", hasil.get("ditimpa_manual", []))

                # cfo dan capex harus dari otomatis
                self.assertEqual(hasil["cash_flow"]["cfo_by_year"]["2025"], 3333333.0)
                self.assertEqual(hasil["cash_flow"]["capex_by_year"]["2025"], 777777.0)

                # Asumsi dan wacc_inputs dari manual
                self.assertEqual(
                    hasil["assumptions"]["terminal_growth_ceiling"],
                    manual_asli["assumptions"]["terminal_growth_ceiling"],
                )
                self.assertEqual(
                    hasil["wacc_inputs"]["risk_free_rate"],
                    manual_asli["wacc_inputs"]["risk_free_rate"],
                )
                self.assertEqual(
                    hasil["wacc_inputs"]["equity_risk_premium"],
                    manual_asli["wacc_inputs"]["equity_risk_premium"],
                )

                # Beta tetap dari otomatis
                self.assertEqual(hasil["wacc_inputs"]["beta"], 1.10)

                # current_portion_lt_debt yang di auto ada di tidak_tersedia diisi dari manual
                self.assertEqual(
                    hasil["balance_sheet"]["current_portion_lt_debt"],
                    manual_asli["balance_sheet"]["current_portion_lt_debt"],
                )
                self.assertNotIn("current_portion_lt_debt", hasil.get("tidak_tersedia", []))
            finally:
                valuasi_otomatis.CACHE_DIR = asli_cache

    def test_db_tanpa_cache_pakai_manual(self):
        """Tanpa cache otomatis -> muat_valuasi menghasilkan berkas manual apa adanya."""
        from app import store

        with tempfile.TemporaryDirectory() as tmpdir:
            asli_cache = valuasi_otomatis.CACHE_DIR
            try:
                valuasi_otomatis.CACHE_DIR = tmpdir
                hasil = store.muat_valuasi("2330")
                with open(os.path.join(ROOT, "valuation", "inputs", "2330.json"), encoding="utf-8") as f:
                    manual_asli = json.load(f)
                self.assertEqual(hasil, manual_asli)
                self.assertNotIn("asumsi_dari", hasil)
            finally:
                valuasi_otomatis.CACHE_DIR = asli_cache

    def test_dc_manual_mengisi_yang_kosong(self):
        """Dengan D-b, utang total 2330 = otomatis + 136.926,5 (selisih dari berkas manual < 1%)."""
        import sys
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import dcf
        from app import store

        with open(os.path.join(ROOT, "valuation", "inputs", "2330.json"), encoding="utf-8") as f:
            manual_asli = json.load(f)
        debt_manual, _, _ = dcf.net_debt(manual_asli["balance_sheet"], include_leases=False)

        # Muat via muat_valuasi("2330")
        gabung = store.muat_valuasi("2330")
        self.assertIsNotNone(gabung)
        debt_gabung, _, _ = dcf.net_debt(gabung["balance_sheet"], include_leases=False)

        selisih_rel = abs(debt_gabung - debt_manual) / debt_manual
        self.assertLess(
            selisih_rel,
            0.01,
            f"Selisih utang gabungan ({debt_gabung}) vs manual ({debt_manual}) melebihi 1%: {selisih_rel:.4%}",
        )


class TestB3SitasiMops(unittest.TestCase):
    """Pemeriksa untuk item B3: sitasi MOPS untuk laporan keuangan."""

    def test_b3_url_mops(self):
        """2330, 2025, Q4, neraca -> URL memuat ajax_t164sb03, co_id=2330, year=114, season=04."""
        from app import sitasi

        url = sitasi.mops_laporan("2330", 2025, "Q4", "neraca")
        self.assertIn("ajax_t164sb03", url)
        self.assertIn("co_id=2330", url)
        self.assertIn("year=114", url)
        self.assertIn("season=04", url)

        # Uji jenis lain (lr dan arus)
        url_lr = sitasi.mops_laporan("2330", 2025, 4, "lr")
        self.assertIn("ajax_t164sb04", url_lr)
        url_cf = sitasi.mops_laporan("2330", 2025, 4, "arus")
        self.assertIn("ajax_t164sb05", url_cf)

    def test_b3_tautan_di_tab_keuangan(self):
        """GET /saham/2330?tab=keu -> setiap kolom periode punya tautan mopsov; tiga bahasa tanpa '⟦'."""
        c = TestClient(main.app)
        for lang in ("en", "zh", "id"):
            resp = c.get(f"/saham/2330?tab=keu&lang={lang}")
            self.assertEqual(resp.status_code, 200, f"Status bukan 200 pada lang={lang}")
            self.assertNotIn("⟦", resp.text, f"String tak terterjemahkan pada lang={lang}")
            self.assertIn("mopsov.twse.com.tw", resp.text, f"Tautan mopsov tidak ada pada lang={lang}")
            self.assertIn("ajax_t164sb04", resp.text, f"Program ajax_t164sb04 tidak ada pada lang={lang}")
            self.assertIn(i18n.t("sh.sumber_resmi_mops", lang), resp.text)

    def test_b3_cek_resmi_kumulatif(self):
        """Sampel buatan t187ap06 kumulatif Q2 vs dua kuartal FinMind -> selisih 0%."""
        import sys
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import cek_finmind_resmi

        seri_fm_revenue = {
            "2026-03-31": 100_000_000.0,
            "2026-06-30": 150_000_000.0,
            "2026-09-30": 200_000_000.0,
        }
        rec_twse_lr = {
            "年度": "115",
            "季別": "2",
            "公司代號": "9999",
            "公司名稱": "Uji",
            "營業收入": "250000.00",
            "稅前淨利（淨損）": "50000.00",
        }
        seri_fm_pbt = {
            "2026-03-31": 20_000_000.0,
            "2026-06-30": 30_000_000.0,
        }

        res = cek_finmind_resmi.bandingkan_angka(
            kode="9999",
            tahun_roc=115,
            kuartal=2,
            rec_lr=rec_twse_lr,
            rec_nr=None,
            seri_lr={"Revenue": seri_fm_revenue, "PreTaxIncome": seri_fm_pbt},
            seri_nr={},
        )

        pos_rev = res["pos"]["營業收入"]
        self.assertEqual(pos_rev["resmi"], 250000.00)
        self.assertEqual(pos_rev["finmind"], 250000.00)
        self.assertEqual(pos_rev["pct"], 0.0)

        pos_pbt = res["pos"]["稅前淨利（淨損）"]
        self.assertEqual(pos_pbt["resmi"], 50000.00)
        self.assertEqual(pos_pbt["finmind"], 50000.00)
        self.assertEqual(pos_pbt["pct"], 0.0)


class TestR4PengungkapanPihakKetiga(unittest.TestCase):
    """Pemeriksa untuk item R4: pengungkapan pihak ketiga dan alat AI."""

    def test_r4_semua_pustaka_tercantum(self):
        """Setiap nama paket di requirements.txt muncul di docs/pengungkapan-pihak-ketiga.md."""
        doc = (ROOT / "docs" / "pengungkapan-pihak-ketiga.md").read_text(encoding="utf-8")
        reqs = (ROOT / "requirements.txt").read_text(encoding="utf-8")

        for line in reqs.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = re.split(r"[=<>\[]", line)[0].strip()
            self.assertIn(
                pkg,
                doc,
                f"Paket '{pkg}' dari requirements.txt belum tercantum di docs/pengungkapan-pihak-ketiga.md",
            )

    def test_r4_tabel_tim_kosong(self):
        """Bagian 'Pembagian kerja tim' ada dan baris isinya kosong."""
        doc = (ROOT / "docs" / "pengungkapan-pihak-ketiga.md").read_text(encoding="utf-8")
        self.assertIn("pembagian kerja tim", doc.lower())

        bagian_tim = doc.lower().split("pembagian kerja tim")[1]
        lines = [l.strip() for l in bagian_tim.splitlines() if l.strip()]
        table_lines = [l for l in lines if l.startswith("|")]
        self.assertEqual(
            len(table_lines),
            2,
            f"Tabel pembagian kerja tim harus kosong (hanya header dan pemisah), ditemukan {len(table_lines)} baris: {table_lines}",
        )


