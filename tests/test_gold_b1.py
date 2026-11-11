"""Pengujian evaluasi gold set B1 dan ekspor kandidat per jalur."""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from app import gold
import evaluasi


class TestGoldB1(unittest.TestCase):
    """Pemeriksaan fitur baru gold set B1: 3-way decision, tingkat sinyal, dan privasi."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_kolom_lama_tetap_jalan(self):
        """Kolom lama harus_terbit (ya/tidak) dipetakan ke keputusan (terbit/arsip)."""
        p = os.path.join(self._tmp.name, "lama.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(
                "source_url,kode,harus_terbit,input,nilai_juta_ntd,butir_no,pelabel,catatan\n"
                "http://u1,2330,ya,capex,1200000,3,FR,ok\n"
                "http://u2,2454,tidak,,,,,FR,lewat\n"
            )
        data = evaluasi.muat_gold(p)
        self.assertEqual(len(data), 2)
        self.assertEqual(data["http://u1"]["keputusan"], "terbit")
        self.assertTrue(data["http://u1"]["harus_terbit"])
        self.assertEqual(data["http://u1"]["angka"], [("capex", 1200000.0)])
        self.assertEqual(data["http://u2"]["keputusan"], "arsip")
        self.assertFalse(data["http://u2"]["harus_terbit"])

    def test_bentrok_harus_terbit_vs_keputusan(self):
        """Jika harus_terbit dan keputusan saling bertentangan, muncul ValueError dengan baris."""
        p = os.path.join(self._tmp.name, "bentrok.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(
                "source_url,kode,harus_terbit,keputusan,tingkat,input,nilai_juta_ntd,butir_no,pelabel,catatan\n"
                "http://u1,2330,ya,arsip,,capex,1200000,3,FR,bentrok\n"
            )
        with self.assertRaises(ValueError) as ctx:
            evaluasi.muat_gold(p)
        pesan = str(ctx.exception)
        self.assertIn("2", pesan)
        self.assertIn("bertentangan", pesan)

    def test_keputusan_tahan_dan_jalur_berat(self):
        """Keputusan tahan valid dan dipetakan dengan benar tanpa memerlukan nilai_juta_ntd."""
        p = os.path.join(self._tmp.name, "tahan.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(
                "source_url,kode,harus_terbit,keputusan,tingkat,input,nilai_juta_ntd,butir_no,pelabel,catatan\n"
                "http://u_berat,2330,,tahan,serius,berat,,,PDK,kejadian pasal 1\n"
            )
        data = evaluasi.muat_gold(p)
        self.assertIn("http://u_berat", data)
        self.assertEqual(data["http://u_berat"]["keputusan"], "tahan")
        self.assertFalse(data["http://u_berat"]["harus_terbit"])
        self.assertEqual(data["http://u_berat"]["tingkat"], "serius")

    def test_tingkat_sinyal_cocok(self):
        """Tingkat sinyal dihitung dan dicocokkan dengan ambang_profil moderat."""
        g = {
            "http://s1": {
                "source_url": "http://s1",
                "harus_terbit": True,
                "keputusan": "terbit",
                "tingkat": "serius",
                "angka": [],
            }
        }
        # Sinyal penjaminan dengan rasio ekuitas 85% (> 80% moderat) -> serius
        h = [
            {
                "source_url": "http://s1",
                "id": "1",
                "status": "terbit",
                "terbit": [],
                "meta": {},
                "sinyal": {"jenis": "penjaminan", "rasio_ekuitas": 0.85, "pemakaian_limit": 0.5},
            }
        ]
        res = evaluasi.nilai(h, g)
        self.assertEqual(res["kecocokan_tingkat"], [1, 1])

    def test_tingkat_sinyal_tidak_cocok(self):
        """Bila tingkat keluaran berbeda dengan gold, tercatat sebagai tidak cocok."""
        g = {
            "http://s2": {
                "source_url": "http://s2",
                "harus_terbit": True,
                "keputusan": "terbit",
                "tingkat": "info",
                "angka": [],
            }
        }
        # Rasio ekuitas 90% memicu 'serius' pada profil moderat, berbeda dari label 'info'
        h = [
            {
                "source_url": "http://s2",
                "id": "2",
                "status": "terbit",
                "terbit": [],
                "meta": {},
                "sinyal": {"jenis": "penjaminan", "rasio_ekuitas": 0.90, "pemakaian_limit": 0.5},
            }
        ]
        res = evaluasi.nilai(h, g)
        self.assertEqual(res["kecocokan_tingkat"], [0, 1])

    def test_input_b1_valid_tanpa_nilai(self):
        """Input jalur sinyal B1 (risiko, modal, laporan, berat, tata_kelola) boleh tanpa nilai_juta_ntd."""
        p = os.path.join(self._tmp.name, "jalur_b1.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(
                "source_url,kode,harus_terbit,keputusan,tingkat,input,nilai_juta_ntd,butir_no,pelabel,catatan\n"
                "http://u_mod,2330,,terbit,perhatian,modal,,,FR,buyback\n"
                "http://u_lap,2330,,terbit,info,laporan,,,FR,q3\n"
                "http://u_gov,2330,,terbit,info,tata_kelola,,,FR,ganti auditor\n"
            )
        data = evaluasi.muat_gold(p)
        self.assertEqual(len(data), 3)
        self.assertEqual(data["http://u_mod"]["input"], "modal")
        self.assertEqual(data["http://u_lap"]["input"], "laporan")
        self.assertEqual(data["http://u_gov"]["input"], "tata_kelola")

    def test_ekspor_tanpa_nama_orang(self):
        """_ringkas pada app.gold tidak boleh memasukkan butir yang mengandung kata 姓名."""
        dokumen = {
            "items": [
                {
                    "no": "1",
                    "label": "舊任者姓名及簡歷",
                    "value": "張忠謀 / 董事長",
                    "satuan_label": "",
                    "sub": [],
                },
                {
                    "no": "2",
                    "label": "新任者姓名及簡歷",
                    "value": "魏哲家 / 總裁",
                    "satuan_label": "",
                    "sub": [],
                },
                {
                    "no": "3",
                    "label": "投資金額",
                    "value": "1500000000",
                    "satuan_label": "元",
                    "sub": [],
                },
            ]
        }
        ringkasan = gold._ringkas(dokumen)
        self.assertNotIn("姓名", ringkasan)
        self.assertNotIn("張忠謀", ringkasan)
        self.assertNotIn("魏哲家", ringkasan)
        self.assertIn("1500000000", ringkasan)

    def test_sampel_per_jalur(self):
        """gold.pilih harus menyeimbangkan sampel berdasarkan jalur sinyal B1."""
        rek = [
            {"code": "2330", "clause": 20, "items": [{"label": "金額", "value": "100"}], "date": "1150901", "name": "TSMC", "subject": "Aset", "source_url": "u20"},
            {"code": "2330", "clause": 22, "items": [], "date": "1150901", "name": "TSMC", "subject": "Penjaminan", "source_url": "u22"},
            {"code": "2330", "clause": 11, "items": [], "date": "1150901", "name": "TSMC", "subject": "Modal", "source_url": "u11"},
            {"code": "2330", "clause": 31, "items": [], "date": "1150901", "name": "TSMC", "subject": "Laporan", "source_url": "u31"},
            {"code": "2330", "clause": 1, "items": [], "date": "1150901", "name": "TSMC", "subject": "Gagal bayar", "source_url": "u1"},
            {"code": "2330", "clause": 7, "items": [], "date": "1150901", "name": "TSMC", "subject": "Auditor", "source_url": "u7"},
            {"code": "2330", "clause": 12, "items": [], "date": "1150901", "name": "TSMC", "subject": "Investor", "source_url": "u12"},
        ]
        pilihan = gold.pilih(rek, per_jalur=1)
        klausul = {x["clause"] for x in pilihan}
        self.assertIn(20, klausul)  # valuasi
        self.assertIn(22, klausul)  # risiko
        self.assertIn(11, klausul)  # modal
        self.assertIn(31, klausul)  # laporan
        self.assertIn(1, klausul)   # berat
        self.assertIn(7, klausul)   # tata_kelola
        self.assertIn(12, klausul)  # dilewati

    def test_matriks_3x3_dan_akurasi_3arah(self):
        """Matriks kebingungan 3x3 dan akurasi 3 arah dihitung akurat."""
        g = {
            "http://1": {"source_url": "http://1", "harus_terbit": True, "keputusan": "terbit", "angka": []},
            "http://2": {"source_url": "http://2", "harus_terbit": False, "keputusan": "tahan", "angka": []},
            "http://3": {"source_url": "http://3", "harus_terbit": False, "keputusan": "arsip", "angka": []},
        }
        h = [
            {"source_url": "http://1", "id": "1", "status": "terbit", "terbit": [], "meta": {}},
            {"source_url": "http://2", "id": "2", "status": "ditahan", "terbit": [], "meta": {}},
            {"source_url": "http://3", "id": "3", "status": "dilewati", "terbit": [], "meta": {}},
        ]
        res = evaluasi.nilai(h, g)
        self.assertEqual(res["keputusan_3arah_tepat"], 3)
        self.assertEqual(res["matriks_3x3"]["terbit"]["terbit"], 1)
        self.assertEqual(res["matriks_3x3"]["tahan"]["tahan"], 1)
        self.assertEqual(res["matriks_3x3"]["arsip"]["arsip"], 1)

        teks = evaluasi.laporan({"aturan": res}, "sumber_uji", "gold.csv", {"aturan": "aturan"}, 0, None)
        self.assertIn("Akurasi keputusan 3 arah", teks)
        self.assertIn("Matriks kebingungan keputusan 3 arah", teks)


class TestGoldTanpaNama(unittest.TestCase):
    def test_teks_bebas_pasal_8_tidak_masuk(self):
        """Kasus nyata 7718: nama pejabat ada di 其他應敘明事項, label tanpa 姓名."""
        from app import gold
        d = {"clause": 8, "items": [
            {"no": 1, "label": "人員變動別", "value": "公司治理主管"},
            {"no": 3, "label": "舊任者姓名、級職及簡歷", "value": "王小明/經理"},
            {"no": 5, "label": "異動情形", "value": "退休"},
            {"no": 6, "label": "異動原因", "value": "李大華先生退休"},
            {"no": 7, "label": "生效日期", "value": "116/01/01"},
            {"no": 8, "label": "其他應敘明事項", "value": "張小英將於115/12/31退休"},
        ]}
        r = gold._ringkas(d)
        for nama in ("王小明", "李大華", "張小英"):
            self.assertNotIn(nama, r)
        self.assertIn("公司治理主管", r)
        self.assertIn("退休", r)


if __name__ == "__main__":
    unittest.main()
