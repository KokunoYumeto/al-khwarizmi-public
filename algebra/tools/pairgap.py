"""Every component of a window of a printed line (ink below 110, at least MIN px) with its box, and the nearest
approach between every two of them that come within 45 px of each other (px at 400 ppi), so that a doubtful gap can be
read between the two letters it actually separates (the census pairs neighbouring bodies only, and the hamza on the
line, split letters and the strokes of the tanwīn can make it pair the wrong ones).
python pairgap.py FRAME BOX X0-X1 [X0-X1 ...] [--min=20] [--up=30] [--img=OUT.png] [--clip]
  (--img: the windows enlarged, stacked, each component boxed with its number;
   --clip: the gaps also measured on the ink above the baseline + 4 px only, as census.py measures them, so that
   the tails of ر, ز and و, which reach under the next letter, do not count; printed as «clipped»)"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, b = int(args[0]), int(args[1])
    mn, up = int(opt.get("min", 20)), int(opt.get("up", 30))
    bx = json.loads((ROOT / "_intake" / "algebra" / "lines" / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    im = Image.open(ROOT / "_intake" / "algebra" / "frames" / f"page_{k:03d}.jpg").convert("L")
    g = np.asarray(im)
    y0, y1 = bx[b - 1][0] - up, bx[b - 1][1] + 5
    by0, by1, bx0, bx1 = bx[b - 1]
    base = by0 + int(np.argmax((g[by0:by1, bx0:bx1] < 110).sum(axis=1)))      # the row of the line with the most ink
    clip = "--clip" in sys.argv[1:]
    tiles, z, font = [], 3, ImageFont.load_default(size=15)
    for w in args[2:]:
        x0, x1 = (int(v) for v in w.split("-"))
        lab, _ = ndimage.label(g[y0:y1, x0:x1] < 110, structure=np.ones((3, 3)))
        cs = []
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            m = lab[sl] == i
            if m.sum() < mn:
                continue
            ys, xs = np.nonzero(m)
            pts = np.c_[ys + sl[0].start + y0, xs + sl[1].start + x0]
            cs.append((int(pts[:, 1].min()), int(pts[:, 1].max()), int(pts[:, 0].min()), int(pts[:, 0].max()),
                       int(m.sum()), pts))
        cs.sort(key=lambda c: -c[1])
        print(f"box {b} x {x0}-{x1}")
        for n, c in enumerate(cs):
            print(f"  [{n}] x{c[0]}-{c[1]} y{c[2]}-{c[3]} ink{c[4]}")
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                d, _ = cKDTree(cs[j][5]).query(cs[i][5])
                if d.min() - 1 <= 45:
                    extra = ""
                    if clip:
                        pi, pj = cs[i][5][cs[i][5][:, 0] <= base + 4], cs[j][5][cs[j][5][:, 0] <= base + 4]
                        if len(pi) and len(pj):
                            dc, _ = cKDTree(pj).query(pi)
                            extra = f"   clipped {dc.min() - 1:.0f}"
                        else:
                            extra = "   clipped -"
                    print(f"     [{i}]-[{j}] {d.min() - 1:.0f}{extra}")
        if "img" in opt:
            t = ImageOps.autocontrast(im.crop((x0, y0, x1, y1)), cutoff=1).convert("RGB")
            t = t.resize((t.width * z, t.height * z), Image.LANCZOS)
            d = ImageDraw.Draw(t)
            for n, c in enumerate(cs):
                d.rectangle([(c[0] - x0) * z, (c[2] - y0) * z, (c[1] - x0 + 1) * z, (c[3] - y0 + 1) * z],
                            outline=(0, 160, 0))
                d.text(((c[0] - x0) * z + 2, (c[2] - y0) * z - 15), str(n), fill=(200, 0, 0), font=font)
            tiles.append(t)
    if tiles:
        o = Image.new("RGB", (max(t.width for t in tiles), sum(t.height + 8 for t in tiles)), "white")
        y = 0
        for t in tiles:
            o.paste(t, (0, y))
            y += t.height + 8
        o.save(ROOT / "_intake" / "algebra" / "lines" / opt["img"])


if __name__ == "__main__":
    main()
