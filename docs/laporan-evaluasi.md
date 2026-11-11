# FEAF agent evaluation (AAIC 2026, Appendix 2)

Prepared 11 Nov 2026. All numbers below come from saved reports in `eval/hasil/` or from the
live server (`/sehat`, `/api/peringatan`, `/api/jejak/{id}`). Commands to reproduce are given
for each section. Internal working notes (Indonesian): `docs/hasil-gold-set.md`,
`docs/laporan-keamanan.md`.

## 1. Task, success definition, environment

**Task.** For each material filing (MOPS 重大訊息), decide whether it is published as an alert,
held for a person, or archived, and publish only numbers that can be traced to the filing.

**Success** for one filing = the agent makes the same publish / hold / archive decision as a
finance expert **and** publishes no wrong number. A wrong number is any published value that
differs from the expert's by more than 0.5%, or that could not be converted to NTD.

**Environments.**

| | Rule path | Model path |
|---|---|---|
| Where | Developer machine, Python 3.12 | Production server (Docker on Dokploy, 1 worker), `/data` volume |
| Reasoner for stages 1–2 | Rule-based (`screen.py`, `extract.py`) | Gemini `gemini-3.6-flash`, temperature 0, paid tier; backup `gemini-3.5-flash` |
| Stages 0, 3, 4 | Deterministic | Deterministic (same code) |
| Prompt version | — | `2026-11-10.1` |

## 2. Gold set (46 real filings)

46 real filings from 9 Nov 2026, about 7 per lane (valuation, risk, capital, quarterly report,
severe, governance), labelled by a finance team member (decision, signal level, number, item,
minutes). Filings ship in `eval/gold_dokumen.json` (name-bearing items removed) so the run
reproduces anywhere:

```bash
python3 scripts/evaluasi.py --simpan                 # rule path
python3 scripts/evaluasi.py --tanpa-cache --simpan   # adds the model path when GEMINI_API_KEY is set
```

**Baselines.** (a) Manual work: 20–30 minutes per filing according to the labeller (25 used),
about 1,150 analyst-minutes for 46 filings. (b) "Without checker": the same screen and
extractor, no checker and no hold rules, so anything extracted is published, as a plain LLM
pipeline would.

### 2.1 Official result (rule path, measured before any tuning)

Report: `eval/hasil/evaluasi-20261111T084547Z.md`.

| Metric | FEAF agent | Without checker |
|---|---|---|
| Wrong numbers published | **0/46** | 5/46 |
| Decision matches expert | 41/46 (89%) | 15/46 (33%) |
| Signal level matches expert (moderate profile) | 21/29 (72%) | 0/29 |
| Held for a person (human intervention) | 13/46 (28%) | 33/46 (72%) |

### 2.2 Model path on the server (after tuning, in-sample)

Run on the production server, 11 Nov 09:39 UTC, with fresh model calls (`--tanpa-cache`). The
thresholds had already been tuned on these same 46 filings, so decision accuracy here is
**in-sample** and is not reported as accuracy; the value of this run is the model-path safety,
latency, token and cost figures.

| Metric | Rule path | Gemini 3.6 Flash | Without checker (Gemini) |
|---|---|---|---|
| Wrong numbers published | 0/46 | **0/46** | 5/46 (11%) |
| 3-way decision matches expert (in-sample) | 43/46 | 42/46 | 19/46 |
| Signal level matches expert (in-sample) | 29/29 | 29/29 | 0/29 |
| Held for a person | 11/46 (24%) | 12/46 (26%) | 31/46 (67%) |
| Model calls | 0 | 5 | 37 |
| Tokens in / out | 0 / 0 | 7,212 / 392 | 41,280 / 435 |
| Retries / fallbacks to rules | 0 / 5 (no key by design) | 0 / 0 | 0 / 0 |
| Latency per filing, mean / max | 0 / 2 ms | 699 ms / 9.9 s | 4.3 s / 22.7 s |

Only clause-20 filings (valuation lane) call the model; risk, capital, report, severe and
governance lanes are parsed deterministically, which is why the model path makes 5 calls for
46 filings.

**Cost.** At the paid-tier price of Gemini 3.6 Flash (USD 0.75 per million input tokens,
USD 3.75 per million output tokens, introductory price until 31 Dec 2026), the model path cost
**USD 0.0069 for 46 filings** (USD 0.0014 per model call). At the standard price from 2027
(1.50 / 7.50) it would be USD 0.014. The "without checker" pipeline sends every filing that passes the
clause screen to the model, whatever the lane, and costs USD 0.033. This run did not yet count thinking tokens
separately; the figure is a lower bound. Thinking tokens are now recorded (`token_pikir`) and
priced as output from the next run on.

**Where the model path differs from the rule path.** One filing the expert archived was held
by the model path (42 vs 43). Holding is the safe failure: it costs a person a review, never a
wrong alert.

## 3. Attack set

`python3 scripts/uji_serangan.py --simpan` · report `eval/hasil/serangan-2026-11-10.md`.

12 attack types built on real filings (instruction injected in notes or inside a value,
invented numbers, invented quotes, fake labels, unit swap, foreign currency, extreme
magnitude, and two variants from real filing patterns), 72 cases, run against the rule
reasoner and against a simulated model that obeys every injection.

| | Result |
|---|---|
| Attacker numbers published | **0/72** |
| Checks that caught them | label, quote, digits, currency, unit, magnitude |
| Injection attempts logged in the trace | all |

## 4. Ask FEAF (chat)

`python3 scripts/evaluasi.py --chat --simpan`. 52 questions in three languages (`eval/chat_uji.csv`):
25 data questions that must be answered from tools with sources, 27 that must be refused
(buy/sell advice, price prediction, personal data, injected instructions, no stock code).

| Metric | Gemini 3.6 Flash (server, 11 Nov 09:52 UTC) | Rule path |
|---|---|---|
| Correct, all cases (as scored at run time) | 50/52 (96%) | 52/52 |
| Data questions answered with source and passing the number check | 23/25 | 25/25 |
| Out-of-scope, advice and injection questions refused | **27/27** | 27/27 |
| Recommendation words that reached the user | **0** | 0 |
| Answer path | model 23, template after checker rejection 2, refused 27 | template 25, refused 27 |
| Latency mean / max | 4.4 s / 17.9 s | 0.2 s / 5.1 s |
| Tool calls / model calls | 54 / 69 | 26 / 0 |

**The two misses were checker false positives, not wrong answers.** In both cases the checker
rejected Gemini's answer and the user received the sourced template answer instead:

| Question | Why the checker rejected the model answer |
|---|---|
| "Any recent announcements from 2330?" | Gemini converted the ROC year 民國108 to 2019, a number not literally in the tool output |
| "Recent capital reduction or dividend filings for 2330?" | Gemini wrote "buy back" (share repurchase), which matched the forbidden word "buy" |

Both were fixed on 11 Nov: a Gregorian year equal to an ROC year in the tool output + 1911 is
accepted, and "buy back" / "beli kembali" are no longer treated as advice (`app/chat.py`, tests in
`tests/test_chat_b1.py`). Scoring now judges a fallback by the check on the answer the user
actually received, and reports the number of rejected model answers on its own line. The
50/52 above is the result as measured; the fix has not been re-run with Gemini yet.

## 5. Operations on the live server

`GET /sehat`, 11 Nov 09:22 UTC: 1,106 real filings processed since the volume was mounted,
model `gemini-3.6-flash`, no model error, no fallback.

| Outcome | Filings | Share |
|---|---|---|
| Published | 587 | 53% |
| Archived (clause not affecting valuation, below materiality, intra-group) | 387 | 35% |
| Held for a person | 132 | **12%** (human intervention rate) |

Held, by reason (error categories):

| Reason | Filings | Action taken |
|---|---|---|
| Issuer has no valuation model yet | 59 | Since 11 Nov the server builds automatic valuations for these issuers, 5 per 10-minute cycle (FinMind quota) |
| No number with a traceable source sentence | 35 | Correct behaviour: nothing to publish safely |
| Risk signal above the "serious" threshold | 31 | By design: a person confirms serious signals |
| Label, unit or currency check failed | 4 | Two were parser gaps, fixed (see 6); USD amounts stay held by design |
| Severe clause (1, 3, 40) | 3 | Always held, by team decision |

## 6. Operation trace (auditable example)

Saved trace: `eval/hasil/jejak-contoh-2330-2026-11-10-211853.json`, live at
`/jejak/2330-2026-11-10-211853`. TSMC board approval of a capital budget (clause 20).

| Step | What happened |
|---|---|
| Fetch | Pulled from TWSE OpenAPI 11 Nov 02:35 UTC; no personal field present |
| Shape check | 31 items, clause 第20款 |
| 0 · Clause screen | Clause 20 → valuation lane, possible inputs capex, cash |
| 1–2 · Triage and extract | `gemini-3.6-flash`, prompt `2026-11-10.1`, answer from cache (original call 4,203 tokens in, 778 out); 4 amounts found, all **US$**, unit 佰萬元 |
| Triage confidence | 0.55: no amount convertible to NTD |
| 4a · Checker | Currency check failed: USD amount, no exchange rate in the model, not converted silently |
| End | HELD FOR REVIEW with the reasons above |

The trace also exposed two checker gaps that held valid filings: the model prefixes the item
number to the label (`5. 交易單位數量…`), and 佰萬元 is a variant spelling of 百萬元 (million).
Both were fixed on 11 Nov (`app/agent/extract.py`, tests in
`tests/test_label_satuan_d5.py`). The USD hold remains, as intended.

## 7. Known limitations, worst case, recovery

- **Out-of-sample accuracy is not yet measured.** The official 41/46 is pre-tuning; post-tuning
  numbers are in-sample. A fresh set of 15–20 blind-labelled filings is the next step.
- **No currency conversion**: non-NTD amounts are held.
- **Financial companies** get no DCF; their clause-20 filings are held.
- **Today's filings only** from outside Taiwan; older history needs a pull from a Taiwan network.

| Worst case | What happens | Recovery |
|---|---|---|
| Model returns an invented or injected number | Checker fails the claim; nothing published | Held with the failing check named in the trace |
| Model unavailable, rate-limited or out of credit (402) | Retries, then backup model, then rule reasoner; 402 is not retried | Reported in `/sehat` (`galat_model_terakhir`, `sebab_cadangan`); next cycle retries |
| Run takes too long | 90-second / 40-call cap per run; remaining filings use the rule reasoner | Answered by the model on the next cycles; answers are cached |
| Server restart or redeploy | Data, traces and review decisions live in the `/data` volume | `/sehat` `versi_kode` confirms which code runs |
