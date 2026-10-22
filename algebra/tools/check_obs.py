"""Check the observations of the page files against their lines: every Arabic word or phrase that an observation
quotes with a line reference, «… (L05)», «… (L04, L06)», «L07: …», must stand on one of the lines named (compared
after removing vowel signs and unifying the hamza seats, the dotless yā' and the tā' marbūṭa, as in ocrcheck.py). The
lines are counted as the build counts them (the printed lines of the page file, headings included). A reference that
names another frame, «… (frame 038, L07)», is checked against the lines of that frame. Prints every reference that
fails; exit status 1 if any.
python check_obs.py [FRAME ...]"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from markup import plain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "algebra" / "pages"
AR = r"[ء-ْٰٮ]"


def norm(s):
    s = re.sub(r"[ً-ْٰـ]", "", s)
    s = re.sub(r"[أإآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي").replace("ٮ", "ب")
    s = re.sub(r"[()]", " ", s)                 # a parenthesis separates the word it encloses, «(مال)ضربت»
    s = re.sub(r"[.:،؛]", " ", s)               # so does a stop set close, «القسمين.فان»
    return re.sub(r" +", " ", re.sub(r"[^ء-ي ]", "", s))


def refs(spec):
    """'L04, L06' / 'L04-L06' / 'L09; but ... L13' -> [4, 6, 9, 13]"""
    out = []
    for a, b in re.findall(r"L(\d+)(?:-L?(\d+))?", spec):
        a = int(a)
        out += list(range(a, int(b) + 1)) if b else [a]
    return out


def page_lines(p):
    raw = p.read_text(encoding="utf-8").splitlines()
    lines = [re.sub(r"^@[hcp] ", "", l) for l in raw
             if l.strip() and not (l.startswith(("%", "@")) and not l.startswith(("@h ", "@c ", "@p ")))]
    return raw, [norm(plain(l)) for l in lines]


def main():
    frames = [int(x) for x in sys.argv[1:]] or None
    bad = n = 0
    allp = {int(p.stem[-3:]): p for p in PAGES.glob("AK01-F*.txt")}
    for k, p in sorted(allp.items()):
        if frames and k not in frames:
            continue
        raw, L0 = page_lines(p)
        for o in (l for l in raw if l.startswith(("@obs", "@variant", "@copy"))):
            # «phrase» or bare Arabic phrase followed by a parenthesised line reference
            # a phrase is words of Arabic letters separated by single spaces; written so, the pattern has one way to match
            # a run of words and cannot backtrack exponentially on a long quotation
            for phrase, spec in re.findall(r"(" + AR + r"+(?: " + AR + r"+)*) ?\(([^)]*L\d+[^)]*)\)", o):
                other = re.match(r"\s*frame (\d+), (L\d+)", spec)
                if other and int(other.group(1)) not in allp:
                    continue                    # a frame not transcribed yet
                L = page_lines(allp[int(other.group(1))])[1] if other else L0
                nums = refs(other.group(2) if other else spec)
                ph = norm(phrase).strip()
                if not ph or not nums:
                    continue
                n += 1
                if not any(1 <= j <= len(L) and ph.split()[-1] in L[j - 1].split() + [L[j - 1].replace(" ", "")]
                           and ph in L[j - 1] for j in nums):
                    bad += 1
                    print(f"{p.stem}: «{phrase.strip()}» not on {spec.strip()}")
            # «L07: phrase …»: the first Arabic phrase after the reference is a reading of that line (other phrases of
            # the observation carry their own references); a variant may quote a reading that is not printed
            m = re.match(r"@obs (L\d+(?:-L\d+)?): (" + AR + r"+(?: " + AR + r"+)*)", o)
            if m:
                nums = refs(m.group(1))
                ph = norm(m.group(2)).strip()
                if len(ph) >= 3:
                    n += 1
                    if not any(1 <= j <= len(L0) and ph in L0[j - 1] for j in nums):
                        bad += 1
                        print(f"{p.stem}: «{m.group(2).strip()}» not on {m.group(1)}")
    print(f"{n} quoted references checked, {bad} not found")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
