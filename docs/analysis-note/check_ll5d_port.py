#!/usr/bin/env python3
"""Check that the LL5D keys ported into the note's make_values_fived16.py (LL5D_PORTED) equal the paper branch's.

usage: check_ll5d_port.py [--self-test]   (run anywhere inside the repository)

The paper branch's values_fived16.tex is read with git at PAPER_REV, the draft/methods-short-20261109 commit the port was
taken from; every ported key must be present there and print the same value as the note's values_fived16.tex. The
note's values are regenerated in memory from its pinned readouts (make_values_fived16.all_values), so a stale
values_fived16.tex cannot pass either. --self-test plants a wrong value and a missing key and requires each to fail.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_values_fived16 as mv  # noqa: E402

PAPER_REV = "037431430"
VALUES = "docs/analysis-note/values_fived16.tex"
KEY = re.compile(r"\\@namedef\{fv@([^}]+)\}\{(.*)\}\s*$")


def parse(text):
    out = {}
    for line in text.splitlines():
        m = KEY.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def paper_values():
    t = subprocess.run(["git", "show", f"{PAPER_REV}:{VALUES}"], cwd=HERE, capture_output=True, text=True, check=True)
    return parse(t.stdout)


def compare(note, paper, keys):
    fails = []
    for k in keys:
        if k not in paper:
            fails.append(f"{k}: not in the paper branch's values at {PAPER_REV}")
        elif k not in note:
            fails.append(f"{k}: not in the note's values")
        elif note[k] != paper[k]:
            fails.append(f"{k}: note {note[k]!r}, paper {paper[k]!r}")
    return fails


def main(argv):
    paper = paper_values()
    note_file = parse((HERE / "values_fived16.tex").read_text())
    fresh = {k: v for k, v in mv.ll5d_port_values(mv.load()).items()}
    fails = compare(fresh, paper, mv.LL5D_PORTED) + compare(note_file, paper, mv.LL5D_PORTED)
    if argv[:1] == ["--self-test"]:
        bad = dict(fresh, **{mv.LL5D_PORTED[0]: "WRONG"})
        f1 = bool(compare(bad, paper, mv.LL5D_PORTED))
        f2 = bool(compare(fresh, {k: v for k, v in paper.items() if k != mv.LL5D_PORTED[-1]}, mv.LL5D_PORTED))
        ok = not fails and f1 and f2
        print(f"LL5D-PORT SELF-TEST :: {'PASS' if ok else 'FAIL'} (real port silent: {not fails}; wrong value fires: {f1}; "
              f"missing key fires: {f2})")
        return 0 if ok else 1
    for x in fails:
        print("  FAIL", x)
    print(f"LL5D-PORT :: {'PASS' if not fails else 'FAIL'} ({len(mv.LL5D_PORTED)} keys against the paper branch at "
          f"{PAPER_REV}, fresh and as written)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
