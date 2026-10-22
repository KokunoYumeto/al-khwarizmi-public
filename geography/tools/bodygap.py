"""The word spaces of a printed line, measured on the letter bodies. A column profile underestimates a space when a
letter overhangs its neighbour (the ascender of a ك or the tail of a ر), so here the line is cut into connected
components (letter bodies of at least MINAREA pixels; dots and signs are left out) and, for each two neighbouring
bodies from right to left, the nearest approach is measured: the smallest horizontal distance between their pixels in
the rows they share (or, where they share no row, the column gap). Prints each pair with its column gap and its
nearest approach (px at 400 ppi); with --img, saves the line with the bodies boxed and the approaches marked
(_intake/geography/lines/bg_fNNN_Y0_P.png, P = 1 the right end; --zoom=Z, --parts=N).
python bodygap.py FRAME Y0 Y1 X0 X1 [MINAREA] [--img] [--zoom=1.5] [--parts=3]
python bodygap.py FRAME --box=N [MINAREA] [--img] ...   (the line box N of lines.py, whole width)"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]


def bodies(a, minarea):
    lab, _ = ndimage.label(a, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < minarea:
            continue
        ys, xs = sl
        rows = {}
        for r, c in zip(*np.nonzero(m)):
            y, x = r + ys.start, c + xs.start
            lo, hi = rows.get(y, (x, x))
            rows[y] = (min(lo, x), max(hi, x))
        out.append({"x0": xs.start, "x1": xs.stop - 1, "y0": ys.start, "y1": ys.stop - 1, "rows": rows})
    return sorted(out, key=lambda b: -b["x1"])


def approach(r, l):
    """r: the body on the right, l: the next body to its left"""
    shared = set(r["rows"]) & set(l["rows"])
    if not shared:
        return r["x0"] - l["x1"] - 1, None
    best, at = None, None
    for y in shared:
        d = r["rows"][y][0] - l["rows"][y][1] - 1
        if best is None or d < best:
            best, at = d, y
    return best, at


def main():
    import json
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if "box" in opt:
        k = int(args[0])
        bx = json.loads((ROOT / "_intake" / "geography" / "lines" / f"f{k:03d}_boxes.json").read_text())
        y0, y1, x0, x1 = bx[int(opt["box"]) - 1]
        y0, x0, x1 = y0 - 12, x0 - 5, x1 + 5
        args = args[:1] + [str(v) for v in (y0, y1, x0, x1)] + args[1:]
    k, y0, y1, x0, x1 = map(int, args[:5])
    minarea = int(args[5]) if len(args) > 5 else 150
    im = Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L")
    a = np.asarray(im)[y0:y1, x0:x1] < 110
    bs = bodies(a, minarea)
    res = []
    for r, l in zip(bs, bs[1:]):
        col = r["x0"] - l["x1"] - 1
        near, at = approach(r, l)
        res.append((r, l, col, near, at))
        print(f"{r['x0'] + x0:5d}-{r['x1'] + x0:<5d} | {l['x0'] + x0:5d}-{l['x1'] + x0:<5d}  column gap {col:4d}  "
              f"nearest {near:4d}" + (f" (row {at + y0})" if at is not None else ""))
    if "--img" in sys.argv:
        z = float(opt.get("zoom", 1.5))
        c = im.crop((x0, y0, x1, y1)).convert("RGB")
        c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)
        d = ImageDraw.Draw(c)
        font = ImageFont.load_default(size=16)
        for b in bs:
            d.rectangle([b["x0"] * z, b["y0"] * z, b["x1"] * z, b["y1"] * z], outline=(120, 190, 120))
        for r, l, col, near, at in res:
            if near < 1:
                continue
            yy = at if at is not None else (r["y0"] + r["y1"]) // 2
            xa, xb = l["rows"].get(yy, (l["x1"], l["x1"]))[1], r["rows"].get(yy, (r["x0"], r["x0"]))[0]
            colr = (220, 0, 0) if near >= 15 else (0, 90, 220)
            d.line([(xa * z, yy * z), (xb * z, yy * z)], fill=colr, width=3)
            d.text((xa * z, max(0, yy * z - 30)), str(near), fill=colr, font=font)
        parts = int(opt.get("parts", 3 if c.width > 1500 else 1))
        step = c.width // parts
        for p in range(parts):
            r1 = c.width - p * step
            tag = f"b{int(opt['box']):02d}" if "box" in opt else str(y0)
            c.crop((max(0, r1 - step - 30), 0, r1, c.height)).save(
                ROOT / "_intake" / "geography" / "lines" / f"bg_f{k:03d}_{tag}_{p + 1}.png")


if __name__ == "__main__":
    main()
