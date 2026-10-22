"""The spacing at the punctuation of every line of a page of the arithmetic.

python spacing.py FRAME [X0 X1]

For each band of the text block it prints the median word space (the median of the gaps of 9-40 px) and each
punctuation mark (an ink run at most 13 px wide whose ink is at most 28 px high: a point, a comma, a colon or a
semicolon) with the gap before it and after it, as gap_before[x]gap_after; a gap of more than 40 px (the end of the
line, the margin) is shown as «end».

Superseded by punct.py, which finds the marks by their form; the rule used in the page files is stated there."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = str(Path(__file__).resolve().parents[2])


def runs(ink):
    xs = np.nonzero(ink)[0]
    out = []
    if not len(xs):
        return out
    s = p = xs[0]
    for x in xs[1:]:
        if x - p - 1 >= 3:
            out.append((s, p))
            s = x
        p = x
    out.append((s, p))
    return out


def main():
    fr = int(sys.argv[1])
    a = np.asarray(Image.open(f"{ROOT}/_intake/arithmetic/frames/page_{fr:03d}.jpg").convert("L")).astype(int)
    cols = np.nonzero((a[200:2400, :] < 140).sum(axis=0) > 25)[0]
    x0 = int(sys.argv[2]) if len(sys.argv) > 2 else max(cols.min() - 10, 0)
    x1 = int(sys.argv[3]) if len(sys.argv) > 3 else cols.max() + 10
    prof = (a[:, x0:x1] < 140).sum(axis=1)
    y, k = 0, 0
    while y < len(prof):
        if prof[y] > 6:
            s = y
            while y < len(prof) and prof[y] > 6:
                y += 1
            if y - s >= 25:
                k += 1
                band = a[s:y, x0:x1] < 150
                rr = runs(band.sum(axis=0) > 0)
                gaps = [rr[i + 1][0] - rr[i][1] - 1 for i in range(len(rr) - 1)]
                ws = [g for g in gaps if 9 <= g <= 40]
                med = float(np.median(ws)) if ws else 0.0
                marks = []
                for i, (u, v) in enumerate(rr):
                    rows = np.nonzero(band[:, u:v + 1].sum(axis=1))[0]
                    h = rows.max() - rows.min() + 1
                    if v - u + 1 <= 13 and h <= 28:
                        gb = gaps[i - 1] if i > 0 else None
                        ga = gaps[i] if i < len(gaps) else None
                        fb = "end" if gb is None or gb > 40 else str(gb)
                        fa = "end" if ga is None or ga > 40 else str(ga)
                        marks.append(f"{fb}[{x0 + u}]{fa}")
                print(f"band {k:2d} y{s}-{y} median {med:4.1f}  {'  '.join(marks)}")
        y += 1


if __name__ == "__main__":
    main()
