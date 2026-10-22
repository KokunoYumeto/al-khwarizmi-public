"""Write the AK-P01 return (evidence and attribution audit of Charette and Schmidl, SCIAMVS 5 (2004), PDF pages 1-34,
with the PAL record of Ayasofya 4830 and the images of Berlin Landberg 56) into practical/P01/.
python build_p01.py   (run from anywhere; the repository is the folder above this file)"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "practical" / "P01"
IMG = REPO / "_intake" / "practical" / "landberg56"
PACKET_STUDY_SHA = "E3FF31E617B84379FCF961310E4914BB6CF40E8E0F5117507AB24D1367626E18"
PAL_SHA = "5F1D6B016F454E6322B43A0C1F24736473804BDB66196E99F6A9E95A50B2FC88"
MANIFEST = "https://digilib.mpiwg-berlin.mpg.de/digitallibrary/Manifester/IIIF/permanent!library!RXBT90D9!pageimg"
SCALER = "https://digilib.mpiwg-berlin.mpg.de/digitallibrary/Scaler/IIIF/permanent%21library%21RXBT90D9%21pageimg%21{c}/full/full/0/default.jpg"
OUT.mkdir(parents=True, exist_ok=True)


def tsv(name, header, rows):
    for r in rows:
        assert len(r) == len(header), (name, r)
        for c in r:
            assert "\t" not in str(c) and "\n" not in str(c), (name, c)
    text = "\t".join(header) + "\n" + "".join("\t".join(str(c) for c in r) + "\n" for r in rows)
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------------------------------------------
# physical units: PDF001-034 of the study (the owned range) and the PAL authority record
units = [
    ("PDF001", "101", "title, authors, dedication, summary; I Introduction begins; acknowledgements (note)"),
    ("PDF002", "102", "introduction: al-Khwarizmi's practical interests; the corpus: two texts ascribed to him, the rest anonymous"),
    ("PDF003", "103", "introduction: the edition and its two manuscripts; I.1 Description of the manuscripts; B begins"),
    ("PDF004", "104", "B: inscriptions of the title page, the Rasulid sultan and the dating, ownership marks, foliation, quires, hand, glosses"),
    ("PDF005", "105", "B: the numerals of the tables; contents of B, items 1-5"),
    ("PDF006", "106", "B: contents, items 6-14"),
    ("PDF007", "107", "B: item 14 ends; A: description, the 59 'chapters' of Ahmedov et al. (1987) rejected; Text 9 announced"),
    ("PDF008", "108", "A: Texts 9-11; the other anonymous tracts of A, 189r-199r"),
    ("PDF009", "109", "A: 199r-200r and the sundial treatise 231v-235r; remarks on the edition and the translation"),
    ("PDF010", "110", "II Edition; Text 1 (B 77v-78r)"),
    ("PDF011", "111", "Text 1: the table (title on B 78r, body on 78v)"),
    ("PDF012", "112", "Text 1 (B 78r-79v)"),
    ("PDF013", "113", "Text 1 (B 79v-80v, with the two figures of 80r and 80v)"),
    ("PDF014", "114", "Text 1 (B 81r-81v)"),
    ("PDF015", "115", "Text 2 [1]-[2d] (B 81v-82v)"),
    ("PDF016", "116", "Text 2 [2d]-[4b] (B 82v-84r)"),
    ("PDF017", "117", "Text 2 [5a]-[9b] (B 84r-85r)"),
    ("PDF018", "118", "Text 2 [10]-[14] (B 85r-86r)"),
    ("PDF019", "119", "Text 2 [15a]-[18] (B 86r-87r)"),
    ("PDF020", "120", "Text 2 [19]-[23] (B 87r-88r)"),
    ("PDF021", "121", "Text 2 [24]-[26b] (B 88r-89r)"),
    ("PDF022", "122", "Text 2 [26c]-[28e] (B 89v:7-11, 89r, 89v:1-6, 90r:11-17)"),
    ("PDF023", "123", "Text 2 [29]-[30b] (B 89v:12-17, 90r:1-10, 90v-91r)"),
    ("PDF024", "124", "Text 2 [30c]-[31b] (B 91r-91v:7); Text 3 begins (B 91v:8-92r)"),
    ("PDF025", "125", "Text 3, with the table of B 94r"),
    ("PDF026", "126", "Text 3 ends; Text 4 (B 92r:17-92v)"),
    ("PDF027", "127", "Text 4: the figure of B 93r; Text 5 (B 96r)"),
    ("PDF028", "128", "Texts 6, 7 and 8 (B 96r-97r)"),
    ("PDF029", "129", "Text 8 ends (B 97r-97v)"),
    ("PDF030", "130", "Text 9 (A 198v-199r)"),
    ("PDF031", "131", "Text 10 (A 196v-197r)"),
    ("PDF032", "132", "Text 10: its table and the figure of the quadrant"),
    ("PDF033", "133", "Text 11 (A 192r), with its table"),
    ("PDF034", "134", "Text 11: the figure of the mukhula (A 192v)"),
]
rows = []
for u, p, c in units:
    role = "MODERN_EDITORIAL: introduction (evidence; read, not reproduced)" if int(p) <= 109 else \
        "MODERN_EDITORIAL: critical edition of the Arabic text (mapped to the folios, not reproduced)"
    rows.append((u, "50_PRACTICAL_ASTRONOMY_CHARETTE_SCHMIDL.pdf", p, role, c, "disposed"))
rows.append(("PAL-A4830", "10_AUTHORITY_METADATA.zip::authority/AYASOFYA_4830_PAL_RECORD.html", "-",
             "AUTHORITY: codex record (evidence)", "Ptolemaeus Arabus et Latinus record of Ayasofya 4830: date, origin, "
             "codicology, contents with folios; images only for ff. 53r-80v", "disposed"))
tsv("physical_unit_disposition.tsv", ("unit", "source_file", "printed_page", "role", "content", "state"), rows)

# ---------------------------------------------------------------------------------------------------------------
# the texts and the other items of the Khwarizmiana, with their attribution
T = [
    ("Text 1", "On the construction of the astrolabe", "B", "77v-81v (table 78v; sections 79r-80v and 81r-81v)",
     "77v red «صنعة الاسطرلاب» after the basmala; 78r red «الكواكب» in mid-page and, at its foot, red «جدول» with the "
     "title of the table, whose body fills 78v; 79r red «عمل المقنطرات بالهندسة»; figures on 80r and 80v; 81r red «عمل "
     "الظل في ظهر الاسطرلاب بالهندسة»; 81v:1-3 end the text",
     "PDF010-014", "110-114", "none", "anonymous; formerly taken for part of al-Farghani's treatise (Wiedemann, Frank); "
     "the study gives arguments for al-Khwarizmi's authorship and evidence against it in its commentary (p. 105)",
     "none named", "AK11", "8 (Sanat al-asturlab)", "ANONYMOUS_ATTRIBUTION_ARGUED"),
    ("Text 2", "On the use of the astrolabe", "B", "81v:4-91v:7",
     "81v: three lines and a figure, then on the fourth line «قال محمد بن موسى الخوارزمي اول ما يحتاج اليه الناظر في عمل "
     "الاسطرلاب», «قال» in red; from the foot of 88r centred red chapter headings; 91v:8 begins Text 3",
     "PDF015-024", "115-124", "explicit: the incipit names Muhammad ibn Musa al-Khwarizmi",
     "the only text of B that names him; untitled; where it ends is not certain; the chapters from the foot of 88r to "
     "91v:7 (sections 24-31) have centred headings; the edition reorders some material (pp. 105, 109)",
     "German, Frank (1922); Russian, Matvievskaya (1983); extracts edited by Kunitzsch (1987), who showed that they are "
     "in part a source of the Sententiae astrolabii (p. 103, n. 6)", "AK10", "6 (Kitab al-amal bi-al-asturlab)",
     "EXPLICIT_ASCRIPTION"),
    ("Text 3", "On a compass for finding the prayer-times", "B", "91v:8-92r:16 and the table on 94r",
     "91v:8 red «عمل بركار يعرف به الاوقات للصلوة»; 92r:6 red «صفة العمل بهذا البيكار»; the table on 94r",
     "PDF024-026", "124-126", "none", "anonymous, of the same milieu (p. 102); the table on 94r is misplaced in the codex "
     "and belongs to this text (King 1983a: 7; King 2004) (p. 106)", "German, Frank and Wiedemann (1919), without the "
     "table", "AK14", "16 (Amal birkar yuraf bihi al-awqat li-al-salah)", "ANONYMOUS_MILIEU"),
    ("Text 4", "On a plate for finding the altitude and the times of moonrise and moonset", "B", "92r:17-93r (figure on 93r)",
     "92r:17 red «عمل صفيحة يؤخذ بها الارتفاع ويعرف بها طلوع»; the text ends on 92v «…وبه القوة»; 93r the figure of the plate",
     "PDF026-027", "126-127", "none", "anonymous, of the same milieu (p. 102); not translated before (p. 105)", "none",
     "AK14", "18 (Amal safihah yukhadh biha al-irtifa)", "ANONYMOUS_MILIEU"),
    ("Text 5", "On the species of astrolabes", "B", "96r",
     "96r «باب معرفة العلة التي سمي بها الاسطرلاب تاما وسمي نصفا وثلثا وسدسا وغير ذلك من الاسماء»",
     "PDF027", "127", "none", "anonymous; Frank (1922: 16) included it and the next two items in his translation of Text 2; "
     "the study doubts that they belong to it (p. 106)", "German, Frank (1922: 16)", "AK14", "-", "ANONYMOUS_MILIEU"),
    ("Text 6", "On projecting the rays with the astrolabe", "B", "96r-96v", "96r red «مطرح الشعاع بالاسطرلاب»",
     "PDF028", "128", "none", "anonymous (p. 106)", "German, Frank (1922: 17)", "AK14", "-", "ANONYMOUS_MILIEU"),
    ("Text 7", "Ptolemy's definition of the five terrestrial zones", "B", "96v", "96v red «قسمة بطلميوس الطرائق الخمس»",
     "PDF028", "128", "none", "anonymous (p. 106)", "German, Frank (1922: 17)", "AK14", "-", "ANONYMOUS_MILIEU"),
    ("Text 8", "On the sine quadrant", "B", "96v-97v",
     "96v red «عمل ربع يستخرج منه الجيب»; 97r red «صفة العمل بهذا الربع اذا عمل»", "PDF028-029", "128-129", "none",
     "anonymous; not translated before (p. 106)", "none", "AK14", "-", "ANONYMOUS_MILIEU"),
    ("Text 9", "On finding the meridian with the astrolabe", "A", "198v-199r", "not seen: no images of A",
     "PDF030", "130", "explicit, according to the study (p. 107)", "differs from the corresponding chapter of Text 2, B "
     "89v-90r (section 29, headed «معرفة السمت» on B 89v:12) (p. 107)", "Russian, Rosenfeld et al. (1983: 216-217), with "
     "the unrelated text that follows on 199r-199v", "AK13", "7 (Marifat al-samt bi-al-asturlab)", "EXPLICIT_ASCRIPTION"),
    ("Text 10", "On the horary quadrant", "A", "196v-197r", "not seen: no images of A", "PDF031-032", "131-132", "none",
     "anonymous; may be al-Khwarizmi's or from his milieu (p. 108)", "Russian, Ahmedov (1991: 193-195)", "AK14",
     "9 (Sinat al-rub al-saat)", "ANONYMOUS_ATTRIBUTION_POSSIBLE"),
    ("Text 11", "On a portable sundial (mukhula)", "A", "192r (figure on 192v)", "not seen: no images of A",
     "PDF033-034", "133-134", "none", "anonymous; probably not al-Khwarizmi's, but of the ninth century (p. 108)",
     "Russian, Ahmedov (1991: 187-189)", "AK14", "14 (Amal al-mukhulah lil-saat)", "ANONYMOUS_PROBABLY_NOT_AUTHORIAL"),
    ("Table B 93v", "the right ascension for every 3 degrees of longitude, in two sexagesimal places", "B", "93v",
     "93v «جدول مطالع الفلك المستقيم لكل ثلث درج…»", "Appendix 2 (outside PDF001-034)", "-", "none",
     "underlying obliquity 23 35; some evidence links it to al-Khwarizmi (King 2004, I: 147, n. 11) (pp. 105-106)",
     "none", "AK14", "-", "ANONYMOUS_LINK_SUGGESTED"),
    ("Table B 94r", "the solar altitude at the times of the day prayers, latitude 33", "B", "94r", "94r the table",
     "PDF025 (with Text 3)", "125", "none", "belongs to Text 3 (p. 106); the manuscript gives the latitude as 13, a "
     "slip (p. 106, n. 22)", "none", "AK14", "16", "ANONYMOUS_MILIEU"),
    ("Table B 94v", "the solar altitude at each temporal hour, for meridian altitudes 25-90", "B", "94v",
     "94v «ارتفاع نصف النهار من كه الى ص وارتفاع الساعات»", "Appendix 2", "-", "none", "anonymous; computed by means of "
     "the function tabulated on 95r-95v (p. 106)", "none", "AK14", "-", "ANONYMOUS_MILIEU"),
    ("Table B 95r-95v", "the 'sine of the hours'", "B", "95r-95v",
     "95r «جدول جيب الساعات لارتفاع نصف النهار من كه الى …»; Indian and abjad numerals side by side, as the study says of "
     "94r-95v (p. 105)", "Appendix 2", "-", "none", "from al-Khwarizmi, as Hogendijk (1991) established (p. 106)", "none",
     "AK13", "-", "ATTRIBUTED_BY_ANALYSIS"),
    ("Margins B 82r-83r", "extracts from an unidentified treatise on the use of the astrolabe", "B", "margins of 82r-83r",
     "a second hand fills the margins of 82r, 82v and 83r, with red «معرفة» headings", "Appendix 1", "-", "none",
     "datable by style to c. 1400-1600 (p. 104)", "none", "-", "-", "LATER_MATERIAL"),
    ("Table B 97v", "solar altitudes for each temporal hour and sign", "B", "97v",
     "97v: a table in a later hand below the end of Text 8; the stamp of the Royal Library of Berlin at the foot",
     "not edited", "-", "none", "not part of the Abbasid corpus; signs misordered, a column missing, latitude 32 9 and "
     "obliquity 23 34 implied (pp. 106-107)", "none", "-", "-", "LATER_MATERIAL"),
    ("Sundial A 231v-235r", "on plane horizontal sundials (Amal al-saat fi basit al-rukhama)", "A", "231v-235r",
     "not seen: no images of A", "not in this study (p. 103, n. 7)", "-", "explicit (study p. 109; PAL record)",
     "King (1999: 349-350) questioned the authorship; the authors see no reason to doubt it (Charette 2003: 181; "
     "Charette and Schmidl 2001: 110-111) (p. 109)", "partial Russian, al-Khwarizmi (1983b: 221-232)", "AK12",
     "15 (Amal al-saat fi basit al-rukhamah)", "EXPLICIT_ASCRIPTION_DISPUTED"),
]
tsv("text_map.tsv", ("item", "study_title", "witness", "folios_in_study", "seen_on_the_leaves_of_B",
                     "study_edition_pdf_pages", "study_printed_pages", "ascription_in_witness", "study_position",
                     "earlier_translations", "packet_work_id", "ismi_row_in_08_map", "classification"), T)

# ---------------------------------------------------------------------------------------------------------------
# the codices: the items of B (study pp. 105-107) and of A that concern the corpus (study pp. 107-109; PAL record)
C = [
    ("B", "1", "1r-77r", "al-Farghani, al-Kamil fi sanat al-asturlab (Ahlwardt 5790); colophon on 77r «تم الكتاب وهو سبعة "
     "انواع بالتمام» (the reading as given by ISMI, witness 176953)", "outside the corpus", "-", "seen: 77r"),
    ("B", "2", "77v-81v", "Text 1", "Khwarizmiana (Ahlwardt 5793)", "8", "seen"),
    ("B", "3", "81v:4-91v:7", "Text 2", "Khwarizmiana", "6", "seen"),
    ("B", "4", "91v:8-92r:16", "Text 3", "Khwarizmiana", "16", "seen"),
    ("B", "5", "92r:17-93r", "Text 4", "Khwarizmiana", "18", "seen"),
    ("B", "6", "93v", "table of the right ascension", "Khwarizmiana, Appendix 2", "-", "seen"),
    ("B", "7", "94r", "table of the altitude at the prayer times (belongs to Text 3)", "Khwarizmiana", "16", "seen"),
    ("B", "8", "94v", "table of the altitude at each temporal hour", "Khwarizmiana, Appendix 2", "-", "seen"),
    ("B", "9", "95r-95v", "table of the 'sine of the hours'", "Khwarizmiana, Appendix 2", "-", "seen"),
    ("B", "10", "96r", "Text 5", "Khwarizmiana", "-", "seen"),
    ("B", "11", "96r-96v", "Text 6", "Khwarizmiana", "-", "seen"),
    ("B", "12", "96v", "Text 7", "Khwarizmiana", "-", "seen"),
    ("B", "13", "96v-97v", "Text 8", "Khwarizmiana", "-", "seen"),
    ("B", "14", "97v", "table in a later hand", "later material, not edited", "-", "seen"),
    ("B", "margins", "82r-83r", "extracts from a later astrolabe treatise", "later material, Appendix 1", "-", "seen"),
    ("A", "group", "182v-200r", "collection of anonymous practical tracts, some incomplete (PAL); the study describes the "
     "group as ff. 183r-199v (p. 107) and itemizes it from 189r", "context of Texts 9-11", "-", "not seen"),
    ("A", "a", "189r-190r", "on a water-clock (binkan)", "anonymous, not edited", "12 (probable, by its title)", "not seen"),
    ("A", "b", "190r-190v", "on a water-clock that shoots pebbles", "anonymous, not edited", "11 (probable, by its title)",
     "not seen"),
    ("A", "c", "191r-192r", "on a horary lifting wheel (dawlab)", "anonymous, not edited", "17", "not seen"),
    ("A", "d", "192r (figure 192v)", "Text 11, the mukhula", "anonymous, edited", "14", "not seen"),
    ("A", "e", "193r", "on a double sundial on the slopes of a roof (maknasa)", "anonymous, not edited", "13", "not seen"),
    ("A", "f", "194v-196v", "a geographical table of 163 localities", "anonymous, not edited", "-", "not seen"),
    ("A", "g", "196v-197r", "Text 10, the horary quadrant", "anonymous, edited", "9", "not seen"),
    ("A", "h", "197r-197v", "on an 'optical compass' for tracing large circles (birkar al-hilla)", "anonymous, not edited",
     "5", "not seen"),
    ("A", "i", "198r (diagram 198v)", "on an instrument for predicting lunar eclipses, ascribed to Umayr ibn Saman",
     "ascribed to another person; not edited", "10 (possible; the titles differ)", "not seen"),
    ("A", "j", "198v-199r", "Text 9, the meridian with the astrolabe", "ascribed to al-Khwarizmi, edited", "7", "not seen"),
    ("A", "k", "199r-199v", "on the latitudes of the seven climates, with a table (Marifat urud al-aqalim)",
     "anonymous, not edited", "28", "not seen"),
    ("A", "l", "200r", "a diagram of circles for the earth, the moon and the sun", "anonymous; probably related to 198r-198v",
     "-", "not seen"),
    ("A", "m", "228v-231r", "Marifat saat al-mashriq fi kull balad ala ma amala Batlamyus min qutr al-falak (PAL: anonymous)",
     "anonymous; not in the study", "20 (by its title)", "not seen"),
    ("A", "n", "231v-235r", "al-Khwarizmi, Amal al-saat fi basit al-rukhama", "ascribed to al-Khwarizmi; authorship "
     "disputed; not in the study", "15", "not seen"),
]
tsv("codex_items.tsv", ("codex", "item", "folios", "content", "role", "ismi_row_in_08_map", "pixels"), C)

# ---------------------------------------------------------------------------------------------------------------
# the edition and the folios: the sections of Text 2 with the folio markers printed in the edition, in its order
S2 = [  # section, pdf page, folio where it begins (from the edition's markers), marker printed inside it
    ("[1]", 15, "81v (line 4)", "81v, 82r"), ("[2a]", 15, "82r", ""), ("[2b]", 15, "82r", "82v"), ("[2c]", 15, "82v", ""),
    ("[2d]", 15, "82v", "83r"), ("[3]", 16, "83r", "83v"), ("[4a]", 16, "83v", ""), ("[4b]", 16, "83v", "84r"),
    ("[5a]", 17, "84r", ""), ("[5b]", 17, "84r", ""), ("[5c]", 17, "84r", ""), ("[6]", 17, "84r", "84v"),
    ("[7]", 17, "84v", ""), ("[8]", 17, "84v", ""), ("[9a]", 17, "84v", ""), ("[9b]", 17, "84v", "85r"),
    ("[10]", 18, "85r", ""), ("[11a]", 18, "85r", ""), ("[11b]", 18, "85r", "85v"), ("[12a]", 18, "85v", ""),
    ("[12b]", 18, "85v", ""), ("[12c]", 18, "85v", ""), ("[13]", 18, "85v", ""), ("[14]", 18, "85v", "86r"),
    ("[15a]", 19, "86r", ""), ("[15b]", 19, "86r", ""), ("[16]", 19, "86r", "86v"), ("[17]", 19, "86v", ""),
    ("[18]", 19, "86v", "87r"), ("[19]", 20, "87r", ""), ("[20]", 20, "87r", ""), ("[21]", 20, "87r", ""),
    ("[22a]", 20, "87v (top)", "87v"), ("[22b]", 20, "87v", ""), ("[23]", 20, "87v", "88r"),
    ("[24]", 21, "88r (foot)", "88v"), ("[25]", 21, "88v", ""), ("[26a]", 21, "88v", ""), ("[26b]", 21, "88v", "89r"),
    ("[26c]", 22, "89v:7-11", "89v:7-11"), ("[27]", 22, "89r (continued)", "89r (cont.)"), ("[28a]", 22, "89r", ""),
    ("[28b]", 22, "89r", ""), ("[28c]", 22, "89v:1-6", "89v:1-6"), ("[28d]", 22, "90r:11-17", "90r:11-17"),
    ("[28e]", 22, "90r:11-17", ""), ("[29]", 23, "89v:12-17", "89v:12-17, 90r:1-10"), ("[30a]", 23, "90v (top)", "90v, 91r"),
    ("[30b]", 23, "91r", ""), ("[30c]", 24, "91r", "91v"), ("[31]", 24, "91v", ""), ("[31b]", 24, "91v (to line 7)", ""),
]
seen = {
    "[24]": "88r foot: red centred «معرفة مطرح الشعاع بالاسطرلاب»",
    "[25]": "88v: red centred «تحويل سني المواليد بالاسطرلاب»",
    "[27]": "89r: red «معرفة المدينة التي انت فيها جنوبية او شمالية»",
    "[28a]": "89r: red «معرفة طلوع الفجر ومغيب الشفق»",
    "[28b]": "89r: red «مغيب الشفق»",
    "[28c]": "89v:1: red «معرفة وقت الظهر والعصر» at the head of the page",
    "[26c]": "89v:7: begins with red «ووجدت» in «ووجدت في نسخة اخرى اذا اردت ان تعلم طالع السنة»; 89v:11 ends «فاعلم ذلك ان شا الله تعالى»",
    "[29]": "89v:12: red «معرفة السمت»",
    "[28d]": "90r:11: red «وقت الظهر» within the line",
    "[30a]": "90v: red «معرفة وقت طلوع القمر» at the head of the page",
    "[30b]": "91r: red «معرفة الطالع بالاسطرلاب من القمر»",
    "[31]": "91v:2: red «اذا اردت ان تعرف انصاف النهار»",
    "[1]": "81v:4: «قال محمد بن موسى الخوارزمي…»",
}
manuscript_order = ["[24]", "[25]", "[26a]", "[26b]", "[27]", "[28a]", "[28b]", "[28c]", "[26c]", "[29]", "[28d]", "[28e]",
                    "[30a]"]
rows = []
for sec, pdf, start, markers in S2:
    note = ""
    if sec in ("[26c]", "[28c]", "[28d]", "[28e]", "[29]", "[27]"):
        note = "reordered: the edition's sequence differs from the manuscript's here; on the leaves the order is " \
               "[27] [28a] [28b] (89r), [28c] (89v:1-6), [26c] (89v:7-11), [29] (89v:12-90r:10), [28d] [28e] (90r:11-17)"
    rows.append(("Text 2", sec, f"PDF{pdf:03d}", str(pdf + 100), start, markers or "-", seen.get(sec, "-"), note or "-"))
T1 = [
    ("Text 1", "opening", "PDF010", "110", "77v", "78r", "77v: basmala and red «صنعة الاسطرلاب»", "-"),
    ("Text 1", "table", "PDF011", "111", "78r (foot: title), 78v (body)", "78r, 78v",
     "78r: red «جدول» and the four lines of the title at the foot of the page; 78v: the table",
     "reordered: the edition prints the title and the table before the paragraph headed «الكواكب», which stands above "
     "the title on 78r and continues on 79r"),
    ("Text 1", "«الكواكب»", "PDF012", "112", "78r (middle)", "78r, 79r, 79v",
     "78r: red «الكواكب» in mid-page; 79r: red «عمل المقنطرات بالهندسة»", "see the row above"),
    ("Text 1", "figures", "PDF013", "113", "79v", "80r, 80v", "80r and 80v: the figures (80r labelled «الدايرة الاولى»)", "-"),
    ("Text 1", "end", "PDF014", "114", "81r", "81r, 81v", "81r: red «عمل الظل في ظهر الاسطرلاب بالهندسة»; 81v:1-3", "-"),
]
O = [
    ("Text 3", "whole", "PDF024-026", "124-126", "91v:8", "91v, 92r, 94r", "91v:8 red «عمل بركار…»; 92r:6 red «صفة العمل بهذا "
     "البيكار»; 94r the table", "reordered: the table of 94r is printed with the text it belongs to (p. 106)"),
    ("Text 4", "whole", "PDF026-027", "126-127", "92r:17", "92r, 92v (the figure of 93r on p. 127)", "92r:17 red «عمل صفيحة…»; 93r the figure", "-"),
    ("Text 5", "whole", "PDF027", "127", "96r", "96r", "96r «باب معرفة العلة…»", "-"),
    ("Text 6", "whole", "PDF028", "128", "96r", "96r, 96v", "96r red «مطرح الشعاع بالاسطرلاب»", "-"),
    ("Text 7", "whole", "PDF028", "128", "96v", "96v", "96v red «قسمة بطلميوس الطرائق الخمس»", "-"),
    ("Text 8", "whole", "PDF028-029", "128-129", "96v", "96v, 97r, 97v", "96v red «عمل ربع…»; 97r red «صفة العمل بهذا الربع اذا "
     "عمل»", "-"),
    ("Text 9", "whole", "PDF030", "130", "A 198v", "198v, 199r", "not seen", "-"),
    ("Text 10", "whole", "PDF031-032", "131-132", "A 196v", "196v, 197r", "not seen", "-"),
    ("Text 11", "whole", "PDF033-034", "133-134", "A 192r", "192r", "not seen", "-"),
]
tsv("edition_folio_concordance.tsv", ("text", "section", "study_pdf_page", "study_printed_page", "folio_where_it_begins",
                                      "folio_markers_printed_in_the_edition", "seen_on_the_leaves", "order_note"),
    T1 + rows + O)

# ---------------------------------------------------------------------------------------------------------------
# the images of B: inventory
rows = []
for n in range(161, 203):
    c = f"{n:04d}"
    f = IMG / f"canvas_{c}.jpg"
    b = f.read_bytes()
    w, h = Image.open(f).size
    fol = f"{77 + (n - 161) // 2}{'r' if n % 2 else 'v'}"
    rows.append((c, fol, f.name, len(b), w, h, hashlib.sha256(b).hexdigest().upper(), SCALER.format(c=c)))
tsv("landberg56_image_inventory.tsv", ("canvas", "folio", "local_file", "bytes", "width", "height", "sha256",
                                       "iiif_image_url"), rows)

# ---------------------------------------------------------------------------------------------------------------
# source acquisition: what the corpus needs, what the packet had, what was found
G = [
    ("G01", "Texts 1-8, the tables of 93v-95v, the margins of 82r-83r, the table of 97v", "B: Berlin, Staatsbibliothek, "
     "Landberg 56", "77v-97v", "HOLD: no target pixels in the packet (2026-08-16)",
     f"ISMI codex 36316 and digitization 284658; IIIF manifest {MANIFEST} (216 canvases); attribution «MPIWG Library / "
     "Staatsbibliothek Berlin»; licence CC BY-SA 4.0 (stated on the ISMI record)",
     "ACQUIRED 2026-10-22: canvases 0161-0202 = ff. 77r-97v, 42 JPEG images at the server's full size (about 1600 x "
     "2300 px); foliation checked on all 21 rectos; kept in _intake/practical/landberg56 (not committed); inventory "
     "landberg56_image_inventory.tsv", "none for the audit; a diplomatic transcription of the Arabic from these images "
     "is not a lane of the session map and needs the user's decision"),
    ("G02", "Texts 9-11 and the other anonymous tracts of A", "A: Istanbul, Suleymaniye, Ayasofya 4830", "182v-200r",
     "HOLD: no target pixels (AKSRC17)", "PAL record (images only for ff. 53r-80v); ISMI codex 354105 (no link to "
     "images); Turkiye Yazma Eserler Kurumu portal, portal.yek.gov.tr: the record of the part 04830-002 (al-Kindi, "
     "record 207243) shows the catalogue data and asks for a member login for more («Daha fazla bilgi icin lutfen uye "
     "girisi yapin»); the records of the parts with ff. 182v-200r were not looked up", "NOT ACQUIRED",
     "the user's own membership of the YEK portal, or an order of reproductions from the Suleymaniye library"),
    ("G03", "the anonymous Marifat saat al-mashriq (ISMI row 20)", "A", "228v-231r", "HOLD", "as G02", "NOT ACQUIRED",
     "as G02"),
    ("G04", "the sundial treatise ascribed to al-Khwarizmi (AK12)", "A", "231v-235r", "HOLD", "as G02", "NOT ACQUIRED",
     "as G02"),
    ("G05", "a modern edition of the sundial treatise", "Charette (2003); partial Russian translation, al-Khwarizmi "
     "(1983b: 221-232)", "-", "not in the packet", "not searched", "NOT ACQUIRED", "not needed for the audit; the study "
     "excludes the treatise (p. 103, n. 7)"),
    ("G06", "the study's commentary, translation and appendices", "packet file 50, PDF035-098", "-", "in the packet",
     "-", "PRESENT", "audited in AK-P02"),
    ("G07", "the older description of A with its 59 'chapters'", "packet file 51, Ahmedov, ad-Dabbagh and Rosenfeld "
     "(1987)", "-", "in the packet", "-", "PRESENT", "audited in AK-P02, with the folios of ISMI rows 19 and 22-26"),
    ("G08", "a possible second witness: ISMI notes at the codex level of Landberg 56 «For another witness of this "
     "treatise, see Berlin, Staatsbibliothek, Ms. Or. quart. 99, ff. 1a-37b»", "Berlin, Ms. Or. quart. 99", "1a-37b",
     "not in the packet", "ISMI codex 36316 (the note does not name the treatise)", "NOT CHECKED",
     "probably al-Farghani's al-Kamil (B 1r-77r); the study states that each text of the corpus survives in only one of "
     "the two manuscripts (p. 103)"),
]
tsv("source_acquisition_gap_ledger.tsv", ("gap", "needed_for", "witness", "folios", "packet_state", "route_checked",
                                          "result", "remaining_action"), G)

# ---------------------------------------------------------------------------------------------------------------
E = [
    ("E01", "The canvases of the MPIWG images map to the folios of B as canvas = 161 + 2 x (folio - 77), the recto first",
     "B 77r-97v; canvases 0161-0201 (odd)", "the pencil foliation 77, 78, ..., 97 in the upper left corner of every recto; "
     "the quire words «حادية عشر» (81r), «ثانية عشر» (89r) and «ثالثة عشر» (97r)",
     "the study: quires of eight, labelled in words on ff. 9r, 17r, 25r, ..., 97r (p. 104); 81 = 9 + 8 x 9", "high",
     "the folio column of landberg56_image_inventory.tsv"),
    ("E02", "The corpus begins on 77v, after the end of al-Farghani's treatise on 77r", "B 77r, 77v",
     "77r ends with a colophon; 77v the basmala and red «صنعة الاسطرلاب»", "the study, item 2 (p. 105)", "high", "-"),
    ("E03", "The edition reorders 78r-78v: it prints the title and the table before the paragraph «الكواكب»",
     "B 78r, 78v; study pp. 110-112", "78r: red «الكواكب» in mid-page, then red «جدول» and the title at the foot; 78v the "
     "table; the edition's markers: (78r) on p. 110, (78r) and 78v on p. 111, (78r) (79r) (79v) on p. 112",
     "the study announces that material is reordered for Text 2 only (p. 109); this is a second case", "high",
     "edition_folio_concordance.tsv, Text 1"),
    ("E04", "Text 2 begins on the fourth line of 81v and names al-Khwarizmi", "B 81v",
     "«قال محمد بن موسى الخوارزمي اول ما يحتاج اليه الناظر في عمل الاسطرلاب»", "the study: 81v:4 (p. 105); its note 17: "
     "the manuscript has «في عمل الاسطرلاب», which it emends; ISMI (witness 390019) quotes the emended incipit «في العمل "
     "بالأصطرلاب»", "high", "the reading of the witness is «في عمل الاسطرلاب»"),
    ("E05", "The margins of 82r-83r carry extracts of a later astrolabe treatise", "B 82r, 82v, 83r",
     "a second hand fills the margins, with red «معرفة» headings", "the study (p. 104, Appendix 1)", "high", "-"),
    ("E06", "From the foot of 88r the chapters of Text 2 have centred red headings", "B 88r-91v",
     "see the column seen_on_the_leaves of edition_folio_concordance.tsv, sections [24]-[31]", "the study (p. 105)",
     "high", "-"),
    ("E07", "The edition reorders 89r-90r of Text 2", "B 89r, 89v, 90r; study pp. 121-123",
     "89v:1-6 «معرفة وقت الظهر والعصر» = [28c]; 89v:7-11 «ووجدت في نسخة اخرى…» = [26c]; 89v:12 «معرفة السمت» = [29]; "
     "90r:11 «وقت الظهر» = [28d]", "the edition's markers (89v:7-11), (89r (cont.)), (89v:1-6), (90r:11-17), "
     "(89v:12-17), (90r:1-10) agree with the leaves; the order on the leaves is [27] [28a] [28b] [28c] [26c] [29] [28d] "
     "[28e]", "high", "edition_folio_concordance.tsv, Text 2"),
    ("E08", "89v:7-11 is an addition from another copy", "B 89v:7",
     "«ووجدت في نسخة اخرى اذا اردت ان تعلم طالع السنة» («and I found in another copy: if you wish to know the ascendant of "
     "the year»), with its numbers in red", "the text of B, or of its exemplar, was "
     "collated with a second copy; the edition places the passage after the chapter on the revolution of the years "
     "([26c])", "high (the reading); medium (who added it)", "a layer of collation in the transmission of Text 2; "
     "for AK-P02 and a later edition"),
    ("E09", "Text 3 begins on 91v:8, Text 4 on 92r:17", "B 91v, 92r",
     "91v:8 red «عمل بركار يعرف به الاوقات للصلوة»; 92r:6 red «صفة العمل بهذا البيكار»; 92r:17 red «عمل صفيحة يؤخذ بها "
     "الارتفاع ويعرف بها طلوع»", "the study (p. 105); it notes that where Text 2 ends is not certain: the leaves show "
     "only where the next heading stands", "high", "-"),
    ("E10", "The tables of 93v-95v and the figure of 93r", "B 93r-95v",
     "93r the figure of the plate; 93v «جدول مطالع الفلك المستقيم لكل ثلث درج…»; 94r a table of the prayer times; 94v "
     "«ارتفاع نصف النهار من كه الى ص وارتفاع الساعات»; 95r-95v «جدول جيب الساعات لارتفاع نصف النهار…», Indian and abjad "
     "numerals together", "the study (pp. 105-106)", "high", "-"),
    ("E11", "Texts 5-8 and the later table", "B 96r-97v",
     "96r «باب معرفة العلة التي سمي بها الاسطرلاب تاما…» and red «مطرح الشعاع بالاسطرلاب»; 96v red «قسمة بطلميوس الطرائق "
     "الخمس» and red «عمل ربع يستخرج منه الجيب»; 97r red «صفة العمل بهذا الربع اذا عمل»; 97v the later table and the "
     "stamp of the Royal Library of Berlin", "the study (p. 106)", "high", "-"),
    ("E12", "No images of A could be consulted", "A 182v-200r, 228v-231r, 231v-235r",
     "PAL images only for ff. 53r-80v; no scans at ISMI; YEK portal behind a member login", "Texts 9-11 and the sundial "
     "treatise cannot be checked against their witness here", "high", "source_acquisition_gap_ledger.tsv, G02-G04"),
    ("E13", "The date of A in the study is the date of one of its parts", "A; PAL record; study p. 107",
     "the study: copied in Damascus in Ramadan 626 H (July-August 1229); PAL: copied from Shaban 626 to Rajab 627 H "
     "(1229-30), the Ptolemaic part in Ramadan 626", "the PAL record is the more precise codicological description",
     "high", "date A as 626-627 H / 1229-30, Damascus, unknown scribe"),
    ("E14", "B is older than the Rasulid note on its title page", "B 2r; study p. 104",
     "a prayer for the dominion of the Rasulid sultan al-Ashraf Ismail (reg. 778-803 H / 1377-1400), written while he "
     "reigned", "terminus ante quem 803 H for the copy; the study proposes c. 700-750 H and rejects Ahlwardt's c. 900 H",
     "medium (f. 2r not seen: outside the acquired range)", "-"),
    ("E15", "The group of A is not one work", "study p. 107",
     "Ahmedov, ad-Dabbagh and Rosenfeld (1987) gave the whole group of ff. 183r-199v and 228v-235r to al-Khwarizmi "
     "and divided it into 59 'chapters'; King (1983a: 2) had left the attribution of each text open",
     "the study rejects the unity; the packet's firewall follows it (08_LOST_DOUBTFUL_ATTRIBUTION_MAP.md)", "high",
     "each item keeps its own attribution row"),
    ("E16", "The item of A 198r is ascribed to someone else", "A 198r; study p. 108",
     "«lawh fi marifat al-kusuf, amal Umayr ibn Saman», with a diagram on 198v", "if ISMI row 10 (Tariq marifah khusuf "
     "al-qamar) is this item, the witness names another person; the titles differ, so the identity is not established",
     "medium", "ISMI row 10 stays a database association"),
]
tsv("evidence_ledger.tsv", ("id", "claim", "source_coordinates", "witnessed_reading", "reasoning", "confidence",
                            "artifact_impact"), E)

U = [
    ("U01", "A 182v-200r: Texts 9-11 and the anonymous tracts unseen", "no public images; YEK needs a member login",
     "G02"),
    ("U02", "A 228v-231r unseen", "as U01", "G03"),
    ("U03", "A 231v-235r, the sundial treatise, unseen", "as U01", "G04"),
    ("U04", "Berlin, Ms. Or. quart. 99, ff. 1a-37b: which treatise ISMI's note means", "the note stands at the codex "
     "level and names no treatise", "G08"),
    ("U05", "where Text 2 ends", "the study leaves it open (p. 105); the leaves show the next heading on 91v:8 only",
     "AK-P02 (the commentary)"),
    ("U06", "whether Texts 5-7 belong to Text 2", "Frank (1922) printed them with it; the study doubts it (p. 106)",
     "AK-P02 (the commentary)"),
    ("U07", "the folios in A of ISMI rows 19 and 22-26", "the study's introduction itemizes A only from 189r",
     "AK-P02 (packet file 51)"),
]
tsv("unresolved.tsv", ("id", "question", "state", "routed_to"), U)

# ---------------------------------------------------------------------------------------------------------------
files = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name not in ("SHA256SUMS", "checkpoint.json"))
canon = hashlib.sha256()
for name in files:
    canon.update(name.encode() + b"\0" + (OUT / name).read_bytes())
ck = {
    "session": "AK-P01",
    "mode": "evidence and attribution audit only; no source-text production",
    "owned_range": "PDF001-PDF034 of 50_PRACTICAL_ASTRONOMY_CHARETTE_SCHMIDL.pdf (printed pp. 101-134) and the PAL "
                   "record of Ayasofya 4830",
    "study_sha256": PACKET_STUDY_SHA,
    "pal_record_sha256": PAL_SHA,
    "canonical_source_checkpoint_sha256": canon.hexdigest(),
    "canonical_source_checkpoint_note": "SHA-256 over the return files in name order (file name, a NUL byte, the bytes), "
                                        "without checkpoint.json and SHA256SUMS",
    "last_fully_transcribed_source_unit": "NONE",
    "last_fully_verified_source_unit": "PDF034",
    "first_untouched_source_unit": "NONE",
    "owned_units_total": 35,
    "owned_units_disposed": 35,
    "unresolved_count": len(U),
    "figure_count": 0,
    "formula_or_table_count": 0,
    "berlin_images_acquired": "canvases 0161-0202 = ff. 77r-97v (42 files)",
    "date": "2026-10-22",
}
(OUT / "checkpoint.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
names = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS")
(OUT / "SHA256SUMS").write_text("".join(f"{hashlib.sha256((OUT / n).read_bytes()).hexdigest()}  {n}\n" for n in names),
                                encoding="utf-8", newline="\n")
print("written:", ", ".join(names + ["SHA256SUMS"]))
