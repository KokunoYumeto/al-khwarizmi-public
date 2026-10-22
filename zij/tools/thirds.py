"""Three overlapping crops of a page of Suter's edition of the Zij (JP2 index), for reading: python thirds.py FRAME OUTPREFIX [SCALE]"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = str(Path(__file__).resolve().parents[2])
fr, pre = int(sys.argv[1]), sys.argv[2]
sc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.82
im = Image.open(f"{ROOT}/_intake/zij/frames/page_{fr:04d}.jpg").convert("L")
a = np.asarray(im).astype(int)
rows = np.nonzero((a[:, 100:a.shape[1] - 100] < 140).sum(axis=1) > 12)[0]
y0, y1 = max(rows.min() - 40, 0), min(rows.max() + 40, im.height)
h = (y1 - y0) // 3
for k in range(3):
    c = im.crop((0, y0 + k * h - (30 if k else 0), im.width, y0 + (k + 1) * h + 30))
    c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS).save(f"{pre}_{k}.png")
print(im.size, y0, y1)
