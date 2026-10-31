# English translation of Suter's German matter in his edition of al-Khwārizmī's astronomical tables

Heinrich Suter's *Die astronomischen Tafeln des Muḥammed ibn Mūsā al-Khwārizmī in der Bearbeitung des Maslama ibn Aḥmed al-Madjrīṭī und der latein. Uebersetzung des Athelhard von Bath* (Copenhagen, 1914), on the preliminary work of A. Bjørnbo and R. Besthorn, gives the Latin text and tables of the recension with Suter's foreword, introduction, commentary, additions, glossary and index in German. The Latin text and tables were translated into English by O. Neugebauer (*The Astronomical Tables of al-Khwārizmī*, Copenhagen, 1962), with his own commentary. This folder translates Suter's German, which has not been translated before. Read [suter_en.pdf](suter_en.pdf).

**Complete:** the title page, the contents, the foreword and the introduction (pp. I–XXV), the commentary (pp. 32–106), the additions and corrections with the slip of further corrections and the list of misprints (pp. 233–237), the glossary (pp. 239–248) and the index of names and subjects (pp. 249–255). Suter's corrections to his commentary are made in the translation of the commentary, each with a translator's note giving the reading of the print.

## How it is made

- The source is the line-by-line transcription of the edition in [../anchors.tsv](../anchors.tsv) and [../pages/](../pages/). Every printed line of Suter's German is translated, in his order; nothing is summarised or left out. Each block of the English names the lines it translates; `build_suter_en.py` checks that every line of a unit belongs to a block and that every one of Suter's footnotes is called once.
- Modern English. Arabic names and words in the running text are given in a modern transliteration (al-Majrīṭī, Yazdegerd, Ibn al-Qifṭī, *zīj*); the forms of the Latin text and of the manuscripts are kept as printed. Bibliographical references keep their titles in the original languages.
- The glossary and the index keep Suter's transcription of Arabic (his *dj* is *j*, his *ḳ* is *q*) and the order of the German. In the index the German headwords are translated, with the German in square brackets.
- The words of the Latin text and of the manuscripts that Suter quotes, and the other Latin, French and Italian that he quotes, keep the original words, followed by an English translation in parentheses. Greek stands as printed.
- Suter's footnotes are numbered as footnotes. The translator's notes are lettered; they record a misprint set right, with the reading of the print, a slip in Suter's reckoning, checked against his numbers, and the figures of the print, which the transcription describes but does not reproduce.
- The pages of Suter's book stand in the margin.

## Files

| File | Content |
|---|---|
| `units.tsv` | the units of the translation, in the order of the book, with the lines of the German that each covers |
| `text/*.txt` | one file per unit: each block of English with the lines it translates, Suter's footnotes and the translator's notes; the format is described at the head of `build_suter_en.py` |
| `build_suter_en.py`, `make_pdf.py` | check the coverage of the lines and the footnotes and build the PDF deterministically |
| `alignment.tsv` | every block of the English with its lines and pages |
| `checkpoint.json` | the units done and a checksum over their files |

## Licence

Suter's work is in the public domain (Suter died in 1922, Bjørnbo in 1911). The translation is AI-translated (Claude), 2026; no person has proofread it. It is dedicated to the public domain (CC0 1.0).
