"""AK-I01: the integration of the sealed session returns of the al-Khwarizmi project. No new transcription.

Reads the lanes (algebra, geography, arithmetic, zij, practical, calendar) and the packet controls in controls/, and
  - proves the coverage of every owned source unit against the session map: no gap, no overlap (COVERAGE.tsv);
  - replays the seams between the sessions and the named seams of the session map, and the catchwords (SEAMS.tsv);
  - lists every figure, table, blank, corrigendum, colophon or explicit, scan card, excluded range and trailing leaf
    with its disposition (SPECIAL_UNITS.tsv);
  - keeps every work and every lost, doubtful, attributed and recensional row of the packet visible
    (WORKS_AND_BOUNDARIES.tsv);
  - assembles each source-language witness, and each editor's layer in another language, as a separate monolingual
    artifact (witnesses/), and proves that together they hold every transcribed line of the lane exactly once;
  - checks the page files against the dispositions, the canonical checkpoints, the checksums of the practical returns,
    the anchors of the critical notes and the files of the figures;
  - writes INTEGRATION_CHECKPOINT.json.
No translation exists in any lane, so there are no target-language artifacts and nothing to synchronize.

python integrate.py [--out DIR]   (default: this folder; the cold audit writes elsewhere and compares)
Exit status 1 if a check fails."""
import collections
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTROLS = ROOT / "controls"
DATE = "2026-10-22"

LANES = [
    {"lane": "algebra", "work": "AK01", "source": "ALGEBRA", "col": "frame", "fmt": "AK01-F{:03d}"},
    {"lane": "geography", "work": "AK05", "source": "GEOGRAPHY", "col": "frame", "fmt": "AK05-F{:03d}"},
    {"lane": "arithmetic", "work": "AK02", "source": "ARITHMETIC", "col": "frame", "fmt": "AK02-F{:03d}"},
    {"lane": "zij", "work": "AK07", "source": "ZIJ", "col": "jp2_index", "fmt": "AK07-J{:04d}"},
    {"lane": "calendar", "work": "AK15", "source": "CALENDAR", "col": "pdf_page", "fmt": "AK15-P{:03d}"},
]
READINESS = {
    "algebra": "READY: the Arabic printed witness (1939 edition), complete; the editors' preface, study and footnotes "
               "recorded, not reproduced",
    "geography": "READY: the Arabic printed witness (Mzik's edition in the 1962 reprint), complete; the German editorial "
                 "matter a separate layer; the German introduction and footnotes recorded, not reproduced",
    "arithmetic": "READY_LATIN_WITNESS: the Latin witness (Boncompagni 1857), complete to the point where it breaks "
                  "off; the Arabic original is lost and is not reconstructed",
    "zij": "READY_DERIVATIVE_RECENSION: the Latin recension of Maslama and Adelard in Suter's edition, complete, with "
           "Suter's German matter as a separate layer; never an Arabic original",
    "practical": "EVIDENCE_ONLY: an evidence and attribution audit of the modern study and the 1987 article; no source "
                 "text produced; Berlin Landberg 56 ff. 77r-97v checked on public images; Istanbul Ayasofya 4830 held "
                 "(no images)",
    "calendar": "READY_PRINTED_WITH_ERRORS: the Arabic printed witness (Hyderabad 1947), complete, with Layer 3 "
                "critical notes; the Patna manuscript not seen",
}
# the units that a rule cannot find: corrigenda, colophons and explicits, ends of text
NAMED = [
    ("algebra", 122, "colophon", "the last page of the text, with the copyist's colophon"),
    ("geography", 164, "end of text", "the last page of the text, printed p. 158"),
    ("geography", 169, "corrigendum", "the editor's additions and corrections, «Nachträge und Verbesserungen», in "
     "German: recorded, not reproduced; each correction recorded on the page it concerns (critical notes, variants)"),
    ("arithmetic", 29, "end of text", "printed p. 23, where the text breaks off"),
    ("zij", 263, "explicit", "Tab. 116, p. 231, with the explicit of manuscript O in the apparatus"),
    ("zij", 265, "corrigendum", "Additions and corrections, p. [233]"),
    ("zij", 266, "corrigendum", "Additions and corrections, p. 234"),
    ("zij", 267, "corrigendum", "Additions and corrections, p. 235"),
    ("zij", 268, "corrigendum", "Additions and corrections, p. 236"),
    ("zij", 269, "corrigendum", "the errata slip «Nachtrag zu den Berichtigungen»"),
    ("zij", 271, "corrigendum", "the list of misprints, p. [237]"),
    ("calendar", 10, "explicit", "the explicit «تم تاريخ اليهود عن محمد بن موسى الخوارزمى», L13-L14"),
]
# seams named in the session map, besides the seams between sessions
NAMED_SEAMS = [
    ("geography", 109, 110, "the seam of the two frame archives (packet files 20 and 21)"),
    ("zij", 0, 1, "the colour card of the digitisation before the book"),
    ("zij", 138, 139, "the end of the commentary and the part title of the tables"),
    ("zij", 140, 141, "the back of the part title and Tab. 1"),
    ("zij", 294, 295, "the back cover and the colour card after the book"),
    ("calendar", 1, 2, "the title page of the collection and the title page of the treatise"),
    ("calendar", 2, 3, "the title page of the treatise and the beginning of the text"),
]
FAIL = []


def check(ok, what):
    if not ok:
        FAIL.append(what)
    return ok


def sha_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_tsv(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))


def write_tsv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = ["\t".join(header)]
    for r in rows:
        cells = [str(c) for c in r]
        assert len(cells) == len(header), (path.name, r)
        for c in cells:
            assert "\t" not in c and "\n" not in c, (path.name, c[:60])
        out.append("\t".join(cells))
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def sealed_commit(lane):
    r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", lane], capture_output=True,
                       text=True)
    return r.stdout.strip() or "unknown"


def canonical(pages):
    h = hashlib.sha256()
    for p in pages:
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def sessions():
    rows = read_tsv(CONTROLS / "05_SESSION_MAP.tsv")
    return [r for r in rows if r["session_id"] != "AK-I01"]


def load_lane(spec):
    d = ROOT / spec["lane"]
    disp = read_tsv(d / "physical_unit_disposition.tsv")
    units, excluded = collections.Counter(), []
    for r in disp:
        v = r[spec["col"]]
        if re.fullmatch(r"\d+", v):
            units[int(v)] += 1
        else:
            excluded.append(r)
    anchors = read_tsv(d / "anchors.tsv")
    return {"disp": disp, "units": units, "excluded": excluded, "anchors": anchors,
            "by_unit": {int(r[spec["col"]]): r for r in disp if re.fullmatch(r"\d+", r[spec["col"]])},
            "ck": json.loads((d / "checkpoint.json").read_text(encoding="utf-8"))}


def unit_of_anchor(a):
    return a.rsplit("-", 1)[0] if re.search(r"-[LN]\d+$", a) else a


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = HERE
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    smap = sessions()
    lanes = {s["lane"]: (s, load_lane(s)) for s in LANES}

    # ---- the transcribed lanes: page files, canonical checkpoints, anchors, critical notes, figures
    lane_report = {}
    for name, (spec, L) in lanes.items():
        d = ROOT / name
        pages = sorted((d / "pages").glob(spec["fmt"].split("-")[0] + "-*.txt"))
        want = [spec["fmt"].format(u) + ".txt" for u in sorted(L["units"])]
        check([p.name for p in pages] == want, f"{name}: the page files are not one per disposed unit")
        canon = canonical(pages)
        check(canon == L["ck"].get("canonical_source_checkpoint_sha256"), f"{name}: the canonical checkpoint differs")
        ids = [r["anchor"] for r in L["anchors"]]
        check(len(ids) == len(set(ids)), f"{name}: repeated anchors")
        anchor_units = {unit_of_anchor(a) for a in ids}
        disp_ids = {r["anchor"] for r in L["disp"]}
        check(anchor_units <= disp_ids, f"{name}: lines on units without a disposition")
        crit = read_tsv(d / "critical_findings.tsv")
        cids = [c["id"] for c in crit]
        check(len(cids) == len(set(cids)), f"{name}: repeated critical-note ids")
        bad = [c["id"] for c in crit if c["anchor"] not in set(ids) and c["anchor"] not in disp_ids]
        check(not bad, f"{name}: critical notes on unknown anchors: {bad[:5]}")
        figs = read_tsv(d / "figure_provenance.tsv") if (d / "figure_provenance.tsv").exists() else []
        for f in figs:
            for suffix, col in (("_raw.png", "raw_sha256"), (".png", "derivative_sha256")):
                fp = d / "figures" / (f["figure"] + suffix)
                check(fp.exists() and sha_file(fp) == f[col], f"{name}: figure file {fp.name} missing or changed")
        lane_report[name] = {"pages": len(pages), "canonical": canon, "anchors": len(ids), "critical": len(crit),
                             "figures": len(figs)}

    # ---- the practical returns: the evidence-only sessions
    prac = {}
    for sess in ("P01", "P02"):
        d = ROOT / "practical" / sess
        disp = read_tsv(d / "physical_unit_disposition.tsv")
        ck = json.loads((d / "checkpoint.json").read_text(encoding="utf-8"))
        files = sorted(p.name for p in d.iterdir() if p.is_file() and p.name not in ("SHA256SUMS", "checkpoint.json"))
        h = hashlib.sha256()
        for n in files:
            h.update(n.encode() + b"\0" + (d / n).read_bytes())
        check(h.hexdigest() == ck["canonical_source_checkpoint_sha256"], f"practical {sess}: canonical checkpoint")
        sums = {}
        for line in (d / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            hx, n = line.split("  ", 1)
            sums[n] = hx
        names = sorted(p.name for p in d.iterdir() if p.is_file() and p.name != "SHA256SUMS")
        check(sorted(sums) == names, f"practical {sess}: SHA256SUMS does not list the files")
        for n, hx in sums.items():
            check(sha_file(d / n) == hx, f"practical {sess}: {n} differs from SHA256SUMS")
        check(ck.get("last_fully_transcribed_source_unit") == "NONE",
              f"practical {sess}: an evidence-only session claims transcription")
        prac[sess] = {"disp": disp, "ck": ck, "canonical": h.hexdigest()}
    prac_units = collections.Counter()
    prac_extra = []
    for sess, P in prac.items():
        for r in P["disp"]:
            m = re.fullmatch(r"(?:50:)?PDF(\d{3})", r["unit"])
            if m:
                prac_units[int(m.group(1))] += 1
            else:
                prac_extra.append((sess, r["unit"], r.get("state", "")))

    # ---- coverage against the session map
    cov_rows = []
    by_source = collections.defaultdict(list)
    for s in smap:
        by_source[s["source_id"]].append(s)
    src_lane = {"ALGEBRA": "algebra", "GEOGRAPHY": "geography", "ARITHMETIC": "arithmetic", "ZIJ": "zij",
                "CALENDAR": "calendar", "PRACTICAL": "practical"}
    for src, rows in by_source.items():
        lane = src_lane[src]
        units = prac_units if lane == "practical" else lanes[lane][1]["units"]
        where = ("practical/P01, practical/P02" if lane == "practical"
                 else f"{lane}/physical_unit_disposition.tsv")
        covered = set()
        prev_end = None
        for s in rows:
            a, b = int(s["start_unit"]), int(s["end_unit"])
            rng = range(a, b + 1)
            missing = [u for u in rng if units[u] == 0]
            dup = [u for u in rng if units[u] > 1]
            abut = prev_end is None or a == prev_end + 1
            check(not missing and not dup and abut, f"coverage {s['session_id']}: missing {missing[:5]}, "
                                                    f"repeated {dup[:5]}, abuts {abut}")
            cov_rows.append((s["session_id"], src, s["owned_units"], where, len(rng), sum(units[u] for u in rng),
                             ",".join(map(str, missing)) or "-", ",".join(map(str, dup)) or "-",
                             "yes" if abut else "NO", "exact" if not missing and not dup and abut else "FAILED"))
            covered.update(rng)
            prev_end = b
        outside = sorted(u for u in units if u not in covered)
        check(not outside, f"coverage {src}: units outside the sessions: {outside[:5]}")
        cov_rows.append((f"{src} (all)", src, f"{min(covered)}-{max(covered)}", where, len(covered),
                         sum(units.values()), "-", "-", "-",
                         "exact" if not outside and sum(units.values()) == len(covered) else "FAILED"))
    cal_ex = lanes["calendar"][1]["excluded"]
    ok = (len(cal_ex) == 1 and cal_ex[0]["pdf_page"] == "11-320" and cal_ex[0]["kind"] == "excluded")
    check(ok, "calendar: the range disposition of PDF 11-320 is missing")
    cov_rows.append(("AK-C01 exclusion", "CALENDAR", "PDF011-PDF320", "calendar/physical_unit_disposition.tsv", 310,
                     "range row" if ok else "missing", "-", "-", "-", "excluded, visible" if ok else "FAILED"))
    for sess, unit, state in prac_extra:
        cov_rows.append((f"AK-{sess} additional", "PRACTICAL", unit, f"practical/{sess}", 1, 1, "-", "-", "-",
                         f"evidence unit outside the numbered range: {state}"))
    write_tsv(out / "COVERAGE.tsv", ["session", "source", "owned_units", "ledger", "expected", "disposed", "missing",
                                     "repeated", "abuts_previous", "state"], cov_rows)

    # ---- seams
    seam_rows = []

    def line_at(lane, unit, last):
        spec, L = lanes[lane]
        pref = spec["fmt"].format(unit) + "-L"
        ls = [r for r in L["anchors"] if r["anchor"].startswith(pref)]
        if not ls:
            return "-"
        r = ls[-1] if last else ls[0]
        return f"{r['anchor']} {r['text'][:80]}"

    def seam(lane, a, b, label):
        if lane == "practical":
            da = [r for P in prac.values() for r in P["disp"] if re.fullmatch(rf"(?:50:)?PDF{a:03d}", r["unit"])]
            db = [r for P in prac.values() for r in P["disp"] if re.fullmatch(rf"(?:50:)?PDF{b:03d}", r["unit"])]
            ok = len(da) == 1 and len(db) == 1
            check(ok, f"seam practical {a}|{b}")
            seam_rows.append((label, lane, f"PDF{a:03d}", da[0]["role"] if da else "-", da[0]["state"] if da else "-",
                              "-", f"PDF{b:03d}", db[0]["role"] if db else "-", db[0]["state"] if db else "-", "-",
                              "adjacent; both disposed" if ok else "FAILED"))
            return
        spec, L = lanes[lane]
        ra, rb = L["by_unit"].get(a), L["by_unit"].get(b)
        ok = ra is not None and rb is not None and b == a + 1
        check(ok, f"seam {lane} {a}|{b}")
        seam_rows.append((label, lane, spec["fmt"].format(a), ra["kind"] if ra else "-",
                          ra["disposition"] if ra else "-", line_at(lane, a, True), spec["fmt"].format(b),
                          rb["kind"] if rb else "-", rb["disposition"] if rb else "-", line_at(lane, b, False),
                          "adjacent; both disposed" if ok else "FAILED"))

    for src, rows in by_source.items():
        lane = src_lane[src]
        for s1, s2 in zip(rows, rows[1:]):
            seam(lane, int(s1["end_unit"]), int(s2["start_unit"]), f"{s1['session_id']} | {s2['session_id']}")
    for lane, a, b, label in NAMED_SEAMS:
        seam(lane, a, b, label)
    # the catchwords of the calendar: the word at the foot of a page must begin the next page
    ev = read_tsv(ROOT / "calendar" / "evidence_ledger.tsv")
    for r in ev:
        m = re.search(r"catchword «([^»]+)», the first word of p\. \S+ \(PDF (\d+)\)", r["text"])
        if not m:
            continue
        word, nxt = m.group(1), int(m.group(2))
        first = [a for a in lanes["calendar"][1]["anchors"] if a["anchor"] == f"AK15-P{nxt:03d}-L01"]
        ok = bool(first) and first[0]["text"].split()[0] == word
        check(ok, f"catchword {r['anchor']} «{word}»")
        seam_rows.append((f"catchword «{word}»", "calendar", r["anchor"], "-", "-", "-", f"AK15-P{nxt:03d}", "-", "-",
                          f"{first[0]['anchor']} {first[0]['text'][:80]}" if first else "-",
                          "the next page begins with the catchword" if ok else "FAILED"))
    write_tsv(out / "SEAMS.tsv", ["seam", "lane", "left_unit", "left_kind", "left_disposition", "left_last_line",
                                  "right_unit", "right_kind", "right_disposition", "right_first_line", "check"],
              seam_rows)

    # ---- special units
    sp = []
    for name, (spec, L) in lanes.items():
        d = ROOT / name
        figs = read_tsv(d / "figure_provenance.tsv") if (d / "figure_provenance.tsv").exists() else []
        for f in figs:
            r = L["by_unit"][int(re.search(r"\d+$", f["anchor"]).group(0))]
            sp.append((name, f["anchor"], "figure" if r["kind"] not in ("facsimile", "plate") else r["kind"],
                       r["kind"], r["disposition"], f"{f['figure']}: raw {f['raw_sha256'][:16]}, derivative "
                                                  f"{f['derivative_sha256'][:16]} (files checked)"))
        tab = collections.Counter(unit_of_anchor(a["anchor"]) for a in L["anchors"] if a["kind"] in ("row", "table"))
        for u in sorted(tab):
            r = next(x for x in L["disp"] if x["anchor"] == u)
            sp.append((name, u, "table", r["kind"], r["disposition"], f"{tab[u]} table lines"))
        for u, r in sorted(L["by_unit"].items()):
            if r["kind"] == "blank":
                sp.append((name, r["anchor"], "blank", r["kind"], r["disposition"], "-"))
            if r["kind"] == "scan":
                sp.append((name, r["anchor"], "scan card", r["kind"], r["disposition"], "-"))
        lines = collections.Counter(unit_of_anchor(a["anchor"]) for a in L["anchors"])
        has_figs = {f["anchor"] for f in figs}
        last_body = max(u for u, r in L["by_unit"].items() if lines[r["anchor"]] or r["anchor"] in has_figs)
        for u in sorted(L["by_unit"]):
            if u > last_body:
                r = L["by_unit"][u]
                sp.append((name, r["anchor"], "trailing leaf", r["kind"], r["disposition"], "after the last unit "
                                                                                          "with text or figures"))
        for r in L["excluded"]:
            sp.append((name, r["anchor"], "excluded range", r["kind"], r["disposition"], r["role"]))
    for lane, u, cls, note in NAMED:
        spec, L = lanes[lane]
        r = L["by_unit"].get(u)
        check(r is not None and bool(r["disposition"]), f"special unit {lane} {u}")
        sp.append((lane, spec["fmt"].format(u), cls, r["kind"] if r else "-", r["disposition"] if r else "-", note))
    write_tsv(out / "SPECIAL_UNITS.tsv", ["lane", "unit", "class", "kind", "disposition", "evidence"], sp)

    # ---- works and boundaries
    works = read_tsv(CONTROLS / "03_BIBLIOGRAPHY_AND_COVERAGE.tsv")
    state = {"AK01": "produced: algebra/", "AK02": "produced: arithmetic/ (the Latin witness; the Arabic is lost)",
             "AK03": "held: bibliographic authority only; not synthesized from AK02",
             "AK04": "held: a composite comparator, not authorial canon",
             "AK05": "produced: geography/",
             "AK06": "lost in Arabic: represented only through the recension AK07, never reconstructed",
             "AK07": "produced: zij/ (the Latin recension; Suter's German layer separate)",
             "AK08": "held: commentary by another author; not merged into AK07",
             "AK09": "held: derivative compilations; not interpolated",
             "AK10": "evidence only: practical/ (Text 2, Berlin Landberg 56)",
             "AK11": "evidence only: practical/ (Text 1 anonymous; attribution kept separate)",
             "AK12": "evidence only: practical/ (Ayasofya 4830 ff. 231v-235r; primary pixels held)",
             "AK13": "evidence only: practical/ (Text 9 and the table of Berlin 95r-v)",
             "AK14": "evidence only: practical/ (the anonymous items, attribution item by item)",
             "AK15": "produced: calendar/ (the printed witness, with critical notes)",
             "AK16": "lost: not fabricated"}
    wrows = []
    for w in works:
        check(w["work_id"] in state, f"work {w['work_id']} has no integration state")
        wrows.append((w["work_id"], w["tier"], w["lane"], w["canonical_title_or_identity"], w["authority_state"],
                      w["survival_or_recension_boundary"], state.get(w["work_id"], "MISSING")))
    md = (CONTROLS / "08_LOST_DOUBTFUL_ATTRIBUTION_MAP.md").read_text(encoding="utf-8")
    ismi = re.findall(r"^\| (\d+) \| (.+?) \| (.+?) \|$", md, flags=re.M)
    check(len(ismi) == 29 and [int(i[0]) for i in ismi] == list(range(1, 30)), "the 29 ISMI rows of controls/08")
    for n, title, boundary in ismi:
        plain = [re.sub(r"[*`]", "", x) for x in (title, boundary)]       # the markdown emphasis of the table
        wrows.append((f"ISMI-{int(n):02d}", "-", "-", plain[0], "ISMI database row", plain[1],
                      "visible (controls/08_LOST_DOUBTFUL_ATTRIBUTION_MAP.md)"))
    write_tsv(out / "WORKS_AND_BOUNDARIES.tsv", ["id", "tier", "lane", "title", "authority", "boundary",
                                                 "integration_state"], wrows)

    # ---- monolingual artifacts
    wdir = out / "witnesses"
    wdir.mkdir(exist_ok=True)
    zdisp = {r["anchor"]: r for r in lanes["zij"][1]["disp"]}

    def lang_of(lane, a):
        if lane in ("algebra", "calendar"):
            return "ar"
        if lane == "geography":
            return "de" if a["kind"] == "latin" else "ar"
        if lane == "zij":
            return "la" if zdisp[unit_of_anchor(a["anchor"])]["file"] == "latin" else "de"
        if lane == "arithmetic":
            u = unit_of_anchor(a["anchor"])
            if u == "AK02-F003" or a["kind"] == "note" or a["anchor"] in ("AK02-F007-L03", "AK02-F007-L04"):
                return "it"
            return "la"

    artifacts = {
        ("algebra", "ar"): ("AK01_algebra_1939.ar.tsv", "AK01", "the Arabic text as printed in the 1939 Cairo edition,"
                                                               " with the edition's cover and title page"),
        ("geography", "ar"): ("AK05_geography_1926.ar.tsv", "AK05", "the Arabic text as printed in Mzik's edition "
                                                                    "(1926; the 1962 reprint), with its Arabic index"),
        ("geography", "de"): ("AK05_geography_1926_editor.de.tsv", "AK05", "MODERN_EDITORIAL: Mzik's German title "
                                                                           "pages, the series title and the imprint"),
        ("arithmetic", "la"): ("AK02_arithmetic_1857.la.tsv", "AK02", "RECENSION_LATIN: the Latin text as printed by "
                                                                      "Boncompagni (1857)"),
        ("arithmetic", "it"): ("AK02_arithmetic_1857_editor.it.tsv", "AK02", "MODERN_EDITORIAL: Boncompagni's Italian "
                                                                             "title page, heading and footnotes"),
        ("zij", "la"): ("AK07_zij_1914.la.tsv", "AK07", "RECENSION_LATIN: the Latin text and tables of the recension "
                                                       "of Maslama and Adelard, with Suter's Latin apparatus"),
        ("zij", "de"): ("AK07_zij_1914_suter.de.tsv", "AK07", "MODERN_EDITORIAL: Suter's German title page, foreword, "
                                                             "introduction, commentary, additions, glossary, index"),
        ("calendar", "ar"): ("AK15_calendar_1947.ar.tsv", "AK15", "the Arabic text as printed in the Hyderabad edition "
                                                                  "(1947), with the two title pages"),
    }
    manifest = []
    for name, (spec, L) in lanes.items():
        parts = collections.defaultdict(list)
        for a in L["anchors"]:
            parts[lang_of(name, a)].append(a)
        has_margin = "margin" in (L["anchors"][0] if L["anchors"] else {})
        total = 0
        for lang, rows in sorted(parts.items()):
            check((name, lang) in artifacts, f"{name}: lines in {lang} without an artifact")
            fn, work, role = artifacts[(name, lang)]
            head = ["anchor", "kind", "text"] + (["margin"] if has_margin else [])
            write_tsv(wdir / fn, head, [[r["anchor"], r["kind"], r["text"]] + ([r["margin"]] if has_margin else [])
                                        for r in rows])
            manifest.append((fn, work, name, lang, role, len(rows), sha_file(wdir / fn)))
            total += len(rows)
        check(total == len(L["anchors"]), f"{name}: the artifacts do not hold every line once")
    write_tsv(wdir / "MANIFEST.tsv", ["file", "work", "lane", "language", "role", "lines", "sha256"], manifest)

    # ---- ledgers of the return protocol
    proposed = {n: len(read_tsv(ROOT / n / "proposed_corrections.tsv")) for n in lanes}
    langsync = {n: len(read_tsv(ROOT / n / "language_synchronization.tsv")) for n in lanes}
    check(all(v == 0 for v in langsync.values()), "a language_synchronization ledger is not empty")

    # ---- checkpoint
    ck = {"session": "AK-I01", "mode": "integration of sealed returns; no new transcription", "date": DATE,
          "lanes": []}
    for name, (spec, L) in lanes.items():
        c = L["ck"]
        ck["lanes"].append({"lane": name, "work": spec["work"], "sealed_commit": sealed_commit(name),
                            "canonical_source_checkpoint_sha256": lane_report[name]["canonical"],
                            "units": len(L["by_unit"]), "page_files": lane_report[name]["pages"],
                            "anchored_lines": lane_report[name]["anchors"],
                            "critical_notes": lane_report[name]["critical"], "figures": lane_report[name]["figures"],
                            "unresolved": c.get("unresolved_count"),
                            "last_fully_verified_source_unit": c.get("last_fully_verified_source_unit"),
                            "proposed_corrections": proposed[name], "readiness": READINESS[name]})
    for sess, P in prac.items():
        ck["lanes"].append({"lane": f"practical/{sess}", "work": "AK10-AK14", "sealed_commit": sealed_commit("practical"),
                            "canonical_source_checkpoint_sha256": P["canonical"], "units": len(P["disp"]),
                            "last_fully_transcribed_source_unit": P["ck"]["last_fully_transcribed_source_unit"],
                            "last_fully_verified_source_unit": P["ck"]["last_fully_verified_source_unit"],
                            "unresolved": P["ck"]["unresolved_count"], "readiness": READINESS["practical"]})
    ck["coverage"] = "exact" if not [f for f in FAIL if f.startswith("coverage")] else "FAILED"
    ck["source_language_artifacts"] = [m[0] for m in manifest]
    ck["target_language_artifacts"] = []
    ck["language_synchronization"] = "no translation exists in any lane; every language_synchronization.tsv is empty"
    ck["works_and_boundaries_rows"] = len(wrows)
    ck["holds"] = ["Istanbul, Ayasofya 4830 ff. 183-200 and 231v-235r: no images (primary-pixel hold)",
                   "the Patna manuscript of the calendar treatise: not available; Layer 3 notes only"]
    ck["checks_failed"] = FAIL
    (out / "INTEGRATION_CHECKPOINT.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8", newline="\n")
    print(f"coverage rows {len(cov_rows)}, seams {len(seam_rows)}, special units {len(sp)}, works {len(wrows)}, "
          f"artifacts {len(manifest)}; failed checks: {len(FAIL)}")
    for f in FAIL:
        print("FAILED:", f)
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
