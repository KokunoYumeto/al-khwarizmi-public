"""Die astronomischen Tafeln des Muhammed ibn Musa al-Khwarizmi in der Bearbeitung des Maslama ibn Ahmed al-Madjriti
und der latein. Uebersetzung des Athelhard von Bath, ed. H. Suter on the preliminary work of A. Bjornbo and R. Besthorn
(Copenhagen: A. F. Host, 1914; D. Kgl. Danske Vidensk. Selsk. Skrifter, 7. Raekke, hist. og filos. Afd. III. 1), the copy
of the Wellcome Library scanned by the Internet Archive (b24872489, 296 JP2 images): the line-anchored transcription of
the images, one line of this edition for each printed line.

The Arabic Zij al-Sindhind of al-Khwarizmi is lost. Suter's book edits a derivative line of it: the recension of
Maslama al-Majriti in the Latin translation ascribed to Adelard of Bath. Its Latin text and tables (the recension) and
Suter's German matter (foreword, introduction, commentary, corrections, glossary, index) are kept apart: the pages of
the Latin recension go to tafeln_1914_latin.tex, Suter's German pages and the pages without text to
tafeln_1914_suter.tex. Suter (d. 1922), Bjornbo (d. 1911) and Besthorn: the edition is in the public domain; this
transcription is dedicated to the public domain (CC0 1.0).

Page files (pages/AK07-J####.txt, one per JP2 image, #### the JP2 index 0000-0295):
  @page JP2 PRINTED     the JP2 index and the page number as printed (- none)
  @kind KIND            text, title, contents, divider (a part title), blank, provenance (copy matter only), binding,
                        scan (matter of the digitisation: colour card, notice)
  @lang la|de           the language of the page's printed lines (text, title, contents, divider pages)
  % ...                 a comment (kept in the record)
  TEXT                  a printed line; prefixes "@h " a heading, "@c " a centred line, "@p " a line with a paragraph
                        indent, "@r " a line set to the right
  @toc TITLE | PAGES [| TABLES]   a line of the contents: its title, its pages and (in the chapters of the
                        commentary) the numbers of its tables
  @t CELL | CELL | ...  a row of a printed table, its cells from left to right (the | is ours, not printed)
  @tw W W ...           the relative widths of the columns of the @t rows that follow, one for each cell, until the
                        next @tw (without it the columns are equal); a cell followed by empty cells takes their
                        widths too. Options before the widths: size=footnotesize|scriptsize (the type of the cells,
                        small by default) and span=F (the share of the line width the table takes, 0.98 by
                        default; above 1 a wide table runs into the right margin)
  @cl TEXT, @cr TEXT    a line of the left or the right column of a passage printed in two columns; the left column
                        is transcribed first, then the right
  @n TEXT               a printed line of the footnotes (anchored N01, N02, ...)
  @m TEXT               a note printed in the right margin beside the next line (folios of the manuscripts);
  @ml TEXT              the same in the left margin
  inline: {i:...} italic; {b:...} bold; {sf:...} the bold sans serif of the headings; {sc:...} small capitals;
          {sp:...} letter-spaced (gesperrt); {sup:...} raised (the note numbers, «1)»); {sub:...} lowered (M₁);
          {ov:...} a bar over letters or figures (the thousands of a Roman numeral, the barred zero);
          {ul:...} a bar under a figure (Suter's sign of a negative day, p. 84);
          {st:LABEL|VALUE} a value with a small label printed above it (the units s, g, p, m of the readings);
          {fr:NUM|DEN} a fraction printed built up, the numerator over the denominator (Suter's formulae);
          {cf:NUM|DEN} a case fraction, small figures over a bar within the line (5⅞, 33½″);
          {rt:...} a square root, the radical sign with its bar over what stands under it;
          {sk:TOP|BOTTOM} two words in small type set one over the other within the line, without a bar
          (the heading of a column of a table, «Gemini» over «Sagittar.», quoted in the text)
  a space before ; : ? ! stands for the thin space that the edition sets there; it is kept as U+2009 THIN SPACE
  ∢                     the angle sign of Suter's geometry (set from the mathematical fonts: Linux Libertine lacks it)
  ∽                     (U+223D) the sign of approximate equality, an S lying on its side (from the mathematical fonts)
  ∶                     (U+2236 RATIO) the colon of a ratio or a proportion, «FB ∶ BE», which the edition sets with a
                        space on either side; the spaces around it stay spaces (not the thin space of the colon)
  @variant TEXT         a reading of a manuscript reported by the editor (in our words)
  @unres TEXT           an unresolved reading
  @obs TEXT             an observation on the print
  @copy TEXT            copy matter (bookplate, stamps, shelfmarks, notes in pencil): recorded, not part of the edition
  @critical ID | CLASS | Lnn | PRINTED | PROPOSED | EVIDENCE | CONFIDENCE | IMPACT   a critical note (layer 3)
Writes tafeln_1914_latin.tex, tafeln_1914_suter.tex, records/AK07-J####.json and the ledgers. python build_tafeln.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FRAMES = ROOT / "_intake" / "zij" / "frames"
INVENTORY = ROOT / "controls" / "zij_1914" / "ZIJ_FRAME_INVENTORY.tsv"
TOTAL = 296
THIN = " "         # the thin space before ; : ? !
KINDS = ("text", "title", "contents", "divider", "blank", "provenance", "binding", "scan")
ROLE = {("text", "la"): "RECENSION_LATIN (the Latin text; the editor's page heads, chapter numbers, margin folios and "
                        "apparatus are MODERN_EDITORIAL)",
        ("text", "de"): "MODERN_EDITORIAL (Suter's German text)",
        ("title", "de"): "MODERN_EDITORIAL (title page)", ("contents", "de"): "MODERN_EDITORIAL (contents)",
        ("divider", "de"): "MODERN_EDITORIAL (part title)", ("divider", "la"): "MODERN_EDITORIAL (part title)",
        ("blank", None): "blank", ("provenance", None): "COPY_PROVENANCE", ("binding", None): "COPY_PROVENANCE (binding)",
        ("scan", None): "SCAN_EXTRINSIC"}
LABEL = {"title": "title page", "blank": "blank", "provenance": "library matter", "binding": "binding",
         "scan": "matter of the digitisation", "contents": "contents", "divider": "part title"}
LINE_KINDS = {"@h": "heading", "@c": "centre", "@p": "indent", "@r": "right", "@cl": "column-left",
              "@cr": "column-right"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}").replace("~", r"\~{}")
            .replace("^", r"\^{}").replace(THIN, r"\,").replace("⟨", r"\ensuremath{\langle}")
            .replace("⟩", r"\ensuremath{\rangle}").replace("∢", r"\ensuremath{\sphericalangle}")
            .replace("∽", r"\ensuremath{\backsim}"))


def groups(s):
    """the markup of a text as a list of plain strings and (kind, content) pairs"""
    out, i, plain = [], 0, ""
    while i < len(s):
        m = re.match(r"\{(i|b|sf|sc|sp|sup|sub|ov|ul|st|fr|cf|rt|sk):", s[i:])
        if not m:
            plain += s[i]
            i += 1
            continue
        depth, j = 1, i + m.end()
        while depth:
            if j >= len(s):
                raise SystemExit(f"unclosed markup: {s[i:i + 40]}")
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            j += 1
        if plain:
            out.append(plain)
            plain = ""
        out.append((m.group(1), s[i + m.end():j - 1]))
        i = j
    if plain:
        out.append(plain)
    return out


def split_top(s):
    """the cells of a table row: s divided at each | outside the markup ({cf:1|12} stays one cell)"""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += {"{": 1, "}": -1}.get(ch, 0)
        if ch == "|" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def stacked(content):
    """the two parts of {st:LABEL|VALUE}, {fr:NUM|DEN} or {sk:TOP|BOTTOM}, divided at the first | outside
    nested markup"""
    depth = 0
    for k, ch in enumerate(content):
        depth += {"{": 1, "}": -1}.get(ch, 0)
        if ch == "|" and depth == 0:
            return content[:k], content[k + 1:]
    raise SystemExit(f"a stacked value or fraction needs A|B: {content[:40]}")


def flat(s):
    """the letters of a text without the markup (a stacked value as VALUE[LABEL])"""
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(g)
        elif g[0] == "st":
            label, value = stacked(g[1])
            out.append(flat(value) + "[" + flat(label) + "]")
        elif g[0] in ("fr", "cf"):
            num, den = stacked(g[1])
            out.append("(" + flat(num) + ")/(" + flat(den) + ")")
        elif g[0] == "rt":
            out.append("√(" + flat(g[1]) + ")")
        elif g[0] == "sk":
            top, bottom = stacked(g[1])
            out.append(flat(top) + "/" + flat(bottom))
        elif g[0] == "ul":
            out.append("".join(ch + "̲" for ch in flat(g[1])))
        else:
            out.append(flat(g[1]))
    return "".join(out)


def latex(s):
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(esc(g))
        elif g[0] == "st":
            label, value = stacked(g[1])
            out.append(r"\Stk{" + latex(label) + "}{" + latex(value) + "}")
        elif g[0] == "fr":
            num, den = stacked(g[1])
            out.append(r"\Frac{" + latex(num) + "}{" + latex(den) + "}")
        elif g[0] == "cf":
            num, den = stacked(g[1])
            out.append(r"\CaseFrac{" + latex(num) + "}{" + latex(den) + "}")
        elif g[0] == "rt":
            out.append(r"\Root{" + latex(g[1]) + "}")
        elif g[0] == "sk":
            top, bottom = stacked(g[1])
            out.append(r"\SmallStack{" + latex(top) + "}{" + latex(bottom) + "}")
        else:
            macro = {"i": r"\textit{", "b": r"\textbf{", "sf": r"\SansBold{", "sc": r"\textsc{",
                     "sp": r"\Sperr{", "sup": r"\textsuperscript{", "sub": r"\textsubscript{", "ov": r"\Ovl{",
                     "ul": r"\underline{"}[g[0]]
            out.append(macro + latex(g[1]) + "}")
    return "".join(out)


def marked(s, kind):
    out = []
    for g in groups(s):
        if isinstance(g, tuple):
            if g[0] == kind:
                out.append(flat(g[1]))
            out += marked(g[1], kind)
    return out


def parse(path):
    rec = {"frame": None, "printed": None, "kind": "text", "lang": None, "lines": [], "notes": [], "variants": [],
           "unres": [], "obs": [], "copy": [], "critical": [], "comment": []}
    margin = None
    widths, tsize, tspan = None, "small", 0.98
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        if raw.startswith("%"):
            rec["comment"].append(raw[1:].strip())
            continue
        if raw.startswith("@page "):
            _, fr, pr = raw.split()
            rec["frame"], rec["printed"] = int(fr), pr
            continue
        tag = raw.split(" ", 1)[0]
        body = raw[len(tag):].strip()
        if tag == "@kind":
            rec["kind"] = body
        elif tag == "@lang":
            rec["lang"] = body
        elif tag in ("@m", "@ml"):
            margin = (body, "right" if tag == "@m" else "left")
        elif tag == "@n":
            rec["notes"].append({"kind": "note", "text": body, "margin": None})
        elif tag == "@toc":
            f = [x.strip() for x in body.split("|")]
            if len(f) not in (2, 3):
                raise SystemExit(f"{path.name}: a contents line needs a title, pages and tables: {raw[:60]}")
            rec["lines"].append({"kind": "toc", "text": f[0], "pages": f[1], "tables": f[2] if len(f) == 3 else None,
                                 "margin": margin})
            margin = None
        elif tag == "@critical":
            f = [x.strip() for x in body.split("|")]
            if len(f) != 8 or not re.fullmatch(r"[LN]\d\d", f[2]):
                raise SystemExit(f"{path.name}: a critical note needs 8 fields: {raw[:60]}")
            rec["critical"].append(dict(zip(["id", "class", "line", "printed", "proposed", "evidence", "confidence",
                                             "impact"], f)))
        elif tag == "@variant":
            rec["variants"].append(body)
        elif tag == "@unres":
            rec["unres"].append(body)
        elif tag == "@obs":
            rec["obs"].append(body)
        elif tag == "@copy":
            rec["copy"].append(body)
        elif tag in LINE_KINDS:
            rec["lines"].append({"kind": LINE_KINDS[tag], "text": body, "margin": margin})
            margin = None
        elif tag == "@tw":
            widths, tsize, tspan = [], "small", 0.98
            for tok in body.split():
                if tok.startswith("size=") and tok[5:] in ("small", "footnotesize", "scriptsize"):
                    tsize = tok[5:]
                elif tok.startswith("span="):
                    tspan = float(tok[5:])
                else:
                    widths.append(float(tok))
            widths = widths or None
        elif tag == "@t":
            cells = [x.strip() for x in split_top(body)]
            if widths is not None and len(widths) != len(cells):
                raise SystemExit(f"{path.name}: {len(cells)} cells against {len(widths)} widths: {raw[:60]}")
            rec["lines"].append({"kind": "table", "text": " | ".join(cells), "cells": cells, "margin": margin,
                                 "widths": widths, "tsize": tsize, "tspan": tspan})
            margin = None
        elif raw.startswith("@"):
            raise SystemExit(f"{path.name}: unknown line {raw[:40]}")
        else:
            rec["lines"].append({"kind": "text", "text": raw.strip(), "margin": margin})
            margin = None
    if margin is not None:
        raise SystemExit(f"{path.name}: a margin note without a line after it")
    if rec["kind"] not in KINDS:
        raise SystemExit(f"{path.name}: unknown kind {rec['kind']}")
    if rec["kind"] in ("text", "title", "contents", "divider"):
        if rec["lang"] not in ("la", "de"):
            raise SystemExit(f"{path.name}: a {rec['kind']} page needs @lang la or de")
    elif rec["lang"] is not None or rec["lines"] or rec["notes"]:
        raise SystemExit(f"{path.name}: a {rec['kind']} page has no printed lines and no language")
    for ln in rec["lines"] + rec["notes"]:
        ln["text"] = re.sub(r"\s+", " ", ln["text"]).strip()
        # the edition sets a thin space before a colon, semicolon, question mark and exclamation mark
        ln["text"] = re.sub(r" (?=[;:?!])", THIN, ln["text"])
        if ln.get("cells"):
            # the cells of a table row, from which the PDF sets the row, keep the same thin spaces
            ln["cells"] = [re.sub(r" (?=[;:?!])", THIN, c) for c in ln["cells"]]
    return rec


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,left=30mm,right=34mm,top=22mm,bottom=22mm]{geometry}
\usepackage{amssymb}
\usepackage{fontspec,needspace,xcolor}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{latin,german}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\SansFont{Linux Biolinum O}
\newcommand{\SansBold}[1]{{\SansFont\bfseries #1}}
\newcommand{\Sperr}[1]{{\addfontfeature{LetterSpace=15}#1}}
% a bar over letters or figures ({ov:...} in the page files): the thousands of a Roman numeral, the barred zero
\newcommand{\Ovl}[1]{\ensuremath{\overline{\mbox{#1}}}}
% a value with a small label printed above it ({st:LABEL|VALUE} in the page files)
\newcommand{\Stk}[2]{\begin{tabular}[b]{@{}c@{}}{\tiny #1}\\[-3pt]#2\end{tabular}}
% a fraction printed built up ({fr:NUM|DEN} in the page files)
\newcommand{\Frac}[2]{\ensuremath{\displaystyle\frac{\mbox{#1}}{\mbox{#2}}}}
% a case fraction, small figures over a bar within the line ({cf:NUM|DEN} in the page files)
\newcommand{\CaseFrac}[2]{\ensuremath{\textstyle\frac{\mbox{\scriptsize #1}}{\mbox{\scriptsize #2}}}}
% a square root, the radical sign with its bar over the radicand ({rt:...} in the page files)
\newcommand{\Root}[1]{\ensuremath{\sqrt{\mbox{#1}}}}
% two words in small type one over the other within the line ({sk:TOP|BOTTOM} in the page files)
\newcommand{\SmallStack}[2]{\begin{tabular}[c]{@{}c@{}}\footnotesize #1\\[-4pt]\footnotesize #2\end{tabular}}
\hypersetup{pdftitle={@TITLE@},pdfauthor={ed. H. Suter (Copenhagen 1914)}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\tracinglostchars=2
\newcommand{\FrameHead}[4]{\par\bigskip\Needspace{8\baselineskip}\penalty-300\pdfbookmark[1]{JP2 #1 (#2)}{fr-#1}\hypertarget{AK07-J#3}{}%
 {\large\bfseries #4}\enspace{\footnotesize\color{gray}JP2 #1}\par\smallskip}
\newcommand{\LnStrut}{\vrule height 0.95em depth 0.35em width 0pt}
% a note in the right or the left margin: the folios of the manuscripts
\newcommand{\Marg}[1]{\rlap{\hspace{\linewidth}\hspace{3mm}\footnotesize\color{gray}#1}}
\newcommand{\MargL}[1]{\llap{\footnotesize\color{gray}#1\hspace{12mm}}}
% one printed line, with its number in the left margin
\newcommand{\EdL}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\raggedright\LnStrut #3\par}\par}
\newcommand{\EdLp}[4]{\EdL{#1}{#2}{\hspace*{6mm}#3}{#4}}
\newcommand{\EdLr}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\raggedleft\LnStrut #3\par}\par}
\newcommand{\EdLc}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\centering\LnStrut #3\par}\par}
\newcommand{\EdLh}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\centering\large\LnStrut #3\par}\par\smallskip}
% a line of the contents: the title with its leader, the pages, and (in the chapters of the commentary) the tables
\newcommand{\EdLt}[6]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#6\parbox[t]{\dimexpr\linewidth-30mm}{\LnStrut #3\dotfill\par}\makebox[12mm][r]{#4}\makebox[18mm][c]{#5}\par}
\newcommand{\EdLtp}[5]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#5\parbox[t]{\dimexpr\linewidth-30mm}{\LnStrut #3\dotfill\par}\makebox[30mm][r]{#4}\par}
\newcommand{\ColHead}[1]{\par\smallskip\noindent{\footnotesize\color{gray}#1}\par}
% a printed line of the footnotes
\newcommand{\EdN}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\raggedright\footnotesize\LnStrut #3\par}\par}
\newcommand{\NoteRule}{\par\smallskip\noindent\rule{30mm}{0.4pt}\par}
\newcommand{\Withheld}[1]{\par\smallskip{\small\color{gray}[#1]}\par}
\begin{document}
"""

ABOUT = (
    r"\noindent The Arabic \textit{Zīj al-Sindhind} of Muḥammad ibn Mūsā al-Khwārizmī is lost. Suter’s book edits a "
    r"derivative line of it: the recension of Maslama ibn Aḥmad al-Majrīṭī, in the Latin translation ascribed to "
    r"Adelard of Bath (twelfth century). It is not al-Khwārizmī’s text. The book is transcribed in two files: the Latin text and tables of the recension, with "
    r"the editor’s apparatus, and Suter’s German matter, his foreword, introduction, commentary, corrections, "
    r"glossary and index, with the pages that carry no text.")
METHOD = (
    r"\par\smallskip\noindent Every printed line of the book is one line here, in the order of the images of the "
    r"Wellcome copy (Internet Archive b24872489), with its number in the margin and its anchor "
    r"AK07-J\#\#\#\#-L\#\# (JP2 image, line); the lines of the footnotes follow below a short rule with the anchors "
    r"N\#\#. The text is transcribed letter for letter as printed, with its punctuation, italics and spaced type, and "
    r"the words divided at the ends of the lines. The folios of the manuscripts that the edition prints in the margin "
    r"are set in the margin. Bookplates, stamps, shelfmarks and notes written in this copy are recorded in the page "
    r"records, not reproduced. Where the print is in error, the transcription keeps it; the critical notes at the "
    r"end, which are not part of the transcription, propose the correction.")
LICENCE = (
    r"\par\smallskip\noindent The Latin text and Suter’s edition are in the public domain, and this transcription is "
    r"dedicated to the public domain (CC0 1.0). It is AI-integrated work (Claude); no person has proofread it. ")


def front(which, n_text, n_notes, n_frames):
    sub = {"latin": "the Latin text and tables of the recension, line by line",
           "suter": "the editor’s German matter and the pages without text, line by line"}[which]
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\LARGE Die astronomischen Tafeln des Muḥammed ibn Mūsā al-Khwārizmī\par\vspace{3mm}"
        r"\large in der Bearbeitung des Maslama ibn Aḥmed al-Madjrīṭī und der lateinischen Uebersetzung des "
        r"Athelhard von Bath\par\vspace{4mm}"
        r"\normalsize edited by H. Suter on the preliminary work of A. Bjørnbo and R. Besthorn\\"
        r"(Copenhagen: A. F. Høst \& Søn, 1914)\par"
        r"\vspace{3mm}the Wellcome Library copy, Internet Archive b24872489, JP2 images 0000–0295\par"
        r"\vspace{4mm}\large " + sub + r"\end{center}\vspace{6mm}",
        ABOUT, METHOD, LICENCE +
        rf"This file holds {n_text} printed lines and {n_notes} lines of the footnotes from {n_frames} images."
        r"\par\clearpage"])


def render(r, fid, label, tex, anchors, records_lines):
    fr = r["frame"]
    tex.append(r"\FrameHead{" + f"{fr:04d}" + "}{" + esc(label) + "}{" + f"{fr:04d}" + "}{" + esc(label) + "}")
    col = None
    for k, ln in enumerate(r["lines"], 1):
        aid = f"{fid}-L{k:02d}"
        marg = ""
        if ln["margin"]:
            text, side = ln["margin"]
            marg = (r"\Marg{" if side == "right" else r"\MargL{") + latex(text) + "}"
        if ln["kind"] in ("column-left", "column-right"):
            if col != ln["kind"]:
                tex.append(r"\ColHead{" + ("left column" if ln["kind"] == "column-left" else "right column") + "}")
                col = ln["kind"]
        elif col is not None:
            tex.append(r"\ColHead{full width}")
            col = None
        if ln["kind"] == "toc" and ln["tables"] is None:
            tex.append(r"\EdLtp{" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}{" + latex(ln["pages"]) + "}{" +
                       marg + "}")
        elif ln["kind"] == "toc":
            tex.append(r"\EdLt{" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}{" + latex(ln["pages"]) + "}{" +
                       latex(ln["tables"] or "") + "}{" + marg + "}")
        elif ln["kind"] == "table":
            # equal columns, or the widths of @tw; a cell followed by empty cells (a head that spans them) takes their
            # width too
            w = ln.get("widths") or [1.0] * len(ln["cells"])
            groups = []
            for c, wi in zip(ln["cells"], w):
                if c or not groups:
                    groups.append([c, wi])
                else:
                    groups[-1][1] += wi
            unit = ln.get("tspan", 0.98) / sum(w)
            # \mbox{} makes an empty cell a line of the full width (an empty \parbox would have no width); each cell
            # keeps 0.5em clear at its right, so that the text of a full cell does not run into the next one
            size = "\\" + ln.get("tsize", "small")
            cells = "".join(r"\parbox[t]{\dimexpr" + f"{unit * n:.4f}" + r"\linewidth-0.5em\relax}{\raggedright" + size +
                            r"\mbox{}" + latex(c) + r"}\hspace{0.5em}" for c, n in groups)
            if ln.get("tspan", 0.98) > 0.98:
                # a table wider than the line: one unbreakable box, which runs on into the right margin
                cells = r"\mbox{" + cells + "}"
            tex.append(r"\EdL{" + str(k) + "}{" + aid + "}{" + cells + "}{" + marg + "}")
        else:
            macro = {"text": r"\EdL", "indent": r"\EdLp", "centre": r"\EdLc", "heading": r"\EdLh", "right": r"\EdLr",
                     "column-left": r"\EdL", "column-right": r"\EdL"}[ln["kind"]]
            tex.append(macro + "{" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}{" + marg + "}")
        full = ln["text"] + (" | " + ln["pages"] + (" | " + ln["tables"] if ln["tables"] else "")
                             if ln["kind"] == "toc" else "")
        anchors.append((aid, fr, r["printed"], f"L{k:02d}", ln["kind"], full,
                        (ln["margin"][0] + (" (left margin)" if ln["margin"][1] == "left" else "")) if ln["margin"]
                        else ""))
        records_lines.append({"id": aid, "n": k, "kind": ln["kind"], "text": ln["text"], "cells": ln.get("cells"),
                              "pages": ln.get("pages"), "tables": ln.get("tables"), "margin": ln["margin"][0] if ln["margin"] else None,
                              "margin_side": ln["margin"][1] if ln["margin"] else None,
                              "plain": flat(ln["text"]), "italic": marked(ln["text"], "i"),
                              "small_caps": marked(ln["text"], "sc"), "spaced": marked(ln["text"], "sp"), "bold": marked(ln["text"], "b") +
                              marked(ln["text"], "sf")})
    if r["notes"]:
        tex.append(r"\NoteRule")
    for k, ln in enumerate(r["notes"], 1):
        aid = f"{fid}-N{k:02d}"
        tex.append(r"\EdN{N" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}")
        anchors.append((aid, fr, r["printed"], f"N{k:02d}", "note", ln["text"], ""))
        records_lines.append({"id": aid, "n": k, "kind": "note", "text": ln["text"], "margin": None,
                              "plain": flat(ln["text"]), "italic": marked(ln["text"], "i"),
                              "small_caps": marked(ln["text"], "sc"), "spaced": marked(ln["text"], "sp"), "bold": marked(ln["text"], "b") +
                              marked(ln["text"], "sf")})
    if r["kind"] == "blank":
        tex.append(r"\Withheld{blank}")
    elif r["kind"] in ("provenance", "binding", "scan"):
        what = {"provenance": "library matter only", "binding": "the binding",
                "scan": "matter of the digitisation"}[r["kind"]]
        tex.append(r"\Withheld{" + what + ": " + esc("; ".join(r["copy"] + r["obs"][:1])) + "}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inv = {int(r["jp2_index"]): r for r in csv.DictReader(open(INVENTORY, encoding="utf-8"), delimiter="\t")}
    pages = sorted((HERE / "pages").glob("AK07-J*.txt"))
    recs = [parse(p) for p in pages]
    frames = [r["frame"] for r in recs]
    assert frames == list(range(0, len(frames))), "images not continuous from 0000"
    for p, r in zip(pages, recs):
        if p.name != f"AK07-J{r['frame']:04d}.txt":
            raise SystemExit(f"{p.name}: the @page line names image {r['frame']}")
        data = (FRAMES / inv[r["frame"]]["reading_copy"]).read_bytes()
        if sha(data).upper() != inv[r["frame"]]["reading_copy_sha256"].upper():
            raise SystemExit(f"image {r['frame']}: the reading copy is not the inventory's")
    tex = {"latin": [], "suter": []}
    anchors, disp, evid, unres, variants, copyrows, crit = [], [], [], [], [], [], []
    count = {"latin": [0, 0, 0], "suter": [0, 0, 0]}
    (HERE / "records").mkdir(exist_ok=True)
    for r in recs:
        fr = r["frame"]
        fid = f"AK07-J{fr:04d}"
        which = "latin" if r["lang"] == "la" else "suter"
        label = f"p. {r['printed']}" if r["printed"] != "-" else LABEL.get(r["kind"], "unnumbered")
        out_lines = []
        render(r, fid, label, tex[which], anchors, out_lines)
        count[which][0] += len(r["lines"])
        count[which][1] += len(r["notes"])
        count[which][2] += 1
        for cn in r["critical"]:
            n = int(cn["line"][1:])
            if n > len(r["lines"] if cn["line"][0] == "L" else r["notes"]):
                raise SystemExit(f"{fid}: critical note {cn['id']} on {cn['line']}, which the page does not have")
            crit.append((cn["id"], f"{fid}-{cn['line']}", cn["class"], cn["printed"], cn["proposed"], cn["evidence"],
                         cn["confidence"], cn["impact"], which))
        for o in r["obs"]:
            evid.append((fid, "observation", o))
        for v in r["variants"]:
            variants.append((fid, "Suter edition 1914 | the manuscripts as the editor reports them", v))
        for u in r["unres"]:
            unres.append((fid, u))
        for c in r["copy"]:
            copyrows.append((fid, c))
        role = ROLE[(r["kind"], r["lang"])]
        inv_row = inv[fr]
        disp.append((fid, fr, inv_row["member"], inv_row["sha256"].lower(), inv_row["reading_copy"],
                     inv_row["reading_copy_sha256"].lower(), r["printed"], r["kind"], r["lang"] or "", role,
                     len(r["lines"]), len(r["notes"]), which,
                     "transcribed" if r["kind"] in ("text", "title", "contents", "divider") else
                     ("recorded, not reproduced" if r["kind"] in ("provenance", "binding", "scan") else "recorded")))
        out = {"anchor": fid, "jp2_index": fr, "jp2_member": inv_row["member"], "jp2_sha256": inv_row["sha256"].lower(),
               "reading_copy": inv_row["reading_copy"], "reading_copy_sha256": inv_row["reading_copy_sha256"].lower(),
               "printed_page": r["printed"], "kind": r["kind"], "language": r["lang"], "role": role, "file": which,
               "comment": " ".join(r["comment"]), "lines": out_lines, "variants": r["variants"],
               "unresolved": r["unres"], "observations": r["obs"], "copy_matter": r["copy"],
               "critical_notes": r["critical"]}
        (HERE / "records" / f"{fid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    for which, title in (("latin", "Die astronomischen Tafeln des al-Khwarizmi, ed. Suter 1914: the Latin recension"),
                         ("suter", "Die astronomischen Tafeln des al-Khwarizmi, ed. Suter 1914: the editor's matter")):
        body = [PREAMBLE.replace("@TITLE@", title), front(which, *count[which])] + tex[which]
        mine = [c for c in crit if c[8] == which]
        if mine:
            body.append(r"\clearpage\pdfbookmark[1]{critical notes}{critical}{\large\bfseries Critical notes}\par"
                        r"\medskip\noindent These notes are not part of the transcription. They record errors of the "
                        r"print and propose corrections; the transcription keeps the print.\par\medskip")
            for c in mine:
                body.append(r"\noindent\textbf{" + esc(c[0]) + r"}\enspace\hyperlink{" + c[1] + "}{" + esc(c[1]) +
                            r"}\enspace(" + esc(c[2]) + r")\par\noindent printed: " + latex(c[3]) +
                            r"\enspace proposed: " + latex(c[4]) + r"\par\noindent " + esc(c[5]) +
                            r"\par\noindent confidence: " + esc(c[6]) + r"\par\noindent impact: " + esc(c[7]) +
                            r"\par\medskip")
        if not tex[which]:
            body.append(r"\noindent\textit{No page of this part is transcribed yet.}\par")
        body.append(r"\end{document}")
        (HERE / f"tafeln_1914_{which}.tex").write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")

    def tsv(name, head, rows):
        with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(head) + "\n")
            for row in rows:
                fh.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    tsv("anchors.tsv", ["anchor", "jp2_index", "printed_page", "line", "kind", "text", "margin"], anchors)
    tsv("physical_unit_disposition.tsv", ["anchor", "jp2_index", "jp2_member", "jp2_sha256", "reading_copy",
                                          "reading_copy_sha256", "printed_page", "kind", "language", "role",
                                          "text_lines", "note_lines", "file", "disposition"], disp)
    tsv("evidence_ledger.tsv", ["anchor", "kind", "text"], evid)
    tsv("unresolved_readings.tsv", ["anchor", "reading"], unres)
    tsv("witness_variants.tsv", ["anchor", "witnesses", "variant"], variants)
    tsv("copy_provenance.tsv", ["anchor", "matter"], copyrows)
    tsv("critical_findings.tsv", ["id", "anchor", "issue_class", "diplomatic_reading", "proposed_critical_reading",
                                  "evidence", "confidence", "propagation_impact", "file"], crit)
    tsv("proposed_corrections.tsv", ["anchor", "current_reading", "proposal", "evidence", "confidence", "state"], [])
    tsv("language_synchronization.tsv", ["language", "canonical_checkpoint", "replay_state", "proposals", "state"], [])
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    last = max(frames)
    ck = {"lane": "AK07 Zij, Majriti/Adelard recension (Suter 1914, the Wellcome copy, IA b24872489, 296 JP2 images)",
          "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the page files in order: file name, a NUL byte, the bytes",
          "last_fully_transcribed_source_unit": f"JP2_{last:04d}",
          "last_fully_verified_source_unit": f"JP2_{last:04d}",
          "first_untouched_source_unit": f"JP2_{last + 1:04d}" if last + 1 < TOTAL else None,
          "owned_units_total": TOTAL, "owned_units_disposed": len(recs),
          "unresolved_count": len(unres), "critical_notes": len(crit),
          "latin_lines": count["latin"][0], "latin_note_lines": count["latin"][1],
          "suter_lines": count["suter"][0], "suter_note_lines": count["suter"][1]}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(recs)} images (0000-{last:04d}); Latin: {count['latin'][2]} pages, {count['latin'][0]} lines, "
          f"{count['latin'][1]} note lines; Suter: {count['suter'][2]} pages, {count['suter'][0]} lines, "
          f"{count['suter'][1]} note lines; {len(evid)} observations, {len(copyrows)} copy records, "
          f"{len(crit)} critical notes")


if __name__ == "__main__":
    main()
