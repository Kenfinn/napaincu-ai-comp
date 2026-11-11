"""HTTP 402 (saldo prabayar Gemini habis) langsung gagal dengan pesan jelas, tanpa ulang atau model cadangan."""
import io
import unittest
import urllib.error
from unittest import mock

from app import config
from app.agent import llm


class TestSaldo402(unittest.TestCase):
    def test_402_sekali_panggil_lalu_gagal(self):
        n = {"panggil": 0}

        def palsu(instruksi, dokumen):
            n["panggil"] += 1
            raise urllib.error.HTTPError("u", 402, "Payment Required", {}, io.BytesIO(b"{}"))
        with mock.patch.object(llm, "_panggil_gemini", side_effect=palsu), \
             mock.patch.object(config, "API_KEY", "uji"), \
             mock.patch.object(config, "MODEL_CADANGAN", ["model-lain"]), \
             mock.patch.object(llm.time, "sleep"):
            with self.assertRaises(llm.GagalModel) as k:
                llm._tanya_model("i", "d")
        self.assertIn("402", str(k.exception))
        self.assertIn("prabayar", str(k.exception))
        self.assertEqual(n["panggil"], 1)


if __name__ == "__main__":
    unittest.main()
