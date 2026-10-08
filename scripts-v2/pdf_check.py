# -*- coding: utf-8 -*-
import fitz, json
from pathlib import Path
from PIL import Image, ImageDraw

r = Path(__file__).resolve().parents[1]
out = r / "output-v2/pdf/rendered"
out.mkdir(exist_ok=True)
d = fitz.open(r / "output-v2/pdf/KingMotors-v2.pdf")
bad = []
for n, p in enumerate(d):
    pix = p.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
    pix.save(str(out / f"page-{n+1:02d}.png"))
    for b in p.get_text("dict")["blocks"]:
        if b["type"] == 0:
            x0, y0, x1, y1 = b["bbox"]
            if min(x0, y0) < 0 or x1 > p.rect.width + 0.5 or y1 > p.rect.height + 0.5:
                bad.append([n + 1, b["bbox"]])
thumb = Image.new("RGB", (1200, math_h := ((len(d) + 3) // 4) * 240), "#d8dcd7")
draw = ImageDraw.Draw(thumb)
for n in range(len(d)):
    im = Image.open(out / f"page-{n+1:02d}.png")
    im.thumbnail((290, 218))
    x = n % 4 * 300
    y = n // 4 * 240
    thumb.paste(im, (x, y))
    draw.text((x + 8, y + 221), str(n + 1), fill="black")
thumb.save(out / "contact.jpg")
(r / "docs-v2/pdf-checks.json").write_text(
    json.dumps(
        {"pages": len(d), "out_of_page_text_blocks": bad, "rendered_pages": len(d)},
        indent=2,
    ),
    encoding="utf-8",
)
print("PDF pages", len(d), "out-of-page", bad)

assert not bad, bad
