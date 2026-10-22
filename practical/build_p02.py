"""Write the AK-P02 return (evidence-only audit of Charette and Schmidl, SCIAMVS 5 (2004), PDF pages 35-98, and of
Ahmedov, ad-Dabbagh and Rosenfeld, Erdem 3/7 (1987), PDF pages 1-20, with the PAL record of Ayasofya 4830) into
practical/P02/.  python build_p02.py   (the repository is the folder above this file)"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "practical" / "P02"
ERDEM = REPO / "_intake" / "practical" / "erdem"
STUDY_SHA = "E3FF31E617B84379FCF961310E4914BB6CF40E8E0F5117507AB24D1367626E18"
ERDEM_SHA = "8E04019E12DE893944D623C63597FAAE965C73A070535276DA58E06600F0160F"
PAL_SHA = "5F1D6B016F454E6322B43A0C1F24736473804BDB66196E99F6A9E95A50B2FC88"
OUT.mkdir(parents=True, exist_ok=True)


def tsv(name, header, rows):
    for r in rows:
        assert len(r) == len(header), (name, r)
        for c in r:
            assert "\t" not in str(c) and "\n" not in str(c), (name, c)
    text = "\t".join(header) + "\n" + "".join("\t".join(str(c) for c in r) + "\n" for r in rows)
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------------------------------------------
# physical units: file 50 PDF035-098, file 51 PDF01-20
U = []
part = {}
for p in range(35, 61):
    part[p] = "III Translation"
for p in (61, 62):
    part[p] = "facsimiles (Figures 1-4)"
for p in range(63, 86):
    part[p] = "IV Commentary"
for p in range(86, 92):
    part[p] = "V Appendices"
for p in range(92, 99):
    part[p] = "Bibliography"
content = {
    35: "Text 1 (B 77v-78r)", 36: "Text 1: the table of 78v", 37: "Text 1 (78r-79v)", 38: "Text 1 (80r-80v, figures)",
    39: "Text 1 (81r-81v)", 40: "Text 2 [1]-[2d] (81v-82v)", 41: "Text 2 [3]-[4a] (83r-83v)",
    42: "Text 2 [4b]-[9a] (83v-84v)", 43: "Text 2 [9b]-[12a] (84v-85v)", 44: "Text 2 [12b]-[15b] (85v-86r)",
    45: "Text 2 [16]-[20] (86r-87r)", 46: "Text 2 [21]-[23] (87r-88r)", 47: "Text 2 [24]-[26c] (88r-89r, 89v:7-11)",
    48: "Text 2 [27]-[29] (89r, 89v:1-6, 90r:11-17, 89v:12-17)", 49: "Text 2 [29]-[30a] (90r:1-11, 90v-91r)",
    50: "Text 2 [30b]-[31b] (91r-91v); Text 3 begins", 51: "Text 3 with the table of B 94r",
    52: "Text 4 (92r-93r)", 53: "Texts 5 and 6 (96r-96v)", 54: "Texts 7 and 8 (96v-97v)", 55: "Text 9 (A 198v-199r)",
    56: "Text 9 continued", 57: "Text 10 (A 196v-197r)", 58: "Text 10: table and illustration",
    59: "Text 11 (A 192r) with its table", 60: "Text 11: end of the table",
    61: "Figure 1 (B 80v-81r); Figure 2 (B 81v-82r)", 62: "Figure 3 (captioned B 81v-82r; it shows B 91v-92r); Figure 4 (B 94v-95r)",
    63: "IV.1 Text 1: the attribution; the table of 78v", 64: "IV.1 the functions of the table, R = 98;11",
    65: "IV.1 the geometrical construction (79r-80v), the shadow scale (81r-81v)", 66: "IV.1 analysis of the table; IV.2 Text 2 begins",
    67: "IV.2 Table 3 (78v, north)", 68: "IV.2 Table 4 (78v, south)", 69: "IV.2 sections 2c-4a",
    70: "IV.2 Figure 5; sections 4b-15", 71: "IV.2 sections 15-26 (the excess of revolution)",
    72: "IV.2 sections 26c-31", 73: "IV.2 end; IV.3 Text 3", 74: "IV.3 the shadow formula", 75: "IV.3 table; IV.4 Text 4",
    76: "IV.4 table; IV.5 Text 5", 77: "IV.5 end; IV.6 Text 6; IV.7 Text 7", 78: "IV.7 the zones", 79: "IV.7 end; IV.8 Text 8",
    80: "IV.8 Figure 6 (the sine quadrant)", 81: "IV.8 end; IV.9 Text 9", 82: "IV.9 end; IV.10 Text 10",
    83: "IV.10 end; IV.11 Text 11", 84: "IV.11 Figure 7 (the horary quadrant)", 85: "IV.11 end",
    86: "Appendix 1: the marginal glosses of B 82r-83r", 87: "Appendix 1 continued", 88: "Appendix 2: the table of B 93v",
    89: "Appendix 2: the table of B 94v", 90: "Appendix 2: the table of B 95r", 91: "Appendix 2: the table of B 95v",
}
for p in range(35, 99):
    U.append((f"50:PDF{p:03d}", "50_PRACTICAL_ASTRONOMY_CHARETTE_SCHMIDL.pdf", str(p + 100), "MODERN_EDITORIAL",
              part[p] + (": " + content[p] if p in content else ""), "disposed (read, not reproduced)"))
erdem_pages = list(range(163, 181)) + [185, 186]
erdem_content = {163: "opening; Sezgin; section 1, the codex", 164: "section 1 continued; section 2, the attribution by King",
                 165: "the chapters 1-19 with their folios", 166: "chapters 20-40", 167: "chapters 41-59 (57 is missing); the Tashkent manuscript",
                 168: "section 3, the qibla", 169: "the qibla, chapter 22 (Arabic and English)", 170: "the qibla, Figure 1",
                 171: "the qibla table, chapter 25; the Cairo table; section 4", 172: "chapter 1: the rising amplitude",
                 173: "chapter 1 continued", 174: "section 5, chapter 2", 175: "chapters 2-3 (cited as f. 182b, 182b-183a)",
                 176: "the spherical cosine theorem", 177: "Varahamihira; chapter 4", 178: "chapter 4 (Arabic and English)",
                 179: "section 6, chapter 32", 180: "chapter 32, Figure 7", 185: "the clocks and sundials (end of section 9)",
                 186: "bibliography"}
for i, p in enumerate(erdem_pages, 1):
    U.append((f"51:PDF{i:02d}", "51_ISTANBUL_MANUSCRIPTS_ERDEM.pdf", str(p), "MODERN_EDITORIAL (comparator)",
              erdem_content[p], "disposed (read, not reproduced)"))
U.append(("51:missing", "51_ISTANBUL_MANUSCRIPTS_ERDEM.pdf", "181-184", "MODERN_EDITORIAL (comparator)",
          "printed pages 181-184 are not in the file (it runs 163-180, 185-186); the publisher's PDF on DergiPark is the "
          "same file; their content (the end of section 6, sections 7 and 8, the beginning of section 9) is read in the "
          "Turkish version of the article, pp. 205-209", "gap; covered by the Turkish version"))
tsv("physical_unit_disposition.tsv", ("unit", "source_file", "printed_page", "role", "content", "state"), U)

# ---------------------------------------------------------------------------------------------------------------
# the 59 'chapters' of Ahmedov, ad-Dabbagh and Rosenfeld (1987), pp. 165-167, with the item-level evidence
CH = [
    (1, "azimuth of sunrise in any city, after Ptolemy's diameter of 120", "228a (p. 165, text); 228b (pp. 165, 172)", "20",
     "PAL: the anonymous item of 228v-231r has this title", "anonymous"),
    (2, "azimuth from altitude, southern signs", "228b (list, p. 165); 182b (quotation, p. 175)", "22 (by its title)", "-", "anonymous"),
    (3, "azimuths, northern signs", "228b, 183a (list); 182b-183a (quotation, p. 175)", "-", "-", "anonymous"),
    (4, "operation with the azimuth, the shadow and the altitude", "183a-183b", "23 (by its title)", "-", "anonymous"),
    (5, "altitude from equal and seasonal hours", "183b", "-", "-", "anonymous"),
    (6, "the azimuth", "183b", "-", "-", "anonymous"), (7, "the azimuth again", "183b-184a", "-", "-", "anonymous"),
    (8, "azimuth for every hour and city", "184a", "-", "-", "anonymous"),
    (9, "azimuth of sunrise of any city", "184a", "-", "-", "anonymous"),
    (10, "another chapter", "184a", "-", "-", "anonymous"), (11, "another chapter", "184a", "-", "-", "anonymous"),
    (12, "another chapter", "184a", "-", "-", "anonymous"),
    (13, "azimuth for an altitude of given size", "184a-184b", "-", "-", "anonymous"),
    (14, "azimuth by another method", "184b", "-", "-", "anonymous"), (15, "azimuth of sunrise", "184b", "-", "-", "anonymous"),
    (16, "azimuth from the ascendant", "184b", "-", "-", "anonymous"),
    (17, "azimuth for any hour and degree of the signs", "184b-185b", "-", "-", "anonymous"),
    (18, "the hours by the azimuth", "185b-186a", "-", "-", "anonymous"),
    (19, "altitude for the hours", "196a (English, p. 165); 186a (Turkish, p. 190)", "-",
     "196a is a misprint: chapter 18 ends and chapter 20 begins on 186a", "anonymous"),
    (20, "direction of the qibla in any city", "186a-186b", "24 (by its title)",
     "Tashkent, al-Biruni Institute 177/3, ff. 148a-151a, has the same title; King found a textual coincidence (p. 165)", "anonymous"),
    (21, "the meridian line", "186b", "-", "-", "anonymous"),
    (22, "qibla for any latitude", "187a", "-", "= Tashkent chapter 2 (p. 167)", "anonymous"),
    (23, "another chapter on the qibla", "187a-187b", "-", "= Tashkent chapter 3", "anonymous"),
    (24, "a shorter chapter on the qibla", "187b", "-", "= Tashkent chapter 4", "anonymous"),
    (25, "azimuth of the qibla from the table", "187b-188a", "-", "= Tashkent chapter 5; a similar table is ascribed to "
     "al-Khwarizmi in Cairo, Taymur 103/2, ff. 101a-102a, 'al-jadwal al-ishrini' (ISMI row 19) (p. 171)", "anonymous"),
    (26, "table of shadows and inclinations", "188b", "-", "-", "anonymous"),
    (27, "the binkans (water clocks), equal and seasonal hours", "189a-190a", "12 (probable)", "study item A-a", "anonymous"),
    (28, "the binkan that shoots pebbles", "190a-190b", "11 (probable)", "study item A-b", "anonymous"),
    (29, "the horary lifting wheel (dulab)", "191a-192a", "17", "study item A-c", "anonymous"),
    (30, "the conical sundial (mukhula)", "192a", "14", "Text 11; obliquity 23;33 of its table: after c. 830; probably not "
     "al-Khwarizmi's (study p. 183)", "anonymous"),
    (31, "the sundial called miknasa", "193a", "13", "study item A-e (maknasa)", "anonymous"),
    (32, "geometric azimuth of sunrise for any sign and latitude", "193b", "26 (by its title)", "-", "anonymous"),
    (33, "latitude of a city", "193b-194a", "25 (by its title)", "-", "anonymous"),
    (34, "geometric latitude of a city", "194a", "-", "-", "anonymous"),
    (35, "cities in all climes (163 cities)", "194b-196b", "-", "study item A-f (194v-196v); the study (n. 92): edited by "
     "Kennedy and Kennedy (1987) as KHZ; Baghdad 70 there, as in Text 2", "anonymous"),
    (36, "the horary quadrant", "196b-197a", "9", "Text 10", "anonymous"),
    (37, "the compass for a camp (birkar al-hilla)", "197a-197b", "5", "study item A-h", "anonymous"),
    (38, "a board for the lunar eclipse", "198a", "10 (by its title)", "study item A-i: the witness ascribes it to Umayr "
     "ibn Saman (p. 108)", "ascribed to another person"),
    (39, "'witty pieces from the work of Muhammad ibn Musa al-Khwarizmi': the azimuth with the astrolabe", "198b-199a", "7",
     "Text 9; the title implies an extract (study p. 181)", "ascribed to al-Khwarizmi"),
    (40, "latitudes of the climes", "199a-199b", "28", "study item A-k", "anonymous"),
    (41, "times of prayers from the table (beginning missing)", "229a-229b", "-", "PAL: within the anonymous item 228v-231r",
     "anonymous"),
    (42, "midday altitude for any day and latitude", "229b", "-", "-", "anonymous"),
    (43, "the surplus of the day from the table", "229b", "-", "-", "anonymous"),
    (44, "when the sun is in the zenith", "229b", "-", "-", "anonymous"),
    (45, "when the sun is in the zenith a second time", "229b", "-", "-", "anonymous"),
    (46, "the shadow of an hour with a gnomon", "229b-230a", "-", "-", "anonymous"),
    (47, "the shadows for the prayer times", "230a", "-", "-", "anonymous"),
    (48, "midday altitude for any day and latitude", "230a", "-", "-", "anonymous"),
    (49, "the altitude and the times of asr and zuhr", "230b", "-", "-", "anonymous"),
    (50, "midday altitude for latitude 34 (table)", "230b", "-", "-", "anonymous"),
    (51, "altitude for latitude 33 (table)", "231a", "-", "-", "anonymous"),
    (52, "the hours on the plane sundial, by Muhammad ibn Musa al-Khwarizmi", "231b", "15", "PAL: al-Khwarizmi, 231v-235r; "
     "authorship questioned by King (1999), defended by Charette (2003)", "ascribed to al-Khwarizmi"),
    (53, "sundial for Baghdad, every sixth of an hour (table)", "231b-232b", "-", "-", "within the ascribed treatise"),
    (54, "first and last azimuths and shadows of asr (tables)", "232b", "-", "-", "within the ascribed treatise"),
    (55, "sundial for the latitudes 15-40 (table)", "233a-234a", "-", "-", "within the ascribed treatise"),
    (56, "sundial for Samarra, latitude 34 (table)", "234a", "-", "-", "within the ascribed treatise"),
    (57, "(no chapter 57 in the list, in the English or the Turkish version)", "-", "-", "-", "-"),
    (58, "sundial for the equator", "234a-234b", "-", "-", "within the ascribed treatise"),
    (59, "geometric sundial for any latitude", "234b-235a", "-", "-", "within the ascribed treatise"),
]
tsv("erdem_chapter_map.tsv", ("chapter", "subject_in_our_words", "folios_as_printed", "ismi_row_in_08_map",
                              "item_level_evidence", "name_in_the_witness"), [tuple(map(str, c)) for c in CH])

# ---------------------------------------------------------------------------------------------------------------
# the unity claim, part by part
UC = [
    ("C1", "the whole group of ff. 182(183)a-199b and 228b-235a is al-Khwarizmi's (Erdem p. 164)",
     "the article itself states that his name appears only on chapters 39 and 52 (p. 164); one tract (chapter 38) is "
     "ascribed in the witness to Umayr ibn Saman (Charette and Schmidl p. 108)", "not supported: two ascriptions to "
     "al-Khwarizmi and one to another person within the group"),
    ("C2", "King established the attribution of the group (Erdem p. 164)",
     "King (1983a: 2), as quoted by Charette and Schmidl (p. 107), states that the attribution of each text is an open "
     "problem", "misreported"),
    ("C3", "a complete sine of 150, borrowed from Brahmagupta, marks al-Khwarizmi's time (Erdem p. 164)",
     "the same base is used in Texts 1, 8 and 10 of B; Charette and Schmidl treat it as a sign of the early ninth "
     "century (p. 163), not of one author; chapter 1 uses a radius of 60 (Erdem p. 173)", "dates, does not attribute"),
    ("C4", "the group is one work divided into 59 chapters (Erdem p. 165)", "the group lies in two blocks separated by "
     "the works of ff. 200v-227v (PAL; Erdem p. 164); the list skips chapter 57; chapter 41 lacks its beginning; the "
     "folios of chapters 2-3 are given as 228b and as 182b; PAL catalogues 228v-231r as anonymous and 231v-235r as "
     "al-Khwarizmi's", "not supported; Charette and Schmidl call it an illusory unity (p. 107)"),
    ("C5", "dating evidence within the group", "the table of chapter 30 (Text 11) rests on the obliquity 23;33, first "
     "observed in 213 H (828-29), so it is later than c. 830 (Charette and Schmidl p. 183); Erdem himself suggests that "
     "the chapters with plane trigonometry are earlier than those with spherical trigonometry (Turkish version p. 205)",
     "the group is not of one date"),
    ("C6", "the qibla chapters 20-25 are al-Khwarizmi's (Erdem pp. 165-171)", "a textual coincidence with the anonymous "
     "Tashkent manuscript (King) and a similar 20 x 20 table ascribed to al-Khwarizmi in Cairo, Taymur 103/2 (p. 171)",
     "a parallel, not an ascription in the witness; the strongest case in the group after chapters 39 and 52"),
]
tsv("unity_claim_comparison.tsv", ("id", "claim_in_erdem", "item_level_evidence", "result"), UC)

# ---------------------------------------------------------------------------------------------------------------
# the attribution, item by item, after the commentary (study pp. 163-185)
AT = [
    ("Text 1", "B 77v-81v", "Ibn al-Nadim lists treatises on the construction and the use; plate radius 150; style close "
     "to Text 2; copied before Text 2 (King 1983a: 23)", "the table of 78v rests on the obliquity 23;35 (R = 98;11), a "
     "Mumtahan value linked to Habash, where al-Khwarizmi used 23;51; the geometric section 79r-80v takes the radius as 60",
     "speculative (p. 163)", "ANONYMOUS_ATTRIBUTION_ARGUED"),
    ("Text 2", "B 81v:4-91v:7", "the incipit names him; the excess of revolution 93;2 (section 25) is his value",
     "section 26c (89v:7-11), «from another copy», gives 93;15, the value of the Zij-i Shah and Mashaallah: probably "
     "interpolated (p. 172); Rayy 37 (section 27) departs from his geography (35;45); Baghdad 70 (section 31) departs from "
     "his geography (73) but agrees with the anonymous table of A", "his treatise, the earliest in Arabic on the subject "
     "(p. 166)", "EXPLICIT_ASCRIPTION (with an interpolated passage)"),
    ("Text 3", "B 91v:8-92r:16, 94r", "-", "-", "no argument (IV.3)", "ANONYMOUS_MILIEU"),
    ("Text 4", "B 92r:17-93r", "-", "-", "no argument (IV.4)", "ANONYMOUS_MILIEU"),
    ("Text 5", "B 96r", "-", "the same nomenclature in Severus Sebokht and a thirteenth-century Latin text", "no argument "
     "(IV.5)", "ANONYMOUS_MILIEU"),
    ("Text 6", "B 96r-96v", "-", "the same method as section 24 of Text 2, more clearly (IV.6)", "no argument",
     "ANONYMOUS_MILIEU"),
    ("Text 7", "B 96v", "-", "the scheme and its error are those of Sebokht, chapter 24: a Syriac or Greek source (IV.7)",
     "no argument", "ANONYMOUS_MILIEU"),
    ("Text 8", "B 96v-97v", "style; base 150; al-Marrakushi reports that some call the sine function al-jayb al-khwarizmi",
     "a declination of 30 degrees given as 25 and minutes; an erroneous graphical procedure (IV.8)", "not unreasonable "
     "(p. 179)", "ANONYMOUS_ATTRIBUTION_ARGUED"),
    ("Text 9", "A 198v-199r", "the title names him («witty pieces from the work of Muhammad ibn Musa al-Khwarizmi»)",
     "the title implies an extract from a larger work (p. 181)", "his", "EXPLICIT_ASCRIPTION (extract)"),
    ("Text 10", "A 196v-197r", "base 150; the term kardaja; latitude 33 (Baghdad)", "-", "could be a sign of his authorship "
     "(p. 182)", "ANONYMOUS_ATTRIBUTION_POSSIBLE"),
    ("Text 11", "A 192r", "-", "the obliquity 23;33 of its table: later than c. 830", "probably not his (p. 183)",
     "ANONYMOUS_PROBABLY_NOT_AUTHORIAL"),
    ("Table B 93v", "B 93v", "a link through King (2004, I: 147, n. 11)", "obliquity 23;35, as Text 1", "-",
     "ANONYMOUS_LINK_SUGGESTED"),
    ("Table B 95r-95v", "B 95r-95v", "Hogendijk (1991)", "-", "his", "ATTRIBUTED_BY_ANALYSIS"),
    ("Sundial", "A 231v-235r", "the treatise names him (Erdem chapter 52; PAL)", "King (1999) questioned the authorship",
     "his (Charette 2003: 181)", "EXPLICIT_ASCRIPTION_DISPUTED"),
    ("Eclipse board", "A 198r", "-", "the witness ascribes it to Umayr ibn Saman (p. 108)", "-", "OTHER_AUTHOR"),
    ("Qibla tract", "A 186a-188a (Erdem chapters 20-25)", "a textual coincidence with the Tashkent manuscript; a similar "
     "table ascribed to al-Khwarizmi in Cairo, Taymur 103/2", "-", "not treated by Charette and Schmidl",
     "ANONYMOUS_ATTRIBUTION_ARGUED"),
]
tsv("attribution_findings.tsv", ("item", "witness", "for_al_khwarizmi", "against_or_other", "study_verdict",
                                 "classification"), AT)

# ---------------------------------------------------------------------------------------------------------------
# recomputations of the study's claims (practical/P02/checks/cs_checks.py)
RC = [
    ("K01", "R = 150 / tan((90 + 23;35) / 2) = 98;11 (p. 164)", "98;11,18; R = 98;11 implies an obliquity of 23;35,09; "
     "with 23;51 R would be 97;41,25", "agrees"),
    ("K02", "the errors of Table 3 (78v, north) against R = 98;11 (p. 167)", "at 1, 2, 10, 17, 23, 29, 45, 60, 89 degrees: "
     "+2, -38, 0, -10, +50, -39, +1, +41, +1 minutes, as printed", "agrees"),
    ("K03", "the excess of revolution of 365;15,30,22,30 days is 93;2,15 and of 365;15,32,30 days 93;15 (pp. 171-172)",
     "93;02,15 and 93;15,00", "agrees"),
    ("K04", "Text 8: the procedure gives 1 2/3 hours for hm = 60, h = 30, the correct formula 2 1/3 (p. 181)",
     "1.711 h and 2.351 h", "agrees"),
    ("K05", "Text 7: the five zones 36;9, 30, 23;51 twice, 30, 36;9 make 180 (p. 178)", "180;0", "agrees"),
    ("K06", "Text 3: the midday shadow is the integer part of 12 cot <90 - phi + delta>, phi = 33 (p. 174)",
     "at longitudes 90, 60, 30, 0, -30, -60, -90 from the equinox: 2, 2, 4, 7, 12, 16, 18, as the study's recomputation "
     "(with the obliquity 23;51)", "agrees"),
]
tsv("recomputation_checks.tsv", ("id", "claim", "result", "verdict"), RC)

# ---------------------------------------------------------------------------------------------------------------
# checks against the other lanes of this project
XC = [
    ("X01", "Text 2 section 27: Kufa 32 (study p. 172: rounded from al-Khwarizmi's 31;50)", "geography AK05-F027-L13: "
     "entry 299, الكوفة, longitude سط ل (69;30), latitude لا ن (31;50)", "agrees with the study"),
    ("X02", "Text 2 section 27: Rayy 37 (study p. 172: al-Khwarizmi's tables give 35;45)", "geography AK05-F028-L06: "
     "entry 309, الرىّ, longitude عه (75;0), latitude له مه (35;45)", "agrees with the study: Text 2 departs from the "
     "geography"),
    ("X03", "Text 2 section 31: Baghdad 70 (study n. 92: Surat al-ard has 73)", "geography AK05-F027-L14: entry 300, بغداد, "
     "longitude printed عح, latitude لح ط; the observation of that page notes that ح there is the form of a ج without "
     "its dot (3): 73, and 33;9", "agrees with the study when ح is read as ج"),
    ("X04", "Text 2 section 31: Damascus 60 (study n. 92: also 60 in Surat al-ard)", "geography AK05-F026-L02: entry 269, "
     "دمشق, longitude س (60), latitude لح (33 when read as لج)", "agrees with the study"),
    ("X05", "Text 2 section 25: excess 93;2, al-Khwarizmi's value", "zij AK07-J0262-L07: Tab. 115, one year, 93 2 15",
     "agrees"),
    ("X06", "study n. 87: al-Majriti's recension mentions a year of 365;15,32,30 (Suter 1914: 42)", "zij AK07-J0074-L08 to "
     "L13: Suter derives 365d 6h 13m (= 365;15,32,30) himself from Tables 4 and 5; zij AK07-J0267-L22 to L33: in his "
     "fourth addition he corrects the computation to 365d 6h 12m; Tab. 115 gives 93;2,15 a year (365;15,30,22,30)",
     "the recension does not state 365;15,32,30: it is Suter's derivation, which he revised"),
    ("X07", "Erdem (Turkish version p. 205): the coordinates of the 163 cities of A 194b-196b agree in general with Surat "
     "al-ard", "A not seen; the comparison with geography/ awaits the images of A (or Kennedy and Kennedy 1987, KHZ)",
     "open: for AK-I01"),
]
tsv("cross_lane_checks.tsv", ("id", "claim", "our_record", "result"), XC)

# ---------------------------------------------------------------------------------------------------------------
# errors in the two studies
ER = [
    ("S01", "Charette-Schmidl", "p. 162, Figure 3", "caption «(B:81v-82r)»", "B:91v-92r",
     "the plate shows f. 92r (with «92» in its corner) and f. 91v, identical with the images of MPIWG canvases 0191 and "
     "0190; the caption repeats that of Figure 2", "high"),
    ("S02", "Charette-Schmidl", "pp. 189-190, Appendix 2", "the tables of 94v and 95r-95v «for latitudes 25 to 90»",
     "for meridian altitudes 25 to 90", "p. 106 (8) describes the argument as the meridian altitude; the heading of 94v "
     "reads «ارتفاع نصف النهار من كه الى ص»", "high"),
    ("S03", "Charette-Schmidl", "p. 172, n. 87", "al-Majriti's recension «mentions» a year of 365;15,32,30",
     "Suter derives it (p. 42) and corrects it to 365d 6h 12m (p. 235)", "see cross_lane_checks.tsv X06", "high"),
    ("S04", "Charette-Schmidl", "p. 192, bibliography", "Ahmedov, ad-Dabbagh and Rosenfeld (1987) «3/7: 164-186»",
     "3/7: 163-186", "the article begins on p. 163 (the PDF and DergiPark)", "high"),
    ("S05", "Charette-Schmidl", "p. 107", "A «copied in Damascus in Ramadan 626 H»", "626-627 H (1229-30); Ramadan 626 for "
     "the Ptolemaic part", "the PAL record", "high"),
    ("S06", "Charette-Schmidl", "pp. 110-112 and 135-137", "the edition and the translation move the table of 78v before "
     "the paragraph «الكواكب» of 78r without saying so", "-", "AK-P01 E03", "high"),
    ("S07", "Charette-Schmidl", "p. 123 (edition)", "the marker (90r:1-10)", "(90r:1-11), as in the translation (p. 149)",
     "the red «وقت الظهر» stands within line 11 of 90r, which is shared by sections 29 and 28d", "medium"),
    ("E01", "Ahmedov et al.", "p. 165", "chapter 19 «(f. 196a)»", "186a", "chapter 18 ends and chapter 20 begins on 186a; "
     "the Turkish version (p. 190) has 186a", "high"),
    ("E02", "Ahmedov et al.", "p. 167", "the list of 59 chapters has no chapter 57", "-", "the same in the Turkish version "
     "(p. 192)", "high"),
    ("E03", "Ahmedov et al.", "pp. 165 and 175", "chapters 1-2 and the beginning of 3 «on f. 228a», chapters 2-3 «228b», "
     "and the quotations of chapters 2-3 «F. 182b» and «182b-183a»", "unresolved", "PAL records f. 228r as blank and the "
     "group as beginning on 182v; the images of A are needed", "high (the inconsistency); open (the true folios)"),
    ("E04", "Ahmedov et al.", "p. 164", "King «established» the attribution of the whole group", "-", "King (1983a: 2) "
     "leaves it open (Charette and Schmidl p. 107)", "high"),
    ("E05", "packet file 51", "pp. 181-184", "missing from the PDF", "-", "the publisher's PDF (DergiPark, article file "
     "693897) is the same file, byte for byte; the Turkish version (pp. 187-210, DergiPark article file 693901) is complete",
     "high"),
]
tsv("errata_of_the_studies.tsv", ("id", "work", "place", "printed", "correct", "evidence", "confidence"), ER)

# ---------------------------------------------------------------------------------------------------------------
# the primary-pixel holds, exactly
H = [
    ("B", "Berlin, Staatsbibliothek, Landberg 56", "77v-97v (Texts 1-8, tables, margins 82r-83r, table 97v)",
     "RELEASED: public images, MPIWG digilib (ISMI digitization 284658), CC BY-SA 4.0; acquired 2026-10-22 as canvases "
     "0161-0202 (ff. 77r-97v; P01/landberg56_image_inventory.tsv)", "AK-P01 G01"),
    ("A", "Istanbul, Suleymaniye, Ayasofya 4830", "182v-200r (PAL); 183a-199b with 182b (Erdem); Texts 9-11, chapters 2-40",
     "HOLD: no public images (PAL shows ff. 53r-80v only; ISMI none; YEK portal after a member login)", "AK-P01 G02"),
    ("A", "Istanbul, Suleymaniye, Ayasofya 4830", "228v-231r (anonymous per PAL; Erdem chapters 1-3? and 41-51)", "HOLD",
     "AK-P01 G03"),
    ("A", "Istanbul, Suleymaniye, Ayasofya 4830", "231v-235r (the sundial treatise; Erdem chapters 52-59)", "HOLD",
     "AK-P01 G04"),
    ("T", "Tashkent, al-Biruni Institute of Oriental Studies, 177/3", "148a-151a (the qibla tract, copied c. 1250; Erdem "
     "p. 165)", "HOLD: not in the packet; not located", "new"),
    ("K", "Cairo, Taymur 103/2", "101a-102a ('al-jadwal al-ishrini' ascribed to al-Khwarizmi; ISMI row 19; Erdem p. 171)",
     "HOLD: not in the packet; not located", "new"),
    ("L", "London, British Library, MS 9116 (as Erdem cites it)", "a zij written in Yemen in the thirteenth century, with a "
     "similar qibla table (Erdem p. 171)", "reference only", "new"),
]
tsv("primary_pixel_holds.tsv", ("siglum", "witness", "folios", "state", "ledger"), H)

# ---------------------------------------------------------------------------------------------------------------
# the acquired supplementary source
inv = []
for f in sorted(ERDEM.glob("*.pdf")):
    b = f.read_bytes()
    inv.append((f.name, len(b), hashlib.sha256(b).hexdigest().upper(),
                "https://dergipark.org.tr/en/download/article-file/" + f.stem.split("_")[-1]))
tsv("erdem_inventory.tsv", ("local_file", "bytes", "sha256", "source_url"), inv)

G = [
    ("G09", "the content of pp. 181-184 of the 1987 article", "packet file 51", "pp. 181-184",
     "missing from the packet's file", "DergiPark, issue 44566: the English article (article file 693897) and its Turkish "
     "version (article file 693901)", "ACQUIRED 2026-10-22: the English PDF is the packet's file byte for byte (same "
     "SHA-256), so the publisher's copy lacks the pages too; the Turkish version, pp. 187-210, is complete and holds the "
     "same sections (pp. 205-209)", "none"),
    ("G10", "the Tashkent witness of the qibla tract", "al-Biruni Institute 177/3", "148a-151a", "not in the packet",
     "not searched", "NOT ACQUIRED", "a later lane, if the qibla tract becomes a production target"),
    ("G11", "the Cairo table ascribed to al-Khwarizmi (ISMI row 19)", "Taymur 103/2", "101a-102a", "not in the packet",
     "not searched", "NOT ACQUIRED", "as G10"),
]
tsv("source_acquisition_gap_ledger.tsv", ("gap", "needed_for", "witness", "folios", "packet_state", "route_checked",
                                          "result", "remaining_action"), G)

E = [
    ("E01", "Figure 3 of the study shows ff. 91v-92r, not 81v-82r", "study p. 162; MPIWG canvases 0190, 0191",
     "the plate and the images agree line for line; «92» in the corner of the left page", "the caption repeats Figure 2's",
     "high", "errata S01"),
    ("E02", "the passage of 89v:7-11 gives 93;15 and is marked by the copyist as from another copy", "B 89v:7; study pp. "
     "171-172", "«ووجدت في نسخة اخرى»", "the study identifies the value with the Zij-i Shah and Mashaallah and judges the "
     "passage interpolated; the recension's Tab. 115 supports section 25's 93;2", "high", "attribution_findings Text 2"),
    ("E03", "The 59-chapter unity is not supported by the item-level evidence", "Erdem pp. 164-167; study pp. 107-108, "
     "181-183; PAL", "two ascriptions to al-Khwarizmi (chapters 39 and 52) and one to Umayr ibn Saman (chapter 38) in the "
     "witness; two separated blocks; a table later than c. 830 (chapter 30)", "see unity_claim_comparison.tsv", "high",
     "the packet's boundary stands"),
    ("E04", "ISMI rows 19 and 20-26 can be placed", "Erdem pp. 165-171", "row 19 = Cairo, Taymur 103/2; row 20 = chapter 1 "
     "(228v); rows 22-26 = chapters 2, 4, 20, 33, 32 (by their titles)", "titles only; no folio of A seen", "medium",
     "erdem_chapter_map.tsv; resolves AK-P01 U07 by title"),
    ("E05", "The packet's file 51 is incomplete, and so is the publisher's PDF", "file 51; DergiPark 693897",
     "same SHA-256; printed pages 163-180 and 185-186", "the Turkish version supplies the content", "high",
     "errata E05; gap G09"),
    ("E06", "Six arithmetic and astronomical claims of the study recompute correctly", "practical/P02/checks/cs_checks.py",
     "see recomputation_checks.tsv", "-", "high", "-"),
    ("E07", "Four comparisons of Text 2 with al-Khwarizmi's geography and two with the Zij agree with the study, one note "
     "of the study overstates its source", "geography and zij anchors", "see cross_lane_checks.tsv", "-", "high",
     "errata S03"),
]
tsv("evidence_ledger.tsv", ("id", "claim", "source_coordinates", "witnessed_reading", "reasoning", "confidence",
                            "artifact_impact"), E)

UR = [
    ("U01", "the folios of Erdem's chapters 1-3 (228v, or 182v, or both through a displaced leaf)", "the article is "
     "inconsistent; PAL: 228r blank, the group from 182v", "the images of A"),
    ("U02", "whether a chapter 57 exists", "missing from both versions of the list", "the images of A"),
    ("U03", "the study's n. 130: the labels of the figure of 192v 'as in the table on f. 191v'", "the table of Text 11 is "
     "on 192r (p. 185); 191v may be a slip or another table", "the images of A"),
    ("U04", "where Text 2 ends; whether Texts 5-7 belong to it", "the commentary treats Texts 5-7 as separate, Text 6 "
     "repeating section 24 more clearly and Text 7 depending on Sebokht's source", "a later edition"),
    ("U05", "Berlin, Ms. Or. quart. 99 (AK-P01 U04)", "not checked", "-"),
    ("U06", "the 163 cities of A against Surat al-ard (Erdem's claim)", "not checked", "AK-I01, with the images of A or "
     "Kennedy and Kennedy (1987)"),
]
tsv("unresolved.tsv", ("id", "question", "state", "routed_to"), UR)

# ---------------------------------------------------------------------------------------------------------------
files = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name not in ("SHA256SUMS", "checkpoint.json"))
canon = hashlib.sha256()
for name in files:
    canon.update(name.encode() + b"\0" + (OUT / name).read_bytes())
ck = {
    "session": "AK-P02",
    "mode": "evidence-only audit; no source-text production; no reader from comparator prose",
    "owned_range": "PDF035-PDF098 of 50_PRACTICAL_ASTRONOMY_CHARETTE_SCHMIDL.pdf (printed pp. 135-198) and PDF01-PDF20 of "
                   "51_ISTANBUL_MANUSCRIPTS_ERDEM.pdf (printed pp. 163-180, 185-186), with the PAL record",
    "study_sha256": STUDY_SHA, "erdem_sha256": ERDEM_SHA, "pal_record_sha256": PAL_SHA,
    "canonical_source_checkpoint_sha256": canon.hexdigest(),
    "canonical_source_checkpoint_note": "SHA-256 over the return files in name order (file name, a NUL byte, the bytes), "
                                        "without checkpoint.json and SHA256SUMS",
    "last_fully_transcribed_source_unit": "NONE",
    "last_fully_verified_source_unit": "51:PDF20",
    "first_untouched_source_unit": "NONE",
    "owned_units_total": 84,
    "owned_units_disposed": 84,
    "unresolved_count": len(UR),
    "figure_count": 0,
    "formula_or_table_count": 0,
    "supplementary_source_acquired": "Erdem 3/7 (1987), pp. 187-210, the Turkish version (DergiPark article file 693901)",
    "date": "2026-10-22",
}
(OUT / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
names = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS")
(OUT / "SHA256SUMS").write_text("".join(f"{hashlib.sha256((OUT / n).read_bytes()).hexdigest()}  {n}\n" for n in names),
                                encoding="utf-8", newline="\n")
print("written:", ", ".join(names + ["SHA256SUMS"]))
