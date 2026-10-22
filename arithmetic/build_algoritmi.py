"""Algoritmi de numero Indorum, the Latin arithmetic that begins «Dixit algorizmi», in the edition of Baldassarre
Boncompagni (Trattati d'aritmetica I, Rome: Tipografia delle scienze fisiche e matematiche, 1857), from the Cambridge
manuscript University Library Ii.6.5, ff. 102r-109v; the copy of the Bayerische Staatsbibliothek, digitised by the
Munich digitisation centre (bsb10525392, 30 frames): the line-anchored transcription of the frames, one line of this
edition for each printed line. The Latin text is a witness of the lost Arabic arithmetic of al-Khwarizmi, not that
text itself. Boncompagni died in 1894: his title page and footnotes are transcribed with the text. The Latin text and
the edition are in the public domain; this transcription is dedicated to the public domain (CC0 1.0).

Page files (pages/AK02-F###.txt, one per frame):
  @page FRAME PRINTED   the frame and the page number as printed (- none)
  @kind KIND            text (default), title, blank, provenance (copy matter only), binding
  % ...                 a comment (kept in the record)
  TEXT                  a printed line of the text; prefixes "@h " a heading (centred, larger), "@c " a centred line,
                        "@p " a line printed with a paragraph indent
  @n TEXT               a printed line of the editor's footnotes (anchored N01, N02, ...)
  @m TEXT               a note printed in the margin beside the next line (the folio of the manuscript)
  inline: {i:...} italic; {b:...} bold; {sc:...} small capitals; {sup:...} raised letters
  @variant TEXT         a reading of the manuscript reported by the editor (in our words)
  @unres TEXT           an unresolved reading
  @obs TEXT             an observation on the print
  @copy TEXT            copy matter (library stamps, readers' notes in pencil or ink): recorded, not part of the edition
  @critical ID | CLASS | Lnn | PRINTED | PROPOSED | EVIDENCE | CONFIDENCE | IMPACT   a critical note (layer 3)
Writes algoritmi_1857.tex, records/AK02-F###.json and the ledgers (see README.md). python build_algoritmi.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FRAMES = ROOT / "_intake" / "arithmetic" / "frames"
INVENTORY = ROOT / "controls" / "arithmetic_1857" / "ARITHMETIC_FRAME_INVENTORY.tsv"
TOTAL = 30
ROLE = {"text": "RECENSION_LATIN (the Latin text and its lines); MODERN_EDITORIAL (the editor's page heads, folio "
                "notes in the margin and footnotes)",
        "title": "MODERN_EDITORIAL (title page)", "blank": "blank", "provenance": "COPY_PROVENANCE",
        "binding": "COPY_PROVENANCE (binding)"}
LABEL = {"title": "title page", "blank": "blank", "provenance": "library matter", "binding": "binding"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}").replace("~", r"\~{}")
            .replace("^", r"\^{}"))


def groups(s):
    """the markup of a text as a list of plain strings and (kind, content) pairs"""
    out, i, plain = [], 0, ""
    while i < len(s):
        m = re.match(r"\{(i|b|sc|sup):", s[i:])
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
    """the letters of a text without the markup"""
    return "".join(g if isinstance(g, str) else flat(g[1]) for g in groups(s))


def latex(s):
    out = []
    for g in groups(s):
        if isinstance(g, str):
            out.append(esc(g))
        else:
            macro = {"i": r"\textit{", "b": r"\textbf{", "sc": r"\textsc{", "sup": r"\textsuperscript{"}[g[0]]
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
    rec = {"frame": None, "printed": None, "kind": "text", "lines": [], "notes": [], "variants": [], "unres": [],
           "obs": [], "copy": [], "critical": [], "comment": []}
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
        elif tag == "@m":
            margin = body
        elif tag == "@n":
            rec["notes"].append({"kind": "note", "text": body, "margin": None})
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
        elif tag in ("@h", "@c", "@p"):
            kind = {"@h": "heading", "@c": "centre", "@p": "indent"}[tag]
            rec["lines"].append({"kind": kind, "text": body, "margin": margin})
            margin = None
        elif raw.startswith("@"):
            raise SystemExit(f"{path.name}: unknown line {raw[:40]}")
        else:
            rec["lines"].append({"kind": "text", "text": raw.strip(), "margin": margin})
            margin = None
    if margin is not None:
        raise SystemExit(f"{path.name}: a margin note without a line after it")
    if rec["kind"] not in ROLE:
        raise SystemExit(f"{path.name}: unknown kind {rec['kind']}")
    for ln in rec["lines"] + rec["notes"]:
        ln["text"] = re.sub(r"\s+", " ", ln["text"]).strip()
    return rec


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,left=26mm,right=34mm,top=22mm,bottom=22mm]{geometry}
\usepackage{fontspec,needspace,xcolor}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{latin,italian}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\hypersetup{pdftitle={Algoritmi de numero Indorum, ed. Boncompagni (Rome 1857): the text, line by line},pdfauthor={the Latin Dixit algorizmi; ed. Baldassarre Boncompagni}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\tracinglostchars=2
\newcommand{\FrameHead}[4]{\par\bigskip\penalty-300\pdfbookmark[1]{frame #1 (#2)}{fr-#1}\hypertarget{AK02-F#3}{}%
 {\large\bfseries #4}\enspace{\footnotesize\color{gray}frame #1}\par\smallskip}
\newcommand{\LnStrut}{\vrule height 0.95em depth 0.35em width 0pt}
% a note in the right margin (the folio of the manuscript)
\newcommand{\Marg}[1]{\rlap{\hspace{\linewidth}\hspace{3mm}\footnotesize\color{gray}#1}}
% one printed line, with its number in the left margin
\newcommand{\EdL}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\raggedright\LnStrut #3\par}\par}
\newcommand{\EdLp}[4]{\EdL{#1}{#2}{\hspace*{6mm}#3}{#4}}
\newcommand{\EdLc}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\centering\LnStrut #3\par}\par}
\newcommand{\EdLh}[4]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}#4\parbox[t]{\linewidth}{\centering\large\LnStrut #3\par}\par\smallskip}
% a printed line of the editor's footnotes
\newcommand{\EdN}[3]{\par\noindent\hypertarget{#2}{}\llap{\footnotesize\color{gray}#1\hspace{4mm}}\parbox[t]{\linewidth}{\raggedright\footnotesize\LnStrut #3\par}\par}
\newcommand{\NoteRule}{\par\smallskip\noindent\rule{30mm}{0.4pt}\par}
\newcommand{\Withheld}[1]{\par\smallskip{\small\color{gray}[#1]}\par}
\begin{document}
"""


def front(n_text, n_notes, n_frames):
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\LARGE Algoritmi de numero Indorum\par\vspace{4mm}"
        r"\large the Latin arithmetic that begins «Dixit algorizmi»\par\vspace{5mm}"
        r"\normalsize in the edition of Baldassarre Boncompagni, \textit{Trattati d’aritmetica} I\\"
        r"(Rome: Tipografia delle scienze fisiche e matematiche, 1857), from the manuscript\\"
        r"Cambridge, University Library, Ii.6.5, ff. 102r–109v\par"
        r"\vspace{3mm}the copy of the Bayerische Staatsbibliothek (bsb10525392), frames 1–30\par"
        r"\vspace{4mm}\large the text, line by line\end{center}\vspace{6mm}",
        r"\noindent The Arabic arithmetic of Muḥammad ibn Mūsā al-Khwārizmī is lost. This Latin text, of the twelfth "
        r"century, is a witness of it, not the work itself: it was long taken for a translation of the lost treatise, "
        r"and it is a composite text, some of whose elements go back to Latin authors such as Boethius and to "
        r"Nicomachus of Gerasa (the Bibliothèque nationale de France, authority record «Dixit Algorizmi», after "
        r"A. Allard, 1990). The Cambridge manuscript is incomplete.",
        r"\par\smallskip\noindent Every printed line of the edition is one line here, in the order of the frames of "
        r"the Munich copy, with its number in the margin and its anchor AK02-F\#\#\#-L\#\#; the lines of the "
        r"editor’s footnotes, which he wrote in Italian, follow below a short rule with the anchors N\#\#. The text is "
        r"transcribed letter for letter as printed: the spelling of the manuscript that the edition keeps "
        r"(u for v, e for ae, and the numerals between points), its punctuation, small capitals and italics, and the "
        r"words divided at the ends of the lines. The folios of the manuscript, which the edition prints in the "
        r"margin, are set in the margin. Library stamps and the readers’ notes written in this copy are recorded in "
        r"the page records, not reproduced. Where the print is in error, the transcription keeps it; the critical "
        r"notes at the end, which are not part of the transcription, propose the correction.",
        r"\par\smallskip\noindent The Latin text and the edition are in the public domain, and this transcription is "
        r"dedicated to the public domain (CC0 1.0). It is AI-integrated work (Claude); no person has proofread it. "
        rf"This file holds {n_text} lines of the text and {n_notes} lines of the footnotes from {n_frames} frames."
        r"\par\clearpage"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inv = {int(r["physical_unit"]): r for r in csv.DictReader(open(INVENTORY, encoding="utf-8"), delimiter="\t")}
    pages = sorted((HERE / "pages").glob("AK02-F*.txt"))
    recs = [parse(p) for p in pages]
    frames = [r["frame"] for r in recs]
    assert frames == sorted(set(frames)), "frames out of order or repeated"
    assert frames == list(range(1, len(frames) + 1)), "frames not continuous from 1"
    for p, r in zip(pages, recs):
        if p.name != f"AK02-F{r['frame']:03d}.txt":
            raise SystemExit(f"{p.name}: the @page line names frame {r['frame']}")
        data = (FRAMES / inv[r["frame"]]["filename"]).read_bytes()
        if sha(data).upper() != inv[r["frame"]]["sha256"].upper():
            raise SystemExit(f"frame {r['frame']}: the image is not the inventory's")
    n_text = sum(len(r["lines"]) for r in recs if r["kind"] == "text")
    n_notes = sum(len(r["notes"]) for r in recs)
    tex = [PREAMBLE, front(n_text, n_notes, len(recs))]
    anchors, disp, evid, unres, variants, copyrows, crit = [], [], [], [], [], [], []
    (HERE / "records").mkdir(exist_ok=True)
    for r in recs:
        fr = r["frame"]
        fid = f"AK02-F{fr:03d}"
        label = f"p. {r['printed']}" if r["printed"] != "-" else LABEL.get(r["kind"], "unnumbered")
        tex.append(r"\FrameHead{" + str(fr) + "}{" + esc(label) + "}{" + f"{fr:03d}" + "}{" + esc(label) + "}")
        out_lines = []
        for k, ln in enumerate(r["lines"], 1):
            aid = f"{fid}-L{k:02d}"
            marg = r"\Marg{" + latex(ln["margin"]) + "}" if ln["margin"] else ""
            macro = {"text": r"\EdL", "indent": r"\EdLp", "centre": r"\EdLc", "heading": r"\EdLh"}[ln["kind"]]
            tex.append(macro + "{" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}{" + marg + "}")
            anchors.append((aid, fr, r["printed"], f"L{k:02d}", ln["kind"], ln["text"], ln["margin"] or ""))
            out_lines.append({"id": aid, "n": k, "kind": ln["kind"], "text": ln["text"], "margin": ln["margin"],
                              "plain": flat(ln["text"]), "italic": marked(ln["text"], "i"),
                              "small_caps": marked(ln["text"], "sc"), "bold": marked(ln["text"], "b")})
        if r["notes"]:
            tex.append(r"\NoteRule")
        for k, ln in enumerate(r["notes"], 1):
            aid = f"{fid}-N{k:02d}"
            tex.append(r"\EdN{N" + str(k) + "}{" + aid + "}{" + latex(ln["text"]) + "}")
            anchors.append((aid, fr, r["printed"], f"N{k:02d}", "note", ln["text"], ""))
            out_lines.append({"id": aid, "n": k, "kind": "note", "text": ln["text"], "margin": None,
                              "plain": flat(ln["text"]), "italic": marked(ln["text"], "i"),
                              "small_caps": marked(ln["text"], "sc"), "bold": marked(ln["text"], "b")})
        for cn in r["critical"]:
            n = int(cn["line"][1:])
            if n > len(r["lines"] if cn["line"][0] == "L" else r["notes"]):
                raise SystemExit(f"{fid}: critical note {cn['id']} on {cn['line']}, which the page does not have")
            crit.append((cn["id"], f"{fid}-{cn['line']}", cn["class"], cn["printed"], cn["proposed"], cn["evidence"],
                         cn["confidence"], cn["impact"]))
        if r["kind"] == "blank":
            tex.append(r"\Withheld{blank}")
        elif r["kind"] in ("provenance", "binding"):
            tex.append(r"\Withheld{" + {"provenance": "library matter only", "binding": "the library's binding"}[
                r["kind"]] + ": " + esc("; ".join(r["copy"])) + "}")
        for o in r["obs"]:
            evid.append((fid, "observation", o))
        for v in r["variants"]:
            variants.append((fid, "Boncompagni edition 1857 | Cambridge UL Ii.6.5 (as the editor reports it)", v))
        for u in r["unres"]:
            unres.append((fid, u))
        for c in r["copy"]:
            copyrows.append((fid, c))
        disp.append((fid, fr, inv[fr]["filename"], inv[fr]["sha256"].lower(), r["printed"], r["kind"], ROLE[r["kind"]],
                     len(r["lines"]), len(r["notes"]),
                     "transcribed" if r["kind"] in ("text", "title") else
                     ("recorded, not reproduced" if r["kind"] in ("provenance", "binding") else "recorded")))
        out = {"anchor": fid, "frame": fr, "frame_file": inv[fr]["filename"], "frame_sha256": inv[fr]["sha256"].lower(),
               "printed_page": r["printed"], "kind": r["kind"], "role": ROLE[r["kind"]],
               "comment": " ".join(r["comment"]), "lines": out_lines, "variants": r["variants"],
               "unresolved": r["unres"], "observations": r["obs"], "copy_matter": r["copy"],
               "critical_notes": r["critical"]}
        (HERE / "records" / f"{fid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    if crit:
        tex.append(r"\clearpage\pdfbookmark[1]{critical notes}{critical}{\large\bfseries Critical notes}\par\medskip"
                   r"\noindent These notes are not part of the transcription. They record errors of the print and "
                   r"propose corrections; the transcription keeps the print.\par\medskip")
        for c in crit:
            tex.append(r"\noindent\textbf{" + esc(c[0]) + r"}\enspace\hyperlink{" + c[1] + "}{" + esc(c[1]) + r"}\enspace"
                       r"(" + esc(c[2]) + r")\par\noindent printed: " + latex(c[3]) + r"\enspace proposed: " +
                       latex(c[4]) + r"\par\noindent " + esc(c[5]) + r"\par\noindent confidence: " + esc(c[6]) +
                       r"\par\noindent impact: " + esc(c[7]) + r"\par\medskip")
    tex.append(r"\end{document}")
    (HERE / "algoritmi_1857.tex").write_text("\n".join(tex) + "\n", encoding="utf-8", newline="\n")

    def tsv(name, head, rows):
        with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join(head) + "\n")
            for row in rows:
                fh.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    tsv("anchors.tsv", ["anchor", "frame", "printed_page", "line", "kind", "text", "margin"], anchors)
    tsv("physical_unit_disposition.tsv", ["anchor", "frame", "frame_file", "frame_sha256", "printed_page", "kind",
                                          "role", "text_lines", "note_lines", "disposition"], disp)
    tsv("evidence_ledger.tsv", ["anchor", "kind", "text"], evid)
    tsv("unresolved_readings.tsv", ["anchor", "reading"], unres)
    tsv("witness_variants.tsv", ["anchor", "witnesses", "variant"], variants)
    tsv("copy_provenance.tsv", ["anchor", "matter"], copyrows)
    tsv("critical_findings.tsv", ["id", "anchor", "issue_class", "diplomatic_reading", "proposed_critical_reading",
                                  "evidence", "confidence", "propagation_impact"], crit)
    tsv("proposed_corrections.tsv", ["anchor", "current_reading", "proposal", "evidence", "confidence", "state"], [])
    tsv("language_synchronization.tsv", ["language", "canonical_checkpoint", "replay_state", "proposals", "state"], [])
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    last = max(frames)
    ck = {"lane": "AK02 arithmetic (Boncompagni 1857, the Munich copy, 30 frames)",
          "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the page files in order: file name, a NUL byte, the bytes",
          "last_fully_transcribed_source_unit": f"frame{last:03d}",
          "last_fully_verified_source_unit": f"frame{last:03d}",
          "first_untouched_source_unit": f"frame{last + 1:03d}" if last < TOTAL else None,
          "owned_units_total": TOTAL, "owned_units_disposed": len(recs),
          "unresolved_count": len(unres), "critical_notes": len(crit), "text_lines": n_text, "note_lines": n_notes}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(recs)} frames ({frames[0]}-{frames[-1]}), {len(anchors)} lines ({n_text} of the text, {n_notes} of "
          f"the notes), {len(evid)} observations, {len(copyrows)} copy records, {len(crit)} critical notes")


if __name__ == "__main__":
    main()
