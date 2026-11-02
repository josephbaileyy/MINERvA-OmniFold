#!/usr/bin/env python3
"""The GENCMP amendment E paper round's values check (director's ruling A of 2026-11-01), re-runnable from git.

It compares values_fived16.tex at the round's base (a4cd6ffcf) with the working tree's, and requires:
  1. the same key set;
  2. the changed keys, with their before and after strings, equal rerun1/values_diff.tsv without its gs- rows, key by key;
  3. every gs- key (Stage G as first made, pin g0) equals what #656 printed (its merge, 750466a70).
It prints every changed key that a note or paper source prints, with its file:line.

usage: check_values.py [--write OUT.txt]      (run inside the repository)
MEASURES: nothing. CANNOT AUTHORIZE: a value, a sentence or a claim."""
import collections
import re
import subprocess
import sys
from pathlib import Path

BASE, PR656 = "a4cd6ffcf", "750466a70"
VALUES = "docs/analysis-note/values_fived16.tex"
EXPECTED = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/rerun1/values_diff.tsv"
ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=True).stdout.strip())


def kv(text):
    return dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", text, re.M))


def show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True, cwd=ROOT).stdout


def main(argv):
    base, cur, c656 = kv(show(BASE, VALUES)), kv((ROOT / VALUES).read_text()), kv(show(PR656, VALUES))
    exp = {}
    for line in (ROOT / EXPECTED).read_text().splitlines()[1:]:
        k, before, after = line.split("\t")
        exp[k] = (before, after)
    out, ok = [], True
    if set(base) != set(cur):
        ok = False
        out.append(f"FAIL key sets differ: {sorted(set(base) ^ set(cur))[:8]}")
    diff = {k: (base[k], cur[k]) for k in base if k in cur and base[k] != cur[k]}
    gs = {k for k in exp if k.startswith("gs-")}
    want = {k: x for k, x in exp.items() if k not in gs}
    fam = collections.Counter(k.split("-")[0] for k in diff)
    if diff == want:
        out.append(f"ok   {len(diff)} changed keys equal values_diff.tsv without its {len(gs)} gs- rows, key by key "
                   f"({', '.join(f'{f} {n}' for f, n in sorted(fam.items()))})")
    else:
        ok = False
        out.append(f"FAIL the changed keys differ from values_diff.tsv without gs-: "
                   f"{sorted(set(diff) ^ set(want))[:8]} or values {[k for k in diff if k in want and diff[k] != want[k]][:8]}")
    gsk = sorted(k for k in cur if k.startswith("gs-"))
    bad = [k for k in gsk if cur[k] != c656.get(k)]
    out.append(f"{'ok  ' if not bad else 'FAIL'} {len(gsk)} gs- keys equal #656's printed values" + (f": {bad[:8]}" if bad else ""))
    ok &= not bad
    uses = collections.defaultdict(list)
    for f in sorted((ROOT / "docs/analysis-note").glob("*.tex")):
        if f.name.startswith("values_"):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if not line.lstrip().startswith("%"):
                for k in re.findall(r"\\fvval\{([^}]*)\}", line):
                    uses[k].append(f"{f.name}:{i}")
    printed = [k for k in sorted(diff) if uses[k]]
    out.append(f"     {len(printed)} of the changed keys print, all at: {sorted({u.split(':')[0] for k in printed for u in uses[k]})}")
    out.append("")
    out.append("key\tbefore\tafter\tprinted at")
    out += [f"{k}\t{diff[k][0]}\t{diff[k][1]}\t{' '.join(uses[k])}" for k in printed]
    out.append("")
    out.append("gs- key\tvalue (g0)\t#656")
    out += [f"{k}\t{cur[k]}\t{c656[k]}" for k in gsk]
    out.append("")
    out.append("VALUES-CHECK :: " + ("PASS" if ok else "FAIL"))
    text = "\n".join(out) + "\n"
    if argv[:1] == ["--write"]:
        Path(argv[1]).write_text(text)
    print(text if not ok else "\n".join(out[:3] + out[-1:]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
