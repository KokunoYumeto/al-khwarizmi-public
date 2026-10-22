"""A second net for the reading: compare the words of the transcription of a frame with a machine reading of the same
lines (Tesseract, Arabic, on the body block of the frame: from the top of the first text line to the bottom of the
last, as lines.py finds them). Both sides are normalized (vowel signs, hamza and madda seats, dotless and dotted yā',
tā' marbūṭa, tatwīl and punctuation removed or unified), and the words are compared as multisets; a word that the
transcription has and the machine reading lacks is printed with its line, for a second look at the scan. The machine
reading is a witness, never a source of readings.
python ocrcheck.py FRAME [FRAME ...]"""
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from markup import plain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "_intake" / "geography" / "frames"
LINES = ROOT / "_intake" / "geography" / "lines"
OCR = ROOT / "_intake" / "geography" / "ocr"
PAGES = ROOT / "geography" / "pages"
TESS = os.environ.get("TESSERACT", "tesseract")                 # the Tesseract executable
TESSDATA = os.environ.get("TESSDATA_PREFIX", "tessdata")        # a folder with ara.traineddata


def norm(w):
    w = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", w)
    w = re.sub(r"[أإآٱ]", "ا", w).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي").replace("ٮ", "ب")
    w = re.sub(r"[^\u0621-\u064A]", "", w)
    return w


def words(text):
    text = plain(text)
    return [norm(w) for w in text.split() if norm(w)]


def main():
    from PIL import Image
    for k in map(int, sys.argv[1:]):
        page = PAGES / f"AK05-F{k:03d}.txt"
        lines = [ln for ln in page.read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.startswith(("%", "@page", "@kind", "@obs", "@copy", "@ednotes", "@variant",
                                                       "@unres", "@withheld", "@fig", "@critical"))]
        lines = [re.sub(r"^@[hcp] ", "", ln) for ln in lines]
        bx = json.loads((LINES / f"f{k:03d}_boxes.json").read_text(encoding="utf-8"))
        tall = [b for b in bx if b[3] - b[2] > 600]               # text lines, not the page number or small marks
        # the body block: as many of the wide boxes from the top as the page has lines, joining split boxes
        hs = sorted(b[1] - b[0] for b in tall)
        med = hs[len(hs) // 2]
        y0, y1 = tall[0][0] - 10, None
        count, prev = 0, None
        for b in tall:
            short = b[1] - b[0] < 0.6 * med or (prev is not None and prev[1] - prev[0] < 0.6 * med)
            if prev is not None and b[0] - prev[1] < 8 and short:   # two pieces of one printed line
                prev = [prev[0], b[1]]
                y1 = b[1] + 10 if count == len(lines) else y1
                continue
            count += 1
            prev = b
            if count == len(lines):
                y1 = b[1] + 10
            if count > len(lines):
                break
        im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
        crop = im.crop((0, y0, im.width, y1))
        OCR.mkdir(parents=True, exist_ok=True)
        cp = OCR / f"body_{k:03d}.png"
        crop.save(cp)
        subprocess.run([TESS, str(cp), str(OCR / f"body_{k:03d}"), "--tessdata-dir", TESSDATA, "-l", "ara", "--psm", "4"],
                       capture_output=True)
        ocr = (OCR / f"body_{k:03d}.txt").read_text(encoding="utf-8")
        mine = Counter(w for ln in lines for w in words(ln))
        theirs = Counter(words(ocr))
        missing = mine - theirs
        extra = theirs - mine
        n = sum(mine.values())
        print(f"frame {k}: {n} words; {n - sum(missing.values())} found in the machine reading; "
              f"{sum(missing.values())} not found; machine-only words {sum(extra.values())}")
        for j, ln in enumerate(lines, 1):
            flag = [w for w in words(ln) if missing.get(w)]
            if flag:
                print(f"  L{j:02d}: " + " ".join(flag))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
