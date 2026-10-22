"""The space before and after the colons and semicolons of a page of Suter's edition (JP2 index).

python marksp.py FRAME [Y0 Y1]

The marks are found as in colons.py. For each mark, the gap between it and the ink to its left and to its right in the
band of the line (rows base-30 to base+2, pixels darker than 150) is printed, with the median word space of the line
(gaps of 15 px or more between ink columns). The edition sets some marks close to the word (2-6 px) and others after
a thin space; a gap well above 6 px and below a word space is a thin space."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = str(Path(__file__).resolve().parents[2])


def baseline(g, x, y0):
    """the last row, within 32 px below the top y0 of the upper dot, of the band around x whose ink is at least 40% of
    the densest row (the next line begins more than 32 px below the upper dot)"""
    xa, xb = max(int(x) - 200, 0), min(int(x) + 200, g.shape[1])
    ya, yb = max(y0 - 40, 0), min(y0 + 32, g.shape[0])
    prof = (g[ya:yb, xa:xb] < 140).sum(axis=1)
    if prof.max() == 0:
        return y1
    rows = np.nonzero(prof >= 0.4 * prof.max())[0]
    return ya + rows.max()


def main():
    fr = int(sys.argv[1])
    g = np.asarray(Image.open(f"{ROOT}/_intake/zij/frames/page_{fr:04d}.jpg").convert("L")).astype(int)
    ylo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    yhi = int(sys.argv[3]) if len(sys.argv) > 3 else g.shape[0]
    lab, n = ndimage.label(g < 150)
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        ys, xs = sl
        w, h = xs.stop - xs.start, ys.stop - ys.start
        if not (5 <= w <= 16 and 5 <= h <= 45 and ylo <= ys.start < yhi):
            continue
        core = (g[sl] < 110) & (lab[sl] == i + 1)
        if core.sum() < 15:
            continue
        cy = np.nonzero(core.any(axis=1))[0]
        comps.append({"x": (xs.start + xs.stop) / 2, "y0": ys.start, "y1": ys.stop, "x0": xs.start, "x1": xs.stop,
                      "h": h, "core_y0": ys.start + int(cy.min())})
    comps.sort(key=lambda c: (c["y0"], c["x"]))
    used = set()
    for a, up in enumerate(comps):
        if a in used or up["h"] > 14 or (up["x1"] - up["x0"]) > 14:
            continue
        for b, lo in enumerate(comps):
            if b in used or b == a:
                continue
            if not (abs(up["x"] - lo["x"]) <= 5 and 2 <= lo["y0"] - up["y1"] <= 22):
                continue
            base = baseline(g, lo["x"], up["y0"])
            dot_bottom = lo["core_y0"] + 8
            if abs(dot_bottom - base) > 6:
                continue
            used.update((a, b))
            ty0, ty1 = lo["core_y0"] + 10, lo["core_y0"] + 28
            tx0, tx1 = int(lo["x0"]) - 8, int(lo["x1"]) + 2
            tail = g[ty0:ty1, max(tx0, 0):tx1]
            mn = int(tail.min()) if tail.size else 255      # a mark at the foot of the image: no room for a tail
            cnt = int((tail < 150).sum())
            if cnt < 6:
                kind = "colon"
            elif mn < 80:
                kind = "semicolon (printed tail)"
            else:
                kind = "colon with a light tail (pencil)"
            y0b, y1b = base - 30, base + 2
            xl = int(min(up["x0"], lo["x0"]))
            xr = int(max(up["x1"], lo["x1"]))
            left = np.nonzero((g[y0b:y1b, max(xl - 150, 0):xl] < 150).any(axis=0))[0]
            before = xl - (max(xl - 150, 0) + int(left.max())) - 1 if len(left) else -1
            right = np.nonzero((g[y0b:y1b, xr:xr + 150] < 150).any(axis=0))[0]
            after = int(right.min()) if len(right) else -1
            ink = np.nonzero((g[y0b:y1b, :] < 150).any(axis=0))[0]
            gaps = [int(q - p - 1) for p, q in zip(ink[:-1], ink[1:]) if q - p - 1 >= 15]
            ws = float(np.median(gaps)) if gaps else 0.0
            print(f"y{up['y0']} x{int(up['x'])}  {kind.split()[0]:9s}  before {before:3d}  after {after:3d}  "
                  f"word space {ws:4.1f}")
            break


if __name__ == "__main__":
    main()
