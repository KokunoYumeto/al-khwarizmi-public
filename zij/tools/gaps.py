"""The gaps between the ink columns of one line of a page, to tell a word space from the spacing of letters.

python gaps.py FRAME Y0 Y1 [X0 X1] [MIN]   prints each gap of MIN px or more (default 6) with its x position and width,
                                           and the run of ink before it (its x range), from left to right

A gap is a run of columns without ink (no pixel darker than 150 between Y0 and Y1); punctuation is ink, so the gap after
a comma or a full stop is measured from the punctuation mark."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = str(Path(__file__).resolve().parents[2])


def main():
    fr, y0, y1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    a = np.asarray(Image.open(f"{ROOT}/_intake/zij/frames/page_{fr:04d}.jpg").convert("L")).astype(int)
    x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    x1 = int(sys.argv[5]) if len(sys.argv) > 5 else a.shape[1]
    mn = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    ink = (a[y0:y1, x0:x1] < 150).sum(axis=0) > 0
    xs = np.nonzero(ink)[0]
    if not len(xs):
        print("no ink")
        return
    start = xs[0]
    prev = xs[0]
    for x in xs[1:]:
        if x - prev - 1 >= mn:
            print(f"ink {x0 + start}-{x0 + prev}  gap {x - prev - 1} px")
            start = x
        prev = x
    print(f"ink {x0 + start}-{x0 + prev}")


if __name__ == "__main__":
    main()
