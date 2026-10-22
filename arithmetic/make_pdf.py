"""Build algoritmi_1857.pdf deterministically: run build_algoritmi.py, then XeLaTeX twice in a temporary folder with a fixed
SOURCE_DATE_EPOCH (FORCE_SOURCE_DATE=1) and always the same folder, and copy the PDF beside the TeX. Two runs give the same bytes.
python make_pdf.py [--check]   (--check: build into the temporary folder only and compare with the PDF here)"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPOCH = "1792195200"          # 2026-10-17 00:00 UTC, fixed


def build(dest):
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1", PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "build_algoritmi.py"], cwd=HERE, env=env, capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode:
        raise SystemExit(r.stderr)
    tmp = Path(tempfile.gettempdir()) / "algoritmi_1857_build"      # always the same folder: its path enters the PDF
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={tmp}",
                            "algoritmi_1857.tex"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600)
        if r.returncode:
            raise SystemExit(f"xelatex failed; see {tmp}")
    log = (tmp / "algoritmi_1857.log").read_text(encoding="utf-8", errors="replace")
    missing = log.count("Missing character")
    shutil.copy2(tmp / "algoritmi_1857.pdf", dest)
    shutil.rmtree(tmp, ignore_errors=True)
    return missing


def main():
    if "--check" in sys.argv:
        out = Path(tempfile.mkdtemp(prefix="algchk_")) / "algoritmi_1857.pdf"
        missing = build(out)
        a = hashlib.sha256(out.read_bytes()).hexdigest()
        b = hashlib.sha256((HERE / "algoritmi_1857.pdf").read_bytes()).hexdigest()
        print(f"rebuilt {a[:16]}; here {b[:16]}; identical: {a == b}; missing characters: {missing}")
        sys.exit(0 if a == b else 1)
    missing = build(HERE / "algoritmi_1857.pdf")
    print(f"algoritmi_1857.pdf {hashlib.sha256((HERE / 'algoritmi_1857.pdf').read_bytes()).hexdigest()}; missing characters: "
          f"{missing}")


if __name__ == "__main__":
    main()
