"""Reading bands with the word gaps measured: printed lines A..B of a frame, one under the other at ZOOM, each with
its box number in the margin, and above every gap between two letter bodies of at least MIN px its width, the
nearest approach of the two bodies (bodygap.py), which is not deceived by a letter that overhangs its neighbour (the
tail of a ر, the foot of a د). Red: at least 15 px. The figures of the page file (@fig) and any rectangle given with
--blank are painted white first, so that the lines beside a figure are cut and measured without it. The boxes are
those of lines.py on the blanked frame, saved as fNNN_rboxes.json.
python readband.py FRAME A B [--zoom=0.9] [--min=8] [--blank=X0,Y0,X1,Y1[;X0,Y0,X1,Y1...]] -> lines/rb_fNNN_AA_BB.png"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bodygap import approach, bodies  # noqa: E402
from lines import boxes as line_boxes  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "_intake" / "geography" / "frames"
PAGES = ROOT / "geography" / "pages"
OUT = ROOT / "_intake" / "geography" / "lines"


def blanked(k, extra):
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    d = ImageDraw.Draw(im)
    rects = list(extra)
    pf = PAGES / f"AK05-F{k:03d}.txt"
    if pf.exists():
        for ln in pf.read_text(encoding="utf-8").splitlines():
            if ln.startswith("@fig "):
                rects.append([int(v) for v in ln.split()[2:6]])
    for x0, y0, x1, y1 in rects:
        d.rectangle([x0, y0, x1, y1], fill=255)
    return im


def frame_boxes(im):
    a = np.asarray(im) < 110
    h, w = a.shape
    m = int(0.06 * w)
    a[:, :m] = False
    a[:, w - m:] = False
    a[:int(0.03 * h)] = False
    a[h - int(0.03 * h):] = False
    return line_boxes(a)


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, a, b = int(args[0]), int(args[1]), int(args[2])
    zoom = float(opt.get("zoom", 0.9))
    gmin = int(opt.get("min", 8))
    extra = [[int(v) for v in r.split(",")] for r in opt["blank"].split(";")] if "blank" in opt else []
    im = blanked(k, extra)
    bx = frame_boxes(im)
    (OUT / f"f{k:03d}_rboxes.json").write_text(json.dumps(bx), encoding="utf-8")
    g = np.asarray(im)
    font = ImageFont.load_default(size=max(11, int(15 * zoom)))
    big = ImageFont.load_default(size=22)
    x0s = min(bb[2] for bb in bx[a - 1:b]) - 10
    x1s = max(bb[3] for bb in bx[a - 1:b]) + 10
    parts = []
    for n in range(a, b + 1):
        y0, y1, _, _ = bx[n - 1]
        y0 -= 12
        y1 += 4
        arr = g[y0:y1, x0s:x1s] < 110
        bs = bodies(arr, 150)
        top = 22
        crop = Image.fromarray(g[y0:y1, x0s:x1s]).convert("RGB")
        crop = crop.resize((int(crop.width * zoom), int(crop.height * zoom)), Image.LANCZOS)
        tile = Image.new("RGB", (crop.width + 50, crop.height + top), "white")
        tile.paste(crop, (50, top))
        d = ImageDraw.Draw(tile)
        d.text((4, top + crop.height // 2 - 11), f"{n}", fill=(0, 0, 0), font=big)
        for r, l in zip(bs, bs[1:]):
            near, at = approach(r, l)
            if near < gmin:
                continue
            xa = (l["rows"][at][1] if at is not None else l["x1"]) + 1
            xb = r["rows"][at][0] if at is not None else r["x0"]
            xm = 50 + (xa + xb) / 2 * zoom
            col = (215, 0, 0) if near >= 15 else (0, 90, 220)
            d.line([(xa * zoom + 50, top - 3), (xb * zoom + 50, top - 3)], fill=col, width=2)
            d.text((xm - 8, 2), str(near), fill=col, font=font)
        parts.append(tile)
    W = max(p.width for p in parts)
    H = sum(p.height + 8 for p in parts)
    out = Image.new("RGB", (W, H), (200, 200, 200))
    y = 0
    for p in parts:
        out.paste(p, (W - p.width, y))
        y += p.height + 8
    path = OUT / f"rb_f{k:03d}_{a:02d}_{b:02d}.png"
    out.save(path)
    print(path.name, out.size, f"{len(bx)} boxes")


if __name__ == "__main__":
    main()
