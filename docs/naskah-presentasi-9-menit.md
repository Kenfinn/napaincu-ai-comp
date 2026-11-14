# Naskah presentasi 9 menit (final 21 Nov)

Dibuat dari deck lengkap 24 slide. Asumsi: 9 menit sudah **termasuk demo langsung 2 menit**; waktu tanya jawab diumumkan terpisah oleh penyelenggara (Pasal 11). Kalau panitia memberi waktu lebih pendek, buang slide 9 (pasar) dan 8 (validasi) dulu.

| Waktu | Slide | Detik |
|---|---|---|
| 0:00 | 1 | 15 |
| 0:15 | 2 | 35 |
| 0:50 | 3 | 45 |
| 1:35 | 6 | 60 |
| 2:35 | 8 | 55 |
| 3:30 | 13 | 70 |
| 4:40 | 14 | 65 |
| 5:45 | 16 | 45 |
| 6:30 | 19 | 30 |
| 7:00 | 21 | 120 |
| **Total** | | **540** |

## 1. Slide 1 (0:00, 15 detik)

**Ucapkan (Inggris):** Good morning. We are Team FEAF. We built an investment assistant that researches, explains and monitors Taiwan stocks, and leaves every decision to the investor.

**Catatan (Indonesia):** Pelan dan tenang. Jangan membaca slide. [ISI: nama pembicara 1]

## 2. Slide 2 (0:15, 35 detik)

**Ucapkan (Inggris):** One investor in our survey told us: AI may give recommendations that are wrong but sound very convincing, and I may not have the expertise to spot the error. That worry is the whole problem. So a question for you: if an AI told you a stock just changed in value, how would you check? Hold that thought. We will come back to it.

**Catatan (Indonesia):** Jeda 2 detik setelah pertanyaan. Ini pembuka dan penutup, jadi harus diingat juri.

## 3. Slide 3 (0:50, 45 detik)

**Ucapkan (Inggris):** Investors are not short of data. News, filings, charts and forums all compete, and the investor filters everything alone. That costs hours, leads to shallow reading, and AI answers cannot be verified. In our survey of ten investors, eight felt overwhelmed, nine wanted to see the AI's reasoning, and eight feared inaccurate answers. Ten people is a small sample, but it shows the need.

**Catatan (Indonesia):** Sebut 'small sample' sendiri; juri menghargai kejujuran angka. [ISI: pembicara 1]

## 4. Slide 6 (1:35, 60 detik)

**Ucapkan (Inggris):** Here is how FEAF works. A new filing arrives from the exchange. Code validates it and screens out routine ones. The language model has one job: read the clause and extract the number with its exact source sentence. From there, code takes over. It checks every number against the source, recomputes the DCF valuation, and decides: publish an alert, or hold it for a person. The model never does arithmetic. We use a DCF because every filing maps to an input we can trace.

**Catatan (Indonesia):** Tunjuk label RULE-BASED / LLM AGENT / HUMAN di slide. Penekanan: model hanya satu langkah. [ISI: pembicara 2]

## 5. Slide 8 (2:35, 55 detik)

**Ucapkan (Inggris):** Why is this an agent and not a chatbot? A chatbot answers when asked. A fixed workflow runs the same steps for every filing. FEAF decides for each filing: publish, hold or archive. It breaks the goal into steps, calls tools, and adapts to results. If the model fails, it switches to a backup and then to rules. If a check fails, it stops and asks a person. Every state is logged.

**Catatan (Indonesia):** Ini menjawab syarat Pasal 3 (state management, tool, kontrol). Tunjuk diagram state di bawah. [ISI: pembicara 2]

## 6. Slide 13 (3:30, 70 detik)

**Ucapkan (Inggris):** We measured it on 46 real filings from 9 November, labelled by a finance member of our team. The agent published zero wrong numbers. The same pipeline without our checker published five. The agent's decision matched the expert in 41 of 46 cases, 89 percent; without the checker, 33 percent. Manual work takes 20 to 30 minutes per filing; the agent takes under a second on average. Model cost for all 46 filings was less than one cent. Limits: these figures were measured before tuning, the labeller is in our team, and accuracy on fresh filings is our next test.

**Catatan (Indonesia):** Jangan menyebut 43/46 atau 42/46 sebagai akurasi (itu di data yang sama dengan penyetelan). Slide ini = kriteria Task Completion 25%. [ISI: pembicara 3]

## 7. Slide 14 (4:40, 65 detik)

**Ucapkan (Inggris):** Safety has three layers. One: a checker, not trust. Seven checks before anything is published. Two: a person decides doubtful cases, and invented numbers can only be archived. Three: information only. No orders, no broker login, no email, no payment. We ran 72 attack cases built on real filings, including hidden instructions and invented numbers, and none got an attacker's number published. We also found one incident ourselves: a company-profile cache briefly kept officer names and emails. It was never shown to users, and a whitelist now blocks it.

**Catatan (Indonesia):** PASTIKAN insiden cache TPEx sudah dilaporkan ke penyelenggara sebelum menyebutnya (Pasal 14.4). Kalau belum, laporkan dulu. [ISI: pembicara 3]

## 8. Slide 16 (5:45, 45 detik)

**Ucapkan (Inggris):** On validation. Level 1: a survey of ten investors with a consent notice. Level 2: 46 real filings labelled by a finance team member, official TWSE, TPEx and MOPS data, and a manual time baseline. Level 3, partly: seven users tried the live website with no real money, and Ask FEAF was the most valued feature. We do not claim a field pilot.

**Catatan (Indonesia):** Sebut field liaison bila sudah ditunjuk [ISI: nama/peran]. Jangan klaim Level 4. [ISI: pembicara 4]

## 9. Slide 19 (6:30, 30 detik)

**Ucapkan (Inggris):** Where next? We start with individual investors in Taiwan: about 14.6 million account holders, 4.3 million of them aged 20 to 40. A free tier, a premium tier, and later licensing to brokers. We sell research and alerts, never buy or sell calls. A commercial rollout will also need licensed market data.

**Catatan (Indonesia):** Angka TAM/SAM belum punya sumber di slide: isi sumbernya, atau hapus angkanya sebelum final. [ISI: pembicara 4]

## 10. Slide 21 (7:00, 120 detik)

**Ucapkan (Inggris):** Back to our opening question: if an AI tells you a stock changed in value, how do you check? With FEAF you ask for the source, and you check the number. Let us check it live.

**Catatan (Indonesia):** DEMO LANGSUNG (2 menit):
7:20-8:00  Alerts: buka kasus 2330 yang TERBIT, tunjukkan kalimat sumber dan 8/8 pemeriksaan lolos.
           SAY: 'This number comes from this sentence in the filing.'
8:00-8:25  Jejak audit kasus itu. SAY: 'Every step is recorded: state, result, time.'
8:25-8:50  Ask FEAF: satu pertanyaan data bersitasi, lalu 'Should I buy 2330?' (ditolak).
           SAY: 'It refuses advice. The investor decides.'
8:50-9:00  SAY: 'AI researches, explains and monitors. The investor decides. Thank you.'
Kasus HELD di Review dilewati demi waktu: ada di slide cadangan.
CADANGAN jika model/koneksi gagal: server turun ke penalar aturan (katakan itu), pakai tangkapan layar atau trace JSON kasus 2330. Latih >= 5 kali.

## Slide cadangan (hanya jika ditanya)

- Slide 5: Why DCF and not P/E, technical analysis or CAPM alone.
- Slide 7: Architecture: sources, one server container, Gemini sees public filing text only; edit routes need an access code.
- Slide 11: Prototype: a held alert (USD amount, no silent conversion) and the review queue. Sample data, rule-based path.
- Slide 12: Prototype: valuation page and the audit trail (the operation trace Appendix 2 asks for).
- Slide 15: User testing: 7 users, no real money. Small sample; say so.
- Slide 18: Limits and worst cases: no currency conversion, no DCF for financial issuers, one-day feed lag, accuracy on fresh filings not yet measured.
- Slide 20: Third-party resources and team roles. Fill the division-of-labour table before the final.
- Slide 22: Is this investment advice? No: research and alerts only, never buy/sell, never trades.
- Slide 23: A real trace: USD amount found, currency check failed, held for review, nothing published.
- Slide 24: Demo plan and fallback.
