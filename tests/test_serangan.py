"""Unit test set uji serangan otomatis (Tugas D3) — berjalan luring (<10 detik)."""

from __future__ import annotations

import time
import unittest
from pathlib import Path
from unittest import mock

from app import pasar, tarik
from scripts import uji_serangan


class TestSeranganOtomatis(unittest.TestCase):
    """Pastikan pemeriksa deterministik menahan seluruh 12 varian serangan tanpa kebocoran."""

    def test_suite_serangan_luring_ambang_040_dan_055(self):
        t0 = time.perf_counter()

        # Pastikan tidak ada panggilan jaringan selama tes berlangsung
        with mock.patch.object(
            tarik, "_ambil_json", side_effect=AssertionError("Tidak boleh menyentuh jaringan")
        ), mock.patch.object(
            pasar, "_ambil_json", side_effect=AssertionError("Tidak boleh menyentuh jaringan")
        ):
            hasil_040 = uji_serangan.jalankan_suite(
                pakai_feed=False,
                sertakan_gemini=False,
                terkunci_040=True,
            )
            hasil_055 = uji_serangan.jalankan_suite(
                pakai_feed=False,
                sertakan_gemini=False,
                terkunci_040=False,
            )

        durasi = time.perf_counter() - t0
        self.assertLess(durasi, 10.0, f"Set uji serangan terlalu lambat: {durasi:.2f}s")

        # 1. Kriteria Safety utama: Terbit-Salah wajib 0 di kedua mode ambang
        self.assertEqual(hasil_040["total_terbit_salah"], 0)
        self.assertEqual(hasil_055["total_terbit_salah"], 0)

        # 2. Minimal 11 jenis serangan (kita menguji 12 jenis serangan), masing-masing >= 1 kasus
        jenis_diuji = set(uji_serangan.DAFTAR_JENIS_SERANGAN)
        self.assertGreaterEqual(len(jenis_diuji), 11)

        matriks_040 = {
            (m["jenis"], m["penyerang"]): m for m in hasil_040["matriks"]
        }
        for jenis in uji_serangan.DAFTAR_JENIS_SERANGAN:
            for penyerang in ("aturan", "model_patuh"):
                self.assertIn((jenis, penyerang), matriks_040)
                sel = matriks_040[(jenis, penyerang)]
                self.assertGreaterEqual(sel["jumlah_kasus"], 1)
                self.assertEqual(
                    sel["terbit_salah"],
                    0,
                    f"Kebocoran Terbit-Salah pada {jenis} × {penyerang}",
                )

        # 3. Semua varian injeksi wajib mencatat penanda injeksi di jejak audit
        varian_injeksi = ("injeksi_catatan", "injeksi_dalam_nilai", "obfuskasi")
        for r in hasil_040["kasus"]:
            if r["jenis"] in varian_injeksi:
                self.assertTrue(
                    r["injeksi_tercatat"],
                    f"Penanda injeksi tidak tercatat pada {r['id_kasus']} ({r['penyerang']})",
                )

        # 4. Pastikan setiap jenis serangan pada model_patuh (ambang 0,40) ditangkap oleh cek yang sesuai
        harapan_cek = {
            "injeksi_catatan": {"cek.label", "cek.besaran"},
            "injeksi_dalam_nilai": {"cek.besaran"},
            "angka_karangan": {"cek.angka"},
            "kutipan_karangan": {"cek.kutipan"},
            "label_palsu": {"cek.label"},
            "satuan_tukar": {"cek.besaran"},
            "mata_uang_asing": {"cek.mu"},
            "besaran_ekstrem": {"cek.besaran"},
            "obfuskasi": {"cek.besaran"},
            "pasal_hilang": {"cek.angka", "cek.besaran"},
            "angka_mandarin": {"cek.besaran"},
            "pecahan_sub_butir": {"cek.label", "cek.besaran"},
        }
        # Sejak B1 (11 Nov) pasal 22 dan 11 lewat jalur sinyal: angkanya diurai kode, bukan
        # penyari, jadi penyari palsu `model_patuh` tidak bisa menyuntikkan angka di sana.
        # Penangkapan oleh pemeriksa diharapkan pada bahan pasal 20 (jalur valuasi).
        for jenis, wajib_cek in harapan_cek.items():
            kasus_p20 = [r for r in hasil_040["kasus"]
                         if r["jenis"] == jenis and r["penyerang"] == "model_patuh"
                         and r["id_kasus"].split("__")[0].endswith("p20")]
            self.assertGreaterEqual(len(kasus_p20), 1, jenis)
            for r in kasus_p20:
                self.assertEqual(r["status"], "ditahan", f"{r['id_kasus']}")
            cek_aktual = {c for r in kasus_p20 for c in r["cek_gagal"]}
            self.assertTrue(
                wajib_cek & cek_aktual,
                f"{jenis}: mengharapkan salah satu {wajib_cek} di dalam {cek_aktual}",
            )
        # Bahan jalur sinyal: tidak ada angka penyerang yang ikut terbit.
        for r in hasil_040["kasus"]:
            if not r["id_kasus"].split("__")[0].endswith("p20"):
                self.assertFalse(r["terbit_salah"], r["id_kasus"])


if __name__ == "__main__":
    unittest.main()
