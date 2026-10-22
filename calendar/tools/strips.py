"""Two-line reading strips of a page of the Hyderabad scan, enlarged.

python strips.py PDFPAGE [SCALE] [PER]

Finds the baselines as the peaks of the smoothed horizontal ink profile (at least 70 px apart, at least 8% of the
highest peak), prints them with their line numbers (the running head is line 0 when the page has one), and writes
strips of PER lines (default 2), enlarged by SCALE (default 1.7), to _intake/calendar/strips/pNNN_k.png."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
p = int(sys.argv[1]); sc = float(sys.argv[2]) if len(sys.argv) > 2 else 1.7; per = int(sys.argv[3]) if len(sys.argv) > 3 else 2
im = Image.open(ROOT / "_intake" / "calendar" / "pages" / f"pdf{p:03d}.png").convert("L")
a = np.asarray(im) < 128
H, W = a.shape
a[:, :int(W * 0.03)] = False; a[:, int(W * 0.97):] = False; a[:int(H * 0.01)] = False; a[int(H * 0.99):] = False
sm = np.convolve(a.sum(axis=1).astype(float), np.ones(9) / 9, mode="same")
peaks = []
for y in np.argsort(-sm):
    if sm[y] < 0.08 * sm.max():
        break
    if all(abs(y - q) >= 70 for q in peaks):
        peaks.append(int(y))
peaks.sort()
cols = np.nonzero(a.any(axis=0))[0]
x0, x1 = max(0, cols.min() - 12), min(W, cols.max() + 12)
out = ROOT / "_intake" / "calendar" / "strips"
out.mkdir(parents=True, exist_ok=True)
print("page", p, "baselines", peaks)
for b in range(0, len(peaks), per):
    grp = peaks[b:b + per]
    y0 = max(0, grp[0] - 72); y1 = min(H, grp[-1] + 42)
    c = im.crop((x0, y0, x1, y1))
    c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS).save(out / f"p{p:03d}_{b // per:02d}.png")
    print(f"  strip {b // per:02d}: baselines {grp}")
