"""The numeral cells of the table rows of a frame, magnified, one row under the other: for each line box the longitude
pair and the latitude pair of cells (x-ranges given or found from the rules of the page), with the box number, so that
every letter, dot and mark of the numerals can be read. Also lists, per row and per cell, the ink components (x, y,
size), to check dots and marks. python cellsheet.py FRAME BOX[,BOX...] [--lon=X0-X1] [--lat=X0-X1] [--zoom=3]
[--up=34] -> _intake/geography/lines/cs_fNNN.png"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
LINES = ROOT / "_intake" / "geography" / "lines"
FRAMES = ROOT / "_intake" / "geography" / "frames"


def rules(g, y0, y1):
    """horizontal rules (long thin dark runs) in the rows y0..y1: their x extents"""
    out = []
    for y in range(y0, y1):
        row = g[y] < 120
        x = 0
        n = len(row)
        while x < n:
            if row[x]:
                s = x
                while x < n and row[x]:
                    x += 1
                if x - s >= 150:
                    out.append((s, x - 1))
            x += 1
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    k = int(args[0])
    boxes = [int(b) for b in args[1].split(",")]
    z, up = float(opt.get("zoom", 3)), int(opt.get("up", 34))
    bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    g = np.asarray(im)
    if "lon" in opt and "lat" in opt:
        lon = tuple(map(int, opt["lon"].split("-")))
        lat = tuple(map(int, opt["lat"].split("-")))
    else:
        # the rules of the numeral columns: long thin dark runs anywhere on the page, clustered by their extent
        from collections import Counter
        cnt, ext = Counter(), {}
        H, Wd = g.shape
        for y in range(0, H, 2):
            row = g[y] < 120
            # close gaps of up to 4 px within a rule
            row = np.convolve(row.astype(int), np.ones(5, int), mode="same") > 0
            x = 0
            while x < Wd:
                if row[x]:
                    s0 = x
                    while x < Wd and row[x]:
                        x += 1
                    if 150 <= x - s0 <= 600:
                        key = (s0 // 40, (x - 1) // 40)
                        cnt[key] += 1
                        ext.setdefault(key, []).append((s0, x - 1))
                x += 1
        spans = []
        for key, n in cnt.most_common(8):
            xs = ext[key]
            spans.append((n, min(a for a, _ in xs), max(c for _, c in xs)))
        merged = []
        for n, s0, e0 in sorted(spans, key=lambda t: -t[0]):
            for i, (m, a, c) in enumerate(merged):
                if s0 <= c and e0 >= a:
                    merged[i] = (m + n, min(a, s0), max(c, e0))
                    break
            else:
                merged.append((n, s0, e0))
        merged.sort(key=lambda t: -t[0])
        print("rule spans (count, x0, x1):", merged)
        if len(merged) < 2:
            raise SystemExit("could not find the two column pairs; give --lon and --lat")
        two = sorted(merged[:2], key=lambda t: -t[2])
        lon, lat = (two[0][1], two[0][2]), (two[1][1], two[1][2])
    print("lon", lon, "lat", lat)
    font = ImageFont.load_default(size=16)
    tiles = []
    for b in boxes:
        y0, y1 = bx[b - 1][0] - up, bx[b - 1][1] + 4
        row = []
        for name, (a, c) in (("lat", lat), ("lon", lon)):
            crop = ImageOps.autocontrast(im.crop((a - 6, y0, c + 6, y1)), cutoff=0.3)
            crop = crop.resize((int(crop.width * z), int(crop.height * z)), Image.LANCZOS).convert("RGB")
            row.append(crop)
            sub = g[y0:y1, a - 6:c + 6] < 130
            lab, _ = ndimage.label(sub, structure=np.ones((3, 3)))
            comps = []
            for i, s in enumerate(ndimage.find_objects(lab), 1):
                m = lab[s] == i
                if m.sum() >= 6 and (s[1].stop - s[1].start) < 140:
                    comps.append((s[1].start + a - 6, s[1].stop - 1 + a - 6, s[0].start + y0, s[0].stop - 1 + y0,
                                  int(m.sum())))
            comps.sort(key=lambda t: -t[1])
            print(f"box {b} {name}: " + "  ".join(f"x{c0}-{c1} y{r0}-{r1} ink{n}" for c0, c1, r0, r1, n in comps))
        w = sum(r.width for r in row) + 20
        h = max(r.height for r in row) + 22
        t = Image.new("RGB", (w, h), "white")
        x = 0
        for r in row:
            t.paste(r, (x, 22))
            x += r.width + 20
        ImageDraw.Draw(t).text((4, 2), f"box {b}   (latitude | longitude)", fill=(200, 0, 0), font=font)
        tiles.append(t)
    W = max(t.width for t in tiles)
    H = sum(t.height + 6 for t in tiles)
    out = Image.new("RGB", (W, H), (190, 190, 190))
    y = 0
    for t in tiles:
        out.paste(t, (0, y))
        y += t.height + 6
    path = LINES / f"cs_f{k:03d}.png"
    out.save(path)
    print(path, out.size)


if __name__ == "__main__":
    main()
