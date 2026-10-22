# al-Khwārizmī and practical astronomy — evidence and attribution audit (AK-P01–P02)

Short Arabic texts on the astrolabe and other portable instruments survive in two codices: Berlin, Staatsbibliothek, Landberg 56 (siglum **B**) and Istanbul, Süleymaniye, Ayasofya 4830 (siglum **A**). Two of the texts name al-Khwārizmī; the others are anonymous. This folder holds an audit of the evidence for these texts and for their attribution. It is not an edition. It reproduces no Arabic text and no translation from the modern study. Short readings of the Berlin manuscript are quoted only to identify its sections.

**Status (2026-10-22):** AK-P01 and AK-P02 are done.

- AK-P01 covers PDF pages 1–34 of the study (the introduction and the critical edition of Texts 1–11) and the Ptolemaeus Arabus et Latinus record of Ayasofya 4830. Its maps, ledgers and checkpoint are in [P01/](P01/).
- AK-P02 covers the rest of the study (translation, facsimiles, commentary, appendices and bibliography, PDF 35–98) and the older description of A by Ahmedov, ad-Dabbagh and Rosenfeld (1987). Its return is in [P02/](P02/).

## Sources

- **The study.** F. Charette and P. G. Schmidl, "al-Khwārizmī and Practical Astronomy in Ninth-Century Baghdad. The Earliest Extant Corpus of Texts in Arabic on the Astrolabe and Other Portable Instruments", *SCIAMVS* 5 (2004), pp. 101–198. It is packet file 50: 98 PDF pages, SHA-256 `E3FF31E6…6E18`. The study is publicly accessible, but no licence for reuse is established, so it serves as evidence only.
- **The Ayasofya record.** The Ptolemaeus Arabus et Latinus record of Ayasofya 4830 (packet file 10, `authority/AYASOFYA_4830_PAL_RECORD.html`).
- **Manuscript B.**
  - The images of Landberg 56 published by the Max Planck Institute for the History of Science. The ISMI record names the source «MPIWG Library / Staatsbibliothek Berlin» and gives the licence as CC BY-SA 4.0.
  - Routes: [ISMI digitization 284658](https://ismi.mpiwg-berlin.mpg.de/digitalization/284658) and the [IIIF manifest](https://digilib.mpiwg-berlin.mpg.de/digitallibrary/Manifester/IIIF/permanent!library!RXBT90D9!pageimg) (216 images).
  - The packet of 2026-08-16 recorded no images of B. They are public; ff. 77r–97v were acquired on 2026-10-22.
  - The images are kept outside the repository; [P01/landberg56_image_inventory.tsv](P01/landberg56_image_inventory.tsv) lists each one with its folio, size and SHA-256.
- **Manuscript A.** No images could be consulted:
  - the PAL record shows images only of ff. 53r–80v;
  - ISMI has no scans;
  - the portal of Türkiye Yazma Eserler Kurumu shows its records of the codex only after a member login.

## The texts

| | Witness | Subject | In the witness | The study's position (pp. 101–109) |
|---|---|---|---|---|
| Text 1 | B 77v–81v | construction of the astrolabe | anonymous | formerly taken for part of al-Farghānī's treatise; arguments for and against al-Khwārizmī |
| Text 2 | B 81v:4–91v:7 | use of the astrolabe | «قال محمد بن موسى الخوارزمي» | the only text of B with his name; untitled; its end uncertain |
| Text 3 | B 91v:8–92r:16, with the table on 94r | compass for the prayer times | anonymous | same milieu |
| Text 4 | B 92r:17–93r | plate for the altitude and moonrise | anonymous | same milieu |
| Texts 5–8 | B 96r–97v | species of astrolabes; projection of the rays; Ptolemy's five zones; sine quadrant | anonymous | same milieu; Text 5's link with Text 2 doubtful |
| Text 9 | A 198v–199r | the meridian with the astrolabe | ascribed to al-Khwārizmī | differs from Text 2's chapter on the azimuth (B 89v–90r) |
| Text 10 | A 196v–197r | horary quadrant | anonymous | possibly his or his milieu's |
| Text 11 | A 192r | portable sundial (*mukḥula*) | anonymous | probably not his; ninth century |
| tables | B 93v, 94v, 95r–v | right ascension; hour altitudes; "sine of the hours" | anonymous | 95r–v from al-Khwārizmī (Hogendijk 1991); 93v possibly linked |
| sundial treatise | A 231v–235r | plane horizontal sundials | ascribed to al-Khwārizmī | authorship questioned by King (1999), defended by the authors; not edited in the study |

Two kinds of material in B are later and outside the Abbasid corpus: the extracts in the margins of ff. 82r–83r (c. 1400–1600) and the table on f. 97v. [P01/text_map.tsv](P01/text_map.tsv) gives each item with its folios, its pages in the study, earlier translations, the work number of the packet (AK10–AK14), the row of the ISMI list in [../controls/08_LOST_DOUBTFUL_ATTRIBUTION_MAP.md](../controls/08_LOST_DOUBTFUL_ATTRIBUTION_MAP.md), and a classification.

## Findings of AK-P01

1. **The folios of B agree with the study.**
   - Checked on the leaves: every boundary the study gives for Texts 1–8 and for the tables of ff. 93v–95v.
   - Images and folios match: canvas = 161 + 2 × (folio − 77). The pencil foliation of every recto confirms this, as do the quire words on ff. 81r, 89r and 97r.
   - Text 2's incipit names al-Khwārizmī on the fourth line of f. 81v. The manuscript reads «في عمل الاسطرلاب». The study emends this, and ISMI quotes the emended form.
2. **The edition reorders material twice.**
   - **Text 2.** The study says it reordered some material of Text 2. Its own folio markers, checked on ff. 89r–90r, give the order of the leaves as §§ [27] [28a] [28b] (89r), [28c] (89v:1–6), [26c] (89v:7–11), [29] (89v:12–90r:10), [28d] [28e] (90r:11–17).
   - **Text 1.** The edition prints the title of the table (foot of 78r) and the table (78v) before the paragraph headed «الكواكب», which stands above the title on 78r. The study does not announce this second case.
   - [P01/edition_folio_concordance.tsv](P01/edition_folio_concordance.tsv) maps every section of the edition to its folio.
3. **Text 2 bears the trace of a second copy.** At f. 89v:7 a passage begins «ووجدت في نسخة اخرى» ("and I found in another copy"). The text of B, or of its exemplar, was collated with a second copy, and the edition places the passage as § [26c].
4. **A cannot yet be checked.** Texts 9–11, the anonymous tracts of ff. 182v–200r and the sundial treatise (231v–235r) remain unchecked against their witness. Two routes remain: the user's own membership of the YEK portal, or reproductions ordered from the Süleymaniye library.
5. **The attributions stay item by item.**
   - The study rejects the grouping of A's tracts into one work of 59 "chapters" (Ahmedov et al. 1987), and the packet's boundary follows it.
   - One tract of A (f. 198r) is ascribed in the manuscript to ʿUmayr ibn Samʿān. ISMI's row "Ṭarīq maʿrifat khusūf al-qamar" may be this item; the titles differ, so that identification remains unproved.
6. **Dates.**
   - A was copied in Damascus between Shaʿbān 626 and Rajab 627 H (1229–30). The study's date, Ramaḍān 626, is that of the codex's Ptolemaic part, according to the PAL record.
   - B is older than the note on its title page. That note prays for the reign of the Rasulid sultan al-Ashraf Ismāʿīl (778–803 H). The study dates the copy to c. 700–750 H.

## Findings of AK-P02

1. **The study's attribution arguments, item by item** ([P02/attribution_findings.tsv](P02/attribution_findings.tsv)):
   - **Text 1:** speculative. The table of f. 78v rests on the obliquity 23;35 (R = 98;11), a value of the observations under al-Maʾmūn, where al-Khwārizmī used 23;51.
   - **Text 2:** al-Khwārizmī's. Its §25 gives his excess of the year, 93;2, while §26c gives 93;15 «from another copy» and is judged an interpolation.
   - **Text 8:** an attribution "not unreasonable".
   - **Text 10:** possibly his.
   - **Text 11:** later than c. 830 by the obliquity of its table.
2. **The arithmetic holds.** Six of the study's computations recompute correctly ([P02/recomputation_checks.tsv](P02/recomputation_checks.tsv), script in `P02/checks/`):
   - the parameter R = 98;11 and the errors of the table of f. 78v;
   - the two year lengths and their excesses;
   - the faulty example of the sine quadrant;
   - the five terrestrial zones;
   - the midday shadows of Text 3.
3. **Checked against the other lanes of this project** ([P02/cross_lane_checks.tsv](P02/cross_lane_checks.tsv)):
   - **Geography.** Text 2 gives Kufa 32° and Rayy 37°. Al-Khwārizmī's geography, in our transcription of Mžik's edition, has 31;50 and 35;45. Text 2's Baghdad (70°) differs from the geography's (printed «عح», 73 with ج read for the undotted letter), and Damascus (60°) agrees. All of this matches the study.
   - **Zīj.** The study's note 87 says that al-Majrīṭī's recension of the Zīj mentions a year of 365;15,32,30. In Suter's book that value is Suter's own derivation (p. 42), which he corrects to 365d 6h 12m in his additions (p. 235). The recension's Tab. 115 gives 93;2,15 a year, the excess of 365;15,30,22,30 days.
4. **The 59 "chapters" of the 1987 article do not form one work by al-Khwārizmī** ([P02/unity_claim_comparison.tsv](P02/unity_claim_comparison.tsv), [P02/erdem_chapter_map.tsv](P02/erdem_chapter_map.tsv)).
   - **Ascriptions.** The article itself says his name appears only on chapters 39 (Text 9) and 52 (the sundial treatise). The witness ascribes chapter 38 to ʿUmayr ibn Samʿān.
   - **Layout.** The group lies in two blocks of the codex with other works between them.
   - **Date.** The table of chapter 30 (Text 11) is later than c. 830.
   - **The list itself.** It skips chapter 57, and it gives the folios of chapters 2–3 both as 228b and as 182b.
   - **ISMI rows.** The article places most of the ISMI database rows: row 19 is a table ascribed to al-Khwārizmī in Cairo, Taymūr 103/2; rows 20 and 22–26 are chapters 1, 2, 4, 20, 33 and 32.
5. **Errors in the two studies** ([P02/errata_of_the_studies.tsv](P02/errata_of_the_studies.tsv)):
   - **In Charette and Schmidl:**
     - Figure 3 shows ff. 91v–92r, not 81v–82r as captioned.
     - Appendix 2 gives the argument of the tables of 94v–95v as latitudes; it is the meridian altitude.
     - The bibliography starts the 1987 article on p. 164, not 163.
   - **In the 1987 article:**
     - Chapter 19's folio is printed 196a for 186a.
     - The article reports that King established the attribution of the whole group; King left it open.
6. **The packet's copy of the 1987 article lacks pp. 181–184.** The publisher's PDF (DergiPark) is the same file. The Turkish version of the article (*Erdem* 3/7, pp. 187–210) is complete; it was acquired and read for these pages ([P02/erdem_inventory.tsv](P02/erdem_inventory.tsv)).
7. **The primary-pixel holds** ([P02/primary_pixel_holds.tsv](P02/primary_pixel_holds.tsv)):
   - **Released:** Berlin, ff. 77v–97v.
   - **Held:** Ayasofya 4830, ff. 182v–200r, 228v–231r and 231v–235r.
   - **Newly recorded:** the Tashkent witness of the qibla tract and the Cairo table, both outside the packet.

## What remains open

[P01/unresolved.tsv](P01/unresolved.tsv) lists the open questions:

- the unseen folios of A;
- a possible second witness named by ISMI (Berlin, Ms. Or. quart. 99, probably al-Farghānī's treatise);
- where Text 2 ends, and whether Texts 5–7 belong to it;
- the folios in A of ISMI rows 19 and 22–26.

AK-P02 placed the ISMI rows by their titles. It left these open ([P02/unresolved.tsv](P02/unresolved.tsv)):

- the folios of the 1987 article's chapters 1–3;
- its missing chapter 57;
- a folio reference of the study (191v) that needs the images of A;
- the comparison of A's table of 163 cities with *Ṣūrat al-arḍ*, which goes to the integration lane.

A diplomatic transcription of the Berlin texts from the images would be a new lane, which the session map does not contain.

## Files

| File | Content |
|---|---|
| `P01/text_map.tsv` | the texts and tables with folios, pages in the study, attribution and classification |
| `P01/codex_items.tsv` | the contents of B (fourteen items and the margins) and of A, as far as they concern the corpus |
| `P01/edition_folio_concordance.tsv` | the sections of the edition, the folio markers it prints, and what the leaves of B show |
| `P01/source_acquisition_gap_ledger.tsv` | what the corpus needs, what the packet had, the routes checked and their results |
| `P01/evidence_ledger.tsv`, `P01/unresolved.tsv` | the claims with their evidence; the open questions |
| `P01/physical_unit_disposition.tsv` | PDF pages 1–34 of the study and the PAL record, each with its role |
| `P01/landberg56_image_inventory.tsv` | the 42 images of B (ff. 77r–97v): folio, size, SHA-256, IIIF address |
| `P01/checkpoint.json`, `P01/SHA256SUMS` | the checkpoint of the return and the hashes of its files |
| `P02/attribution_findings.tsv`, `P02/unity_claim_comparison.tsv`, `P02/erdem_chapter_map.tsv` | the attribution after the commentary; the 1987 article's claim of unity, part by part; its 59 chapters with their folios and the evidence for each |
| `P02/recomputation_checks.tsv`, `P02/cross_lane_checks.tsv`, `P02/checks/` | the recomputed claims; the comparisons with our geography and Zīj; the script and its output |
| `P02/errata_of_the_studies.tsv`, `P02/primary_pixel_holds.tsv` | errors found in the two studies; the exact holds |
| `P02/source_acquisition_gap_ledger.tsv`, `P02/erdem_inventory.tsv` | the new gaps and the acquired Turkish version of the 1987 article |
| `P02/evidence_ledger.tsv`, `P02/unresolved.tsv`, `P02/physical_unit_disposition.tsv`, `P02/checkpoint.json`, `P02/SHA256SUMS` | the evidence, the open questions, the disposition of PDF pages 35–98 of the study and 1–20 of the article, the checkpoint and the hashes |
| `build_p01.py`, `build_p02.py` | write the files of `P01/` and `P02/` (two runs give the same bytes) |

## Licence

The records and the script are AI-integrated work (Claude) and are dedicated to the public domain (CC0 1.0). The study's text and the images of the manuscripts are not reproduced here.
