"""Tes regresi untuk perbaikan temuan QA (K-1, T-1..T-2, M-1..M-6)."""

from __future__ import annotations

import os
import tempfile
import threading
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import config, main, pasar, review, ringkasan, sitasi, store, tarik
from app.agent import llm


class TestSitasiFallback(unittest.TestCase):
    """K-1: mops_laporan aman saat tahun_iso None dan /saham?tab=keu tidak 500."""

    def test_mops_laporan_tanpa_periode_jatuh_ke_cadangan(self):
        self.assertEqual(sitasi.mops_laporan("2330", None, None, "lr"), sitasi.mops_cadangan("lr"))
        self.assertEqual(sitasi.mops_laporan("2330", "", None, "neraca"), sitasi.mops_cadangan("neraca"))
        self.assertEqual(sitasi.mops_laporan("2330", "None", None, "arus"), sitasi.mops_cadangan("arus"))

    def test_halaman_saham_keu_kosong_tidak_crash(self):
        c = TestClient(main.app)
        tb_kosong = {"ada": False, "info": {"galat": "offline"}}
        with mock.patch("app.pasar.tabel", return_value=tb_kosong), \
             mock.patch("app.pasar.harga", return_value=None), \
             mock.patch("app.pasar._ambil_json", return_value=[]):
            for lang in ("en", "zh", "id"):
                r = c.get(f"/saham/2330?tab=keu&lang={lang}")
                self.assertEqual(r.status_code, 200, f"Gagal di bahasa {lang}")
                self.assertIn(sitasi.mops_cadangan("lr"), r.text)


class TestCssDanUiReview(unittest.TestCase):
    """T-1, M-1, M-6: [hidden] CSS, chip filter /review, lencana duplikat, dan cari_hasil."""

    def test_css_memiliki_aturan_hidden_global(self):
        css_path = os.path.join(config.ROOT, "app", "static", "app.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        self.assertIn("[hidden] { display: none !important; }", css)

    def test_review_memakai_chip_on_dan_tanpa_held_duplikat(self):
        c = TestClient(main.app)
        with mock.patch("app.pasar.harga_dari_cache", return_value=None):
            for lang in ("en", "zh", "id"):
                r = c.get(f"/review?lang={lang}")
                self.assertEqual(r.status_code, 200)
                self.assertNotIn('class="chip aktif"', r.text)
                self.assertNotIn('class="lencana l-dilewati mono">HELD<', r.text)
                if 'data-filter-sebab="semua"' in r.text:
                    self.assertIn('class="chip on" data-filter-sebab="semua"', r.text)

    def test_cari_hasil_tabel_geser_dan_terlokalisasi(self):
        c = TestClient(main.app)
        palsu = [
            {"kode": "2330", "nama": "台積電", "nama_en": "TSMC", "bursa": "TWSE"},
            {"kode": "2303", "nama": "聯電", "nama_en": "UMC", "bursa": "TWSE"},
        ]
        with mock.patch("app.indeks_nama.cari", return_value=palsu), \
             mock.patch("app.indeks_nama.apakah_cocok_persis", return_value=False):
            r = c.get("/saham?kode=semi&lang=id")
            self.assertEqual(r.status_code, 200)
            self.assertIn('<div class="tabel-geser">', r.text)
            self.assertNotIn("<th>English</th>", r.text)
            self.assertNotIn("<th>Exchange</th>", r.text)
            self.assertIn("<th>Bursa</th>", r.text)


class TestKunciBacaKeamanan(unittest.TestCase):
    """T-2: halaman 401 tidak membocorkan sidebar/watchlist, cookie HMAC, dan POST /akses."""

    def setUp(self):
        self._asli = (config.KUNCI_BACA, config.KODE_AKSES, tarik.WATCHLIST_FILE)
        self._tmp = tempfile.TemporaryDirectory()
        tarik.WATCHLIST_FILE = os.path.join(self._tmp.name, "watchlist.json")
        tarik.simpan_watchlist(["2330", "2454"])

    def tearDown(self):
        config.KUNCI_BACA, config.KODE_AKSES, tarik.WATCHLIST_FILE = self._asli
        self._tmp.cleanup()

    def test_401_mandiri_tanpa_bocor_dan_post_akses_bertanda_hmac(self):
        config.KUNCI_BACA = True
        config.KODE_AKSES = "rahasia-qa-99"
        c = TestClient(main.app)

        r401 = c.get("/")
        self.assertEqual(r401.status_code, 401)
        self.assertIn('method="post" action="/akses"', r401.text)
        self.assertNotIn("2330", r401.text)
        self.assertNotIn("side-nav", r401.text)
        self.assertNotIn("cp-panel", r401.text)

        r_salah = c.post("/akses", data={"kode": "tebak", "kembali": "/watchlist"}, follow_redirects=False)
        self.assertEqual(r_salah.status_code, 303)
        self.assertEqual(c.get("/watchlist").status_code, 401)

        r_ok = c.post("/akses", data={"kode": "rahasia-qa-99", "kembali": "/watchlist"}, follow_redirects=False)
        self.assertEqual(r_ok.status_code, 303)
        cookie_val = c.cookies.get("akses")
        self.assertIsNotNone(cookie_val)
        self.assertNotEqual(cookie_val, "rahasia-qa-99")

        self.assertEqual(c.get("/watchlist").status_code, 200)


class TestKonkurensiDanPemeriksa(unittest.TestCase):
    """M-2, M-3: keutuhan penulisan konkuren review/cache dan word boundary ringkasan."""

    def test_simpan_review_konkuren_utuh(self):
        asli_file = review.KEPUTUSAN_FILE
        with tempfile.TemporaryDirectory() as td:
            review.KEPUTUSAN_FILE = os.path.join(td, "keputusan_review.json")
            try:
                galat = []

                def tulis(idx: int):
                    try:
                        review.simpan(f"2330-2026-11-{idx:02d}", "arsipkan", f"catatan {idx}", jenis="verifikasi")
                    except Exception as e:  # noqa: BLE001
                        galat.append(e)

                threads = [threading.Thread(target=tulis, args=(i,)) for i in range(16)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                self.assertEqual(galat, [])
                data = review.baca()
                self.assertEqual(len(data), 16)
            finally:
                review.KEPUTUSAN_FILE = asli_file

    def test_tulis_cache_llm_konkuren_aman(self):
        asli_dir = llm.CACHE_DIR
        with tempfile.TemporaryDirectory() as td:
            llm.CACHE_DIR = td
            try:
                galat = []

                def tulis(idx: int):
                    try:
                        llm._tulis_cache("kunci_bersama", {"i": idx}, {"model": "uji"})
                    except Exception as e:  # noqa: BLE001
                        galat.append(e)

                threads = [threading.Thread(target=tulis, args=(i,)) for i in range(12)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                self.assertEqual(galat, [])
                self.assertIsNotNone(llm._baca_cache("kunci_bersama"))
            finally:
                llm.CACHE_DIR = asli_dir

    def test_ringkasan_izinkan_buyback_dan_pembelian(self):
        res_kosong = {
            "kode": "2330", "bahasa": "en", "kesimpulan": "Summary.",
            "kecocokan": "Fits profile.", "fakta": [{"teks": "Capital expenditure is steady."}],
        }
        for kalimat_aman in (
            "Program pembelian aset tetap berjalan sesuai rencana.",
            "Perseroan mengumumkan program buyback saham.",
            "Perusahaan akan melakukan beli kembali saham beredar.",
            "Average selling price stayed stable.",
        ):
            ok, msg = ringkasan.periksa_narasi(kalimat_aman, res_kosong)
            self.assertTrue(ok, f"Seharusnya lolos: {kalimat_aman} ({msg})")

        for kalimat_larang in (
            "A good time to buy this stock.",
            "Investors should sell immediately.",
            "Strong buy on valuation.",
            "Waktunya beli saham ini.",
            "建議買進。",
        ):
            ok, _ = ringkasan.periksa_narasi(kalimat_larang, res_kosong)
            self.assertFalse(ok, f"Seharusnya ditolak: {kalimat_larang}")

    def test_api_tanya_berjalan_di_worker_thread(self):
        from app import chat
        c = TestClient(main.app)
        tid = threading.get_ident()
        dipanggil_dari: list[int] = []

        def tanya_palsu(*args, **kwargs):
            dipanggil_dari.append(threading.get_ident())
            return {
                "id": "uji-1", "jalur": "aturan", "jawaban": "OK",
                "sumber": [], "tautan": [], "tanda": "", "periksa": True,
                "ditolak": False, "durasi_ms": 1, "panggilan_model": 0, "panggilan_alat": 0,
            }

        with mock.patch.object(chat, "tanya", side_effect=tanya_palsu):
            r = c.post("/api/tanya", json={"pertanyaan": "harga 2330?", "bahasa": "en"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(dipanggil_dari), 1)
        self.assertNotEqual(dipanggil_dari[0], tid)


class TestTampilanDanCookie(unittest.TestCase):
    """M-4, M-5, M-6: harga watchlist, lokalisasi sebab_cadangan, stats 0, cookie risiko."""

    def test_watchlist_memuat_harga_cache(self):
        c = TestClient(main.app)
        palsu = {"tutup": 1060.0, "nama": "台積電", "ubah_pct": 0.015}
        with mock.patch("app.tarik.baca_watchlist", return_value=["2330"]), \
             mock.patch("app.pasar.harga_dari_cache", return_value=palsu):
            r = c.get("/watchlist")
            self.assertEqual(r.status_code, 200)
            self.assertIn("1,060.00", r.text)

    def test_jejak_cadangan_terlokalisasi_di_html_tetap_utuh_di_api(self):
        c = TestClient(main.app)
        en_html = c.get("/jejak/2330-2026-09-18-1?lang=en")
        zh_html = c.get("/jejak/2330-2026-09-18-1?lang=zh")
        api_json = c.get("/api/jejak/2330-2026-09-18-1")
        self.assertEqual(en_html.status_code, 200)
        self.assertEqual(zh_html.status_code, 200)
        self.assertEqual(api_json.status_code, 200)
        self.assertIn("no API key set", en_html.text)
        self.assertNotIn("tidak ada kunci API", en_html.text)
        self.assertIn("未設定 API 金鑰", zh_html.text)
        self.assertNotIn("tidak ada kunci API", zh_html.text)
        self.assertIn("tidak ada kunci API", api_json.text)

    def test_saham_stats_nilai_nol_tampil_nol_bukan_dash(self):
        from app import i18n
        c = TestClient(main.app)
        stats_nol = {
            "ttm_sampai": "2026-06-30",
            "kapitalisasi": 0.0,
            "lembar": 0.0,
            "pendapatan_ttm": 0.0,
            "laba_bersih_ttm": 0.0,
            "eps_ttm": 0.0,
            "margin_kotor": None,
            "margin_usaha": None,
            "margin_bersih": None,
            "roe": None,
            "roa": None,
            "utang_ekuitas": 0.0,
            "rasio_lancar": 0.0,
            "fcf_ttm": 0.0,
        }
        with mock.patch("app.pasar.statistik", return_value=stats_nol), \
             mock.patch("app.pasar.harga", return_value=None):
            r = c.get("/saham/2330?tab=stats&lang=en")
            self.assertEqual(r.status_code, 200)
            self.assertIn(f"0 {i18n.t('al.juta_ntd', 'en')}", r.text)

    def test_cookie_risiko_tersimpan_di_ambang_dan_valuasi(self):
        c = TestClient(main.app)
        r1 = c.get("/ambang?risiko=agresif")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.cookies.get("risiko"), "agresif")

        r2 = c.get("/valuasi/2330?risiko=konservatif")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.cookies.get("risiko"), "konservatif")


if __name__ == "__main__":
    unittest.main()
