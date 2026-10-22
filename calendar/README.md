# al-Khwārizmī, *Maqāla fī istikhrāj taʾrīkh al-yahūd wa-aʿyādihim* — the Hyderabad edition (1947), line by line

Muḥammad ibn Mūsā al-Khwārizmī's treatise on the Jewish calendar, as printed in Hyderabad by the Maṭbaʿat Jamʿiyyat Dāʾirat al-Maʿārif al-ʿUthmāniyya (1366 H / 1947; no editor is named) and bound first in the collection *al-Rasāʾil al-mutafarriqa fī al-hayʾa li-l-mutaqaddimīn wa-muʿāṣirī al-Bīrūnī* (1367 H / 1948). The source is the scan of the collection on Arabic Wikisource, [ملف:الرسائل المتفرقة في الهيئة.pdf](https://ar.wikisource.org/wiki/%D9%85%D9%84%D9%81:%D8%A7%D9%84%D8%B1%D8%B3%D8%A7%D8%A6%D9%84_%D8%A7%D9%84%D9%85%D8%AA%D9%81%D8%B1%D9%82%D8%A9_%D9%81%D9%8A_%D8%A7%D9%84%D9%87%D9%8A%D8%A6%D8%A9.pdf) (320 pages; the packet's file 60 has the same bytes, SHA-1 `1f69885e58d5cdca5bc79423a9c2dbda5b92605d`, SHA-256 `26C55E7E…4382573`). Its pages are bitonal images of 1449 × 2538 px (PDF 10: 1449 × 2574), about 170 px to the inch. Every printed line of the treatise is one line here, with its anchor `AK15-P###-L##` (PDF page, line); the line of the edition's footnote has the anchor `AK15-P008-N01`.

**Done:** PDF pages 1–10, the whole range of this lane: the title page of the collection with its list of the eleven treatises (PDF 1), the title page of the treatise (PDF 2), and the whole text, printed pp. 2–9 (PDF 3–10), from the basmala to the explicit «تم تاريخ اليهود عن محمد بن موسى الخوارزمى»: 143 lines of text, the edition's one footnote, and 26 lines of the two title pages. In de Blois's division of the treatise into nine sections: the introduction (pp. 2–4), the months (p. 4), the nineteen-year cycle (pp. 4–5), the hour, the month, the lunar years and the cycle (p. 5), the rules for the first day of Tishri and the length of the year, later called the four gates (pp. 5–7), the solar year and the years from Adam (p. 7), the positions of the sun, the moon, the planets and the head on the first day of Adam, at the building of the Temple and at the beginning of the Seleucid era (pp. 7–8), the procedure for the mean positions of the sun and the moon (pp. 8–9), and the procedure for the time since the conjunction (p. 9). PDF pages 11–320, the other ten treatises of the collection, are outside this lane and have a range disposition only.

## Read

- [calendar_1947.pdf](calendar_1947.pdf): the transcription, page by page, and the critical notes at the end.

## What is reproduced

- **The text**, as the edition prints it, letter for letter: the final ى without dots where it is so printed, the hamza and the madda only where they are printed (رأس, التورٰة with its small alif, آدم, ومأية), the numerals as printed, in Arabic-Indic digits and in the letters of the abjad, and the edition's errors. The dashes that the print sets around many numbers, of varying length, are written ـ; the large round full stop is written •; the Arabic comma ، is kept. Lines printed with a paragraph indent are indented; the heading of the last section is set as a heading; the explicit is centred.
- **The word division.** The print leaves irregular white after the letters that do not join the next: on p. 2 the white inside a word measures 5 to 14 px and a word space 6 to 17 px (`tools/gaps.py`), so the gaps do not show where a word ends. The words are divided by the sense; where the print suggests another division (فاذ افعل, ولدا لقمر), the page record says so.
- **The positions in abjad letters** (pp. 7–8): each group as printed, with the print's spaces and dashes; two letters that cannot form one abjad number (اه, وه, او) are written as two groups, and the page records give the measurements.
- **The dots.** The scan is bitonal and some dots run together or into the letters. Each doubtful dot was measured on the scan (`tools/band.py`): a single dot measures about 5–9 px, a pair run together 9–15 px. Where a letter is printed with wrong dots (يعد for بعد, فليأخد for فليأخذ), the line keeps the print and a critical note proposes the correction. A broken type is read as the letter it is: the initial م that prints as a filled oval apart from the next letter (يمضى من, pp. 7–8) is read م.
- **The two title pages**, line by line, the list of the collection in its two columns, and the edition's footnote on p. 7, «(١) بياض فى الاصل», a blank in the manuscript where the position of Mercury should stand.

## What is not reproduced

- **The running heads, the page numbers, the catchwords** (on pp. 2, 4, 6 and 8) and the foot marks «(١)» of pp. 4 and 9, which no mark in the text refers to: recorded in the page records, not transcribed as lines.
- **Copy matter**: a number written in ink on the title page of the treatise (PDF 2), and the stamp «To: www.al-mostafa.com» at the foot of the last page of the treatise (PDF 10), added to this digital copy (`copy_provenance.tsv`).
- **The manuscript.** The treatise survives in one manuscript, copied in Mosul in 632 H (1234) and now in the Khuda Bakhsh Library at Patna; it was not available here. This transcription is of the printed edition, not of the manuscript.
- **Translations**: none was requested; `language_synchronization.tsv` is empty.

## The critical notes

The edition keeps the errors of the manuscript and adds its own, above all in the numerals: de Blois notes that its editor did not know the older form of the Indian numerals, and the five is printed as a four (589 as ٤٨٩, 595 as ٤٩٤). The line always keeps the print. Twenty-six critical notes, kept apart from the transcription (`critical_findings.tsv` and the end of the PDF), propose corrections with their evidence; they rest on the arithmetic of the calendar, computed from the text's own figures (`checks/constants.py`) and from the standard rules (`checks/gates.py`), and on de Blois's summary of the manuscript where he reports it:

- **The Genesis quotation** of p. 2 (Genesis 1:14): لكن for لتكن, ربيع for رقيع (the firmament), and الصبا, perhaps for الضياء (low confidence); and four letters and words of the introduction and the list of months (فضت for مضت, اشهر for شهر, فرحشوان for مرحشوان, الزياد for الزيادة).
- **The cycle**: the print marks only five of the seven intercalated years; the third and the fifth of the scheme 3, 5, 8, 11, 14, 16, 19 that de Blois reads in the manuscript are missing.
- **The figures of §4**: thirteen months make 383 days 21 hours 589 parts (printed 489), the cycle 6939 days 16 hours 595 parts (printed 494).
- **The rules for the first of Tishri** (pp. 5–7): every limit was compared with the four gates of the standard calendar, run part by part through a week. The limits of 491 parts of the ninth hour of the day of Friday and of Sunday, of 408 parts of the first hour of the night of Friday, of 204 parts of the tenth hour of the night of Sunday, Tuesday and Thursday, and of the seventh hour of the day of Tuesday agree with them. Ten notes: 408 printed as ١٠٩ where it recurs; a rule whose middle is lost between two occurrences of 204 (p. 5); for a leap year that begins on Thursday the limit 960 parts of the eleventh hour of the night of Wednesday, where the text's own figures give 695 parts of the twelfth (Wednesday 11h 695p), and the figure missing in the second clause; 589 parts of the fourth hour of Monday printed ٨٩; «the day of Sunday» for «the night of Sunday»; السنة for الساعة; يعد for بعد; and two missing words.
- **The years from Adam** to the end of the year 1135 of the Seleucid era: printed 4082; 4583 by the 3448 years that the Jewish reckoning puts before the era, which the treatise's own rule of adding nine before casting out nineteens confirms (3448 = 19 × 181 + 9).
- **The positions**: the moon at the building of the Temple lacks its sign (ه); several groups of the lists for the Temple and for the Seleucid era are not abjad numbers and stay unresolved.
- **The constants of §8 and §9**: the base of days, 35,975,351, is 5184 nineteen-year cycles, the least number that makes whole days, and the 98,496 revolutions of the sun are their years; the revolutions of the moon are 1,316,736 (printed 1,016,736: «وثلثمائة» is missing); the divisor of §9 is the number of parts in a month, 765,433, where the print has «يوما» for «الفا».

Seven readings remain unresolved (`unresolved_readings.tsv`): «والصاحة» (p. 3), «آخر الساعة» (p. 5), the figure ١١٢ followed by eight zeros in a sentence that is complete without it (p. 6), «واخبار الآن» and Saturn's «ح نه» (p. 7), and the groups of p. 8 that are not abjad numbers.

## How it was checked

- Every line was read on the scan, cut into strips by the baselines of the lines (`tools/strips.py`); each doubtful letter, dot, space and numeral was enlarged and measured (`tools/band.py`, `tools/gaps.py`), and the digits of each number were identified one by one in their left-to-right order.
- Each build checks the pixels of the reading images against the hashes of the packet's pages (`controls/calendar_1947/IMAGE_INVENTORY.tsv`).
- The calendar: `checks/gates.py` computes the four gates of the standard calendar by running the molad through a week, part by part, under the standard rules (`gates.out.txt`); `checks/constants.py` checks the month, the years, the cycle, the solar year, two limits derived from the text's own figures, the interval from Adam and the base of days with exact integer arithmetic (`constants.out.txt`).
- No machine reading of the scan was compared with the transcription.
- The PDF builds deterministically: `python make_pdf.py --check` rebuilds it and compares the bytes.

## Files

| File | Content |
|---|---|
| `pages/AK15-P###.txt` | one page file per PDF page: the lines as printed, with observations, unresolved readings and critical notes; the format is described at the head of `build_calendar.py` |
| `build_calendar.py`, `make_pdf.py` | write `calendar_1947.tex`, the records and the ledgers; build the PDF |
| `records/AK15-P###.json` | one record per PDF page |
| `anchors.tsv` | every printed line with its anchor |
| `physical_unit_disposition.tsv` | every PDF page with its image hashes, kind, role and lines, and the range disposition of PDF 11–320 |
| `evidence_ledger.tsv`, `unresolved_readings.tsv`, `copy_provenance.tsv` | the observations; the unresolved readings; the copy matter |
| `critical_findings.tsv` | the critical notes: errors of the print and the proposed corrections, with evidence and confidence |
| `formula_table_ledger.tsv` | the numerical matter of the treatise (the constants, the rules for Tishri, the solar year, the years from Adam, the lists of positions, the two procedures) with its checks |
| `witness_variants.tsv`, `figure_provenance.tsv`, `proposed_corrections.tsv`, `language_synchronization.tsv` | the remaining ledgers of the return protocol (empty: no second witness, no figures, no translation) |
| `checkpoint.json` | the checkpoint of the lane |
| `checks/` | `gates.py` and `constants.py` with their outputs |
| `tools/` | the line strips, the enlarged bands with the dots boxed, the measurement of the white in a line |

## Credits and licence

- Muḥammad ibn Mūsā al-Khwārizmī: the text, in the public domain.
- The Dāʾirat al-Maʿārif al-ʿUthmāniyya, Hyderabad: the edition (1947/1948); no editor is named.
- Arabic Wikisource: the scan of the collection; the scan bears the stamp of al-mostafa.com.
- François de Blois, "Some early Islamic and Christian sources regarding the Jewish calendar (9th to 11th centuries)", in Sacha Stern and Charles Burnett (eds), *Time, Astronomy, and Calendars in the Jewish Tradition* (Leiden: Brill, 2014), pp. 65–78: consulted for the critical notes.
- Transcription, records and scripts: AI-integrated work (Claude), 2026. No person has proofread it. Dedicated to the public domain (CC0 1.0).
