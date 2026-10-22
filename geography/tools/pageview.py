"""Readable views of a frame: the page cut into horizontal bands of about H px (at SCALE), and the names column of the
table rows magnified, each row with its box number. python pageview.py FRAME [--h=760] [--scale=0.6]
[--names=BOX,BOX,...] [--nx=X0-X1] [--nz=1.6] -> _intake/geography/lines/pv_fNNN_K.png, nm_fNNN.png"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "geography" / "lines"
FRAMES = ROOT / "_intake" / "geography" / "frames"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    k = int(args[0])
    h, sc = int(opt.get("h", 760)), float(opt.get("scale", 0.6))
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    W, H = im.size
    x0, x1 = int(W * 0.04), int(W * 0.96)
    y, n = int(H * 0.04), 1
    while y < H * 0.95:
        c = ImageOps.autocontrast(im.crop((x0, y, x1, min(H, y + h))), cutoff=1)
        c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
        c.save(LINES / f"pv_f{k:03d}_{n}.png")
        print(LINES / f"pv_f{k:03d}_{n}.png", c.size, f"y {y}-{min(H, y + h)}")
        y += h - 40
        n += 1
    if "names" in opt:
        bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
        a, b = map(int, opt.get("nx", "1000-2150").split("-"))
        z = float(opt.get("nz", 1.6))
        font = ImageFont.load_default(size=16)
        tiles = []
        for bb in (int(v) for v in opt["names"].split(",")):
            y0, y1 = bx[bb - 1][0] - 30, bx[bb - 1][1] + 6
            c = ImageOps.autocontrast(im.crop((a, y0, b, y1)), cutoff=0.5)
            c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS).convert("RGB")
            t = Image.new("RGB", (c.width, c.height + 20), "white")
            t.paste(c, (0, 20))
            ImageDraw.Draw(t).text((4, 2), f"box {bb}", fill=(200, 0, 0), font=font)
            tiles.append(t)
        Wt = max(t.width for t in tiles)
        Ht = sum(t.height + 4 for t in tiles)
        out = Image.new("RGB", (Wt, Ht), (190, 190, 190))
        yy = 0
        for t in tiles:
            out.paste(t, (0, yy))
            yy += t.height + 4
        out.save(LINES / f"nm_f{k:03d}.png")
        print(LINES / f"nm_f{k:03d}.png", out.size)


if __name__ == "__main__":
    main()
