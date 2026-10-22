"""Colons and semicolons of a page of Suter's edition of the Zij (JP2 index), told apart by the tail below the lower dot.

python colons.py FRAME [Y0 Y1]

Components are taken at the threshold 150, so that the parts of a letter (the head and the bowl of an a, the dot and
the stem of an i) hang together and only free-standing marks remain small. The upper dot is a component 5-14 px wide
and high; the lower component, 5-16 px wide and 5-45 px high (a pencil tail can lengthen it), stands 2-22 px below it within 5 px horizontally and its
dot ends within 6 px of the base line of the line: a dot on the base line, or a dot with the tail of a semicolon (or a
pencil tail). The tail of a printed semicolon is nearly as dark as the dots (its darkest pixel below 80, mostly 20-66);
a reader of the Munich copy has added tails in pencil to some colons, which are lighter (darkest pixel 85 or more).
For each pair the position, the base line, the height of the lower component and the darkest pixel and the number of
pixels darker than 150 in the area below the lower dot are printed, with the reading. A pencil tail can join the two
dots into one component or close the gap between them; such colons are not found and are read on the scan (compare
the count of the colons and semicolons found with the page file)."""
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
            print(f"y{up['y0']}-{lo['y1']} x{int(up['x'])}  base {base}  lower h {lo['h']}  below: darkest {mn}, "
                  f"{cnt} px  -> {kind}")
            break


if __name__ == "__main__":
    main()
