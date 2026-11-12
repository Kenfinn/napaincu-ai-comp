# FEAF · Agentic AI Investment Assistant

An agent that watches official Taiwan exchange filings (MOPS 重大訊息), works out which
valuation input each filing touches, recalculates the valuation when the numbers change,
and **refuses to publish an alert** when a number cannot be traced back to the filing it
came from.

Built for the NAPAI Agentic AI Innovation Competition 2026 (AAIC 2026), SYSTEX track:
*Investment Intelligence & AI-Powered Stock Selection Agent*.

**Version 1.0.0** (git tag `v1.0.0`, finalist package). Changes: [`CHANGELOG.md`](CHANGELOG.md).
`GET /sehat` reports the running version.

> **Not a trading tool.** There is no broker connection and no order execution, and the agent
> gives no buy or sell advice. It screens, explains and cites; a person decides.

Results on a 46-filing gold set labelled by a finance team member (official numbers, measured
before any tuning): **0 wrong numbers published**, 41/46 publish/hold/archive decisions match
the expert, 13/46 sent to a person. Without the checker, 5 wrong numbers were published.
Details in [Evaluation](#evaluation).

---

## Run locally · 本機執行 · Menjalankan di lokal

### English

Requirements: Python 3.12 or newer, Git, internet access (TWSE/TPEx OpenAPI). No database.

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. On the first run the feed shows clearly marked sample
filings. Press **Check now** (or add a stock on **Watchlist**) to pull today's real
filings from TWSE/TPEx. The interface defaults to English; switch to 中文 or ID in the left menu.

Optional settings, set before `uvicorn`:

```bash
export GEMINI_API_KEY=...                 # without it the rule-based reasoner is used
export SENTINEL_MODEL=gemini-3.6-flash    # default
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # pull new filings every 10 minutes
export SENTINEL_KODE_AKSES=...            # require an access code for actions
```

On Windows PowerShell use `$env:GEMINI_API_KEY="..."` instead of `export`.
Run the tests with `python -m unittest discover -s tests` (no network needed).

### 繁體中文

需求：Python 3.12 以上、Git、可連線至證交所與櫃買中心 OpenAPI。不需要資料庫。

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows：.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

開啟 <http://127.0.0.1:8000>。第一次執行時，動態頁會顯示標示為「範例」的公告。按下
**立即檢查**（或在**自選股**加入股票）即可從證交所與櫃買中心取得今日的真實重大訊息。
介面預設為英文，可在左側選單切換為「中文」。

選用設定（在執行 `uvicorn` 前設定）：

```bash
export GEMINI_API_KEY=...                 # 未設定時改用規則推理
export SENTINEL_MODEL=gemini-3.6-flash    # 預設模型
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # 每 10 分鐘自動抓取新公告
export SENTINEL_KODE_AKSES=...            # 操作需輸入存取碼
```

Windows PowerShell 請改用 `$env:GEMINI_API_KEY="..."`。
執行測試：`python -m unittest discover -s tests`（不需網路）。

### Bahasa Indonesia

Kebutuhan: Python 3.12 atau lebih baru, Git, akses internet ke OpenAPI TWSE/TPEx. Tanpa database.

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Buka <http://127.0.0.1:8000>. Saat pertama dijalankan, feed menampilkan pengumuman contoh
yang diberi tanda jelas. Tekan **Periksa sekarang** (atau tambah saham di **Watchlist**) untuk
menarik pengumuman asli hari ini dari TWSE/TPEx. Tampilan bawaan berbahasa Inggris; ganti
ke 中文 atau ID di menu kiri.

Pengaturan opsional, diisi sebelum `uvicorn`:

```bash
export GEMINI_API_KEY=...                 # tanpa ini dipakai penalar aturan
export SENTINEL_MODEL=gemini-3.6-flash    # bawaan
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # tarik pengumuman baru tiap 10 menit
export SENTINEL_KODE_AKSES=...            # aksi butuh kode akses
```

Di Windows PowerShell pakai `$env:GEMINI_API_KEY="..."`, bukan `export`.
Tes: `python -m unittest discover -s tests` (tanpa jaringan).

### Pulling real filings

Open **Watchlist**, add a stock code, then press **Check now**. From a terminal:

```bash
python3 scripts/tarik.py                 # pull for the watchlist in data/watchlist.json
python3 scripts/tarik.py --ulang 600     # check every 10 minutes until Ctrl+C
```

The sources are the official TWSE (`t187ap04_L`) and TPEx (`mopsfin_t187ap04_O`) OpenAPI
endpoints. They carry the full text of today's material filings and are reachable from
outside Taiwan. They keep no history, so every pull is merged into `data/parsed/details.json`
without duplicates. Older history can only be pulled from MOPS on a Taiwan network
(`scripts/spike_mops.py` → `parse_mops.py` → `fetch_details.py`, see
[`docs/tarik-riwayat.md`](docs/tarik-riwayat.md)) and uploaded with `scripts/kirim_riwayat.py`.

### Deploy (Docker / Dokploy)

```bash
docker build -t feaf .
docker run -p 8000:8000 -v feaf-data:/data -e SENTINEL_TARIK_OTOMATIS_DETIK=600 feaf
```

Pulled filings, the watchlist, audit traces and review decisions live in the `/data` volume and
survive redeploys. `GET /sehat` is the health check; its `versi_kode` field is a hash of
`app/*.py`, so you can confirm the server runs the same code as your checkout
(`python3 -c "from app.main import VERSI_KODE; print(VERSI_KODE)"`). Full Dokploy steps:
[`docs/deploy-dokploy.md`](docs/deploy-dokploy.md).

### Tests

```bash
python3 -m unittest discover -s tests
```

269 tests, no network access needed. They include the attack set, multi-turn chat security, the
rule that API keys never reach a file, page or trace, and the rule that personal names never
reach the model or the gold-set export.

---

## Architecture

```
TWSE / TPEx OpenAPI (today)      MOPS history (Taiwan network)
            │                              │
            └──── scripts/tarik.py ────────┘   personal fields dropped before saving
                        │
                data/parsed/details.json
                        │
 [0] CLAUSE SCREEN    deterministic. The 重大訊息 clause number picks a lane, or skips
                        │
 [1] TRIAGE           model  Which valuation input does this touch? How sure?
 [2] EXTRACT          model  Which number, quoted from which exact item?
                        │
 [3] RECOMPUTE        deterministic. dcf.compute() before vs after
 [4] VERIFY           deterministic. Every number and quote must exist in the filing
                        │
     PUBLISHED      HELD FOR REVIEW (a person decides)      ARCHIVED (reason logged)
```

**Stages 3 and 4 never use a model.** Numbers come from arithmetic, and every claim the model
makes is checked back against the filing. The model never calculates and never grades itself.
Without an API key, stages 1 and 2 fall back to a rule-based reasoner, which is also the
baseline the evaluation compares against. The screen and the trace always say which one ran.

### Lanes by clause

The clause list and thresholds were set with the team's finance members (Ferry, Patrice).
Full mapping and the reasoning behind each decision: [`docs/pemetaan-pasal.md`](docs/pemetaan-pasal.md).

| Clause | Lane | What happens |
|---|---|---|
| 20 (asset acquisition / disposal) | Valuation scenario | DCF recomputed as an "if this is realised" scenario. DCF is cash-based: a plan does not move the valuation until a quarterly report shows the cash. Deals with a 100%-owned subsidiary are archived (cash stays in the group) |
| 22, 23 (guarantees, loans of funds) | Risk signal | Balance ÷ equity, limit usage, per recipient, related vs outside party. Loans ≥ 40% of equity are flagged |
| 11, 35 (capital changes, bonds, buybacks) | Capital signal | Dilution and money amounts against materiality thresholds (shares ≥ 1%, money ≥ 2% of market cap) |
| 31 (quarterly reports) | Report signal | Profit/loss, debt ratio. Losses written in brackets `(339,123)` are read as negative |
| 1, 3, 40 (default, halt of production, trading suspension) | Severe | Always held for a person |
| 7, 8 (external auditor change, key officer change) | Governance | Published as information; officer names are never extracted |
| 6, 51, 53 and others | Skipped | Never reach the model |

Signal level (info / attention / serious) depends on a risk profile (conservative / moderate /
aggressive) chosen on screen; thresholds live in `app/ambang_profil.py`. The server uses
*moderate* (the finance team's answers) for hold decisions.

### What stage 4 checks

| Check | Catches |
|---|---|
| Item label allowed for the input | Quotes taken from free-text notes, where injected instructions usually sit |
| Quote exists in the filing | Invented source sentences |
| Digits exist in the filing | Hallucinated numbers |
| Supported currency | USD amounts silently converted without an exchange rate |
| Known unit | 仟元 / 百萬元 / 億元 mix-ups (thousand-fold errors) |
| Magnitude within 0.2–3.0× of the base | Wrong item, or an injected number |
| Circularity intact | Arithmetic bugs in the calculator |

### Valuation

`scripts/dcf.py` is a standalone DCF calculator; the web app calls the same `compute()`, so the
screen cannot silently differ from the worksheet. `valuation/inputs/2330.json` is a manual
worksheet with a source for every input. For other non-financial issuers,
`app/valuasi_otomatis.py` builds the same input structure from exchange prices and FinMind
financial statements, cached for 12 hours ([`docs/valuasi-otomatis.md`](docs/valuasi-otomatis.md)).
Financial companies (banks, insurers) get no DCF.

### Ask FEAF (chat)

Ask FEAF is available as a slide-over panel on every page (`_panel_chat.html`, `chat.js`,
`chat.css`) and on the full `/tanya` page (which also works via plain HTML form POST when
JavaScript is off). Answers come **only from read-only tool results** (`app/chat.py`):

- **12 read-only tools**: 6 stock tools (`harga`, `statistik`, `laporan`, `pengumuman`,
  `valuasi`, `ringkasan`) and 6 menu tools (`feed`, `peringatan`, `jejak`, `review`, `ambang`,
  `watchlist`). No tool modifies the watchlist, review queue, or thresholds, and no tool returns
  raw `items` or officer/spokesperson names.
- **Multi-turn conversation with signed history**: the browser keeps up to 12 messages in
  `sessionStorage["feaf_chat"]` across page navigation, and the server accepts at most the last
  6 verified turns. Every assistant answer is signed with a 32-hex HMAC-SHA256 tag
  (`tanda(id, jawaban)` using `SENTINEL_CHAT_RAHASIA`). Unsigned or modified assistant turns and
  any user turn matching `TOLAK` are dropped before reaching the model or checker and logged in
  the trace (`tahap: "riwayat"`).
- **Follow-ups and Recap**: follow-up questions resolve the active stock code from the question,
  page context (`konteks.kode`), the last verified turn, or the announcement prefix
  (`konteks.id`). **Recap** summarizes verified turns in at most 5 bullet points; every number
  is checked against signed assistant turns, falling back to `recap_template` if rejected.
- **Verification and refusal**: every number in an answer must exist in the current tool output,
  the question, or a signed assistant turn (never an unverified old user turn). Questions asking
  for buy/sell advice, price predictions, order placement, personal data, or containing prompt
  injections are refused before any tool or model call. Model calls are capped at 60 per hour.

### Pages

| Page | Content |
|---|---|
| `/` | Alert feed |
| `/saham/{code}` | Stock page: filings, financial statements, valuation, signals |
| `/peringatan/{id}` | Alert detail with MOPS citation and checker verdict |
| `/jejak/{id}` | Operation trace (every step, model call, token count, latency) |
| `/valuasi/{code}` | DCF, cost of capital, sensitivity, source of each input |
| `/review` | HELD FOR REVIEW queue; a person approves or rejects |
| `/ambang` | Triage thresholds per clause, adjusted by 👍/👎 feedback, with history |
| `/watchlist` | Stocks being watched |
| `/tanya` | Ask FEAF |

The interface is available in English, 繁體中文 and Bahasa Indonesia.

---

## API

`/docs` serves the OpenAPI description.

| Route | Content |
|---|---|
| `GET /api/peringatan` | All processing results (JSON) |
| `GET /api/jejak/{id}` | Operation trace of one filing |
| `GET /api/valuasi/{code}` | DCF calculator output |
| `GET /api/saham/{code}/keuangan` | Financial statement tables |
| `GET /api/review` | Review queue and human decisions |
| `GET /api/ambang` | Thresholds per clause and their history |
| `GET /api/watchlist` | Watched stock codes |
| `GET /api/cari?q=` | Search issuers by code or name |
| `POST /api/tanya` | Ask FEAF |
| `GET /api/tanya/jejak/{id}` | Trace of one Ask FEAF answer |
| `POST /periksa` | Pull new filings for the watchlist and reprocess |
| `POST /api/impor` | Import MOPS history pulled on a Taiwan network |
| `GET /sehat` | Health check: filing count, last run, model in use, fallback reasons, code version |

---

## Model and version

| | |
|---|---|
| Provider | Google Gemini API (`generativelanguage.googleapis.com`), paid tier |
| Main model | `gemini-3.6-flash`, temperature 0 |
| Backup model | `gemini-3.5-flash`, used only when the main model is busy (429/5xx) after retries |
| Pipeline prompt version | `VERSI_PROMPT` in `app/agent/llm.py` (currently `2026-11-10.1`) |
| Chat prompt version | `PROMPT_VERSION` in `app/chat.py` (currently `chat-2026-11-12.1`) |
| Baseline | Rule-based reasoner in `app/agent/screen.py` / `extract.py` |

Safeguards around the model: answers are cached per filing and prompt version; each run is
capped at 40 model calls and 90 seconds; three failures in a row switch the rest of the run to
the rule-based reasoner; an exhausted prepaid balance (HTTP 402) is reported in `/sehat` and
never retried. Each fallback and its reason is written to the trace.

Only public MOPS filings are sent to the model, with personal fields already removed. No
SYSTEX or partner data is sent to any model.

---

## Data flow and privacy

```
TWSE / TPEx / MOPS → scripts/ → data/parsed/ → app/agent/ → app/ (web)
                        │                          │
            personal fields dropped         data/traces/ (audit)
```

- `scripts/fetch_details.py` and `app/tarik.py` drop `發言人`, `發言人職稱` and
  `發言人電話` **before anything is saved**. Only the fact that a field was dropped is logged,
  never its value. Personal data cannot reach the model by construction.
- Names of officers, directors and auditors (clauses 1, 6, 7, 8) are never extracted, shown or
  exported. The governance lane reports the role and the kind of change only.
- Filing text is treated as **untrusted data**: it enters the prompt inside delimiters, the
  system instruction says nothing inside may be followed, and injection attempts are logged in
  the trace.
- API keys are read from the environment only and are never written to a file, page, log or
  trace (tested).

## Access and permissions

| Setting | Effect |
|---|---|
| none | Every page readable; actions (watchlist, Check now, review, thresholds) open |
| `SENTINEL_KODE_AKSES=<code>` | Actions require opening `/akses?kode=<code>` once; reading stays open |
| plus `SENTINEL_KUNCI_BACA=1` | Every page and `/api/*` require the code; `/sehat` and static files stay open |

The access code for the judges' environment is given through the competition form, not in this
repository.

---

## Environment variables

| Name | Required | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | no | — | Model key. Without it the rule-based reasoner is used |
| `SENTINEL_MODEL` | no | `gemini-3.6-flash` | Main model |
| `SENTINEL_MODEL_CADANGAN` | no | `gemini-3.5-flash` | Backup models, comma-separated |
| `SENTINEL_PENYEDIA` | no | `gemini` | Model provider |
| `SENTINEL_MODEL_MAKS_PER_JALAN` | no | `40` | Model calls allowed per run |
| `SENTINEL_RETRY` | no | `2` | Retries before falling back |
| `SENTINEL_TIMEOUT` | no | `45` | Model call timeout (seconds) |
| `SENTINEL_TRIAGE_THRESHOLD` | no | `0.55` | Triage confidence threshold |
| `SENTINEL_DATA_DIR` | no | `./data` (`/data` in Docker) | Where pulled data and traces live |
| `SENTINEL_TARIK_OTOMATIS_DETIK` | no | `0` (off) | Pull new filings every N seconds (minimum 300) |
| `SENTINEL_PROSES_SEMUA` | no | `1` | Process filings of all issuers, not only the watchlist |
| `SENTINEL_KODE_AKSES` | no | — | Access code for actions |
| `SENTINEL_KUNCI_BACA` | no | `0` | `1` = access code also required for reading |
| `SENTINEL_SERTAKAN_CONTOH` | no | `0` | `1` = show the four sample filings next to real data |
| `SENTINEL_CHAT_MAKS_PER_JAM` | no | `60` | Ask FEAF questions per hour |
| `SENTINEL_CHAT_RAHASIA` | no | per-process random hex | Secret for HMAC-SHA256 signing of assistant chat turns |
| `FINMIND_TOKEN` | no | — | Higher FinMind quota for financial statements |

---

## Evaluation

```bash
python3 scripts/evaluasi.py --simpan                    # gold set: agent vs no checker
python3 scripts/evaluasi.py --chat --simpan             # Ask FEAF single-turn set (52 questions)
python3 scripts/evaluasi.py --chat-percakapan --simpan  # Ask FEAF multi-turn set (12 scenarios, 36 turns)
python3 scripts/uji_serangan.py --simpan                # attack set
```

Reports are written to `eval/hasil/` (inside the Docker image, where `/app` is read-only, to
`/data/eval-hasil/`). The 46 gold filings ship in `eval/gold_dokumen.json` (name-bearing items
removed, market caps as of the official run), so the evaluation reproduces on any machine without
pulling data. Add `--tanpa-cache` to measure real model latency and cost instead of cached answers.
The gold set and how it was labelled:
[`docs/hasil-gold-set.md`](docs/hasil-gold-set.md), [`docs/panduan-gold-set.md`](docs/panduan-gold-set.md).

**Gold set.** 46 real filings from 9 Nov 2026, about 7 per lane, labelled publish / hold /
archive and signal level by a finance team member. Success = the agent makes the same decision
and publishes no wrong number. Baseline ("without checker"): the same clause screen and extractor with no checker and no hold rules, so anything extracted is published, as a plain LLM pipeline would. Manual
time per filing, from the labeller: 20–30 minutes.

| Metric | FEAF agent | Without checker |
|---|---|---|
| Wrong numbers published | **0/46** | 5/46 |
| Decision matches expert | 41/46 (89%) | 15/46 (33%) |
| Signal level matches expert (moderate profile) | 21/29 (72%) | 0/29 |
| Held for a person (human intervention) | 13/46 (28%) | 33/46 (72%) |

These numbers were measured **before** tuning. The disagreements exposed two parser bugs
(losses in brackets read as profits; share counts in 仟股 not read) and three thresholds; all
were fixed afterwards. On the same 46 filings the tuned agent scores 43/46 and 29/29, but that
is in-sample and is not reported as accuracy.

**Model path on the server** (Gemini 3.6 Flash, fresh calls, 11 Nov): 0/46 wrong numbers
published (without checker: 5/46), mean latency 0.7 s per filing (max 9.9 s), 5 model calls,
7,212 input / 392 output tokens, about **USD 0.007 for all 46 filings** at paid-tier prices. Only
clause-20 filings call the model; the other lanes are parsed deterministically. Full write-up
with error categories, the live-server intervention rate (12% held) and an annotated
operation trace: [`docs/laporan-evaluasi.md`](docs/laporan-evaluasi.md).

**Attack set** ([`eval/hasil/serangan-2026-11-10.md`](eval/hasil/serangan-2026-11-10.md)).
12 attack types on real filings (injected instructions, invented numbers and quotes, fake labels,
unit swaps, foreign currency, extreme magnitudes), 72 cases, attacked by both the rule-based
reasoner and a simulated model that obeys every injection: **0 wrong numbers published**.

**Ask FEAF** ([`eval/hasil/chat-20261111T062005Z.md`](eval/hasil/chat-20261111T062005Z.md),
[`eval/hasil/chat-percakapan-20261112T150427Z.md`](eval/hasil/chat-percakapan-20261112T150427Z.md)).
- Single-turn set (52 questions in three languages): with Gemini 3.6 Flash on the server, 27/27
  advice, out-of-scope and injection questions refused, 0 recommendation words reached the user,
  50/52 correct overall (the two misses were checker false positives, since fixed; the user still
  received a sourced answer), 52/52 on the rule path. Mean latency 4.4 s with the model, 0.2 s on
  the rule path.
- Multi-turn conversation set (`eval/chat_percakapan.csv`, 12 scenarios × 3 turns = 36 turns in
  English, 繁體中文 and Bahasa Indonesia, covering page-context follow-ups, history follow-ups,
  Recap, menu tools `feed`/`review`/`ambang`/`watchlist`/`peringatan`/`jejak`, mid-conversation
  prompt injection, and turn-3 buy/order/prediction refusals): **36/36 turns and 12/12 scenarios
  correct** on the rule path, **0 recommendation words**, **1 injected history turn dropped**, mean
  latency 2 ms (max 42 ms).

**Operations** ([`eval/hasil/operasional-20261111T024832Z.md`](eval/hasil/operasional-20261111T024832Z.md)).
581 real filings: 318 passed the clause screen, 241 published, 58 held (10% of all), the rest
archived with a logged reason. Latency per filing (rule path): mean 1 ms, max 29 ms.

Every result has an operation trace at `/jejak/{id}` and `GET /api/jejak/{id}`: each stage, its
input and output, model name, tokens, retries, latency, and the checker verdict.

---

## Known limitations

1. **Clause 20 recalculations are scenarios, not forecasts.** DCF is cash-based; a plan or
   board approval moves the valuation only once a quarterly report shows the cash.
2. **No valuation for financial companies** (banks, insurers). Their clause-20 filings are held.
3. **No currency conversion.** Non-NTD amounts are held, not converted.
4. **Today's filings only, outside Taiwan.** The OpenAPI endpoints keep no history; older filings
   need a pull from a Taiwan network.
5. **Thresholds for the conservative and aggressive profiles** are proposals awaiting the finance
   team's review; the moderate profile is the team's answer.
6. **The tuned accuracy is in-sample.** A fresh, blind-labelled test set is needed for an
   out-of-sample figure.
7. **Reverse DCF gives no intrinsic value**; it gives the perpetual growth the market implies.
   Fair value is shown only as a scenario with a stated growth assumption.

Worst case and recovery: if the model is unavailable or out of credit, the run switches to the
rule-based reasoner and says so on screen and in `/sehat`; if a number cannot be verified, the
filing is held for a person rather than published.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Screen says "rule-based reasoner" | No API key in the environment. This is valid; set `GEMINI_API_KEY` for the model path |
| `/sehat` shows `galat_model_terakhir` with 402 | The Gemini prepaid balance is empty. Top up in AI Studio billing |
| `/sehat` shows `sebab_cadangan` with a time limit | The 90-second run cap was reached; remaining filings are answered on the next runs |
| MOPS pull returns HTTP 200 but a block page | Geo-blocking. MOPS is only reachable from a Taiwan network; use the OpenAPI pull instead |
| Empty feed | `data/parsed/` is empty; press **Check now** or set `SENTINEL_SERTAKAN_CONTOH=1` |
| No valuation on a stock page | Financial company, or FinMind quota reached (set `FINMIND_TOKEN`) |
| Server behaves like an older version | Compare `versi_kode` in `/sehat` with your checkout |

---

## Repository contents

| Path | Content |
|---|---|
| `app/` | Web app, Ask FEAF, thresholds, valuation builder |
| `app/agent/` | Pipeline stages: screen, triage, extract, recompute, verify |
| `app/teks/`, `app/i18n.py` | Interface text in three languages |
| `scripts/` | Filing pulls, DCF calculator, evaluation, attack set |
| `valuation/inputs/` | Manual DCF worksheets with a source for every input |
| `eval/` | Gold set, Ask FEAF test set, evaluation reports |
| `tests/` | Unit and end-to-end tests (no network) |
| `data/fixtures/` | Four sample filings so the app runs anywhere |
| `design/`, `wireframe/` | Screen designs and diagrams |
| `docs/` | Clause mapping, evaluation notes, deploy guide (mostly in Indonesian) |

---

## License · 授權 · Lisensi

All rights reserved. See [`LICENSE`](LICENSE). AAIC 2026 organisers and judges may run and
inspect this repository to evaluate the entry. Third-party components and data keep their own
licences ([`docs/pengungkapan-pihak-ketiga.md`](docs/pengungkapan-pihak-ketiga.md)).

版權所有，詳見 [`LICENSE`](LICENSE)。AAIC 2026 主辦單位與評審可為評選目的執行及檢視本專案。
第三方元件與資料沿用其原授權。

Hak cipta dilindungi; lihat [`LICENSE`](LICENSE). Panitia dan juri AAIC 2026 boleh menjalankan
dan memeriksa repo ini untuk penilaian. Komponen dan data pihak ketiga tetap memakai lisensinya masing-masing.

