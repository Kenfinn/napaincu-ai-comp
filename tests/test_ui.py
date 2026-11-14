"""Tes otomatis antarmuka pengguna (UI v1.1, U8)."""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from starlette.testclient import TestClient

from app import (
    config,
    gold,
    harga_resmi,
    indeks_nama,
    main,
    pasar,
    review,
    tarik,
    umpan_balik,
    valuasi_otomatis,
)
from app.agent import llm
from app.main import app, hasil
from scripts import qa_halaman

ROOT = Path(__file__).resolve().parent.parent
PASAR_SAMPEL = json.loads((ROOT / "tests" / "data" / "pasar_sampel.json").read_text(encoding="utf-8"))
MANUAL_2330 = json.loads((Path(config.VALUATION_DIR) / "2330.json").read_text(encoding="utf-8"))


class TestUI(unittest.TestCase):
    """Memastikan seluruh halaman UI v1.1 merender bersih dalam 3 bahasa."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        parsed = tmp / "parsed"  # sengaja tidak dibuat/kosong agar jatuh bersih ke data/fixtures/
        raw = tmp / "raw" / "openapi"
        cls._patches = [
            unittest.mock.patch.object(config, "DATA_DIR", str(tmp)),
            unittest.mock.patch.object(config, "PARSED_DIR", str(parsed)),
            unittest.mock.patch.object(config, "TRACE_DIR", str(tmp / "traces")),
            unittest.mock.patch.object(config, "KODE_AKSES", ""),
            unittest.mock.patch.object(config, "SERTAKAN_CONTOH", True),
            unittest.mock.patch.dict(os.environ, {"SENTINEL_SERTAKAN_CONTOH": "1"}, clear=False),
            unittest.mock.patch.object(tarik, "WATCHLIST_FILE", str(tmp / "watchlist.json")),
            unittest.mock.patch.object(tarik, "STATUS_FILE", str(tmp / "status_tarik.json")),
            unittest.mock.patch.object(tarik, "RAW_DIR", str(raw)),
            unittest.mock.patch.object(tarik, "DETAIL_FILE", str(parsed / "details.json")),
            unittest.mock.patch.object(tarik, "LIST_FILE", str(parsed / "announcements.json")),
            unittest.mock.patch.object(review, "KEPUTUSAN_FILE", str(tmp / "keputusan_review.json")),
            unittest.mock.patch.object(umpan_balik, "FILE", str(tmp / "umpan_balik.json")),
            unittest.mock.patch.object(pasar, "CACHE_DIR", str(tmp / "pasar")),
            unittest.mock.patch.object(valuasi_otomatis, "CACHE_DIR", tmp / "valuasi_otomatis"),
            unittest.mock.patch.object(llm, "CACHE_DIR", str(tmp / "cache_model")),
            unittest.mock.patch.object(indeks_nama, "BERKAS_INDEKS", str(tmp / "indeks_nama.json")),
            unittest.mock.patch.object(gold, "ARSIP_DIR", str(raw)),
            unittest.mock.patch.object(tarik, "_ambil_json", return_value=[]),
            unittest.mock.patch.object(pasar, "_ambil_json", return_value=[]),
            unittest.mock.patch.object(pasar, "_finmind", return_value=[]),
            unittest.mock.patch.object(harga_resmi, "_ambil_json", return_value=None),
            unittest.mock.patch.object(indeks_nama, "_ambil_url_json", return_value=None),
            unittest.mock.patch.object(valuasi_otomatis, "pemicu_hitung_beta_latar", return_value=None),
        ]
        for p in cls._patches:
            p.start()

        for nama, isi in PASAR_SAMPEL.items():
            pasar._tulis_cache(nama, isi)
        va_2330 = copy.deepcopy(MANUAL_2330)
        va_2330["otomatis"] = True
        va_2330["bursa"] = "TWSE"
        valuasi_otomatis.simpan_cache("2330", va_2330)

        with main._kunci_cache:
            main._cache = None
        cls.client = TestClient(app, follow_redirects=True)
        daftar = hasil()
        ids = {h["id"]: h.get("status") for h in daftar}
        cls.id_terbit = "2330-2026-09-18-1"
        cls.id_ditahan = "2330-2026-09-19-4"
        assert ids.get(cls.id_terbit) == "terbit", f"Fixture {cls.id_terbit} bukan terbit: {ids}"
        assert ids.get(cls.id_ditahan) == "ditahan", f"Fixture {cls.id_ditahan} bukan ditahan: {ids}"
        cls.rute_utama = [
            "/",
            "/watchlist",
            "/review",
            "/ambang",
            "/tanya",
            "/sehat",
            "/valuasi/2330",
            "/saham/2330?tab=ringkasan",
            "/saham/2330?tab=stream",
            "/saham/2330?tab=stats",
            "/saham/2330?tab=keu",
            "/saham/2330?tab=valuasi",
            "/saham/2330?tab=profil",
            f"/peringatan/{cls.id_terbit}",
            f"/peringatan/{cls.id_ditahan}",
            f"/jejak/{cls.id_terbit}",
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        with main._kunci_cache:
            main._cache = None
        for p in reversed(cls._patches):
            p.stop()
        cls._tmp.cleanup()

    def test_semua_halaman_utama_200_dan_tanpa_kunci_mentah(self) -> None:
        """Semua halaman utama mengembalikan HTTP 200 dan bebas dari '⟦' di 3 bahasa."""
        for rute in self.rute_utama:
            for bhs in ("en", "zh", "id"):
                with self.subTest(rute=rute, bahasa=bhs):
                    r = self.client.get(rute, cookies={"bahasa": bhs})
                    self.assertEqual(r.status_code, 200, f"Gagal {rute} ({bhs})")
                    self.assertNotIn("⟦", r.text, f"Kunci mentah ⟦ di {rute} ({bhs})")
                    mentah = qa_halaman.periksa_kunci_mentah(r.text)
                    self.assertEqual(mentah, [], f"Kunci mentah {mentah} di {rute} ({bhs})")

    def test_tidak_ada_kata_beli_jual_di_luar_penafian(self) -> None:
        """Tidak ada label rekomendasi beli/jual/buy/sell di luar blok penafian."""
        for rute in self.rute_utama:
            for bhs in ("en", "zh", "id"):
                with self.subTest(rute=rute, bahasa=bhs):
                    r = self.client.get(rute, cookies={"bahasa": bhs})
                    temu = qa_halaman.periksa_kata_rekomendasi(r.text)
                    self.assertEqual(
                        temu, [], f"Kata rekomendasi terlarang {temu} di {rute} ({bhs})"
                    )

    def test_panel_chat_tetap_ada_di_base_html(self) -> None:
        """Pastikan {% include \"_panel_chat.html\" %} tidak dihapus dari base.html."""
        akar = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        jalur_base = os.path.join(akar, "app", "templates", "base.html")
        with open(jalur_base, encoding="utf-8") as f:
            isi = f.read()
        self.assertIn('{% include "_panel_chat.html" %}', isi)

        jalur_css = os.path.join(akar, "app", "static", "app.css")
        with open(jalur_css, encoding="utf-8") as f:
            css = f.read()
        for angka in re.findall(r"z-index\s*:\s*(\d+)", css):
            self.assertLessEqual(
                int(angka), 900, f"z-index {angka} di app.css melampaui batas 900"
            )

    def test_komponen_ui_v11_hadir(self) -> None:
        """Pastikan komponen kerangka ponsel, remah roti, kotak artinya, dan garis waktu hadir."""
        r_feed = self.client.get("/", cookies={"bahasa": "id"})
        self.assertIn("bilah-atas", r_feed.text)
        self.assertIn("/static/ui.js", r_feed.text)
        self.assertIn("kartu-filter", r_feed.text)

        r_detail = self.client.get(f"/peringatan/{self.id_terbit}", cookies={"bahasa": "id"})
        self.assertIn("kotak-artinya", r_detail.text)
        self.assertIn('class="remah"', r_detail.text)

        r_jejak = self.client.get(f"/jejak/{self.id_terbit}", cookies={"bahasa": "id"})
        self.assertIn("garis-waktu", r_jejak.text)

    def test_alasan_ditahan_bahasa_polos(self) -> None:
        """QA-3: kasus besaran gagal tidak memuat 'OUTSIDE the 0.20' di luar <details> dan memuat kalimat polos 3 bahasa."""
        import copy
        from app import main, store
        from app.agent import pipeline

        daftar_asli = list(hasil())
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "fixtures", "details.json"), encoding="utf-8") as f:
            import json
            d_asli = next(r for r in json.load(f) if r["_fixture"] == "kasus-1-capex-bersih")
        d_kecil = copy.deepcopy(d_asli)
        d_kecil["seq_no"] = "99"
        d_kecil["time"] = "18:05:00"
        d_kecil["items"][2]["value"] = "新台幣 60,400,000 仟元"
        h_kecil = pipeline.jalankan(d_kecil, store.muat_valuasi("2330"))
        self.assertEqual(h_kecil["status"], "ditahan")

        import html
        with unittest.mock.patch.object(main, "hasil", return_value=daftar_asli + [h_kecil]):
            for bhs, frasa in (
                ("en", "One announcement rarely moves a company's yearly figure"),
                ("zh", "單一公告極少直接代表整年度規模"),
                ("id", "Satu pengumuman jarang langsung menggantikan angka tahunan perusahaan"),
            ):
                r = self.client.get(f"/peringatan/{h_kecil['id']}", cookies={"bahasa": bhs})
                self.assertEqual(r.status_code, 200)
                teks = html.unescape(r.text)
                self.assertNotIn("⟦", teks)
                self.assertIn(frasa, teks)
                tanpa_details = re.sub(r"<details\b.*?</details>", "", teks, flags=re.DOTALL)
                self.assertNotIn("OUTSIDE the 0.20", tanpa_details)
                self.assertNotIn("DI LUAR pita", tanpa_details)
                self.assertNotIn("超出 0.2", tanpa_details)

            for bhs, frasa_mu in (
                ("en", "The amount is in USD. FEAF does not convert currencies"),
                ("zh", "金額以 USD 計價。FEAF 不自動換算匯率"),
                ("id", "Jumlah ini tercatat dalam mata uang USD. FEAF tidak mengonversi mata uang"),
            ):
                r_mu = self.client.get("/peringatan/2330-2026-09-19-4", cookies={"bahasa": bhs})
                self.assertEqual(r_mu.status_code, 200)
                teks_mu = html.unescape(r_mu.text)
                self.assertNotIn("⟦", teks_mu)
                self.assertIn(frasa_mu, teks_mu)

    def test_responsif_menu_lebar_dan_ponsel(self) -> None:
        """QA-6: menu samping 264-280 px, gulir terpisah, kunci gulir laci, tooltip display:none saat tutup, tabel/tab responsif."""
        akar = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(akar, "app", "static", "app.css"), encoding="utf-8") as f:
            css = f.read()

        m_rail = re.search(r"\.rail\s*\{\s*width:\s*(\d+)px", css)
        self.assertIsNotNone(m_rail, "Aturan lebar .rail tidak ditemukan")
        lebar_rail = int(m_rail.group(1))
        self.assertGreaterEqual(lebar_rail, 264)
        self.assertLessEqual(lebar_rail, 280)

        self.assertIn("body.laci-terbuka { overflow: hidden; }", css)
        self.assertRegex(css, r"@media \(min-width: 901px\)[\s\S]*?\.rail\s*\{[^}]*overflow-y:\s*auto")
        self.assertRegex(css, r"\.info::after\s*\{[^}]*display:\s*none")
        self.assertRegex(css, r"\.tab-saham\s*\{[^}]*overflow-x:\s*auto")
        self.assertRegex(css, r"\.tabel-geser\s*\{[^}]*overflow-x:\s*auto")

        # Pastikan berkas skrip QA responsif dapat diimpor bersih
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "qa_responsif", os.path.join(akar, "scripts", "qa_responsif.py")
        )
        self.assertIsNotNone(spec)

    def test_animasi_a1_css_js_dan_form_check(self) -> None:
        """A1.5: View Transitions, reduced motion, token gerak, pageshow, dan action='/check' 3 bahasa."""
        akar = Path(__file__).resolve().parent.parent
        app_css = (akar / "app" / "static" / "app.css").read_text(encoding="utf-8")
        chat_css = (akar / "app" / "static" / "chat.css").read_text(encoding="utf-8")
        ui_js = (akar / "app" / "static" / "ui.js").read_text(encoding="utf-8")

        self.assertIn("@view-transition", app_css)
        self.assertIn("prefers-reduced-motion", app_css)
        self.assertIn("--gerak-sedang", app_css)
        self.assertIn("prefers-reduced-motion", chat_css)
        self.assertIn("pageshow", ui_js)

        for rute in ("/", "/watchlist"):
            for bhs in ("en", "zh", "id"):
                with self.subTest(rute=rute, bahasa=bhs):
                    r = self.client.get(rute, cookies={"bahasa": bhs})
                    self.assertEqual(r.status_code, 200)
                    self.assertIn('action="/check"', r.text)


if __name__ == "__main__":
    unittest.main()
