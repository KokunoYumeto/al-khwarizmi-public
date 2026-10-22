"""Gap census of printed lines: every gap between two neighbouring letter bodies, measured as the smallest distance
between their ink above the baseline (rows above the baseline + 4 px, so that the tails of ر, ز, و and the like,
which reach under the next letter, do not count), in px at 400 ppi. Letter bodies are the components of at least
60 px of ink that reach the baseline (the dots above and below the line are left out; a hamza on the line counts).
The baseline is the row of the line with the most ink. The bodies are taken in reading order, by their right edge.
Each line is drawn enlarged in PARTS pieces, with every gap marked at its place: red at least 16 px, blue less.
python census.py FRAME FIRSTBOX LASTBOX [--zoom=1.5] [--parts=2] [--boxes=FILE] [--print]
  (--print: also list every gap as XLEFT-XRIGHT:WIDTH, right to left)
  -> lines/cs_fNNN_BB_P.png (one image per line and piece; P = 1 the right end)"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "algebra" / "lines"


def gaps(g, y0, y1, x0, x1):
    band = g[y0:y1, x0:x1] < 110
    base = int(np.argmax(band.sum(axis=1)))
    lab, n = ndimage.label(band, structure=np.ones((3, 3)))
    bodies = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < 60 or sl[0].start > base + 4 or sl[0].stop - 1 < base - 8:
            continue
        ys, xs = np.nonzero(m)
        ys, xs = ys + sl[0].start, xs + sl[1].start
        up = ys <= base + 4
        if up.sum() == 0:
            continue
        bodies.append({"x0": int(xs.min()), "x1": int(xs.max()), "pts": np.c_[ys[up], xs[up]]})
    bodies.sort(key=lambda b: -b["x1"])
    out = []
    for r, l in zip(bodies, bodies[1:]):
        d, idx = cKDTree(l["pts"]).query(r["pts"])
        j = int(np.argmin(d))
        pr, pl = r["pts"][j], l["pts"][idx[j]]
        out.append({"gap": float(d[j] - 1), "xr": int(pr[1]) + x0, "xl": int(pl[1]) + x0, "y": int((pr[0] + pl[0]) / 2) + y0})
    return base + y0, out


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, a, b = int(args[0]), int(args[1]), int(args[2])
    z = float(opt.get("zoom", 1.5))
    parts = int(opt.get("parts", 2))
    bx = json.loads((LINES / opt.get("boxes", f"f{k:03d}_boxes.json")).read_text(encoding="utf-8"))
    im = Image.open(ROOT / "_intake" / "algebra" / "frames" / f"page_{k:03d}.jpg").convert("L")
    g = np.asarray(im)
    font = ImageFont.load_default(size=15)
    for n in range(a, b + 1):
        y0, y1, x0, x1 = bx[n - 1]
        y0, y1, x0, x1 = y0 - 16, y1 + 8, x0 - 6, x1 + 6
        base, gs = gaps(g, y0, y1, x0, x1)
        if "print" in sys.argv[1:] or "--print" in sys.argv[1:]:
            print(f"box {n}: " + "  ".join(f"{gp['xl']}-{gp['xr']}:{gp['gap']:.0f}" for gp in gs))
        crop = ImageOps.autocontrast(im.crop((x0, y0, x1, y1)), cutoff=1).convert("RGB")
        crop = crop.resize((int(crop.width * z), int(crop.height * z)), Image.LANCZOS)
        t = Image.new("RGB", (crop.width, crop.height + 40), "white")
        t.paste(crop, (0, 0))
        d = ImageDraw.Draw(t)
        lane = 0
        for gp in gs:
            if gp["gap"] < 0.5:
                continue
            col = (215, 0, 0) if gp["gap"] >= 16 else (0, 90, 220)
            xa, xb = (gp["xl"] - x0) * z, (gp["xr"] - x0) * z
            yy = (gp["y"] - y0) * z
            d.line([(xa, yy), (xb, yy)], fill=col, width=2)
            xm = (xa + xb) / 2
            d.line([(xm, yy), (xm, crop.height + 2 + 18 * lane)], fill=col, width=1)
            d.text((xm - 7, crop.height + 2 + 18 * lane), f"{gp['gap']:.0f}", fill=col, font=font)
            lane = 1 - lane
        step = t.width // parts
        for q in range(parts):
            r1 = t.width - q * step
            t.crop((max(0, r1 - step - 50), 0, r1, t.height)).save(LINES / f"cs_f{k:03d}_{n:02d}_{q + 1}.png")
    print("done")


if __name__ == "__main__":
    main()
