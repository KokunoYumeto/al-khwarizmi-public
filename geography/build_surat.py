"""al-Khwarizmi, Kitab surat al-ard, in the edition of Hans von Mzik (Leipzig: Harrassowitz, 1926; Bibliothek arabischer
Historiker und Geographen 3), in the Baghdad reprint of 1962 (Columbia University Libraries G93 .K48, digitised by
Arabic Collections Online, columbia_aco004109, 218 frames): the line-anchored transcription of the frames, one line of
this edition for each printed line or table row of al-Khwarizmi's text. Mzik's German introduction and footnotes are
recorded (where they stand, how many lines) but not reproduced: Hans von Mzik died in 1961, and his own writing is
protected in the EU until the end of 2031. al-Khwarizmi's text is in the public domain; this transcription is
dedicated to the public domain (CC0 1.0).

Page files (pages/AK05-F###.txt, one per frame):
  @page FRAME PRINTED   the frame and the page number as printed (Arabic-Indic digits; - none)
  @kind KIND            text (default), binding, title, blank, provenance (copy matter only), extrinsic (scan or
                        acquisition matter), editorial (Mzik's German matter, described), plate
  % ...                 a comment (kept in the record)
  TEXT                  a printed line; prefixes "@h " a heading (centred, larger), "@c " a centred line, "@p " a line
                        printed with a paragraph indent, "@lc " a centred line in Latin script, left to right (the
                        German title pages and imprints)
  @r C1 | C2 | ...      a table row: its cells as printed, right to left (an empty cell stays empty); "TEXT^4"
                        spans four columns
  @rh C1 | ...          a row of table heads; "TEXT^2" spans two columns
  @cols W1,W2,...       the widths in mm of the table columns, right to left, from this page on
  @align A1,A2,...      the alignment of the table cells, right to left, r (to the right), c (centred) or l, from this
                        page on; a page with @cols and no @align returns to the default (the first three cells r, the
                        others c)
  @m TEXT               a note printed in the margin beside the next line (the folio of the manuscript, "(fol. 2ᵇ)")
  inline: {n:a} a note mark of the editor, set as a superscript; {z} the sign for zero of the numeral tables (a small
          circle with a stroke above it); {b:...} words printed in bold; {ov:...} letters printed with a line above
          them; {u:...} letters printed with a line below them; the angle brackets ⟨ ⟩ with which the editor marks
          what he supplies are written as printed
  @ednotes MARKS LINES [continued]   the editor's footnotes at the foot of the page: their marks and how many printed
                        lines they take, not reproduced
  @withheld TEXT        the editor's text that fills the frame, described, not reproduced
  @fig ID X0 Y0 X1 Y1   a figure or plate: the rectangle of the frame cut out untouched and as a conservative derivative
  @variant TEXT         a reading of the manuscript reported by the editor (in our words)
  @unres TEXT           an unresolved reading
  @obs TEXT             an observation on the print
  @copy TEXT            copy matter (library marks): recorded, not part of the edition
  @critical ID | CLASS | Lnn | PRINTED | PROPOSED | EVIDENCE | CONFIDENCE | IMPACT   a critical note (layer 3)
Writes surat_1962.tex, records/AK05-F###.json and the ledgers (see README.md). python build_surat.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FRAMES = ROOT / "_intake" / "geography" / "frames"
INVENTORY = ROOT / "controls" / "geography_1962" / "10_IMAGE_INVENTORY_SHA256.csv"
AR = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ROLE = {"text": "AK_TEXT (lines and table rows); MODERN_EDITORIAL (the editor's numbers, brackets, note marks and "
                "folio references; his footnotes not reproduced)",
        "binding": "COPY_PROVENANCE (binding)", "title": "MODERN_EDITORIAL (title page)", "blank": "blank",
        "provenance": "COPY_PROVENANCE", "extrinsic": "SCAN_EXTRINSIC",
        "editorial": "MODERN_EDITORIAL (not reproduced)", "plate": "AK_TABLE_OR_FIGURE plus MODERN_EDITORIAL (plate)"}
LABEL = {"binding": "binding", "title": "title page", "blank": "blank", "provenance": "library matter",
         "extrinsic": "acquisition notice", "editorial": "editor's matter", "plate": "plate"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}"))


def groups(s):
    """the markup of a text as a list of plain strings and (kind, content) pairs"""
    out, i, plain = [], 0, ""
    while i < len(s):
        if s.startswith("{z}", i):
            if plain:
                out.append(plain)
                plain = ""
            out.append(("z", ""))
            i += 3
            continue
        m = re.match(r"\{(n|ov|b|u):", s[i:])
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


def flat(s):
    """the letters of a text without the markup (note marks dropped; the zero sign as ō)"""
    return "".join(g if isinstance(g, str) else ("" if g[0] == "n" else ("ō" if g[0] == "z" else flat(g[1])))
                   for g in groups(s))


def plain_tex(s):
    s = esc(s)
    # the editor's angle brackets: the font has none, so they are drawn; in right-to-left text the opening one
    # stands on the right and opens to the left
    return s.replace("⟨", r"\AngOpen{}").replace("⟩", r"\AngClose{}")


def artex(s):
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(plain_tex(g))
        elif g[0] == "z":
            out.append(r"\Zero{}")
        elif g[0] == "n":
            out.append(r"\NoteMark{" + esc(g[1].strip()) + "}")
        else:
            macro = {"ov": r"\Ov{", "b": r"\Bd{", "u": r"\Ul{"}[g[0]]
            out.append(macro + artex(g[1]) + "}")
    return "".join(out)


def marked(s, kind):
    out = []
    for g in groups(s):
        if isinstance(g, tuple) and g[0] not in ("z",):
            if g[0] == kind:
                out.append(flat(g[1]) if kind != "n" else g[1])
            if g[0] != "n":
                out += marked(g[1], kind)
    return out


def mixed(s):
    """an English label with Arabic words: the Arabic runs set right to left in the Arabic font"""
    out, pos = [], 0
    for m in re.finditer(r"[؀-ۿ][؀-ۿ\s]*[؀-ۿ]|[؀-ۿ]", s):
        out.append(esc(s[pos:m.start()]))
        out.append(r"\RL{\ArBody " + esc(m.group(0)) + "}")
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out).replace("⟨", r"\ensuremath{\langle}").replace("⟩", r"\ensuremath{\rangle}")


def cells(body):
    return [c.strip() for c in body.split("|")]


def parse(path):
    rec = {"frame": None, "printed": None, "kind": "text", "lines": [], "ednotes": [], "withheld": [], "figs": [],
           "variants": [], "unres": [], "obs": [], "copy": [], "critical": [], "comment": [], "cols": None,
           "align": None}
    margin = None
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
        elif tag == "@cols":
            rec["cols"] = [float(v) for v in body.split(",")]
        elif tag == "@align":
            rec["align"] = [v.strip() for v in body.split(",")]
            if not all(a in ("r", "c", "l") for a in rec["align"]):
                raise SystemExit(f"{path.name}: @align takes r, c or l: {raw[:60]}")
        elif tag == "@m":
            margin = body
        elif tag == "@ednotes":
            parts = body.split()
            cont = parts[-1] == "continued"
            if cont:
                parts = parts[:-1]
            rec["ednotes"].append({"marks": parts[:-1], "lines": int(parts[-1]), "continued": cont})
        elif tag == "@withheld":
            rec["withheld"].append(body)
        elif tag == "@fig":
            fid, *rest = body.split()
            rec["figs"].append({"id": fid, "rect": [int(v) for v in rest]})
        elif tag == "@critical":
            f = [x.strip() for x in body.split("|")]
            if len(f) != 8 or not re.fullmatch(r"L\d\d", f[2]):
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
        elif tag in ("@h", "@c", "@p", "@r", "@rh", "@lc"):
            kind = {"@h": "heading", "@c": "centre", "@p": "indent", "@r": "row", "@rh": "head", "@lc": "latin"}[tag]
            ln = {"kind": kind, "text": body, "margin": margin}
            if kind in ("row", "head"):
                ln["cells"] = cells(body)
            rec["lines"].append(ln)
            margin = None
        elif raw.startswith("@"):
            raise SystemExit(f"{path.name}: unknown line {raw[:40]}")
        else:
            rec["lines"].append({"kind": "text", "text": raw.strip(), "margin": margin})
            margin = None
    if margin is not None:
        raise SystemExit(f"{path.name}: a margin note without a line after it")
    for ln in rec["lines"]:
        ln["text"] = re.sub(r"\s+", " ", ln["text"]).strip()
    return rec


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,left=26mm,right=30mm,top=22mm,bottom=22mm]{geometry}
\usepackage{fontspec,graphicx,needspace,xcolor,amsmath}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{arabic}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\arabicfont{Amiri}[Script=Arabic]
\newfontfamily\ArBody{Amiri}[Script=Arabic,Scale=1.1,BoldFont={Amiri Bold}]
\newfontfamily\ArHead{Amiri}[Script=Arabic,Scale=1.45]
\hypersetup{pdftitle={al-Khwarizmi, Kitab surat al-ard, ed. Mzik (1926; Baghdad reprint 1962): the text, line by line},pdfauthor={Muhammad ibn Musa al-Khwarizmi}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\tracinglostchars=2
\newcommand{\FrameHead}[4]{\par\bigskip\penalty-300\pdfbookmark[1]{frame #1 (#2)}{fr-#1}\hypertarget{AK05-F#3}{}%
 {\large\bfseries #4}\enspace{\footnotesize\color{gray}frame #1}\par\smallskip}
\newcommand{\ArStrut}{\vrule height 1.1em depth 0.5em width 0pt}
% a note in the right margin (the folio of the manuscript)
\newcommand{\Marg}[1]{\rlap{\hspace{\linewidth}\hspace{3mm}\footnotesize\color{gray}#1}}
% one printed line, right to left, with its number in the left margin
\newcommand{\EdL}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\setRTL\ArBody\raggedleft\ArStrut #3\par}\par}
\newcommand{\EdLp}[4]{\EdL{#1}{#2}{\hspace*{8mm}#3}{#4}}
\newcommand{\EdLc}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\setRTL\ArBody\centering\ArStrut #3\par}\par}
% a centred line in Latin script, left to right
\newcommand{\EdLl}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\centering\ArStrut #3\par}\par}
\newcommand{\EdLh}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\setRTL\ArHead\centering #3\par}\par\smallskip}
% a table row: its cells in boxes of fixed width, right to left
\newcommand{\EdR}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\setRTL\ArBody\raggedleft\ArStrut #3\par}\par}
\newcommand{\Cell}[3]{\makebox[#1mm][#2]{#3}}
\newcommand{\NoteMark}[1]{\textsuperscript{\LR{#1}}}
\newcommand{\Zero}{\ensuremath{\bar{\mathrm{o}}}}
\newcommand{\AngOpen}{\ensuremath{\rangle}}
\newcommand{\AngClose}{\ensuremath{\langle}}
\newcommand{\Ov}[1]{\ensuremath{\overline{\hbox{\RL{#1}}}}}
\newcommand{\Ul}[1]{\ensuremath{\underline{\hbox{\RL{#1}}}}}
\newcommand{\HCell}[2]{\parbox[b]{#1mm}{\centering\footnotesize\ArStrut #2}}
\newcommand{\Bd}[1]{{\bfseries #1}}
\newcommand{\Withheld}[1]{\par\smallskip{\small\color{gray}[#1]}\par}
\begin{document}
"""

DEFAULT_COLS = [12, 14, 74, 12, 12, 12, 12]


def front(n_text, n_frames):
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\Large AL-KHWĀRIZMĪ\par\vspace{4mm}\LARGE The image of the earth\par\vspace{4mm}"
        r"{\ArHead\RL{كتاب صورة الارض}}\par\vspace{5mm}"
        r"\normalsize in the edition of Hans von Mžik\\"
        r"(Leipzig: Otto Harrassowitz, 1926; Bibliothek arabischer Historiker und Geographen 3), "
        r"in the Baghdad reprint of 1962\par"
        r"\vspace{3mm}the copy of Columbia University Libraries (G93 .K48), frames 1–218\par"
        r"\vspace{4mm}\large the text, line by line\end{center}\vspace{6mm}",
        r"\noindent Every printed line and every row of the tables of al-Khwārizmī’s text is one line here, in the "
        r"order of the frames of the Columbia copy, with its number in the margin and its anchor AK05-F\#\#\#-L\#\#. "
        r"The letters and the numerals of the tables, which are written with letters, are transcribed as printed; "
        r"the sign for zero, a small circle with a stroke above it, is set as \Zero{}. The editor’s running numbers in "
        r"parentheses, the numbers in square brackets, the angle brackets with which he marks what he supplies, his "
        r"note marks and the folios of the manuscript in the margin are kept where they stand. Hans von Mžik’s German "
        r"introduction and footnotes are not reproduced: they are his own writing, and he died in 1961. Their place "
        r"is marked on each page. Library marks of the Columbia copy are recorded in the page records, not "
        r"reproduced. Where the print is in error, the transcription keeps it; the critical notes at the end, which "
        r"are not part of the transcription, propose the correction.",
        r"\par\smallskip\noindent al-Khwārizmī’s text is in the public domain, and this transcription is dedicated "
        r"to the public domain (CC0 1.0). It is AI-integrated work (Claude); no person has proofread it. "
        rf"This file holds {n_text} lines from {n_frames} frames.\par\clearpage"])


def crop_figure(fr, fig, frame_sha):
    from PIL import Image
    src = FRAMES / f"page_{fr:03d}.jpg"
    data = src.read_bytes()
    if sha(data).upper() != frame_sha.upper():
        raise SystemExit(f"frame {fr}: the image is not the inventory's")
    im = Image.open(src)
    x0, y0, x1, y1 = fig["rect"]
    raw = im.crop((x0, y0, x1, y1))
    (HERE / "figures").mkdir(exist_ok=True)
    rp = HERE / "figures" / f"{fig['id']}_raw.png"
    raw.save(rp, optimize=True)
    der = raw.convert("L").resize((raw.width // 2, raw.height // 2))
    dp = HERE / "figures" / f"{fig['id']}.png"
    der.save(dp, optimize=True)
    return {"raw": rp, "raw_size": raw.size, "der": dp, "der_size": der.size}


def row_tex(ln, cols, align=None):
    spans, out, k = [], [], 0
    for c in ln["cells"]:
        n = 1
        m = re.match(r"(.*)\^(\d)$", c)
        if m:
            c, n = m.group(1).strip(), int(m.group(2))
        w = sum(cols[k:k + n]) if k + n <= len(cols) else 12 * n
        start = k
        k += n
        if ln["kind"] == "head":
            out.append(r"\HCell{" + f"{w:g}" + "}{" + artex(c) + "}")
        else:
            # the running number, the number of Suhrāb and the name (also when the name spans further columns)
            # stand to the right of their cells; the numerals are centred
            a = align[start] if align and start < len(align) else ("r" if start < 3 else "c")
            out.append(r"\Cell{" + f"{w:g}" + "}{" + a + "}{" + artex(c) + "}")
    if k > len(cols):
        raise SystemExit(f"a row has {k} cells and the table {len(cols)} columns: {ln['text'][:50]}")
    return "".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inv = {int(r["physical_page"]): r for r in csv.DictReader(open(INVENTORY, encoding="utf-8"))}
    pages = sorted((HERE / "pages").glob("AK05-F*.txt"))
    recs = [parse(p) for p in pages]
    frames = [r["frame"] for r in recs]
    assert frames == sorted(set(frames)), "frames out of order or repeated"
    assert frames == list(range(1, len(frames) + 1)), "frames not continuous from 1"
    n_text = sum(len(r["lines"]) for r in recs if r["kind"] == "text")
    tex = [PREAMBLE, front(n_text, len(recs))]
    anchors, disp, evid, unres, variants, figs, ednotes, copyrows, crit, tables = [], [], [], [], [], [], [], [], [], []
    (HERE / "records").mkdir(exist_ok=True)
    cols, align = DEFAULT_COLS, None
    for r in recs:
        fr = r["frame"]
        fid = f"AK05-F{fr:03d}"
        if r["cols"]:
            cols, align = r["cols"], r["align"]
        elif r["align"]:
            align = r["align"]
        label = f"p. {r['printed']}" if r["printed"] != "-" else LABEL.get(r["kind"], "unnumbered")
        mark = label.translate(AR)
        if r["figs"]:
            tex.append(r"\needspace{0.8\textheight}")    # the heading of a plate stays on the page of the plate
        tex.append(r"\FrameHead{" + str(fr) + "}{" + esc(mark) + "}{" + f"{fr:03d}" + "}{" + mixed(label) + "}")
        for fg in r["figs"]:
            c = crop_figure(fr, fg, inv[fr]["sha256"])
            tex.append(r"\par\smallskip\begin{center}\includegraphics[width=0.8\linewidth,height=0.72\textheight,"
                       r"keepaspectratio]{figures/" + fg["id"] + r".png}\end{center}\smallskip")
            figs.append((fg["id"], fid, inv[fr]["filename"], inv[fr]["sha256"].lower(), " ".join(map(str, fg["rect"])),
                         f"{c['raw_size'][0]}x{c['raw_size'][1]}", sha(c["raw"].read_bytes()),
                         f"{c['der_size'][0]}x{c['der_size'][1]}", sha(c["der"].read_bytes()),
                         "raw: crop of the decoded JPEG frame, pixels untouched, saved losslessly; derivative: "
                         "converted to grey and halved in size (bilinear), no other change", "included"))
        out_lines = []
        rows = 0
        for k, ln in enumerate(r["lines"], 1):
            aid = f"{fid}-L{k:02d}"
            marg = r"\Marg{" + mixed(ln["margin"]) + "}" if ln["margin"] else ""
            if ln["kind"] in ("row", "head"):
                tex.append(r"\EdR{" + str(k) + "}{" + aid + "}{" + row_tex(ln, cols, align) + "}{" + marg + "}")
                rows += ln["kind"] == "row"
            else:
                macro = {"text": r"\EdL", "indent": r"\EdLp", "centre": r"\EdLc", "heading": r"\EdLh",
                         "latin": r"\EdLl"}[ln["kind"]]
                if r["kind"] == "title" and ln["kind"] != "latin":
                    macro = r"\EdLc"
                tex.append(macro + "{" + str(k) + "}{" + aid + "}{" + artex(ln["text"]) + "}{" + marg + "}")
            anchors.append((aid, fr, r["printed"], k, ln["kind"], ln["text"], ln["margin"] or ""))
            out_lines.append({"id": aid, "n": k, "kind": ln["kind"], "text": ln["text"], "margin": ln["margin"],
                              "cells": ln.get("cells"), "plain": flat(ln["text"]),
                              "note_marks": marked(ln["text"], "n"), "bold": marked(ln["text"], "b"),
                              "underlined": marked(ln["text"], "u")})
        if rows:
            tables.append((fid, "coordinate table", f"{rows} rows",
                           "every cell read on the frame at full resolution; numerals transcribed as printed", ""))
        for cn in r["critical"]:
            if int(cn["line"][1:]) > len(r["lines"]):
                raise SystemExit(f"{fid}: critical note {cn['id']} on {cn['line']}, which the page does not have")
            crit.append((cn["id"], f"{fid}-{cn['line']}", cn["class"], cn["printed"], cn["proposed"], cn["evidence"],
                         cn["confidence"], cn["impact"]))
        if r["kind"] == "blank":
            tex.append(r"\Withheld{blank}")
        elif r["kind"] in ("provenance", "binding", "extrinsic"):
            tex.append(r"\Withheld{" + {"provenance": "library matter only", "binding": "the library's binding",
                                         "extrinsic": "acquisition notice"}[r["kind"]] + ": " +
                       mixed("; ".join(r["copy"])) + "}")
        for w in r["withheld"]:
            tex.append(r"\Withheld{" + mixed(w) + " --- not reproduced}")
        for e in r["ednotes"]:
            marks = " ".join(e["marks"])
            what = (f"the editor’s note {marks}, continued from the page before" if e["continued"] else
                    f"the editor’s note{'s' if len(e['marks']) > 1 else ''} {marks}")
            tex.append(r"\par\smallskip\noindent\rule{30mm}{0.4pt}\Withheld{" + mixed(what) +
                       f", {e['lines']} printed line{'' if e['lines'] == 1 else 's'} --- not reproduced" + "}")
            ednotes.append((fid, r["printed"], " ".join(e["marks"]), e["lines"], "continued" if e["continued"] else ""))
        for o in r["obs"]:
            evid.append((fid, "observation", o))
        for v in r["variants"]:
            variants.append((fid, "Mzik edition 1926 | Strasbourg manuscript (as the editor reports it)", v))
        for u in r["unres"]:
            unres.append((fid, u))
        for c in r["copy"]:
            copyrows.append((fid, c))
        disp.append((fid, fr, inv[fr]["filename"], inv[fr]["sha256"].lower(), r["printed"], r["kind"], ROLE[r["kind"]],
                     len(r["lines"]), sum(e["lines"] for e in r["ednotes"]), len(r["figs"]),
                     "transcribed" if r["kind"] in ("text", "title") else
                     ("figure reproduced" if r["kind"] == "plate" else
                      ("recorded, not reproduced" if r["kind"] in ("editorial", "provenance", "binding", "extrinsic")
                       else "recorded"))))
        out = {"anchor": fid, "frame": fr, "frame_file": inv[fr]["filename"], "frame_sha256": inv[fr]["sha256"].lower(),
               "printed_page": r["printed"], "kind": r["kind"], "role": ROLE[r["kind"]],
               "comment": " ".join(r["comment"]), "lines": out_lines, "editors_notes": r["ednotes"],
               "withheld": r["withheld"], "figures": r["figs"], "variants": r["variants"], "unresolved": r["unres"],
               "observations": r["obs"], "copy_matter": r["copy"], "critical_notes": r["critical"]}
        (HERE / "records" / f"{fid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    if crit:
        tex.append(r"\clearpage\pdfbookmark[1]{critical notes}{critical}{\large\bfseries Critical notes}\par\medskip"
                   r"\noindent These notes are not part of the transcription. They record errors of the print and "
                   r"propose corrections; the transcription keeps the print.\par\medskip")
        for c in crit:
            tex.append(r"\noindent\textbf{" + esc(c[0]) + r"}\enspace\hyperlink{" + c[1] + "}{" + esc(c[1]) + r"}\enspace"
                       r"(" + esc(c[2]) + r")\par\noindent printed: " + mixed(c[3]) + r"\enspace proposed: " +
                       mixed(c[4]) + r"\par\noindent " + mixed(c[5]) + r"\par\noindent confidence: " + mixed(c[6]) +
                       r"\par\noindent impact: " + mixed(c[7]) + r"\par\medskip")
    tex.append(r"\end{document}")
    (HERE / "surat_1962.tex").write_text("\n".join(tex) + "\n", encoding="utf-8", newline="\n")

    def tsv(name, head, rows):
        with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(head) + "\n")
            for row in rows:
                fh.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    tsv("anchors.tsv", ["anchor", "frame", "printed_page", "line", "kind", "text", "margin"], anchors)
    tsv("physical_unit_disposition.tsv", ["anchor", "frame", "frame_file", "frame_sha256", "printed_page", "kind",
                                          "role", "text_lines", "editors_note_lines", "figures", "disposition"], disp)
    tsv("evidence_ledger.tsv", ["anchor", "kind", "text"], evid)
    tsv("unresolved_readings.tsv", ["anchor", "reading"], unres)
    tsv("witness_variants.tsv", ["anchor", "witnesses", "variant"], variants)
    tsv("figure_provenance.tsv", ["figure", "anchor", "frame_file", "frame_sha256", "rect_x0_y0_x1_y1", "raw_size",
                                  "raw_sha256", "derivative_size", "derivative_sha256", "operations", "status"], figs)
    tsv("editors_notes_withheld.tsv", ["anchor", "printed_page", "marks", "printed_lines", "continued"], ednotes)
    tsv("copy_provenance.tsv", ["anchor", "matter"], copyrows)
    tsv("critical_findings.tsv", ["id", "anchor", "issue_class", "diplomatic_reading", "proposed_critical_reading",
                                  "evidence", "confidence", "propagation_impact"], crit)
    tsv("formula_table_ledger.tsv", ["anchor", "kind", "coverage", "verification", "companion"], tables)
    tsv("proposed_corrections.tsv", ["anchor", "current_reading", "proposal", "evidence", "confidence", "state"], [])
    tsv("language_synchronization.tsv", ["language", "canonical_checkpoint", "replay_state", "proposals", "state"], [])
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    last = max(frames)
    ck = {"lane": "AK05 geography (Mzik 1926 in the Baghdad reprint of 1962, 218 frames)",
          "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the page files in order: file name, a NUL byte, the bytes",
          "last_fully_transcribed_source_unit": f"frame{last:03d}",
          "last_fully_verified_source_unit": f"frame{last:03d}",
          "first_untouched_source_unit": f"frame{last + 1:03d}" if last < 218 else None,
          "owned_units_total": 218, "owned_units_disposed": len(recs),
          "unresolved_count": len(unres), "figure_count": len(figs), "table_rows": sum(int(t[2].split()[0]) for t in tables),
          "critical_notes": len(crit), "text_lines": n_text,
          "editors_note_lines_withheld": sum(x[3] for x in ednotes)}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(recs)} frames ({frames[0]}-{frames[-1]}), {len(anchors)} lines ({n_text} of the text), "
          f"{len(figs)} figures, {len(ednotes)} withheld note blocks, {len(evid)} observations, {len(variants)} variants")


if __name__ == "__main__":
    main()
