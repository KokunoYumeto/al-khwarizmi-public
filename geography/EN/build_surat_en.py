"""English translation of al-Khwārizmī's Kitāb ṣūrat al-arḍ in the edition of Hans von Mžik (1926; Baghdad reprint
1962).

python build_surat_en.py     checks text_en.txt against ../anchors.tsv and writes surat_en.tex, surat_en.pdf and
                             alignment.tsv

text_en.txt holds one block for each title line, heading, run of paragraphs and table row of the edition, in its
order (the format is described at its head). The build stops unless every line of the edition (../anchors.tsv)
belongs to exactly one block, the blocks follow the order of the edition, every [^n] has its translator's note and no
mark of the draft is left. The pages of the edition stand in the margin, also where a page ends inside a paragraph:
there the mark follows the last point of the page."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = "AK05-"
fallback = []   # page marks set at the head of a paragraph, where the page ends inside its first point
AR = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
TITLE_FRAMES = {5, 7, 209, 210, 212, 214}


def anchors():
    rows = []
    for line in (HERE.parent / "anchors.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        a, frame, printed, _line, kind, text, _margin = line.split("\t")
        rows.append((a, int(frame), printed.translate(AR), kind, text))
    return rows


def parse():
    blocks, cur = [], None
    for raw in (HERE / "text_en.txt").read_text(encoding="utf-8").splitlines():
        if raw.startswith("#"):
            continue
        m = re.match(r"@([thpr]) (F\d{3}-L\d{2}(?:\.\.F\d{3}-L\d{2})?)$", raw)
        if m:
            cur = {"kind": m.group(1), "spec": m.group(2), "text": [], "notes": []}
            blocks.append(cur)
        elif raw.startswith("@n "):
            cur["notes"].append(raw[3:])
        elif raw.startswith("@"):
            raise SystemExit(f"unknown line: {raw[:60]}")
        elif cur is not None:
            cur["text"].append(raw)
    return blocks


def esc(t):
    return (t.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("~", r"\textasciitilde{}"))


def arabic(t):
    t = esc(t).replace("{z}", r"\Zero{}")
    # the editor's angle brackets inside Arabic words, drawn as in the transcription (they open to the left)
    return r"\textarabic{" + t.replace("⟨", r"\AngOpen{}").replace("⟩", r"\AngClose{}") + "}"


def inline(t):
    """the TeX of a stretch of English with {ar:...} spans"""
    out, pos = [], 0
    for m in re.finditer(r"\{ar:((?:[^{}]|\{z\})*)\}", t):
        out.append(esc(t[pos:m.start()]))
        out.append(arabic(m.group(1)))
        pos = m.end()
    out.append(esc(t[pos:]))
    s = "".join(out)
    s = re.sub(r"°(⟩?) (⟨?[\d/])", r"°\1~\2", s)   # degrees and minutes stay on one line
    s = re.sub(r"\b(longitude|latitude)(⟩?) (⟨?\d)", r"\1\2~\3", s)
    if re.search(r"[{}]", re.sub(r"\\textarabic\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\\[A-Za-z]+\{\}", "", s)):
        raise SystemExit(f"a brace is left in: {t[:80]}")
    return s.replace("⟨", r"\Ang{\langle}").replace("⟩", r"\Ang{\rangle}")


# the widths of the columns of the tables (mm), by the number of columns a row fills
COLS = {
    "cities7": [13, 19, 78, 10, 10, 10, 10],
    "cities10": [13, 19, 44, 10, 10, 14, 10, 10, 10, 10],
    "names3": [22, 31, 97],
    "coords10": [11, 11, 11, 11, 11, 11, 11, 11, 38, 22],
    "contents2": [125, 25],
}


def scheme(frame, ncols, first):
    if 165 <= frame <= 167 and ncols == 2:
        return "contents2"
    if 9 <= frame <= 43:
        return {7: "cities7", 10: "cities10"}.get(ncols)
    if 44 <= frame <= 71:
        if ncols == 3:
            return "names3"
        if ncols == 10:
            return "coords10"
    return None


def row_tex(cells, frame, tex):
    spans = []
    for c in cells:
        m = re.match(r"(.*)\^(\d)$", c)
        spans.append((m.group(1).strip(), int(m.group(2))) if m else (c, 1))
    n = sum(s for _, s in spans)
    sch = scheme(frame, n, cells[0])
    if sch is None:
        raise SystemExit(f"frame {frame}: a row of {n} columns has no table layout: {' | '.join(cells)[:80]}")
    widths, out, k = COLS[sch], [], 0
    for c, s in spans:
        w = sum(widths[k:k + s])
        name = sch in ("cities7", "cities10", "names3") and k == 2 or sch == "contents2" and k == 0
        numeral = re.fullmatch(r"[\d/⟨⟩\[\]() ]*(?:\[\^n\])?", c) is not None
        align = r"\raggedright" if name or not numeral and sch != "coords10" else r"\centering"
        if s > 1 or (sch == "coords10" and k >= 8):
            align = r"\centering"
        body = tex(c).replace("/", r"/\allowbreak{}") if numeral else tex(c)
        if not numeral and not name and s == 1 and not (sch == "coords10" and k >= 8):
            body = r"{\footnotesize " + body + "}"   # the heads «degrees», «minutes» in the narrow columns
        out.append(r"\parbox[t]{" + f"{w:g}" + r"mm}{" + align + r"\strut " + body + r"\strut}")
        k += s
    return "".join(out)


def render(blocks, rows):
    frame_of = {a: f for a, f, _p, _k, _t in rows}
    page_of = {}
    for a, f, p, _k, _t in rows:
        page_of.setdefault(f, p)
    text_of = {a: t for a, _f, _p, _k, t in rows}
    body, last_frame = [], None

    def pmark(f):
        p = page_of.get(f, "-")
        return r"\Pg{p. " + p + "}" if p != "-" else ""

    for b in blocks:
        frames = sorted({frame_of[a] for a in b["anchors"]})
        notes = list(b["notes"])
        rownotes = []

        def tex(text, inrow=False):
            parts = re.split(r"(\[\^n\])", text)
            out = []
            for part in parts:
                if part == "[^n]":
                    note = inline(notes.pop(0))
                    if inrow:
                        out.append(r"\footnotemarkT{}")
                        rownotes.append(note)
                    else:
                        out.append(r"\footnoteT{" + note + "}")
                else:
                    out.append(inline(part))
            return "".join(out)

        first = frames[0]
        if first in TITLE_FRAMES and first != last_frame:
            body.append(r"\clearpage")
        mark = pmark(first) if first != last_frame else ""
        if b["kind"] == "p":
            paras = [[]]
            for line in b["text"]:
                if line.strip():
                    paras[-1].append(line.strip())
                elif paras[-1]:
                    paras.append([])
            paras = [" ".join(p) for p in paras if p]
            # where a page of the edition ends inside the block: after the last point of that page
            joined = "\n\n".join(paras)
            for f in frames[1:]:
                prev = [a for a in b["anchors"] if frame_of[a] == f - 1] or \
                       [a for a in b["anchors"] if frame_of[a] < f]
                nums = re.findall(r"\(([٠-٩]+(?:/[٠-٩]+)?)\)", " ".join(text_of[a] for a in prev))
                placed = False
                if nums:
                    n = nums[-1].translate(AR)
                    m = re.search(r"\(" + re.escape(n) + r"\)(?:\[\^n\])?(?: \[[\d –]+\])?(?:\[\^n\])?", joined)
                    if m:
                        joined = joined[:m.end()] + f"⁅{f}⁆" + joined[m.end():]
                        placed = True
                if not placed:   # the page ends inside the first point of the block: at the head of its paragraph
                    later = [a for a in b["anchors"] if frame_of[a] == f]
                    nums = re.findall(r"\(([٠-٩]+(?:/[٠-٩]+)?)\)", " ".join(text_of[a] for a in later))
                    m = re.search(r"\(" + re.escape(nums[0].translate(AR)) + r"\)", joined) if nums else None
                    if not m:
                        raise SystemExit(f"{b['spec']}: no place for the mark of frame {f}")
                    start = joined.rfind("\n\n", 0, m.start())
                    start = 0 if start < 0 else start + 2
                    joined = joined[:start] + f"⁅{f}⁆" + joined[start:]
                    fallback.append(f"{b['spec']} p. {page_of[f]}")
            texts = []
            for para in joined.split("\n\n"):
                pieces = re.split(r"⁅(\d+)⁆", para)
                t = ""
                for k, piece in enumerate(pieces):
                    t += tex(piece) if k % 2 == 0 else pmark(int(piece))
                texts.append(t)
            texts[0] = mark + texts[0]
            body.append("\n\n".join(texts))
        elif b["kind"] == "r":
            cells = [c.strip() for c in " ".join(b["text"]).split("|")]
            gap = r"\medskip" if first != last_frame else ""   # a table continued on the facing page
            line = gap + r"\par\noindent" + mark + r"{\small " + row_tex(cells, first, lambda c: tex(c, True)) + r"}\par"
            for note in rownotes:
                line += r"\footnotetextT{" + note + "}"
            body.append(line)
        elif b["kind"] == "h":
            t = tex(" ".join(b["text"]).strip())
            body.append(r"\par\medskip\begin{center}" + mark + r"\bfseries " + t + r"\end{center}\pdfbookmark[1]{" +
                        re.sub(r"[\\{}]|textarabic", "", t)[:60] + "}{" + b["spec"] + r"}\par")
        else:
            t = tex(" ".join(b["text"]).strip())
            size = r"\large " if first in TITLE_FRAMES else ""
            body.append(r"\begin{center}" + mark + size + t + r"\end{center}")
        last_frame = frames[-1]
        if notes:
            raise SystemExit(f"{b['spec']}: notes left over")
    return PREAMBLE + "\n\n".join(body) + "\n" + END


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,top=25mm,bottom=25mm,left=26mm,right=34mm,marginparwidth=16mm,marginparsep=5mm]{geometry}
\usepackage{fontspec,polyglossia,bigfoot,perpage}
\usepackage[unicode,hidelinks]{hyperref}
\setmainlanguage{english}\setotherlanguage{arabic}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\arabicfont{Amiri}[Script=Arabic]
\hypersetup{pdftitle={al-Khwarizmi, The Book of the Image of the Earth: English translation},pdfauthor={Muhammad ibn Musa al-Khwarizmi}}
\DeclareNewFootnote{T}[alph]
\MakePerPage{footnoteT}
\makeatletter
\newcommand{\TNoteLetter}[1]{\ifnum#1>26 \@alph{\numexpr(#1-14)/26\relax}\@alph{\numexpr#1-26*((#1-14)/26)\relax}\else\@alph{#1}\fi}
\renewcommand{\thefootnoteT}{\TNoteLetter{\value{footnoteT}}}
\makeatother
\newcommand{\Pg}[1]{\marginpar{\footnotesize #1}}
\newcommand{\Ang}[1]{\ensuremath{#1}}
\newcommand{\AngOpen}{\ensuremath{\rangle}}
\newcommand{\AngClose}{\ensuremath{\langle}}
\newcommand{\Zero}{\ensuremath{\bar{\mathrm{o}}}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.45em}\setlength{\emergencystretch}{3em}
\tracinglostchars=2
\pagestyle{plain}
\begin{document}
\begin{center}{\LARGE al-Khwārizmī}\\[3mm]
{\Large \textit{The Book of the Image of the Earth}}\\[2mm]
{\large (\textit{Kitāb ṣūrat al-arḍ})}\\[4mm]
English translation of the Arabic text in the edition of Hans von Mžik\\
(Leipzig: Otto Harrassowitz, 1926; reprinted Baghdad, 1962)\end{center}
\medskip
{\small Every line of the edition is translated, in its order, from the line-by-line transcription in this repository
(\texttt{../anchors.tsv}): the title pages, the headings, the tables of the cities and of the mountains, the
descriptions of the seas, the islands, the boundaries of the countries and the rivers, and the index. The pages of the
edition stand in the margin; where a page ends inside a paragraph, the mark follows the last point of the page. As in
the edition, the names of the mountains stand on one page and their coordinates, row by row in the same order, on the
next; the headings of these tables run across both pages, and their halves are marked with \dots.

The numerals of al-Khwārizmī, letters with their abjad values, are given as figures, in degrees and minutes. Two
letters without their dots allow more than one value (\textarabic{ڡ} 80 or 100; \textarabic{ٮ} 2, 10 or 50). Where the
neighbouring points of the same entry, or else of the next entries, decide clearly between the readings, the nearest
is given; in the tables of the cities and in the headings of the climes, the band of the clime decides the latitude. Otherwise every value is given, as
88/108\textdegree. A group of letters that is no abjad number stays in Arabic letters. Most names stand in Arabic
letters, as the edition prints them; familiar ones are given in transliteration or in their English form.

The edition's apparatus: its running numbers stand in parentheses; the numbers in square brackets are those of the
same items in Suhrāb's \textit{ʿAjāʾib al-aqālīm al-sabʿa}, as Mžik gives them; angle brackets enclose what Mžik
supplies. Where his supplement begins or ends inside a word, the brackets stand on the whole words it covers; a
supplement within a single word is not marked. A figure that Mžik supplies wholly or in part stands in angle
brackets. Obvious misprints of the running numbers and of the brackets are corrected. Mžik's note marks are not
reproduced, and his German introduction and footnotes are not translated: they are his own writing, protected until
the end of 2031. The lettered footnotes are the translator's: they record misprints of al-Khwārizmī's text, the
editor's corrections of it that the translation follows (his additions and corrections, p.~163), and readings that
stay open. The qualifier \textit{mukhayyar} (\textarabic{مخيّر}) of some colours of the mountains is left
untranslated; its sense here is not certain.

AI-translated (Claude), 2026, from the transcription in this repository; no person has proofread it.
al-Khwārizmī's text is in the public domain. To the extent that any rights exist in this AI-produced translation,
they are dedicated to the public domain under CC0 1.0. The dedication does not concern Mžik's edition or its German
matter.}
\bigskip

"""
END = r"\end{document}" + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = anchors()
    order = {a: k for k, (a, *_r) in enumerate(rows)}
    blocks = parse()
    errors, nxt = [], 0
    for b in blocks:
        a, _, z = b["spec"].partition("..")
        a, z = PREFIX + a, PREFIX + (z or a)
        if a not in order or z not in order or order[z] < order[a]:
            errors.append(f"bad range {b['spec']}")
            continue
        if order[a] != nxt:
            errors.append(f"block {b['spec']} does not follow the block before (expected {rows[nxt][0]})")
        b["anchors"] = [rows[k][0] for k in range(order[a], order[z] + 1)]
        nxt = order[z] + 1
        text = "\n".join(b["text"])
        n = text.count("[^n]")
        if n != len(b["notes"]):
            errors.append(f"block {b['spec']}: {n} [^n] marks, {len(b['notes'])} notes")
        for bad in ("⟪", "⟫", "{de:", "{la:", "\t"):
            if bad in text:
                errors.append(f"block {b['spec']}: draft mark {bad!r} left")
        for para in re.split(r"\n\s*\n", text):
            if para.count("⟨") != para.count("⟩"):
                errors.append(f"block {b['spec']}: angle brackets do not pair: {para[:60]}")
    if nxt != len(rows):
        errors.append(f"lines without English from {rows[nxt][0]}")
    if errors:
        raise SystemExit("\n".join(errors))
    tex = render(blocks, rows)
    (HERE / "surat_en.tex").write_text(tex, encoding="utf-8", newline="\n")
    with open(HERE / "alignment.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("block\tkind\tfirst_anchor\tlast_anchor\tlines\twords\n")
        for k, b in enumerate(blocks, 1):
            words = len(re.findall(r"\w+", " ".join(b["text"])))
            f.write(f"{k}\t{b['kind']}\t{b['anchors'][0]}\t{b['anchors'][-1]}\t{len(b['anchors'])}\t{words}\n")
    for run in (1, 2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "surat_en.tex"], cwd=HERE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise SystemExit("XeLaTeX failed:\n" + r.stdout[-3000:])
    log = (HERE / "surat_en.log").read_text(encoding="utf-8", errors="replace")
    miss = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
    over = len(re.findall(r"Overfull \\hbox", log))
    for ext in ("aux", "log", "out"):
        (HERE / f"surat_en.{ext}").unlink(missing_ok=True)
    words = sum(len(re.findall(r"\w+", " ".join(b["text"] + b["notes"]))) for b in blocks)
    notes = sum(len(b["notes"]) for b in blocks)
    print(f"{len(rows)} lines in {len(blocks)} blocks, {words} words, {notes} translator's notes; overfull lines: "
          f"{over}; missing characters: {''.join(miss) or 'none'}; page marks at the head of a paragraph: "
          f"{'; '.join(fallback) or 'none'}")
    if miss:
        raise SystemExit(1)


main()
