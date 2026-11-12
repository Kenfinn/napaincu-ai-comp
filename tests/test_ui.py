"""Tes otomatis antarmuka pengguna (UI v1.1, U8)."""

from __future__ import annotations

import os
import re
import unittest
import unittest.mock

from starlette.testclient import TestClient

from app.main import app, hasil
from scripts import qa_halaman


class TestUI(unittest.TestCase):
    """Memastikan seluruh halaman UI v1.1 merender bersih dalam 3 bahasa."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app, follow_redirects=True)
        daftar = hasil()
        cls.id_terbit = next(
            (h["id"] for h in daftar if h.get("status") == "terbit"),
            daftar[0]["id"],
        )
        cls.id_ditahan = next(
            (h["id"] for h in daftar if h.get("status") == "ditahan"),
            daftar[0]["id"],
        )
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

    def test_semua_halaman_utama_200_dan_tanpa_kunci_mentah(self) -> None:
        """Semua halaman utama mengembalikan HTTP 200 dan bebas dari '⟦' di 3 bahasa."""
        with unittest.mock.patch("app.tarik._ambil_json", return_value=[]), \
             unittest.mock.patch("app.pasar._ambil_json", return_value=[]), \
             unittest.mock.patch("app.harga_resmi._ambil_json", return_value=None), \
             unittest.mock.patch("app.valuasi_otomatis.pemicu_hitung_beta_latar", return_value=None):
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
        with unittest.mock.patch("app.tarik._ambil_json", return_value=[]), \
             unittest.mock.patch("app.pasar._ambil_json", return_value=[]), \
             unittest.mock.patch("app.harga_resmi._ambil_json", return_value=None), \
             unittest.mock.patch("app.valuasi_otomatis.pemicu_hitung_beta_latar", return_value=None):
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


if __name__ == "__main__":
    unittest.main()
