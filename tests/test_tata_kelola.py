"""Pasal 7 (auditor) dan 8 (pejabat kunci): sinyal tata kelola tanpa nama orang (tim keuangan 11 Nov)."""
import json
import unittest

from app import ambang_profil
from app.agent import screen, sinyal


def _b(no, label, value):
    return {"no": no, "label": label, "label_lengkap": label, "satuan_label": None, "value": value}


def _auditor(kantor_baru="資誠聯合會計師事務所", siapa="不適用", beda="無", subjek="公告本公司因會計師事務所內部輪調更換會計師"):
    return {"code": "8081", "clause": 7, "subject": subjek, "items": [
        _b(1, "董事會通過日期", "115/11/06"),
        _b(2, "舊會計師事務所名稱", "資誠聯合會計師事務所"),
        _b(3, "舊任簽證會計師姓名1", "王小明"),
        _b(5, "新會計師事務所名稱", kantor_baru),
        _b(6, "新任簽證會計師姓名1", "李大華"),
        _b(8, "變更會計師之原因", "配合事務所內部輪調政策。"),
        _b(9, "說明係由公司主動終止委任或不再繼續委任或前任會計師主動終止委任", siapa),
        _b(12, "公司對上開調整或建議事項有無不同意見", beda),
    ]}


def _pejabat(jabatan="會計主管", perubahan="新任", subjek="公告本公司會計主管異動"):
    return {"code": "4551", "clause": 8, "subject": subjek, "items": [
        _b(1, "人員變動別（請輸入發言人、代理發言人、財務主管、會計主管）", jabatan),
        _b(2, "發生變動日期", "115/11/09"),
        _b(3, "舊任者姓名、級職及簡歷", "代理會計主管:吳正芬/本公司會計課長"),
        _b(4, "新任者姓名、級職及簡歷", "會計主管:詹文裕/資深經理"),
        _b(5, "異動情形（請輸入「辭職」、「職務調整」、「資遣」、「退休」、「死亡」、「新任」或「解任」）", perubahan),
        _b(6, "異動原因", "原任者鍾先生另有規劃"),
        _b(7, "生效日期", "115/11/09"),
    ]}


NAMA = ("王小明", "李大華", "吳正芬", "詹文裕", "鍾先生")


class TestAuditor(unittest.TestCase):
    def test_jalur(self):
        self.assertEqual(screen.saring(_auditor())["jalur"], "tata_kelola")
        self.assertEqual(screen.saring(_pejabat())["jalur"], "tata_kelola")

    def test_rotasi_info(self):
        s = sinyal.urai_auditor(_auditor())
        self.assertFalse(s["ganti_kantor"])
        self.assertEqual(ambang_profil.tingkat(s, "moderat")["tingkat"], "info")

    def test_ganti_kantor_perhatian(self):
        s = sinyal.urai_auditor(_auditor(kantor_baru="勤業眾信聯合會計師事務所"))
        self.assertTrue(s["ganti_kantor"])
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "perhatian")

    def test_auditor_mundur_dan_beda_pendapat_serius(self):
        s = sinyal.urai_auditor(_auditor(siapa="前任會計師主動終止委任"))
        self.assertTrue(s["auditor_mundur"])
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "serius")
        s = sinyal.urai_auditor(_auditor(beda="有，對存貨評價調整有不同意見"))
        self.assertTrue(s["beda_pendapat"])
        self.assertEqual(ambang_profil.tingkat(s, "moderat")["tingkat"], "serius")

    def test_tanpa_nama(self):
        for d in (_auditor(), _pejabat()):
            s = sinyal.urai_auditor(d) if d["clause"] == 7 else sinyal.urai_pejabat(d)
            teks = json.dumps(s, ensure_ascii=False)
            for n in NAMA:
                self.assertNotIn(n, teks)


class TestPejabat(unittest.TestCase):
    def test_kunci_keluar_perhatian(self):
        s = sinyal.urai_pejabat(_pejabat(jabatan="財務長", perubahan="辭職"))
        self.assertTrue(s["kunci"] and s["keluar"])
        self.assertEqual(ambang_profil.tingkat(s, "agresif")["tingkat"], "perhatian")

    def test_kunci_baru_ikut_profil(self):
        s = sinyal.urai_pejabat(_pejabat())
        self.assertEqual(ambang_profil.tingkat(s, "konservatif")["tingkat"], "perhatian")
        self.assertEqual(ambang_profil.tingkat(s, "moderat")["tingkat"], "info")

    def test_jabatan_lain_info_dan_anak_perusahaan(self):
        s = sinyal.urai_pejabat(_pejabat(jabatan="發言人", perubahan="職務調整", subjek="代子公司公告發言人異動"))
        self.assertFalse(s["kunci"])
        self.assertTrue(s["anak_perusahaan"])
        tg = ambang_profil.tingkat(s, "konservatif")
        self.assertEqual(tg["tingkat"], "info")
        self.assertIn("tg.anak_perusahaan", [k for k, _ in tg["alasan"]])


class TestPipeline(unittest.TestCase):
    def test_terbit_dan_ditahan(self):
        from app.agent import pipeline
        from app import store
        def jalan(d):
            d = dict(d, date="2026-11-10", name="Uji", source_url="https://contoh/x")
            return pipeline.jalankan(d, None)
        self.assertEqual(jalan(_auditor())["status"], "terbit")
        self.assertEqual(jalan(_pejabat())["status"], "terbit")
        h = jalan(_auditor(siapa="前任會計師主動終止委任"))
        self.assertEqual(h["status"], "ditahan")
        self.assertEqual(h["muatan"]["tahan"]["jenis"], "tata_kelola_serius")
        teks = json.dumps(jalan(_pejabat())["muatan"], ensure_ascii=False)
        for n in NAMA:
            self.assertNotIn(n, teks)


if __name__ == "__main__":
    unittest.main()
