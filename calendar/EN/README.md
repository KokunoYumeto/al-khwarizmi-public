# English translation of al-Khwārizmī's treatise on the Jewish calendar

Muḥammad ibn Mūsā al-Khwārizmī, *Maqāla fī istikhrāj taʾrīkh al-yahūd wa-aʿyādihim*, «A treatise on finding the era of the Jews and their festivals», translated into English from the Hyderabad edition (1366 H / 1947) as this repository transcribes it line by line in [../](../). E. S. Kennedy described the treatise in «Al-Khwārizmī on the Jewish Calendar», *Scripta Mathematica* 27 (1964), pp. 55–59, and F. de Blois in his chapter of *Time, Astronomy, and Calendars in the Jewish Tradition* (Leiden, 2014); no complete English translation of the text was found.

Read [calendar_en.pdf](calendar_en.pdf) (7 pages).

## How it is made

- Every line of the edition is translated, in its order: the title page of the collection with its list of eleven treatises, the title page of the treatise, the whole text from the basmala to the explicit, and the edition's one footnote. Each block of [text_en.txt](text_en.txt) names the lines of [../anchors.tsv](../anchors.tsv) that it translates; `build_calendar_en.py` checks that every line belongs to exactly one block, in the order of the edition, and that every note is called.
- Modern English. The months have their usual English names (Nisan, Iyyar, Sivan, Tammuz, Av, Elul, Tishri, Marheshvan, Kislev, Tevet, Shevat, Adar); the Hebrew *maḥzor* keeps the Arabic form *maḥzūr*; «full», «deficient» and «as in the regular year» render the text's words for the months Marheshvan and Kislev of 30, 29 and 29/30 days. The positions in the letters of the abjad are given in figures (5ˢ 26° is 5 signs 26 degrees); the groups that are not abjad numbers stand in Arabic letters, as printed.
- The translator's notes, lettered, record where the translation follows a correction of the print, with the evidence; where the print's figure is kept and the computation gives another; and the readings that stay unresolved. The corrections are those of the critical notes of the transcription ([../critical_findings.tsv](../critical_findings.tsv), [../unresolved_readings.tsv](../unresolved_readings.tsv)), which check the figures by the arithmetic of the calendar and by de Blois's account of the manuscript. Misprints of a letter or a numeral are set right with «The print has …»; words the print leaves out are supplied in square brackets; the limit of 960 parts of the eleventh hour of the night of Wednesday and the 4082 years from Adam stand as printed, with the checked figures (695 parts of the twelfth hour; 4583 years) in the notes, because the error may be older than the edition.
- The notes also check the constants: 35,975,351 days are 5184 cycles of nineteen years exactly (the least number of cycles that makes whole days), their 98,496 years give the year of 365 days 5 hours and 3791/4104 of an hour stated in the text, and the revolutions of the moon are 1,316,736.

## Files

| File | Content |
|---|---|
| `text_en.txt` | the English, block by block, with the lines each block translates and the notes |
| `build_calendar_en.py` | checks the coverage and writes `calendar_en.tex`, `calendar_en.pdf` and `alignment.tsv` |
| `alignment.tsv` | every block with its first and last line, the number of lines and of words |
| `calendar_en.pdf` | the English translation |

## Credits

- Muḥammad ibn Mūsā al-Khwārizmī: the treatise (9th century). The Hyderabad edition (Dāʾirat al-Maʿārif al-ʿUthmāniyya, 1947) names no editor; its text is in the public domain.
- The translation: AI-translated (Claude), 2026. No person has proofread it. Dedicated to the public domain (CC0 1.0).
