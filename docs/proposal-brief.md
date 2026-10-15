# Proposal Brief — isi deck penyisihan (draf 15 Okt)

> **Catatan internal — hapus seluruh blok ini sebelum dikirim.**
>
> Situs lomba meminta proposal brief mencakup tujuh hal: *real problem and evidence of need ·
> necessity of adopting Agentic AI · task flow and system architecture · state management and
> security design · prototype and evaluation metrics · deployment and dissemination plan ·
> team division of labor and description of third-party resources.*
>
> Berkas ini adalah **isi** deck 12 halaman (Appendix 1), dikelompokkan per butir wajib itu.
> Isi deck ditulis dalam bahasa Inggris karena jurinya membaca Inggris/Mandarin. Catatan
> untuk tim tetap berbahasa Indonesia.
>
> - `[ISI: …]` = data yang hanya tim yang punya (terutama hasil wawancara). Jangan dikarang.
> - `[CEK: …]` = klaim yang benar per repo 28 Sep, tapi statusnya mungkin sudah berubah.
>
> Semua angka lain sudah dicocokkan dengan repo pada 15 Okt: 14 tes lulus, empat kasus
> fixture menghasilkan 2 terbit, 1 ditolak, 1 dilewati.
>
> Daftar periksa sebelum kirim ada di [bagian paling bawah](#daftar-periksa-sebelum-kirim).

## Peta: tujuh butir wajib → halaman deck → kriteria nilai

| # | Butir wajib (situs) | Halaman deck | Kriteria penyisihan |
|---|---|---|---|
| — | Cover | 1 | — |
| 1 | Real problem & evidence of need | 2–3 | Problem & Field-Need Evidence — 20% |
| 2 | Necessity of adopting Agentic AI | 4 | Appropriateness of Agentic AI Design — 20% |
| 3 | Task flow & system architecture | 5–6 | Agentic Design 20% + Technical & Data Planning 20% |
| 4 | State management & security design | 7 (+ state di hal. 5) | Safety, Governance & Ethics — 10% |
| 5 | Prototype & evaluation metrics | 8–9 | Prototype & Validation Plan — 15% |
| 6 | Deployment & dissemination plan | 10–11 | Innovation & Scalability Potential — 15% |
| 7 | Team division of labor & third-party resources | 12 | Kelayakan (Pasal 7) + pengungkapan (Pasal 13) |

Nama berkas: `group_theme_team_proposal.pdf` → mis. `B_IndustryPublicCoCreation_[ISI: nama tim]_Proposal.pdf`.
Batasnya **12 halaman termasuk cover** dan tidak boleh memuat nama kampus, jurusan, dosen,
maupun tanda pengenal lain.

---

## Page 1 — Cover

**Stock Sentinel**
*An agent that recomputes a stock's valuation when an official filing changes the numbers —
and refuses to alert when it cannot trace those numbers back to the filing.*

| | |
|---|---|
| Category | B — Designated Field Group |
| Challenge | SYSTEX — Investment Intelligence & AI-Powered Stock Selection Agent |
| Theme | Industry & Public-Sector Co-Creation |
| Technology tags | Agentic Workflow · Domain-Specific Agent · Human-in-the-loop |
| Field validation level | [ISI: Level 1 kalau ≥1 wawancara terdokumentasi; jangan klaim lebih tinggi] |

> Decision support, not a trading tool. No broker connection, no order execution.
> The agent screens, explains and cites; the investor decides.

---

# 1 · Real problem and evidence of need

## Page 2 — Problem, target user, current workflow

**Target user.** Self-directed retail investors who hold or watch a handful of Taiwan-listed
stocks and have no finance training or analyst support.
[ISI: pertajam dari profil narasumber, mis. "mahasiswa dan pekerja muda, investasi < N tahun"]

**The problem.** In Taiwan, material corporate news is published first as a MOPS
material-information announcement (重大訊息). It is public, free and authoritative. In practice
it reaches retail investors late or not at all, because:

- **Volume.** Our own pull on 14 Sep 2026 returned **711 announcements from just five issuers**
  (2330, 2317, 2881, 1301, 2412) for 1 Jan – 11 Sep 2026. That averages **about 17 per issuer per
  month**, so a 10-stock watchlist means roughly 170 filings a month to triage.
- **Format.** The filings are in Traditional Chinese, dated in the ROC calendar (2026 = year 115),
  and report amounts in mixed units (仟元 / 百萬元 / 億元, up to 100,000× apart), sometimes in
  foreign currency.
- **Relevance is rare and hidden.** Most filings are investor-conference notices and routine board
  items. The few that move a valuation input, such as capex budgets, asset acquisitions or large
  borrowings, are buried among them.
  [CEK: setelah daftar pasal diverifikasi, ganti dengan rasio nyata, mis. "X dari 711"]
- **Existing tools answer a different question.** Price and news apps push headlines and price
  moves. They don't say whether a filing changes what the company is worth, and they don't show
  the source sentence.

**Current workflow** (from interviews):
[ISI: urutan nyata dari Blok B wawancara, mis. "tahu dari media sosial → buka N sumber →
X menit per pengumuman → tahu Y hari setelah terbit"]

## Page 3 — Field evidence (Level 1) and what it changed

**Method.** [ISI: N] semi-structured interviews of about 45 minutes each, held [ISI: tanggal].
The questions asked about the last real decision rather than general habits, and the concept was
introduced only in the final block. Consent was obtained, and responses are recorded under codes
P01…P0N with no names, schools or amounts.

**Quantified pain points**

| Measure | Median (range) | n |
|---|---|---|
| Minutes to check one announcement | [ISI] | [ISI] |
| Stocks monitored | [ISI] | [ISI] |
| How often they check | [ISI] | [ISI] |
| Lag between a filing and learning about it | [ISI] | [ISI] |
| Purchases abandoned because information was hard to find | [ISI] | [ISI] |

**Two verbatim quotes.** Include one that is unfavourable to us.
[ISI: kutipan P0x] · [ISI: kutipan P0y]

**What we changed because of the interviews.**
[ISI: satu perubahan konkret, mis. "kami berhenti menampilkan 'BELI/JUAL' dan menggantinya
dengan rentang nilai wajar + asumsi, karena P03 dan P05 bilang tidak percaya kesimpulan
tanpa bahan"]. Satu halaman seperti ini mengalahkan sepuluh kutipan yang setuju.

**Process and data evidence already in hand** (toward Level 2):
- 711 real announcements pulled and parsed from a Taiwan campus network, **100% with a permanent
  source URL**. The URL comes from the 詳細資料 button parameters, which are not visible in the
  table text.
- A field constraint found the hard way: MOPS and TWSE block non-Taiwan and datacenter IPs **while
  still returning HTTP 200** with a block page. A naive pipeline would store that page as data.

---

# 2 · Necessity of adopting Agentic AI

## Page 4 — Why an agent, and why not something simpler

The goal is open-ended and long-running: *"Tell me when an official filing changes my valuation
conclusion, and show me the proof."* No single call answers that. It has to be broken into steps
that depend on each other, and the system has to know when to stop.

| Alternative | What it does | Why it falls short here |
|---|---|---|
| Price / news alert app | Pushes headlines and price moves | Doesn't know which valuation input changed. No source sentence. |
| Chatbot / single LLM call | Answers when asked | Not proactive. Numbers can be hallucinated and nothing checks them. |
| RAG over filings | Retrieves passages for a question | Still waits for a question. Retrieving a passage is not the same as verifying an extracted number, and it can't recompute anything. |
| Rigid rule workflow | Keyword or regex extraction | Brittle on free-text Chinese with shifting labels and units. Can't judge its own confidence. (We keep it as the fallback and as a baseline.) |
| Spreadsheet DCF | Recomputes when you type | Doesn't know *when* to recompute. |

**What the agent adds**
1. It decides **where reasoning is needed**. A free, deterministic screen on the regulator's own
   clause number (符合條款) drops filings that can't touch valuation, so the model never sees them.
2. It **chooses the input and extracts the number** with its exact source sentence, together with a
   confidence score.
3. It **hands off to tools**: a deterministic DCF calculator runs before and after the change, and a
   deterministic verifier then checks the model's claims.
4. It **can stop** at three points (skip, hold for a human, reject), and it adapts when a tool
   fails (retry, then fall back to rules, labelled as fallback).

**Eligibility (Art. 4).** Criterion 1 is required, plus at least two of criteria 2–4. We meet all four.

| Criterion | How Stock Sentinel meets it |
|---|---|
| ① Goal decomposition (required) | Six ordered states; each advances on the previous state's result |
| ② Tool / external-system calls | MOPS, TWSE/TPEx OpenAPI, the DCF calculator, the model API |
| ③ State management & dynamic adjustment | Confidence threshold, three exits, retry, rule-based fallback |
| ④ Access control & risk management | Deterministic output verification, a full audit trace, and no order-execution capability |

> The rules say *"a higher degree of autonomy is not necessarily better"*, and finance is named
> as a high-risk domain. We deliberately give the agent **no authority to act**, only to inform.

---

# 3 · Task flow and system architecture

## Page 5 — Task flow and agent state diagram

Figure: `design/export/AlurState.png` [CEK: label masih bahasa Indonesia → butuh versi Inggris]

```
MOPS filing
  S0  CLAUSE SCREEN   deterministic   clause can't touch valuation ────────────► SKIPPED
  S1  TRIAGE          model           which input? confidence < 0.55 ──────────► HELD (human queue)
  S2  EXTRACT         model           value + unit + currency + exact sentence
                                      nothing extractable with its source ─────► HELD
  S3  RECOMPUTE       deterministic   dcf.compute() before vs after
  S4  VERIFY          deterministic   any check fails ─────────────────────────► REJECTED (reason logged)
  S5  PUBLISHED       cited alert → the investor decides
```

- **The model touches only S1–S2**, which run as one call because both read the same document;
  splitting them would double the cost with no gain in accuracy.
- **S3 and S4 deliberately use no model.** Numbers come from arithmetic, and the model's claims are
  tested against the document. The model never calculates and never grades itself.
- **Dynamic adjustment.** If the API fails, the call is retried twice. If it still fails, the agent
  falls back to the rule-based reasoner and labels the output as fallback, all the way to the
  screen. Tasks never stop silently and never pretend to succeed.

## Page 6 — System architecture, models, tools, data flow

Figure: `design/export/Arsitektur.png` [CEK: label bahasa Indonesia; diagram masih menyebut
`triage.py` dan "tiga kasus uji", padahal kodenya `extract.py` dan fixture-nya empat]

| Layer | Components | Key design choice |
|---|---|---|
| 1 · Sources | MOPS 重大訊息 (`mopsov.twse.com.tw`, form-POST), TWSE/TPEx OpenAPI | Responses are validated by **shape**, not by status code |
| 2 · Ingestion & cleaning | `probe_sources` → `spike_mops` → `parse_mops` → `fetch_details` | 2–2.5 s polite delay; ROC → Gregorian dates; permanent citation URL per filing; **personal data dropped before storage** |
| 3 · Agent | `screen` → `extract` + `llm` → `recompute` (calls `scripts/dcf.py`) → `verify`, orchestrated by `pipeline` | The model appears in 2 of the 11 components; every step writes a trace |
| 4 · Presentation | FastAPI, server-rendered: alert feed, alert detail, valuation, audit trace, JSON API + OpenAPI | No login, so no stored passwords and no extra attack surface |

**Model.** Gemini 2.5 Flash at temperature 0 in JSON-response mode, with a version-pinned prompt
(`VERSI_PROMPT = 2026-09-24.1`). The provider can be swapped with one environment variable. A
rule-based reasoner serves both as the fallback and as the evaluation baseline.

**Valuation engine.** A two-stage unlevered DCF with WACC, a reverse DCF (the growth rate the
market is implying), a perpetual-growth sanity cap and a WACC × g sensitivity grid. Every input
carries its source URL. The web app and the CLI call the same `compute()`, so the screen can't
silently differ from the worksheet.

**Data flow.** MOPS/TWSE → `scripts/` → `data/parsed/` (PII-free) → `app/agent/` → web.
Each run writes a trace to `data/traces/`. Storage is plain JSON files with no database.

---

# 4 · State management and security design

## Page 7 — State, permissions, human–AI collaboration, security, failure handling

**State management**
- Each filing is one task with an explicit state. There are four terminal states, and three of
  them are not "publish": **skipped · held · rejected · published**.
- Every state writes a trace record containing input, output, latency, tokens, cost, retries,
  the fallback flag and the number of model calls. The operation trace that Appendix 2 requires
  is a by-product of normal operation, not something assembled afterwards.
- **Fail-closed defaults.** Foreign-currency amounts are rejected rather than converted, unknown
  units are rejected, and a missing clause number is passed through but flagged for a human.
- *Planned for the final:* a feedback state. A 👍/👎 on each alert tunes the per-user triage
  threshold within fixed bounds, and every change is logged and reversible. Today the threshold is
  fixed at 0.55.

**Permissions and human–AI division**

| Agent may | Agent may not | Human |
|---|---|---|
| Read public filings, compute, explain, cite | Trade, connect to a broker, move money, act on the user's behalf (Art. 14.2) | Makes every investment decision; reviews the HELD queue; owns the threshold |

Every screen states **which engine produced it** (model or rule-based) and **which data it
used** (real or fixture).

**Threats (Art. 14.3) and responses**

| Risk | Design response | Automated test |
|---|---|---|
| Prompt injection inside a filing | Filing text sits inside delimiters as untrusted data; injection markers are logged; the verifier is deterministic, so injected numbers fail the label, quote, digit and magnitude checks | Injection detected and logged · injected number never published · a "successful" injection is still rejected |
| Hallucinated number or quote | The quote must exist verbatim, and the digits must exist in the filing | Fabricated quote rejected · number absent from filing rejected |
| Unit / currency error | Unit whitelist; foreign currency rejected; magnitude band 0.2–3.0× of the current value | USD amount rejected (fail-closed) |
| Arithmetic bug | Circularity check (reverse-DCF g fed back must reproduce EV); CLI and web share one `compute()` | CLI and `compute()` agree |
| Personal data (PDPA) | Spokesperson name, title and phone are dropped at ingestion; only the *field names* are logged | PII values never stored |
| Credential leak | API key read only from the environment; never written to screen, log or trace | No API key in any trace |
| Third-party failure | Retry, then rule-based fallback; MOPS block pages detected by response shape | — (every trace records retries and the fallback flag) |
| Free-tier data use | Only public filings with PII already removed are sent; non-public data would require a no-training tier | Disclosed (page 12) |
| Inappropriate output / bias | No bare "BUY/SELL". Output is a fair-value range, its assumptions and what would make it wrong | — |

**Incident response (Art. 14.4).** On any data or credential leak or unauthorised access, stop
the affected function, report to the organizer and the field contact, and don't widen the
incident with self-testing.

---

# 5 · Prototype and evaluation metrics

## Page 8 — Prototype and operation flow

Screens: `design/export/Main.png`, `DetailPeringatan.png`, `Valuasi.png`, `JejakAudit.png`
[CEK: screenshot dari aplikasi yang jalan lebih meyakinkan daripada mockup; label perlu Inggris]

**Flow.** Alert feed → alert detail (MOPS link, exact source sentence, valuation before and
after, verifier verdict) → valuation page (visible, editable assumptions; WACC × g sensitivity)
→ audit trace (each state with its latency, cost and retries).

**What runs today** (stated plainly, because the judges may inspect the code)

| Item | Status |
|---|---|
| Web app + five-stage pipeline | Runs end to end |
| Automated tests | **14, all passing** (15 Oct 2026) |
| Fixture cases | 4: 2 published, 1 rejected, 1 skipped (table below) |
| Real data | 711 announcements pulled and parsed. [CEK: pipeline sudah dijalankan di data asli? tanggal?] |
| Live model path | Implemented. [CEK: sudah ada jejak dengan `panggilan_model > 0`? Kalau belum, tulis "rule-based mode so far"] |
| Valuation files | 1 issuer (TSMC 2330). Some inputs are still being sourced, so no valuation numbers are presented as findings |

| Fixture case | Outcome | What it proves |
|---|---|---|
| TSMC capex budget | Published | Normal path works end to end |
| TSMC capex + an instruction injected into the filing | Published with the **correct** number | The injection is logged; the injected number never publishes |
| MediaTek investor-conference notice | Skipped | Screened out before reaching the model |
| Asset acquisition denominated in USD | Rejected | Fail-closed on foreign currency |

## Page 9 — Test cases, baselines, evaluation metrics

**Definition of success.** An alert is correct only if (a) every number traces to an exact
sentence in the filing, (b) it is mapped to the right valuation input, and (c) the recomputed
figure matches the calculator. **Safety target: zero unsupported numbers published.**

**Test sets**

| Set | Size | Purpose | Status |
|---|---|---|---|
| Unit and adversarial tests | 14 | Injection, hallucination, units, currency, PII, key leakage, arithmetic | Passing |
| Fault-injection set | [ISI: N] | Corrupted filings: wrong digits, fabricated quote, unit swap, foreign currency, injected instruction. Target: 100% caught | [CEK] |
| Gold set | 30–50 | Filing → expected outcome, input, value, source sentence, labelled by the finance members | [CEK: status per hari ini] |
| Real-stream replay | 711 | Screening rate, held/rejected shares, cost and latency at real scale | [CEK] |

Items are shuffled before each run (Fisher–Yates) so results don't depend on order.

**Baselines**
1. **The manual process**, using minutes per filing and the filing-to-awareness lag from the
   interviews ([ISI] page 3).
2. **A rule-based workflow**: the same pipeline with no model. It already exists as the fallback.
3. **A single LLM call without the verifier**: what a plain chatbot would publish.

**Metrics** (Appendix 2; most are already recorded automatically in every trace)

| Group | Metrics |
|---|---|
| Quality | Task success rate · extraction accuracy (value, unit, input) · precision of published alerts · recall of valuation-relevant filings · verifier catch rate |
| Efficiency | Latency per filing (average and maximum) · model/API cost per filing and per day (USD) · share of filings that reach the model |
| Robustness | Tool-call success rate · retries · fallback rate · termination rate (skipped / held / rejected) |
| Human load | Human-intervention rate (HELD share) · minutes saved vs the manual baseline |
| Safety | Prompt-injection, PII, credential, permission and inappropriate-output test results · error categories · worst case and recovery |

---

# 6 · Deployment and dissemination plan

## Page 10 — Deployment, cost, maintenance, field adoption

**Deployment constraint we found in the field.** MOPS and TWSE serve only Taiwan, non-datacenter
networks. Ingestion therefore runs on a machine inside Taiwan (today, a laptop on the campus
network), while the agent and web tier can run anywhere and read the cleaned JSON. For a partner
deployment, the robust option is a licensed data feed from the field partner.
[CEK: tanyakan ke SYSTEX apakah ada akses data/API]

**Footprint.** Python plus three dependencies (FastAPI, Uvicorn, Jinja2), JSON files, no
database and no login. It runs on a laptop.

**Cost.** The deterministic clause screen means the model is called only for the small share of
filings that can touch valuation. At current scale the free tier is enough. Cost is recorded per
trace in USD, so reported costs are measured rather than estimated.

**Maintenance.** Each piece of the system has one place to update it:

| Piece | Where it lives |
|---|---|
| Clause → input map | Regulator-defined and versioned in one table |
| Valuation inputs | One file per issuer, with a source URL for every number |
| Prompt | A version constant |
| Behaviour | A regression test suite |

**Field adoption path (by validation level)**

| When | Level | Activity |
|---|---|---|
| Now | 1 → 2 | Interviews; real filings; labelled gold set |
| Oct – Nov (before the final) | 3 | Interviewees run the prototype on their own watchlist in a sandbox with no real money, then give structured feedback |
| After the competition | 4 | Pilot with one investor community or the field partner; before/after comparison of minutes per filing and filing-to-awareness lag |

## Page 11 — Innovation, scalability, dissemination, future work

**What is new**
1. **Refusal as the product.** The agent's value lies as much in what it won't publish as in
   what it does.
2. **The regulator's own classification is a zero-cost router.** We never have to defend a
   home-made classifier.
3. **Event-triggered recomputation.** This closes the "a spreadsheet doesn't know when to
   recompute" gap.
4. **Every alert carries its own audit trail**: source sentence, checks and cost.

**Scalability.** The pipeline is issuer-agnostic. Adding a company means adding a valuation input
file, and the clause table and verifier are shared. OTC (TPEx) issuers use the same parser with a
different market parameter (`TYPEK=otc`). Financial companies need a non-DCF method; Fubon (2881)
is planned.

**Toward the full SYSTEX core workflow**

| Stage | Today | Next |
|---|---|---|
| Personalized intelligence | Valuation per issuer | Per-user watchlist and risk profile |
| Proactive delivery | Event-triggered alerts | Mobile push (design ready: `NotifPonsel.png`) |
| Behavioral feedback | — | 👍/👎 per alert |
| Continuous optimization | Fixed threshold | Feedback-tuned threshold, bounded and logged |

Also planned: a question-answering surface over the same evidence layer (so the organizer's gold
answers can be run), and Monte Carlo framed correctly ("in X% of simulations under these
assumptions", never "X% chance the price rises").

**Dissemination.**
[ISI: putuskan tim]

| Channel | Content |
|---|---|
| Open source | Pipeline, verifier and evaluation set after the competition, under [ISI: lisensi, mis. MIT/Apache-2.0] |
| Write-up | Publish the field lessons (geo-block with HTTP 200; citation URLs hidden in buttons) |
| Investor communities | Demo to student investment clubs |
| Field partner | Integration discussions through a separate agreement (Art. 13) |

---

# 7 · Team division of labor and third-party resources

## Page 12 — Team, prior work, third-party resources, risk disclosure

**Team** (anonymous roles; all members are active students)

| Member | Role | Owns |
|---|---|---|
| A | Agent & data lead | Ingestion, agent pipeline, verifier, web prototype, tests, traces, demo recording |
| B | Field & evidence (finance) | Interviews, manual baseline, gold set, verification of the clause map |
| C | Product & submission (finance) | Valuation inputs and sources, deck, video, forms, anonymity check |

[ISI: pastikan pembagian B/C sesuai kenyataan] · Field liaison: [ISI: wajib Pasal 7, kalau ada
validasi lapangan nyata] · Advisor: [ISI: ada/tidak; kalau ada, hanya membimbing]

**Prior work.** [CEK: "This is new work, not submitted to other competitions, not commercialized
or funded." Sesuaikan dengan formulir deklarasi.]

**Third-party resources (Art. 13.4)**

| Resource | Provider / license | Purpose | Scope of use |
|---|---|---|---|
| MOPS 公開資訊觀測站 | TWSE, public disclosure system | Primary data and citation target | Material announcements for selected issuers; polite rate limit; raw pages kept locally, not redistributed |
| TWSE / TPEx OpenAPI | Public open data | Prices, shares outstanding | Read-only |
| Gemini 2.5 Flash API (free tier) | Google, Gemini API terms | Triage and extraction (S1–S2) only | Public filings with PII removed. **Free-tier content may be used by Google to improve its products.** |
| FastAPI · Uvicorn · Jinja2 | MIT · BSD-3-Clause · BSD-3-Clause | Web framework, server, templates | Runtime dependencies |
| FinMind | Open-source aggregator | Reachability probe only | Not used in the pipeline; never cited to users |
| Playwright / Chromium · pptxgenjs | Apache-2.0 · MIT | Rendering design mockups and slides | Development only |
| Generative AI coding assistant ([ISI: nama alat, mis. Claude by Anthropic]) | Commercial service | Helped draft code, tests and documentation under the team's direction | Problem definition, design decisions, field validation, evaluation and presentation are the team's own |

**Known limitations and risk disclosure**
1. The clause → input map is provisional until it has been checked line by line against the
   official 重大訊息 list. [CEK: sudah diverifikasi?]
2. Only one issuer has a valuation file, and some of its inputs are still being sourced.
3. There is no currency conversion: non-NTD amounts are rejected, not converted.
4. Budget announcements are treated as a run-rate ("if this level continues"), not as a forecast.
5. Reverse DCF gives the growth rate the market is implying, not an intrinsic value.
6. Ingestion depends on a Taiwan network, and the model's free-tier quota limits daily volume.

---

## Daftar periksa sebelum kirim

**Pemblokir (tanpa ini, 20% nilai tidak tertolong)**
- [ ] Hal. 2–3 terisi data wawancara nyata. Kalau baru sedikit, tulis jumlah sebenarnya; jangan
      klaim Level 1 tanpa satu pun wawancara terdokumentasi.
- [ ] Field liaison ditunjuk dan tercantum di formulir.
- [ ] Deklarasi pihak ketiga di formulir **sama** dengan tabel hal. 12, termasuk Gemini free tier
      dan alat AI generatif yang dipakai menulis kode (Pasal 13: sumber, tujuan, lingkup).

**Perbarui status (`[CEK]`)**
- [ ] Apakah Gemini sudah dipanggil dengan kunci asli (`panggilan_model > 0`)?
- [ ] Apakah pipeline sudah dijalankan di data MOPS asli?
- [ ] Apakah daftar pasal di `app/agent/screen.py` sudah diverifikasi? Kalau sudah, ganti
      "~30 of 711" di diagram dengan angka hasil nyata.
- [ ] Status gold set dan fault-injection set.

**Gambar**
- [ ] `design/export/*.png` berlabel bahasa Indonesia. Juri membaca Inggris/Mandarin, jadi buat
      versi Inggris dulu (sumbernya `design/*.dc.html`, render ulang lewat
      `scripts/render_design.js`).
- [ ] Samakan diagram arsitektur dengan kode: `triage.py` → `extract.py`, "tiga kasus" → empat.

**Anonimitas**
- [ ] Tidak ada nama kampus, jurusan, dosen, atau nama anggota di deck, video, dan nama berkas.
- [ ] Nama produk "Sentinel Saham" (bahasa Indonesia) sebaiknya diganti "Stock Sentinel" di deck.
- [ ] URL repo GitHub tidak dicantumkan (nama akunnya bisa mengidentifikasi).

**Format**
- [ ] PDF ≤ 12 halaman termasuk cover; nama berkas sesuai pola.
- [ ] Video ≤ 4 menit, anggota tim tampil menjelaskan dan mendemokan.
- [ ] Semua tautan diuji dari jendela incognito.
