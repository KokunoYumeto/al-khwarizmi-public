"""Line bands of a page of the arithmetic (Latin, left to right) and crops of them for reading.

python lines.py FRAME                      list the bands of ink rows with their x extents
python lines.py FRAME OUT K1-K2 [SCALE]    write OUT.png, the bands K1..K2 each cut in two halves, enlarged

A band is a run of rows whose ink (pixels darker than 140, in the column range of the text block) exceeds a threshold;
small marks above or below a line can form bands of their own and are listed with their height."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = str(Path(__file__).resolve().parents[2])


def bands(a, x0, x1, thr=6, minh=5):
    prof = (a[:, x0:x1] < 140).sum(axis=1)
    out, y = [], 0
    while y < len(prof):
        if prof[y] > thr:
            s = y
            while y < len(prof) and prof[y] > thr:
                y += 1
            if y - s >= minh:
                out.append((s, y))
        y += 1
    return out


def main():
    fr = int(sys.argv[1])
    im = Image.open(f"{ROOT}/_intake/arithmetic/frames/page_{fr:03d}.jpg").convert("L")
    a = np.asarray(im).astype(int)
    x0, x1 = int(a.shape[1] * 0.04), int(a.shape[1] * 0.70)
    bs = bands(a, x0, x1)
    if len(sys.argv) == 2:
        for k, (y0, y1) in enumerate(bs, 1):
            cols = np.nonzero((a[y0:y1, :] < 140).sum(axis=0) > 1)[0]
            print(k, y0, y1, y1 - y0, cols.min() if len(cols) else -1, cols.max() if len(cols) else -1)
        return
    out = sys.argv[2]
    k1, k2 = [int(v) for v in sys.argv[3].split("-")]
    sc = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    tiles = []
    for k in range(k1, k2 + 1):
        y0, y1 = bs[k - 1]
        cols = np.nonzero((a[y0:y1, :] < 140).sum(axis=0) > 1)[0]
        l, r = max(cols.min() - 20, 0), min(cols.max() + 20, a.shape[1])
        mid = (l + r) // 2
        for p, (u, v) in enumerate(((l, mid + 30), (mid - 30, r)), 1):
            t = im.crop((u, max(y0 - 22, 0), v, min(y1 + 14, a.shape[0])))
            tiles.append((f"{k}.{p}", t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)))
    W = max(t.width for _, t in tiles) + 50
    H = sum(t.height + 8 for _, t in tiles)
    sheet = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(sheet)
    y = 0
    for n, t in tiles:
        d.text((2, y + 4), n, fill=0)
        sheet.paste(t, (48, y))
        y += t.height + 8
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
