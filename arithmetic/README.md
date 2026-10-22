# Algoritmi de numero Indorum — Boncompagni's edition (Rome, 1857), line by line

The Latin arithmetic that begins «Dixit algorizmi», a twelfth-century Latin text connected with the lost arithmetic of Muḥammad ibn Mūsā al-Khwārizmī, transcribed from the edition of Baldassarre Boncompagni, *Trattati d'aritmetica* I (Rome: Tipografia delle scienze fisiche e matematiche, 1857), printed from the manuscript Cambridge, University Library, Ii.6.5, ff. 102r–109v as the edition numbers them. The copy is that of the Bayerische Staatsbibliothek, Munich (4 Math.u. 9 u-1/2), the editor's presentation copy to the Royal Library in Munich, digitised by the Munich Digitisation Centre (bsb10525392, 30 frames). Every printed line is one line here, with its anchor `AK02-F###-L##` (frame, line); the lines of the editor's footnotes have the anchors `AK02-F###-N##`.

**Status (2026-10-21): all 30 frames transcribed.** The library's cover, the printed wrapper with the title, the leaves before the text, the whole text of printed pp. 1–23 with the editor's footnotes, and the blank back of the last leaf. The text covers the invocation, the purpose of the book, the nine letters, one as the root of number, the differences, the places of the units, tens, hundreds and thousands with their figures, the example 325, the carrying of ten units to the next place, the names of the places up to the thirteenth, the reading of a number of sixteen places, addition and subtraction with the examples 6422 less 3211 and 1144 less 144, halving and doubling, multiplication with the example 2326 by 214, the proof by casting out nines, division with the examples 46468 by 324 and 1800 by 9, with a shortening for the circles left in the number divided, the sexagesimal fractions and their places, the multiplication of fractions with the examples six minutes by seven minutes, seven seconds by nine minutes, one and a half by one and a half, and two degrees 45 minutes by three degrees 10 minutes 30 seconds, the division of fractions with the examples fifteen thirds by six thirds, ten seconds by five minutes and ten minutes by five thirds, the proof of division, the setting out of a number with its fractions, the addition, subtraction, doubling and halving of fractions, and other fractions, with the example three sevenths by four ninths; it breaks off in the example three and a half by eight and three elevenths, at the foot of fol. 109 verso of the manuscript, as the editor's last footnote reports. No person has proofread the transcription; the integrated audit (AK-I01) is still to come.

## What this text is

The Arabic arithmetic of al-Khwārizmī is lost. This Latin text is a witness of it, not the work itself: it was long taken for a translation of the lost treatise; the Bibliothèque nationale de France, in its authority record «Dixit Algorizmi», which cites R. Rashed's *Histoire des sciences arabes* (1997) and A. Allard's edition (1990), describes it as a composite text of the middle of the twelfth century, some of whose elements go back to authors such as Boethius and Nicomachus of Gerasa. The Cambridge manuscript is incomplete.

## Read

- [algoritmi_1857.pdf](algoritmi_1857.pdf): the transcription, frame by frame.

## What is reproduced

- **The Latin text** letter for letter as the edition prints it: the spelling of the manuscript that the edition keeps (u for v, e for ae and oe), the numerals in small capitals between points (`.ix.`, `.x̄.` with a bar over the x), its punctuation and its words divided at the ends of the lines. Spaces at punctuation follow the print, measured on the scan (`tools/punct.py`, which finds the points, commas, colons and semicolons by their form and measures the gaps beside them): after a mark, a space where the gap is at least 12 px or two thirds of the median word space of the line; before a mark, where it is at least 10 px. The gaps after marks fall into a group of 3–8 px and a group from about 15 px up, with a thin plateau between: gaps of 9–11 px, a hair space or none, are decided by the rule and are the least certain. Specks and pencil strokes beside a mark shorten the measured gap; such places are read on the scan. Colons and semicolons are told apart by the darkness of the tail (`tools/colons.py`), because a reader of this copy has added pencil tails to some colons.
- **The editor's apparatus**: his heading, the leaves of the manuscript printed in the margin and the vertical bar with which he marks the beginning of a leaf in the text, his «(sic)», and his footnotes, which are in Italian. Baldassarre Boncompagni died in 1894; his writing is in the public domain and is transcribed.
- **The title** on the printed wrapper.
- **Errors of the print** are kept in the line; a critical note (`critical_findings.tsv` and the last page of the PDF) proposes the correction. There are twenty-two: the article of «nelle linea» in the footnote of p. 1; the figure of two hundred printed .300. (p. 4); a stray point before «numerus» (p. 5); the figure of the example 325 printed .335. (p. 5); a «mille» missing before «quinque uicibus», five times, where four are printed (p. 7); «pur» for «per» (p. 11); «debebimus» where the work requires «delebimus», we shall delete (p. 12); «quadringinta» for «quadraginta», forty, in the number 46468 (p. 15); «cxxviii.», 128, for «cxlviii.», 148, in the working of the same division (p. 16); «.ix. ix.», the numeral printed twice (p. 16); the products of seconds by seconds, thirds by thirds and fourths by fourths, printed as thirds, fourths and fourths, where the rule on the same page, the places of the factors joined, gives fourths, sixths and eighths (p. 18); one and a half multiplied «in duo et dimidio», by two and a half, where the working multiplies one and a half by one and a half (p. 18); «xvi.», sixteen, for fifteen minutes in the result of that example, two and a quarter (p. 18); the 165 minutes of two degrees and forty-five minutes printed «.xlv.» with «.c.» set above it (p. 19); the thirty seconds left out of 11430 seconds, which the product that follows uses (p. 19); «per minuta» printed twice (p. 20); the quotient of ten seconds by five minutes, two minutes, named seconds in the working and in its proof (pp. 20–21); forty-six seconds stated and forty-five set out in the example of setting out a number with its fractions (p. 21); «.ii.», two, for «in», into, in the rule that turns the numbers into the kind of their lowest order (p. 23); «et» for «ex» in twelve parts of sixty-three parts of one (p. 23); and «idest» for «in» before the second factor of the last example (p. 23).

## What is not reproduced

- **Copy matter** of the Munich copy: the editor's presentation inscription, the shelfmark, the stamps and labels, and the notes and marks that a reader wrote in pencil and ink in the margins and in the text. They are recorded on each page (`copy_provenance.tsv`).

## The frames

The 30 frames are the BSB/MDZ images of bsb10525392 (IIIF manifest and inventory with SHA-256 in [../controls/arithmetic_1857/](../controls/arithmetic_1857/)); each is checked against the inventory at every build. The rights statement of the images is NoC-NC 1.0 (no copyright, non-commercial use only); the transcription reproduces the text, not the images.

## Files

| File | Content |
|---|---|
| `pages/AK02-F###.txt` | the page files: the lines, the footnotes, the observations and the records of each frame |
| `build_algoritmi.py`, `make_pdf.py` | build the TeX, the records and the ledgers, and the PDF (deterministic: two builds give the same bytes) |
| `records/`, `*.tsv`, `checkpoint.json` | the records of each frame and the ledgers, written by the build |
| `tools/` | the reading kit: line bands, crops, gaps between words |

## Licence

The Latin text and Boncompagni's edition are in the public domain. The transcription, records and scripts are AI-integrated work (Claude) and are dedicated to the public domain (CC0 1.0); no person has proofread them.
