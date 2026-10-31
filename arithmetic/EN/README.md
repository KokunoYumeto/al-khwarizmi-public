# Boncompagni's Italian in his edition of *Algoritmi de numero Indorum* (1857), in English

Baldassarre Boncompagni printed the Latin arithmetic «Dixit Algorizmi» from the Cambridge manuscript Ii.6.5 in the first volume of his *Trattati d'aritmetica* (Rome, 1857), transcribed line by line in [../](../). His own matter is in Italian: the title page, the heading of the text, the folio marks of the manuscript in the margin and six footnotes on the lacunae of the manuscript and on its margin at the end. This folder gives all of it in English.

The Latin text of the treatise is not translated here: J. N. Crossley and A. S. Henry translated the Cambridge manuscript into English («Thus Spake al-Khwārizmī: A Translation of the Text of Cambridge University Library Ms. Ii.vi.5», *Historia Mathematica* 17, 1990, pp. 103–131).

Read [italian_en.pdf](italian_en.pdf) (3 pages): each line as transcribed, beside its English.

## How it is made

- [italian_en.tsv](italian_en.tsv) has one row for each item: the lines of [../anchors.tsv](../anchors.tsv) that it covers and its English. `build_italian_en.py` stops unless every line of the title page, every line of the heading, every footnote line and every margin note has exactly one row, and writes `italian_en.tex` and `italian_en.pdf`.
- The Latin that Boncompagni quotes from the manuscript stands in italics, with an English rendering in parentheses; «guazal cora» is left as it stands.

## Credits

- Baldassarre Boncompagni: the edition (1857), in the public domain.
- The English: AI-translated (Claude), 2026. No person has proofread it. Dedicated to the public domain (CC0 1.0).
