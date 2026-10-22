"""The markup of the page files, removed: {ov:..} (a figure label), {inv:..} (a turned letter) and {b:..} (bold)
keep their letters, {n:..} (a note mark) becomes a space. The markup may nest ({ov:ه{inv:ن}})."""
import re


def plain(text):
    while True:
        new = re.sub(r"\{(?:ov|inv|b):([^{}]*)\}", r"\1", text)
        new = re.sub(r"\{n:[^{}]*\}", " ", new)
        if new == text:
            return new
        text = new
