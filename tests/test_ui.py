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


if __name__ == "__main__":
    unittest.main()
