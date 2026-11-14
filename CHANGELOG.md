# Changelog

## 1.2.0 · 14 Nov 2026

- English API paths: `/health`, `/check`, `/api/alerts`, `/api/traces/{id}`,
  `/api/valuation/{code}`, `/api/stocks/{code}/financials`, `/api/thresholds`, `/api/search`,
  `/api/ask`, `/api/ask/traces/{id}`, `/api/import`. The old Indonesian paths (`/sehat`,
  `/periksa`, `/api/peringatan`, `/api/jejak`, `/api/valuasi`, `/api/saham/.../keuangan`,
  `/api/ambang`, `/api/cari`, `/api/tanya`, `/api/impor`) stay as hidden aliases, so nothing
  breaks. JSON field names are unchanged.
- `/docs` (OpenAPI) is now in English and lists only the JSON API; HTML pages are hidden from it.
  API error messages are in English.
- `POST /api/ask` accepts English body fields (`question`, `language`, `history`, `context`,
  `type`) next to the old ones; `POST /api/import` accepts header `X-Access-Code` next to
  `X-Kode-Akses`.
- Pages, `chat.js`, `ui.js`, the Docker health check and `scripts/kirim_riwayat.py` use the new
  paths.
- README rewritten (architecture diagrams, API reference with examples, tech stack) in English,
  with translations in 繁體中文 (`README.zh-TW.md`), Bahasa Indonesia (`README.id.md`) and
  Tiếng Việt (`README.vi.md`).
- Tests: `tests/test_api_inggris.py` (new paths, legacy aliases, English OpenAPI); 301 tests.

## 1.1.0 · 13 Nov 2026

- Ask FEAF slide-over panel on every page (`_panel_chat.html`, `app/static/chat.js`,
  `app/static/chat.css`) with page-aware suggestion chips and `sessionStorage` conversation
  persistence across pages.
- Multi-turn chat API (`POST /api/tanya` accepting `riwayat` and `konteks`) with 32-hex
  HMAC-SHA256 signing (`tanda(id, jawaban)` via `SENTINEL_CHAT_RAHASIA`); unsigned or altered
  assistant turns and injected user turns are dropped and logged in the trace.
- Follow-up question resolution without repeating the stock code (from question, page context,
  last verified turn, or announcement prefix) and conversation **Recap** (`recap` /
  `recap_template` verified against signed assistant turns).
- Six read-only menu tools (`feed`, `peringatan`, `jejak`, `review`, `ambang`, `watchlist`)
  alongside the six stock tools, with internal navigation links (`tautan`) and zero PII / zero
  file mutation.
- Multi-turn chat evaluation (`eval/chat_percakapan.csv`, `scripts/evaluasi.py --chat-percakapan`:
  36/36 turns and 12/12 scenarios in three languages on the rule path) and 7 mandatory
  conversation security tests (`tests/test_chat_percakapan.py`).
- UI and accessibility refinements across feed, stock detail, alert detail, valuation, review,
  thresholds, watchlist, trace, and plain-language hold reasons.
- QA hardening: offline MOPS citation fallback on empty financials, `[hidden]` CSS visibility
  guarantee, standalone `401` lock page (`POST /akses` + signed access cookie), thread-safe chat
  worker offloading and LLM/review locking, word-boundary narration checker, watchlist cached
  prices, and localized fallback trace labels.

## 1.0.0 · 12 Nov 2026 · finalist package (AAIC 2026)

The version submitted with the finalist package. Evaluation numbers in the README and
`docs/laporan-evaluasi.md` were measured on this code line.

- Agent pipeline: clause screen → triage → extraction (Gemini 3.6 Flash, rule-based fallback)
  → deterministic recompute → deterministic checker. Lanes for valuation, risk, capital,
  quarterly report, severe and governance clauses.
- Automatic DCF for non-financial issuers, built for every issuer whose filing needs it.
- Ask FEAF chat page: answers only from tools, every number checked, advice refused.
- Review queue, 👍/👎 thresholds, watchlist, stock pages with six tabs, three languages.
- Evaluation: gold set (46 filings), attack set (72 cases), chat set (52 questions),
  operations report, reproducible offline from `eval/gold_dokumen.json`.
