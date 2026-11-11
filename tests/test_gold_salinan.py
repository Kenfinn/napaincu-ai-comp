"""eval/gold_dokumen.json: salinan gold set yang masuk repo. Tidak boleh memuat nama orang,
dan evaluasi harus bisa memakainya tanpa data server."""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from app import gold  # noqa: E402

SALINAN = os.path.join(ROOT, "eval", "gold_dokumen.json")


class TestSalinanGold(unittest.TestCase):
    def test_tanpa_butir_nama(self):
        with open(SALINAN, encoding="utf-8") as f:
            s = json.load(f)
        self.assertEqual(len(s["pengumuman"]), 46)
        for d in s["pengumuman"]:
            for b in d["items"]:
                for x in [b] + b.get("sub", []):
                    lbl = (x.get("label_lengkap") or "") + (x.get("label") or "")
                    self.assertNotIn("姓名", lbl, d["source_url"])
                    self.assertNotIn("發言人電話", lbl)
                    if d.get("clause") in gold.PASAL_ORANG and x.get("value"):
                        self.assertTrue(any(a in lbl for a in gold.LABEL_AMAN_ORANG + gold.LABEL_AMAN_AUDITOR),
                                        (d["source_url"], lbl))

    def test_untuk_snapshot_buang_nama(self):
        d = {"clause": 8, "items": [
            {"no": "1", "label": "人員變動別", "value": "財務主管"},
            {"no": "3", "label": "舊任者姓名及簡歷", "value": "王小明"},
            {"no": "9", "label": "其他應敘明事項", "value": "由王小明代理"}]}
        s = json.dumps(gold.untuk_snapshot(d), ensure_ascii=False)
        self.assertIn("財務主管", s)
        self.assertNotIn("王小明", s)

    def test_evaluasi_pakai_salinan_tanpa_data(self):
        import evaluasi
        with tempfile.TemporaryDirectory() as tmp:
            gold_csv = os.path.join(tmp, "gold.csv")
            with open(SALINAN, encoding="utf-8") as f:
                url = json.load(f)["pengumuman"][0]["source_url"]
            with open(gold_csv, "w", encoding="utf-8") as f:
                f.write("source_url,kode,harus_terbit,keputusan\n" + f"{url},x,tidak,arsip\n")
            import contextlib
            import io
            from app import pasar
            asli = pasar.kapitalisasi_dari_cache
            self.addCleanup(setattr, pasar, "kapitalisasi_dari_cache", asli)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                kode = evaluasi.main(["--gold", gold_csv, "--mode", "aturan"])
            self.assertEqual(kode, 0)
            self.assertIn("salinan gold", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
