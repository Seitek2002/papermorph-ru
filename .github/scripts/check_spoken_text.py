#!/usr/bin/env python3
"""lint.py's spoken-text warning: what a voice would have to guess in a narration line, without a voice.

    python3 .github/scripts/check_spoken_text.py

In a language whose numbers decline (Russian), digits and signs left in the narration are read in one form whatever
the sentence needs; lint.py names them. The lines here are what the pilot Russian chapter ran into.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("lint", ROOT / ".claude/skills/papermorph/scripts/lint.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)

failures = []


def check(name, got, want):
    if got != want:
        failures.append(f"{name}:\n  got  {got!r}\n  want {want!r}")


check("Russian is checked", "ru" in lint.SPOKEN_LANGS, True)
check("English is not", "en" in lint.SPOKEN_LANGS, False)
check("digits and a degree sign, as one run", lint.unspoken("Угол [[a]]равен 30°."), ["30°"])
check("a formula left as symbols", lint.unspoken("tg α = sin α / cos α"), ["tg", "α", "=", "sin", "/", "cos"])
check("a decimal comma", lint.unspoken("Отношение равно 0,6."), ["0", "6"])
check("written in words: nothing to guess", lint.unspoken("Синус тридцати градусов равен одной второй."), [])
check("{{shown|spoken}} counts as its spoken form",
      lint.unspoken("[[sin]]{{sin|синус}} угла {{α|альфа}} равен {{1/2|одной второй}}."), [])
check("a spoken form with a digit is still named", lint.unspoken("{{C|си 3}}"), ["3"])
check("a hyphen inside a word is spelling", lint.unspoken("Смотрит по-разному."), [])
check("a minus between spaces is a sign", lint.unspoken("икс - игрек"), ["-"])
check("marks and audio tags are not spoken", lint.unspoken("[[w1]]Итак. [whispers] тише"), [])

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("spoken text check: ok")
