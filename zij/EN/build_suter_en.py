"""The English translation of Heinrich Suter's German matter in his edition of al-Khwarizmi's astronomical tables
(Copenhagen, 1914): check the unit files against the line-anchored transcription of the edition and write the TeX.

The German is read from ../anchors.tsv (one printed line per row: anchor, JP2 image, printed page, line, kind, text).
units.tsv lists the units in the order of the book: unit, part, title, and its lines (RANGES, as below; no line is in
two units). Each unit is one file text/<unit>.txt:
  @unit ID
  % ...                       a comment
  @part RANGES                the title of a part of the book; the English on the next line
  @h RANGES                   a heading
  @c RANGES                   a centred line
  @r RANGES                   a line set to the right (the signature of the foreword)
  @p RANGES                   a paragraph
  @p+ RANGES                  a paragraph that goes on from the last paragraph of the unit before
  @m RANGES                   display formulas, one per line, in TeX math
  @e RANGES                   an entry of the glossary or the index (a compact paragraph with a hanging indent)
  @e+ RANGES                  an entry that goes on from the last entry of the unit before
  @t [spec=lrr] [size=footnotesize] RANGES   a table: one row per line, cells separated by " | "; a row beginning
                              "! " is a heading; a cell "<N> text" spans N columns; "---" is a rule
  @f KEY RANGES               one of Suter's footnotes; the block that calls it has [^KEY] where his number stands
                              (KEY is the printed page and the number of the note: XI.3, 45.1)
  @n TEXT                     a translator's note to the block before it
RANGES is FIRST..LAST, or one anchor, or several of these joined by " + ". An anchor is written in full
(AK07-J0011-L02) or short (0011L02, 0276L100; 0011N01 for a line of the footnotes). Every line of a unit belongs to one block; a
line may also end one block and begin another, where a sentence ends inside it. Every footnote is called once.
Inline: *...* italics, **...** bold, $...$ and \\[...\\] TeX math; Greek and the astronomical signs are set in
FreeSerif.

python build_suter_en.py   (writes suter_en.tex, alignment.tsv and checkpoint.json; fails on any error)"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZIJ = HERE.parent
csv.field_size_limit(10 ** 8)
PARTS = (("F", "the title page, the contents, the foreword and the introduction"), ("K", "the commentary"),
         ("B", "the additions and corrections"), ("G", "the glossary"), ("I", "the index"))


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))


def load_source():
    rows, where = [], {}
    for r in read_tsv(ZIJ / "anchors.tsv"):
        where[r["anchor"]] = len(rows)
        rows.append({"anchor": r["anchor"], "page": r["printed_page"].strip("[]"), "kind": r["kind"],
                     "text": r["text"], "jp2": int(r["jp2_index"])})
    return rows, where


def full(a):
    m = re.fullmatch(r"(\d{4})([LN]\d{2,3})", a)
    return f"AK07-J{m.group(1)}-{m.group(2)}" if m else a


def ranges_of(spec):
    out = []
    for part in spec.split(" + "):
        a, _, z = part.strip().partition("..")
        out.append((full(a), full(z or a)))
    return out


def parse(path):
    unit, blocks = None, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("%"):
            continue
        if raw.startswith("@unit "):
            unit = raw.split()[1]
            continue
        if raw.startswith("@n "):
            blocks[-1]["notes"].append(raw[3:].strip())
            continue
        m = re.match(r"@(part|h|c|r|p\+?|m|e\+?) (.+)$", raw)
        if m:
            blocks.append({"kind": m.group(1).rstrip("+"), "cont": m.group(1).endswith("+"), "ranges": ranges_of(m.group(2)),
                           "text": [], "notes": []})
            continue
        m = re.match(r"@t (?:spec=(\S+) )?(?:size=(\w+) )?(.+)$", raw)
        if m:
            blocks.append({"kind": "t", "spec": m.group(1), "size": m.group(2), "ranges": ranges_of(m.group(3)),
                           "text": [], "notes": []})
            continue
        m = re.match(r"@f (\S+) (.+)$", raw)
        if m:
            blocks.append({"kind": "f", "key": m.group(1), "ranges": ranges_of(m.group(2)), "text": [], "notes": []})
            continue
        if raw.startswith("@"):
            raise SystemExit(f"{path.name}: unknown line {raw[:50]}")
        blocks[-1]["text"].append(raw.rstrip() if blocks[-1]["kind"] in ("m", "t") else raw.strip())
    return unit, blocks


def check(unit, blocks, rows, where, allowed):
    errors, count, ends = [], {}, {}
    for k, b in enumerate(blocks):
        if not b["text"]:
            errors.append(f"block {k}: no English")
        for a, z in b["ranges"]:
            if a not in where or z not in where:
                errors.append(f"block {k}: unknown anchor {a if a not in where else z}")
                continue
            i, j = where[a], where[z]
            if i > j or any(x not in allowed for x in range(i, j + 1)):
                errors.append(f"block {k}: range {a}..{z} out of order or outside the unit")
                continue
            for x in range(i, j + 1):
                count[x] = count.get(x, 0) + 1
                ends.setdefault(x, []).append("first" if x == i else "last" if x == j else "mid")
    for x, n in count.items():
        if n > 2 or (n == 2 and sorted(ends[x]) != ["first", "last"]):
            errors.append(f"{rows[x]['anchor']} is in {n} blocks")
    missing = [rows[x]["anchor"] for x in sorted(allowed) if x not in count]
    if missing:
        errors.append(f"not translated: {', '.join(missing[:6])}{' …' if len(missing) > 6 else ''} ({len(missing)})")
    keys = [b["key"] for b in blocks if b["kind"] == "f"]
    calls = [c for b in blocks for line in b["text"] for c in re.findall(r"\[\^([^\]]+)\]", line) if c != "n"]
    for k, b in enumerate(blocks):
        if sum(line.count("[^n]") for line in b["text"]) != len(b["notes"]) and b["kind"] != "f":
            errors.append(f"block {k}: {sum(line.count('[^n]') for line in b['text'])} [^n] marks, "
                          f"{len(b['notes'])} notes")
    for key in set(keys) | set(calls):
        if keys.count(key) != 1 or calls.count(key) != 1:
            errors.append(f"footnote {key}: {keys.count(key)} texts, {calls.count(key)} calls")
    return [f"{unit}: {e}" for e in errors]


def tex_escape(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
            .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}").replace("^", r"\^{}")
            .replace("~", r"\textasciitilde{}"))


_GR = f"{chr(0x370)}-{chr(0x3FF)}{chr(0x1F00)}-{chr(0x1FFF)}"
GREEK_RUN = re.compile(rf"([{_GR}](?:[{_GR}\s’',.]*[{_GR}])?)")
SIGNS = "☉☽☾♈-♓☿♀♂♃♄⊙☊☋∢∶∽∓∥∠†"


def plain(s):
    s = tex_escape(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", s)
    s = GREEK_RUN.sub(r"{\\greekfont \1}", s)
    s = re.sub(rf"([{SIGNS}])", r"{\\SignFont\\upshape \1}", s)   # Linux Libertine lacks these signs
    return s


def display(math):
    return r"\par\smallskip\noindent\hspace*{1.5em}$\displaystyle " + math + r"$\par\smallskip"


def inline(s, notes=None, tn=None):
    """the English of a block: math passes as TeX; [^KEY] becomes Suter's footnote, [^n] the next note of the
    translator"""
    out = []
    for part in re.split(r"(\\\[.*?\\\]|\$[^$]+\$|\[\^[^\]]+\])", s):
        if part == "[^n]":
            out.append(r"\footnoteT{" + tn.pop(0) + "}")
        elif part.startswith("[^"):
            out.append(r"\footnote{" + notes[part[2:-1]] + "}")
        elif part.startswith(r"\["):
            out.append(display(part[2:-2].strip()))
        elif part.startswith("$"):
            out.append(part)
        else:
            out.append(plain(part))
    return "".join(out)


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,left=28mm,right=32mm,top=25mm,bottom=25mm,marginparwidth=18mm,marginparsep=4mm]{geometry}
\usepackage{fontspec,amsmath,amssymb,xcolor,needspace,array,booktabs}
\usepackage{manyfoot,perpage}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{greek,german,latin}
\setmainfont{Linux Libertine O}[Ligatures=TeX]
\setlength{\emergencystretch}{1.5em}
\newfontfamily\greekfont{FreeSerif}[Script=Greek]
\newfontfamily\SignFont{FreeSerif}
\DeclareNewFootnote{T}[alph]
\MakePerPage{footnote}\MakePerPage{footnoteT}
\makeatletter
\newcommand{\TNoteLetter}[1]{\ifnum#1>26 \@alph{\numexpr(#1-14)/26\relax}\@alph{\numexpr#1-26*((#1-14)/26)\relax}\else\@alph{#1}\fi}
\renewcommand{\thefootnoteT}{\TNoteLetter{\value{footnoteT}}}
\makeatother
\hypersetup{pdftitle={H. Suter, the German matter of his edition of al-Khwarizmi's astronomical tables: an English translation},pdfauthor={H. Suter}}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.55em}
\tracinglostchars=2
\newcommand{\Pg}[1]{\marginpar{\footnotesize\color{gray}#1}}
\newcommand{\Entry}[1]{\par{\parskip=0.2em\relax\noindent\hangindent=1.5em\hangafter=1 #1\par}}
\newcommand{\PartHead}[2]{\clearpage\pdfbookmark[0]{#1}{part-#2}{\centering\LARGE #1\par}\bigskip}
\newcommand{\UnitHead}[3]{\par\needspace{8\baselineskip}\bigskip\pdfbookmark[1]{#2}{unit-#3}\hypertarget{EN-#3}{}%
 {\large\bfseries\interlinepenalty=10000 #1\par}\nobreak\medskip}
\begin{document}
"""


def front(done):
    return "\n".join([
        r"\thispagestyle{empty}",
        r"\begin{center}\Large H. SUTER\par\vspace{4mm}\LARGE The Astronomical Tables of\par al-Khwārizmī\par"
        r"\vspace{2mm}\large the foreword, the introduction, the commentary, the additions, the glossary and the index"
        r" of his edition (Copenhagen, 1914)\par\vspace{5mm}\normalsize translated from the German\end{center}"
        r"\vspace{8mm}",
        r"\noindent Heinrich Suter's \emph{Die astronomischen Tafeln des Muḥammed ibn Mūsā al-Khwārizmī} (Copenhagen, "
        r"1914), on the preliminary work of A. Bjørnbo and R. Besthorn, edits the astronomical tables of "
        r"al-Khwārizmī in the recension of Maslama ibn Aḥmad al-Majrīṭī and the Latin translation of Adelard of Bath. "
        r"The Latin text and tables were translated into English by O. Neugebauer (\emph{The Astronomical Tables of "
        r"al-Khwārizmī}, Copenhagen, 1962), with his own commentary; Suter's German, his foreword, introduction, "
        r"commentary, additions, glossary and index, has not been translated before. This volume translates it from "
        r"the line-by-line transcription of the edition in this repository. Every sentence is translated, in "
        r"Suter's order; nothing is summarised or left out. The words of the Latin text that Suter quotes are kept, "
        r"followed by an English translation in parentheses; Greek stands as printed. Arabic names and words are "
        r"given in a modern transliteration (j for Suter's dj, q for his ḳ), except in the glossary and the index, "
        r"which keep Suter's transcription. Suter's footnotes are numbered; the notes of the translator are lettered: they record a "
        r"misprint set right, with the reading of the print, a slip in Suter's reckoning, checked against his "
        r"numbers, and the figures of the print, which are not reproduced. The pages of Suter's book are given in the margin.",
        r"\par\smallskip\noindent " + done + ". It is AI-translated (Claude), 2026; no person has proofread it. "
        r"Suter's work is in the public domain; the translation is dedicated to the public domain (CC0 1.0).",
        r"\par\clearpage"])


def table_tex(b, notes, tn):
    """cells are split at |; a cell «<N> text» spans N columns, and « // » breaks a line within a cell"""
    def span(c):
        m = re.match(r"<(\d+)>\s*", c)
        return (int(m.group(1)), c[m.end():]) if m else (1, c)

    rows = [re.split(r"\s*\|\s*", r[2:] if r.startswith("! ") else r) for r in b["text"] if r.strip() != "---"]
    n = max(sum(span(c)[0] for c in r) for r in rows)
    spec = b.get("spec") or "l" * n
    size = b.get("size") or "small"
    out, texts, ttexts = [r"\begin{center}" + "\\" + size + r"\begin{tabular}{" + spec + "}"], [], []

    def cell(c):
        parts = []
        for part in re.split(r"(\[\^[^\]]+\])", c):
            if part == "[^n]":
                parts.append(r"\footnotemarkT{}")
                ttexts.append(tn.pop(0))
            elif part.startswith("[^"):
                parts.append(r"\footnotemark{}")
                texts.append(notes[part[2:-1]])
            else:
                parts.append(inline(part))
        return "".join(parts)

    def lines(c, head):
        parts = [(r"\emph{" + cell(p) + "}") if head and p.strip() else cell(p) for p in c.split(" // ")]
        return parts[0] if len(parts) == 1 else r"\begin{tabular}[b]{@{}c@{}}" + r"\\".join(parts) + r"\end{tabular}"

    for r in b["text"]:
        if r.strip() == "---":
            out.append(r"\midrule")
            continue
        head = r.startswith("! ")
        cells = [span(c) for c in re.split(r"\s*\|\s*", r[2:] if head else r)]
        cells += [(1, "")] * (n - sum(k for k, _ in cells))
        cells = [lines(c, head) if k == 1 else r"\multicolumn{" + str(k) + "}{c}{" + lines(c, head) + "}"
                 for k, c in cells]
        out.append(" & ".join(cells) + r" \\")
    out.append(r"\end{tabular}\end{center}")
    if texts:
        out.append(r"\addtocounter{footnote}{-" + str(len(texts)) + "}" + "".join(
            r"\stepcounter{footnote}\footnotetext{" + t + "}" for t in texts))
    if ttexts:
        out.append(r"\addtocounter{footnoteT}{-" + str(len(ttexts)) + "}" + "".join(
            r"\stepcounter{footnoteT}\footnotetextT{" + t + "}" for t in ttexts))
    return "\n".join(out)


def math_tex(b):
    return r"\par\smallskip" + "\n".join(r"\[" + line.strip() + r"\]" for line in b["text"]) + r"\par\smallskip"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows, where = load_source()
    units = read_tsv(HERE / "units.tsv")
    body, align, errors, done, covered, words = [], [], [], [], set(), 0
    owner = {}
    for u in units:
        u["set"] = set()
        for a, z in ranges_of(u["lines"]):
            for x in range(where[a], where[z] + 1):
                if x in owner:
                    errors.append(f"units.tsv: {rows[x]['anchor']} in {owner[x]} and {u['unit']}")
                owner[x] = u["unit"]
                u["set"].add(x)
    last_part, last_page = None, None
    for u in units:
        path = HERE / "text" / f"{u['unit']}.txt"
        if not path.exists():
            continue
        unit, blocks = parse(path)
        if unit != u["unit"]:
            errors.append(f"{path.name}: @unit {unit}")
        errors += check(u["unit"], blocks, rows, where, u["set"])
        if errors:
            continue
        done.append(u)
        notes = {}
        for b in blocks:
            if b["kind"] == "f":
                notes[b["key"]] = inline(" ".join(b["text"])) + "".join(
                    r" [\emph{Translator:} " + inline(x) + "]" for x in b["notes"])
        for k, b in enumerate(blocks):
            idx = [x for a, z in b["ranges"] for x in range(where[a], where[z] + 1)]
            covered.update(idx)
            if b["kind"] == "f":
                continue
            pages = []
            for x in idx:
                if rows[x]["kind"] != "note" and rows[x]["page"] not in pages and rows[x]["page"] != "-":
                    pages.append(rows[x]["page"])
            mark = "".join(r"\Pg{" + p + "}" for p in pages if p != last_page)
            last_page = pages[-1] if pages else last_page
            text = " ".join(b["text"])
            tn = [inline(x) for x in b["notes"]]
            if b["kind"] in ("part", "h", "c", "r", "p", "e"):
                text = inline(text, notes, tn)
            elif b["kind"] == "m":
                text = math_tex(b)
            tnotes = "".join(r"\footnoteT{" + x + "}" for x in tn)
            if b["kind"] == "part":
                if u["part"] != last_part:
                    body.append(r"\PartHead{" + text + "}{" + u["part"] + "}" + mark)
            elif b["kind"] == "h":
                bookmark = plain(re.sub(r"\[\^[^\]]+\]|\$[^$]*\$|\*", "", re.sub(r"\$\^\{(\w+)\}\$", r"\1",
                                                                                  " ".join(b["text"]))))  # no notes, no math
                body.append(r"\UnitHead{" + text + tnotes + "}{" + bookmark + "}{" + u["unit"] + f"-{k}" + "}" + mark)
            elif b["kind"] == "c":
                body.append(r"\par\begin{center}" + mark + text + tnotes + r"\end{center}")
            elif b["kind"] == "r":
                body.append(r"\par\noindent\hfill " + mark + text + tnotes + r"\par")
            elif b["kind"] == "p" and b["cont"] and body and body[-1].endswith(r"\par"):  # @p+: the same paragraph
                body[-1] = body[-1][:-len(r"\par")] + " " + mark + text + tnotes + r"\par"
            elif b["kind"] == "p":
                body.append(r"\par " + mark + text + tnotes + r"\par")
            elif b["kind"] == "e" and b["cont"] and body and body[-1].startswith(r"\Entry{"):  # @e+: the same entry
                body[-1] = body[-1][:-1] + " " + mark + text + tnotes + "}"
            elif b["kind"] == "e":
                body.append(r"\Entry{" + mark + text + tnotes + "}")
            elif b["kind"] == "m":
                body.append(mark + text + tnotes)
            elif b["kind"] == "t":
                body.append(mark + table_tex(b, notes, tn) + "".join(r"\footnoteT{" + x + "}" for x in tn))
            n = len(re.sub(r"\$[^$]*\$|\\\[.*?\\\]", "", " ".join(b["text"])).split())
            words += n
            align.append((f"EN-{u['unit']}-B{k:02d}", u["unit"], b["kind"],
                          " + ".join(f"{a}..{z}" for a, z in b["ranges"]), " ".join(pages), n))
        last_part = u["part"]
    if errors:
        for e in errors:
            print("ERROR", e)
        raise SystemExit(1)
    held = []
    for part, name in PARTS:
        mine = [u for u in units if u["part"] == part]
        got = [u for u in done if u["part"] == part]
        pages = [rows[x]["page"] for u in got for x in sorted(u["set"]) if rows[x]["kind"] != "note"]
        if got:
            held.append(("the whole of " if len(got) == len(mine) else "") + name + f" (pp. {pages[0]}–{pages[-1]})")
    if len(held) == len(PARTS) and all(u in done for u in units):
        status = "The translation is complete"
    else:
        status = ("The translation is in progress. This version holds " + ", ".join(held[:-1]) + " and " + held[-1]
                  if len(held) > 1 else "The translation is in progress. This version holds " + "".join(held))
    tex = [PREAMBLE, front(status)] + body + [r"\end{document}"]
    (HERE / "suter_en.tex").write_text("\n".join(tex) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "alignment.tsv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("block\tunit\tkind\tlines\tpages\tenglish_words\n")
        for row in align:
            fh.write("\t".join(str(x) for x in row) + "\n")
    h = hashlib.sha256()
    for u in done:
        f = HERE / "text" / f"{u['unit']}.txt"
        h.update(f.name.encode() + b"\0" + f.read_bytes())
    ck = {"edition": "EN: English translation of Suter's German matter in his edition of al-Khwarizmi's tables",
          "units_done": [u["unit"] for u in done], "german_lines_translated": len(covered), "blocks": len(align),
          "english_words": words, "canonical_source_checkpoint_sha256": h.hexdigest(),
          "canonical_source_checkpoint_note": "SHA-256 over the unit files in order: file name, a NUL byte, the bytes"}
    (HERE / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(f"{len(done)} units: {len(covered)} German lines, {len(align)} blocks, {words} words")


if __name__ == "__main__":
    main()
