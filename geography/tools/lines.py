"""Cut a frame of the 1939 edition (400-ppi colour JPEG, _intake/geography/frames/page_NNN.jpg) into its printed lines,
for reading. The printed ink is dark; the pencil marks of a reader of the Columbia copy are light grey and fall below
the threshold. The text block is found from the column profile; the lines are the runs of rows with ink in it, the
dots and vowel signs above and below a line joined to it across small gaps. Prints the line boxes (pixels) and saves
each line, split into a right and a left half at its middle and scaled by ZOOM, as scratch images:
  _intake/geography/lines/fNNN_LL_R.png, fNNN_LL_L.png
python lines.py FRAME [ZOOM] [THRESHOLD]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "_intake" / "geography" / "frames"
OUT = ROOT / "_intake" / "geography" / "lines"


def boxes(a, min_gap=14, min_h=12):
    """the line boxes of a boolean ink array a (rows x columns) of the text block"""
    h, w = a.shape
    rows = a.sum(axis=1)
    ink = rows > max(3, int(0.002 * w))
    runs, y = [], 0
    while y < h:
        if ink[y]:
            y0 = y
            while y < h and ink[y]:
                y += 1
            runs.append([y0, y])
        else:
            y += 1
    merged = []
    for r in runs:                      # join the dots and vowel signs to their line across small gaps
        if merged and r[0] - merged[-1][1] < min_gap and (r[1] - r[0] < 22 or merged[-1][1] - merged[-1][0] < 22):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    hs = sorted(y1 - y0 for y0, y1 in merged if y1 - y0 >= min_h)
    med = hs[len(hs) // 2] if hs else 100
    split = []
    for y0, y1 in merged:                # two lines joined by their signs: cut at the emptiest row of the middle
        n = max(1, round((y1 - y0) / med)) if y1 - y0 > 1.6 * med else 1
        cuts = [y0]
        for j in range(1, n):
            c = y0 + (y1 - y0) * j // n
            lo, hi = c - (y1 - y0) // (3 * n), c + (y1 - y0) // (3 * n)
            cut = lo + int(np.argmin(rows[lo:hi]))
            if rows[cut] < 0.15 * rows[y0:y1].max():   # a real gap between two lines, not a tall heading
                cuts.append(cut)
        cuts.append(y1)
        n = len(cuts) - 1
        split += [[cuts[j], cuts[j + 1]] for j in range(n)]
    out = []
    for y0, y1 in split:
        if y1 - y0 < min_h:
            if out and y0 - out[-1][1] < 40:   # a stray dot or sign close below a line belongs to it
                out[-1][1] = y1
            continue
        cols = np.where(a[y0:y1].any(axis=0))[0]
        out.append([int(y0), int(y1), int(cols.min()), int(cols.max()) + 1])
    return out


def main():
    k = int(sys.argv[1])
    zoom = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    thr = int(sys.argv[3]) if len(sys.argv) > 3 else 110
    im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
    g = np.array(im)
    a = g < thr
    h, w = a.shape
    # the text block: columns and rows with printed ink, away from the page edges and the binding shadow
    m = int(0.06 * w)
    a[:, :m] = False
    a[:, w - m:] = False
    a[:int(0.03 * h)] = False
    a[h - int(0.03 * h):] = False
    bx = boxes(a)
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob(f"f{k:03d}_*.png"):
        f.unlink()
    for i, (y0, y1, x0, x1) in enumerate(bx, 1):
        pad = 10
        crop = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)))
        cw, ch = crop.size
        mid = cw // 2
        for side, part in (("R", crop.crop((mid - 40, 0, cw, ch))), ("L", crop.crop((0, 0, mid + 40, ch)))):
            if zoom != 1.0:
                part = part.resize((int(part.width * zoom), int(part.height * zoom)), Image.LANCZOS)
            part.save(OUT / f"f{k:03d}_{i:02d}_{side}.png")
    (OUT / f"f{k:03d}_boxes.json").write_text(json.dumps(bx), encoding="utf-8")
    for i, b in enumerate(bx, 1):
        print(i, b, "h", b[1] - b[0], "w", b[3] - b[2])


if __name__ == "__main__":
    main()
