# Draf slide tambahan untuk deck Canva (final 21 Nov)

Disusun 13 Nov 2026 dari audit deck Canva (11 slide) terhadap aturan final AAIC 2026 (Appendix 2, Pasal 13, Pasal 14).
Teks di slide berbahasa Inggris (juri membaca Inggris/Mandarin). Catatan untuk tim berbahasa Indonesia.

Semua angka diambil dari `docs/laporan-evaluasi.md`, `docs/hasil-gold-set.md`, `docs/laporan-keamanan.md`,
`docs/laporan-serangan.md`, `docs/diagram-alur.md`, dan `docs/pengungkapan-pihak-ketiga.md`.

- `[ISI: …]` = data yang hanya tim yang punya. Jangan dikarang.
- `[CEK: …]` = angka yang berumur atau belum dijalankan ulang. Perbarui sebelum deck dikirim.

## Urutan yang disarankan

| Posisi | Slide | Status |
|---|---|---|
| 1 | Cover (perbaikan) | ubah |
| 2 | Kutipan R10 | tetap |
| 3–4 | Problem, How we analyse | tetap |
| 5 | Why DCF (perbaikan klaim "100%") | ubah |
| 6 | How it works (alur 8 langkah) | tetap |
| **6b** | **Why agentic + state diagram** | **baru A** |
| **6c** | **Closed loop: personalised, proactive, feedback** | **baru B** |
| 7 | What we built | tetap |
| **7b** | **Results (Appendix 2)** | **baru C** |
| **7c** | **Safety, control, governance (Pasal 14)** | **baru D** |
| 8–9 | User testing, What we will improve | tetap |
| **9b** | **Field validation: what we have, what level** | **baru E** |
| **9c** | **Limits, worst case, recovery** | **baru F** |
| 10 | Market & business model | tambah sumber + deployment |
| **10b** | **Third-party resources and team roles (Pasal 13)** | **baru G** |
| 11 | Closing, live demo | tambah skrip cadangan |
| Cadangan | Q&A backup (H1–H4) | baru, setelah slide 11 |

Total 17 slide + cadangan. Kalau durasi pitch terbatas, A+B bisa digabung, E+F digabung, dan C+D dipertahankan sebagai
inti (Task Completion 25% dan Safety 15%).

---

## Perbaikan slide yang sudah ada

**Cover.** Tambah satu baris kecil di bawah subjudul:
`Category B · SYSTEX · Industry & Public-Sector Co-Creation · Tags: Agentic Workflow, Domain-Specific Agent, Human-in-the-loop`
Tag teknologi cukup yang benar-benar dipakai. Multi-Agent dan RAG **jangan** dicantumkan: sistem ini satu agent
berpemeriksa kode, dan juri menghukum tumpukan teknologi tanpa alasan.

**Slide 5, kotak "100%".** Ganti teks:
- Sekarang: `100% of numbers traced to an exact source sentence`
- Usulan: `0 untraced numbers published · 0/46 on real filings, 0/72 under attack`
Kalimat "audited financial statements" di bawah MOPS juga perlu disesuaikan: angka laporan keuangan datang dari FinMind,
dengan tautan ke MOPS. `[CEK: uji 10 angka FinMind vs MOPS (tugas B3b) belum tercatat selesai; kalau belum, jangan klaim "sama dengan MOPS".]`

**Slide 10 (market).** Tambah sumber di catatan kaki untuk TAM 14,58 juta dan SAM 4,29 juta `[ISI: sumber dan tahun, mis. TDCC/TWSE]`.
Tambah satu baris deployment: `Runs today as a single container (Docker on Dokploy); model cost about USD 0.007 per 46 filings; data from open TWSE/TPEx/MOPS sources.`

**Slide 11 (closing).** Tambah di catatan pembicara skrip demo 3 menit dan rencana cadangan (lihat Slide H4).

---

## Slide A (6b): Why agentic, and how state is managed

**Title:** Why this needs an agent, not a chatbot

**Left, tiga baris perbandingan:**

| Approach | What happens with a new filing | Why it falls short |
|---|---|---|
| Chatbot / RAG | Answers when asked, quotes text | Never starts, cannot recompute a valuation, no check on its own numbers |
| Fixed workflow | Same steps for every filing | Cannot read free-text clauses or decide when to stop and ask a person |
| **FEAF agent** | Decides per filing: publish, hold, or archive | Plans steps, uses tools, adjusts on the result, stops for a human when unsure |

**Right, diagram state** (versi sederhana dari `docs/diagram-alur.md` bagian 2, gambarnya di `docs/diagram/`):

`FETCHED → VALIDATED → SCREENED → TRIAGED → EXTRACTED → VERIFIED → VALUED → PUBLISHED`
dengan tiga jalur keluar: `ARCHIVED` (tidak relevan), `HELD` (tunggu manusia), dan `HUMAN REVIEW → PUBLISHED / ARCHIVED`.

**Satu baris di bawah:** `Decisions are made by code that can be audited. The model is used in one step only: reading the clause.`

**Catatan pembicara.** Agent memecah tujuan ("beri investor angka yang bisa diperiksa") menjadi langkah berurutan dan
bergantung satu sama lain. Ia memanggil tool (TWSE/TPEx OpenAPI, FinMind, kalkulator DCF, model bahasa), menyesuaikan
langkah berikut berdasarkan hasil (model gagal → model cadangan → penalar aturan; pemeriksa gagal → HELD) dan
berhenti untuk manusia pada kasus ragu. Itu memenuhi butir 1 wajib dan butir 2, 3, 4 syarat minimum.
`[CEK: bagian "model dipakai di satu langkah" konsisten dengan slide 6 yang melabeli dua langkah sebagai LLM AGENT: triase dan ekstraksi dilakukan model hanya untuk pasal 20; jalur lain diurai kode.]`

---

## Slide B (6c): Closing the loop

**Title:** From personalised intelligence to continuous optimisation

Empat kotak berurutan (sesuai alur inti tantangan SYSTEX):

| Stage | What FEAF does | Where |
|---|---|---|
| Personalised intelligence | Risk profile (conservative / moderate / aggressive) changes thresholds, DCF class, strengths and watch-outs | `/ambang`, profile switch |
| Proactive delivery | Server checks filings every 10 minutes and raises an alert without being asked | Watchlist, Alerts |
| Behavioural feedback | 👍 / 👎 on each alert | Alert page |
| Continuous optimisation | 👎 raises that clause's threshold by 0.05, 👍 lowers it by 0.02, within 0.40–0.90 | Next triage |

**Catatan pembicara.** Tunjukkan satu contoh: dua 👎 pada pasal yang sama membuat peringatan serupa berikutnya
diarsipkan dengan alasan "skor di bawah ambang". `[CEK: A2 dinyatakan lulus QA di rencana-finalis; ulangi di server sebelum demo.]`
Catatan: ambang berlaku **satu per server** (satu investor per server), keputusan 10 Nov. Jangan klaim personalisasi per pengguna.

---

## Slide C (7b): Results, measured on real filings

**Title:** Measured, not promised

**Satu kalimat uji:** `46 real MOPS filings (9 Nov 2026), labelled by a finance team member. Success = same publish / hold / archive decision as the expert and no wrong number published.`

| Metric (rule path, before any tuning) | FEAF agent | Same pipeline without checker |
|---|---|---|
| Wrong numbers published | **0 / 46** | 5 / 46 |
| Decision matches expert | 41 / 46 (89%) | 15 / 46 (33%) |
| Signal level matches expert | 21 / 29 (72%) | 0 / 29 |
| Held for a person | 13 / 46 (28%) | 33 / 46 (72%) |

**Baris kedua, kecil:**

| | Result |
|---|---|
| Manual baseline | 20–30 min per filing (25 used), about 1,150 analyst-minutes for 46 |
| Agent time per filing | 0.7 s mean, 9.9 s max (Gemini 3.6 Flash, temperature 0) |
| Model cost | USD 0.0069 for 46 filings |
| Ask FEAF, 52 questions in 3 languages | 27/27 out-of-scope and injected questions refused · 0 buy/sell words reached the user · 50/52 correct |
| Operation trace | Every decision has an auditable trace at `/jejak/<id>` |

**Catatan pembicara dan peringatan kejujuran:**
- 41/46 adalah angka **sebelum** penyetelan. Angka sesudah penyetelan (43/46 aturan, 42/46 model) bersifat in-sample, jangan dilaporkan sebagai akurasi.
  Katakan terus terang: "out-of-sample belum diukur." Sebaiknya siapkan set buta 15–20 filing (langkah berikut di laporan evaluasi).
- Dua kegagalan Ask FEAF (50/52) adalah false positive pemeriksa: pengguna menerima jawaban template bersumber, bukan angka salah.
  Sudah diperbaiki 11 Nov, **belum dijalankan ulang dengan Gemini** `[CEK: jalankan ulang scripts/evaluasi.py --chat sebelum deck final.]`
- Pelabel gold set adalah anggota tim sendiri. Sebutkan di slide atau catatan agar tidak terkesan validasi independen.
- Tabel tingkat operasi server: `[CEK: angka 1,106 filing / 53% / 35% / 12% HELD diambil 11 Nov 09:22 UTC. Ambil ulang dari /sehat.]`

Kolom yang diminta Appendix 2 dan sudah punya angka: sukses, akurasi, latensi rata-rata dan maksimum, biaya, intervensi manusia (12% di server),
kategori error, trace. **Belum ada** di slide: tool-call success rate dan jumlah retry (ada di laporan: retry 0, fallback 0 pada run model) dan tingkat terminasi.
Cantumkan di catatan pembicara atau slide cadangan.

---

## Slide D (7c): Safety, control and governance

**Title:** Built so a wrong number cannot reach an investor

**Kiri, tiga lapis kendali:**

1. **Checker, not trust.** Seven checks before publishing: label, quote, digits, currency, written unit, conversion, magnitude. The model never does arithmetic: DCF runs in plain code.
2. **A person decides the doubtful cases.** Held filings go to a review queue. Invented numbers can only be archived, never approved. Severe clauses (default, trading halt, mass layoff) are always held.
3. **No action beyond information.** No orders, no broker login, no email, no payment. Edit routes need an access code. Analysis carries no buy/sell label (FSC rules).

**Kanan, tabel risiko Pasal 14 (satu baris tiap kategori, hasil singkat):**

| Risk | Protection | Evidence |
|---|---|---|
| Prompt injection | Pattern scan + every number needs a verbatim source sentence | 0 / 72 attacker numbers published (12 attack types) |
| Unauthorised tool use | Closed tool list, no shell or order tool | Edit routes return 401 without code |
| Data leakage | Whitelist of public company fields | TPEx incident 10 Nov, fixed same day |
| Hallucinated numbers | Code computes, checker matches every number to tool output | Failed claim → HELD |
| Bias (sector) | Financial-sector issuers flagged "DCF not applicable" | Test in suite |
| Malicious input | Escaped templates, strict stock-code pattern, 500-character limit | Tests in suite |
| Supply chain | Four pinned Python libraries, no JavaScript framework | `requirements.txt` |
| Service failure | Retry, backup model, then rule reasoner; cache keeps pages open | `/sehat` health page |

**Satu baris jujur di bawah:** `Open gaps: shared access code (no roles), no per-IP rate limit, injection patterns are regex-based; the number check is the backstop.`

**Catatan pembicara.** Sebutkan insiden TPEx dengan lugas: cache profil emiten TPEx sempat menyimpan nama pejabat dan email
kontak perusahaan hingga 10 Nov (commit `e4572d6`), tidak pernah ditampilkan ke publik, diperbaiki dengan daftar izin dan tes otomatis.
Pasal 14.4 meminta kejujuran soal insiden dan melarang menutupinya.
Aturan juga melarang password, API key, dan data pribadi di dokumen. `[CEK: pastikan tidak ada kunci di repo dan tidak ada nama pejabat di deck; berkas "API KEY .txt" di akar proyek jangan ikut terkirim.]`

---

## Slide E (9b): Field validation: what we have

**Title:** Evidence from real users and real filings

| Level | Evidence | Status |
|---|---|---|
| 1 Needs | Survey of 10 investors, 6–8 Oct 2026, PDPA consent notice (8/10 overwhelmed, 9/10 want to see reasoning, 8/10 fear wrong AI answers) | Done (declared in preliminary) |
| 2 Data / process | 46 real filings from 9 Nov labelled by a finance team member; manual time baseline; official TWSE/TPEx/MOPS data; documented flow and API sources | Done, labeller is in-team |
| 3 Prototype trial | 7 users tested the live website, no real money, no trading; Ask FEAF most valued | Done, small sample |
| 4 Pilot | — | Not claimed |

**Catatan pembicara.** Juri menilai "Field Impact" 20% dengan patokan Level 2 ke atas. Klaim yang aman: Level 2 tercapai,
Level 3 sebagian (7 pengguna). Jangan klaim Level 4.

`[ISI: field liaison, kontak lapangan, dan siapa yang diwawancarai (investor ritel, analis?). Rapat sebelumnya mencatat field liaison belum ditunjuk (rencana-dan-status.md baris 89). Aturan resmi Pasal 6.2 mewajibkan bila ada validasi lapangan.]`
`[ISI: hasil user testing yang lebih kuat. "4/6 valid answers" di slide 8 terlihat lemah; tambahkan metrik tugas (waktu, berhasil/tidak) bila ada.]`
`[ISI: perbandingan sebelum/sesudah dari responden: waktu mereka mengumpulkan data hari ini vs dengan FEAF.]`

---

## Slide F (9c): Limits, worst case and recovery

**Title:** What FEAF does not do, and what happens when it fails

**Known limits:**
- Accuracy is measured on 46 filings, labelled in-team. A blind set of fresh filings is the next step.
- No currency conversion: USD and other foreign-currency amounts are held for a person.
- Financial-sector issuers get no DCF.
- The exchange feed lags about one day; older history needs a Taiwan network.
- DCF inputs use fixed market constants (risk-free 1.94%, equity risk premium 5.01%), beta from two years of weekly returns, 1.0 when data is short.

**Worst cases:**

| Worst case | What happens | Recovery |
|---|---|---|
| Model returns an invented or injected number | Checker fails it, nothing published | Held, failing check named in the trace |
| Model down, rate-limited or out of credit | Retry → backup model → rule reasoner | Reported on `/sehat`; next cycle retries |
| Run takes too long | 90-second / 40-call cap per run | Remaining filings answered next cycle |
| Server restart | Data and traces live in `/data` volume | `/sehat` shows running code version |

---

## Slide G (10b): Third-party resources and who did what (Pasal 13)

**Title:** Open sources, tools and team roles

**Tabel (ringkas dari `docs/pengungkapan-pihak-ketiga.md`):**

| Type | What | Used for |
|---|---|---|
| Market data | TWSE / TPEx OpenAPI, MOPS | Filings, prices, shares, company profile |
| Financial statements | FinMind | Quarterly statements (cached 12 h) |
| Model | Google Gemini 3.6 Flash (backup 3.5 Flash) | Read clause text, Ask FEAF; public text only, no personal data |
| Reference inputs | Damodaran (ERP 5.01%), Taiwan 10-year bond (1.94%) | WACC |
| Development tools | Claude Code, Antigravity | Pair programming; they do not run inside the product |
| Libraries | FastAPI, uvicorn, Jinja2, httpx (MIT / BSD) | Web app and tests |

**Teks kecil:** `All third-party data and model use follows each licence. Only public filings are sent to the model.`

**Pembagian kerja (wajib):**

| Part | Done by | Role of AI tools |
|---|---|---|
| `[ISI: bagian]` | `[ISI: nama anggota, tanpa menambah identitas yang tidak perlu]` | `[ISI]` |

Tabel di `pengungkapan-pihak-ketiga.md` bagian 2 masih kosong sengaja untuk diisi tim. Penyelenggara juga membatasi peran
pembimbing dan penasihat teknis: mereka tidak boleh mengerjakan desain inti, kode, evaluasi, atau presentasi. Pastikan tabel ini sesuai kenyataan.
`[CEK: Yahoo Finance dan alat tangkap layar Playwright, Mermaid, serta skill humanizer/anti-slop ada di daftar penuh; di slide cukup sebut yang memengaruhi produk.]`

---

## Slide cadangan (setelah slide 11)

### H1. Why not P/E, technical analysis, or a single LLM?
Sudah ada di slide 5. Tambahkan angka: pipeline "tanpa pemeriksa" menerbitkan 5 dari 46 angka salah (11%).

### H2. Is this investment advice?
`No. FEAF shows research, valuation and alerts. It never says buy or sell, never trades, and shows an FSC-style disclaimer on every stock and valuation page. The investor decides.`

### H3. What if the model is attacked or wrong?
Gunakan satu trace nyata: TSMC pasal 20, 11 Nov. Model menemukan 4 jumlah, semuanya US$, keyakinan 0.55. Pemeriksa mata uang gagal,
filing **HELD FOR REVIEW**, tidak ada angka terbit. Buka `/jejak/2330-2026-11-10-211853`.

### H4. Demo script and fallback
1. Watchlist → Alerts: kasus 2330 TERBIT, 8/8 cek lolos.
2. Buka jejak audit kasus itu: tunjukkan langkah dan sumber kalimat.
3. Tanya FEAF: satu pertanyaan data (sitasi) dan satu pertanyaan "should I buy 2330?" yang ditolak.
4. Halaman Review: satu kasus HELD, keputusan manusia tercatat.

Cadangan jika koneksi atau model gagal: tangkapan layar tiap langkah di slide cadangan, plus trace JSON `eval/hasil/jejak-contoh-2330-2026-11-10-211853.json`.
Server jatuh ke jalur aturan otomatis, jadi demo tetap berjalan tetapi tanpa model: sebut itu bila terjadi. Latih ≥5 kali (rencana-finalis).

---

## Daftar periksa sebelum deck dikirim

- [ ] Angka server (`/sehat`) diambil ulang, bukan 11 Nov
- [ ] `evaluasi.py --chat` dijalankan ulang dengan Gemini setelah perbaikan 11 Nov
- [ ] Klaim "100%" di slide 5 diganti
- [ ] Field liaison, kontak lapangan, dan pembagian kerja terisi
- [ ] Sumber TAM/SAM terisi
- [ ] Tidak ada kunci API, nama pribadi, atau data rahasia di deck atau catatan pembicara
- [ ] Cover memuat Category B / SYSTEX / tema / tag
- [ ] Durasi pitch diuji; jika perlu, gabungkan A+B dan E+F
