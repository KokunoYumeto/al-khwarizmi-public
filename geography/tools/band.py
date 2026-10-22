"""Render printed lines A..B of a frame (boxes from lines.py) as one image for reading, at ZOOM, each line labelled.
python band.py FRAME A B [ZOOM] -> _intake/geography/lines/band_fNNN_A_B.png"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "_intake" / "geography" / "frames"
OUT = ROOT / "_intake" / "geography" / "lines"


def main():
    k, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    zoom = float(sys.argv[4]) if len(sys.argv) > 4 else 0.85
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    bx = json.loads((OUT / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    sel = bx[a - 1:b]
    x0 = min(r[2] for r in sel) - 20
    x1 = max(r[3] for r in sel) + 20
    parts = []
    for i, (y0, y1, _, _) in enumerate(sel, a):
        crop = im.crop((x0, y0 - 8, x1, y1 + 8))
        crop = crop.resize((int(crop.width * zoom), int(crop.height * zoom)), Image.LANCZOS)
        lab = Image.new("L", (crop.width + 60, crop.height), 255)
        lab.paste(crop, (60, 0))
        ImageDraw.Draw(lab).text((6, crop.height // 2 - 6), f"{i:02d}", fill=0)
        parts.append(lab)
    W = max(p.width for p in parts)
    H = sum(p.height for p in parts) + 6 * len(parts)
    out = Image.new("L", (W, H), 160)
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.height + 6
    path = OUT / f"band_f{k:03d}_{a:02d}_{b:02d}.png"
    out.save(path)
    print(path, out.size)


if __name__ == "__main__":
    main()
