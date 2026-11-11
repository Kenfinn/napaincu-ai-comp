"""scripts/buat_paket_gold.py: Excel kandidat tanpa nama orang, dan bisa dibalik ke CSV gold."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import buat_paket_gold as pg  # noqa: E402
from scripts.evaluasi import muat_gold  # noqa: E402


def _d(kode, pasal, items, subjek="uji"):
    return {"code": kode, "name": "Uji", "date": "2026-11-09", "clause": pasal, "subject": subjek,
            "source_url": f"https://contoh/{kode}-{pasal}", "items": items}


class TestPaketGold(unittest.TestCase):
    def test_xlsx_tanpa_nama_dan_bolak_balik(self):
        from openpyxl import load_workbook
        rek = [
            _d("1111", 8, [{"no": 1, "label": "人員變動別", "value": "會計主管"},
                           {"no": 3, "label": "舊任者姓名、級職及簡歷", "value": "王小明/經理"},
                           {"no": 8, "label": "其他應敘明事項", "value": "李大華將退休"}]),
            _d("2222", 20, [{"no": 5, "label": "交易總金額(仟元)", "value": "1,000,000"}]),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            x = os.path.join(tmp, "g.xlsx")
            pg.buat_xlsx(rek, x)
            wb = load_workbook(x)
            teks = " ".join(str(c.value) for ws in wb for row in ws.iter_rows() for c in row)
            self.assertNotIn("王小明", teks)
            self.assertNotIn("李大華", teks)
            self.assertIn("會計主管", teks)
            ws = wb["Label"]
            kepala = [c.value for c in ws[1]]
            ws.cell(3, kepala.index("keputusan") + 1, "terbit")
            ws.cell(3, kepala.index("input") + 1, "capex")
            ws.cell(3, kepala.index("nilai_juta_ntd") + 1, "1000")
            ws.cell(3, kepala.index("menit") + 1, "4")
            wb.save(x)
            c = os.path.join(tmp, "g.csv")
            self.assertEqual(pg.ke_csv(x, c), 1)
            g = muat_gold(c)
            self.assertEqual(len(g), 1)


if __name__ == "__main__":
    unittest.main()
