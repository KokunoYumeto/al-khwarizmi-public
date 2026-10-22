"""The four gates of the standard Jewish calendar, computed from its rules, for checking the limits that
al-Khwarizmi's treatise gives for the first day of Tishri and the length of the year.

Rules (Maimonides, Sanctification of the New Moon, chapters 6-8; the later standard calendar):
  hour = 1080 parts, day = 24 hours, counted from nightfall; weekdays 1 = Sunday ... 7 = Saturday;
  lunar month = 29 days 12 hours 793 parts; common year 12 months, leap year 13;
  the first of Tishri is the day of the molad of Tishri, postponed
    (1) to the next day if the molad is at or after 18 hours (molad zaken),
    (2) in a common year, from Tuesday to Thursday if the molad of a Tuesday is at or after 9h 204p (GaTaRaD),
    (3) after a leap year, from Monday to Tuesday if the molad of a Monday is at or after 15h 589p (BeTUTaKPaT),
    (4) by one more day if the day so found is Sunday, Wednesday or Friday (lo ADU).
The length of a year is the difference of the first days of Tishri of the year and of the next.

For each case (this year common or leap, the year before leap or not, the next year leap or not) the script runs
the molad of Tishri through a whole week, part by part, and prints the ranges of the molad that give the same first
day and the same length: the four gates. Output: gates.out.txt beside this file.
python gates.py"""
from pathlib import Path

PART, HOUR, DAY = 1, 1080, 25920
WEEK = 7 * DAY
MONTH = 29 * DAY + 12 * HOUR + 793
NAMES = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}


def fmt(p):
    d, r = divmod(p, DAY)
    h, q = divmod(r, HOUR)
    return f"{NAMES[d % 7 + 1]} {h}h {q}p"


def rosh(molad, this_leap, prev_leap):
    """the absolute day (0 = the Sunday of the week of the molad) of the first of Tishri"""
    d, t = divmod(molad, DAY)
    wd = d % 7 + 1
    if t >= 18 * HOUR:
        d += 1
    elif not this_leap and wd == 3 and t >= 9 * HOUR + 204:
        d += 2
    elif prev_leap and wd == 2 and t >= 15 * HOUR + 589:
        d += 1
    if d % 7 + 1 in (1, 4, 6):
        d += 1
    return d


def gates(this_leap, prev_leap, next_leap):
    length = (13 if this_leap else 12) * MONTH
    out, last, start = [], None, 0
    for m in range(0, WEEK + 1):
        mm = m % WEEK
        r0 = rosh(mm, this_leap, prev_leap)
        r1 = rosh(mm + length, next_leap, this_leap)
        key = (NAMES[r0 % 7 + 1], r1 - r0)
        if m == WEEK or key != last:
            if last is not None:
                out.append((start, m, last))
            start, last = m, key
    return out


def main():
    lines = []
    cases = [(False, False, False), (False, False, True), (False, True, False), (True, False, False)]
    for this_leap, prev_leap, next_leap in cases:
        lines.append(f"this year {'leap' if this_leap else 'common'}, the year before {'leap' if prev_leap else 'common'}, "
                     f"the next year {'leap' if next_leap else 'common'}:")
        for a, b, (wd, n) in gates(this_leap, prev_leap, next_leap):
            kind = {353: "deficient", 354: "regular", 355: "complete", 383: "deficient", 384: "regular",
                    385: "complete"}[n]
            lines.append(f"  molad from {fmt(a):24s} to {fmt(b % WEEK) if b < WEEK else 'Sunday 0h 0p':24s} -> first of "
                         f"Tishri {wd:9s} {n} days ({kind})")
        lines.append("")
    text = "\n".join(lines)
    (Path(__file__).with_name("gates.out.txt")).write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
