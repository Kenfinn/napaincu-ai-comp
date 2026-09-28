"""
Bikin satu berkas SVG berisi seluruh artboard, tersusun sesuai design/canvas.json.

    python3 scripts/build_figma_svg.py            # folder design/
    python3 scripts/build_figma_svg.py wireframe  # folder wireframe/

Hasilnya design/export/Sentinel-Saham-figma.svg — sekali seret ke Figma, seluruh
papan langsung terbentuk beserta judul tiap layar.

Jalankan `node scripts/render_design.js` dulu supaya PNG-nya ada dan terbaru.

Catatan: SVG itu XML ketat. Judul artboard harus di-escape — ada satu judul
memakai "&" ("Watchlist & Profil Risiko") dan tanpa escape parser berhenti di
situ, menyisakan sebagian artboard hilang tanpa pesan error apa pun.
"""
import base64
import io
import json
import os
import re
import sys
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Argumen pertama memilih folder: "design" (hi-fi) atau "wireframe" (lo-fi).
DIRNAME = sys.argv[1] if len(sys.argv) > 1 else "design"
DESIGN = os.path.join(ROOT, DIRNAME)
EXPORT = os.path.join(DESIGN, "export")
OUT = os.path.join(EXPORT, f"Sentinel-Saham-{'wireframe' if DIRNAME == 'wireframe' else 'figma'}.svg")

PAD = 120       # margin sekeliling papan
TITLE_H = 46    # ruang untuk judul di atas tiap artboard


def slug(s):
    """id yang aman dipakai XML — jadi nama layer di Figma."""
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s.replace("·", "-")).strip("-")


def main():
    with io.open(os.path.join(DESIGN, "canvas.json"), encoding="utf-8") as fh:
        boards = json.load(fh)["artboards"]

    width = max(b["x"] + b["w"] for b in boards) + PAD * 2
    height = max(b["y"] + b["h"] for b in boards) + PAD * 2 + TITLE_H

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#F6F7F8"/>',
    ]

    for b in boards:
        png = os.path.join(EXPORT, b["file"].replace(".dc.html", ".png"))
        if not os.path.exists(png):
            raise SystemExit(f"{png} belum ada — jalankan `node scripts/render_design.js {DIRNAME}` dulu")
        with io.open(png, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")

        x = b["x"] + PAD
        y = b["y"] + PAD + TITLE_H
        parts += [
            f'<g id="{slug(b["title"])}">',
            f'<text x="{x}" y="{y - 16}" font-family="Instrument Sans, sans-serif" '
            f'font-size="26" font-weight="600" fill="#101418">{escape(b["title"])}</text>',
            f'<rect x="{x}" y="{y}" width="{b["w"]}" height="{b["h"]}" fill="#FFFFFF"/>',
            f'<image x="{x}" y="{y}" width="{b["w"]}" height="{b["h"]}" '
            f'preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{b64}"/>',
            "</g>",
        ]

    parts.append("</svg>")
    with io.open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))

    print(f"{OUT}  {width}x{height}  {os.path.getsize(OUT) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
