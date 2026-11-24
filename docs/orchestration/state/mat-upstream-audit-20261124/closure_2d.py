#!/usr/bin/env python3
"""Bound the 2D effect of the GEANT_* truth-weighting difference (MAT-MINERvA 3e411c0d) on Q.

    python3 -I closure_2d.py <main-commit>        # run from inside the repository

Reads two committed files at <main-commit> through `git show`, so the inputs are the bytes at
that commit, not the working tree. It prints each file's path and sha256, the values it reads,
and the bounds:

  - per-band GEANT sizes: VL175 budget.json, /adopted/per_band/full_GEANT_{Neutron,Pion,Proton},
    fields median_pct and integral_sigma_pct;
  - Q's sizes: the Stage F rebuild recompute_results.json, /sigma/Q/{median,integral}.

The quadrature of per-bin medians is an approximate bound, not a recomputation of Q without the
bands. Standard library only.
"""
import hashlib
import json
import math
import subprocess
import sys

BUDGET = "docs/orchestration/state/2d-closeout/c04-repair/products/budget.json"
QFILE = "docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/recompute_results.json"
BANDS = ("full_GEANT_Neutron", "full_GEANT_Pion", "full_GEANT_Proton")


def blob(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    commit = subprocess.run(["git", "rev-parse", sys.argv[1]], capture_output=True, text=True,
                            check=True).stdout.strip()
    print(f"main commit {commit}")
    raw_b, raw_q = blob(commit, BUDGET), blob(commit, QFILE)
    for path, raw in ((BUDGET, raw_b), (QFILE, raw_q)):
        print(f"input {path} sha256 {hashlib.sha256(raw).hexdigest()} bytes {len(raw)}")

    per_band = json.loads(raw_b)["adopted"]["per_band"]
    med, integ = {}, {}
    for b in BANDS:
        med[b] = per_band[b]["median_pct"]
        integ[b] = per_band[b]["integral_sigma_pct"]
        print(f"{b}: median_pct {med[b]:.6f}  integral_sigma_pct {integ[b]:.6f}")

    q = json.loads(raw_q)["sigma"]["Q"]
    qm, qi = q["median"], q["integral"]
    print(f"Q: median {qm:.6f}  integral {qi:.6f}")

    gm = math.sqrt(sum(v * v for v in med.values()))
    gi = math.sqrt(sum(v * v for v in integ.values()))
    print(f"GEANT quadrature: median {gm:.6f}  integral {gi:.6f}")
    print(f"variance fraction of Q: median {gm * gm / (qm * qm):.6f}  integral {gi * gi / (qi * qi):.8f}")
    print(f"remove all three: median {qm:.6f} -> {math.sqrt(qm * qm - gm * gm):.6f}  "
          f"integral {qi:.6f} -> {math.sqrt(qi * qi - gi * gi):.6f}")
    print(f"double all three: median {qm:.6f} -> {math.sqrt(qm * qm + 3 * gm * gm):.6f}  "
          f"integral {qi:.6f} -> {math.sqrt(qi * qi + 3 * gi * gi):.6f}")


if __name__ == "__main__":
    main()
