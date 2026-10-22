"""al-Khwarizmi, Kitab al-jabr wa-l-muqabala, in the edition of Ali Mustafa Musharrafa and Muhammad Mursi Ahmad
(Cairo, 1939; Columbia University Libraries copy, 130 frames at 400 ppi): the line-anchored transcription of the frames,
one line of this edition for each printed line of al-Khwarizmi's text. The editors' preface, their study and their
footnotes are recorded (where they stand, how many lines) but not reproduced: Muhammad Mursi Ahmad died in 1989, and
their text is protected in the EU until 2059. al-Khwarizmi's text is in the public domain; this transcription is
dedicated to the public domain (CC0 1.0).

Page files (pages/AK01-F###.txt, one per frame):
  @page FRAME PRINTED   the frame and the page number as printed (Arabic-Indic digits; [١٥] a number not printed but
                        given by the sequence; - none)
  @kind KIND            text (default), cover, title, blank, provenance (copy matter only), facsimile, editorial,
                        wrapper (the back of the edition's printed wrapper: the publisher's list, described)
  % ...                 a comment (kept in the record)
  TEXT                  a printed line of al-Khwarizmi's text; prefixes "@h " a heading (centred, larger), "@c " a
                        centred line, "@p " a line printed with a paragraph indent; inline {n:١} the editors' note mark
                        printed in the line, {ov:اب} letters printed as the labels of a figure, with a line above them,
                        {inv:ج} a letter printed upside down (a turned sort), {b:...} words printed in bold
  @ednotes N.. LINES [continued]   the editors' footnotes at the foot of the page: their marks and how many printed
                        lines they take ("continued": a note carried over from the page before), not reproduced
  @withheld TEXT        the edition's matter that fills the frame (the editors' text; the publisher's list on the
                        back wrapper), described, not reproduced
  @fig ID X0 Y0 X1 Y1 [after=N]   a figure: the rectangle of the frame (pixels) cut out untouched (figures/ID_raw.png)
                        and as a conservative derivative (figures/ID.png: grey, half size); set after line N of the
                        page (where it begins on the page), else after the last line
  @variant TEXT         a reading of the manuscript reported by the editors (in our words)
  @unres TEXT           an unresolved reading
  @obs TEXT             an observation on the print
  @copy TEXT            copy matter (library marks, a reader's pencil): recorded, not part of the edition
  @critical ID | CLASS | Lnn | PRINTED | PROPOSED | EVIDENCE | CONFIDENCE | IMPACT   a critical note (layer 3): an
                        error of the print and the proposed correction; the line keeps the print
Writes jabr_1939.tex, records/AK01-F###.json and the ledgers (see README.md). python build_jabr.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FRAMES = ROOT / "_intake" / "algebra" / "frames"
INVENTORY = ROOT / "controls" / "algebra_1939" / "10_IMAGE_INVENTORY_SHA256.csv"
AR = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ROLE = {"text": "AK_TEXT (lines); MODERN_EDITORIAL (note marks, footnotes not reproduced)",
        "cover": "MODERN_EDITORIAL (the edition's printed wrapper); COPY_PROVENANCE (binding)",
        "title": "MODERN_EDITORIAL (the edition's title page)", "blank": "blank",
        "provenance": "COPY_PROVENANCE", "facsimile": "MODERN_EDITORIAL (plate: facsimile of the manuscript)",
        "editorial": "MODERN_EDITORIAL (not reproduced)",
        "wrapper": "MODERN_EDITORIAL (the back of the edition's printed wrapper: the publisher's list, not reproduced)"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}"))


def groups(s):
    """the markup of a line as a list of plain strings and (kind, content) pairs; the markup may nest, as a turned
    letter in a figure label: {ov:ه{inv:ن}}"""
    out, i, plain = [], 0, ""
    while i < len(s):
        m = re.match(r"\{(n|ov|inv|b):", s[i:])
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
    """the letters of a line or a group without the markup (note marks dropped)"""
    return "".join(g if isinstance(g, str) else ("" if g[0] == "n" else flat(g[1])) for g in groups(s))


def artex(s):
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(esc(g))
        elif g[0] == "n":
            out.append(r"\NoteMark{" + esc(g[1].strip()) + "}")
        else:
            macro = {"ov": r"\Ov{", "inv": r"\Inv{", "b": r"\Bd{"}[g[0]]
            out.append(macro + artex(g[1] if g[0] == "b" else g[1].strip()) + "}")
    return "".join(out)


def marked(s, kind):
    """the plain contents of every group of a kind, nested groups included"""
    out = []
    for g in groups(s):
        if isinstance(g, tuple):
            if g[0] == kind:
                out.append(flat(g[1]))
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
    return "".join(out)


def parse(path):
    rec = {"frame": None, "printed": None, "kind": "text", "lines": [], "ednotes": [], "withheld": [], "figs": [],
           "variants": [], "unres": [], "obs": [], "copy": [], "critical": [], "comment": []}
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
            after = [int(v[6:]) for v in rest if v.startswith("after=")]
            rec["figs"].append({"id": fid, "rect": [int(v) for v in rest if not v.startswith("after=")],
                                "after": after[0] if after else None})
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
        elif tag in ("@h", "@c", "@p"):
            rec["lines"].append({"kind": {"@h": "heading", "@c": "centre", "@p": "indent"}[tag], "text": body})
        elif raw.startswith("@"):
            raise SystemExit(f"{path.name}: unknown line {raw[:40]}")
        else:
            rec["lines"].append({"kind": "text", "text": raw.strip()})
    for ln in rec["lines"]:
        ln["text"] = re.sub(r"\s+", " ", ln["text"]).strip()
    return rec


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,left=24mm,right=30mm,top=22mm,bottom=22mm]{geometry}
\usepackage{fontspec,graphicx,needspace,xcolor}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{arabic}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\arabicfont{Amiri}[Script=Arabic]
\newfontfamily\ArBody{Amiri}[Script=Arabic,Scale=1.1,BoldFont={Amiri Bold}]
\newfontfamily\ArHead{Amiri}[Script=Arabic,Scale=1.45]
\hypersetup{pdftitle={al-Khwarizmi, Kitab al-jabr wa-l-muqabala, ed. Musharrafa and Ahmad (Cairo, 1939): the text, line by line},pdfauthor={Muhammad ibn Musa al-Khwarizmi}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\tracinglostchars=2
\newcommand{\FrameHead}[4]{\par\bigskip\penalty-300\pdfbookmark[1]{frame #1 (#2)}{fr-#1}\hypertarget{AK01-F#3}{}%
 {\large\bfseries #4}\enspace{\footnotesize\color{gray}frame #1}\par\smallskip}
% a strut that gives every printed line the same height and depth, so that the lines stand at even distances
\newcommand{\ArStrut}{\vrule height 1.05em depth 0.45em width 0pt}
% one printed line, right to left, with its number in the left margin
\newcommand{\EdL}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArBody\raggedleft\ArStrut #3\par}\par}
\newcommand{\EdLp}[3]{\EdL{#1}{#2}{\hspace*{8mm}#3}}
\newcommand{\EdLc}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArBody\centering\ArStrut #3\par}\par}
\newcommand{\EdLh}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArHead\centering #3\par}\par\smallskip}
\newcommand{\NoteMark}[1]{\textsuperscript{(#1)}}
% letters printed as the labels of a figure, with a line above them
\newcommand{\Ov}[1]{\ensuremath{\overline{\hbox{\RL{#1}}}}}
% a letter printed upside down; words printed in bold
\newcommand{\Inv}[1]{\rotatebox[origin=c]{180}{\RL{#1}}}
\newcommand{\Bd}[1]{{\bfseries #1}}
\newcommand{\Withheld}[1]{\par\smallskip{\small\color{gray}[#1]}\par}
\begin{document}
"""


def front(n_text, n_frames):
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\Large AL-KHWĀRIZMĪ\par\vspace{4mm}\LARGE The book of algebra\par\vspace{4mm}"
        r"{\ArHead\RL{كتاب الجبر والمقابلة}}\par\vspace{5mm}"
        r"\normalsize in the edition of ʿAlī Muṣṭafā Mušarrafa and Muḥammad Mursī Aḥmad\\"
        r"(Cairo: the Egyptian University, Faculty of Science, 1939; printed by Fatḥ Allāh Ilyās Nūrī and sons)\par"
        r"\vspace{3mm}the copy of Columbia University Libraries (QA32 .K45), frames 1–130 at 400\,ppi\par"
        r"\vspace{4mm}\large the text, line by line\end{center}\vspace{6mm}",
        r"\noindent Every printed line of al-Khwārizmī’s text is one line here, in the order of the frames of the "
        r"Columbia copy, with its number in the margin and its anchor AK01-F\#\#\#-L\#\#. The letters are "
        r"transcribed as printed: the dotless final \RL{\ArBody ى} where the print has it, the hamza and the madda "
        r"where they are printed and not where they are not, the tanwīn on the final alif where it is printed, "
        r"the full stops and commas with the spaces the print sets around them. A word space is omitted where the "
        r"print sets none after a letter that does not join the next (\RL{\ArBody مماكانوا}, "
        r"\RL{\ArBody العشرةوتثلث}); after a joining letter, whose final form ends the word, the space is written. "
        r"The gaps were measured on the scan; in doubt, the space is written. "
        r"The word \RL{\ArBody الله} is printed as the usual ligature, which the font draws from the plain letters. "
        r"The elongation strokes (kashīda) with which the print stretches some words to fill a line are not "
        r"transcribed, nor the wider gaps with which it spreads the letters of a word for the same purpose. "
        r"Letters printed as the labels of a figure carry a short wavy line above them; they are set "
        r"here with a line above ({\ArBody\RL{سطح \Ov{اٮ}}}). A letter printed upside down is set upside down; "
        r"words the edition prints in bold, as the statements of some problems, are set in bold. The \RL{\ArBody ب} of "
        r"the labels is printed without its dot and is written \RL{\ArBody ٮ}. "
        r"The editors’ note marks are kept in the lines where they stand. The figures of the text are reproduced "
        r"as images where they begin on the page. Where the print is in error, the transcription keeps it; the "
        r"critical notes at the end, which are not part of the transcription, propose the correction.",
        r"\par\smallskip\noindent The editors’ preface, their study of algebra before al-Khwārizmī and of his life "
        r"and book, and their footnotes, which restate the problems in modern notation and report readings of the "
        r"manuscript, are not reproduced: they are the editors’ own writing, and Muḥammad Mursī Aḥmad died in 1989. "
        r"Their place is marked on each page. The three facsimiles of the manuscript in the edition are reproduced as "
        r"images. The back of the edition’s wrapper, a list of the Faculty of Science’s publications, is described "
        r"in its page record, not reproduced. Library marks and a reader’s pencil notes in the Columbia copy are "
        r"recorded in the page records, "
        r"not reproduced. The edition corrects what its editors judged obvious copying errors of the manuscript "
        r"without marking them (preface, frame 012); this transcription follows the edition as printed.",
        r"\par\smallskip\noindent al-Khwārizmī’s text is in the public domain, and this transcription is dedicated "
        r"to the public domain (CC0 1.0). It is AI-integrated work (Claude); no person has proofread it. "
        rf"This file holds {n_text} lines from {n_frames} frames.\par\clearpage"])


def crop_figure(fr, fig, frame_sha):
    from PIL import Image
    src = FRAMES / f"page_{fr:03d}.jpg"
    data = src.read_bytes()
    if sha(data).upper() != frame_sha.upper():
        raise SystemExit(f"frame {fr}: the image is not the packet's")
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inv = {int(r["physical_page"]): r for r in csv.DictReader(open(INVENTORY, encoding="utf-8"))}
    pages = sorted((HERE / "pages").glob("AK01-F*.txt"))
    recs = [parse(p) for p in pages]
    frames = [r["frame"] for r in recs]
    assert frames == sorted(set(frames)), "frames out of order or repeated"
    n_text = sum(len(r["lines"]) for r in recs if r["kind"] == "text")
    tex = [PREAMBLE, front(n_text, len(recs))]
    anchors, disp, evid, unres, variants, figs, ednotes, copyrows, crit = [], [], [], [], [], [], [], [], []
    (HERE / "records").mkdir(exist_ok=True)
    for r in recs:
        fr = r["frame"]
        fid = f"AK01-F{fr:03d}"
        label = (f"p. {r['printed']}" if r["printed"] != "-" else
                 {"cover": "cover", "title": "title page", "blank": "blank", "provenance": "library matter",
                  "facsimile": "plate", "editorial": "editors' matter",
                  "wrapper": "back wrapper"}.get(r["kind"], "unnumbered"))
        mark = label.translate(AR)                                   # the bookmark in Western digits
        tex.append(r"\FrameHead{" + str(fr) + "}{" + esc(mark) + "}{" + f"{fr:03d}" + "}{" + mixed(label) + "}")
        figtex = {}
        for fg in r["figs"]:
            if fg["after"] is not None and not 1 <= fg["after"] <= len(r["lines"]):
                raise SystemExit(f"{fid}: figure {fg['id']} after line {fg['after']}, which the page does not have")
            c = crop_figure(fr, fg, inv[fr]["sha256"])
            # a figure of the text, which stands among the lines, is smaller than a plate
            size = (r"width=0.6\linewidth,height=0.5\textheight" if fg["after"] is not None else
                    r"width=0.8\linewidth,height=0.72\textheight")
            figtex.setdefault(fg["after"], []).append(
                r"\par\smallskip\begin{center}\includegraphics[" + size + r",keepaspectratio]{figures/" + fg["id"] +
                r".png}\end{center}\smallskip")
            figs.append((fg["id"], fid, inv[fr]["filename"], inv[fr]["sha256"].lower(), " ".join(map(str, fg["rect"])),
                         f"{c['raw_size'][0]}x{c['raw_size'][1]}", sha(c["raw"].read_bytes()),
                         f"{c['der_size'][0]}x{c['der_size'][1]}", sha(c["der"].read_bytes()),
                         "raw: crop of the decoded JPEG frame, pixels untouched, saved losslessly; derivative: "
                         "converted to grey and halved in size (bilinear), no other change",
                         "included" + (f", after line {fg['after']}" if fg["after"] is not None else "")))
        out_lines = []
        for k, ln in enumerate(r["lines"], 1):
            aid = f"{fid}-L{k:02d}"
            macro = {"text": r"\EdL", "indent": r"\EdLp", "centre": r"\EdLc", "heading": r"\EdLh"}[ln["kind"]]
            if r["kind"] in ("cover", "title"):
                macro = r"\EdLc"
            tex.append(macro + "{" + str(k) + "}{" + aid + "}{" + artex(ln["text"]) + "}")
            tex.extend(figtex.get(k, []))
            anchors.append((aid, fr, r["printed"], k, ln["kind"], ln["text"]))
            out_lines.append({"id": aid, "n": k, "kind": ln["kind"], "text": ln["text"],
                              "note_marks": re.findall(r"\{n:([^}]*)\}", ln["text"]),
                              "figure_labels": marked(ln["text"], "ov"),
                              "turned_letters": marked(ln["text"], "inv"),
                              "bold": marked(ln["text"], "b")})
        tex.extend(figtex.get(None, []))
        for cn in r["critical"]:
            if int(cn["line"][1:]) > len(r["lines"]):
                raise SystemExit(f"{fid}: critical note {cn['id']} on {cn['line']}, which the page does not have")
            crit.append((cn["id"], f"{fid}-{cn['line']}", cn["class"], cn["printed"], cn["proposed"], cn["evidence"],
                         cn["confidence"], cn["impact"]))
        if r["kind"] == "blank":
            tex.append(r"\Withheld{blank}")
        elif r["kind"] == "provenance":
            tex.append(r"\Withheld{library matter only: " + mixed("; ".join(r["copy"])) + "}")
        for w in r["withheld"]:
            tex.append(r"\Withheld{" + mixed(w) + " --- not reproduced}")
        for e in r["ednotes"]:
            marks = " ".join(f"({m})" for m in e["marks"])
            what = (f"the editors’ note {marks}, continued from the page before" if e["continued"] else
                    f"the editors’ note{'s' if len(e['marks']) > 1 else ''} {marks}")
            tex.append(r"\par\smallskip\noindent\rule{30mm}{0.4pt}\Withheld{" + mixed(what) +
                       f", {e['lines']} printed line{'' if e['lines'] == 1 else 's'} --- not reproduced" + "}")
            ednotes.append((fid, r["printed"], " ".join(e["marks"]), e["lines"], "continued" if e["continued"] else ""))
        for o in r["obs"]:
            evid.append((fid, "observation", o))
        for v in r["variants"]:
            variants.append((fid, "1939 edition | manuscript (as the editors report it)", v))
        for u in r["unres"]:
            unres.append((fid, u))
        for c in r["copy"]:
            copyrows.append((fid, c))
        disp.append((fid, fr, inv[fr]["filename"], inv[fr]["sha256"].lower(), r["printed"], r["kind"], ROLE[r["kind"]],
                     len(r["lines"]), sum(e["lines"] for e in r["ednotes"]), len(r["figs"]),
                     "transcribed" if r["kind"] in ("text", "cover", "title") else
                     ("figure reproduced" if r["kind"] == "facsimile" else
                      ("recorded, not reproduced" if r["kind"] in ("editorial", "provenance", "wrapper") else
                       "recorded"))))
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
    (HERE / "jabr_1939.tex").write_text("\n".join(tex) + "\n", encoding="utf-8", newline="\n")

    def tsv(name, head, rows):
        with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(head) + "\n")
            for row in rows:
                fh.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    tsv("anchors.tsv", ["anchor", "frame", "printed_page", "line", "kind", "text"], anchors)
    tsv("physical_unit_disposition.tsv", ["anchor", "frame", "frame_file", "frame_sha256", "printed_page", "kind",
                                          "role", "text_lines", "editors_note_lines", "figures", "disposition"], disp)
    tsv("evidence_ledger.tsv", ["anchor", "kind", "text"], evid)
    tsv("unresolved_readings.tsv", ["anchor", "reading"], unres)
    tsv("witness_variants.tsv", ["anchor", "witnesses", "variant"], variants)
    tsv("figure_provenance.tsv", ["figure", "anchor", "frame_file", "frame_sha256", "rect_x0_y0_x1_y1", "raw_size",
                                  "raw_sha256", "derivative_size", "derivative_sha256", "operations", "status"], figs)
    tsv("editors_notes_withheld.tsv", ["anchor", "printed_page", "marks", "printed_lines", "continued"], ednotes)
    tsv("copy_provenance.tsv", ["anchor", "matter"], copyrows)
    # the ledgers of the packet's return protocol that hold nothing yet keep their heads
    tsv("critical_findings.tsv", ["id", "anchor", "issue_class", "diplomatic_reading", "proposed_critical_reading",
                                  "evidence", "confidence", "propagation_impact"], crit)
    tsv("formula_table_ledger.tsv", ["anchor", "kind", "coverage", "verification", "companion"], [])
    tsv("proposed_corrections.tsv", ["anchor", "current_reading", "proposal", "evidence", "confidence", "state"], [])
    tsv("language_synchronization.tsv", ["language", "canonical_checkpoint", "replay_state", "proposals", "state"], [])
    # the cumulative checkpoint of the algebra lane
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    text_frames = [r["frame"] for r in recs]
    last = max(text_frames)
    ck = {"lane": "AK01 algebra (1939 edition, 130 frames)",
          "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the page files in order: file name, a NUL byte, the bytes",
          "last_fully_transcribed_source_unit": f"frame{last:03d}",
          "last_fully_verified_source_unit": f"frame{last:03d}",
          "first_untouched_source_unit": f"frame{last + 1:03d}" if last < 130 else None,
          "owned_units_total": 130, "owned_units_disposed": len(recs),
          "unresolved_count": len(unres), "figure_count": len(figs), "formula_or_table_count": 0,
          "critical_notes": len(crit),
          "text_lines": n_text, "editors_note_lines_withheld": sum(x[3] for x in ednotes),
          "frames_withheld_editorial": [r["frame"] for r in recs if r["kind"] == "editorial"]}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(recs)} frames ({frames[0]}-{frames[-1]}), {len(anchors)} lines ({n_text} of the text), "
          f"{len(figs)} figures, {len(ednotes)} withheld note blocks, {len(evid)} observations, {len(variants)} variants")


if __name__ == "__main__":
    main()
