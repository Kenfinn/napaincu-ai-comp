import io, os, sys

HELMET = io.open("style_bersama.txt", encoding="utf-8").read().strip()

WRAP = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
{helmet}

{body}
</x-dc>
</body>
</html>
"""

def legend(items, cols=2):
    """Pita catatan di bawah tiap wireframe. Isinya alasan, bukan label."""
    cells = []
    for n, t in items:
        cells.append(
            f'<div style="display: flex; gap: 8px; align-items: baseline;">'
            f'<span class="legn">{n}</span><span class="leg">{t}</span></div>')
    return ('<div style="border-top: 1px solid #C9CDD2; background: #FAFBFB; padding: 16px 26px; '
            f'display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 9px 30px;">'
            + "".join(cells) + '</div>')

def marker(n):
    return f'<div class="cal">{n}</div>'

def write(name, w, h, inner):
    body = (f'<div style="width: {w}px; height: {h}px; display: flex; flex-direction: column; '
            f'background: #FFFFFF; color: #2B313A;">' + inner + '</div>')
    src = WRAP.format(helmet=HELMET, body=body)
    io.open(f"{name}.dc.html", "w", encoding="utf-8").write(src)
    print(f"{name}.dc.html  {w}x{h}")
