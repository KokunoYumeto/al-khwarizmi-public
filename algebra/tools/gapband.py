"""Gap bands: printed lines A..B of a frame, each cut into a right and a left half and stacked (all right halves in one
image, all left halves in another), with every gap between two letter bodies drawn at the gap and labelled with its
width, the nearest approach of the two bodies (bodygap.py). Red: at least 15 px. The line boxes are those of
lines.py (fNNN_boxes.json, or --boxes=FILE in the lines folder); the figures of the page file and --blank rectangles
are painted white first.
python gapband.py FRAME A B [--zoom=1.0] [--parts=2] [--boxes=FILE] [--blank=X0,Y0,X1,Y1[;...]]
  -> lines/gb_fNNN_AA_BB_P.png, P = 1 the right part (with --parts=2 also named R and L)"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bodygap import approach, bodies  # noqa: E402
from readband import blanked  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_intake" / "algebra" / "lines"


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, a, b = int(args[0]), int(args[1]), int(args[2])
    z = float(opt.get("zoom", 1.0))
    extra = [[int(v) for v in r.split(",")] for r in opt["blank"].split(";")] if "blank" in opt else []
    im = blanked(k, extra)
    g = np.asarray(im)
    bx = json.loads((OUT / opt.get("boxes", f"f{k:03d}_boxes.json")).read_text(encoding="utf-8"))
    font = ImageFont.load_default(size=max(12, int(17 * z)))
    big = ImageFont.load_default(size=22)
    halves = {}
    for n in range(a, b + 1):
        y0, y1, x0, x1 = bx[n - 1]
        y0, y1, x0, x1 = y0 - 12, y1 + 4, x0 - 6, x1 + 6
        arr = g[y0:y1, x0:x1] < 110
        bs = bodies(arr, 150)
        top = 4
        line = Image.fromarray(g[y0:y1, x0:x1]).convert("RGB")
        line = line.resize((int(line.width * z), int(line.height * z)), Image.LANCZOS)
        canvas = Image.new("RGB", (line.width, line.height + top + 22), "white")
        canvas.paste(line, (0, top))
        d = ImageDraw.Draw(canvas)
        for bb in bs:
            d.rectangle([bb["x0"] * z, bb["y0"] * z + top, (bb["x1"] + 1) * z, (bb["y1"] + 1) * z + top],
                        outline=(150, 205, 150))
        for r, l in zip(bs, bs[1:]):
            near, at = approach(r, l)
            yy = at if at is not None else (r["y0"] + r["y1"]) // 2
            xa = (l["rows"][yy][1] if yy in l["rows"] else l["x1"]) + 1
            xb = r["rows"][yy][0] if yy in r["rows"] else r["x0"]
            col = (215, 0, 0) if near >= 15 else (0, 90, 220)
            if near >= 1:
                d.line([(xa * z, yy * z + top), (xb * z, yy * z + top)], fill=col, width=3)
            d.text(((xa + xb) / 2 * z - 7, line.height + top + 2), str(near), fill=col, font=font)
            d.line([((xa + xb) / 2 * z, yy * z + top), ((xa + xb) / 2 * z, line.height + top)], fill=col, width=1)
        parts = int(opt.get("parts", 2))
        step = canvas.width // parts
        cuts = []
        for q in range(parts):
            r1 = canvas.width - q * step
            cuts.append((str(q + 1), canvas.crop((max(0, r1 - step - 40), 0, r1, canvas.height))))
        for side, part in cuts:
            tile = Image.new("RGB", (part.width + 46, part.height), "white")
            tile.paste(part, (46, 0))
            ImageDraw.Draw(tile).text((4, part.height // 2 - 11), str(n), fill=(0, 0, 0), font=big)
            halves.setdefault(side, []).append(tile)
    for side, tiles in halves.items():
        W = max(t.width for t in tiles)
        H = sum(t.height + 6 for t in tiles)
        out = Image.new("RGB", (W, H), (190, 190, 190))
        y = 0
        for t in tiles:
            out.paste(t, (W - t.width, y))
            y += t.height + 6
        name = {"1": "R", "2": "L"}[side] if int(opt.get("parts", 2)) == 2 else side
        out.save(OUT / f"gb_f{k:03d}_{a:02d}_{b:02d}_{name}.png")
        print(f"gb_f{k:03d}_{a:02d}_{b:02d}_{name}.png", out.size)


if __name__ == "__main__":
    main()
