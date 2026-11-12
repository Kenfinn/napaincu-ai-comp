# Changelog

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
