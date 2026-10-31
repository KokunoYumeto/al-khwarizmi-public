"""Build suter_en.pdf deterministically: run build_suter_en.py, then XeLaTeX in a temporary folder with a fixed
SOURCE_DATE_EPOCH (FORCE_SOURCE_DATE=1) and always the same folder, until the .aux file no longer changes (the
footnote marks are numbered by page, so a page break moved by the second run needs a third), and copy the PDF beside
the TeX. Two builds give the same bytes.
python make_pdf.py [--check]   (--check: build into the temporary folder only and compare with the PDF here)"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPOCH = "1793404800"          # 2026-10-31 00:00 UTC, fixed


def build(dest):
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1", PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "build_suter_en.py"], cwd=HERE, env=env, capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode:
        raise SystemExit(r.stderr)
    tmp = Path(tempfile.gettempdir()) / "suter_en_build"      # always the same folder: its path enters the PDF
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    aux = None
    for _ in range(5):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={tmp}",
                            "suter_en.tex"], cwd=HERE, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"xelatex failed; see {tmp}")
        now = (tmp / "suter_en.aux").read_bytes()
        if now == aux:
            break
        aux = now
    else:
        raise SystemExit("the .aux file did not settle in five runs")
    log = (tmp / "suter_en.log").read_text(encoding="utf-8", errors="replace")
    missing = sorted(set(line for line in log.splitlines() if "Missing character" in line))
    shutil.copy2(tmp / "suter_en.pdf", dest)
    shutil.rmtree(tmp, ignore_errors=True)
    return missing


def main():
    if "--check" in sys.argv:
        out = Path(tempfile.mkdtemp(prefix="suterenchk_")) / "suter_en.pdf"
        missing = build(out)
        a = hashlib.sha256(out.read_bytes()).hexdigest()
        b = hashlib.sha256((HERE / "suter_en.pdf").read_bytes()).hexdigest()
        print(f"rebuilt {a[:16]}; here {b[:16]}; identical: {a == b}; missing characters: {len(missing)}")
        sys.exit(0 if a == b else 1)
    missing = build(HERE / "suter_en.pdf")
    for line in missing:
        print(line)
    print(f"suter_en.pdf {hashlib.sha256((HERE / 'suter_en.pdf').read_bytes()).hexdigest()}; missing "
          f"characters: {len(missing)}")


if __name__ == "__main__":
    main()
