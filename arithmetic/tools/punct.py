"""The punctuation of a page of the arithmetic, found by its form, with the gaps before and after each mark.

python punct.py FRAME [--all]        one line per mark: line, kind, x, gap before, gap after, the median word space of
                                     the line and the ratio after/median; --all also lists the marks inside numerals

Components are taken at the threshold 150 (so that the parts of a letter hang together). A dot is a component 5-14 px
wide and high with a dark core (darker than 110, at least 15 px); a dot whose bottom lies within 6 px of the base line
of its line is a point; a component 5-15 px wide and 15-34 px high whose top lies within 13 px above the base line and
which reaches at least 6 px below it is a comma; a dot standing 3-22 px above a point or a comma, within 5 px
horizontally, makes a colon or a semicolon. The base line of a line is the last row whose ink is at least 40% of its
densest row. Gaps are measured between columns that hold ink in the rows of the line (pencil strokes fainter than the
threshold do not count). The median word space is the median of the gaps of 9-45 px between the ink runs of the line.

The decision used in the page files: after a mark, a space where the gap is at least 12 px or at least two thirds of
the median word space of the line; before a mark, a space where the gap is at least 10 px. Over pp. 1-16 the gaps
after marks fall into a group of 3-8 px (no space) and a group from about 15 px up (a word space), with a thin
plateau of 9-14 px between them: gaps of 9-11 px, a hair space or none, are decided by the rule and are the least
certain. A pencil stroke darker than the threshold, or a letter whose stroke overhangs its neighbour (the cross-bar
of f), shortens the measured gap; every such case is read on the scan.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = str(Path(__file__).resolve().parents[2])


def text_block(g):
    """the columns of the text block: the widest run of columns whose ink (rows darker than 140) is at least 15% of
    the densest column, gaps of less than 40 px bridged"""
    col = (g[250:g.shape[0] - 300, :] < 140).sum(axis=0)
    dense = np.nonzero(col >= 0.15 * col.max())[0]
    best, s, p = (0, 0), dense[0], dense[0]
    for x in list(dense[1:]) + [10 ** 9]:
        if x - p > 40:
            if p - s > best[1] - best[0]:
                best = (s, p)
            s = x
        p = x
    return max(int(best[0]) - 5, 0), min(int(best[1]) + 6, g.shape[1])


def bands_of(g, x0, x1, y_lo=200, y_hi=None, pitch=59):
    """the printed lines: runs of rows with ink, a run taller than 1.3 lines split at the emptiest rows"""
    y_hi = y_hi or g.shape[0] - 150
    prof = (g[:, x0:x1] < 140).sum(axis=1)
    raw, y = [], y_lo
    while y < y_hi:
        if prof[y] > 3:
            s = y
            while y < y_hi and prof[y] > 3:
                y += 1
            if y - s >= 20:
                raw.append((s, y))
        y += 1
    out = []
    for s, e in raw:
        h = e - s
        k = int(round(h / pitch))
        if h > 1.3 * pitch and k >= 2:
            cuts = []
            for j in range(1, k):
                c = s + j * h / k
                a, b = int(c - 18), int(c + 18)
                cuts.append(a + int(np.argmin(prof[a:b])))
            edges = [s] + cuts + [e]
            out += [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
        else:
            out.append((s, e))
    return out


def runs(ink):
    xs = np.nonzero(ink)[0]
    out = []
    if not len(xs):
        return out
    s = p = xs[0]
    for x in xs[1:]:
        if x - p - 1 >= 3:
            out.append((s, p))
            s = x
        p = x
    out.append((s, p))
    return out


def analyse(fr):
    g = np.asarray(Image.open(f"{ROOT}/_intake/arithmetic/frames/page_{fr:03d}.jpg").convert("L")).astype(int)
    bx0, bx1 = text_block(g)
    lab, n = ndimage.label(g < 150)
    objs = ndimage.find_objects(lab)
    result = []
    for li, (y0, y1) in enumerate(bands_of(g, bx0, bx1), 1):
        band = g[y0:y1, bx0:bx1]
        prof = (band < 140).sum(axis=1)
        base = y0 + int(np.nonzero(prof >= 0.4 * prof.max())[0].max())
        ids = set(np.unique(lab[max(y0 - 6, 0):y1 + 14, bx0:bx1]).tolist()) - {0}
        dots, commas = [], []
        for i in ids:
            ys, xs = objs[i - 1]
            w, h = xs.stop - xs.start, ys.stop - ys.start
            core = ((g[ys, xs] < 110) & (lab[ys, xs] == i)).sum()
            if core < 15:
                continue
            if 5 <= w <= 14 and 5 <= h <= 14:
                dots.append({"x0": xs.start, "x1": xs.stop, "y0": ys.start, "y1": ys.stop, "id": i})
            elif 5 <= w <= 15 and 15 <= h <= 34 and base - 13 <= ys.start <= base - 2 and ys.stop >= base + 6:
                commas.append({"x0": xs.start, "x1": xs.stop, "y0": ys.start, "y1": ys.stop, "id": i})
        points = [d for d in dots if abs(d["y1"] - 1 - base) <= 6]
        uppers = [d for d in dots if d["y1"] - 1 < base - 6]
        marks, used = [], set()
        for low, kind1, kind2 in [(c, "comma", "semicolon") for c in commas] + [(p, "point", "colon") for p in points]:
            cx = (low["x0"] + low["x1"]) / 2
            up = None
            for u in uppers:
                if u["id"] in used:
                    continue
                ux = (u["x0"] + u["x1"]) / 2
                if abs(ux - cx) <= 5 and 3 <= low["y0"] - u["y1"] <= 22:
                    up = u
                    break
            if up:
                used.add(up["id"])
                marks.append((kind2, min(low["x0"], up["x0"]), max(low["x1"], up["x1"]), {low["id"], up["id"]}))
            else:
                marks.append((kind1, low["x0"], low["x1"], {low["id"]}))
        # the ink columns of the line, without the marks themselves
        line_lab = lab[y0:y1 + 8, bx0:bx1]
        inkmask = (g[y0:y1 + 8, bx0:bx1] < 150)
        rr = runs(inkmask.sum(axis=0) > 0)
        gaps = [rr[k + 1][0] - rr[k][1] - 1 for k in range(len(rr) - 1)]
        ws = [x for x in gaps if 9 <= x <= 45]
        med = float(np.median(ws)) if ws else 0.0
        for kind, mx0, mx1, mid in sorted(marks, key=lambda m: m[1]):
            other = inkmask & ~np.isin(line_lab, list(mid))
            colink = other.sum(axis=0) > 0
            left = np.nonzero(colink[:mx0 - bx0])[0]
            right = np.nonzero(colink[mx1 - bx0:])[0]
            before = (mx0 - bx0 - 1 - left.max()) if len(left) else None
            after = int(right.min()) if len(right) else None
            result.append({"line": li, "kind": kind, "x": mx0, "before": before, "after": after, "median": med,
                           "y": y0})
    return result


def main():
    fr = int(sys.argv[1])
    for r in analyse(fr):
        b = "end" if r["before"] is None or r["before"] > 45 else r["before"]
        a = "end" if r["after"] is None or r["after"] > 45 else r["after"]
        ratio = f"{r['after'] / r['median']:.2f}" if isinstance(a, int) and r["median"] else "-"
        sp_b = "space before" if isinstance(b, int) and b >= 10 else ""
        sp_a = ("space after" if isinstance(a, int) and (a >= 12 or (r["median"] and a >= 2 / 3 * r["median"])) else
                ("no space after" if isinstance(a, int) else ""))
        print(f"line {r['line']:2d}  {r['kind']:9s} x{r['x']:5d}  before {str(b):>3s}  after {str(a):>3s}  "
              f"median {r['median']:4.1f}  ratio {ratio:>4s}  {sp_b} {sp_a}")


if __name__ == "__main__":
    main()
