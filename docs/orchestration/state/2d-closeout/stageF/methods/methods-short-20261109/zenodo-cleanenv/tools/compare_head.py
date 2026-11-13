"""Compare every check #981's build makes (checks.tsv from log_checks.py) with a #977 checkout (D6 clean-env test).

usage: python3 -I compare_head.py <#977 checkout's docs/analysis-note> <checks.tsv>
For a key: is it still in values_fived16.tex, with the same value? For a macro: the same in values.tex? For a printed
phrase: does it occur exactly once in paper_body.tex or supplemental_body.tex (comments stripped, whitespace
collapsed)? Prints a summary line, then one line per check that does not hold. Reads only.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_fv import load  # noqa: E402


def norm(s):
    return " ".join(re.sub(r"(?m)(?<!\\)%.*$", "", s).split())


def main():
    d, checks = sys.argv[1], sys.argv[2]
    _, val = load(d + "/values_fived16.tex")
    vt = {}
    for line in open(d + "/values.tex"):
        m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}", line)
        if m:
            vt[m[1]] = m[2]
    paper = norm(open(d + "/paper_body.tex").read())
    supp = norm(open(d + "/supplemental_body.tex").read())
    miss = diff = same = 0
    rows = []
    for line in open(checks):
        kind, f, n, g = line.rstrip("\n").split("\t")
        if kind == "key":
            if n not in val:
                miss += 1
                rows.append(("KEY-GONE", f, n, g, ""))
            elif val[n] != g:
                diff += 1
                rows.append(("KEY-DIFF", f, n, g, val[n]))
            else:
                same += 1
        elif kind == "macro":
            if vt.get(n) != g:
                rows.append(("MACRO-DIFF", f, n, g, str(vt.get(n))))
            else:
                same += 1
        else:
            doc = paper if kind.endswith("paper") else supp
            c = doc.count(" ".join(n.split()))
            if c != 1:
                rows.append(("PHRASE-COUNT-%d" % c, f, n[:110], "", ""))
            else:
                same += 1
    print("equal at head:", same, "| key gone:", miss, "| key value differs:", diff, "| other:", len(rows) - miss - diff)
    for r in rows:
        print(" | ".join(r))


if __name__ == "__main__":
    main()
