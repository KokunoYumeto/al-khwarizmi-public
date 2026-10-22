"""Several places of a frame's lines, each enlarged with the gap between every two neighbouring components written at
the gap: the smallest distance between their inked pixels (px at 400 ppi; red at least 15). Components of at least
40 px of ink are boxed; the gaps are measured between the letter bodies and hamzas (at least 95 px of ink; the dots
are left out of the chain), neighbours in x order. One image, the places stacked, each captioned. A place given as
BOX alone is the whole line, cut into --parts pieces.
python gapzoom.py FRAME OUT.png BOX[:X0-X1[:LABEL]] [...] [--zoom=2.0] [--parts=3]   (boxes of fNNN_boxes.json)"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "geography" / "lines"


def tile(g, y0, y1, x0, x1, z, caption, font, small):
    band = g[y0:y1, x0:x1] < 110
    lab, n = ndimage.label(band, structure=np.ones((3, 3)))
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < 40:
            continue
        ys, xs = np.nonzero(m)
        comps.append((sl[1].start, sl[1].stop - 1, sl[0].start, sl[0].stop - 1, np.c_[ys + sl[0].start, xs + sl[1].start]))
    comps.sort(key=lambda c: -(c[0] + c[1]))
    top = 24
    img = Image.fromarray(g[y0:y1, x0:x1]).convert("RGB")
    img = img.resize((int(img.width * z), int(img.height * z)), Image.LANCZOS)
    t = Image.new("RGB", (img.width, img.height + top + 4), "white")
    t.paste(img, (0, top))
    d = ImageDraw.Draw(t)
    d.text((4, 2), caption, fill=(0, 0, 0), font=font)
    for c in comps:
        d.rectangle([c[0] * z, c[2] * z + top, (c[1] + 1) * z, (c[3] + 1) * z + top], outline=(140, 200, 140))
    chain = [c for c in comps if len(c[4]) >= 95]
    for a, b in zip(chain, chain[1:]):
        dist, idx = cKDTree(b[4]).query(a[4])
        j = int(np.argmin(dist))
        pa, pb = a[4][j], b[4][idx[j]]
        v = dist[j] - 1
        if v < 0.5:
            continue
        col = (215, 0, 0) if v >= 15 else (0, 90, 220)
        d.line([(pa[1] * z, pa[0] * z + top), (pb[1] * z, pb[0] * z + top)], fill=col, width=2)
        d.text(((pa[1] + pb[1]) / 2 * z - 6, (pa[0] + pb[0]) / 2 * z + top + 3), f"{v:.0f}", fill=col, font=small)
    return t


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, out = int(args[0]), args[1]
    z = float(opt.get("zoom", 2.0))
    bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    g = np.asarray(Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L"))
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=16)
    tiles = []
    np_ = int(opt.get("parts", 3))
    for spec in args[2:]:
        parts = spec.split(":")
        box = int(parts[0])
        y0, y1, bx0, bx1 = bx[box - 1]
        if len(parts) > 1:
            ranges = [tuple(int(v) for v in parts[1].split("-"))]
        else:
            step = (bx1 - bx0) // np_ + 1
            ranges = [(max(bx0 - 6, bx1 + 6 - (q + 1) * step - 40), bx1 + 6 - q * step) for q in range(np_)]
        label = parts[2] if len(parts) > 2 else ""
        for x0, x1 in ranges:
            tiles.append(tile(g, y0 - 16, y1 + 8, x0, x1, z, f"box {box}  x {x0}-{x1}  {label}", font, small))
    W = max(t.width for t in tiles)
    H = sum(t.height + 6 for t in tiles)
    o = Image.new("RGB", (W, H), (170, 170, 170))
    y = 0
    for t in tiles:
        o.paste(t, (0, y))
        y += t.height + 6
    o.save(LINES / out)
    print(out, o.size)


if __name__ == "__main__":
    main()
