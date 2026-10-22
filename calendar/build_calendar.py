"""al-Khwarizmi, Maqala fi istikhraj tarikh al-yahud wa-a'yadihim (on the Jewish calendar), in the Hyderabad edition
(Matba'at Jam'iyyat Da'irat al-Ma'arif al-'Uthmaniyya, 1366 H / 1947, bound first in the collection al-Rasa'il
al-mutafarriqa fi al-hay'a, 1367 H / 1948), from the scan on Arabic Wikisource (packet file 60, 320 PDF pages; this lane
owns PDF pages 1-10): the line-anchored transcription of the printed witness, one line here for each printed line.
The edition names no editor. The text, the edition and this transcription are in the public domain; the transcription
is dedicated to the public domain (CC0 1.0).

Page files (pages/AK15-P###.txt, one per PDF page):
  @page PDF PRINTED     the PDF page and the page number as printed (Arabic-Indic digits; - none)
  @kind KIND            text (default), title (a title page), blank
  % ...                 a comment (kept in the record)
  TEXT                  a printed line; prefixes "@h " a heading (centred, bold), "@c " a centred line, "@p " a line with
                        a paragraph indent
  @t CELL | CELL ...    a row of a printed list set in columns, its cells from right to left (the | is ours)
  @n TEXT               a printed line of the edition's footnotes (anchored N01, N02, ...)
  inline: {b:...} bold; {fr:ABOVE|BELOW} two lines set one over the other with a rule between (the dates of the title
          pages)
  @unres TEXT           an unresolved reading
  @obs TEXT             an observation on the print (the running head, the page number, catchwords, spacing, damage)
  @copy TEXT            copy matter (accession numbers, stamps of the scan): recorded, not part of the edition
  @critical ID | CLASS | Lnn | PRINTED | PROPOSED | EVIDENCE | CONFIDENCE | IMPACT   a critical note (layer 3): an error
                        of the printed witness and the proposed correction; the line keeps the print
Writes calendar_1947.tex, records/AK15-P###.json and the ledgers. python build_calendar.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INVENTORY = ROOT / "controls" / "calendar_1947" / "IMAGE_INVENTORY.tsv"
PAGES_PNG = ROOT / "_intake" / "calendar" / "pages"
ROLE = {"text": "AK_TEXT (the printed witness of al-Khwarizmi's treatise)",
        "title": "MODERN_EDITORIAL (a title page of the 1947/1948 edition)", "blank": "blank"}
PACKET_PDF_SHA = "26C55E7ECCA9597508EE4552B72CCBA95DEEC91C7F75F1DC49FF1E64C4382573"
# the numerical matter of the treatise and its checks (formula_table_ledger.tsv): anchor range, kind, coverage,
# verification, companion notes
FORMULAS = [
    ("AK15-P006-L02..AK15-P006-L10", "the hour of 1080 parts, the lunar month, the lunar years of 12 and 13 months, the "
     "nineteen-year cycle", "every figure transcribed as printed",
     "checks/constants.py: 29d 12h 793p, 354d 8h 876p, 383d 21h 589p, 6939d 16h 595p", "AK15-CN010, AK15-CN011"),
    ("AK15-P006-L10..AK15-P008-L10", "the rules for the first day of Tishri and the length of the year (the four "
     "gates)", "every limit transcribed as printed",
     "checks/gates.py (gates.out.txt), the standard rules run through a week part by part; checks/constants.py",
     "AK15-CN012 to AK15-CN021"),
    ("AK15-P008-L11..AK15-P008-L12", "the solar year, 365 days 5 3791/4104 hours", "transcribed as printed",
     "checks/constants.py: the cycle divided by 19", "none"),
    ("AK15-P008-L12..AK15-P008-L14", "the years from the creation of Adam to the end of the year 1135 of the "
     "Seleucid era", "transcribed as printed", "checks/constants.py: 3448 = 19 x 181 + 9", "AK15-CN022"),
    ("AK15-P008-L15..AK15-P009-L06", "three lists of positions in abjad letters (the first day of Adam, the "
     "building of the Temple, the beginning of the years of Dhu l-Qarnayn), set as running text",
     "every group transcribed as printed",
     "each group read as an abjad number; the sun and the moon in conjunction at 176 degrees in the first two lists "
     "(de Blois); unresolved groups in unresolved_readings.tsv", "AK15-CN023"),
    ("AK15-P009-L07..AK15-P010-L03", "the procedure for the mean positions of the sun and the moon; the base of "
     "days and the revolutions of the sun and the moon", "every figure transcribed as printed",
     "checks/constants.py: 35,975,351 days = 5184 cycles, 98,496 years, 1,218,240 months, 1,316,736 revolutions "
     "of the moon", "AK15-CN024, AK15-CN025"),
    ("AK15-P010-L05..AK15-P010-L12", "the procedure for the months, days, hours and parts since the conjunction",
     "every figure transcribed as printed", "checks/constants.py: 25,920 parts in a day, 765,433 in a month",
     "AK15-CN026"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}"))


def groups(s):
    out, i, plain = [], 0, ""
    while i < len(s):
        m = re.match(r"\{(b|fr):", s[i:])
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
    return "".join(g if isinstance(g, str) else (" ".join(flat(x) for x in g[1].split("|")) if g[0] == "fr" else
                                                 flat(g[1])) for g in groups(s))


def artex(s):
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(esc(g))
        elif g[0] == "b":
            out.append(r"{\bfseries " + artex(g[1]) + "}")
        else:
            up, down = g[1].split("|")
            out.append(r"\Fr{" + artex(up) + "}{" + artex(down) + "}")
    return "".join(out)


AR_RUN = re.compile(r"[؀-ۿ](?:[؀-ۿ\s\[\]()•?]|\.\.\.)*(?:[؀-ۿ\])]|\.\.\.)|[؀-ۿ]")


def mixed(s):
    """an English text with Arabic words: the Arabic runs set right to left in the Arabic font; brackets, parentheses,
    ellipses and the full stop between Arabic words stay inside the run, so that they keep their place in it"""
    out, pos = [], 0
    for m in AR_RUN.finditer(s):
        out.append(esc(s[pos:m.start()]))
        out.append(r"\RL{\ArBody " + esc(m.group(0)) + "}")
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out)


def parse(path):
    rec = {"pdf": None, "printed": None, "kind": "text", "lines": [], "notes": [], "unres": [], "obs": [], "copy": [],
           "critical": [], "comment": []}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        if raw.startswith("%"):
            rec["comment"].append(raw[1:].strip())
            continue
        if raw.startswith("@page "):
            _, pg, pr = raw.split()
            rec["pdf"], rec["printed"] = int(pg), pr
            continue
        tag = raw.split(" ", 1)[0]
        body = raw[len(tag):].strip()
        if tag == "@kind":
            rec["kind"] = body
        elif tag == "@critical":
            f = [x.strip() for x in body.split("|")]
            if len(f) != 8 or not re.fullmatch(r"[LN]\d\d", f[2]):
                raise SystemExit(f"{path.name}: a critical note needs 8 fields: {raw[:60]}")
            rec["critical"].append(dict(zip(["id", "class", "line", "printed", "proposed", "evidence", "confidence",
                                             "impact"], f)))
        elif tag == "@unres":
            rec["unres"].append(body)
        elif tag == "@obs":
            rec["obs"].append(body)
        elif tag == "@copy":
            rec["copy"].append(body)
        elif tag == "@n":
            rec["notes"].append(body)
        elif tag == "@t":
            rec["lines"].append({"kind": "row", "text": body, "cells": [c.strip() for c in body.split("|")]})
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
\usepackage[a4paper,left=26mm,right=30mm,top=22mm,bottom=22mm]{geometry}
\usepackage{fontspec,needspace,xcolor}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{arabic}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\newfontfamily\arabicfont{Amiri}[Script=Arabic]
\newfontfamily\ArBody{Amiri}[Script=Arabic,Scale=1.1,BoldFont={Amiri Bold}]
\newfontfamily\ArHead{Amiri}[Script=Arabic,Scale=1.3,BoldFont={Amiri Bold}]
\hypersetup{pdftitle={al-Khwarizmi, On the Jewish calendar, Hyderabad edition (1947): the printed text, line by line},pdfauthor={Muhammad ibn Musa al-Khwarizmi}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\tracinglostchars=2
\newcommand{\PageHead}[4]{\par\bigskip\penalty-300\pdfbookmark[1]{PDF #1 (#2)}{pg-#1}\hypertarget{AK15-P#3}{}%
 {\large\bfseries #4}\enspace{\footnotesize\color{gray}PDF page #1}\par\smallskip}
\newcommand{\ArStrut}{\vrule height 1.05em depth 0.45em width 0pt}
\newcommand{\EdL}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArBody\raggedleft\ArStrut #3\par}\par}
\newcommand{\EdLp}[3]{\EdL{#1}{#2}{\hspace*{8mm}#3}}
\newcommand{\EdLc}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArBody\centering\ArStrut #3\par}\par}
\newcommand{\EdLh}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArHead\centering\bfseries #3\par}\par\smallskip}
\newcommand{\EdLn}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\setRTL\ArBody\small\raggedleft #3\par}\par}
\newcommand{\Fr}[2]{\begin{tabular}[c]{@{}c@{}}#1\\[-2pt]\hline #2\end{tabular}}
\newcommand{\Withheld}[1]{\par\smallskip{\small\color{gray}[#1]}\par}
\begin{document}
"""


def front(n_text, n_pages):
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\Large AL-KHWĀRIZMĪ\par\vspace{4mm}\LARGE On the Jewish calendar\par\vspace{4mm}"
        r"{\ArHead\RL{مقالة فى استخراج تاريخ اليهود واعيادهم}}\par\vspace{5mm}"
        r"\normalsize in the edition of Hyderabad (Maṭbaʿat Jamʿiyyat Dāʾirat al-Maʿārif al-ʿUthmāniyya, 1366\,H / 1947),"
        r" the first of the eleven treatises of \emph{al-Rasāʾil al-mutafarriqa fī al-hayʾa} (1367\,H / 1948)\par"
        r"\vspace{3mm}the scan of Arabic Wikisource, PDF pages 1–10\par"
        r"\vspace{4mm}\large the printed text, line by line\end{center}\vspace{6mm}",
        r"\noindent Every printed line of the edition is one line here, page by page, with its number in the margin and "
        r"its anchor AK15-P\#\#\#-L\#\# (PDF page, line); the lines of the edition’s footnotes have the anchors "
        r"AK15-P\#\#\#-N\#\#. The text is transcribed as printed: the spelling of the edition, with the final "
        r"\RL{\ArBody ى} without dots where it is so printed, the hamza only where it is printed, and every numeral in "
        r"the form the edition prints, Arabic-Indic digits and the letters of the abjad. The running heads, the page "
        r"numbers and the catchwords are recorded in the page records. The edition’s spacing after letters that do not "
        r"join the next is irregular: the white inside a word can be as wide as a word space; the words are divided by "
        r"the sense, and the page records note where the print suggests another division.",
        r"\par\smallskip\noindent The treatise survives in one manuscript, made in Mosul in 632\,H (1234), now in the "
        r"Khuda Bakhsh Library at Patna, which is not part of this work. The printed text is known to keep the errors of "
        r"that copy and to add new ones, above all in the numerals. This transcription keeps the print; the critical "
        r"notes at the end, which are not part of the transcription, propose corrections where the arithmetic of the "
        r"calendar, or the text itself, shows the print to be wrong.",
        r"\par\smallskip\noindent The text is in the public domain, and this transcription is dedicated to the public "
        r"domain (CC0 1.0). It is AI-integrated work (Claude); no person has proofread it. "
        rf"This file holds {n_text} lines from {n_pages} PDF pages.\par\clearpage"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inv = {int(r["pdf_page"]): r for r in csv.DictReader(open(INVENTORY, encoding="utf-8"), delimiter="\t")}
    pages = sorted((HERE / "pages").glob("AK15-P*.txt"))
    recs = [parse(p) for p in pages]
    nums = [r["pdf"] for r in recs]
    assert nums == sorted(set(nums)), "pages out of order or repeated"
    n_text = sum(len(r["lines"]) for r in recs if r["kind"] == "text")
    tex = [PREAMBLE, front(n_text, len(recs))]
    anchors, disp, evid, unres, copyrows, crit = [], [], [], [], [], []
    (HERE / "records").mkdir(exist_ok=True)
    for r in recs:
        pg = r["pdf"]
        pid = f"AK15-P{pg:03d}"
        png = PAGES_PNG / f"pdf{pg:03d}.png"
        if png.exists():
            # the reading image must be the packet's page: its pixels against the inventory
            from PIL import Image
            import numpy as np
            if sha(np.asarray(Image.open(png).convert("L")).tobytes()) != inv[pg]["decoded_pixels_sha256"]:
                raise SystemExit(f"{pid}: the reading image is not the packet's page")
        label = {"title": "title page", "blank": "blank"}.get(r["kind"], f"p. {r['printed']}")
        if r["kind"] == "title" and r["printed"] != "-":
            label = f"title page (p. {r['printed']})"
        tex.append(r"\PageHead{" + str(pg) + "}{" + esc(label) + "}{" + f"{pg:03d}" + "}{" + mixed(label) + "}")
        out_lines = []
        for k, ln in enumerate(r["lines"], 1):
            aid = f"{pid}-L{k:02d}"
            if ln["kind"] == "row":
                cells = r"\hfill".join(r"\mbox{" + artex(c) + "}" for c in ln["cells"])
                tex.append(r"\EdL{" + str(k) + "}{" + aid + "}{" + cells + "}")
            else:
                macro = {"text": r"\EdL", "indent": r"\EdLp", "centre": r"\EdLc", "heading": r"\EdLh"}[ln["kind"]]
                if r["kind"] == "title" and ln["kind"] == "text":
                    macro = r"\EdLc"
                tex.append(macro + "{" + str(k) + "}{" + aid + "}{" + artex(ln["text"]) + "}")
            anchors.append((aid, pg, r["printed"], f"L{k:02d}", ln["kind"], ln["text"]))
            out_lines.append({"id": aid, "n": k, "kind": ln["kind"], "text": ln["text"], "plain": flat(ln["text"]),
                              "cells": ln.get("cells")})
        if r["notes"]:
            tex.append(r"\par\smallskip\noindent\hfill\rule{30mm}{0.4pt}\par")
        for k, n in enumerate(r["notes"], 1):
            aid = f"{pid}-N{k:02d}"
            tex.append(r"\EdLn{N" + str(k) + "}{" + aid + "}{" + artex(n) + "}")
            anchors.append((aid, pg, r["printed"], f"N{k:02d}", "note", n))
            out_lines.append({"id": aid, "n": k, "kind": "note", "text": n, "plain": flat(n)})
        for cn in r["critical"]:
            kind, num = cn["line"][0], int(cn["line"][1:])
            if num > (len(r["lines"]) if kind == "L" else len(r["notes"])):
                raise SystemExit(f"{pid}: critical note {cn['id']} on {cn['line']}, which the page does not have")
            crit.append((cn["id"], f"{pid}-{cn['line']}", cn["class"], cn["printed"], cn["proposed"], cn["evidence"],
                         cn["confidence"], cn["impact"]))
        if r["kind"] == "blank":
            tex.append(r"\Withheld{blank}")
        for o in r["obs"]:
            evid.append((pid, "observation", o))
        for u in r["unres"]:
            unres.append((pid, u))
        for c in r["copy"]:
            copyrows.append((pid, c))
        row = inv.get(pg, {})
        disp.append((pid, pg, row.get("raw_stream_sha256", ""), row.get("decoded_pixels_sha256", ""), r["printed"],
                     r["kind"], ROLE[r["kind"]], len(r["lines"]), len(r["notes"]),
                     "transcribed" if r["kind"] in ("text", "title") else "recorded"))
        out = {"anchor": pid, "pdf_page": pg, "printed_page": r["printed"], "kind": r["kind"], "role": ROLE[r["kind"]],
               "image_raw_stream_sha256": row.get("raw_stream_sha256"),
               "image_decoded_pixels_sha256": row.get("decoded_pixels_sha256"),
               "comment": " ".join(r["comment"]), "lines": out_lines, "unresolved": r["unres"],
               "observations": r["obs"], "copy_matter": r["copy"], "critical_notes": r["critical"]}
        (HERE / "records" / f"{pid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    # the pages of the file outside this lane: one range disposition
    disp.append(("AK15-P011-P320", "11-320", "", "", "-", "excluded", "OTHER_WORKS (the ten other treatises of the "
                 "collection, from al-Nayrizi's on the drawing of the hour lines, PDF 11, to the end)", 0, 0,
                 "out of scope: range disposition only"))
    if crit:
        tex.append(r"\clearpage\pdfbookmark[1]{critical notes}{critical}{\large\bfseries Critical notes}\par\medskip"
                   r"\noindent These notes are not part of the transcription. They record errors of the printed "
                   r"witness and propose corrections; the transcription keeps the print.\par\medskip")
        for c in crit:
            tex.append(r"\noindent\textbf{" + esc(c[0]) + r"}\enspace\hyperlink{" + c[1] + "}{" + esc(c[1]) +
                       r"}\enspace(" + esc(c[2]) + r")\par\noindent printed: " + mixed(c[3]) + r"\enspace proposed: " +
                       mixed(c[4]) + r"\par\noindent " + mixed(c[5]) + r"\par\noindent confidence: " + mixed(c[6]) +
                       r"\par\noindent impact: " + mixed(c[7]) + r"\par\medskip")
    tex.append(r"\end{document}")
    (HERE / "calendar_1947.tex").write_text("\n".join(tex) + "\n", encoding="utf-8", newline="\n")

    def tsv(name, head, rows):
        with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(head) + "\n")
            for row in rows:
                fh.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    tsv("anchors.tsv", ["anchor", "pdf_page", "printed_page", "line", "kind", "text"], anchors)
    tsv("physical_unit_disposition.tsv", ["anchor", "pdf_page", "image_raw_stream_sha256", "image_decoded_pixels_sha256",
                                          "printed_page", "kind", "role", "lines", "note_lines", "disposition"], disp)
    tsv("evidence_ledger.tsv", ["anchor", "kind", "text"], evid)
    tsv("unresolved_readings.tsv", ["anchor", "reading"], unres)
    tsv("copy_provenance.tsv", ["anchor", "matter"], copyrows)
    tsv("critical_findings.tsv", ["id", "anchor", "issue_class", "diplomatic_reading", "proposed_critical_reading",
                                  "evidence", "confidence", "propagation_impact"], crit)
    tsv("witness_variants.tsv", ["anchor", "witnesses", "variant"], [])
    tsv("figure_provenance.tsv", ["figure", "anchor", "source", "rect", "raw_sha256", "derivative_sha256", "status"], [])
    tsv("formula_table_ledger.tsv", ["anchor", "kind", "coverage", "verification", "companion"], FORMULAS)
    tsv("proposed_corrections.tsv", ["anchor", "current_reading", "proposal", "evidence", "confidence", "state"], [])
    tsv("language_synchronization.tsv", ["language", "canonical_checkpoint", "replay_state", "proposals", "state"], [])
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    last = max(nums)
    ck = {"lane": "AK15 Jewish calendar (Hyderabad edition, 1947; packet file 60, PDF pages 1-10)",
          "packet_file_sha256": PACKET_PDF_SHA,
          "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the page files in order: file name, a NUL byte, the bytes",
          "last_fully_transcribed_source_unit": f"PDF{last:03d}",
          "last_fully_verified_source_unit": f"PDF{last:03d}",
          "first_untouched_source_unit": f"PDF{last + 1:03d}" if last < 10 else None,
          "owned_units_total": 10, "owned_units_disposed": len(recs),
          "excluded_range": "PDF011-PDF320 (range disposition)",
          "unresolved_count": len(unres), "figure_count": 0, "formula_or_table_count": len(FORMULAS),
          "critical_notes": len(crit), "text_lines": n_text,
          "note_lines": sum(len(r["notes"]) for r in recs)}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(recs)} pages ({nums[0]}-{nums[-1]}), {len(anchors)} lines ({n_text} of the text), "
          f"{len(evid)} observations, {len(crit)} critical notes")


if __name__ == "__main__":
    main()
