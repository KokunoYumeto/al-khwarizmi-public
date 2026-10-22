"""An enlarged band of a page of the Hyderabad scan, with its dots measured.

python band.py PDFPAGE Y0 Y1 [X0 X1] [SCALE]

Writes _intake/calendar/bands/pNNN_yY0-Y1.png: the band enlarged (default 3x) with every small component (a dot, or
the two dots of a letter printed as one blob) boxed: blue for a single dot (width 3-7 px), red for a wider blob
(8-13 px, as a rule two dots run together), green for a still wider one. The scan is bitonal at about 170 px to the
inch; on the title page of the collection the single dots measure 5-7 px across and the pairs 9-12 px. Prints the
boxes from right to left."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
args = [int(x) for x in sys.argv[1:4]]
page, y0, y1 = args
rest = sys.argv[4:]
im = Image.open(ROOT / "_intake" / "calendar" / "pages" / f"pdf{page:03d}.png").convert("L")
a = np.asarray(im) < 128
H, W = a.shape
if len(rest) >= 2:
    x0, x1 = int(rest[0]), int(rest[1])
    rest = rest[2:]
else:
    cols = np.nonzero(a[y0:y1, int(W * 0.03):int(W * 0.97)].any(axis=0))[0]
    x0, x1 = max(0, cols.min() + int(W * 0.03) - 10), min(W, cols.max() + int(W * 0.03) + 10)
sc = float(rest[0]) if rest else 3.0
sub = a[y0:y1, x0:x1]
lab, n = ndimage.label(sub)
boxes = []
for s in ndimage.find_objects(lab):
    h = s[0].stop - s[0].start
    w = s[1].stop - s[1].start
    if 3 <= w <= 20 and 3 <= h <= 13 and w * h <= 220:
        boxes.append((s[1].start, s[0].start, w, h))
out = im.crop((x0, y0, x1, y1)).convert("RGB").resize((int((x1 - x0) * sc), int((y1 - y0) * sc)), Image.NEAREST)
d = ImageDraw.Draw(out)
for (x, y, w, h) in boxes:
    col = (0, 0, 255) if w <= 7 else ((255, 0, 0) if w <= 13 else (0, 160, 0))
    d.rectangle((x * sc - 1, y * sc - 1, (x + w) * sc, (y + h) * sc), outline=col, width=2)
dest = ROOT / "_intake" / "calendar" / "bands"
dest.mkdir(parents=True, exist_ok=True)
name = dest / f"p{page:03d}_y{y0}-{y1}.png"
out.save(name)
print(name.name, f"x {x0}-{x1}")
for (x, y, w, h) in sorted(boxes, key=lambda b: -b[0]):
    print(f"  x {x + x0} y {y + y0}  {w}x{h}")
