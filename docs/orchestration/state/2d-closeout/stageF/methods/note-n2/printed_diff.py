#!/usr/bin/env python3
"""The standing guard for any scripted edit of the note's TeX sources (director, n2, 2026-10-26).

usage: printed_diff.py <before.tex> <after.tex> [--expect N]
       printed_diff.py --dirs <before-dir> <after-dir> <file> [<file> ...] [--expect-total N]

Prints every printed sentence (comments removed, whitespace collapsed) that differs between the two versions, so the
author can confirm that ONLY the intended sentences changed. With --expect N (or --expect-total N over several files),
it exits 1 unless exactly N sentence lines changed (an edited sentence counts twice: one removed, one added). The
hazard it exists for: a replacement that ends in a `%` comment line, on a source line whose text continued, comments
out the rest of that line. That happened twice in two rounds (n1 apply_acc.py; n2's sec_joint and App. C edits), and
is invisible in the source diff but shows here as an unintended changed sentence.
"""
import difflib
import re
import sys
from pathlib import Path


def sentences(text: str) -> list[str]:
    printed = re.sub(r"\s+", " ", re.sub(r"(?<!\\)%[^\n]*", "", text))
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\$(])", printed) if s.strip()]


def changed(before: str, after: str) -> list[str]:
    return [d for d in difflib.ndiff(sentences(before), sentences(after)) if d[:1] in "+-"]


def main(argv: list[str]) -> int:
    expect = None
    for flag in ("--expect", "--expect-total"):
        if flag in argv:
            i = argv.index(flag)
            expect = int(argv[i + 1])
            del argv[i:i + 2]
    if argv[:1] == ["--dirs"]:
        a, b, files = Path(argv[1]), Path(argv[2]), argv[3:]
        pairs = [(f, (a / f).read_text(), (b / f).read_text()) for f in files]
    else:
        pairs = [(argv[1], Path(argv[0]).read_text(), Path(argv[1]).read_text())]
    total = 0
    for name, x, y in pairs:
        d = changed(x, y)
        total += len(d)
        print(f"== {name}: {len(d)} changed sentence line(s)")
        for line in d:
            print("   " + line[:200])
    ok = expect is None or total == expect
    print(f"PRINTED-DIFF :: {'OK' if ok else 'FAIL'} ({total} changed sentence line(s)"
          f"{'' if expect is None else f', expected {expect}'})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
