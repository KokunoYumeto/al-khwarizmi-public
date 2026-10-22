"""The gap at given places of a printed line: x, read off the reading strips of framekit.py, is first moved to the
column with the least ink within S px of it (the gap itself, where the letters do not overhang); the letters on
either side are then the components of the line (ink below 110, at least 40 px) whose centre lies within W px to the
right, resp. to the left, of that column, and the gap is the smallest distance between the ink of the two sides (px at
400 ppi). Prints each gap with the column used and the two nearest ink points.
python gapat.py FRAME BOX X[:LABEL] [X[:LABEL] ...] [--w=45] [--s=15]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, box = int(args[0]), int(args[1])
    w = int(opt.get("w", 45))
    y0, y1, _, _ = json.loads((ROOT / "_intake" / "geography" / "lines" / f"f{k:03d}_boxes.json").read_text())[box - 1]
    y0 -= 14
    y1 += 6
    g = np.asarray(Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L"))
    band = g[y0:y1] < 110
    colink = band.sum(axis=0)
    s = int(opt.get("s", 15))
    lab, n = ndimage.label(band, structure=np.ones((3, 3)))
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < 40:
            continue
        ys, xs = np.nonzero(m)
        pts = np.c_[ys + sl[0].start, xs + sl[1].start]
        comps.append((pts[:, 1].mean(), sl[1].start, sl[1].stop - 1, pts))
    for spec in args[2:]:
        x, _, label = spec.partition(":")
        x0 = int(x)
        cand = range(x0 - s, x0 + s + 1)
        x = min(cand, key=lambda c: (colink[c], abs(c - x0)))
        right =[c for c in comps if x < c[0] <= x + w or (c[1] > x and c[1] <= x + w)]
        left = [c for c in comps if x - w <= c[0] < x or (c[2] < x and c[2] >= x - w)]
        right = [c for c in right if c[1] >= x - 3]
        left = [c for c in left if c[2] <= x + 3]
        if not right or not left:
            print(f"{label or x}: no letters on both sides of {x}")
            continue
        R = np.vstack([c[3] for c in right])
        L = np.vstack([c[3] for c in left])
        d, idx = cKDTree(L).query(R)
        j = int(np.argmin(d))
        print(f"{(label or str(x0)):24s} at x {x0}->{x}: {d[j] - 1:.0f} px  (right ink x {R[j][1]}, left ink x "
              f"{L[idx[j]][1]})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
