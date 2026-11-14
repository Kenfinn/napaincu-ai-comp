import re
import unittest

from fastapi.testclient import TestClient

from app import main

C = TestClient(main.app)
ID_WORDS = re.compile(r"\b(pengumuman|dipakai|wajib|berkas|emiten|tidak|dengan|untuk|atau|yang|dan|adalah)\b", re.I)


def texts(sch):
    out = [sch["info"]["title"], sch["info"]["description"]]
    out += [t["name"] + " " + t["description"] for t in sch["tags"]]
    for item in sch["paths"].values():
        for op in item.values():
            out += [op.get("summary", ""), op.get("description", "")]
            out += [p.get("description", "") for p in op.get("parameters", [])]
            out += [r.get("description", "") for r in op.get("responses", {}).values()]
            out.append(op.get("requestBody", {}).get("description", ""))
    return out


class ApiDocsTest(unittest.TestCase):
    def test_english_default_has_no_indonesian(self):
        sch = C.get("/openapi.json").json()
        for t in texts(sch):
            plain = re.sub(r"`[^`]*`", "", t)
            self.assertIsNone(ID_WORDS.search(plain), t)
            self.assertFalse(re.search(r"[一-鿿]", plain.replace("繁體中文", "")), t)

    def test_every_operation_tagged_and_summarised(self):
        sch = C.get("/openapi.json").json()
        for path, item in sch["paths"].items():
            for op in item.values():
                self.assertTrue(op["summary"], path)
                self.assertTrue(op["tags"] and "default" not in op["tags"], path)

    def test_query_params_described(self):
        sch = C.get("/openapi.json").json()
        for path in ("/api/stocks/{code}/financials", "/api/search"):
            for p in sch["paths"][path]["get"]["parameters"]:
                self.assertTrue(p.get("description"), (path, p["name"]))

    def test_languages(self):
        en = C.get("/openapi.json").json()
        zh = C.get("/openapi.json?lang=zh").json()
        idn = C.get("/openapi.json?lang=id").json()
        xx = C.get("/openapi.json?lang=xx").json()
        self.assertEqual(xx, en)
        self.assertEqual(set(en["paths"]), set(zh["paths"]))
        self.assertEqual(set(en["paths"]), set(idn["paths"]))
        for item in zh["paths"].values():
            for op in item.values():
                self.assertTrue(re.search(r"[一-鿿]", op["summary"]))
        self.assertEqual(idn["paths"]["/api/alerts"]["get"]["summary"], "Daftar peringatan")
        self.assertIn("lap", [p["name"] for p in zh["paths"]["/api/stocks/{code}/financials"]["get"]["parameters"]])

    def test_docs_page(self):
        r = C.get("/docs")
        self.assertEqual(r.status_code, 200)
        self.assertIn("/openapi.json?lang=en", r.text)
        self.assertIn("lang=zh", C.get("/docs?lang=zh").text)
        self.assertIn("/docs?lang=id", C.get("/openapi.json").json()["info"]["description"])
        self.assertIn("/docs?lang=zh", C.get("/openapi.json").json()["info"]["description"])

    def test_docs_ignores_cookie(self):
        r = TestClient(main.app, cookies={"bahasa": "zh"}).get("/docs")
        self.assertIn("/openapi.json?lang=en", r.text)


if __name__ == "__main__":
    unittest.main()
