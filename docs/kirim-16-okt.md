# Kirim 16 Okt — apa diunggah ke mana

Tenggat **16 Oktober 2026, 23:59**. Berkas ini memetakan tujuh isian form pendaftaran ke
berkas yang sudah jadi, plus teks bahasa Inggris yang tinggal ditempel.

Bahan yang dipakai:
- **Deck 5 halaman buatan teman** (FEAF briefing). Isinya tidak diubah; hanya nomor halaman,
  nomor bagian, dan satu rujukan halaman yang disesuaikan.
- **Survei 10 responden**, 6–8 Okt 2026, dari form "QUESTIONS LIST OF AI COMPETITION". Semua
  angka di deck teman sudah dicocokkan ulang dengan respons mentahnya dan cocok.
- **Repo ini**: agent, verifier, tes, dan data MOPS.

Skrip pembangun deck ada di `slides/build_proposal_deck.py`, dengan masukan deck teman.
Berkas PDF, PPTX, dan materi lapangan **tidak di-commit** karena memuat kutipan responden.

## Ringkasan

| # | Isian form | Wajib | Yang diisi |
|---|---|---|---|
| 1 | Proposal Presentation / Pitch Deck | Ya | PDF 12 halaman (5 halaman teman + cover + 6 halaman baru) |
| 2 | Concept / Demo Video Link | Ya | **Belum ada — harus direkam.** Naskah di bawah |
| 3 | Field Verification Level | Ya | Level 1 + teks di bawah |
| 4 | Field Requirements & Verification Materials | Ya | PDF materi lapangan 4 halaman (sudah tanpa nama/email) |
| 5 | GitHub / GitLab link | Opsional (final) | **Kosongkan** |
| 6 | README / technical docs | Opsional (final) | **Kosongkan** |
| 7 | Third-party resource disclosure | Opsional di form | **Isi** — Pasal 13.4 tetap mewajibkan pengungkapan |

---

## 1 · Pitch deck

Unggah `DesignatedField_IndustryPublicSectorCoCreation_FEAF_proposal.pdf` (12 halaman A4, font
tertanam). Pola nama dari situs: `group_theme_team_proposal.pdf`.

| Hal. | Isi | Asal |
|---|---|---|
| 1 | Cover: kategori, tantangan, tema, tag teknologi, level validasi, daftar isi | baru |
| 2–4 | Masalah investor · customer journey · kenapa agentic | teman |
| 5 | Alur tugas & enam state agent, tiga jalan berhenti, syarat Pasal 4 | baru |
| 6 | Arsitektur, aliran data, deployment | baru |
| 7 | State, izin, ancaman & respons keamanan | baru |
| 8 | Prototipe: keluaran asli untuk satu test filing + status jujur | baru |
| 9 | Test case, tiga baseline, metrik Appendix 2 | baru |
| 10–11 | Pasar & model bisnis · roadmap validasi + sumber | teman |
| 12 | Peran tim, resource pihak ketiga, keterbatasan | baru |

**Cek bersama teman sebelum unggah** (yang tidak kuketahui pasti):
1. **Hal. 12, kartu tim.** Kutulis "Technical · 1 member" dan "Finance & field · 2 members".
   Sesuaikan kalau pembagiannya lain.
2. **Hal. 12, Originality.** Kalimatnya: karya baru, belum pernah dilombakan, menang,
   dikomersialkan, atau didanai. Hapus kalau tidak benar.
3. **Hal. 12, baris "Generative AI assistants".** Kalau teman memakai alat AI lain untuk
   deck-nya (mis. ChatGPT), sebut juga di sana.
4. **Hal. 1, Level 1.** Harus sama dengan isian nomor 3.

Kalau mau mengedit, buka `FEAF_Proposal_12hal_editable.pptx`. Font Inter dan Manrope (gratis di
Google Fonts) harus terpasang, kalau tidak PowerPoint menggantinya dan teks bisa meluber.

## 2 · Video ≤ 4 menit (harus direkam hari ini)

Aturan: anggota tim **tampil** menjelaskan dan mendemokan. Unggah ke YouTube (*unlisted*) atau
Google Drive (*anyone with the link*), lalu buka tautannya di jendela incognito untuk
memastikan bisa diputar.

Demo bisa jalan dari laptop mana pun tanpa jaringan Taiwan dan tanpa kunci API:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest discover -s tests      # Ran 14 tests ... OK
uvicorn app.main:app                       # buka http://127.0.0.1:8000
```

Aplikasinya akan menampilkan pita "Data contoh". **Biarkan**: itu jujur dan sesuai hal. 8 deck.
Tampilan aplikasi berbahasa Indonesia, jadi narasikan dalam bahasa Inggris (tambah teks
terjemahan kalau sempat).

| Waktu | Siapa | Layar | Yang diucapkan (Inggris) |
|---|---|---|---|
| 0:00–0:25 | Anggota keuangan, wajah | Deck hal. 2 | "We surveyed ten self-directed investors. Eight in ten feel overwhelmed by news and data, nine in ten want to check an AI's reasoning before trusting it, and eight in ten fear hallucinated numbers." |
| 0:25–0:50 | Sama | Deck hal. 4 → 5 | "So we didn't build a chatbot. Our agent watches official filings, decides when a filing matters, and can stop at three points. The investor always makes the decision." |
| 0:50–1:15 | Anggota teknis, wajah | Deck hal. 6 | "The model touches only two of eleven boxes. Numbers come from the filing and from arithmetic. MOPS blocks traffic from outside Taiwan with an HTTP 200 page, so we validate the shape of every response." |
| 1:15–1:30 | Teknis, layar | Terminal | Jalankan tes: "Fourteen automated tests, including prompt-injection and data-leak tests, all pass." |
| 1:30–2:00 | Teknis, layar | Feed → peringatan TSMC | "Four test filings, four different endings. This one was published: here's the official source link, the exact sentence, and eight verifier checks, all passed." |
| 2:00–2:25 | Teknis, layar | Kasus injeksi → jejak audit | "This filing hides an instruction telling the AI to record a fake number and skip human review. The injection is logged, and only the real number is published." |
| 2:25–2:45 | Teknis, layar | Kasus USD | "This one is rejected: the amount is in US dollars and the model has no exchange rate, so it refuses instead of guessing." |
| 2:45–3:15 | Anggota keuangan | Deck hal. 7 → 9 | "No trade execution exists anywhere. We evaluate on traceability first, against three baselines: the manual process, a rule-based workflow, and a single LLM without a verifier." |
| 3:15–3:45 | Semua | Deck hal. 11 | "Next: follow-up interviews, a labelled gold set, and a sandbox trial with real investors before the final. AI researches, analyses, explains and monitors; the investor decides." |

**Anonimitas di video:** tidak boleh ada nama kampus, logo, jaket/almamater, kartu mahasiswa,
nama dosen, atau nama lengkap anggota. Sembunyikan nama akun di prompt terminal, tab browser, dan
URL GitHub (`Kenfinn`). Jangan perlihatkan halaman nilai valuasi TSMC sebagai temuan, karena
inputnya belum lengkap (hal. 8 dan 12 deck menyatakan ini).

## 3 · Field Verification Level

Pilih **Level 1**. Teks pendamping:

```
Level 1 (needs interviews). We documented pain points and needs with 10 self-directed
investors (ages 18–34, up to 3 years' experience) through a structured questionnaire with
open-text answers, 6–8 Oct 2026, under a PDPA Art. 8 consent notice. Level 2 evidence is
in progress: 711 real MOPS material-information filings pulled from a Taiwan network on
14 Sep 2026 (100% with permanent source URLs), documented data-access endpoints, and
labelled test cases for the agent.
```

Kenapa bukan Level 2: Level 2 menuntut data/proses yang tervalidasi bersama lapangan. Kita
baru punya data publik dan test case buatan sendiri, belum gold set. Mengklaim Level 1 dengan
bukti Level 2 yang sedang berjalan lebih aman daripada klaim berlebih yang bisa dibantah juri.

## 4 · Field Requirements & Verification Materials

Unggah `FEAF_Field_Need_and_Validation_Materials.pdf` (4 halaman). Isinya: metode dan
persetujuan, profil R01–R10 tanpa nama/email, hasil per pertanyaan, kutipan (termasuk satu yang
tidak setuju), tabel kebutuhan → keputusan desain, bukti data MOPS, keterbatasan, dan langkah
berikutnya.

Kalau ada kolom teks:

```
Need source: self-directed investors research alone across many sources and cannot verify
what AI tools tell them. Target users: self-directed investors aged 18–34 in their first
~3 years. Evidence (questionnaire, n = 10, 6–8 Oct 2026): 8/10 feel overwhelmed at least
sometimes; 5/10 say analysing financial data consumes most of their time; 9/10 want to
inspect the AI's reasoning trail; 8/10 name accuracy or hallucination as their top concern;
8/10 want any trade to require their approval. Data validation: 711 real MOPS filings from
5 issuers, and the geo-blocking behaviour of the official sources documented. Full
de-identified materials attached.
```

> **Jangan tempel tautan spreadsheet Responses.** Spreadsheet itu memuat nama lengkap dan
> email responden, sementara consent notice di form menjanjikan data dianonimkan. Tautannya
> juga berbentuk `?usp=sharing`, jadi **periksa pengaturan berbagi** dan batasi hanya untuk
> anggota tim.

Nama dan kontak field liaison diisi di kolom kontak form pendaftaran, bukan di PDF, karena
PDF ikut direview secara anonim.

## 5 & 6 · GitHub dan README — kosongkan sekarang

Keduanya opsional dan baru dinilai di final. Mengisinya sekarang justru berisiko: nama akun
GitHub bisa mengidentifikasi tim, dan isi repo berbahasa Indonesia. Siapkan untuk 13 November.

## 7 · Third-party resource disclosure — isi

```
1. MOPS (TWSE public disclosure system) — primary data and citation target; read-only,
   polite rate limit; raw pages kept locally, not redistributed.
2. TWSE / TPEx OpenAPI (public open data) — prices and shares outstanding; read-only.
3. Google Gemini 2.5 Flash API, free tier (Gemini API terms) — triage and extraction steps
   only; only public filings with personal data removed are sent; free-tier content may be
   used by Google to improve its products.
4. FastAPI (MIT), Uvicorn (BSD-3-Clause), Jinja2 (BSD-3-Clause) — web prototype.
5. Playwright (Apache-2.0), pptxgenjs (MIT) — rendering design mock-ups and slides only.
6. FinMind (open-source aggregator) — reachability probe only; not used in the pipeline.
7. Google Forms — survey collection under a PDPA consent notice; results de-identified.
8. Generative AI assistants (e.g. Claude by Anthropic) — drafting code, tests,
   documentation and slide text under the team's direction; problem definition, design
   decisions, field validation, analysis and presentation are the team's own.
9. Market and industry sources cited on page 11 of the deck — market sizing and benchmarks.
```

Baris 8 wajib jujur (Pasal 13): sebagian kode dan dokumen repo ini, juga halaman tambahan deck,
ditulis dengan bantuan Claude.

## Sebelum klik submit

- [ ] Empat poin "cek bersama teman" di bagian 1 sudah diputuskan
- [ ] Video terunggah, durasi ≤ 4:00, bisa diputar dari incognito
- [ ] Tidak ada nama kampus/jurusan/dosen di deck, video, PDF, maupun nama berkas
- [ ] Spreadsheet Responses tidak dibagikan publik dan tidak ditautkan di form
- [ ] Level di form = level di cover deck = level di PDF lapangan (Level 1)
- [ ] Field liaison terisi di form pendaftaran
- [ ] Kirim hari ini (15 Okt); tanggal 16 hanya cadangan
