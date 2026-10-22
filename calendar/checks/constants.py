"""Exact checks of the figures of al-Khwarizmi's treatise on the Jewish calendar that the critical notes of
calendar/pages rest on: the month and the years in days, hours and parts, the nineteen-year cycle and the solar year,
two limits of the four gates derived from the text's own figures, the interval from Adam to the Seleucid era, and the
base of days with the revolutions of the sun and the moon. Integer and fraction arithmetic only.

Output: constants.out.txt beside this file.
python constants.py"""
from fractions import Fraction
from pathlib import Path

HOUR, DAY = 1080, 25920
WEEK = 7 * DAY
MONTH = 29 * DAY + 12 * HOUR + 793
NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def dhp(parts):
    d, r = divmod(parts, DAY)
    h, p = divmod(r, HOUR)
    return f"{d}d {h}h {p}p"


def weekday(parts):
    parts %= WEEK
    d, r = divmod(parts, DAY)
    h, p = divmod(r, HOUR)
    return f"{NAMES[d]} {h}h {p}p"


def at(day, h, p=0):
    return NAMES.index(day) * DAY + h * HOUR + p


def main():
    out = []
    say = out.append
    say(f"month: {dhp(MONTH)} = {MONTH} parts (AK15-CN026: 765,433)")
    say(f"12 months: {dhp(12 * MONTH)}; 13 months: {dhp(13 * MONTH)} (AK15-CN010)")
    cycle = 235 * MONTH
    say(f"cycle of 235 months: {dhp(cycle)} (AK15-CN011)")
    year = Fraction(cycle, 19)
    days, rest = divmod(year, DAY)
    hours, parts = divmod(rest, HOUR)
    say(f"solar year = cycle / 19: {days}d {hours}h {parts} parts; parts / 1080 = {Fraction(parts, HOUR)} hour"
        f" (p. 7: 3791/4104)")
    leap_rest = 13 * MONTH % WEEK
    say(f"13 months less whole weeks: {dhp(leap_rest)}")
    say(f"gate for a leap year beginning on Thursday: Tuesday 9h 204p less {dhp(leap_rest)} = "
        f"{weekday(at('Tuesday', 9, 204) - leap_rest)} (AK15-CN015)")
    say(f"BeTUTaKPaT: Monday 15h 589p less {dhp(leap_rest)} = {weekday(at('Monday', 15, 589) - leap_rest)}"
        f" (AK15-CN021)")
    say(f"Adam to the Seleucid era: 3448 mod 19 = {3448 % 19}; 3448 + 1135 = {3448 + 1135}; "
        f"printed 4082 - 1135 = {4082 - 1135}, mod 19 = {(4082 - 1135) % 19} (AK15-CN022)")
    whole = 1
    while (whole * cycle) % DAY:
        whole += 1
    base_days = whole * cycle // DAY
    say(f"least number of cycles with whole days: {whole}; days {base_days} (printed 35,975,351)")
    years, months = whole * 19, whole * 235
    say(f"years {years} (printed 98,496); months {months}; days / years = {Fraction(base_days, years)}"
        f" = {base_days / years:.6f}")
    moon = months + years
    say(f"revolutions of the moon = months + years = {moon} (printed 1,016,736; AK15-CN025); "
        f"days / revolutions = {base_days / moon:.6f}; days / months = {base_days / months:.6f}")
    text = "\n".join(out)
    Path(__file__).with_name("constants.out.txt").write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
