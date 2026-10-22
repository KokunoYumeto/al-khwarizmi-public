"""The gap after ر, ز or و, whose tail reaches under the next letter: the gap between the letters measured on the ink
above the baseline only (rows above the baseline + CLIP px), so that the tail does not count. The baseline is the row
of the line with the most ink. For each x (inside the gap, read off a reading strip), the split column is the one with
the least ink above the baseline within S px; the two sides are the letter bodies (components of at least 95 px of
ink that reach the baseline; dots left out) that have ink within W px of the split on their side. Prints the clipped gap and the full gap.
python clipgap.py FRAME BOX X[:LABEL] [...] [--clip=4] [--s=15] [--w=70]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k, box = int(args[0]), int(args[1])
    clip, s, w = int(opt.get("clip", 4)), int(opt.get("s", 15)), int(opt.get("w", 70))
    y0, y1, _, _ = json.loads((ROOT / "_intake" / "geography" / "lines" / f"f{k:03d}_boxes.json").read_text())[box - 1]
    y0 -= 14
    y1 += 6
    g = np.asarray(Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L"))
    band = g[y0:y1] < 110
    base = int(np.argmax(band.sum(axis=1)))
    lab, n = ndimage.label(band, structure=np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    keep = np.zeros(n + 1, bool)
    # letter bodies: at least 60 px of ink, reaching the baseline (dots above and below the line are left out)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sizes[i - 1] >= 60 and sl[0].start <= base + 4 and sl[0].stop - 1 >= base - 8:
            keep[i] = True
    body = keep[lab]
    upper = body.copy()
    upper[base + clip + 1:] = False
    colink = upper.sum(axis=0)
    for spec in args[2:]:
        x, _, label = spec.partition(":")
        x0 = int(x)
        split = min(range(x0 - s, x0 + s + 1), key=lambda c: (colink[c], abs(c - x0)))
        out = []
        for name, m in (("clipped", upper), ("full", body)):
            ys, xs = np.nonzero(m[:, split - w:split + w + 1])
            xs = xs + split - w
            R = np.c_[ys[xs > split], xs[xs > split]]
            L = np.c_[ys[xs < split], xs[xs < split]]
            if len(R) == 0 or len(L) == 0:
                out.append(f"{name} -")
                continue
            # only the letters next to the split: the ink connected to the column nearest the split on each side
            Rl = lab[R[:, 0], R[:, 1]]
            Ll = lab[L[:, 0], L[:, 1]]
            rc = Rl[np.argmin(R[:, 1])]
            lc = Ll[np.argmax(L[:, 1])]
            R = R[Rl == rc]
            L = L[Ll == lc]
            d = cKDTree(L).query(R)[0].min() - 1
            out.append(f"{name} {d:.0f}")
        print(f"{(label or str(x0)):22s} x {x0}->{split}: " + ", ".join(out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
