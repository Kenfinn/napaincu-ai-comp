"""Tes unit untuk skrip QA halaman tiga bahasa (QA1).

Memverifikasi fungsi deteksi kunci terjemahan mentah, deteksi teks rusak,
dan pembedaan kata rekomendasi terlarang vs blok penafian resmi.
"""

from __future__ import annotations

import unittest

from scripts import qa_halaman


class TestQAHalaman(unittest.TestCase):
    """Pengujian fungsi-fungsi audit halaman di scripts/qa_halaman.py."""

    def test_deteksi_kunci_mentah(self):
        """Kunci terjemahan mentah (mis. va.xxx, sn.xxx) wajib terdeteksi."""
        html_kotor = """
        <div class="konten">
            <h1>Profil Saham</h1>
            <p>Status: va.otomatis.tanpa_harga</p>
            <span>sn.penjaminan.label</span>
        </div>
        """
        temu = qa_halaman.periksa_kunci_mentah(html_kotor)
        self.assertIn("va.otomatis.tanpa_harga", temu)
        self.assertIn("sn.penjaminan.label", temu)

        html_bersih = """
        <div class="konten">
            <h1>Profil Saham</h1>
            <p>Status: Normal</p>
        </div>
        """
        self.assertEqual(qa_halaman.periksa_kunci_mentah(html_bersih), [])

    def test_deteksi_placeholder_rusak(self):
        """Deteksi teks GANTI, TODO, None, nan, atau Traceback di dalam HTML."""
        html_rusak = """
        <div>
            <h2>Laporan Keuangan</h2>
            <p>GANTI ini segera</p>
            <span>TODO: implementasi</span>
            <td>None</td>
            <div>Traceback (most recent call last):</div>
        </div>
        """
        temu = qa_halaman.periksa_placeholder_rusak(html_rusak)
        self.assertIn("GANTI", temu)
        self.assertIn("TODO", temu)
        self.assertIn("Traceback", temu)
        self.assertIn("None", temu)

    def test_pemeriksa_kata_rekomendasi_di_luar_penafian(self):
        """Kata beli/jual di luar penafian harus ditangkap, tapi kata dalam penafian resmi diabaikan."""
        # 1. Halaman yang hanya memuat blok penafian resmi: harus BERSIH
        html_penafian = """
        <div class="pita fixture">
            <div>This is research, not a buy or sell recommendation. Robo-advice in Taiwan requires an FSC licence.</div>
        </div>
        <p>Penjualan kuartal ini meningkat 12% dan perusahaan tidak menjual aset tetap.</p>
        """
        temu = qa_halaman.periksa_kata_rekomendasi(html_penafian)
        self.assertEqual(temu, [], "Kata dalam penafian dan kata turunan 'penjualan' tidak boleh dihitung pelanggaran")

        # 2. Halaman dengan kata rekomendasi telanjang di luar penafian: harus TERTANGKAP
        html_ilegal = """
        <div class="pita fixture">
            <div>This is research, not a buy or sell recommendation.</div>
        </div>
        <div class="rekomendasi">
            <b>BUY</b> saham ini sekarang.
        </div>
        """
        temu_ilegal = qa_halaman.periksa_kata_rekomendasi(html_ilegal)
        self.assertIn("buy", temu_ilegal)

    def test_kebocoran_bahasa_indonesia_di_en_dan_zh(self):
        """Kata Indonesia umum pada halaman EN atau ZH harus terdeteksi sebagai peringatan."""
        html_bocor = """
        <div>
            <h1>Overview</h1>
            <p>Data belum tersedia dan untuk kuartal ini tidak ada laporan.</p>
        </div>
        """
        bocor_en = qa_halaman.periksa_kebocoran_bahasa(html_bocor, "en")
        self.assertIn("belum", bocor_en)
        self.assertIn("dan", bocor_en)
        self.assertIn("untuk", bocor_en)
        self.assertIn("tidak", bocor_en)

        # Di bahasa Indonesia tidak dianggap bocor
        bocor_id = qa_halaman.periksa_kebocoran_bahasa(html_bocor, "id")
        self.assertEqual(bocor_id, [])

    def test_jalankan_qa_eksekusi_luring(self):
        """Memastikan fungsi jalankan_qa dapat dieksekusi offline dengan TestClient."""
        total_gagal, hasil_uji = qa_halaman.jalankan_qa()
        self.assertTrue(len(hasil_uji) > 0)
        # Verifikasi format keluaran
        item = hasil_uji[0]
        self.assertIn("rute", item)
        self.assertIn("bahasa", item)
        self.assertIn("sukses", item)
