"""Temuan D5 (jejak 2330-2026-11-10-211853): label dengan nomor butir dan satuan 佰萬元."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import extract  # noqa: E402


class TestLabelSatuan(unittest.TestCase):
    def test_label_dengan_nomor_butir(self):
        lbl = "5. 交易單位數量（如ＸＸ平方公尺，折合ＸＸ坪）、每單位價格及交易總金額"
        self.assertTrue(extract.label_sah(lbl, "capex"))
        self.assertTrue(extract.label_sah("12、交易金額", "cash"))
        self.assertFalse(extract.label_sah("9. 其他應敘明事項", "capex"))

    def test_satuan_varian(self):
        self.assertEqual(extract._satuan_dari("美金19,442佰萬元"), ("佰萬元", 1.0))
        self.assertEqual(extract._satuan_dari("新台幣3仟萬元"), ("仟萬元", 10.0))
        self.assertEqual(extract._satuan_dari("新台幣3千萬元"), ("千萬元", 10.0))
        self.assertEqual(extract._satuan_dari("新台幣500萬元"), ("萬元", 0.01))



class TestKodePerluValuasi(unittest.TestCase):
    def test_pilih_yang_tertahan_tanpa_valuasi(self):
        from unittest import mock
        from app import main
        cache = [
            {"id": "a", "status": "ditahan", "tanggal": "2026-11-10", "emiten": {"kode": "1111"},
             "muatan": {"tahan": {"jenis": "tanpa_valuasi"}}},
            {"id": "b", "status": "ditahan", "tanggal": "2026-11-10", "emiten": {"kode": "2222"},
             "muatan": {"tahan": {"jenis": "tanpa_angka"}}},
            {"id": "c", "status": "terbit", "tanggal": "2026-11-10", "emiten": {"kode": "3333"}},
        ]
        with mock.patch.object(main, "_cache", cache), mock.patch.object(main, "_valuasi_dicoba", {}), \
                mock.patch.object(main.valuasi_otomatis, "baca_cache", return_value=None):
            self.assertEqual(main._kode_perlu_valuasi(), ["1111"])
            self.assertEqual(main._kode_perlu_valuasi(), [])      # baru dicoba: tunggu 6 jam


if __name__ == "__main__":
    unittest.main()
