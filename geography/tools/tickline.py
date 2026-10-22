"""A printed line enlarged in pieces, with the frame's x coordinate ticked every 10 px and labelled every 50, for
locating letters before measuring them (pairgap.py, clipgap.py).
python tickline.py FRAME BOX [--parts=3] [--zoom=1.6] [--up=40] -> lines/tl_fNNN_BB_P.png (P = 1 the right end)"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "geography" / "lines"


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, b = int(args[0]), int(args[1])
    parts, z, up = int(opt.get("parts", 3)), float(opt.get("zoom", 1.6)), int(opt.get("up", 40))
    bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    im = Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L")
    y0, y1, x0, x1 = bx[b - 1]
    y0, y1, x0, x1 = y0 - up, y1 + 8, x0 - 6, x1 + 6
    font = ImageFont.load_default(size=15)
    step = (x1 - x0) // parts
    for q in range(parts):
        r1 = x1 - q * step
        r0 = max(x0, r1 - step - 30)
        c = ImageOps.autocontrast(im.crop((r0, y0, r1, y1)), cutoff=1).convert("RGB")
        c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)
        t = Image.new("RGB", (c.width, c.height + 26), "white")
        t.paste(c, (0, 0))
        d = ImageDraw.Draw(t)
        for x in range(r0 - r0 % 10 + 10, r1, 10):
            xx = (x - r0) * z
            big = x % 50 == 0
            d.line([(xx, c.height), (xx, c.height + (10 if big else 5))], fill=(200, 0, 0) if big else (0, 0, 200))
            if big:
                d.text((xx - 14, c.height + 10), str(x), fill=(200, 0, 0), font=font)
        t.save(LINES / f"tl_f{k:03d}_{b:02d}_{q + 1}.png")
    print("done")


if __name__ == "__main__":
    main()
