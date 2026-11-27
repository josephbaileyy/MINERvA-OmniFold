#!/usr/bin/env python3
"""Addendum A1 to 2D-CLOSURE.md: S5's own per-band GEANT sizes, and the per-cell tail.

    python3 -I closure_2d_a1.py <main-commit>        # run from inside the repository

Reads two committed files at <main-commit> through `git show` and prints each file's path and sha256:

  - S5's production covariance npz (per-band matrices `band_GEANT_{Neutron,Pion,Proton}`, `total`,
    `universe`, `cells_x_EU`, `area`); its sha256 must equal Q's input in the Stage F rebuild
    `input_sha256.txt`, which this script also reads and checks;
  - the Stage F rebuild recompute_results.json (`/sigma/{total,universe,Q}`);
  - the VL175 budget.json, for the per-band comparison.

Definitions (checked here against recompute_results.json): per-cell relative sigma
sqrt(C_cc) / x_c * 100 with x = cells_x_EU, and integral sqrt(a^T C a) / (x . a) * 100 with a = area.
The per-cell tail is read against S5's `total`, not Q: Q = total + C_PL, and C_PL is not committed.
Standard library plus numpy.
"""
import hashlib
import io
import json
import math
import subprocess
import sys

import numpy as np

S5 = "docs/orchestration/state/2d-closeout/stageC/production/evidence/production/results/production_cov.npz"
REC = "docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/recompute_results.json"
INSHA = "docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/input_sha256.txt"
VL175 = "docs/orchestration/state/2d-closeout/c04-repair/products/budget.json"
BANDS = ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton")
THRESHOLDS = (0.05, 0.1, 0.2, 0.3)
N_NAMED = 8


def blob(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    commit = subprocess.run(["git", "rev-parse", sys.argv[1]], capture_output=True, text=True,
                            check=True).stdout.strip()
    print(f"main commit {commit}")
    raw = {p: blob(commit, p) for p in (S5, REC, INSHA, VL175)}
    for p, b in raw.items():
        print(f"input {p} sha256 {hashlib.sha256(b).hexdigest()} bytes {len(b)}")

    s5_sha = hashlib.sha256(raw[S5]).hexdigest()
    q_inputs = [ln.split()[0] for ln in raw[INSHA].decode().splitlines() if ln.strip()]
    print(f"S5 npz sha256 is one of Q's recorded inputs: {s5_sha in q_inputs}")
    if s5_sha not in q_inputs:
        sys.exit("STOP: the committed S5 npz is not the file Q was built from")

    z = np.load(io.BytesIO(raw[S5]), allow_pickle=False)
    x, a = z["cells_x_EU"], z["area"]
    norm = float(x @ a)

    def rel(c):
        return np.sqrt(np.clip(np.diag(c), 0.0, None)) / x * 100.0

    def integral(c):
        return math.sqrt(float(a @ c @ a)) / norm * 100.0

    sig = json.loads(raw[REC])["sigma"]
    print("formula control against recompute_results.json:")
    for key in ("total", "universe"):
        m, i = float(np.median(rel(z[key]))), integral(z[key])
        dm, di = abs(m - sig[key]["median"]), abs(i - sig[key]["integral"])
        print(f"  {key}: median {m:.9f} vs {sig[key]['median']:.9f} (|d| {dm:.1e}); "
              f"integral {i:.9f} vs {sig[key]['integral']:.9f} (|d| {di:.1e})")
        if dm > 1e-9 or di > 1e-9:
            sys.exit("STOP: the formula does not reproduce the recorded values")

    vl = json.loads(raw[VL175])["adopted"]["per_band"]
    print("per band, S5 against VL175 (percent of x):")
    for b in BANDS:
        r = rel(z["band_" + b])
        v = vl["full_" + b]
        print(f"  {b}: S5 median {np.median(r):.6f} p84 {np.percentile(r, 84):.6f} max {r.max():.6f} "
              f"(cell {int(r.argmax())}) integral {integral(z['band_' + b]):.6f} | VL175 median "
              f"{v['median_pct']:.6f} p84 {v['p84_pct']:.6f} max {v['max_pct']:.6f} "
              f"integral {v['integral_sigma_pct']:.6f}")

    qm, qi = sig["Q"]["median"], sig["Q"]["integral"]
    gm = math.sqrt(sum(float(np.median(rel(z["band_" + b]))) ** 2 for b in BANDS))
    g = sum(z["band_" + b] for b in BANDS)
    gi = integral(g)
    print(f"S5 GEANT quadrature of medians {gm:.6f}; integral of the summed matrix {gi:.6f}")
    print(f"median (approximate bound, caveat 2 stands): remove {qm:.6f} -> {math.sqrt(qm * qm - gm * gm):.6f}; "
          f"double -> {math.sqrt(qm * qm + 3 * gm * gm):.6f}")
    print(f"integral (exact: variances add): remove {qi:.6f} -> {math.sqrt(qi * qi - gi * gi):.6f}; "
          f"double -> {math.sqrt(qi * qi + 3 * gi * gi):.6f}")

    tc, gc = rel(z["total"]), rel(g)
    f = gc / tc
    print(f"per-cell tail against S5 total ({len(tc)} cells), G = sum of the three band matrices:")
    for th in THRESHOLDS:
        print(f"  cells with GEANT sigma / total sigma > {th}: {int((f > th).sum())}")
    print(f"  median variance share {float(np.median(f ** 2)):.6f}")
    for c in np.argsort(-f)[:N_NAMED]:
        print(f"  cell {int(c)}: total {tc[c]:.4f}% GEANT {gc[c]:.4f}% ratio {f[c]:.4f} "
              f"variance share {f[c] ** 2:.4f}")
    rem = tc - np.sqrt(tc ** 2 - gc ** 2)
    print(f"S5-only per-cell bound on removal (too loose to bound the median): max shift {rem.max():.6f} pp "
          f"in cell {int(rem.argmax())}")


if __name__ == "__main__":
    main()
