"""AK-I01: the cold audit of the al-Khwarizmi repository. It patches nothing. Run it in a fresh clone (a new root),
never in the working copy, because the builders it replays rewrite their derived files in place:

  git clone -c core.autocrlf=false REMOTE NEWROOT
  link NEWROOT/_intake to the local source images (they are verified by hash by the builders)
  python NEWROOT/integration/audit.py --receipt FILE_OUTSIDE_NEWROOT

From the committed files alone it checks that
  1. the clone is clean, and records its HEAD;
  2. integrate.py, run into a temporary folder, passes every check and reproduces every committed integration artifact
     byte for byte;
  3. every lane replays: make_pdf.py --check runs the lane's builder, which rewrites the records, ledgers, TeX and
     figures in place from the page files and the source images, rebuilds every PDF and compares its bytes with the
     committed PDF, and counts the missing characters;
  4. the practical returns replay (build_p01.py, build_p02.py);
  5. after all replays the clone is still clean (git status): every committed derived file is reproduced exactly;
  6. every committed PDF opens, every page renders, and every font is embedded (PyMuPDF);
and writes a receipt (JSON). Exit status 1 if any step fails.
python audit.py --receipt FILE"""
import datetime
import filecmp
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LANES = ["algebra", "geography", "arithmetic", "zij", "calendar"]
PDFS = ["algebra/jabr_1939.pdf", "geography/surat_1962.pdf", "arithmetic/algoritmi_1857.pdf",
        "zij/tafeln_1914_latin.pdf", "zij/tafeln_1914_suter.pdf", "calendar/calendar_1947.pdf"]
ARTIFACTS = ["COVERAGE.tsv", "SEAMS.tsv", "SPECIAL_UNITS.tsv", "WORKS_AND_BOUNDARIES.tsv",
             "INTEGRATION_CHECKPOINT.json"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(args, cwd=ROOT, timeout=3600):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1")
    r = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def git(*args):
    return run(["git", "-C", str(ROOT), *args])[1].strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    receipt_path = Path(sys.argv[sys.argv.index("--receipt") + 1]).resolve()
    if ROOT in receipt_path.parents:
        raise SystemExit("the receipt must be written outside the audited root")
    steps, ok_all = [], True

    def step(name, ok, detail):
        nonlocal ok_all
        ok_all &= bool(ok)
        steps.append({"step": name, "result": "PASS" if ok else "FAIL", "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail if isinstance(detail, str) else json.dumps(detail)[:300]}")

    started = now()
    head = git("rev-parse", "HEAD")
    status0 = git("status", "--porcelain")
    step("clean clone", status0 == "", {"head": head, "status": status0 or "clean"})

    # 2. the integration artifacts
    tmp = Path(tempfile.mkdtemp(prefix="akh_integrate_"))
    rc, out, err = run([sys.executable, "-B", str(HERE / "integrate.py"), "--out", str(tmp)])
    step("integrate.py checks", rc == 0, out.strip().splitlines()[-1] if out.strip() else err[-300:])
    names = ARTIFACTS + ["witnesses/" + p.name for p in sorted((HERE / "witnesses").glob("*.tsv"))]
    differ = [n for n in names if not (tmp / n).exists() or not filecmp.cmp(tmp / n, HERE / n, shallow=False)]
    extra = sorted(str(p.relative_to(tmp)).replace("\\", "/") for p in tmp.rglob("*") if p.is_file()
                   and str(p.relative_to(tmp)).replace("\\", "/") not in names)
    step("integration artifacts reproduced", not differ and not extra,
         {"compared": len(names), "differ": differ, "not committed": extra})

    # 3. the lanes
    for lane in LANES:
        rc, out, err = run([sys.executable, "-B", "make_pdf.py", "--check"], cwd=ROOT / lane)
        ident = re.findall(r"identical: (True|False)", out)
        miss = [int(x) for x in re.findall(r"missing characters: (\d+)", out)]
        ok = rc == 0 and ident and all(x == "True" for x in ident) and not any(miss)
        step(f"replay {lane}", ok, {"returncode": rc, "pdfs_identical": ident, "missing_characters": miss,
                                    "builder": out.strip().splitlines()[0] if out.strip() else err[-300:]})

    # 4. the practical returns
    for b in ("build_p01.py", "build_p02.py"):
        rc, out, err = run([sys.executable, "-B", b], cwd=ROOT / "practical")
        step(f"replay practical {b}", rc == 0, out.strip().splitlines()[-1][:200] if out.strip() else err[-300:])

    # 5. nothing changed
    status1 = git("status", "--porcelain")
    step("derived files reproduced exactly (clone still clean)", status1 == "", status1 or "clean")

    # 6. the PDFs
    import fitz
    for rel in PDFS:
        p = ROOT / rel
        try:
            doc = fitz.open(p)
            n = doc.page_count
            fonts, unembedded = set(), set()
            for pg in doc:
                pg.get_pixmap(dpi=24)
                for f in pg.get_fonts():
                    fonts.add(f[3])
                    if f[1] in ("", "n/a"):
                        unembedded.add(f[3])
            step(f"render {rel}", n > 0 and not unembedded,
                 {"pages": n, "fonts": len(fonts), "unembedded": sorted(unembedded)})
        except Exception as e:  # noqa: BLE001 - every failure is reported in the receipt
            step(f"render {rel}", False, repr(e)[:300])

    xe = (run(["xelatex", "--version"])[1].splitlines() or [""])[0]
    receipt = {
        "audit": "AK-I01 cold audit (new root; no patching)",
        "audited_head": head,
        "root_folder": ROOT.name,
        "started_utc": started, "finished_utc": now(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "xelatex": xe,
                        "pymupdf": fitz.VersionBind},
        "result": "PASS" if ok_all else "FAIL",
        "steps": steps,
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                            newline="\n")
    print("result:", receipt["result"], "receipt:", receipt_path.name)
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
