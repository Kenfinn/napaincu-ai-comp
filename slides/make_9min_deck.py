"""Cut the full final deck down to a 9-minute talk and write a timed speaker script.

Usage: python make_9min_deck.py <full.pptx> <out.pptx> <out-script.md>

Main talk = 10 slides (9:00 including a 2-minute live demo). The rest follows a
"Backup" divider and is used only for Q&A. Slide numbers refer to the 24-slide
full deck built by build_final_deck.js.
"""
import sys

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER

SRC, OUT, MD = sys.argv[1:4]

# (full-deck slide number, start, seconds, say, tip)
TALK = [
    (1, "0:00", 15,
     "Good morning. We are Team FEAF. We built an investment assistant that researches, "
     "explains and monitors Taiwan stocks, and leaves every decision to the investor.",
     "Pelan dan tenang. Jangan membaca slide. [ISI: nama pembicara 1]"),
    (2, "0:15", 35,
     "One investor in our survey told us: AI may give recommendations that are wrong but "
     "sound very convincing, and I may not have the expertise to spot the error. That worry "
     "is the whole problem. So a question for you: if an AI told you a stock just changed in "
     "value, how would you check? Hold that thought. We will come back to it.",
     "Jeda 2 detik setelah pertanyaan. Ini pembuka dan penutup, jadi harus diingat juri."),
    (3, "0:50", 45,
     "Investors are not short of data. News, filings, charts and forums all compete, and the "
     "investor filters everything alone. That costs hours, leads to shallow reading, and AI "
     "answers cannot be verified. In our survey of ten investors, eight felt overwhelmed, "
     "nine wanted to see the AI's reasoning, and eight feared inaccurate answers. Ten people "
     "is a small sample, but it shows the need.",
     "Sebut 'small sample' sendiri; juri menghargai kejujuran angka. [ISI: pembicara 1]"),
    (6, "1:35", 60,
     "Here is how FEAF works. A new filing arrives from the exchange. Code validates it and "
     "screens out routine ones. The language model has one job: read the clause and extract "
     "the number with its exact source sentence. From there, code takes over. It checks every "
     "number against the source, recomputes the DCF valuation, and decides: publish an alert, "
     "or hold it for a person. The model never does arithmetic. We use a DCF because every "
     "filing maps to an input we can trace.",
     "Tunjuk label RULE-BASED / LLM AGENT / HUMAN di slide. Penekanan: model hanya satu langkah. [ISI: pembicara 2]"),
    (8, "2:35", 55,
     "Why is this an agent and not a chatbot? A chatbot answers when asked. A fixed workflow "
     "runs the same steps for every filing. FEAF decides for each filing: publish, hold or "
     "archive. It breaks the goal into steps, calls tools, and adapts to results. If the model "
     "fails, it switches to a backup and then to rules. If a check fails, it stops and asks a "
     "person. Every state is logged.",
     "Ini menjawab syarat Pasal 3 (state management, tool, kontrol). Tunjuk diagram state di bawah. [ISI: pembicara 2]"),
    (13, "3:30", 70,
     "We measured it on 46 real filings from 9 November, labelled by a finance member of our "
     "team. The agent published zero wrong numbers. The same pipeline without our checker "
     "published five. The agent's decision matched the expert in 41 of 46 cases, 89 percent; "
     "without the checker, 33 percent. Manual work takes 20 to 30 minutes per filing; the "
     "agent takes under a second on average. Model cost for all 46 filings was less than one "
     "cent. Limits: these figures were measured before tuning, the labeller is in our team, "
     "and accuracy on fresh filings is our next test.",
     "Jangan menyebut 43/46 atau 42/46 sebagai akurasi (itu di data yang sama dengan penyetelan). "
     "Slide ini = kriteria Task Completion 25%. [ISI: pembicara 3]"),
    (14, "4:40", 65,
     "Safety has three layers. One: a checker, not trust. Seven checks before anything is "
     "published. Two: a person decides doubtful cases, and invented numbers can only be "
     "archived. Three: information only. No orders, no broker login, no email, no payment. We "
     "ran 72 attack cases built on real filings, including hidden instructions and invented "
     "numbers, and none got an attacker's number published. We also found one incident "
     "ourselves: a company-profile cache briefly kept officer names and emails. It was never "
     "shown to users, and a whitelist now blocks it.",
     "PASTIKAN insiden cache TPEx sudah dilaporkan ke penyelenggara sebelum menyebutnya (Pasal 14.4). "
     "Kalau belum, laporkan dulu. [ISI: pembicara 3]"),
    (16, "5:45", 45,
     "On validation. Level 1: a survey of ten investors with a consent notice. Level 2: 46 "
     "real filings labelled by a finance team member, official TWSE, TPEx and MOPS data, and "
     "a manual time baseline. Level 3, partly: seven users tried the live website with no "
     "real money, and Ask FEAF was the most valued feature. We do not claim a field pilot.",
     "Sebut field liaison bila sudah ditunjuk [ISI: nama/peran]. Jangan klaim Level 4. [ISI: pembicara 4]"),
    (19, "6:30", 30,
     "Where next? We start with individual investors in Taiwan: about 14.6 million account "
     "holders, 4.3 million of them aged 20 to 40. A free tier, a premium tier, and later "
     "licensing to brokers. We sell research and alerts, never buy or sell calls. A "
     "commercial rollout will also need licensed market data.",
     "Angka TAM/SAM belum punya sumber di slide: isi sumbernya, atau hapus angkanya sebelum final. [ISI: pembicara 4]"),
    (21, "7:00", 120,
     "Back to our opening question: if an AI tells you a stock changed in value, how do you "
     "check? With FEAF you ask for the source, and you check the number. Let us check it live.",
     "DEMO LANGSUNG (2 menit):\n"
     "7:20-8:00  Alerts: buka kasus 2330 yang TERBIT, tunjukkan kalimat sumber dan 8/8 pemeriksaan lolos.\n"
     "           SAY: 'This number comes from this sentence in the filing.'\n"
     "8:00-8:25  Jejak audit kasus itu. SAY: 'Every step is recorded: state, result, time.'\n"
     "8:25-8:50  Ask FEAF: satu pertanyaan data bersitasi, lalu 'Should I buy 2330?' (ditolak).\n"
     "           SAY: 'It refuses advice. The investor decides.'\n"
     "8:50-9:00  SAY: 'AI researches, explains and monitors. The investor decides. Thank you.'\n"
     "Kasus HELD di Review dilewati demi waktu: ada di slide cadangan.\n"
     "CADANGAN jika model/koneksi gagal: server turun ke penalar aturan (katakan itu), "
     "pakai tangkapan layar atau trace JSON kasus 2330. Latih >= 5 kali."),
]

# Backup slides (full-deck numbers), kept for Q&A only.
BACKUP = {
    5: "Why DCF and not P/E, technical analysis or CAPM alone.",
    7: "Architecture: sources, one server container, Gemini sees public filing text only; edit routes need an access code.",
    11: "Prototype: a held alert (USD amount, no silent conversion) and the review queue. Sample data, rule-based path.",
    12: "Prototype: valuation page and the audit trail (the operation trace Appendix 2 asks for).",
    15: "User testing: 7 users, no real money. Small sample; say so.",
    18: "Limits and worst cases: no currency conversion, no DCF for financial issuers, one-day feed lag, accuracy on fresh filings not yet measured.",
    20: "Third-party resources and team roles. Fill the division-of-labour table before the final.",
    22: "Is this investment advice? No: research and alerts only, never buy/sell, never trades.",
    23: "A real trace: USD amount found, currency check failed, held for review, nothing published.",
    24: "Demo plan and fallback.",
}

MAIN_ORDER = [t[0] for t in TALK]
BACKUP_ORDER = list(BACKUP.keys())

prs = Presentation(SRC)
lst = prs.slides._sldIdLst
ids = list(lst)
total = len(ids)
if total != 24:
    sys.exit(f"expected the 24-slide full deck, found {total}")

# divider slide on the DARK layout
dark = next(l for l in prs.slide_layouts if l.name == "DARK")
div = prs.slides.add_slide(dark)
for ph in div.placeholders:
    if ph.placeholder_format.type == PP_PLACEHOLDER.TITLE:
        ph.text_frame.text = "Backup"
div.notes_slide.notes_text_frame.text = "BACKUP DIVIDER. Do not present. Use the slides after this one only if asked."
div_id = list(lst)[-1]

keep = MAIN_ORDER + ["DIV"] + BACKUP_ORDER
id_by_num = {i + 1: ids[i] for i in range(total)}

# notes first (slides are still addressable by their original index)
slides = list(prs.slides)
for num, start, secs, say, tip in TALK:
    sl = slides[num - 1]
    sl.notes_slide.notes_text_frame.text = (
        f"[{start}, {secs} s]\nSAY: {say}\n\nTIP: {tip}"
    )
for num, line in BACKUP.items():
    sl = slides[num - 1]
    sl.notes_slide.notes_text_frame.text = "BACKUP, use only if asked.\n" + line + "\n\n" + (
        sl.notes_slide.notes_text_frame.text or ""
    )

# drop slides not kept
kept_ids = {id_by_num[n].rId for n in MAIN_ORDER + BACKUP_ORDER}
for el in ids:
    if el.rId not in kept_ids:
        prs.part.drop_rel(el.rId)
        lst.remove(el)

# reorder
for el in list(lst):
    lst.remove(el)
for k in keep:
    lst.append(div_id if k == "DIV" else id_by_num[k])

# drop the old section list (it names slides that no longer exist)
P14 = "{http://schemas.microsoft.com/office/powerpoint/2010/main}sectionLst"
root = prs.part._element
for sec in list(root.iter(P14)):
    ext = sec.getparent()
    ext_lst = ext.getparent()
    ext_lst.remove(ext)
    if len(ext_lst) == 0:
        ext_lst.getparent().remove(ext_lst)

prs.save(OUT)

# markdown script
tot = sum(t[2] for t in TALK)
rows = ["# Naskah presentasi 9 menit (final 21 Nov)", "",
        "Dibuat dari deck lengkap 24 slide. Asumsi: 9 menit sudah **termasuk demo langsung 2 menit**; "
        "waktu tanya jawab diumumkan terpisah oleh penyelenggara (Pasal 11). Kalau panitia memberi waktu "
        "lebih pendek, buang slide 9 (pasar) dan 8 (validasi) dulu.", "",
        "| Waktu | Slide | Detik |", "|---|---|---|"]
for num, start, secs, say, tip in TALK:
    rows.append(f"| {start} | {num} | {secs} |")
rows += [f"| **Total** | | **{tot}** |", ""]
for i, (num, start, secs, say, tip) in enumerate(TALK, 1):
    rows += [f"## {i}. Slide {num} ({start}, {secs} detik)", "", f"**Ucapkan (Inggris):** {say}", "", f"**Catatan (Indonesia):** {tip}", ""]
rows += ["## Slide cadangan (hanya jika ditanya)", ""] + [f"- Slide {n}: {t}" for n, t in BACKUP.items()]
open(MD, "w").write("\n".join(rows) + "\n")
print("slides:", len(prs.slides), "seconds:", tot)
