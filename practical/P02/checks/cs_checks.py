"""Recompute claims of Charette and Schmidl (2004) that are pure arithmetic or spherical astronomy."""
from math import radians, degrees, tan, sin, asin, atan, cos, floor

def sexa(x, places=2):
    s = "-" if x < 0 else ""; x = abs(x); i = int(x); r = x - i; out = [str(i)]
    for _ in range(places):
        r *= 60; d = int(r + 1e-9); out.append(f"{d:02d}"); r -= d
    return s + out[0] + ";" + ",".join(out[1:])
def unsexa(s):
    a, b = s.split(";"); v = float(a)
    for k, p in enumerate(b.split(","), 1): v += float(p) / 60 ** k
    return v

# 1. R for an astrolabe plate of radius 150 whose rim is Capricorn, obliquity 23;35 (study p. 164)
eps = 23 + 35 / 60
R = 150 / tan(radians((90 + eps) / 2))
print("1. R = 150/tan((90+23;35)/2) =", round(R, 4), "=", sexa(R), "(study: 98;11)")
# obliquity implied by R = 98;11 exactly
R0 = unsexa("98;11")
e0 = 2 * degrees(atan(150 / R0)) - 90
print("   R = 98;11 implies obliquity", sexa(e0), "; with 23;51 R would be", sexa(150 / tan(radians((90 + 23 + 51 / 60) / 2))))

# 2. Table 3 (f. 78v, north column): fN(theta) = R tan((90 - theta)/2); the study's errors in minutes for a sample
ms = {1: "96;31", 2: "94;11", 10: "82;23", 17: "72;29", 23: "65;49", 29: "57;11", 45: "40;41", 60: "26;59", 89: "0;52"}
for th, v in ms.items():
    rec = R0 * tan(radians((90 - th) / 2))
    print(f"   theta {th:2d}: ms {v:>6}  rec {sexa(rec, 1):>6}  err {round((unsexa(v) - rec) * 60):+d}'")

# 3. the excess of revolution of a year of 365 days and a fraction, in equatorial degrees (study pp. 171-172)
for y in ("365;15,30,22,30", "365;15,32,30"):
    exc = (unsexa(y) - 365) * 360
    print("3. year", y, "-> excess", sexa(exc, 2))

# 4. Text 8 example (study p. 181): hm = 60, h = 30
wrong = degrees(asin(sin(radians(30)) * sin(radians(60)))) / 15
right = degrees(asin(sin(radians(30)) / sin(radians(60)))) / 15
print(f"4. procedure of the text: {wrong:.3f} h (study: about 1 2/3); correct formula: {right:.3f} h (study: 2 1/3)")

# 5. Text 7: the five zones (study p. 178)
z = [36 + 9 / 60, 30, 2 * (23 + 51 / 60), 30, 36 + 9 / 60]
print("5. zones sum to", sexa(sum(z), 1), "degrees")

# 6. Text 3 table (study pp. 174-175): midday shadow = 12 cot <90 - phi + delta>, phi = 33, then the integer part
def decl(lam, e=23 + 51 / 60):
    return degrees(asin(sin(radians(e)) * sin(radians(lam))))
rows = {90: 2, 60: 2, 30: 4, 0: 7, -30: 12, -60: 16, -90: 18}
for lam, rec in rows.items():
    a = floor(90 - 33 + decl(lam))
    sh = 12 / tan(radians(a))
    print(f"6. lambda' {lam:+3d}: <90-33+delta> = {a}, 12 cot = {sh:.3f}, integer part {floor(sh)} (study rec. {rec})")
