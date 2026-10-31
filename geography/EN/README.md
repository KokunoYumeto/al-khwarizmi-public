# English translation of al-Khwārizmī's *Kitāb ṣūrat al-arḍ*

Muḥammad ibn Mūsā al-Khwārizmī, *Kitāb ṣūrat al-arḍ*, «The book of the image of the earth»: the coordinates of the cities, mountains, seas, islands and rivers of the inhabited earth that he drew from Ptolemy's *Geography*, translated into English from the edition of Hans von Mžik (Leipzig: Otto Harrassowitz, 1926; Bibliothek arabischer Historiker und Geographen 3; Baghdad reprint, 1962), as this repository transcribes it line by line in [../](../). No complete English translation of the text was found.

Read [surat_en.pdf](surat_en.pdf) (79 pages).

## How it is made

- Every line of the edition is translated, in its order: the Arabic title pages, the tables of the cities (entries 1–539) and of the mountains (540–966), the courses of the coasts of the seas, the islands, the places where the boundaries of the countries are written, the springs and rivers of each clime, the editor's index, and the German title pages and imprint. Each block of [text_en.txt](text_en.txt) names the lines of [../anchors.tsv](../anchors.tsv) that it translates; `build_surat_en.py` checks that every line belongs to exactly one block, in the order of the edition, that every note is called and that the angle brackets pair.
- The numerals of al-Khwārizmī are letters with their abjad values; they are given as figures, in degrees and minutes. The manuscript leaves two letters without their dots, and the edition keeps them: ڡ can be 80 or 100, ٮ 2, 10 or 50. Where the neighbouring points of the same entry, or else of the next entries, decide clearly between the readings, the nearest is given; in the tables of the cities and in the headings of the climes, the band of the clime decides the latitude. Otherwise every value is given, as 88/108°; about two hundred figures stay open in this way. A group of letters that is no abjad number stays in Arabic letters.
- Most names stand in Arabic letters, as the edition prints them, mostly Ptolemy's names in Arabic transcription; familiar ones are given in transliteration (Ṣanʿāʾ, Ḥulwān, al-Maṣṣīṣa) or in their English form (Damascus, Constantinople, Mount Lebanon).
- The edition's apparatus: its running numbers stand in parentheses; the numbers in square brackets are those of the same items in Suhrāb's *ʿAjāʾib al-aqālīm al-sabʿa*, as Mžik gives them; angle brackets ⟨ ⟩ enclose what Mžik supplies. Where his supplement begins or ends inside a word, the brackets stand on the whole words it covers; a supplement within a single word is not marked. A figure that Mžik supplies wholly or in part stands in angle brackets. Obvious misprints of the running numbers and of the brackets are corrected (the running numbers 280, 384 and 2078, the brackets of 294 and 1550, the lost last digit of 1784); the critical notes of the transcription ([../critical_findings.tsv](../critical_findings.tsv)) record them. Mžik's note marks are not reproduced.
- The translator's notes, lettered, record misprints of al-Khwārizmī's text («The print has …»), the corrections of the editor that the translation follows (his additions and corrections, p. 163: Barqa, Cyprus, the latitude of al-Andalus, a latitude of the coast of the Great Sea) and readings that stay open (the longitudes of the river ٮاطس).
- As in the edition, the names of the mountains stand on one page and their coordinates, row by row in the same order, on the next, with the colours of the mountains on the map and the directions of their heads; the headings of these tables run across both pages, and their halves are marked with «…». The qualifier *mukhayyar* (مخيّر) of some colours is left untranslated; its sense here is not certain.
- The pages of the edition stand in the margin. Where a page ends inside a paragraph, the mark follows the last point of the page; in two places, where a page ends inside the first point of a paragraph, it stands at the head of the paragraph.
- The English was first drafted from the transcription with a table of phrases and a converter of the abjad numerals, then read against the Arabic block by block and corrected. The five plates of the edition (the manuscript's maps and its last page) are images in the transcription ([../figures/](../figures/)).

## Files

| File | Content |
|---|---|
| `text_en.txt` | the English, block by block, with the lines each block translates and the notes |
| `build_surat_en.py` | checks the coverage and writes `surat_en.tex`, `surat_en.pdf` and `alignment.tsv` |
| `alignment.tsv` | every block with its first and last line, the number of lines and of words |
| `surat_en.tex` | the LaTeX source of the PDF |
| `surat_en.pdf` | the English translation |

## Credits

- Muḥammad ibn Mūsā al-Khwārizmī: the *Kitāb ṣūrat al-arḍ* (9th century), in the public domain.
- Hans von Mžik: the edition (1926), from the unique manuscript of the Bibliothèque de l'Université et Régionale in Strasbourg (Cod. 4247). His running numbers, his numbers from Suhrāb and his supplements are kept as described above. His German introduction and footnotes are not translated: they are his own writing, and he died in 1961, so they are protected in the EU until the end of 2031.
- The translation: AI-translated (Claude), 2026. No person has proofread it. To the extent that any rights exist in this AI-produced translation, they are dedicated to the public domain under CC0 1.0; the dedication does not concern Mžik's edition or its German matter.
