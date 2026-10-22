"""The gaps of a printed line of the Hyderabad scan (file 60, native image of a PDF page), right to left.

python gaps.py PDFPAGE BASELINE [MIN]   (MIN: the smallest gap to list, in px, default 6)

The line band runs from 62 px above to 38 px below the baseline. Every column with ink in the band counts, dots and
marks included, so a gap is the white run between two ink columns. The gaps are listed from the right (where the line
begins) with their x position and width; a copy of the band with the gaps marked (red for the gaps of MIN px and more,
numbered) is written to _intake/calendar/gaps/pNNN_yYYYY.png for reading. The scan is bitonal, about 170 px to the
inch across the line: a word space of the print is about 12 to 30 px, the white between letters that do not join
inside a word about 2 to 10 px."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
page, base = int(sys.argv[1]), int(sys.argv[2])
mn = int(sys.argv[3]) if len(sys.argv) > 3 else 6
im = Image.open(ROOT / "_intake" / "calendar" / "pages" / f"pdf{page:03d}.png").convert("L")
a = np.asarray(im) < 128
H, W = a.shape
y0, y1 = max(0, base - 62), min(H, base + 38)
band = a[y0:y1, int(W * 0.03):int(W * 0.97)]
off = int(W * 0.03)
cols = band.any(axis=0)
xs = np.nonzero(cols)[0]
left, right = xs.min(), xs.max()
gaps = []
x = right
while x > left:
    if not cols[x]:
        e = x
        while x > left and not cols[x]:
            x -= 1
        gaps.append((x + 1 + off, e - x))           # start (left end) of the white run, width
    x -= 1
out = Image.fromarray(np.where(band, 0, 255).astype(np.uint8)).convert("RGB")
d = ImageDraw.Draw(out)
k = 0
print(f"page {page}, baseline {base}: ink x {left + off}-{right + off}")
for gx, w in gaps:
    if w >= mn:
        k += 1
        d.rectangle((gx - off, 0, gx - off + w - 1, band.shape[0] - 1), outline=(255, 0, 0))
        d.text((gx - off + 1, 1), str(k), fill=(255, 0, 0))
        print(f"  {k:2d}: x {gx}, {w} px")
dest = ROOT / "_intake" / "calendar" / "gaps"
dest.mkdir(parents=True, exist_ok=True)
out.save(dest / f"p{page:03d}_y{base:04d}.png")
