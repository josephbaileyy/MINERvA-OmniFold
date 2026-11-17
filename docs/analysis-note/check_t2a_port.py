#!/usr/bin/env python3
"""Check that the Tier 2 (a) keys ported into the note's make_values_landed.py (T2A_PORTED) equal the paper branch's.

usage: check_t2a_port.py [--self-test]   (run anywhere inside the repository)

The paper keys them in values_fived16.tex (\\fvval); the note in values_landed.tex (\\lrval). The paper's file is read
with git at PAPER_REV (draft/methods-short-20261109), and the note's is regenerated in memory from its pinned readouts
(make_values_landed.build) as well as read as written. --self-test plants a wrong value and a missing key.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_values_landed as ml  # noqa: E402

PAPER_REV = "037431430"
T2A_PORTED = ("t2a-r1", "t2a-r2")


def parse(text, prefix):
    out = {}
    for line in text.splitlines():
        m = re.match(r"\\@namedef\{%s@([^}]+)\}\{(.*)\}\s*$" % prefix, line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def compare(note, paper):
    fails = []
    for k in T2A_PORTED:
        if k not in paper:
            fails.append(f"{k}: not in the paper branch's values at {PAPER_REV}")
        elif k not in note:
            fails.append(f"{k}: not in the note's values")
        elif note[k] != paper[k]:
            fails.append(f"{k}: note {note[k]!r}, paper {paper[k]!r}")
    return fails


def main(argv):
    t = subprocess.run(["git", "show", f"{PAPER_REV}:docs/analysis-note/values_fived16.tex"], cwd=HERE,
                       capture_output=True, text=True, check=True).stdout
    paper = parse(t, "fv")
    fresh = ml.build(ml.load())
    written = parse((HERE / "values_landed.tex").read_text(), "lr")
    fails = compare(fresh, paper) + compare(written, paper)
    if argv[:1] == ["--self-test"]:
        f1 = bool(compare(dict(fresh, **{T2A_PORTED[0]: "WRONG"}), paper))
        f2 = bool(compare(fresh, {k: v for k, v in paper.items() if k != T2A_PORTED[-1]}))
        ok = not fails and f1 and f2
        print(f"T2A-PORT SELF-TEST :: {'PASS' if ok else 'FAIL'} (real port silent: {not fails}; wrong value fires: {f1}; "
              f"missing key fires: {f2})")
        return 0 if ok else 1
    for x in fails:
        print("  FAIL", x)
    print(f"T2A-PORT :: {'PASS' if not fails else 'FAIL'} ({len(T2A_PORTED)} keys against the paper branch at {PAPER_REV})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
