"""Extend Team FEAF's 5-page A4 briefing into the 12-page proposal deck.

Friend's pages are kept as they are (only page numbers, section numbers and one
cross-reference change). New pages are drawn in the same visual language:
navy 10233F, teal 16B8A6, Inter body, Manrope headings, 0.55" margins.
"""

import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SRC, OUT = sys.argv[1], sys.argv[2]

C = dict(
    navy="10233F", navy2="1B355C", navy3="2C4A73", teal="16B8A6", tealD="0E8C7E",
    gray="68758A", bg="F7F9FC", tint="E3F6F3", line="D5DCE6", mute="C9D3E0",
    white="FFFFFF", amber="9A6400", amberT="FBF3E4", red="B42318", redT="FDECEA",
    grayT="EEF1F5",
)
L, W = 0.55, 7.17
TOTAL = 12
FOOT = "Team FEAF  ·  Agentic AI Investment Assistant  ·  Proposal Briefing"


def I(x):
    return Inches(x)


def _strip_style(shp):
    st = shp._element.find(qn("p:style"))
    if st is not None:
        shp._element.remove(st)


def _fmt_run(run, d):
    f = run.font
    f.size = Pt(d["size"])
    f.bold = bool(d.get("bold"))
    f.italic = bool(d.get("italic"))
    f.name = d.get("font", "Inter")
    f.color.rgb = RGBColor.from_string(d["color"])
    rPr = run._r.get_or_add_rPr()
    if d.get("spc") is not None:
        rPr.set("spc", str(d["spc"]))
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", d.get("font", "Inter"))


def fill_tf(tf, content, d):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    bp = tf._txBody.find(qn("a:bodyPr"))
    for k in ("lIns", "tIns", "rIns", "bIns"):
        bp.set(k, "0")
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE,
                          "b": MSO_ANCHOR.BOTTOM}[d["anchor"]]
    paras = content if isinstance(content, list) else content.split("\n")
    for i, p in enumerate(paras):
        P = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        pd = dict(d)
        if isinstance(p, dict):
            pd.update({k: v for k, v in p.items() if k != "runs"})
            runs = p["runs"]
        else:
            runs = p
        if isinstance(runs, (str, tuple)):
            runs = [runs]
        P.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[pd["align"]]
        if pd.get("ls"):
            P.line_spacing = pd["ls"]
        if pd.get("after"):
            P.space_after = Pt(pd["after"])
        if pd.get("bullet"):
            pPr = P._p.get_or_add_pPr()
            ind = int(I(pd.get("ind", 0.11)))
            pPr.set("marL", str(ind))
            pPr.set("indent", str(-ind))
            bc = etree.SubElement(pPr, qn("a:buClr"))
            etree.SubElement(bc, qn("a:srgbClr")).set("val", pd.get("bucolor", C["teal"]))
            etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
            etree.SubElement(pPr, qn("a:buChar")).set("char", pd.get("buchar", "•"))
        for r in runs:
            rd = dict(pd)
            if isinstance(r, tuple):
                t, o = r
                rd.update(o)
            else:
                t = r
            R = P.add_run()
            R.text = t
            _fmt_run(R, rd)


DEF = dict(size=8, color=C["navy"], bold=False, font="Inter", align="l", anchor="t")


def tb(s, x, y, w, h, content, **kw):
    d = dict(DEF)
    d.update(kw)
    t = s.shapes.add_textbox(I(x), I(y), I(w), I(h))
    fill_tf(t.text_frame, content, d)
    return t


def box(s, x, y, w, h, fill=None, line=None, lw=0.75, r=0.08, text=None, **kw):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE
    shp = s.shapes.add_shape(kind, I(x), I(y), I(w), I(h))
    _strip_style(shp)
    if r:
        shp.adjustments[0] = min(0.5, r / min(w, h))
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = RGBColor.from_string(line)
        shp.line.width = Pt(lw)
    else:
        shp.line.fill.background()
    if text is not None:
        d = dict(DEF)
        d.update(dict(align="c", anchor="m"))
        d.update(kw)
        fill_tf(shp.text_frame, text, d)
    return shp


def pill(s, x, y, w, h, text, fill, color, line=None, size=6.5, bold=True, spc=60):
    return box(s, x, y, w, h, fill=fill, line=line, r=h / 2, text=text, size=size,
               bold=bold, color=color, spc=spc)


def ln(s, x1, y1, x2, y2, color, w=1.0, arrow=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, I(x1), I(y1), I(x2), I(y2))
    _strip_style(c)
    c.line.color.rgb = RGBColor.from_string(color)
    c.line.width = Pt(w)
    if arrow:
        lnel = c.line._get_or_add_ln()
        te = etree.SubElement(lnel, qn("a:tailEnd"))
        te.set("type", "triangle")
        te.set("w", "med")
        te.set("len", "med")
    return c


def cap(s, x, y, w, text, color=C["gray"], size=7, spc=150, h=0.16, **kw):
    return tb(s, x, y, w, h, text, size=size, bold=True, color=color, spc=spc, **kw)


def h2(s, x, y, w, text, h=0.25):
    return tb(s, x, y, w, h, text, size=11.5, bold=True, font="Manrope")


def header(s, num, label, title, sub):
    tb(s, L, 0.55, W, 0.22, f"{num}  ·  {label}", size=8, bold=True, color=C["teal"], spc=200)
    tb(s, L, 0.80, W, 0.76, title, size=21, bold=True, font="Manrope")
    tb(s, L, 1.62, W, 0.40, sub, size=9.5, color=C["gray"])


def footer(s, page, dark=False):
    col = C["mute"] if dark else C["gray"]
    tb(s, L, 11.27, 5.0, 0.18, FOOT, size=7, color=col)
    tb(s, 6.72, 11.27, 1.0, 0.18, f"{page:02d} / {TOTAL:02d}", size=7, bold=True,
       color=col, align="r")


prs = Presentation(SRC)
LAYOUT = [l for l in prs.slide_layouts if l.name == "A4_PAGE"][0]
orig = list(prs.slides)


def new_slide():
    s = prs.slides.add_slide(LAYOUT)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


# ---------------------------------------------------------------- page 1 cover
cover = new_slide()
s = cover
box(s, 0, 0, 8.27, 11.69, fill=C["navy"], r=0)
tb(s, L, 0.95, W, 0.22, "PROPOSAL BRIEFING  ·  NAPAI AGENTIC AI INNOVATION COMPETITION 2026",
   size=8, bold=True, color=C["teal"], spc=200)
tb(s, L, 1.35, W, 1.3, "Agentic AI Investment Assistant", size=36, bold=True, font="Manrope",
   color=C["white"])
tb(s, L, 2.78, 6.7, 0.75,
   "From stock information to decision support that is explainable, verifiable and "
   "continuously tracked — with the investor always making the final call.",
   size=12, color=C["mute"])

box(s, L, 3.85, W, 2.85, fill=C["navy2"], r=0.1)
rows = [
    ("CATEGORY", [("B  ·  Designated Field Group", {"bold": True})]),
    ("CHALLENGE", [("SYSTEX  ·  ", {"bold": True}),
                   "Investment Intelligence & AI-Powered Stock Selection Agent"]),
    ("APPLICATION THEME", "Industry & Public-Sector Co-Creation"),
    ("TECHNOLOGY TAGS", "Agentic Workflow  ·  Domain-Specific Agent  ·  Human-in-the-loop"),
    ("FIELD VALIDATION", [("Level 1  ", {"bold": True, "color": C["teal"]}),
                          "needs documented with 10 self-directed investors (6–8 Oct 2026). "
                          "Level 2 evidence in progress: 711 real MOPS filings, labelled test cases."]),
]
y = 4.07
for i, (k, v) in enumerate(rows):
    cap(s, 0.8, y + 0.02, 1.75, k, color=C["teal"])
    tb(s, 2.6, y, 4.9, 0.42, [v], size=9.5, color=C["white"])
    if i < len(rows) - 1:
        ln(s, 0.8, y + 0.45, 7.47, y + 0.45, C["navy3"], w=0.75)
    y += 0.52

cap(s, L, 7.0, 3.0, "CONTENTS", color=C["teal"], spc=200, size=7.5)
contents = [
    ("02", "The investor problem"),
    ("03", "Customer journey & survey evidence"),
    ("04", "Why agentic AI"),
    ("05", "Task flow & agent states"),
    ("06", "Architecture, data flow & deployment"),
    ("07", "State, permissions & security"),
    ("08", "Prototype & operation flow"),
    ("09", "Test cases, baselines & metrics"),
    ("10", "Market feasibility & growth"),
    ("11", "Validation roadmap & adoption"),
    ("12", "Team & third-party resources"),
]
for i, (n, t) in enumerate(contents):
    col, row = (0, i) if i < 6 else (1, i - 6)
    x = L + col * 3.65
    yy = 7.32 + row * 0.31
    tb(s, x, yy, 0.4, 0.22, n, size=10, bold=True, font="Manrope", color=C["teal"])
    tb(s, x + 0.42, yy + 0.02, 3.1, 0.22, t, size=9.5, color=C["white"])

box(s, L, 9.6, W, 1.25, fill=C["navy2"], r=0.1)
tb(s, 0.8, 9.8, 6.7, 0.5,
   [[("AI researches, analyses, explains and monitors. ", {"color": C["white"]}),
     ("The investor makes the final decision.", {"color": C["teal"]})]],
   size=12, bold=True, font="Manrope")
tb(s, 0.8, 10.35, 6.7, 0.4,
   "Decision support, not a trading tool: no order execution, no buy/sell calls, and no number "
   "published unless it traces back to an official source.", size=8.5, color=C["mute"])
footer(s, 1, dark=True)

# ----------------------------------------------------- page 5 task flow & states
flow = new_slide()
s = flow
header(s, "05", "TASK FLOW & AGENT STATES", "One Filing, Six States, Three Ways to Stop",
       "Version 1 builds the riskiest loop first: watch official MOPS filings, recompute valuation "
       "when a filing changes an input, and refuse to publish anything it cannot trace.")

box(s, L, 2.25, W, 5.35, fill=C["navy"], r=0.08)
cap(s, 0.8, 2.43, 3.5, "THE AGENT LOOP  ·  ONE FILING", color=C["teal"], spc=200, size=7.5)
tb(s, 4.2, 2.43, 3.27, 0.16, "Built and tested — runs end to end today", size=6.5,
   italic=True, color=C["mute"], align="r")

states = [
    ("0", "Clause screen", "DET",
     "Reads the regulator's own event-type clause (符合條款). Routine filings stop here and never "
     "reach the model.",
     ("SKIPPED", "clause cannot change a valuation input", C["grayT"], C["navy"])),
    ("1", "Triage", "MODEL",
     "Which valuation input does this filing touch — capex, cash or debt? Returns a confidence score.",
     ("HELD", "confidence below 0.55 → human review queue", C["amberT"], C["amber"])),
    ("2", "Extract", "MODEL",
     "Pulls the number, its unit and currency, and the exact sentence it came from.",
     ("HELD", "no number found together with its source sentence", C["amberT"], C["amber"])),
    ("3", "Recompute", "DET",
     "Runs the DCF calculator twice, before and after the new number, so the change is "
     "arithmetic, not opinion.",
     None),
    ("4", "Verify", "DET",
     "Eight checks against the filing: field label, verbatim quote, digits, currency, unit, "
     "conversion, magnitude band, circularity.",
     ("REJECTED", "any check fails · reason logged, nothing published", C["redT"], C["red"])),
    ("5", "Cited alert", "OUT",
     "Source link, exact sentence, valuation before and after, and the verifier's verdict.",
     ("INVESTOR DECIDES", "the agent has no trade-execution capability", C["teal"], C["white"])),
]
cx, cw, rh, gap, y0 = 0.8, 4.45, 0.68, 0.11, 2.75
for i, (n, name, kind, desc, exit_) in enumerate(states):
    y = y0 + i * (rh + gap)
    box(s, cx, y, cw, rh, fill=C["navy2"], r=0.06)
    tb(s, cx + 0.12, y + 0.08, 0.25, 0.2, n, size=9, bold=True, color=C["teal"])
    tb(s, cx + 0.38, y + 0.07, 2.4, 0.2, name, size=9.5, bold=True, font="Manrope",
       color=C["white"])
    if kind == "MODEL":
        pill(s, cx + cw - 1.07, y + 0.08, 0.95, 0.18, "MODEL", C["teal"], C["navy"], size=6)
    elif kind == "DET":
        pill(s, cx + cw - 1.07, y + 0.08, 0.95, 0.18, "DETERMINISTIC", None, C["teal"],
             line=C["teal"], size=6)
    else:
        pill(s, cx + cw - 1.07, y + 0.08, 0.95, 0.18, "OUTPUT", C["white"], C["navy"], size=6)
    tb(s, cx + 0.38, y + 0.3, cw - 0.5, 0.36, desc, size=7.2, color=C["mute"])
    if i < len(states) - 1:
        ln(s, cx + 0.2, y + rh, cx + 0.2, y + rh + gap, C["teal"], w=1.25, arrow=True)
    ex = cx + cw + 0.32
    if exit_:
        label, why, fill, col = exit_
        ln(s, cx + cw, y + 0.17, ex, y + 0.17, C["navy3"] if fill != C["teal"] else C["teal"],
           w=1.0, arrow=True)
        pill(s, ex, y + 0.07, 1.62, 0.2, label, fill, col, size=6.5)
        tb(s, ex + 0.05, y + 0.32, 1.6, 0.34, why, size=6.6, color=C["mute"])
    else:
        tb(s, ex + 0.05, y + 0.1, 1.6, 0.4, "No exit here: arithmetic cannot guess.", size=6.6,
           italic=True, color=C["mute"])

# dynamic adjustment strip
box(s, L, 7.78, W, 0.62, fill=C["bg"], line=C["line"], r=0.06)
cap(s, 0.72, 7.9, 1.6, "DYNAMIC ADJUSTMENT", color=C["tealD"])
tb(s, 0.72, 8.1, 1.7, 0.26, "States 1–2 only", size=7, color=C["gray"])
chips = [("Model API fails", C["white"]), ("Retry × 2", C["white"]),
         ("Rule-based fallback, labelled on screen", C["tint"])]
xs = [2.45, 3.62, 4.79]
ws = [1.0, 1.0, 2.75]
for (t, f), x, w in zip(chips, xs, ws):
    pill(s, x, 7.9, w, 0.26, t, f, C["navy"], line=C["line"], size=7, spc=0)
for x, w in zip(xs[:-1], ws[:-1]):
    ln(s, x + w, 8.03, x + w + 0.17, 8.03, C["teal"], w=1.0, arrow=True)
tb(s, 2.45, 8.2, 5.1, 0.16, "Tasks never stop silently and never pretend to succeed.", size=6.6,
   italic=True, color=C["gray"])

# mapping to the page-4 workflow
tb(s, L, 8.62, 2.2, 0.18, "Maps to the workflow on page 4:", size=8, bold=True)
wf = [("Plan", "state 0"), ("Retrieve", "states 1–2"), ("Analyse", "state 3"),
      ("Verify", "state 4"), ("Explain", "state 5"), ("Monitor", "next filing")]
x = 2.55
for i, (t, sub) in enumerate(wf):
    on = t == "Verify"
    pill(s, x, 8.58, 0.78, 0.26, t, C["teal"] if on else C["tint"],
         C["white"] if on else C["navy"], size=7.5, spc=0)
    tb(s, x, 8.88, 0.78, 0.16, sub, size=6.3, color=C["gray"], align="c")
    if i < len(wf) - 1:
        ln(s, x + 0.78, 8.71, x + 0.86, 8.71, C["teal"], w=1.0)
    x += 0.86

# eligibility cards
h2(s, L, 9.25, W, "Competition eligibility (Art. 4): all four criteria met")
tb(s, L, 9.52, W, 0.18, "Required: ① plus any two of ②–④. Agentic only where it helps — "
   "the model reasons in two states; the other four are deterministic.", size=7.5, color=C["gray"])
elig = [
    ("① Goal decomposition", "required",
     "Six dependent states; each advances only on the previous state's result."),
    ("② Tool & system calls", "",
     "MOPS, TWSE/TPEx OpenAPI, the DCF calculator and the model API."),
    ("③ State & adjustment", "",
     "Confidence threshold, three exits, retry and labelled fallback."),
    ("④ Access & risk control", "",
     "Deterministic verification, full audit trace, no execution."),
]
cw4, gx = 1.7, 0.123
for i, (t, tag, d) in enumerate(elig):
    x = L + i * (cw4 + gx)
    last = i == 3
    box(s, x, 9.8, cw4, 1.25, fill=C["teal"] if last else C["bg"], r=0.06)
    tb(s, x + 0.12, 9.9, cw4 - 0.24, 0.2, t, size=8.2, bold=True,
       color=C["white"] if last else C["navy"])
    if tag:
        tb(s, x + 0.12, 10.1, cw4 - 0.24, 0.16, "REQUIRED", size=6, bold=True, spc=100,
           color=C["tealD"])
    tb(s, x + 0.12, 10.3, cw4 - 0.24, 0.7, d, size=7.4,
       color=C["white"] if last else C["navy"])
footer(s, 5)

# --------------------------------------------------- page 6 architecture
arch = new_slide()
s = arch
header(s, "06", "SYSTEM ARCHITECTURE, DATA FLOW & DEPLOYMENT",
       "The Model Touches Two Boxes Out of Eleven",
       "Numbers come from official filings and arithmetic. The language model only reads and points; "
       "every other step is deterministic, logged and testable.")

bands = [
    ("1", "SOURCES", 2.25, 0.86, [
        ("MOPS 公開資訊觀測站", "Material-information filings (重大訊息); form-POST, ROC calendar", "D"),
        ("TWSE / TPEx OpenAPI", "Closing price, shares outstanding", "D"),
    ]),
    ("2", "INGEST & CLEAN", 3.33, 0.86, [
        ("Probe", "Reachability per source; checks response shape", "D"),
        ("Fetch", "Polite 2–2.5 s delay between requests", "D"),
        ("Parse", "ROC → Gregorian dates; permanent citation URL", "D"),
        ("Detail fetch", "Drops spokesperson name, title, phone before storage", "D"),
    ]),
    ("3", "AGENT", 4.41, 0.86, [
        ("Screen", "Clause → input map", "D"),
        ("Triage", "Which input? confidence", "M"),
        ("Extract", "Number + exact sentence", "M"),
        ("Recompute", "dcf.compute() × 2", "D"),
        ("Verify", "8 checks vs filing", "D"),
    ]),
    ("4", "PRESENT", 5.49, 0.86, [
        ("Alert feed", "Every outcome, labelled", "W"),
        ("Alert detail", "Source, sentence, verdict", "W"),
        ("Valuation", "Assumptions, sensitivity", "W"),
        ("Audit trace", "Per-state log, cost", "W"),
        ("JSON API", "+ OpenAPI docs", "W"),
    ]),
]
lx, lw_, bx = L, 1.12, L + 1.25
bw = W - 1.25
for n, name, y, h, comps in bands:
    box(s, lx, y, lw_, h, fill=C["navy"], r=0.06)
    tb(s, lx + 0.12, y + 0.12, 0.4, 0.22, n, size=11, bold=True, font="Manrope", color=C["teal"])
    tb(s, lx + 0.12, y + 0.4, lw_ - 0.2, 0.36, name, size=7, bold=True, spc=120, color=C["white"])
    if name == "SOURCES":
        widths = [1.95, 1.65]
        note_x = bx + sum(widths) + 2 * 0.1
    else:
        widths = [(bw - 0.1 * (len(comps) - 1)) / len(comps)] * len(comps)
    x = bx
    for (t, d, k), w in zip(comps, widths):
        model = k == "M"
        box(s, x, y, w, h, fill=C["teal"] if model else C["bg"],
            line=None if model else C["line"], r=0.06)
        tb(s, x + 0.08, y + 0.1, w - 0.16, 0.2, t, size=8, bold=True,
           color=C["white"] if model else C["navy"])
        tb(s, x + 0.08, y + 0.33, w - 0.16, 0.5, d, size=6.8,
           color=C["white"] if model else C["gray"])
        x += w + 0.1
    if name == "SOURCES":
        nw = L + W - note_x
        box(s, note_x, y, nw, h, fill=C["amberT"], r=0.06)
        tb(s, note_x + 0.08, y + 0.08, nw - 0.16, 0.74,
           [[("Geo-blocked outside Taiwan. ", {"bold": True}),
             "The block page returns HTTP 200, so we validate response shape, not status code."]],
           size=6.8, color=C["amber"])
    if name != "PRESENT":
        ln(s, lx + lw_ / 2, y + h, lx + lw_ / 2, y + h + 0.22, C["teal"], w=1.25, arrow=True)
tb(s, bx, 6.39, bw, 0.16,
   "pipeline.py orchestrates the agent states and writes one trace record per step.  "
   "Teal = language model (2 of 11 processing boxes).", size=6.6, italic=True, color=C["gray"])

cards = [
    ("Model layer", [
        "Gemini 2.5 Flash, temperature 0, JSON-only output",
        "Prompt version pinned (2026-09-24.1)",
        "Provider swappable by one environment variable",
        "Rule-based reasoner = fallback and evaluation baseline",
    ]),
    ("Valuation engine", [
        "Two-stage unlevered DCF with WACC",
        "Reverse DCF: the growth the market implies",
        "Perpetual-growth sanity cap; WACC × g sensitivity",
        "Every input carries its source URL; web and CLI share one compute()",
    ]),
    ("Storage & access", [
        "Plain JSON files, no database",
        "No login, so no stored passwords",
        "One trace file per run, readable on screen",
        "API key read only from the environment",
    ]),
]
cw3 = (W - 0.24) / 3
for i, (t, items) in enumerate(cards):
    x = L + i * (cw3 + 0.12)
    box(s, x, 6.72, cw3, 1.72, fill=C["bg"], r=0.06)
    tb(s, x + 0.14, 6.84, cw3 - 0.28, 0.22, t, size=9.5, bold=True, font="Manrope")
    tb(s, x + 0.14, 7.1, cw3 - 0.26, 1.3, [{"runs": it, "bullet": True, "after": 2} for it in items],
       size=7.2)

box(s, L, 8.66, W, 1.62, fill=C["navy"], r=0.08)
cap(s, 0.8, 8.82, 4, "DEPLOYMENT  ·  WHERE EACH PART RUNS", color=C["teal"], spc=200, size=7.5)
dep = [
    ("Ingestion — inside Taiwan",
     "MOPS and TWSE serve only Taiwan, non-datacenter networks. Today: a laptop on a Taiwan campus "
     "network. Partner path: a licensed data feed from the field partner."),
    ("Agent + web — anywhere",
     "Python plus three libraries (FastAPI, Uvicorn, Jinja2). Reads the cleaned JSON; runs on a "
     "laptop. Maintenance: clause map, one input file per issuer, prompt version, regression tests."),
    ("Cost — measured, not estimated",
     "The model is called only for filings that pass the clause screen. Cost per trace is logged in "
     "USD; the free tier covers today's volume."),
]
dw = (W - 0.5 - 0.3) / 3
for i, (t, d) in enumerate(dep):
    x = 0.8 + i * (dw + 0.15)
    tb(s, x, 9.12, dw, 0.22, t, size=8.6, bold=True, font="Manrope", color=C["white"])
    tb(s, x, 9.38, dw, 1.2, d, size=7.2, color=C["mute"])
tb(s, L, 10.42, W, 0.3,
   "Field data check, 14 Sep 2026, from a Taiwan network: 711 MOPS filings from 5 issuers "
   "(2330, 2317, 2881, 1301, 2412), 100% with a permanent source URL.",
   size=7, color=C["gray"])
footer(s, 6)

# --------------------------------------------- page 7 state, permissions, security
sec = new_slide()
s = sec
header(s, "07", "STATE MANAGEMENT, PERMISSIONS & SECURITY", "Built to Stop, Not Just to Answer",
       "Finance is high-risk, so autonomy is bounded on purpose: the agent may read, compute, "
       "explain and cite. It has no way to act on an account.")

perm = [
    ("AGENT MAY", C["tint"], C["tealD"], C["navy"], [
        "Read public filings and market data",
        "Compute and recompute valuation",
        "Explain and cite every number",
        "Queue uncertain cases for a human",
    ]),
    ("AGENT MAY NOT", C["bg"], C["red"], C["navy"], [
        "Place, change or cancel trades",
        "Connect to a brokerage or bank account",
        "Act or pay on the user's behalf (Art. 14.2)",
        "Publish a number it cannot trace",
    ]),
    ("THE INVESTOR", C["navy"], C["teal"], C["white"], [
        "Makes every investment decision",
        "Reviews the HELD queue",
        "Rates alerts; ratings tune thresholds within fixed bounds (planned for final)",
    ]),
]
pw = (W - 0.24) / 3
for i, (t, f, tc, bc, items) in enumerate(perm):
    x = L + i * (pw + 0.12)
    box(s, x, 2.25, pw, 1.5, fill=f, r=0.06)
    cap(s, x + 0.14, 2.37, pw - 0.28, t, color=tc)
    tb(s, x + 0.14, 2.6, pw - 0.26, 1.1,
       [{"runs": it, "bullet": True, "after": 2, "bucolor": tc} for it in items], size=7.4, color=bc)

box(s, L, 3.87, W, 0.36, fill=C["tint"], r=0.06)
tb(s, 0.7, 3.95, W - 0.3, 0.22,
   [[("Why these limits — survey (n = 10):  ", {"bold": True}),
     "8/10 want any trade to need their approval  ·  8/10 name accuracy or hallucination as their "
     "top concern  ·  9/10 want the full reasoning trail"]],
   size=7.2, color=C["tealD"])

h2(s, L, 4.4, W, "State management")
sm = [
    ("Explicit state per filing",
     "Four endings: skipped, held, rejected, published. Three of the four are not \"publish\"."),
    ("A trace record for every state",
     "Input, output, latency, tokens, cost, retries, fallback flag and number of model calls."),
    ("Fail-closed defaults",
     "Foreign currency and unknown units are rejected, not converted; a missing clause is passed "
     "on but flagged for a human."),
    ("Feedback state (planned for final)",
     "👍/👎 per alert tunes the triage threshold within fixed bounds; every change logged and "
     "reversible."),
]
sw = (W - 0.12) / 2
for i, (t, d) in enumerate(sm):
    x = L + (i % 2) * (sw + 0.12)
    y = 4.72 + (i // 2) * 0.74
    box(s, x, y, sw, 0.64, fill=C["bg"], r=0.06)
    tb(s, x + 0.14, y + 0.08, sw - 0.28, 0.18, t, size=8, bold=True)
    tb(s, x + 0.14, y + 0.27, sw - 0.28, 0.36, d, size=7.2, color=C["gray"])

h2(s, L, 6.27, W, "Threats and responses (Art. 14.3)")
cols = [(L + 0.12, 1.75, "RISK"), (L + 1.95, 3.55, "DESIGN RESPONSE"),
        (L + 5.6, 1.5, "AUTOMATED TEST")]
for x, w, t in cols:
    cap(s, x, 6.58, w, t, color=C["tealD"] if t == "AUTOMATED TEST" else C["gray"])
threats = [
    ("Prompt injection inside a filing",
     "Filing text is delimited as untrusted data; injection markers are logged; the deterministic "
     "verifier blocks injected numbers", "Injected number never published"),
    ("Hallucinated number or quote",
     "The quote must exist verbatim and the digits must exist in the filing",
     "Fabricated quote and absent number rejected"),
    ("Unit or currency error",
     "Unit whitelist; foreign currency rejected; new value must sit within 0.2–3.0× of the current one",
     "USD amount rejected"),
    ("Arithmetic bug", "Circularity check; web and CLI share one compute()",
     "CLI and compute() agree"),
    ("Personal data (PDPA)",
     "Spokesperson name, title and phone dropped at ingestion; only the field names are logged",
     "PII values never stored"),
    ("Credential leak", "API key read only from the environment; never on screen, in logs or traces",
     "No key in any trace"),
    ("Third-party failure",
     "Retry × 2, then labelled rule-based fallback; block pages detected by response shape",
     "Every trace carries retry and fallback fields"),
]
y = 6.8
rh2 = 0.42
for i, (r, d, t) in enumerate(threats):
    box(s, L, y, W, rh2 - 0.05, fill=C["bg"] if i % 2 == 0 else C["white"],
        line=None if i % 2 == 0 else C["line"], r=0.05)
    tb(s, L + 0.12, y + 0.06, 1.75, 0.3, r, size=7.4, bold=True, anchor="t")
    tb(s, L + 1.95, y + 0.06, 3.55, 0.3, d, size=7.1)
    tb(s, L + 5.6, y + 0.06, 1.5, 0.3, [[("✓ ", {"bold": True}), t]], size=7.1, color=C["tealD"])
    y += rh2

box(s, L, 9.88, W, 0.92, fill=C["navy"], r=0.08)
tb(s, 0.8, 10.0, 3.25, 0.8,
   [{"runs": [("Incident response (Art. 14.4)", {"bold": True, "color": C["white"], "font": "Manrope",
                                         "size": 8.6})], "after": 3},
    "On any leak or unauthorised access: stop the affected function, report to the organiser "
    "and the field contact, and never widen it by self-testing."],
   size=7.2, color=C["mute"])
tb(s, 4.3, 10.0, 3.2, 0.8,
   [{"runs": [("Free-tier model disclosure", {"bold": True, "color": C["white"], "font": "Manrope",
                                      "size": 8.6})], "after": 3},
    "Only public filings with personal data already removed are sent. Free-tier content may be "
    "used by the provider; non-public data would require a no-training tier."],
   size=7.2, color=C["mute"])
footer(s, 7)

# --------------------------------------------------- page 8 prototype
proto = new_slide()
s = proto
header(s, "08", "PROTOTYPE & OPERATION FLOW", "A Working Prototype, Stated Plainly",
       "Below is the prototype's real output for a test filing, redrawn in English (the V1 "
       "interface is in Indonesian). Four screens, one flow.")

steps = [("1", "Alert feed", "Every filing's ending, labelled by engine and data source"),
         ("2", "Alert detail", "Source link, exact sentence, verifier verdict"),
         ("3", "Valuation", "Visible, editable assumptions; WACC × g sensitivity"),
         ("4", "Audit trace", "Each state with latency, cost and retries")]
sw4 = (W - 0.45) / 4
for i, (n, t, d) in enumerate(steps):
    x = L + i * (sw4 + 0.15)
    box(s, x, 2.22, sw4, 0.66, fill=C["bg"], r=0.06)
    tb(s, x + 0.1, 2.3, sw4 - 0.2, 0.2,
       [[(n + "  ", {"color": C["teal"]}), t]], size=8.5, bold=True, font="Manrope")
    tb(s, x + 0.1, 2.52, sw4 - 0.2, 0.34, d, size=6.8, color=C["gray"])
    if i < 3:
        ln(s, x + sw4, 2.55, x + sw4 + 0.15, 2.55, C["teal"], w=1.0, arrow=True)

# alert card
ax, ay, aw, ah = L, 3.08, 4.55, 4.62
box(s, ax, ay, aw, ah, fill=C["white"], line=C["line"], r=0.08)
pill(s, ax + 0.18, ay + 0.16, 1.1, 0.2, "PUBLISHED", C["tint"], C["tealD"], size=6.5)
pill(s, ax + 1.36, ay + 0.16, 1.55, 0.2, "TEST FILING · FIXTURE 1", C["grayT"], C["gray"], size=6)
tb(s, ax + 3.0, ay + 0.18, 1.4, 0.18, "2026-09-18 · 17:32", size=6.8, color=C["gray"], align="r")
tb(s, ax + 0.18, ay + 0.46, aw - 0.36, 0.24,
   [[("2330  TSMC 台積電", {"bold": True})]], size=10, font="Manrope")
tb(s, ax + 0.18, ay + 0.72, aw - 0.36, 0.2,
   [["公告本公司董事會通過資本支出預算案  ", ("— board approves capex budget", {"color": C["gray"]})]],
   size=7.6)
pill(s, ax + 0.18, ay + 0.98, 1.95, 0.19, "CLAUSE 11  ·  BOARD CAPEX DECISION", C["navy"], C["white"],
     size=5.8)
box(s, ax + 0.18, ay + 1.27, aw - 0.36, 0.3, fill=C["bg"], r=0.05)
tb(s, ax + 0.28, ay + 1.33, aw - 1.6, 0.2,
   "mops.twse.com.tw/mops/web/t05st01?co_id=2330&seq_no=1…", size=6.5, color=C["navy"])
pill(s, ax + aw - 1.2, ay + 1.33, 0.95, 0.18, "OFFICIAL SOURCE", C["tint"], C["tealD"], size=5.6, spc=20)

cap(s, ax + 0.18, ay + 1.72, 2, "EXTRACTED", color=C["tealD"])
box(s, ax + 0.18, ay + 1.92, aw - 0.36, 0.72, fill=C["tint"], r=0.05)
tb(s, ax + 0.3, ay + 1.99, aw - 0.6, 0.78,
   [[("Input  ", {"color": C["gray"]}), ("capex (capital expenditure)", {"bold": True})],
    [("Value  ", {"color": C["gray"]}), ("1,480,000,000 仟元", {"bold": True}),
     "  →  NT$1,480,000 million"],
    [("Quote  ", {"color": C["gray"]}), "item 3 · 資本支出預算金額: 新台幣 1,480,000,000 仟元"]],
   size=7.4, after=2)

cap(s, ax + 0.18, ay + 2.93, 2.5, "VERIFIER  ·  8 / 8 PASSED", color=C["tealD"])
checks = ["Field label valid for input", "Quote found verbatim", "Digits found in filing",
          "Currency supported (NTD)", "Unit recognised (仟元)", "Conversion available",
          "Magnitude 1.16× (band 0.2–3.0×)", "Circularity intact"]
for i, c in enumerate(checks):
    x = ax + 0.18 + (i % 2) * 2.1
    y = ay + 3.15 + (i // 2) * 0.22
    tb(s, x, y, 2.05, 0.2, [[("✓  ", {"bold": True, "color": C["teal"]}), c]], size=7)
box(s, ax + 0.18, ay + 4.08, aw - 0.36, 0.38, fill=C["bg"], r=0.05)
tb(s, ax + 0.28, ay + 4.13, aw - 0.56, 0.3,
   [[("Engine: ", {"bold": True}), "rule-based reasoner   ", ("Data: ", {"bold": True}),
     "test fixture   ", ("Model calls: ", {"bold": True}), "0   ", ("Cost: ", {"bold": True}),
     "US$0"]], size=6.8, color=C["gray"], anchor="m")

callouts = [
    ("①", "A source a judge can open",
     "Every alert links to the filing's permanent MOPS address."),
    ("②", "Number + exact sentence",
     "The value, its unit and the item it came from, quoted verbatim in the original Chinese."),
    ("③", "Eight checks, all deterministic",
     "Any failure blocks the alert and records why. The model never grades itself."),
    ("④", "Honest labels",
     "Every screen says which engine produced it and whether the data is real or a test case."),
]
cx2 = ax + aw + 0.2
cwid = L + W - cx2
for i, (n, t, d) in enumerate(callouts):
    y = ay + i * 1.17
    tb(s, cx2, y + 0.02, 0.3, 0.3, n, size=13, bold=True, font="Manrope", color=C["teal"])
    tb(s, cx2 + 0.32, y + 0.05, cwid - 0.32, 0.2, t, size=8.4, bold=True, font="Manrope")
    tb(s, cx2 + 0.32, y + 0.3, cwid - 0.32, 0.8, d, size=7.3, color=C["gray"])

h2(s, L, 7.9, 3.6, "Four test filings, four endings")
cases = [("TSMC capex budget", "Published", "Normal path works end to end", C["tint"], C["tealD"]),
         ("Capex + instruction injected into the filing", "Published",
          "Correct number published; injected number never used", C["tint"], C["tealD"]),
         ("MediaTek investor-conference notice", "Skipped",
          "Screened out before reaching the model", C["grayT"], C["navy"]),
         ("Asset purchase in USD", "Rejected", "Fail-closed on foreign currency", C["redT"],
          C["red"])]
y = 8.22
for t, o, p, f, col in cases:
    box(s, L, y, 3.6, 0.6, fill=C["bg"], r=0.05)
    tb(s, L + 0.1, y + 0.07, 2.2, 0.22, t, size=7.3, bold=True)
    tb(s, L + 0.1, y + 0.3, 3.4, 0.26, p, size=6.8, color=C["gray"])
    pill(s, L + 2.35, y + 0.08, 1.15, 0.19, o.upper(), f, col,
         size=5.6)
    y += 0.66

rx = L + 3.75
rw = W - 3.75
h2(s, rx, 7.9, rw, "What runs today")
status = [
    ("Web app + five-state pipeline", "Runs end to end"),
    ("Automated tests", "14 / 14 passing (15 Oct 2026)"),
    ("Real filings", "711 pulled and parsed; full replay is in the evaluation plan"),
    ("Model path", "Built with retry and fallback; outputs shown here are rule-based"),
    ("Valuation coverage", "1 issuer (TSMC). Inputs still being sourced, so no valuation figure "
                           "is presented as a finding"),
]
y = 8.22
for t, d in status:
    tb(s, rx, y, 1.15, 0.45, t, size=7.2, bold=True)
    tb(s, rx + 1.2, y, rw - 1.2, 0.45, d, size=7.2, color=C["gray"])
    ln(s, rx, y + 0.47, rx + rw, y + 0.47, C["line"], w=0.5)
    y += 0.52
footer(s, 8)

# --------------------------------------------------- page 9 evaluation
ev = new_slide()
s = ev
header(s, "09", "TEST CASES, BASELINES & EVALUATION METRICS",
       "Traceability First, Then Speed and Cost",
       "An alert counts as correct only if every number traces to an exact sentence in the filing, "
       "maps to the right valuation input and matches the calculator.")

stats = [("14/14", "automated tests passing, incl. injection, PII and key-leak tests"),
         ("0", "injected numbers published in the prompt-injection test"),
         ("4/4", "test filings reached their expected ending"),
         ("711", "real filings ready for replay, 100% with a source URL")]
tw = (W - 0.36) / 4
for i, (n, d) in enumerate(stats):
    x = L + i * (tw + 0.12)
    box(s, x, 2.22, tw, 1.12, fill=C["bg"], r=0.06)
    tb(s, x + 0.14, 2.3, tw - 0.28, 0.5, n, size=26, bold=True, font="Manrope",
       color=C["tealD"] if i != 1 else C["navy"])
    tb(s, x + 0.14, 2.82, tw - 0.28, 0.5, d, size=7, color=C["gray"])

box(s, L, 3.46, W, 0.34, fill=C["navy"], r=0.06)
tb(s, 0.72, 3.53, W - 0.34, 0.22,
   [[("Safety target:  ", {"bold": True, "color": C["teal"]}),
     ("zero unsupported numbers published. ", {"bold": True, "color": C["white"]}),
     ("Speed and cost matter only once that holds.", {"color": C["mute"]})]], size=8)

h2(s, L, 3.98, W, "Test sets")
tcols = [(L + 0.12, 1.55, "SET"), (L + 1.72, 0.6, "SIZE"), (L + 2.37, 3.45, "WHAT IT TESTS"),
         (L + 5.92, 1.15, "STATUS")]
for x, w, t in tcols:
    cap(s, x, 4.28, w, t)
tests = [
    ("Unit & adversarial tests", "14",
     "Injection, hallucination, units, currency, PII, key leakage, arithmetic", "Passing", True),
    ("Test filings", "4",
     "Normal, injected instruction, routine notice (skip), foreign currency (reject)", "Passing", True),
    ("Fault-injection set", "planned",
     "Corrupted filings: wrong digits, fabricated quote, unit swap, injected instruction. "
     "Target: 100% caught", "Before final", False),
    ("Gold set", "30–50",
     "Filing → expected ending, input, value and source sentence, labelled by the finance members",
     "Before final", False),
    ("Real-stream replay", "711",
     "Screening rate, held and rejected shares, latency and cost at real scale", "Before final", False),
]
y = 4.48
for i, (a, b, c_, d, ok) in enumerate(tests):
    box(s, L, y, W, 0.4, fill=C["bg"] if i % 2 == 0 else C["white"],
        line=None if i % 2 == 0 else C["line"], r=0.05)
    tb(s, L + 0.12, y + 0.07, 1.55, 0.3, a, size=7.4, bold=True)
    tb(s, L + 1.72, y + 0.07, 0.6, 0.3, b, size=7.4)
    tb(s, L + 2.37, y + 0.07, 3.45, 0.32, c_, size=7)
    pill(s, L + 5.92, y + 0.1, 1.05, 0.19, d.upper(), C["tint"] if ok else C["grayT"],
         C["tealD"] if ok else C["gray"], size=5.8)
    y += 0.44

h2(s, L, 6.78, W, "Three baselines")
base = [("① Manual process",
         "How long investors take today to find and check a filing. Measured with users in "
         "prototype testing (page 11)."),
        ("② Rule-based workflow",
         "The same pipeline with no model. Already built: it is our fallback, so the comparison "
         "runs on identical cases."),
        ("③ Single LLM call, no verifier",
         "What a plain chatbot would publish. Shows exactly what the verifier prevents.")]
for i, (t, d) in enumerate(base):
    x = L + i * (cw3 + 0.12)
    box(s, x, 7.08, cw3, 0.98, fill=C["bg"], r=0.06)
    tb(s, x + 0.14, 7.17, cw3 - 0.28, 0.2, t, size=8.4, bold=True, font="Manrope")
    tb(s, x + 0.14, 7.42, cw3 - 0.28, 0.62, d, size=7.1, color=C["gray"])

h2(s, L, 8.24, W, "Metrics (Appendix 2), most recorded automatically in every trace")
mets = [
    ("Quality", "Task success rate · extraction accuracy (value, unit, input) · precision of published "
                "alerts · recall of valuation-relevant filings · verifier catch rate"),
    ("Efficiency", "Latency per filing (mean, max) · model/API cost per filing and per day · "
                   "share of filings that reach the model"),
    ("Robustness", "Tool-call success rate · retries · fallback rate · termination rate "
                   "(skipped / held / rejected)"),
    ("Human load", "Human-intervention rate (held share) · minutes saved vs the manual baseline"),
    ("Safety", "Prompt-injection, PII, credential, permission and inappropriate-output results · "
               "error categories · worst case and recovery"),
]
y = 8.54
for i, (g, m) in enumerate(mets):
    tb(s, L + 0.12, y + 0.04, 1.0, 0.2, g, size=7.6, bold=True, color=C["tealD"])
    tb(s, L + 1.15, y + 0.04, W - 1.25, 0.32, m, size=7.1)
    ln(s, L, y + 0.37, L + W, y + 0.37, C["line"], w=0.5)
    y += 0.39
tb(s, L, 10.55, W, 0.55,
   "Method: evaluation items are shuffled (Fisher–Yates) to avoid order bias; temperature 0 and a "
   "pinned prompt version keep runs repeatable. User-level pilot metrics (task time, claim "
   "accuracy, risk comprehension, alert usefulness, repeat use) are on page 11.",
   size=7, italic=True, color=C["gray"])
footer(s, 9)

# --------------------------------------------------- page 12 team & 3rd party
team = new_slide()
s = team
header(s, "12", "TEAM, THIRD-PARTY RESOURCES & RISK DISCLOSURE", "Who Built What, and What We Rely On",
       "Three students: one technical, two finance. Every external resource is listed with its "
       "purpose and scope (Art. 13).")

tm = [("TECHNICAL  ·  1 MEMBER", "Agent & data",
       "MOPS ingestion and cleaning, agent pipeline, verifier, valuation engine, web prototype, "
       "tests and demo."),
      ("FINANCE & FIELD  ·  2 MEMBERS", "Evidence & business",
       "Survey design and analysis, customer journey, market sizing and business model, valuation "
       "inputs, clause verification, gold set."),
      ("ADVISOR & FIELD LIAISON", "Named in the registration form",
       "May guide and explain needs only; no core design, programming, evaluation or presentation "
       "(Art. 7).")]
for i, (k, t, d) in enumerate(tm):
    x = L + i * (cw3 + 0.12)
    dark = i == 2
    box(s, x, 2.22, cw3, 1.38, fill=C["navy"] if dark else C["bg"], r=0.06)
    cap(s, x + 0.14, 2.33, cw3 - 0.28, k, color=C["teal"] if dark else C["tealD"], size=6.6)
    tb(s, x + 0.14, 2.53, cw3 - 0.28, 0.22, t, size=9.5, bold=True, font="Manrope",
       color=C["white"] if dark else C["navy"])
    tb(s, x + 0.14, 2.8, cw3 - 0.28, 0.78, d, size=7.2, color=C["mute"] if dark else C["gray"])

h2(s, L, 3.78, W, "Third-party resources")
rcols = [(L + 0.12, 1.9, "RESOURCE"), (L + 2.1, 1.45, "PROVIDER / LICENCE"),
         (L + 3.65, 3.4, "PURPOSE & SCOPE")]
for x, w, t in rcols:
    cap(s, x, 4.08, w, t)
res = [
    ("MOPS 公開資訊觀測站", "TWSE public disclosure",
     "Primary data and citation target; polite rate limit; raw pages kept locally, not redistributed"),
    ("TWSE / TPEx OpenAPI", "Public open data", "Prices and shares outstanding; read-only"),
    ("Gemini 2.5 Flash API (free tier)", "Google · Gemini API terms",
     "Triage and extraction only (states 1–2); public filings with personal data removed"),
    ("FastAPI · Uvicorn · Jinja2", "MIT · BSD-3 · BSD-3", "Web framework, server, templates"),
    ("Playwright · pptxgenjs", "Apache-2.0 · MIT", "Rendering design mock-ups and slides; "
                                                   "development only"),
    ("FinMind", "Open-source aggregator", "Reachability probe only; not used in the pipeline, "
                                          "never cited to users"),
    ("Google Forms", "Google", "Survey collection under a PDPA consent notice; results de-identified"),
    ("Generative AI assistants (e.g. Claude)", "Commercial services",
     "Drafting code, tests, documentation and slide text under the team's direction; decisions, "
     "field validation and analysis are the team's own"),
    ("Market & industry sources [2]–[9]", "As cited on page 11", "Market sizing and benchmarks only"),
]
y = 4.28
for i, (a, b, c_) in enumerate(res):
    box(s, L, y, W, 0.37, fill=C["bg"] if i % 2 == 0 else C["white"],
        line=None if i % 2 == 0 else C["line"], r=0.05)
    tb(s, L + 0.12, y + 0.06, 1.92, 0.3, a, size=7.2, bold=True)
    tb(s, L + 2.1, y + 0.06, 1.5, 0.3, b, size=7)
    tb(s, L + 3.65, y + 0.06, 3.45, 0.3, c_, size=7, color=C["gray"])
    y += 0.4

h2(s, L, 7.98, W, "Known limitations & risk disclosure")
lims = [
    "The clause → input map is provisional until checked line by line against the official 重大訊息 list.",
    "One issuer (TSMC) has a valuation file; some inputs are still being sourced.",
    "No currency conversion: non-NTD amounts are rejected, not converted.",
    "Ingestion needs a Taiwan network; the free-tier quota limits daily volume.",
    "The survey is a small convenience sample (n = 10, ages 18–34): directional, not representative.",
    "Reverse DCF gives the growth the market implies, not intrinsic value; budget filings are "
    "treated as run-rate scenarios, not forecasts.",
]
half = (W - 0.2) / 2
for i, t in enumerate(lims):
    x = L + (i % 2) * (half + 0.2)
    y = 8.3 + (i // 2) * 0.46
    tb(s, x, y, 0.22, 0.2, str(i + 1), size=8, bold=True, font="Manrope", color=C["teal"])
    tb(s, x + 0.22, y + 0.01, half - 0.22, 0.42, t, size=7.1)

box(s, L, 9.75, W, 1.1, fill=C["navy"], r=0.08)
tb(s, 0.8, 9.88, W - 0.5, 0.4,
   [[("Originality.  ", {"bold": True, "color": C["teal"]}),
     "A new work built for this competition; not previously entered, awarded, commercialised or funded."]],
   size=7.6, color=C["mute"])
tb(s, 0.8, 10.28, W - 0.5, 0.5,
   [[("Better-informed investors. Verifiable numbers. ", {"color": C["white"]}),
     ("A human who decides.", {"color": C["teal"]})]], size=12, bold=True, font="Manrope")
footer(s, 12)

# ---------------------------------------------- friend's pages: renumber only
renum = {0: (2, "02"), 1: (3, "03"), 2: (4, "04"), 3: (10, "10"), 4: (11, "11")}
for idx, (page, sec_no) in renum.items():
    sl = orig[idx]
    for sh in sl.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                t = r.text
                if t.strip().endswith("/ 05") and len(t.strip()) <= 7:
                    r.text = f"{page:02d} / {TOTAL:02d}"
                elif sec_no and t.startswith(f"{idx + 1:02d}  ·  "):
                    r.text = sec_no + t[2:]
                elif "on page 5." in t:
                    r.text = t.replace("on page 5.", "on page 11.")

# ------------------------------------------------------------- reorder
sld = prs.slides._sldIdLst
ids = list(sld)
n_orig = len(orig)
o = ids[:n_orig]
new = ids[n_orig:]  # cover, flow, arch, sec, proto, ev, team
order = [new[0], o[0], o[1], o[2], new[1], new[2], new[3], new[4], new[5], o[3], o[4], new[6]]
for e in ids:
    sld.remove(e)
for e in order:
    sld.append(e)

prs.save(OUT)
print("saved", OUT, len(order), "slides")
