"""English of Boncompagni's Italian in his edition of the Latin «Dixit Algorizmi» (Rome, 1857).

python build_italian_en.py     checks italian_en.tsv against ../anchors.tsv and writes italian_en.tex and
                               italian_en.pdf

The edition's own matter is in Italian: the title page, the heading of the text, the folio marks of the Cambridge
manuscript in the margin and the six footnotes. The build stops unless every line of the title page (frame 3), every
line of the heading (frame 7, lines 1-4), every note line and every margin note of ../anchors.tsv has exactly one
English row. The Latin text of the treatise itself is not translated here."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def lines():
    rows = []
    for line in (HERE.parent / "anchors.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        a, frame, printed, _l, kind, text, margin = (line.split("\t") + [""])[:7]
        rows.append({"a": a, "frame": int(frame), "page": printed, "kind": kind, "text": text, "margin": margin})
    return rows


def wanted(rows):
    out = []
    for r in rows:
        if r["frame"] == 3 or (r["frame"] == 7 and r["a"] <= "AK02-F007-L04") or r["kind"] == "note":
            out.append(r["a"])
        if r["margin"]:
            out.append(r["a"] + "@margin")
    return out


def tex(t):
    t = t.replace("&", r"\&").replace("%", r"\%")
    t = re.sub(r"\{i:([^{}]*)\}", r"\\textit{\1}", t)
    t = re.sub(r"\{b:([^{}]*)\}", r"\\textbf{\1}", t)
    t = re.sub(r"\{sc:([^{}]*)\}", r"\\textsc{\1}", t)
    t = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", t)
    return t


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = lines()
    by = {r["a"]: r for r in rows}
    order = [r["a"] for r in rows]
    items = []
    for raw in (HERE / "italian_en.tsv").read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        spec, en = raw.split("\t")
        if spec.endswith("@margin"):
            cover = [spec]
            it = by[spec[:-7]]["margin"]
        else:
            a, _, b = spec.partition("..")
            b = b or a
            cover = order[order.index(a):order.index(b) + 1]
            it = " ".join(by[x]["text"] for x in cover)
            it = re.sub(r"(\w)- (\w)", r"\1\2", it)
            it = re.sub(r"(\w)-\} \{i:(\w)", r"\1\2", it)   # a word divided between two italic lines
        items.append((spec, cover, it, en))
    got = [c for _s, cover, _i, _e in items for c in cover]
    want = wanted(rows)
    errors = [f"no English: {a}" for a in want if a not in got]
    errors += [f"not Italian matter of the edition or covered twice: {a}" for a in got
               if a not in want or got.count(a) > 1]
    if errors:
        raise SystemExit("\n".join(sorted(set(errors))))
    body = []
    section = None
    for spec, cover, it, en in items:
        a = cover[0].split("@")[0]
        r = by[a]
        kind = ("Title page" if r["frame"] == 3 else "Heading of the text" if r["frame"] == 7 and "N" not in a
                and not spec.endswith("@margin") else "Margin note" if spec.endswith("@margin") else "Footnote")
        if kind in ("Title page", "Heading of the text") and section != kind:
            body.append(r"\subsection*{" + kind + "}")
            section = kind
        if kind in ("Margin note", "Footnote") and section not in ("Margin notes and footnotes",):
            body.append(r"\subsection*{The folio marks in the margin and the footnotes}")
            section = "Margin notes and footnotes"
        where = f"p. {r['page']}, " if r["page"] not in ("", "-") else ""
        label = (where + ("margin, at l. " + str(int(a[-2:])) if spec.endswith("@margin")
                          else "footnote" if kind == "Footnote" else "l. " + str(int(a[-2:]))))
        body.append(r"\noindent\begin{tabular}{@{}p{0.2\textwidth}@{\hspace{2mm}}p{0.38\textwidth}@{\hspace{3mm}}"
                    r"p{0.38\textwidth}@{}}{\footnotesize " + label + r"} & {\small " + tex(it) + "} & " + tex(en)
                    + r"\end{tabular}\par\smallskip")
    doc = r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=22mm]{geometry}
\usepackage{fontspec,polyglossia}
\setmainlanguage{english}\setotherlanguages{italian,latin}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\setlength{\parindent}{0pt}
\begin{document}
\begin{center}{\Large Boncompagni's Italian in his edition of \textit{Algoritmi de numero Indorum} (1857)}\\[1mm]
{\large in English}\end{center}
{\small Baldassarre Boncompagni printed the Latin arithmetic «Dixit Algorizmi» from the Cambridge manuscript Ii.\,6.\,5
in the first volume of his \textit{Trattati d'aritmetica} (Rome, 1857). His own matter is in Italian: the title page,
the heading of the text, the folio marks of the manuscript in the margin and six footnotes. Each line is given as this
repository transcribes it (\texttt{../anchors.tsv}), with its English; the Latin he quotes stands in italics with an
English rendering in parentheses. The Latin text of the treatise is not translated here: J. N. Crossley and A. S.
Henry translated the Cambridge manuscript into English («Thus Spake al-Khwārizmī», \textit{Historia Mathematica} 17,
1990). AI-translated (Claude), 2026; no person has proofread it. Dedicated to the public domain (CC0 1.0).}
\medskip
""" + "\n".join(body) + "\n\\end{document}\n"
    (HERE / "italian_en.tex").write_text(doc, encoding="utf-8", newline="\n")
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "italian_en.tex"], cwd=HERE,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("XeLaTeX failed:\n" + r.stdout[-3000:])
    log = (HERE / "italian_en.log").read_text(encoding="utf-8", errors="replace")
    miss = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
    for ext in ("aux", "log"):
        (HERE / f"italian_en.{ext}").unlink(missing_ok=True)
    print(f"{len(items)} items over {len(got)} lines and margin notes; missing characters: {''.join(miss) or 'none'}")
    if miss:
        raise SystemExit(1)


main()
