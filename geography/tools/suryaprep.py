"""Prepare frames for the second machine reading (Surya OCR): the text block of each frame in grey, with the figures
of its page file (@fig rectangles) painted white, so that the machine reads the printed lines and not the labels of
the figures. The page number, the editors' footnotes and a reader's pencil are read too; suryacheck.py aligns the
lines and ignores what the transcription does not contain.
python suryaprep.py FRAME [FRAME ...]   -> _intake/geography/surya_in2/body_NNN.png
then: surya_ocr _intake/geography/surya_in2 --disable_math --output_dir _intake/geography/surya_out2"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "_intake" / "geography" / "frames"
PAGES = ROOT / "geography" / "pages"
OUT = ROOT / "_intake" / "geography" / "surya_in2"
BLOCK = (120, 300, 2430, 3860)          # the printed area of the frames, with the margins, away from the binding


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for k in map(int, sys.argv[1:]):
        im = Image.open(FRAMES / f"page_{k:03d}.jpg").convert("L")
        d = ImageDraw.Draw(im)
        for ln in (PAGES / f"AK05-F{k:03d}.txt").read_text(encoding="utf-8").splitlines():
            if ln.startswith("@fig "):
                x0, y0, x1, y1 = (int(v) for v in ln.split()[2:6])
                d.rectangle([x0, y0, x1, y1], fill=255)
        im.crop(BLOCK).save(OUT / f"body_{k:03d}.png")
        print(f"frame {k}: body_{k:03d}.png")


if __name__ == "__main__":
    main()
