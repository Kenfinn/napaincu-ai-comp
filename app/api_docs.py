"""Dokumentasi API interaktif (/docs) tiga bahasa: en (bawaan), zh (繁體中文), id.

Teks skema OpenAPI ditimpa dari tabel di bawah, jadi docstring handler (boleh Indonesia)
tidak pernah bocor ke /docs. Path, metode, nama parameter dan nama field JSON tidak berubah.
"""
from __future__ import annotations

import copy

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse

LANGS = ("en", "zh", "id")

TITLE = {
    "en": "FEAF · Agentic AI Investment Assistant",
    "zh": "FEAF · 代理式 AI 投資助理",
    "id": "FEAF · Asisten Investasi AI Agentik",
}
DESC = {
    "en": "Agent that watches official Taiwan exchange filings (MOPS), recalculates the valuation when "
          "a filing changes an input, and refuses to publish any number that cannot be traced back to "
          "its source document. Read-only JSON API (except the two write endpoints `POST /check` and "
          "`POST /api/import`). Legacy Indonesian paths still work but are hidden here.",
    "zh": "監看臺灣交易所官方重大訊息（MOPS）的代理程式：當公告改變估值輸入時重新計算估值，"
          "且拒絕發布任何無法追溯到來源文件的數字。除 `POST /check` 與 `POST /api/import` 兩個寫入端點外，"
          "皆為唯讀 JSON API。舊的印尼文路徑仍可使用，但不在此顯示。",
    "id": "Agen yang memantau pengumuman resmi bursa Taiwan (MOPS), menghitung ulang valuasi saat "
          "pengumuman mengubah input, dan menolak menerbitkan angka yang tidak bisa ditelusuri ke "
          "dokumen sumber. API JSON hanya-baca (kecuali dua endpoint tulis `POST /check` dan "
          "`POST /api/import`). Path lama berbahasa Indonesia masih berfungsi tetapi disembunyikan di sini.",
}
SWITCH = "**Language:** [English](/docs?lang=en) · [繁體中文](/docs?lang=zh) · [Bahasa Indonesia](/docs?lang=id)"

# kunci tag -> nama per bahasa, deskripsi per bahasa
TAGS = [
    ("System", {"en": "System", "zh": "系統", "id": "Sistem"},
     {"en": "Health check and pulling new filings.", "zh": "健康檢查與抓取新公告。",
      "id": "Pemeriksaan kesehatan dan penarikan pengumuman baru."}),
    ("Alerts & traces", {"en": "Alerts & traces", "zh": "警示與軌跡", "id": "Peringatan & jejak"},
     {"en": "Processing result of every filing and its full operation trace.",
      "zh": "每則公告的處理結果與完整操作軌跡。", "id": "Hasil pemrosesan tiap pengumuman dan jejak operasinya."}),
    ("Valuation & financials", {"en": "Valuation & financials", "zh": "估值與財報", "id": "Valuasi & keuangan"},
     {"en": "DCF calculator output and financial statement tables.",
      "zh": "DCF 計算器輸出與財務報表。", "id": "Keluaran kalkulator DCF dan tabel laporan keuangan."}),
    ("Review & thresholds", {"en": "Review & thresholds", "zh": "審查與門檻", "id": "Review & ambang"},
     {"en": "Human review queue and per-clause triage thresholds.",
      "zh": "人工審查佇列與各條款的分流門檻。", "id": "Antrean review manusia dan ambang triase per pasal."}),
    ("Watchlist & search", {"en": "Watchlist & search", "zh": "自選股與搜尋", "id": "Watchlist & pencarian"},
     {"en": "Watched stock codes and issuer search.", "zh": "追蹤中的股票代號與公司搜尋。",
      "id": "Kode saham yang dipantau dan pencarian emiten."}),
    ("Ask FEAF", {"en": "Ask FEAF", "zh": "詢問 FEAF", "id": "Tanya FEAF"},
     {"en": "Chat answers built only from read-only tool results; every number is checked.",
      "zh": "回答僅取自唯讀工具結果，每個數字都經過檢查。",
      "id": "Jawaban chat hanya dari hasil alat hanya-baca; setiap angka diperiksa."}),
    ("Import", {"en": "Import", "zh": "匯入", "id": "Impor"},
     {"en": "Write endpoint for MOPS history pulled on a Taiwan network.",
      "zh": "寫入端點，用於匯入在臺灣網路上抓取的 MOPS 歷史資料。",
      "id": "Endpoint tulis untuk riwayat MOPS yang ditarik di jaringan Taiwan."}),
]

# (metode, path) -> (kunci tag, {lang: (summary, description)})
OPS = {
    ("get", "/health"): ("System", {
        "en": ("Health check", "Returns service status: version, code hash, filing count, last run time, model in use and fallback reasons."),
        "zh": ("健康檢查", "回傳服務狀態：版本、程式碼雜湊、公告數量、上次執行時間、使用中的模型與備援原因。"),
        "id": ("Cek kesehatan", "Mengembalikan status layanan: versi, hash kode, jumlah pengumuman, waktu jalan terakhir, model yang dipakai dan alasan fallback.")}),
    ("post", "/check"): ("System", {
        "en": ("Pull and reprocess filings", "Pulls the latest filings for the watchlist and reprocesses them. This is a browser form post and answers with a redirect."),
        "zh": ("抓取並重新處理公告", "為自選股抓取最新公告並重新處理。這是瀏覽器表單送出，會回應重新導向。"),
        "id": ("Tarik dan proses ulang pengumuman", "Menarik pengumuman terbaru untuk watchlist lalu memprosesnya ulang. Ini form post dari browser dan dijawab dengan redirect.")}),
    ("get", "/api/alerts"): ("Alerts & traces", {
        "en": ("List alerts", "Processing result of every filing. `status` is `terbit` (published), `ditahan` (held for review) or `dilewati` (archived)."),
        "zh": ("警示清單", "每則公告的處理結果。`status` 為 `terbit`（已發布）、`ditahan`（待人工審查）或 `dilewati`（已歸檔）。"),
        "id": ("Daftar peringatan", "Hasil pemrosesan setiap pengumuman. `status` bernilai `terbit` (diterbitkan), `ditahan` (ditahan untuk review) atau `dilewati` (diarsipkan).")}),
    ("get", "/api/traces/{id}"): ("Alerts & traces", {
        "en": ("Get filing trace", "Full operation trace of one filing: every stage, model call, token count, latency and checker verdict. Returns 404 if the id is unknown."),
        "zh": ("取得公告軌跡", "單一公告的完整操作軌跡：每個階段、模型呼叫、token 數、延遲與檢查結果。若 id 不存在則回傳 404。"),
        "id": ("Ambil jejak pengumuman", "Jejak operasi lengkap satu pengumuman: tiap tahap, panggilan model, jumlah token, latensi dan putusan pemeriksa. 404 jika id tidak dikenal.")}),
    ("get", "/api/valuation/{code}"): ("Valuation & financials", {
        "en": ("Get DCF valuation", "Output of the DCF calculator for one issuer: cost of capital, reverse-DCF implied growth, sensitivity and the source of every input. Returns 404 for an unknown code or when no valuation file exists yet."),
        "zh": ("取得 DCF 估值", "單一公司的 DCF 計算器輸出：資金成本、反向 DCF 隱含成長率、敏感度分析與每項輸入的來源。代號不存在或尚無估值檔案時回傳 404。"),
        "id": ("Ambil valuasi DCF", "Keluaran kalkulator DCF untuk satu emiten: biaya modal, pertumbuhan tersirat reverse-DCF, sensitivitas, dan sumber setiap input. 404 untuk kode tidak dikenal atau bila belum ada berkas valuasi.")}),
    ("get", "/api/stocks/{code}/financials"): ("Valuation & financials", {
        "en": ("Get financial statements", "Financial statement table of one issuer: income statement, balance sheet or cash flow, quarterly or yearly, as values or year-over-year change."),
        "zh": ("取得財務報表", "單一公司的財務報表：損益表、資產負債表或現金流量表，可選季或年，顯示數值或年增率。"),
        "id": ("Ambil laporan keuangan", "Tabel laporan keuangan satu emiten: laba rugi, neraca atau arus kas, kuartalan atau tahunan, sebagai nilai atau perubahan tahun-ke-tahun.")}),
    ("get", "/api/review"): ("Review & thresholds", {
        "en": ("Review queue", "Filings HELD FOR REVIEW and the history of human decisions."),
        "zh": ("審查佇列", "待人工審查（HELD FOR REVIEW）的公告與人工決定的歷史紀錄。"),
        "id": ("Antrean review", "Pengumuman yang DITAHAN UNTUK REVIEW dan riwayat keputusan manusia.")}),
    ("get", "/api/thresholds"): ("Review & thresholds", {
        "en": ("Triage thresholds", "Triage threshold per clause, where it came from (thumbs up/down feedback) and its change history."),
        "zh": ("分流門檻", "各條款的分流門檻、其來源（👍/👎 回饋）與變更歷史。"),
        "id": ("Ambang triase", "Ambang triase per pasal, asalnya (umpan balik 👍/👎) dan riwayat perubahannya.")}),
    ("get", "/api/watchlist"): ("Watchlist & search", {
        "en": ("Get watchlist", "Watched stock codes and the status of the last pull."),
        "zh": ("取得自選股", "追蹤中的股票代號與上次抓取的狀態。"),
        "id": ("Ambil watchlist", "Kode saham yang dipantau dan status penarikan terakhir.")}),
    ("get", "/api/search"): ("Watchlist & search", {
        "en": ("Search issuers", "Search issuers by numeric code or by name."),
        "zh": ("搜尋公司", "以數字代號或名稱搜尋公司。"),
        "id": ("Cari emiten", "Cari emiten berdasarkan kode angka atau nama.")}),
    ("post", "/api/ask"): ("Ask FEAF", {
        "en": ("Ask FEAF", "Answers a question using only read-only tool results; every number in the answer is checked against them, and buy/sell advice is refused. Body fields `question`, `language`, `history`, `context`, `type` (legacy Indonesian names are also accepted)."),
        "zh": ("詢問 FEAF", "僅使用唯讀工具結果回答問題，答案中的每個數字都會與結果核對，並拒絕提供買賣建議。請求欄位：`question`、`language`、`history`、`context`、`type`（亦接受舊的印尼文欄位名稱）。"),
        "id": ("Tanya FEAF", "Menjawab pertanyaan hanya dari hasil alat hanya-baca; setiap angka dalam jawaban dicocokkan dengannya dan saran beli/jual ditolak. Field body `question`, `language`, `history`, `context`, `type` (nama lama berbahasa Indonesia juga diterima).")}),
    ("get", "/api/ask/traces/{id}"): ("Ask FEAF", {
        "en": ("Get Ask FEAF trace", "Trace of one Ask FEAF answer. Returns 404 if not found."),
        "zh": ("取得 Ask FEAF 軌跡", "單一 Ask FEAF 回答的軌跡。找不到時回傳 404。"),
        "id": ("Ambil jejak Tanya FEAF", "Jejak satu jawaban Tanya FEAF. 404 jika tidak ditemukan.")}),
    ("post", "/api/import"): ("Import", {
        "en": ("Import filing history", "Imports MOPS filing history pulled from a laptop on a Taiwan network (used by scripts/kirim_riwayat.py). Requires header `X-Access-Code` (legacy `X-Kode-Akses` also accepted) equal to the server access code; import is disabled when the server has none. Body is a JSON array, max 25 MB."),
        "zh": ("匯入公告歷史", "匯入在臺灣網路的筆電上抓取的 MOPS 公告歷史（由 scripts/kirim_riwayat.py 使用）。需帶 `X-Access-Code` 標頭（亦接受舊的 `X-Kode-Akses`），值須等於伺服器的存取碼；伺服器未設定存取碼時匯入功能關閉。請求本文為 JSON 陣列，上限 25 MB。"),
        "id": ("Impor riwayat pengumuman", "Mengimpor riwayat pengumuman MOPS yang ditarik dari laptop di jaringan Taiwan (dipakai scripts/kirim_riwayat.py). Wajib header `X-Access-Code` (`X-Kode-Akses` lama juga diterima) sama dengan kode akses server; impor ditutup jika server tidak punya kode. Body berupa array JSON, maks 25 MB.")}),
}

# nama parameter -> deskripsi per bahasa (berlaku per (metode, path) bila ada, kalau tidak per nama)
PARAMS = {
    "code": {"en": "Stock code (4-6 characters, e.g. `2330`).", "zh": "股票代號（4–6 碼，例如 `2330`）。",
             "id": "Kode saham (4-6 karakter, mis. `2330`)."},
    "id": {"en": "Filing id from `GET /api/alerts` (e.g. `2330-2026-09-18-1`), or answer id from `POST /api/ask`.",
           "zh": "公告 id 取自 `GET /api/alerts`（例如 `2330-2026-09-18-1`），或回答 id 取自 `POST /api/ask`。",
           "id": "Id pengumuman dari `GET /api/alerts` (mis. `2330-2026-09-18-1`), atau id jawaban dari `POST /api/ask`."},
    "lap": {"en": "Statement: `lr` income statement, `neraca` balance sheet, `arus` cash flow.",
            "zh": "報表：`lr` 損益表、`neraca` 資產負債表、`arus` 現金流量表。",
            "id": "Laporan: `lr` laba rugi, `neraca` neraca, `arus` arus kas."},
    "per": {"en": "Period: `q` quarterly, `y` yearly.", "zh": "期間：`q` 季、`y` 年。",
            "id": "Periode: `q` kuartalan, `y` tahunan."},
    "mode": {"en": "Display: `nilai` values, `yoy` year-over-year change.", "zh": "顯示方式：`nilai` 數值、`yoy` 年增率。",
             "id": "Tampilan: `nilai` nilai, `yoy` perubahan tahun-ke-tahun."},
    "q": {"en": "Search text: numeric stock code or part of the company name.", "zh": "搜尋文字：數字股票代號或公司名稱的一部分。",
          "id": "Teks pencarian: kode saham angka atau sebagian nama perusahaan."},
}
RESP = {
    "200": {"en": "Successful response", "zh": "成功", "id": "Respons sukses"},
    "422": {"en": "Validation error", "zh": "驗證錯誤", "id": "Kesalahan validasi"},
}
BODY = {
    ("post", "/api/import"): {"en": "JSON array of filing records (max 25 MB).", "zh": "公告紀錄的 JSON 陣列（上限 25 MB）。",
                              "id": "Array JSON berisi catatan pengumuman (maks 25 MB)."},
    ("post", "/api/ask"): {"en": "JSON object: `question` (required), `language` (`en|zh|id`), `history`, `context`, `type`.",
                           "zh": "JSON 物件：`question`（必填）、`language`（`en|zh|id`）、`history`、`context`、`type`。",
                           "id": "Objek JSON: `question` (wajib), `language` (`en|zh|id`), `history`, `context`, `type`."},
}
HEADERS = {"X-Access-Code": {"en": "Server access code (legacy name `X-Kode-Akses` also accepted).",
                             "zh": "伺服器存取碼（亦接受舊名稱 `X-Kode-Akses`）。",
                             "id": "Kode akses server (nama lama `X-Kode-Akses` juga diterima)."}}

_cache: dict[str, dict] = {}


def lang_of(raw: str | None) -> str:
    return raw if raw in LANGS else "en"


def schema(app: FastAPI, lang: str) -> dict:
    lang = lang_of(lang)
    if lang in _cache:
        return _cache[lang]
    s = copy.deepcopy(app.openapi_schema or _base(app))
    s["info"]["title"] = TITLE[lang]
    s["info"]["description"] = DESC[lang] + "\n\n" + SWITCH
    s["tags"] = [{"name": n[lang], "description": d[lang]} for _, n, d in TAGS]
    tagname = {k: n[lang] for k, n, _ in TAGS}
    for path, item in s["paths"].items():
        for method, op in item.items():
            ent = OPS.get((method, path))
            if ent:
                key, txt = ent
                op["tags"] = [tagname[key]]
                op["summary"], op["description"] = txt[lang]
            for p in op.get("parameters", []):
                if p["in"] == "header":
                    p["description"] = HEADERS.get(p["name"], {}).get(lang, p.get("description", ""))
                elif p["name"] in PARAMS:
                    p["description"] = PARAMS[p["name"]][lang]
            for code, r in op.get("responses", {}).items():
                if code in RESP:
                    r["description"] = RESP[code][lang]
            if (method, path) in BODY:
                op.setdefault("requestBody", {"content": {"application/json": {"schema": {}}}})["description"] = BODY[(method, path)][lang]
            if (method, path) == ("post", "/api/import"):
                op.setdefault("parameters", []).append(
                    {"name": "X-Access-Code", "in": "header", "required": True,
                     "schema": {"type": "string"}, "description": HEADERS["X-Access-Code"][lang]})
    _cache[lang] = s
    return s


def _base(app: FastAPI) -> dict:
    from fastapi.openapi.utils import get_openapi
    app.openapi_schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    return app.openapi_schema


def install(app: FastAPI) -> None:
    """Pasang /openapi.json (?lang=) dan /docs (?lang=). Panggil setelah semua router terpasang."""
    @app.get("/openapi.json", include_in_schema=False)
    def openapi_json(lang: str = "en"):
        return JSONResponse(schema(app, lang))

    @app.get("/docs", include_in_schema=False)
    def docs(lang: str = "en") -> HTMLResponse:
        lang = lang_of(lang)
        return get_swagger_ui_html(openapi_url=f"/openapi.json?lang={lang}", title=TITLE[lang] + " - API docs")
