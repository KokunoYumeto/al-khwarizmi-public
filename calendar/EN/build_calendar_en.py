"""English translation of al-Khwārizmī's treatise on the Jewish calendar (Hyderabad edition, 1947).

python build_calendar_en.py     checks text_en.txt against ../anchors.tsv and writes calendar_en.tex, calendar_en.pdf
                                and alignment.tsv

text_en.txt holds one block for each title-page line, heading or paragraph of the edition (the format is described at
its head). The build stops unless every line of the edition (../anchors.tsv) belongs to exactly one block, the blocks
follow the order of the edition, every [^n] has its translator's note and every footnote of the edition is called
once. Translator's notes are lettered, the edition's footnote is numbered; the printed pages stand in the margin."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = "AK15-"


def anchors():
    rows = []
    for line in (HERE.parent / "anchors.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        a, pdf, printed, _line, kind, text = line.split("\t", 5)
        rows.append((a, printed, kind, text))
    return rows


def expand(spec, order):
    out = []
    for part in spec.split(" + "):
        a, _, b = part.strip().partition("..")
        a, b = PREFIX + a, PREFIX + (b or a)
        if a not in order or b not in order or order[b] < order[a]:
            raise SystemExit(f"bad range {part!r}")
        out += [x for x in order if order[a] <= order[x] <= order[b]]
    return out


def parse():
    blocks, cur = [], None
    for raw in (HERE / "text_en.txt").read_text(encoding="utf-8").splitlines():
        if raw.startswith("#"):
            continue
        m = re.match(r"@(t|r|h|p) (\S.*)$", raw)
        f = re.match(r"@f (\S+) (\S.*)$", raw)
        if m or f:
            cur = {"kind": "f" if f else m.group(1), "spec": (f or m).group(2), "key": f.group(1) if f else None,
                   "text": [], "notes": []}
            if f:
                cur["spec"] = f.group(2)
            blocks.append(cur)
        elif raw.startswith("@n "):
            cur["notes"].append(raw[3:])
        elif cur is not None:
            cur["text"].append(raw)
    return blocks


def inline(t):
    """the TeX of a stretch of English"""
    t = t.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
    t = re.sub(r"\{ar:([^{}]*)\}", lambda m: r"\textarabic{" + m.group(1) + "}", t)
    t = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", t)
    t = re.sub(r"\^s\b", r"\\textsuperscript{s}", t)
    t = t.replace("«", "«\u202f").replace("»", "\u202f»") if False else t
    return t


def render(blocks, rows):
    printed = {a: p.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")) for a, p, _k, _t in rows}
    foot = {b["key"]: inline(" ".join(b["text"])) for b in blocks if b["kind"] == "f"}
    body, seen_pages = [], set()
    for b in blocks:
        if b["kind"] == "f":
            continue
        pages = []
        for a in b["anchors"]:
            p = printed[a]
            if p != "-" and p not in pages:
                pages.append(p)
        mark = ""
        new = [p for p in pages if p not in seen_pages]
        if new:
            mark = r"\Pg{" + ("p. " if len(pages) == 1 else "pp. ") + "–".join(dict.fromkeys([pages[0], pages[-1]]))\
                   + "}"
            seen_pages.update(pages)
        notes = list(b["notes"])

        def tex(text):
            parts = re.split(r"(\[\^[^\]]+\])", text)
            out = []
            for part in parts:
                if part == "[^n]":
                    out.append(r"\footnoteT{" + inline(notes.pop(0)) + "}")
                elif re.fullmatch(r"\[\^[^\]]+\]", part):
                    out.append(r"\footnote{" + foot[part[2:-1]] + "}")
                else:
                    out.append(inline(part))
            return "".join(out)

        paras = [[]]
        for line in b["text"]:
            if line.strip():
                paras[-1].append(line.strip())
            elif paras[-1]:
                paras.append([])
        texts = [tex(" ".join(p)) for p in paras if p] if b["kind"] != "r" else []
        if b["kind"] == "t":
            body.append(r"\begin{center}" + mark + texts[0] + r"\end{center}")
        elif b["kind"] == "r":
            cells = [tex(c.strip()) for c in " ".join(b["text"]).split(" | ")]
            body.append(r"\noindent" + mark + r"\begin{tabular}{@{}p{0.48\textwidth}@{\hspace{0.04\textwidth}}"
                        r"p{0.48\textwidth}@{}}" + " & ".join(cells) + r"\end{tabular}\par\smallskip")
        elif b["kind"] == "h":
            body.append(r"\subsection*{" + mark + texts[0] + "}")
        else:
            body.append(mark + "\n\n".join(texts))
        if b["anchors"][-1] in (PREFIX + "P001-L14", PREFIX + "P002-L12"):
            body.append(r"\bigskip\noindent\rule{\textwidth}{0.4pt}\bigskip")
    return PREAMBLE + "\n\n".join(body) + "\n" + END


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,top=25mm,bottom=25mm,left=30mm,right=40mm,marginparwidth=22mm]{geometry}
\usepackage{fontspec,polyglossia,bigfoot,perpage}
\setmainlanguage{english}\setotherlanguage{arabic}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\arabicfont{Amiri}[Script=Arabic]
\DeclareNewFootnote{default}\DeclareNewFootnote{T}[alph]
\MakePerPage{footnote}\MakePerPage{footnoteT}
\makeatletter
\newcommand{\TNoteLetter}[1]{\ifnum#1>26 \@alph{\numexpr(#1-14)/26\relax}\@alph{\numexpr#1-26*((#1-14)/26)\relax}\else\@alph{#1}\fi}
\renewcommand{\thefootnoteT}{\TNoteLetter{\value{footnoteT}}}
\makeatother
\newcommand{\Pg}[1]{\marginpar{\footnotesize #1}}
\setlength{\parindent}{1.5em}\setlength{\parskip}{0.3em}
\pagestyle{plain}
\begin{document}
\begin{center}{\Large al-Khwārizmī, \textit{On Finding the Era of the Jews and Their Festivals}}\\[1mm]
{\large English translation of the Hyderabad edition (1947)}\end{center}
\medskip
{\small Every line of the edition is translated, in its order, from the line-by-line transcription in this repository
(\texttt{../anchors.tsv}). The pages of the edition stand in the margin. The edition's footnote is numbered; the
translator's notes are lettered. They record where the translation follows a correction of the print, with the
evidence; where the print's figure is kept and the computation gives another; and the readings that stay unresolved.
The corrections rest on the critical notes of the transcription (\texttt{../critical\_findings.tsv}), which check the
figures by the arithmetic of the calendar and by F. de Blois's account of the manuscript. Words in square brackets are
supplied. AI-translated (Claude), 2026; no person has proofread it. Dedicated to the public domain (CC0 1.0).}
\bigskip

"""
END = r"\end{document}" + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = anchors()
    order = {a: k for k, (a, _p, _k, _t) in enumerate(rows)}
    blocks = parse()
    errors, used, last = [], [], -1
    for b in blocks:
        b["anchors"] = expand(b["spec"], order)
        if b["kind"] != "f":   # a footnote of the edition stands where it is called
            if order[b["anchors"][0]] <= last:
                errors.append(f"block {b['spec']} is out of order or overlaps the one before")
            last = order[b["anchors"][-1]]
        used += b["anchors"]
        n = sum(t.count("[^n]") for t in b["text"])
        if n != len(b["notes"]):
            errors.append(f"block {b['spec']}: {n} [^n] marks, {len(b['notes'])} notes")
    missing = [a for a, *_ in rows if a not in used]
    twice = sorted({a for a in used if used.count(a) > 1})
    if missing:
        errors.append("lines without English: " + ", ".join(missing))
    if twice:
        errors.append("lines in two blocks: " + ", ".join(twice))
    keys = [b["key"] for b in blocks if b["kind"] == "f"]
    calls = [c for b in blocks for t in b["text"] for c in re.findall(r"\[\^([^\]n][^\]]*)\]", t)]
    for k in set(keys) | set(calls):
        if keys.count(k) != 1 or calls.count(k) != 1:
            errors.append(f"footnote {k}: {keys.count(k)} texts, {calls.count(k)} calls")
    if errors:
        raise SystemExit("\n".join(errors))
    tex = render(blocks, rows)
    (HERE / "calendar_en.tex").write_text(tex, encoding="utf-8", newline="\n")
    with open(HERE / "alignment.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("block\tkind\tfirst_anchor\tlast_anchor\tlines\twords\n")
        for k, b in enumerate(blocks, 1):
            words = len(re.findall(r"\w+", " ".join(b["text"])))
            f.write(f"{k}\t{b['kind']}\t{b['anchors'][0]}\t{b['anchors'][-1]}\t{len(b['anchors'])}\t{words}\n")
    for run in (1, 2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "calendar_en.tex"], cwd=HERE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise SystemExit("XeLaTeX failed:\n" + r.stdout[-3000:])
    log = (HERE / "calendar_en.log").read_text(encoding="utf-8", errors="replace")
    miss = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
    for ext in ("aux", "log", "out"):
        (HERE / f"calendar_en.{ext}").unlink(missing_ok=True)
    words = sum(len(re.findall(r"\w+", " ".join(b["text"] + b["notes"]))) for b in blocks)
    print(f"{len(rows)} lines in {len(blocks)} blocks, {words} words; missing characters: {''.join(miss) or 'none'}")
    if miss:
        raise SystemExit(1)


main()
