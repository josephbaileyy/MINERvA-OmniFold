#!/usr/bin/env python3
"""The GENCMP addendum E2 paper round's values check (DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md), re-runnable from git.

It compares values_fived16.tex at the round's base (63493acdc) with the working tree's, and requires:
  1. no base key is removed and no base value changes (the covariance, Table IV and every other printed value stay);
  2. the added keys are exactly the e2- family (from the pinned e2.json and x_e2_sens.out.txt) and the one-decimal
     carbon chi2 of NuWro and GiBUU (g-*-carbon-*-chi2r1, both arms);
  3. each added e2- chi2 equals its readout field, rounded as printed.
It prints every added key that a note or paper source prints, with its file:line.

usage: check_values.py [--write OUT.txt]      (run inside the repository)
MEASURES: nothing. CANNOT AUTHORIZE: a value, a sentence or a claim."""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

BASE = "63493acdc"
VALUES = "docs/analysis-note/values_fived16.tex"
E2 = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/rerun1"
ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=True).stdout.strip())
PRED = {"gcv": "genie_cv", "gmec": "genie_mec", "nuwro": "nuwro", "gibuu": "gibuu"}
TAG = {"x0": "removed", "x1": "carbon", "x2": "doubled", "ch": "CH"}


def kv(text):
    return dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", text, re.M))


def main(argv):
    base = kv(subprocess.run(["git", "show", f"{BASE}:{VALUES}"], capture_output=True, text=True, check=True,
                             cwd=ROOT).stdout)
    cur = kv((ROOT / VALUES).read_text())
    e2 = json.loads((ROOT / E2 / "chi2/e2.json").read_text())
    s = (ROOT / E2 / "sens/x_e2_sens.out.txt").read_text()
    sens = json.loads(s[s.index("\n{") + 1:])
    out, ok = [], True
    gone = sorted(set(base) - set(cur))
    moved = sorted(k for k in base if k in cur and base[k] != cur[k])
    added = sorted(set(cur) - set(base))
    if gone or moved:
        ok = False
        out.append(f"FAIL base keys removed {gone[:8]} or changed {moved[:8]}")
    else:
        out.append(f"ok   all {len(base)} base keys print the base value")
    r1 = re.compile(r"^g-(nuwro|gibuu)-carbon-(total|shape_only)-chi2r1(-nopl)?$")
    stray = [k for k in added if not (k.startswith("e2-") or r1.match(k))]
    n_e2, n_r1 = sum(k.startswith("e2-") for k in added), sum(bool(r1.match(k)) for k in added)
    if stray or n_r1 != 8:
        ok = False
        out.append(f"FAIL added keys outside e2- and the eight chi2r1 keys: {stray[:8]} (chi2r1 {n_r1})")
    else:
        out.append(f"ok   {len(added)} added keys: {n_e2} e2- and {n_r1} g-*-carbon-*-chi2r1")
    bad, n = [], 0
    for k in added:
        m = re.fullmatch(r"e2-(with|nopl)-(gcv|gmec|nuwro|gibuu)-(total|shape_only)-(x0|x1|x2|ch)", k)
        if m:
            a, p, part, t = m.groups()
            n += 1
            want = f"{sens['chi2'][a][PRED[p]][part][TAG[t]]:.2f}"
            if t in ("x1", "ch"):
                assert f"{e2['chi2'][a][PRED[p]][part][TAG[t]]:.2f}" == want
            if cur[k] != want:
                bad.append(k)
    out.append(f"{'ok  ' if not bad else 'FAIL'} {n} e2- chi2 keys equal their readout fields as printed" +
               (f": {bad[:8]}" if bad else ""))
    ok &= not bad
    uses = defaultdict(list)
    for f in sorted((ROOT / "docs/analysis-note").glob("*.tex")):
        if f.name.startswith("values_"):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if not line.lstrip().startswith("%"):
                for k in re.findall(r"\\fvval\{([^}]*)\}", line):
                    uses[k].append(f"{f.name}:{i}")
    printed = [k for k in added if uses[k]]
    out.append(f"     {len(printed)} of the added keys print, at: {sorted({u.split(':')[0] for k in printed for u in uses[k]})}")
    out.append("")
    out.append("key\tvalue\tprinted at")
    out += [f"{k}\t{cur[k]}\t{' '.join(uses[k])}" for k in printed]
    out.append("")
    out.append("VALUES-CHECK :: " + ("PASS" if ok else "FAIL"))
    text = "\n".join(out) + "\n"
    if argv[:1] == ["--write"]:
        Path(argv[1]).write_text(text)
    print(text if not ok else "\n".join(out[:4] + out[-1:]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
