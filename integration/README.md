# AK-I01 — integration and cold audit

The integration of the sealed returns of all the sessions of the packet: the algebra (AK-A01–A04), the geography (AK-G01–G05), the arithmetic (AK-N01), the Zīj (AK-Z01–Z08), the practical astronomy (AK-P01–P02) and the Jewish calendar (AK-C01). No new transcription was made. `integrate.py` reads the lanes and the packet controls in [controls/](../controls/) and writes the files below; `audit.py` is the cold audit, run in a fresh clone of the repository.

## Coverage

[COVERAGE.tsv](COVERAGE.tsv) checks every session of the session map against the disposition ledger of its lane: every owned unit is disposed exactly once, no unit is missing or repeated, each session begins where the one before it ends, and no lane has a unit outside its sessions.

| Source | Sessions | Units | State |
|---|---|---|---|
| Algebra, the 1939 Cairo edition | AK-A01–A04 | frames 1–130 | exact |
| Geography, Mžik's edition in the 1962 reprint | AK-G01–G05 | frames 1–218 | exact |
| Arithmetic, Boncompagni 1857 | AK-N01 | frames 1–30 | exact |
| Zīj, Suter 1914 | AK-Z01–Z08 | JP2 0000–0295 | exact |
| Practical astronomy, Charette and Schmidl's study | AK-P01–P02 | PDF 1–98 | exact; with 22 further evidence units: the PAL record of Ayasofya 4830, pp. 163–180 and 185–186 of the 1987 *Erdem* article and its missing pp. 181–184, covered by the Turkish version |
| Jewish calendar, the Hyderabad collection | AK-C01 | PDF 1–10 | exact; PDF 11–320, the other treatises, carry a visible range disposition |

## Seams

[SEAMS.tsv](SEAMS.tsv) replays the 15 seams between sessions, the 7 seams that the session map names (the seam of the two frame archives of the geography at frames 109/110; the colour cards, the part title and the first table of the Zīj; the two title pages of the calendar), and the 4 catchwords of the calendar. At every seam both units are disposed and adjacent; the last line before and the first line after each seam are given, and the text runs on across every seam between text pages. Each catchword of the calendar is the first word of the next page.

## Special units

[SPECIAL_UNITS.tsv](SPECIAL_UNITS.tsv) lists, with their dispositions: the 21 figures of the algebra (three facsimiles of the manuscript and eighteen figures of the text) and the five plates of the geography, each with its two files checked against their hashes; every unit with table lines (66 in the geography, 165 in the Zīj, the list of the eleven treatises on the title page of the calendar collection); 37 blanks; the corrigenda (the geography's additions and corrections, recorded, each correction entered on the page it concerns; the Zīj's four pages of additions and corrections, the errata slip and the list of misprints); the copyist's colophon of the algebra, the explicit of the Zīj's manuscript O and the explicit of the calendar, and the last pages of the geography and of the arithmetic, which breaks off; the three colour cards of the Zīj's digitisation; 19 trailing leaves after the last page with text or figures; and the excluded range of the calendar file.

## Works and boundaries

[WORKS_AND_BOUNDARIES.tsv](WORKS_AND_BOUNDARIES.tsv) keeps visible the sixteen works of the packet's coverage table with their state here (produced, evidence only, held, lost), and the 29 rows of the ISMI database with the boundary the packet gives each. Nothing is promoted: the arithmetic and the Zīj are Latin witnesses and no Arabic original is reconstructed; the practical sessions are evidence only; the lost *Book on History* is not fabricated.

## Monolingual artifacts

Each source-language witness, and each editor's layer in another language, is a separate artifact in [witnesses/](witnesses/), one line per transcribed line with its anchor, kind and text as in the lane (the markup of the page files kept), and the editor's manuscript locators in a margin column where the lane has them. Together the artifacts of a lane hold every one of its anchored lines exactly once ([witnesses/MANIFEST.tsv](witnesses/MANIFEST.tsv)).

| File | Language | Content | Lines |
|---|---|---|---|
| `AK01_algebra_1939.ar.tsv` | Arabic | the text of the 1939 edition, with its cover and title page | 1637 |
| `AK05_geography_1926.ar.tsv` | Arabic | the text of Mžik's edition, with its Arabic index | 2526 |
| `AK05_geography_1926_editor.de.tsv` | German | Mžik's German title pages, the series title and the imprint | 43 |
| `AK02_arithmetic_1857.la.tsv` | Latin | the Latin text of Boncompagni's edition | 730 |
| `AK02_arithmetic_1857_editor.it.tsv` | Italian | Boncompagni's title page, heading and footnotes | 38 |
| `AK07_zij_1914.la.tsv` | Latin | the Latin text and tables of the recension, with Suter's Latin apparatus | 6357 |
| `AK07_zij_1914_suter.de.tsv` | German | Suter's title page, foreword, introduction, commentary, additions, glossary and index | 5303 |
| `AK15_calendar_1947.ar.tsv` | Arabic | the text of the Hyderabad edition, with the two title pages | 170 |

No translation was requested or made, so there are no target-language artifacts, and every `language_synchronization.tsv` is empty. Every `proposed_corrections.tsv` is empty too: the corrections proposed for the printed witnesses are the 430 critical notes of Layer 3, kept apart from the transcriptions in each lane's `critical_findings.tsv`.

## Readiness

| Lane | Readiness |
|---|---|
| algebra | ready: the Arabic printed witness, complete; the editors' preface, study and footnotes recorded, not reproduced |
| geography | ready: the Arabic printed witness, complete; the German editorial matter a separate layer; the German introduction and footnotes recorded, not reproduced |
| arithmetic | ready as a Latin witness, complete to where the text breaks off; the Arabic original is lost |
| zij | ready as a derivative recension: the Latin recension of Maslama and Adelard, complete, with Suter's German layer apart |
| practical | evidence only: no source text; Berlin, Landberg 56 ff. 77r–97v checked on public images; Istanbul, Ayasofya 4830 held, without images |
| calendar | ready as a printed witness with errors: complete, with 26 critical notes; the Patna manuscript not seen |

[INTEGRATION_CHECKPOINT.json](INTEGRATION_CHECKPOINT.json) gives, for each lane, the last commit that touched it, its canonical checkpoint recomputed over its page files (or, for the practical returns, over their files, with their `SHA256SUMS` checked), its units, lines, critical notes, figures and unresolved readings, and its readiness.

## The cold audit

`audit.py` was run in a fresh clone of the repository from its remote, made with `core.autocrlf=false` and with the local source images linked into it as `_intake`, where the builders check them by hash. It patches nothing. On commit `0f01207` it passed all seventeen steps ([AUDIT_RECEIPT.json](AUDIT_RECEIPT.json), 2026-10-22): the clone was clean; `integrate.py` passed every check and reproduced the fourteen committed integration files byte for byte; every lane replayed: its builder rewrote the records, ledgers, TeX and figures from the page files and the source images, and the PDFs of the algebra, the geography, the arithmetic, the two Zīj volumes and the calendar were rebuilt with the same bytes and without a missing character; the two practical returns replayed; afterwards the clone was still clean, so every committed derived file is reproduced exactly; and the six PDFs open, every page renders, and every font is embedded. A first run, on commit `dfcc089`, passed the same steps; the only change between the two commits removes the markdown emphasis from the database rows of `WORKS_AND_BOUNDARIES.tsv`.

The audit was run by the same AI that made the transcriptions. It replays and checks the work mechanically; it is not an independent reading of the texts, which no person has proofread.

The commits named here are commits of the project's working repository; [KokunoYumeto/al-khwarizmi-public](https://github.com/KokunoYumeto/al-khwarizmi-public) holds a snapshot of the same files.

## Files

| File | Content |
|---|---|
| `integrate.py` | writes the files of this folder and fails on any broken check |
| `audit.py` | the cold audit |
| `COVERAGE.tsv`, `SEAMS.tsv`, `SPECIAL_UNITS.tsv`, `WORKS_AND_BOUNDARIES.tsv` | the proofs and lists described above |
| `witnesses/` | the monolingual artifacts and their manifest |
| `INTEGRATION_CHECKPOINT.json` | the checkpoint of the integration |
| `AUDIT_RECEIPT.json` | the receipt of the cold audit |

AI-integrated work (Claude), 2026. Dedicated to the public domain (CC0 1.0).
