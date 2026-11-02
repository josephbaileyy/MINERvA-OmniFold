#!/usr/bin/env python3
"""The quadrant-sentence and Section IV paper round's values check (DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md), re-runnable from git.

It compares values_fived16.tex at the round's base (7bac3c634) with the working tree's, and requires:
  1. no base key is removed and no base value changes (the covariance, Table IV and every other printed value stay);
  2. the added keys are exactly the cr- family (step C-R, from overlap_refined.json) and the x- family (GENCMP X, from
     k.json);
  3. each added key that carries a readout number equals that field, recomputed here and rounded as printed.
It prints every added key that a note or paper source prints, with its file:line.

usage: check_values.py [--write OUT.txt]      (run inside the repository)
MEASURES: nothing. CANNOT AUTHORIZE: a value, a sentence or a claim."""
import json
import math
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

BASE = "7bac3c634"
VALUES = "docs/analysis-note/values_fived16.tex"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=True).stdout.strip())
Q = ["QA", "QB", "QC", "QD"]
READING = {"prim": "primary", "qr": "Q_R_alone", "nopair": "C_PL_pair_zero"}


def kv(text):
    return dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", text, re.M))


def expected(cr, k):
    """Every added key whose value is a readout number, recomputed from the two readouts."""
    want = {}
    for n in Q:
        x, t = cr["quadrants"][n], cr["quadrants"][n]["2D"]
        want[f"cr-{n}-s16"], want[f"cr-{n}-sig16"] = f"{x['S16'] * 1e39:.4f}", f"{x['sigma16_reported'] * 1e39:.4f}"
        want[f"cr-{n}-s2"], want[f"cr-{n}-sig2"] = f"{t['S'] * 1e39:.4f}", f"{t['sigma'] * 1e39:.4f}"
        want[f"cr-{n}-dpct"], want[f"cr-{n}-z0"] = f"{t['d_pct']:+.3f}", f"{t['z_rho0']:+.3f}"
        want[f"cr-{n}-rhostar"] = f"{t['rho_star']:.4f}"
        want[f"cr-{n}-nopl-rhostar"] = f"{t['printed_only_without_C_PL5D']['rho_star']:.4f}"
        want[f"cr-{n}-reading"] = t["outcome"]
        want[f"cr-{n}-nopl-reading"] = t["printed_only_without_C_PL5D"]["outcome"]
    p = k["primary"]
    for i, n in enumerate(Q):
        want[f"x-{n}-z0"], want[f"x-{n}-z1"] = f"{p['r0']['z'][i]:+.3f}", f"{p['r1']['z'][i]:+.3f}"
        want[f"x-{n}-rho0"], want[f"x-{n}-rho1"] = f"{k['rho_q']['r0'][n]:.2f}", f"{k['rho_q']['r1'][n]:.2f}"
    for key, name in READING.items():
        for r in ("r0", "r1"):
            want[f"x-{key}-chi2-{r}"], want[f"x-{key}-p-{r}"] = f"{k[name][r]['chi2_4']:.3f}", f"{k[name][r]['p']:.3f}"
        want[f"x-{key}-zmax"] = f"{max(abs(z) for r in ('r0', 'r1') for z in k[name][r]['z']):.3f}"
    pct = [cr["quadrants"][n]["2D"]["d_pct"] for n in Q]
    want["x-dpct-min"], want["x-dpct-max"] = f"{min(pct):.1f}", f"{max(pct):+.1f}"
    want["x-chi2-lo"], want["x-chi2-hi"] = f"{p['r0']['chi2_4']:.2f}", f"{p['r1']['chi2_4']:.2f}"
    want["x-p-min"] = f"{math.floor(100 * min(p['r0']['p'], p['r1']['p'])) / 100:.2f}"
    want["x-zmax"] = want["x-prim-zmax"]
    want["x-nbands-paired"] = str(sum(c.startswith("band:") for c in k["crosses"]))
    want["x-nbands"] = str(int(want["x-nbands-paired"]) + len(k["bounded"]))
    want["x-nlat"] = str(sum(c.startswith("lat:") for c in k["crosses"]))
    want["x-ncontrols"] = str(len(k["controls"]))
    want["x-bounded"] = ", ".join(b.split(":", 1)[1] for b in k["bounded"])
    for n in Q:
        c = cr["quadrants"][n]["cells"]
        want[f"cr-{n}-cells"] = f"{c[0]}--{c[-1]}"
    return want


def main(argv):
    base = kv(subprocess.run(["git", "show", f"{BASE}:{VALUES}"], capture_output=True, text=True, check=True,
                             cwd=ROOT).stdout)
    cur = kv((ROOT / VALUES).read_text())
    cr = json.loads((ROOT / FD / "gencmp-e/c-r/overlap_refined.json").read_text())
    k = json.loads((ROOT / FD / "xcov/run/k/k.json").read_text())
    out, ok = [], True
    gone = sorted(set(base) - set(cur))
    moved = sorted(x for x in base if x in cur and base[x] != cur[x])
    added = sorted(set(cur) - set(base))
    if gone or moved:
        ok = False
        out.append(f"FAIL base keys removed {gone[:8]} or changed {moved[:8]}")
    else:
        out.append(f"ok   all {len(base)} base keys print the base value")
    stray = [x for x in added if not (x.startswith("cr-") or x.startswith("x-"))]
    if stray:
        ok = False
        out.append(f"FAIL added keys outside cr- and x-: {stray[:8]}")
    else:
        out.append(f"ok   {len(added)} added keys: {sum(x.startswith('cr-') for x in added)} cr- and "
                   f"{sum(x.startswith('x-') for x in added)} x-")
    want = expected(cr, k)
    bad = [x for x in added if want.get(x) != cur[x]]
    unchecked = sorted(set(added) - set(want))
    out.append(f"{'ok  ' if not bad and not unchecked else 'FAIL'} {len(want)} added keys equal their readout fields "
               f"as printed" + (f": differ {bad[:8]}" if bad else "") + (f"; unchecked {unchecked[:8]}" if unchecked else ""))
    ok &= not bad and not unchecked
    uses = defaultdict(list)
    for f in sorted((ROOT / "docs/analysis-note").glob("*.tex")):
        if f.name.startswith("values_"):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if not line.lstrip().startswith("%"):
                for x in re.findall(r"\\fvval\{([^}]*)\}", line):
                    uses[x].append(f"{f.name}:{i}")
    printed = [x for x in added if uses[x]]
    out.append(f"     {len(printed)} of the added keys print, at: {sorted({u.split(':')[0] for x in printed for u in uses[x]})}")
    out.append("")
    out.append("key\tvalue\tprinted at")
    out += [f"{x}\t{cur[x]}\t{' '.join(uses[x])}" for x in printed]
    out.append("")
    out.append("VALUES-CHECK :: " + ("PASS" if ok else "FAIL"))
    text = "\n".join(out) + "\n"
    if argv[:1] == ["--write"]:
        Path(argv[1]).write_text(text)
    print(text if not ok else "\n".join(out[:4] + out[-1:]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
