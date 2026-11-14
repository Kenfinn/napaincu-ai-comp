// Final-round deck for FEAF (AAIC 2026, 21 Nov), revised from the Canva deck
// "Agentic_AI_Investment_Assistant_Slides.pptx" using docs/draf-slide-tambahan.md.
//
// Run:  NODE_PATH=<dir with pptxgenjs, react-icons, react, react-dom, sharp>/node_modules \
//       node slides/build_final_deck.js <output.pptx> <skill-dir>
// <skill-dir> is the pptx skill folder (for scripts/apply_theme.js).

const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const OUT = process.argv[2];
const SKILL = process.argv[3];
const { applyTheme } = require(SKILL + "/scripts/apply_theme.js");

const C = {
  navy: "10233F", navy2: "1B355C", navy3: "2C4A73", teal: "16B8A6", tealD: "0E8C7E",
  tealL: "7FE3D6", gray: "68758A", bg: "F7F9FC", tint: "E3F6F3", line: "D5DCE6",
  mute: "C9D3E0", white: "FFFFFF", amber: "9A6400", amberT: "FBF3E4", red: "B42318",
  redT: "FDECEA", grayT: "EEF1F5", purple: "5B3FA0", purpleT: "EFEAFA",
};
const FONT = "Arial";

const THEME = {
  name: "FEAF Final",
  headFontFace: FONT,
  bodyFontFace: FONT,
  colors: {
    dk1: C.navy, lt1: C.white, dk2: C.navy2, lt2: C.bg,
    accent1: C.teal, accent2: C.tealD, accent3: C.amber, accent4: C.red,
    accent5: C.gray, accent6: C.navy3, hlink: C.tealD, folHlink: C.gray,
  },
};

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { color: "#" + color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
  pres.title = "Agentic AI Investment Assistant";
  pres.author = "Team FEAF";

  const FOOT = "Team FEAF  ·  Agentic AI Investment Assistant";
  const footer = (color) => ({
    text: {
      text: FOOT,
      options: { x: 0.6, y: 7.05, w: 8, h: 0.28, fontSize: 10, color, fontFace: FONT, margin: 0 },
    },
  });

  pres.defineSlideMaster({
    title: "LIGHT",
    background: { color: C.bg },
    objects: [
      footer(C.gray),
      {
        placeholder: {
          options: {
            name: "title", type: "title", x: 0.6, y: 0.72, w: 12.1, h: 0.75,
            fontSize: 30, bold: true, color: C.navy, fontFace: FONT, margin: 0, valign: "top", align: "left",
          },
          text: "",
        },
      },
    ],
    slideNumber: { x: 12.1, y: 7.05, w: 0.63, h: 0.28, fontSize: 10, color: C.gray, fontFace: FONT, align: "right" },
  });
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.navy },
    objects: [
      footer(C.mute),
      {
        placeholder: {
          options: {
            name: "title", type: "title", x: 0.9, y: 2.15, w: 11.6, h: 1.3,
            fontSize: 46, bold: true, color: C.white, fontFace: FONT, margin: 0, valign: "top", align: "left",
          },
          text: "",
        },
      },
    ],
    slideNumber: { x: 12.1, y: 7.05, w: 0.63, h: 0.28, fontSize: 10, color: C.mute, fontFace: FONT, align: "right" },
  });

  // ---------- helpers ----------
  const T = (s, text, x, y, w, h, o = {}) =>
    s.addText(text, Object.assign({ x, y, w, h, fontFace: FONT, margin: 0, isTextBox: true, valign: "top", color: C.navy, fontSize: 14 }, o));

  const card = (s, x, y, w, h, o = {}) =>
    s.addShape(pres.ShapeType.roundRect, Object.assign({
      x, y, w, h, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line, width: 0.75 },
    }, o));

  const pill = (s, text, x, y, w, fill, color, fs = 10) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.28, rectRadius: 0.14, fill: { color: fill }, line: { color: fill, width: 0.5 } });
    T(s, text, x, y, w, 0.28, { fontSize: fs, bold: true, color, align: "center", valign: "middle", charSpacing: 1 });
  };

  const circle = (s, label, x, y, d, fill, color = C.white, fs = 14) => {
    s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0.5 } });
    T(s, label, x, y, d, d, { fontSize: fs, bold: true, color, align: "center", valign: "middle" });
  };

  const arrow = (s, x1, y1, x2, y2, color = C.gray) =>
    s.addShape(pres.ShapeType.line, {
      x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
      line: { color, width: 1.5, endArrowType: "triangle" },
    });

  const eyebrow = (s, text, color = C.tealD) =>
    T(s, text, 0.6, 0.38, 10, 0.25, { fontSize: 11, bold: true, color, charSpacing: 3 });

  const light = (section, eb, title, notes) => {
    const s = pres.addSlide({ masterName: "LIGHT", sectionTitle: section });
    eyebrow(s, eb);
    s.addText(title, { placeholder: "title" });
    if (notes) s.addNotes(notes);
    return s;
  };

  const th = (text, o = {}) => ({ text, options: Object.assign({ bold: true, color: C.white, fill: { color: C.navy2 }, fontSize: 12, fontFace: FONT, valign: "middle" }, o) });
  const td = (text, o = {}) => ({ text, options: Object.assign({ color: C.navy, fill: { color: C.white }, fontSize: 12, fontFace: FONT, valign: "middle" }, o) });
  const border = { type: "solid", color: C.line, pt: 0.75 };

  // ---------- sections ----------
  pres.addSection({ title: "Opening" });

  // 1 · Cover
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
    T(s, "TEAM FEAF  ·  NAPAI COMPETITION 2026", 0.9, 1.55, 11, 0.3, { fontSize: 13, bold: true, color: C.teal, charSpacing: 4 });
    s.addText("Agentic AI Investment Assistant", { placeholder: "title" });
    T(s, "Turning stock filings into explainable, proactive and verifiable decision support", 0.9, 3.45, 10.8, 0.9, { fontSize: 22, color: C.mute });
    T(s, "The AI researches, explains and monitors. The investor makes every decision.", 0.9, 4.65, 11, 0.5, { fontSize: 18, bold: true, color: C.tealL });
    T(s, "Category B  ·  SYSTEX  ·  Industry & Public-Sector Co-Creation", 0.9, 5.85, 11, 0.3, { fontSize: 13, color: C.mute });
    let px = 0.9;
    for (const [t, w] of [["Agentic Workflow", 1.9], ["Domain-Specific Agent", 2.4], ["Human-in-the-loop", 2.1]]) {
      s.addShape(pres.ShapeType.roundRect, { x: px, y: 6.3, w, h: 0.34, rectRadius: 0.17, fill: { color: C.navy2 }, line: { color: C.teal, width: 0.75 } });
      T(s, t, px, 6.3, w, 0.34, { fontSize: 11, color: C.tealL, align: "center", valign: "middle" });
      px += w + 0.18;
    }
    s.addNotes("Cover. Category, track and technology tags added so the jury sees the scope at once. Only tags we really use: no Multi-Agent, no RAG.");
  }

  // 2 · Quote
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
    T(s, "“", 0.9, 0.7, 2, 1.6, { fontSize: 120, bold: true, color: C.teal, fontFace: "Georgia" });
    T(s, "I worry that AI might provide recommendations that are incorrect yet sound highly convincing, and that I might lack the expertise to spot the error.", 0.9, 2.2, 11.4, 2.2, { fontSize: 30, italic: true, color: C.white });
    T(s, "— Respondent R10, from our field survey —", 0.9, 4.65, 10, 0.35, { fontSize: 14, color: C.mute });
    T(s, "If an AI told you a stock just changed in value… how would you check?", 0.9, 5.75, 11.4, 0.5, { fontSize: 20, bold: true, color: C.tealL });
  }

  pres.addSection({ title: "Method" });

  // 3 · Problem
  {
    const s = light("Method", "THE PROBLEM", "Not short of data. Short of trust",
      "Survey of 10 investors, 6-8 Oct 2026, PDPA consent notice. Small sample: say so. The numbers show the need, they do not prove it for the whole market.");
    const chips = ["News & social feeds", "Filings & statements", "Charts & quotes", "Analysts & forums"];
    chips.forEach((c, i) => {
      const x = 0.6 + i * 2.35;
      card(s, x, 1.75, 2.2, 0.62, { fill: { color: C.grayT }, line: { color: C.line, width: 0.75 } });
      T(s, c, x, 1.75, 2.2, 0.62, { fontSize: 13, align: "center", valign: "middle" });
    });
    arrow(s, 10.05, 2.06, 10.5, 2.06, C.gray);
    card(s, 10.55, 1.75, 2.15, 0.62, { fill: { color: C.navy }, line: { color: C.navy, width: 0.75 } });
    T(s, "The investor filters & checks it all, alone", 10.62, 1.75, 2.0, 0.62, { fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle" });

    const pains = [
      [fa.FaClock, "Time drain", "Hours spent gathering before any analysis"],
      [fa.FaSearch, "Shallow reading", "Ratios read without context; value traps slip through"],
      [fa.FaQuestionCircle, "Unverifiable", "AI answers sound right but can’t be checked"],
    ];
    for (let i = 0; i < 3; i++) {
      const x = 0.6 + i * 4.1;
      card(s, x, 2.85, 3.9, 2.35);
      s.addShape(pres.ShapeType.ellipse, { x: x + 0.3, y: 3.1, w: 0.7, h: 0.7, fill: { color: C.tint }, line: { color: C.tint, width: 0.5 } });
      s.addImage({ data: await icon(pains[i][0], C.tealD), x: x + 0.47, y: 3.27, w: 0.36, h: 0.36 });
      T(s, pains[i][1], x + 0.3, 3.98, 3.3, 0.4, { fontSize: 20, bold: true });
      T(s, pains[i][2], x + 0.3, 4.45, 3.3, 0.7, { fontSize: 14, color: C.gray });
    }
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 5.5, w: 12.1, h: 1.25, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy, width: 0.5 } });
    [["8/10", "feel overwhelmed"], ["9/10", "want to see the AI’s reasoning"], ["8/10", "fear inaccurate AI answers"]].forEach(([n, l], i) => {
      const x = 0.9 + i * 3.95;
      T(s, n, x, 5.65, 1.4, 0.7, { fontSize: 34, bold: true, color: C.teal, valign: "middle" });
      T(s, l, x + 1.45, 5.65, 2.3, 0.7, { fontSize: 14, color: C.white, valign: "middle" });
    });
    T(s, "Field survey, n = 10", 0.9, 6.42, 6, 0.25, { fontSize: 10, color: C.mute });
  }

  // 4 · DCF
  {
    const s = light("Method", "HOW WE ANALYSE A STOCK", "We value each company with a DCF model",
      "Inputs not on the slide: risk-free 1.94% (Taiwan 10-year government bond), equity risk premium 5.01% (Damodaran), beta from two years of weekly returns vs TAIEX, 1.0 when data is short. All arithmetic runs in plain code, never in the model.");
    const cards = [
      ["FCF", "Free cash flow", "Free cash flow the business generates after reinvestment"],
      ["WACC", "Discount rate", "Cost of equity estimated with CAPM"],
      ["Debt", "Net debt", "Debt minus cash, from the balance sheet"],
      ["Shares", "Shares outstanding", "To get value per share"],
    ];
    cards.forEach(([big, h, d], i) => {
      const x = 0.6 + i * 3.08;
      card(s, x, 1.8, 2.85, 2.7);
      T(s, big, x + 0.3, 2.05, 2.3, 0.7, { fontSize: 34, bold: true, color: C.tealD });
      T(s, h, x + 0.3, 2.9, 2.3, 0.4, { fontSize: 16, bold: true });
      T(s, d, x + 0.3, 3.35, 2.3, 1.0, { fontSize: 14, color: C.gray });
    });
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.85, w: 12.1, h: 1.2, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy, width: 0.5 } });
    T(s, "Value per share = (present value of future cash flows − net debt) ÷ shares outstanding, then compared with the market price.", 0.95, 4.85, 11.4, 1.2, { fontSize: 18, color: C.white, valign: "middle" });
    T(s, "Fixed inputs: risk-free 1.94% (Taiwan 10-year bond) · equity risk premium 5.01% (Damodaran) · beta from two years of weekly returns vs TAIEX, 1.0 when data is short.", 0.6, 6.3, 12.1, 0.5, { fontSize: 12, color: C.gray });
  }

  // 5 · Why DCF
  {
    const s = light("Method", "WHY DCF  ·  TRUSTED DATA", "Why DCF, not other methods",
      "Replaces the old claim '100% of numbers traced'. What we can defend: 0 wrong numbers on 46 real filings and 0 of 72 attacker numbers published. Say 'every published number carries its source sentence'.");
    const tiles = [
      ["MOPS", "Official filings and company announcements"],
      ["TWSE + TPEx", "Open data: prices and shares outstanding"],
      ["0 / 46", "wrong numbers published on real filings, each with its source sentence"],
    ];
    tiles.forEach(([big, d], i) => {
      const y = 1.75 + i * 1.62;
      card(s, 0.6, y, 4.2, 1.45, { fill: { color: i === 2 ? C.navy : C.white }, line: { color: i === 2 ? C.navy : C.line, width: 0.75 } });
      T(s, big, 0.9, y + 0.15, 3.6, 0.6, { fontSize: 26, bold: true, color: i === 2 ? C.teal : C.tealD });
      T(s, d, 0.9, y + 0.8, 3.6, 0.6, { fontSize: 13, color: i === 2 ? C.white : C.gray });
    });
    const rows = [
      [th("Method"), th("Why it falls short")],
      [td("P/E & P/B multiples", { bold: true }), td("Quick, but depends on peers and market mood; can’t show what one filing changes")],
      [td("Technical analysis", { bold: true }), td("Reads price patterns only; ignores cash, debt and earnings")],
      [td("CAPM alone", { bold: true }), td("Gives a required return, not a fair value per share")],
      [td("DCF (our choice)", { bold: true, color: C.tealD, fill: { color: C.tint } }), td("Values the business from its cash flows; every filing maps to an input we can trace", { fill: { color: C.tint }, bold: true })],
    ];
    s.addTable(rows, { x: 5.1, y: 1.75, w: 7.6, colW: [2.2, 5.4], rowH: [0.45, 0.95, 0.85, 0.85, 1.0], border, fontFace: FONT, margin: [0.06, 0.12, 0.06, 0.12], fontSize: 13 });
    T(s, "Financial-sector issuers get no DCF (marked “not applicable”); their filings are held for a person.", 5.1, 6.4, 7.6, 0.4, { fontSize: 12, color: C.gray });
  }

  // 6 · How it works
  {
    const s = light("Method", "HOW IT WORKS", "From a new filing to a verified, explained alert",
      "Only clause-20 filings (valuation lane) call the model in the 46-filing test: 5 model calls. Risk, capital, report, severe and governance clauses are parsed by code.");
    const steps = [
      ["Fetch", "RULE-BASED", "Pull new MOPS filings for watched stocks"],
      ["Validate", "RULE-BASED", "Reject block pages, fix dates"],
      ["Screen", "RULE-BASED", "Drop routine filings"],
      ["Triage", "LLM AGENT", "Does it touch valuation?"],
      ["Extract", "LLM AGENT", "Number + exact source sentence"],
      ["Recompute", "RULE-BASED", "Update valuation, show change"],
      ["Verify", "RULE-BASED", "Every number must match the source"],
      ["Decide", "HUMAN", "Publish alert, or hold for a human"],
    ];
    steps.forEach(([name, tag, d], i) => {
      const col = i % 4, row = Math.floor(i / 4);
      const x = 0.6 + col * 3.08, y = 1.75 + row * 2.2;
      card(s, x, y, 2.85, 1.95);
      circle(s, String(i + 1), x + 0.25, y + 0.22, 0.46, C.navy);
      const [pf, pc] = tag === "LLM AGENT" ? [C.tint, C.tealD] : tag === "HUMAN" ? [C.amberT, C.amber] : [C.grayT, C.gray];
      pill(s, tag, x + 1.45, y + 0.3, 1.2, pf, pc, 9);
      T(s, name, x + 0.25, y + 0.85, 2.4, 0.4, { fontSize: 19, bold: true });
      T(s, d, x + 0.25, y + 1.28, 2.4, 0.6, { fontSize: 13, color: C.gray });
    });
    T(s, "The LLM is used only where language understanding is needed. Code checks every number before anyone sees it.", 0.6, 6.25, 12.1, 0.5, { fontSize: 16, bold: true });
  }

  // 6b · Architecture and data flow
  {
    const s = light("Method", "ARCHITECTURE AND DATA FLOW", "Where data comes from, and where it goes",
      "Based on docs/diagram-alur.md part 1. The server holds the only copy of data and traces. The model sees public filing text only. Edit routes (add or remove a stock, change a threshold, approve a review) need an access code; there is no route that trades, sends email or pays. Ask FEAF can only call six read-only tools, at most five steps per question.");
    // sources
    const src = [
      ["TWSE / TPEx OpenAPI", "Daily filings (material information)"],
      ["TWSE / TPEx OpenAPI", "Prices, P/E, company profile"],
      ["FinMind", "Income statement, balance sheet, cash flow"],
      ["MOPS", "Filing history, via a Taiwan network"],
    ];
    T(s, "SOURCES", 0.6, 1.62, 2.9, 0.22, { fontSize: 10, bold: true, color: C.gray, charSpacing: 3 });
    src.forEach(([h, d], i) => {
      const y = 1.9 + i * 1.08;
      card(s, 0.6, y, 2.9, 0.92, { fill: { color: C.grayT } });
      T(s, h, 0.75, y + 0.1, 2.6, 0.3, { fontSize: 13, bold: true });
      T(s, d, 0.75, y + 0.42, 2.6, 0.45, { fontSize: 11, color: C.gray });
      arrow(s, 3.52, y + 0.46, 3.88, y + 0.46, C.gray);
    });
    // server
    s.addShape(pres.ShapeType.roundRect, { x: 3.9, y: 1.62, w: 6.0, h: 4.6, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.navy2, width: 1.25 } });
    T(s, "SERVER  ·  one Docker container", 4.08, 1.72, 5.5, 0.25, { fontSize: 10, bold: true, color: C.navy2, charSpacing: 3 });
    const box = (x, y, w, h, title, body, f, c) => {
      s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: f }, line: { color: c, width: 1 } });
      T(s, title, x + 0.12, y + 0.08, w - 0.24, 0.3, { fontSize: 13, bold: true, color: C.navy });
      T(s, body, x + 0.12, y + 0.4, w - 0.24, h - 0.45, { fontSize: 11, color: C.navy });
    };
    box(4.08, 2.1, 1.75, 1.45, "Fetcher", "Validates the response shape and drops personal fields before saving.", C.amberT, C.amber);
    box(6.05, 2.1, 3.65, 1.45, "Agent pipeline", "Screen, triage, extract, verify, recompute, publish or hold. The checker and the DCF are plain code; the model only reads the clause.", C.amberT, C.amber);
    arrow(s, 5.85, 2.82, 6.03, 2.82, C.gray);
    box(4.08, 3.85, 5.62, 0.95, "Data store (/data volume)", "Filings, audit traces, review decisions, thumbs feedback, cache", C.purpleT, C.purple);
    arrow(s, 4.95, 3.57, 4.95, 3.83, C.gray);
    arrow(s, 7.88, 3.57, 7.88, 3.83, C.gray);
    box(4.08, 5.08, 5.62, 1.0, "Ask FEAF", "Guard (refuses advice, prediction, personal data) → six read-only tools, 5 steps at most → number checker", C.amberT, C.amber);
    arrow(s, 7.88, 5.06, 7.88, 4.82, C.gray);
    // model
    s.addShape(pres.ShapeType.roundRect, { x: 10.2, y: 2.1, w: 2.5, h: 3.98, rectRadius: 0.06, fill: { color: C.tint }, line: { color: C.teal, width: 1 } });
    T(s, "Gemini 3.6 Flash", 10.32, 2.18, 2.26, 0.3, { fontSize: 13, bold: true, color: C.tealD });
    T(s, "Reads clause text and calls Ask FEAF tools. Temperature 0. Backup model, then rule reasoner if it fails.", 10.32, 2.55, 2.26, 1.5, { fontSize: 11 });
    T(s, "Sees public filing text only: no personal data, keys or credentials. Never computes a number.", 10.32, 3.75, 2.26, 1.5, { fontSize: 11, bold: true });
    s.addShape(pres.ShapeType.line, { x: 9.72, y: 2.82, w: 0.46, h: 0, line: { color: C.tealD, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
    s.addShape(pres.ShapeType.line, { x: 9.72, y: 5.58, w: 0.46, h: 0, line: { color: C.tealD, width: 1.5, beginArrowType: "triangle", endArrowType: "triangle" } });
    // UI
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 6.37, w: 12.1, h: 0.5, rectRadius: 0.06, fill: { color: C.navy }, line: { color: C.navy, width: 0.5 } });
    T(s, "Web, English / 中文 / Bahasa Indonesia:  Watchlist  ·  Alerts  ·  Review  ·  Audit trail  ·  Ask FEAF", 0.85, 6.37, 11.6, 0.5, { fontSize: 13, bold: true, color: C.white, valign: "middle" });
  }

  pres.addSection({ title: "Agent design" });

  // 7 · Why agentic + states
  {
    const s = light("Agent design", "AGENT DESIGN", "Why this needs an agent, not a chatbot",
      "The agent breaks one goal into dependent steps, calls tools (TWSE/TPEx OpenAPI, FinMind, DCF calculator, language model), adjusts on results (model fails -> backup model -> rule reasoner; checker fails -> HELD) and stops for a person when unsure. Decisions are taken by code that can be audited; the model reads the clause in one step only.");
    const cmp = [
      ["Chatbot / RAG", "Answers when asked and quotes text. Never starts, cannot recompute a valuation, no check on its own numbers.", false],
      ["Fixed workflow", "Same steps for every filing. Cannot read free-text clauses or decide when to stop and ask a person.", false],
      ["FEAF agent", "Decides per filing: publish, hold or archive. Plans steps, uses tools, adjusts on results, stops for a human.", true],
    ];
    cmp.forEach(([h, d, hi], i) => {
      const x = 0.6 + i * 4.1;
      card(s, x, 1.7, 3.9, 1.75, { fill: { color: hi ? C.navy : C.white }, line: { color: hi ? C.navy : C.line, width: 0.75 } });
      T(s, h, x + 0.25, 1.85, 3.4, 0.4, { fontSize: 18, bold: true, color: hi ? C.teal : C.navy });
      T(s, d, x + 0.25, 2.3, 3.4, 1.1, { fontSize: 13, color: hi ? C.white : C.gray });
    });
    T(s, "STATE OF ONE FILING", 0.6, 3.72, 6, 0.25, { fontSize: 11, bold: true, color: C.tealD, charSpacing: 3 });
    const st = ["FETCHED", "VALIDATED", "SCREENED", "TRIAGED", "EXTRACTED", "VERIFIED", "VALUED", "PUBLISHED"];
    const cw = 1.3, gap = 0.24;
    st.forEach((n, i) => {
      const x = 0.6 + i * (cw + gap);
      const last = i === st.length - 1;
      s.addShape(pres.ShapeType.roundRect, { x, y: 4.1, w: cw, h: 0.55, rectRadius: 0.08, fill: { color: last ? C.teal : C.navy2 }, line: { color: last ? C.teal : C.navy2, width: 0.5 } });
      T(s, n, x, 4.1, cw, 0.55, { fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle" });
      if (!last) arrow(s, x + cw + 0.02, 4.375, x + cw + gap - 0.02, 4.375, C.gray);
    });
    const cx = (i) => 0.6 + i * (cw + gap) + cw / 2;
    const boxes = [
      [0.6 + 2 * (cw + gap), 2 * cw + gap, "ARCHIVED", "Not relevant, or below the threshold", C.grayT, C.gray, [2, 3]],
      [0.6 + 4 * (cw + gap), 2 * cw + gap, "HELD", "Check failed, low confidence, or no model yet", C.amberT, C.amber, [4, 5]],
      [0.6 + 6 * (cw + gap), 2 * cw + gap, "HUMAN REVIEW", "Approve doubtful cases; invented numbers can only be archived", C.purpleT, C.purple, []],
    ];
    boxes.forEach(([x, w, h, d, f, c, from]) => {
      s.addShape(pres.ShapeType.roundRect, { x, y: 5.25, w, h: 1.0, rectRadius: 0.08, fill: { color: f }, line: { color: c, width: 1 } });
      T(s, h, x + 0.12, 5.3, w - 0.24, 0.3, { fontSize: 12, bold: true, color: c });
      T(s, d, x + 0.12, 5.62, w - 0.24, 0.6, { fontSize: 11, color: C.navy });
      from.forEach((i) => arrow(s, cx(i), 4.68, cx(i), 5.23, c));
    });
    T(s, "Decisions are taken by code that can be audited. The model is used in one step only: reading the clause.", 0.6, 6.5, 12.1, 0.4, { fontSize: 14, bold: true });
  }

  // 8 · Closed loop
  {
    const s = light("Agent design", "AGENT DESIGN", "Four stages, one closed loop",
      "The tender asks for personalised intelligence, proactive delivery, behavioural feedback and continuous optimisation. Show one example live: two thumbs-down on the same clause make the next similar alert archived with its score and threshold as the reason. Thresholds are per server (one investor per server); do not claim per-user personalisation.");
    const stages = [
      [fa.FaUserCog, "Personalised", "Risk profile (conservative, moderate, aggressive) sets thresholds, DCF class, strengths and watch-outs"],
      [fa.FaBell, "Proactive", "The server checks filings every 10 minutes and raises an alert without being asked"],
      [fa.FaThumbsUp, "Feedback", "Thumbs up or down on each alert tells the agent what was useful"],
      [fa.FaSlidersH, "Optimised", "Each thumbs-down raises that clause’s threshold by 0.05, each thumbs-up lowers it by 0.02, within 0.40–0.90"],
    ];
    for (let i = 0; i < 4; i++) {
      const x = 0.6 + i * 3.08;
      card(s, x, 1.8, 2.75, 3.2);
      s.addShape(pres.ShapeType.ellipse, { x: x + 0.3, y: 2.05, w: 0.75, h: 0.75, fill: { color: C.tint }, line: { color: C.tint, width: 0.5 } });
      s.addImage({ data: await icon(stages[i][0], C.tealD), x: x + 0.49, y: 2.24, w: 0.37, h: 0.37 });
      T(s, `${i + 1}  ${stages[i][1]}`, x + 0.3, 3.0, 2.3, 0.4, { fontSize: 18, bold: true });
      T(s, stages[i][2], x + 0.3, 3.5, 2.25, 1.45, { fontSize: 13, color: C.gray });
      if (i < 3) arrow(s, x + 2.78, 3.4, x + 3.05, 3.4, C.teal);
    }
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 5.35, w: 12.1, h: 1.2, rectRadius: 0.08, fill: { color: C.tint }, line: { color: C.teal, width: 0.75 } });
    T(s, "The loop closes: ", 0.9, 5.35, 2.2, 1.2, { fontSize: 15, bold: true, color: C.tealD, valign: "middle" });
    T(s, "two thumbs-down on the same clause, and the next similar alert is archived with its score and threshold as the reason. Thresholds are kept per server.", 3.0, 5.35, 9.4, 1.2, { fontSize: 15, valign: "middle" });
  }

  // 9 · What we built
  {
    const s = light("Agent design", "WHAT WE BUILT", "The FEAF website: four parts, one goal");
    const parts = [
      [fa.FaChartLine, "DCF valuation", "Value per share with WACC, cost of debt and cost of equity, built from verified numbers"],
      [fa.FaBell, "Watchlist & alerts", "Follow your stocks; get an alert when a filing changes a valuation input"],
      [fa.FaShieldAlt, "Safe by design", "Every number traced to its source; no trading, no broker login"],
      [fa.FaComments, "Ask FEAF", "Ask about any Taiwan stock: prices, fundamentals, company comparisons, in English, Chinese or Bahasa Indonesia"],
    ];
    for (let i = 0; i < 4; i++) {
      const x = 0.6 + (i % 2) * 6.15, y = 1.75 + Math.floor(i / 2) * 2.55;
      card(s, x, y, 5.95, 2.3);
      s.addShape(pres.ShapeType.ellipse, { x: x + 0.35, y: y + 0.4, w: 0.9, h: 0.9, fill: { color: C.navy }, line: { color: C.navy, width: 0.5 } });
      s.addImage({ data: await icon(parts[i][0], C.teal), x: x + 0.59, y: y + 0.64, w: 0.42, h: 0.42 });
      T(s, parts[i][1], x + 1.6, y + 0.35, 4.1, 0.45, { fontSize: 22, bold: true });
      T(s, parts[i][2], x + 1.6, y + 0.9, 4.1, 1.3, { fontSize: 15, color: C.gray });
    }
  }

  // 9b · Prototype screens (alert -> human decision)
  const shot = (s, file, x, y, w, caption, sub) => {
    const h = (w * 800) / 1168;
    card(s, x - 0.06, y - 0.06, w + 0.12, h + 0.12, { fill: { color: C.white }, line: { color: C.line, width: 1 } });
    s.addImage({ path: require("path").join(__dirname, "assets", file), x, y, w, h, altText: caption });
    T(s, caption, x, y + h + 0.17, w, 0.3, { fontSize: 14, bold: true });
    T(s, sub, x, y + h + 0.5, w, 0.7, { fontSize: 12, color: C.gray });
  };
  {
    const s = light("Agent design", "THE PROTOTYPE", "From held alert to a human decision",
      "Real screens of the running app (QA-6 captures, 12 Nov). They use the four sample cases shipped in data/fixtures (the amber banner says so) and the rule-based path (no API key on that run). TODO(team): recapture from the live server with Gemini active before the final, so the screens match the model path described in the deck.");
    shot(s, "ui-alert-held.png", 0.8, 1.7, 5.2, "Alert held for review", "A USD amount cannot be converted silently, so the verifier stops it and says why. The source sentence and the original MOPS link are shown.");
    shot(s, "ui-review-queue.png", 7.3, 1.7, 5.2, "Review queue", "Doubtful filings wait here. A person approves and publishes, or archives. A note is required and the decision is recorded.");
    T(s, "Screens use the sample data shipped with the app and the rule-based path. Real filings replace the samples after “Check now”.", 0.6, 6.68, 12.1, 0.28, { fontSize: 11, color: C.gray });
  }

  // 9c · Prototype screens (valuation, audit trail)
  {
    const s = light("Agent design", "THE PROTOTYPE", "Every number shows how it was made",
      "Valuation page: the DCF is computed by plain code (scripts/dcf.py), with sensitivity table and the source of every input. Audit trail: nine states from FETCHED to PUBLISHED, with the prompt version and fallback reason recorded; this is the operation trace Appendix 2 asks for. Same caveat as the previous slide: sample data, rule-based path.");
    shot(s, "ui-valuation.png", 0.8, 1.7, 5.2, "Valuation, TSMC 2330", "Enterprise-value bridge, cost of capital, reverse DCF and a sensitivity table. Below the fold: the source of each input.");
    shot(s, "ui-audit-trail.png", 7.3, 1.7, 5.2, "Audit trail, one filing", "Each state with its result and timing, from FETCHED to PUBLISHED. This run used the rule-based reasoner, so it shows 0 model calls.");
    T(s, "Screens use the sample data shipped with the app and the rule-based path. Real filings replace the samples after “Check now”.", 0.6, 6.68, 12.1, 0.28, { fontSize: 11, color: C.gray });
  }

  pres.addSection({ title: "Evidence" });

  // 10 · Results
  {
    const s = light("Evidence", "RESULTS", "Measured on real filings, not promised",
      "Official numbers are the rule path measured BEFORE any tuning (eval/hasil/evaluasi-20261111T084547Z.md). After tuning the figures are in-sample (43/46 rules, 42/46 model): do not call them accuracy. Out-of-sample accuracy is not yet measured; a blind set of 15-20 fresh filings is the next step. The labeller is a team member. Ask FEAF 50/52 was measured before the 11 Nov checker fix and has not been re-run with Gemini. TODO(team): re-run scripts/evaluasi.py --chat before the final.");
    const stats = [
      ["0 / 46", "wrong numbers published", "5 / 46 without the checker"],
      ["41 / 46", "decisions match the expert", "15 / 46 without the checker"],
      ["25 min → 0.7 s", "per filing: manual vs agent", "mean latency with Gemini 3.6 Flash"],
      ["USD 0.007", "model cost, 46 filings", "temperature 0, paid tier"],
    ];
    stats.forEach(([n, l, sub], i) => {
      const x = 0.6 + (i % 2) * 2.95, y = 1.75 + Math.floor(i / 2) * 1.95;
      card(s, x, y, 2.8, 1.8, { fill: { color: i === 0 ? C.navy : C.white }, line: { color: i === 0 ? C.navy : C.line, width: 0.75 } });
      T(s, n, x + 0.2, y + 0.15, 2.45, 0.6, { fontSize: i === 2 ? 20 : 26, bold: true, color: i === 0 ? C.teal : C.tealD, valign: "middle" });
      T(s, l, x + 0.2, y + 0.82, 2.45, 0.4, { fontSize: 13, bold: true, color: i === 0 ? C.white : C.navy });
      T(s, sub, x + 0.2, y + 1.22, 2.45, 0.5, { fontSize: 11, color: i === 0 ? C.mute : C.gray });
    });
    const rows = [
      [th("Metric"), th("FEAF agent", { align: "center" }), th("Without checker", { align: "center" })],
      [td("Wrong numbers published"), td("0 / 46", { align: "center", bold: true, color: C.tealD }), td("5 / 46", { align: "center", color: C.red, bold: true })],
      [td("Decision matches expert"), td("41 / 46 (89%)", { align: "center", bold: true }), td("15 / 46 (33%)", { align: "center" })],
      [td("Signal level matches expert"), td("21 / 29 (72%)", { align: "center", bold: true }), td("0 / 29", { align: "center" })],
      [td("Held for a person"), td("13 / 46 (28%)", { align: "center", bold: true }), td("33 / 46 (72%)", { align: "center" })],
    ];
    s.addTable(rows, { x: 6.7, y: 1.75, w: 6.0, colW: [2.5, 1.75, 1.75], rowH: 0.5, border, fontFace: FONT, margin: [0.04, 0.1, 0.04, 0.1] });
    card(s, 6.7, 4.5, 6.0, 1.55, { fill: { color: C.tint }, line: { color: C.teal, width: 0.75 } });
    T(s, "Ask FEAF: 52 questions, 3 languages", 6.95, 4.62, 5.5, 0.35, { fontSize: 14, bold: true, color: C.tealD });
    T(s, "27 / 27 out-of-scope, advice and injected questions refused\n0 buy / sell words reached the user\n50 / 52 correct (both misses fell back to a sourced answer)", 6.95, 5.0, 5.55, 1.0, { fontSize: 12 });
    T(s, "Test set: 46 real MOPS filings of 9 Nov 2026, labelled by a finance team member. Rule path, measured before tuning. “Without checker” = same pipeline that publishes whatever is extracted. Manual baseline 20–30 min per filing (25 used). Source: eval/hasil.", 0.6, 6.3, 12.1, 0.55, { fontSize: 10, color: C.gray });
  }

  // 11 · Safety
  {
    const s = light("Evidence", "SAFETY, CONTROL AND GOVERNANCE", "Built so a wrong number cannot reach an investor",
      "Open gaps, say them plainly: one shared access code (no roles), no per-IP rate limit, injection patterns are regex-based so the number check is the backstop. Incident: the TPEx company-profile cache briefly kept officer names and contact emails until 10 Nov (commit e4572d6); never shown to users; fixed with a whitelist and an automated test. Rules forbid keys and personal data in the deck.");
    const ctr = [
      ["Checker, not trust", "Seven checks before publishing: label, quote, digits, currency, unit, conversion, magnitude. The model never does arithmetic."],
      ["A person decides doubtful cases", "Held filings go to a review queue. Invented numbers can only be archived. Severe clauses are always held."],
      ["Information only", "No orders, no broker login, no email, no payment. Edits need an access code. No buy or sell label (FSC)."],
    ];
    ctr.forEach(([h, d], i) => {
      const y = 1.7 + i * 1.65;
      card(s, 0.6, y, 4.6, 1.5);
      circle(s, String(i + 1), 0.85, y + 0.2, 0.42, C.teal);
      T(s, h, 1.4, y + 0.2, 3.65, 0.42, { fontSize: 15, bold: true, valign: "middle" });
      T(s, d, 0.85, y + 0.72, 4.15, 0.75, { fontSize: 12, color: C.gray });
    });
    const risk = [
      ["Prompt injection", "Pattern scan; every number needs a source sentence", "0 / 72 attacker numbers published"],
      ["Unauthorised tool use", "Closed tool list; no shell, order or email tool", "Edit routes: 401 without code"],
      ["Data leakage", "Whitelist of public company fields", "TPEx cache fix, 10 Nov"],
      ["Hallucinated numbers", "Code computes; checker matches every number", "Failed claim goes to HELD"],
      ["Sector bias", "Financial issuers: “DCF not applicable”", "Test in suite"],
      ["Malicious input", "Escaped templates; strict stock-code pattern", "Tests in suite"],
      ["Supply chain", "4 pinned Python libraries; no JS framework", "requirements.txt"],
      ["Service failure", "Retry, backup model, rule reasoner, cache", "/sehat health page"],
    ];
    const rows = [[th("Risk (Art. 14)", { fontSize: 11 }), th("Protection", { fontSize: 11 }), th("Evidence", { fontSize: 11 })]].concat(
      risk.map((r, i) => [
        td(r[0], { bold: true, fontSize: 11, fill: { color: i % 2 ? C.grayT : C.white } }),
        td(r[1], { fontSize: 11, fill: { color: i % 2 ? C.grayT : C.white } }),
        td(r[2], { fontSize: 11, fill: { color: i % 2 ? C.grayT : C.white } }),
      ])
    );
    s.addTable(rows, { x: 5.5, y: 1.7, w: 7.2, colW: [1.75, 3.2, 2.25], rowH: 0.5, border, fontFace: FONT, margin: [0.03, 0.08, 0.03, 0.08] });
    T(s, "Open gaps: one shared access code (no roles), no per-IP rate limit, injection patterns are regex-based; the number check is the backstop.", 0.6, 6.55, 12.1, 0.4, { fontSize: 11, color: C.amber });
  }

  // 12 · User testing
  {
    const s = light("Evidence", "USER TESTING  ·  FEAF WEBSITE", "What users valued",
      "Small sample, no real money, no trading. 4/6 means six valid answers on this question. TODO(team): add task metrics (time, success) and before/after time from respondents if available.");
    const tiles = [["7", "users tested the live website"], ["4/6", "valid answers: purpose very or mostly clear"], ["#1", "most valued feature: Ask FEAF"], ["DCF", "output seen as a core strength"]];
    tiles.forEach(([n, l], i) => {
      const x = 0.6 + i * 3.08;
      card(s, x, 1.75, 2.85, 2.2);
      T(s, n, x + 0.3, 1.95, 2.3, 0.9, { fontSize: 44, bold: true, color: C.tealD, valign: "middle" });
      T(s, l, x + 0.3, 2.95, 2.3, 0.9, { fontSize: 14, color: C.gray });
    });
    card(s, 0.6, 4.3, 12.1, 2.3, { fill: { color: C.navy }, line: { color: C.navy, width: 0.75 } });
    T(s, "What they actually used it for", 0.95, 4.5, 11, 0.4, { fontSize: 18, bold: true, color: C.teal });
    T(s, "Checking prices, comparing companies (e.g., TSMC 2330 vs Hon Hai 2317) and understanding fundamentals. Beginners also used it to learn investment terms. Watchlist and alerts were valued for monitoring.", 0.95, 5.0, 11.2, 1.0, { fontSize: 16, color: C.white });
    T(s, "Sandbox use: no real money, no trading.", 0.95, 6.1, 11, 0.3, { fontSize: 12, color: C.mute });
  }

  // 13 · Field validation
  {
    const s = light("Evidence", "FIELD VALIDATION", "Evidence from real users and real filings",
      "Claim: Level 2 reached, Level 3 partly (7 users). Do not claim Level 4. The gold-set labeller is in the team, say so. TODO(team): name the field liaison and contacts (Art. 6.2 requires one when field validation is done), say who was interviewed, add a before/after time from respondents.");
    const stat = (t, f, c) => td(t, { fill: { color: f }, color: c, bold: true, align: "center" });
    const rows = [
      [th("Level"), th("Evidence"), th("Status", { align: "center" })],
      [td("1  Needs", { bold: true }), td("Survey of 10 investors, 6–8 Oct 2026, with a PDPA consent notice: 8/10 overwhelmed, 9/10 want to see the reasoning, 8/10 fear wrong AI answers"), stat("Done", C.tint, C.tealD)],
      [td("2  Data / process", { bold: true }), td("46 real filings of 9 Nov labelled by a finance team member; manual time baseline of 25 minutes per filing; official TWSE / TPEx / MOPS data and documented sources"), stat("Done (labeller in team)", C.tint, C.tealD)],
      [td("3  Prototype trial", { bold: true }), td("7 users tested the live website with no real money; Ask FEAF the most valued feature"), stat("Partly (small sample)", C.amberT, C.amber)],
      [td("4  Field pilot", { bold: true }), td("Limited deployment with operating records and before/after comparison"), stat("Not claimed", C.grayT, C.gray)],
    ];
    s.addTable(rows, { x: 0.6, y: 1.75, w: 12.1, colW: [2.2, 7.6, 2.3], rowH: [0.45, 0.95, 1.0, 0.8, 0.8], border, fontFace: FONT, margin: [0.06, 0.14, 0.06, 0.14], fontSize: 13 });
    card(s, 0.6, 6.0, 12.1, 0.75, { fill: { color: C.tint }, line: { color: C.teal, width: 0.75 } });
    T(s, "The jury scores Field Impact from Level 2 upward. We state exactly what we have and where its limits are.", 0.9, 6.0, 11.5, 0.75, { fontSize: 14, bold: true, valign: "middle" });
  }

  // 14 · Improve next
  {
    const s = light("Evidence", "WHAT USERS ASKED FOR", "What we will improve next");
    const items = [
      ["Charts", "Visual DCF, WACC and company comparisons"],
      ["Onboarding", "Tooltips and a guided tour for Alerts, Review, Thresholds"],
      ["Clean sources", "Readable citations instead of raw JSON"],
      ["Mobile layout", "Less scrolling on data-heavy pages"],
    ];
    items.forEach(([h, d], i) => {
      const x = 0.6 + i * 3.08;
      card(s, x, 1.8, 2.85, 2.7);
      circle(s, String(i + 1), x + 0.3, 2.05, 0.55, C.teal, C.white, 18);
      T(s, h, x + 0.3, 2.85, 2.3, 0.45, { fontSize: 20, bold: true });
      T(s, d, x + 0.3, 3.4, 2.3, 1.0, { fontSize: 14, color: C.gray });
    });
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.9, w: 12.1, h: 1.3, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy, width: 0.5 } });
    T(s, "Next phase", 0.95, 4.9, 2.3, 1.3, { fontSize: 18, bold: true, color: C.teal, valign: "middle" });
    T(s, "Peer benchmarking and supply-chain data (suppliers, commodity prices) for deeper analysis; a blind test set of fresh filings to measure out-of-sample accuracy.", 3.3, 4.9, 9.1, 1.3, { fontSize: 16, color: C.white, valign: "middle" });
  }

  // 15 · Limits
  {
    const s = light("Evidence", "LIMITS AND RECOVERY", "What FEAF does not do, and how it fails safely",
      "Appendix 2 asks for known limits, worst case and recovery. Out-of-sample accuracy is not measured yet. DCF constants (risk-free 1.94%, ERP 5.01%) are fixed inputs.");
    card(s, 0.6, 1.75, 5.2, 4.95);
    T(s, "Known limits", 0.9, 1.9, 4.6, 0.4, { fontSize: 18, bold: true, color: C.tealD });
    const lim = [
      "Accuracy is measured on 46 filings labelled in-team; a blind set is next",
      "No currency conversion: USD and other foreign amounts are held",
      "Financial-sector issuers get no DCF",
      "The exchange feed lags about one day; older history needs a Taiwan network",
      "Beta is 1.0 (flagged) when price history is short",
    ].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1, paraSpaceAfter: 14 } }));
    T(s, lim, 0.9, 2.4, 4.7, 4.1, { fontSize: 15 });
    const rows = [
      [th("Worst case"), th("What happens"), th("Recovery")],
      [td("Model returns an invented or injected number", { bold: true }), td("Checker fails it; nothing published"), td("Held, failing check named in the trace")],
      [td("Model down, rate-limited or out of credit", { bold: true }), td("Retry, then backup model, then rule reasoner"), td("Shown on /sehat; next cycle retries")],
      [td("Run takes too long", { bold: true }), td("Cap of 90 s and 40 calls per run"), td("Rest answered next cycle")],
      [td("Server restart", { bold: true }), td("Data and traces live in the /data volume"), td("/sehat shows the code version")],
    ];
    s.addTable(rows, { x: 6.1, y: 1.75, w: 6.6, colW: [2.2, 2.3, 2.1], rowH: [0.45, 1.1, 1.1, 0.95, 0.95], border, fontFace: FONT, fontSize: 12, margin: [0.05, 0.1, 0.05, 0.1] });
  }

  pres.addSection({ title: "Business" });

  // 16 · Market
  {
    const s = light("Business", "MARKET & BUSINESS MODEL", "Start focused, then scale with partners",
      "TODO(team): fill the sources for TAM and SAM (e.g. TDCC / TWSE account statistics and year). Premium price is a test price from the survey.");
    [["14.58M", "TAM", "individual TWSE account holders"], ["4.29M", "SAM", "holders aged 20–40"], ["~43K", "SOM", "~1% of SAM, illustrative"]].forEach(([n, k, d], i) => {
      const x = 0.6 + i * 4.1;
      card(s, x, 1.75, 3.9, 1.85, { fill: { color: i === 2 ? C.navy : C.white }, line: { color: i === 2 ? C.navy : C.line, width: 0.75 } });
      T(s, n, x + 0.3, 1.9, 3.3, 0.8, { fontSize: 40, bold: true, color: i === 2 ? C.teal : C.tealD, valign: "middle" });
      T(s, k, x + 0.3, 2.8, 3.3, 0.3, { fontSize: 13, bold: true, color: i === 2 ? C.white : C.navy });
      T(s, d, x + 0.3, 3.1, 3.3, 0.4, { fontSize: 13, color: i === 2 ? C.mute : C.gray });
    });
    [["Free", "Ask FEAF, watchlist and limited alerts"], ["Premium", "Full alerts, DCF charts, peer comparison, audit trail · test price NT$600–800 / month"], ["B2B2C (later)", "Licensed to brokers and fintech apps"]].forEach(([h, d], i) => {
      const x = 0.6 + i * 4.1;
      card(s, x, 3.85, 3.9, 1.65, { fill: { color: C.tint }, line: { color: C.teal, width: 0.75 } });
      T(s, h, x + 0.3, 4.0, 3.3, 0.4, { fontSize: 18, bold: true, color: C.tealD });
      T(s, d, x + 0.3, 4.5, 3.3, 0.95, { fontSize: 13 });
    });
    T(s, "Survey median willingness to pay ≈ US$25 / month. We sell research and alerts, not buy / sell calls (FSC rules).", 0.6, 5.7, 12.1, 0.35, { fontSize: 13, bold: true });
    T(s, "Deployment: one container (Docker on Dokploy) on open TWSE / TPEx / MOPS data; model cost about USD 0.007 per 46 filings.", 0.6, 6.1, 12.1, 0.35, { fontSize: 13, color: C.gray });
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 6.5, w: 5.6, h: 0.34, rectRadius: 0.05, fill: { color: C.amberT }, line: { color: C.amber, width: 0.75 } });
    T(s, "Sources for TAM / SAM: [team to fill]", 0.75, 6.5, 5.4, 0.34, { fontSize: 11, color: C.amber, valign: "middle", bold: true });
  }

  // 17 · Third party + team
  {
    const s = light("Business", "RESOURCES AND TEAM (ART. 13)", "Open sources, tools and who did what",
      "TODO(team): fill the division-of-labour table with real names and roles. Advisers and technical consultants may only guide; they must not do core design, code, evaluation or presentation. Full list of third parties: docs/pengungkapan-pihak-ketiga.md.");
    const rows = [
      [th("Type", { fontSize: 11 }), th("What", { fontSize: 11 }), th("Used for", { fontSize: 11 })],
      ["Market data", "TWSE / TPEx OpenAPI, MOPS", "Filings, prices, shares, profiles"],
      ["Statements", "FinMind", "Quarterly statements (cached 12 h)"],
      ["Model", "Google Gemini 3.6 Flash (backup 3.5 Flash)", "Reads clause text, Ask FEAF; public text only"],
      ["Reference", "Damodaran (ERP 5.01%); Taiwan 10-year bond (1.94%)", "WACC inputs"],
      ["Dev tools", "Claude Code, Antigravity", "Pair programming; not part of the product"],
      ["Libraries", "FastAPI, uvicorn, Jinja2, httpx (MIT / BSD)", "Web app and tests"],
    ].map((r, i) => (i === 0 ? r : r.map((c, j) => td(c, { fontSize: 11, bold: j === 0, fill: { color: i % 2 ? C.white : C.grayT } }))));
    s.addTable(rows, { x: 0.6, y: 1.7, w: 7.3, colW: [1.2, 3.2, 2.9], rowH: [0.4, 0.62, 0.62, 0.72, 0.72, 0.72, 0.62], border, fontFace: FONT, margin: [0.04, 0.09, 0.04, 0.09] });
    T(s, "Only public filings are sent to the model. No personal data, keys or credentials.", 0.6, 6.45, 7.3, 0.4, { fontSize: 11, color: C.gray });
    const ph = (t) => td(t, { fontSize: 11, fill: { color: C.amberT }, color: C.amber, bold: true });
    const roles = [
      [th("Part", { fontSize: 11 }), th("Done by", { fontSize: 11 }), th("AI tools’ role", { fontSize: 11 })],
      [ph("[fill]"), ph("[name]"), ph("[fill]")],
      [ph("[fill]"), ph("[name]"), ph("[fill]")],
      [ph("[fill]"), ph("[name]"), ph("[fill]")],
      [ph("[fill]"), ph("[name]"), ph("[fill]")],
    ];
    T(s, "Team division of labour", 8.25, 1.7, 4.4, 0.3, { fontSize: 14, bold: true });
    s.addTable(roles, { x: 8.25, y: 2.1, w: 4.45, colW: [1.5, 1.3, 1.65], rowH: [0.4, 0.55, 0.55, 0.55, 0.55], border, fontFace: FONT, margin: [0.04, 0.09, 0.04, 0.09] });
    T(s, "Advisers guide only: they do not do core design, code, evaluation or presentation.", 8.25, 4.85, 4.45, 0.7, { fontSize: 11, color: C.gray });
  }

  // 18 · Closing
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Business" });
    T(s, "BACK TO OUR OPENING QUESTION", 0.9, 1.5, 10, 0.3, { fontSize: 13, bold: true, color: C.teal, charSpacing: 4 });
    s.addText("Answers you can ask for. Numbers you can check.", { placeholder: "title" });
    T(s, "AI researches, explains and monitors. The investor decides.", 0.9, 4.1, 11, 0.5, { fontSize: 20, color: C.mute });
    s.addShape(pres.ShapeType.roundRect, { x: 0.9, y: 5.15, w: 6.4, h: 1.0, rectRadius: 0.08, fill: { color: C.navy2 }, line: { color: C.teal, width: 1 } });
    T(s, "Don’t take our word for it.", 1.2, 5.3, 5.9, 0.4, { fontSize: 18, bold: true, color: C.white });
    T(s, "Let’s check it, live.", 1.2, 5.72, 5.9, 0.35, { fontSize: 14, color: C.tealL });
    s.addNotes("Demo plan is on the last backup slide (plan, not yet rehearsed): Alerts (2330, published, all checks passed) -> audit trace -> Ask FEAF (data question, then 'should I buy 2330?' refused) -> Review (one held case). If the connection or model fails, the server falls back to the rule reasoner: say so, and use the saved trace.");
  }

  pres.addSection({ title: "Backup" });

  // 19 · Q: investment advice
  {
    const s = light("Backup", "BACKUP  ·  Q&A", "Is this investment advice?");
    T(s, "No.", 0.6, 1.75, 3, 1.1, { fontSize: 66, bold: true, color: C.tealD });
    T(s, "FEAF shows research, valuation and alerts. The investor decides.", 0.6, 3.0, 5.4, 1.2, { fontSize: 20, bold: true });
    const pts = [
      "Never says buy or sell; no recommendation label on any analysis",
      "Never trades; no broker login, no payment, no email",
      "A disclaimer appears on every stock and valuation page (FSC)",
      "Scope: research and alerts, as the tender asks",
    ].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1, paraSpaceAfter: 10 } }));
    card(s, 6.4, 1.75, 6.3, 3.3);
    T(s, pts, 6.7, 2.0, 5.7, 2.9, { fontSize: 15 });
    card(s, 6.4, 5.3, 6.3, 1.4, { fill: { color: C.navy }, line: { color: C.navy, width: 0.75 } });
    T(s, "27 / 27", 6.7, 5.4, 2.0, 1.2, { fontSize: 30, bold: true, color: C.teal, valign: "middle" });
    T(s, "advice, prediction, personal-data and injected questions refused by Ask FEAF; 0 buy / sell words reached the user", 8.7, 5.4, 3.8, 1.2, { fontSize: 12, color: C.white, valign: "middle" });
  }

  // 20 · Trace
  {
    const s = light("Backup", "BACKUP  ·  Q&A", "A real trace: held, not published",
      "Saved trace: eval/hasil/jejak-contoh-2330-2026-11-10-211853.json, live at /jejak/2330-2026-11-10-211853. TSMC board approval of a capital budget, clause 20. Pulled from TWSE OpenAPI on 11 Nov 02:35 UTC.");
    const rows = [
      [th("Step"), th("What happened")],
      [td("Fetch", { bold: true }), td("TSMC board approval of a capital budget (clause 20), pulled from TWSE OpenAPI; no personal field present")],
      [td("Clause screen", { bold: true }), td("Clause 20 → valuation lane; possible inputs: capex, cash")],
      [td("Triage and extract", { bold: true }), td("gemini-3.6-flash, prompt 2026-11-10.1: 4 amounts found, all in US$, unit million")],
      [td("Confidence", { bold: true }), td("0.55: no amount convertible to NTD")],
      [td("Checker", { bold: true }), td("Currency check failed: USD amount, no exchange rate in the model, not converted silently", { color: C.red, bold: true })],
      [td("End", { bold: true }), td("HELD FOR REVIEW. Nothing published.", { fill: { color: C.amberT }, color: C.amber, bold: true })],
    ];
    s.addTable(rows, { x: 0.6, y: 1.75, w: 12.1, colW: [2.4, 9.7], rowH: [0.45, 0.7, 0.6, 0.7, 0.6, 0.7, 0.6], border, fontFace: FONT, fontSize: 14, margin: [0.05, 0.14, 0.05, 0.14] });
    T(s, "Audit it: /jejak/2330-2026-11-10-211853", 0.6, 6.45, 12.1, 0.35, { fontSize: 12, color: C.gray });
  }

  // 21 · Demo plan
  {
    const s = light("Backup", "BACKUP  ·  DEMO", "Live demo plan and fallback");
    const steps = [
      ["Alerts", "Case 2330: published, all checks passed"],
      ["Audit trace", "Open its trace: steps and the source sentence"],
      ["Ask FEAF", "One data question with sources; then “should I buy 2330?”, refused"],
      ["Review", "One held case; the human decision is recorded"],
    ];
    steps.forEach(([h, d], i) => {
      const y = 1.75 + i * 1.2;
      card(s, 0.6, y, 7.2, 1.05);
      circle(s, String(i + 1), 0.85, y + 0.25, 0.55, C.navy, C.white, 18);
      T(s, h, 1.65, y + 0.12, 5.9, 0.38, { fontSize: 17, bold: true });
      T(s, d, 1.65, y + 0.53, 5.9, 0.45, { fontSize: 13, color: C.gray });
    });
    card(s, 8.1, 1.75, 4.6, 4.65, { fill: { color: C.amberT }, line: { color: C.amber, width: 0.75 } });
    T(s, "If something fails", 8.4, 1.95, 4.0, 0.4, { fontSize: 18, bold: true, color: C.amber });
    const fb = [
      "No model or no connection: the server falls back to the rule reasoner. Say so.",
      "Prepare screenshots of each step before the final.",
      "Saved trace JSON for case 2330 can be shown offline.",
      "Practise at least five times.",
    ].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1, paraSpaceAfter: 10 } }));
    T(s, fb, 8.4, 2.5, 4.0, 3.8, { fontSize: 15 });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
