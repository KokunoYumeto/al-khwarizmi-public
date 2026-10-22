"""Build tafeln_1914_latin.pdf and tafeln_1914_suter.pdf deterministically: run build_tafeln.py, then XeLaTeX twice for
each file in a temporary folder with a fixed SOURCE_DATE_EPOCH (FORCE_SOURCE_DATE=1) and always the same folder, and copy
the PDFs beside the TeX. Two runs give the same bytes.
python make_pdf.py [--check]   (--check: build into the temporary folder only and compare with the PDFs here)"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPOCH = "1792195200"          # 2026-10-17 00:00 UTC, fixed
NAMES = ("tafeln_1914_latin", "tafeln_1914_suter")


def build(dest_dir):
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1", PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "build_tafeln.py"], cwd=HERE, env=env, capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode:
        raise SystemExit(r.stderr)
    missing = {}
    for name in NAMES:
        tmp = Path(tempfile.gettempdir()) / f"{name}_build"      # always the same folder: its path enters the PDF
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        for _ in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={tmp}",
                                f"{name}.tex"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=900)
            if r.returncode:
                raise SystemExit(f"xelatex failed on {name}; see {tmp}")
        log = (tmp / f"{name}.log").read_text(encoding="utf-8", errors="replace")
        missing[name] = log.count("Missing character")
        shutil.copy2(tmp / f"{name}.pdf", Path(dest_dir) / f"{name}.pdf")
        shutil.rmtree(tmp, ignore_errors=True)
    return missing


def main():
    if "--check" in sys.argv:
        out = Path(tempfile.mkdtemp(prefix="tafchk_"))
        missing = build(out)
        same = True
        for name in NAMES:
            a = hashlib.sha256((out / f"{name}.pdf").read_bytes()).hexdigest()
            b = hashlib.sha256((HERE / f"{name}.pdf").read_bytes()).hexdigest()
            same &= a == b
            print(f"{name}: rebuilt {a[:16]}; here {b[:16]}; identical: {a == b}; missing characters: {missing[name]}")
        sys.exit(0 if same else 1)
    missing = build(HERE)
    for name in NAMES:
        print(f"{name}.pdf {hashlib.sha256((HERE / f'{name}.pdf').read_bytes()).hexdigest()}; missing characters: "
              f"{missing[name]}")


if __name__ == "__main__":
    main()
