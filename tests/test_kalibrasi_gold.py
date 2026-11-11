"""Kalibrasi 11 Nov dari gold set Patrice: rugi dalam kurung, satuan 仟股, ambang a–d."""
import unittest

from app import ambang_profil
from app.agent import screen, sinyal


def _b(no, label, value):
    return {"no": no, "label": label, "label_lengkap": label, "value": value}


class TestKalibrasi(unittest.TestCase):
    def test_rugi_dalam_kurung_negatif(self):
        d = {"clause": 31, "items": [
            _b(4, "1月1日累計至本期止營業收入(仟元)", "18,958"),
            _b(9, "1月1日累計至本期止歸屬於母公司業主淨利(損) (仟元)", "(339,123)"),
            _b(10, "1月1日累計至本期止基本每股盈餘(損失) (元)", "(2.04)"),
            _b(11, "期末總資產(仟元)", "1,304,688"), _b(12, "期末總負債(仟元)", "112,744")]}
        s = sinyal.urai_laporan(d)
        self.assertAlmostEqual(s["laba_induk_juta"], -339.123)
        self.assertEqual(s["eps"], -2.04)
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "perhatian")

    def test_ambang_utang_moderat_50(self):
        s = {"jenis": "laporan", "laba_induk_juta": 10.0, "rasio_utang": 0.55}
        self.assertEqual(ambang_profil.tingkat(s, "moderat")["tingkat"], "perhatian")
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "info")

    def test_saham_baru_satuan_ribu(self):
        for label, isi, lembar in (("全案發行總金額及股數", "本公司擬發行普通股(上限)120,000仟股", 120_000_000),
                                   ("私募股數或張數", "發行股數不超過15,000仟股", 15_000_000),
                                   ("因認股權行使而須發行之新股總數", "新股總數為1,000,000股。", 1_000_000)):
            d = {"clause": 11, "subject": "公告本公司董事會決議辦理現金增資發行新股", "items": [_b(4, label, isi)]}
            self.assertEqual(sinyal.urai_modal(d, None)["lembar_berubah"], lembar, label)

    def test_saham_baru_tak_terbaca_perhatian(self):
        s = {"jenis": "modal", "subjenis": "saham_baru", "persen_saham": None, "persen_kapitalisasi": None}
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "perhatian")

    def test_pinjaman_40_persen(self):
        s = {"jenis": "pinjaman", "rasio_ekuitas": 0.468, "pemakaian_limit": None, "pihak_luar": False}
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "perhatian")
        s["rasio_ekuitas"] = 0.21
        self.assertEqual(ambang_profil.tingkat(s, "moderat")["tingkat"], "info")
        p = {"jenis": "penjaminan", "rasio_ekuitas": 0.468, "pemakaian_limit": None, "pihak_luar": False}
        self.assertEqual(ambang_profil.tingkat(p, "moderat")["tingkat"], "info")

    def test_pasal20_anak_100_persen_diarsipkan(self):
        d = {"clause": 20, "subject": "公告本公司董事會決議通過對100%直接持有之子公司群環科技股份有限公司現金增資案", "items": []}
        self.assertFalse(screen.saring(d)["lolos"])
        d2 = {"clause": 20, "subject": "新建工程結算", "items": [
            _b(5, "契約相對人及其與公司之關係", "契約相對人：甲公司 其與公司之關係：本公司100%之子公司")]}
        self.assertFalse(screen.saring(d2)["lolos"])
        d3 = {"clause": 20, "subject": "公告本公司董事會決議申購土地", "items": [
            _b(5, "交易相對人及其與公司之關係", "某建設公司，非關係人"),
            _b(9, "其他應敘明事項", "本公司持股100%之子公司另案辦理")]}
        self.assertTrue(screen.saring(d3)["lolos"], "100% di butir lain tidak boleh memicu arsip")


if __name__ == "__main__":
    unittest.main()
