"""Magnified names of table rows, each with an x ruler, and the list of their ink components (x range, height relative
to the baseline, ink), to check dots and marks. python namezoom.py FRAME OUT.png BOX:X0-X1[:LABEL] [...] [--z=3]
[--up=30] [--thr=150]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "geography" / "lines"
FRAMES = ROOT / "_intake" / "geography" / "frames"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    k, out = int(args[0]), args[1]
    z, up, thr = float(opt.get("z", 3)), int(opt.get("up", 30)), int(opt.get("thr", 150))
    bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    g = np.asarray(im)
    font = ImageFont.load_default(size=15)
    tiles = []
    for spec in args[2:]:
        parts = spec.split(":")
        b = int(parts[0])
        x0, x1 = map(int, parts[1].split("-"))
        lab = parts[2] if len(parts) > 2 else f"box {b}"
        y0, y1 = bx[b - 1][0] - up, bx[b - 1][1] + 8
        band = g[y0:y1, x0:x1] < 120
        base = y0 + int(np.argmax(band.sum(axis=1)))
        lab_, _ = ndimage.label(g[y0:y1, x0:x1] < thr, structure=np.ones((3, 3)))
        comps = []
        for i, s in enumerate(ndimage.find_objects(lab_), 1):
            m = lab_[s] == i
            if m.sum() >= 5:
                comps.append((s[1].start + x0, s[1].stop - 1 + x0, s[0].start + y0 - base, s[0].stop - 1 + y0 - base,
                              int(m.sum())))
        comps.sort(key=lambda t: -t[1])
        print(f"{lab} (box {b}, baseline y{base}): " + "  ".join(f"x{a}-{c} {r0:+d}..{r1:+d} ink{n}"
                                                             for a, c, r0, r1, n in comps))
        c = im.crop((x0, y0, x1, y1))
        c = c.resize((int(c.width * z), int(c.height * z)), Image.BICUBIC).convert("RGB")
        t = Image.new("RGB", (c.width, c.height + 40), "white")
        t.paste(c, (0, 20))
        d = ImageDraw.Draw(t)
        d.text((3, 1), lab, fill=(200, 0, 0), font=font)
        for x in range((x0 // 10 + 1) * 10, x1, 10):
            px = (x - x0) * z
            d.line([(px, c.height + 20), (px, c.height + (30 if x % 50 == 0 else 25))], fill=(0, 0, 170))
            if x % 50 == 0:
                d.text((px + 2, c.height + 24), str(x), fill=(0, 0, 170), font=font)
        tiles.append(t)
    W = max(t.width for t in tiles)
    H = sum(t.height + 6 for t in tiles)
    o = Image.new("RGB", (W, H), (190, 190, 190))
    y = 0
    for t in tiles:
        o.paste(t, (0, y))
        y += t.height + 6
    o.save(out)
    print(out, o.size)


if __name__ == "__main__":
    main()
