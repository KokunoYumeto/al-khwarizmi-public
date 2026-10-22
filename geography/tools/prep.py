"""Prepare the reading of one frame of the geography: the line boxes (framekit.py), the page views (pageview.py), the
cell sheet of the table rows (cellsheet.py) and the names column (pageview.py --names). The table rows are the boxes
whose ink reaches both the names column and the numeral columns; the rest (headings, notes) are listed.
python prep.py FRAME [--rows=B,B,...] [--lon=X0-X1 --lat=X0-X1]"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LINES = ROOT / "_intake" / "geography" / "lines"
FRAMES = ROOT / "_intake" / "geography" / "frames"


def run(*a):
    r = subprocess.run([sys.executable, "-B", *map(str, a)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("failed: " + " ".join(map(str, a)))
    return r.stdout


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    k = int(args[0])
    print(run(HERE / "framekit.py", k, "--first=1").strip().splitlines()[-1])
    bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
    g = np.asarray(Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L"))
    W = g.shape[1]
    rows = []
    for i, (y0, y1, x0, x1) in enumerate(bx, 1):
        band = g[y0:y1] < 120
        right = band[:, int(W * 0.45):int(W * 0.80)].sum()
        left = band[:, int(W * 0.08):int(W * 0.40)].sum()
        h = y1 - y0
        kind = "row?" if (right > 400 and left > 400 and 60 <= h <= 170) else ""
        print(f"box {i:2d} y{y0}-{y1} x{x0}-{x1} h{h} {kind}")
        if kind:
            rows.append(i)
    if "rows" in opt:
        rows = [int(v) for v in opt["rows"].split(",")]
    print("rows:", ",".join(map(str, rows)))
    for line in run(HERE / "pageview.py", k, "--names=" + ",".join(map(str, rows)), "--nz=1.3").splitlines():
        print(line)
    extra = []
    if "lon" in opt and "lat" in opt:
        extra = ["--lon=" + opt["lon"], "--lat=" + opt["lat"]]
    out = run(HERE / "cellsheet.py", k, ",".join(map(str, rows)), "--zoom=2.5", *extra)
    print("\n".join(l for l in out.splitlines() if not l.startswith("box ")))
    (LINES / f"cs_f{k:03d}.txt").write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
