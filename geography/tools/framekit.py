"""Reading kit for one frame: the line boxes (lines.py on the frame with the figures of its page file, if any, and the
--blank rectangles painted white; saved as fNNN_boxes.json), an overview (ov_fNNN.png, a third of the size), and the
printed lines in reading strips of N lines at ZOOM (rs_fNNN_K.png), each line with its box number in the margin and a
light tick every 100 px of the frame below it, for locating letters by their x. Lines are taken from FIRST to LAST box.
python framekit.py FRAME [--first=2] [--last=N] [--per=3] [--zoom=1.0] [--blank=X0,Y0,X1,Y1[;...]]"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from readband import blanked, frame_boxes  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_intake" / "geography" / "lines"


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    k = int(args[0])
    extra = [[int(v) for v in r.split(",")] for r in opt["blank"].split(";")] if "blank" in opt else []
    im = blanked(k, extra)
    bx = frame_boxes(im)
    (OUT / f"f{k:03d}_boxes.json").write_text(json.dumps(bx), encoding="utf-8")
    for i, b in enumerate(bx, 1):
        print(i, b, "h", b[1] - b[0], "w", b[3] - b[2])
    full = Image.open(ROOT / "_intake" / "geography" / "frames" / f"page_{k:03d}.jpg").convert("L")
    ov = ImageOps.autocontrast(full, cutoff=1)
    ov.resize((ov.width // 3, ov.height // 3), Image.LANCZOS).save(OUT / f"ov_f{k:03d}.png")
    first = int(opt.get("first", 2))
    last = int(opt.get("last", len(bx)))
    per = int(opt.get("per", 3))
    z = float(opt.get("zoom", 1.0))
    font = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=13)
    x0 = min(b[2] for b in bx[first - 1:last]) - 10
    x1 = max(b[3] for b in bx[first - 1:last]) + 10
    strips = []
    for n in range(first, last + 1):
        y0, y1, _, _ = bx[n - 1]
        crop = ImageOps.autocontrast(full.crop((x0, y0 - 14, x1, y1 + 6)), cutoff=1)
        crop = crop.resize((int(crop.width * z), int(crop.height * z)), Image.LANCZOS)
        t = Image.new("RGB", (crop.width + 50, crop.height + 16), "white")
        t.paste(crop.convert("RGB"), (50, 0))
        d = ImageDraw.Draw(t)
        d.text((4, crop.height // 2 - 11), str(n), fill=(0, 0, 0), font=font)
        for x in range((x0 // 100 + 1) * 100, x1, 100):
            xx = 50 + (x - x0) * z
            d.line([(xx, crop.height + 2), (xx, crop.height + 8)], fill=(200, 60, 60))
            d.text((xx + 2, crop.height + 2), str(x), fill=(200, 60, 60), font=small)
        strips.append(t)
    for j in range(0, len(strips), per):
        part = strips[j:j + per]
        W = max(s.width for s in part)
        H = sum(s.height + 6 for s in part)
        out = Image.new("RGB", (W, H), (180, 180, 180))
        y = 0
        for s in part:
            out.paste(s, (0, y))
            y += s.height + 6
        out.save(OUT / f"rs_f{k:03d}_{j // per + 1}.png")
    print(f"{len(strips)} lines in {(len(strips) + per - 1) // per} strips; overview ov_f{k:03d}.png")


if __name__ == "__main__":
    main()
