"""A second machine reading for the transcription: Surya OCR (run on the text block of a frame, see suryaprep.py) is
compared with the transcription line by line. Surya's lines are grouped by their height on the page (pieces of one
printed line joined right to left) and aligned with the transcribed lines in order, each transcribed line paired with
the machine line that resembles it most, so that the page number, the editors' footnotes and pencil notes, which the
transcription does not contain, fall out. In each pair the words are normalized (vowel signs, hamza and madda seats,
dotless and dotted yā', tā' marbūṭa, tatwīl, punctuation; the labels of figures are kept, the note marks dropped) and
aligned, and every difference is printed for a second look at the scan. Word spaces are compared too: a word of one
side that is two words of the other is reported as a spacing difference. The machine reading is a witness, never a
source of readings.
python suryacheck.py RESULTS.json FRAME [FRAME ...]"""
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from markup import plain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "algebra" / "pages"


def norm(w):
    w = re.sub(r"[ً-ْٰـ]", "", w)
    w = re.sub(r"[أإآٱ]", "ا", w).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي").replace("ٮ", "ب")
    return re.sub(r"[^ء-ي]", "", w)


def toks(text):
    text = plain(text)
    return [n for n in (norm(w) for w in text.split()) if n]


def page_lines(k):
    out = []
    for ln in (PAGES / f"AK01-F{k:03d}.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith(("%", "@")) and not ln.startswith(("@h ", "@c ", "@p ")):
            continue
        out.append(re.sub(r"^@[hcp] ", "", ln))
    return out


def machine_lines(page):
    """Surya's lines, the pieces of one printed line (overlapping in height) joined from right to left"""
    tl = sorted(page["text_lines"], key=lambda t: (t["bbox"][1] + t["bbox"][3]) / 2)
    groups = []
    for t in tl:
        y0, y1 = t["bbox"][1], t["bbox"][3]
        if groups:
            g0, g1 = groups[-1]["y"]
            if min(y1, g1) - max(y0, g0) > 0.5 * min(y1 - y0, g1 - g0):
                groups[-1]["items"].append(t)
                groups[-1]["y"] = (min(g0, y0), max(g1, y1))
                continue
        groups.append({"y": (y0, y1), "items": [t]})
    return [" ".join(t["text"] for t in sorted(g["items"], key=lambda t: -t["bbox"][2])) for g in groups]


def align(a, b):
    """order-preserving pairing of the transcribed lines a with the machine lines b, maximizing the summed
    similarity; a pair needs a similarity of at least 0.3"""
    sim = [[difflib.SequenceMatcher(a=" ".join(toks(x)), b=" ".join(toks(y)), autojunk=False).ratio() for y in b]
           for x in a]
    n, m = len(a), len(b)
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            s = best[i + 1][j + 1] + sim[i][j] if sim[i][j] >= 0.3 else -1
            best[i][j] = max(s, best[i + 1][j], best[i][j + 1])
    pairs, i, j = {}, 0, 0
    while i < n and j < m:
        if sim[i][j] >= 0.3 and best[i][j] == best[i + 1][j + 1] + sim[i][j]:
            pairs[i] = j
            i, j = i + 1, j + 1
        elif best[i][j] == best[i + 1][j]:
            i += 1
        else:
            j += 1
    return pairs


def main():
    res = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    total = diffs = 0
    for k in map(int, sys.argv[2:]):
        page = res[f"body_{k:03d}"][0]
        mine = page_lines(k)
        theirs = machine_lines(page)
        pairs = align(mine, theirs)
        print(f"frame {k}: {len(mine)} lines transcribed, {len(theirs)} lines read by Surya, {len(pairs)} paired")
        for j, ln in enumerate(mine):
            a = toks(ln)
            total += len(a)
            if j not in pairs:
                diffs += 1
                print(f"  L{j + 1:02d} no machine line resembles it")
                continue
            b = toks(theirs[pairs[j]])
            sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal":
                    continue
                x, y = " ".join(a[i1:i2]), " ".join(b[j1:j2])
                kind = "space" if x.replace(" ", "") == y.replace(" ", "") else op
                diffs += 1
                print(f"  L{j + 1:02d} {kind:7s} mine «{x}»  surya «{y}»")
    print(f"{total} words compared, {diffs} differences")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
