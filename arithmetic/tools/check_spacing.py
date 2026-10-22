"""Compare the spaces at the punctuation of the page files with the measured gaps (tools/punct.py).

python check_spacing.py FRAME [FRAME ...]

For each printed line the marks found by punct.py are paired, in order, with the punctuation characters of the
transcribed line (. , : ;); where the counts differ the line is reported for reading on the scan. For each pair the rule
of punct.py is applied: a space after a mark where the gap is at least 12 px or at least two thirds of the median word
space of the line, a space before a mark where the gap is at least 10 px. Disagreements with the transcription are
printed. The lines of the text are the bands of the page after the page number (the first band); the editor's footnotes
are compared as well (they follow the text)."""
import re
import sys
from pathlib import Path

import punct

PAGES = Path(__file__).resolve().parents[1] / "pages"


def transcribed_lines(fr):
    out = []
    for raw in (PAGES / f"AK02-F{fr:03d}.txt").read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith(("%", "@obs", "@copy", "@critical", "@variant", "@unres", "@m", "@page", "@kind")):
            continue
        tag = "N" if raw.startswith("@n ") else "L"
        body = raw.split(" ", 1)[1] if raw.startswith(("@p ", "@c ", "@h ", "@n ")) else raw
        body = re.sub(r"\{(?:i|b|sc|sup):([^{}]*)\}", r"\1", body)
        out.append((tag, body))
    return out


def marks_in(text):
    """the punctuation characters of a line with the space before and after each"""
    res = []
    for k, ch in enumerate(text):
        if ch in ".,:;":
            res.append((ch, k > 0 and text[k - 1] == " ", k + 1 < len(text) and text[k + 1] == " ",
                        k + 1 == len(text)))
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for fr in [int(a) for a in sys.argv[1:]]:
        tl = transcribed_lines(fr)
        found = {}
        for r in punct.analyse(fr):
            found.setdefault(r["line"], []).append(r)
        nl, nn = sum(1 for t, _ in tl if t == "L"), sum(1 for t, _ in tl if t == "N")
        print(f"== frame {fr}: {nl} text lines, {nn} note lines; {len(found)} lines with marks found")
        first = 1 if fr == 7 else 2            # frame 7 has its page number above the area searched
        for idx, (tag, text) in enumerate(tl):
            band = idx + first
            lab = f"{'L' if tag == 'L' else 'N'}{(idx + 1) if tag == 'L' else (idx + 1 - nl):02d}"
            tm = marks_in(text)
            fm = sorted(found.get(band, []), key=lambda r: r["x"])
            if len(tm) != len(fm):
                print(f"  {lab}: {len(tm)} marks transcribed, {len(fm)} found  | {text[:70]}")
                continue
            for (ch, sp_b, sp_a, at_end), r in zip(tm, fm):
                b, a, med = r["before"], r["after"], r["median"]
                if b is not None and b <= 45:
                    want_b = b >= 10
                    if want_b != sp_b:
                        print(f"  {lab}: «{ch}» at x{r['x']}: before {b} px -> {'space' if want_b else 'no space'}"
                              f" before, transcribed {'with' if sp_b else 'without'}  | {text[:70]}")
                if a is not None and a <= 45 and not at_end:
                    want_a = a >= 12 or (med and a >= 2 / 3 * med)
                    if want_a != sp_a:
                        print(f"  {lab}: «{ch}» at x{r['x']}: after {a} px (median {med:.1f}) -> "
                              f"{'space' if want_a else 'no space'} after, transcribed {'with' if sp_a else 'without'}"
                              f"  | {text[:70]}")


if __name__ == "__main__":
    main()
