#!/usr/bin/env python3
"""Mutation harness for valid_region.py (DECLARATION.md section 9). There is one mutant per control, per bar, per
noise term, per domain rule, for the threshold's direction, and for the VR-1 guard (reading (3) carries no class).
Every mutant must be KILLED by test_valid_region.py.

Each mutant replaces one exact snippet in the module, in place, and the snippet must occur exactly once. It then
runs the whole suite in a child process and restores the original in `finally`. The original's sha256 is checked
before the first mutant and after the last. The child runs with PYTHONDONTWRITEBYTECODE=1 and -B, so a stale .pyc
cannot mask a mutant. A run counts only if the runner printed "Ran N tests" with the baseline's N. "Killed" means
the suite failed or errored.

Usage (from this directory): python3 -B mutate_valid_region.py > mutants.txt
Exit code: 0 if the baseline passes and every mutant is killed; 3 otherwise.
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "valid_region.py"

MUTANTS = [
    # V-PRIOR: threshold, direction, agreement, spreads, noise terms, domains, truth selection
    ("tau-1", "TAU = 0.5  ", "TAU = 1.0  "),
    ("tau-le", "if all(v < tau for v in vals):", "if all(v <= tau for v in vals):"),
    ("tau-direction-swapped", "        return VALID\n    if all(v >= tau for v in vals):\n        return NOT_VALID",
     "        return NOT_VALID\n    if all(v >= tau for v in vals):\n        return VALID"),
    ("undefined-rho-ignored", "    if any(v is None for v in vals):\n        return UNRES_NOISE\n", "    vals = [v for v in vals if v is not None]\n"),
    ("mixed-reads-valid", "        return NOT_VALID\n    return UNRES_NOISE", "        return NOT_VALID\n    return VALID"),
    ("spread-sub-no-subtraction", "np.mean(v ** 2 - w)", "np.mean(v ** 2)"),
    ("spread-about-mean", "raw = math.sqrt(float(np.mean(v ** 2)))", "raw = math.sqrt(float(np.var(v)))"),
    ("noise-not-squared", 'nu.append(float(t["noise_sigma"][k]) ** 2)', 'nu.append(float(t["noise_sigma"][k]))'),
    ("vg-no-ratio-factor", "var.append((1.0 + dlt) ** 2 * (sG ** 2 + sP ** 2))", "var.append((sG ** 2 + sP ** 2))"),
    ("vg-drop-prior-term", "* (sG ** 2 + sP ** 2))", "* (sG ** 2))"),
    ("sP-not-relative-to-g", "sP = sP_f * fP / gP", "sP = sP_f"),
    ("rho-g-index-fixed", 'out[f"{bn}/{gn}"] = None if sg[gi] <= 0.0 else sb[bi] / sg[gi]',
     'out[f"{bn}/{gn}"] = None if sg[gi] <= 0.0 else sb[bi] / sg[0]'),
    ("gibuu-truth-domain-off", 'if gibuu_domain and t.get("own_vertex") == "gibuu":', "if False:"),
    ("gibuu-generator-dropped", 'GENERATORS = ("genie_cv", "genie_mec", "nuwro", "gibuu")', 'GENERATORS = ("genie_cv", "genie_mec", "nuwro")'),
    ("select-includes-prior", 'return [t for t in i1["truths"] if t["graded"] and t["group"] != "prior"]',
     'return [t for t in i1["truths"] if t["graded"]]'),
    ("select-includes-ungraded", 'return [t for t in i1["truths"] if t["graded"] and t["group"] != "prior"]',
     'return [t for t in i1["truths"] if t["group"] != "prior"]'),
    # V-ATLAS: thresholds, comparisons, the graded set, the conjunction
    ("A1-strict", "a1 = neff >= NEFF_MIN", "a1 = neff > NEFF_MIN"),
    ("A2-le", "a2 = stat < STAT_MAX", "a2 = stat <= STAT_MAX"),
    ("A3-strict", "a3 = all(abs(z) <= Z_CLOSURE for z in zs.values())", "a3 = all(abs(z) < Z_CLOSURE for z in zs.values())"),
    ("A3-signed", "a3 = all(abs(z) <= Z_CLOSURE for z in zs.values())", "a3 = all(z <= Z_CLOSURE for z in zs.values())"),
    ("A-drop-A2", "VALID if (a1 and a2 and a3)", "VALID if (a1 and a3)"),
    ("neff-4000", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.15, 2.0", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 4000.0, 0.15, 2.0"),
    ("stat-0.2", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.15, 2.0", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.2, 2.0"),
    ("zclosure-2.5", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.15, 2.0", "NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.15, 2.5"),
    ("atlas-all-truths", 'graded = [t for t in d["I1"]["truths"] if t["graded"]]', 'graded = list(d["I1"]["truths"])'),
    # reading (3): covariance terms, contrasts, and the VR-1 guard
    ("departure-no-VP", "R = Dinv @ C @ Dinv + np.diag(f ** 2 * VP / gP ** 4)", "R = Dinv @ C @ Dinv"),
    ("contrast-no-correlation", "s = math.sqrt(R[i, i] + R[j, j] - 2.0 * R[i, j])", "s = math.sqrt(R[i, i] + R[j, j])"),
    ("quadrant-var-diagonal", "var = float(C[np.ix_(idx, idx)].sum()) / G ** 2", "var = float(np.trace(C[np.ix_(idx, idx)])) / G ** 2"),
    ("contrasts-all-cells", "vq = [c for c in cells if c in valid]", "vq = list(cells)"),
    ("resolved-size-1sigma", '"resolved_3sigma": POS * s,', '"resolved_3sigma": s,'),
    ("VR1-class-reinstated", 'rq_out[q] = {"valid_cells": vq, "contrasts": pairs}',
     'rq_out[q] = {"valid_cells": vq, "contrasts": pairs, "class": "localized" if pairs else ""}'),
    # controls and the stop
    ("C-PIN-drop", "        if got != want:\n            bad[key]", "        if False:\n            bad[key]"),
    ("C-CELLS-drop-I6", 'if d["I6"]["cells"] != CELLS:', "if False:"),
    ("C-CELLS-drop-reported", "or not all(c[\"reported\"] for c in rc):", ":"),
    ("C-BOX-drop-equality", 'bad.append(f"{c}: I4 box != I5 box")', "pass"),
    ("C-BOX-drop-siblings", "            if not differing_axes(b4[a], b4[b]):", "            if False:"),
    ("C-DOMAIN-drop", "ok = len(gib) == 1 and gib[0] == low and len(low) == 8 and fam and all(f == low for f in fam)", "ok = True"),
    ("C-TRUTHS-drop", "ok = names == TRUTH_NAMES and n_graded == N_GRADED", "ok = n_graded == N_GRADED"),
    ("C-BIAS-drop", "    ok = a == b\n", "    ok = True\n"),
    ("C-F-tol", '"C-F": 1e-12', '"C-F": 1e-10'),
    ("C-GF-tol", '"C-GF": 1e-12', '"C-GF": 1e-10'),
    ("C-COV-sym-tol", '"C-COV-sym": 1e-12', '"C-COV-sym": 1e-6'),
    ("C-COV-sig-tol", '"C-COV-sig": 1e-12', '"C-COV-sig": 1e-10'),
    ("C-COV-drop-cholesky", 'ok = asym <= TOL["C-COV-sym"] and chol and', 'ok = asym <= TOL["C-COV-sym"] and'),
    ("C-FINITE-stat-zero", "np.all(stat > 0)", "np.all(stat >= 0)"),
    ("C-RHO-drop", 'return _ctl("C-RHO", ok,', 'return _ctl("C-RHO", True,'),
    ("stop-ignored", "    if ok:\n        out[\"readings\"] = readings(d)", "    if True:\n        out[\"readings\"] = readings(d)"),
    ("exit-0-on-stop", "return 0 if ok else 3", "return 0"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_suite():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_valid_region"], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=900)
    m = re.search(r"^Ran (\d+) tests? in", r.stderr, re.M)
    return r.returncode, int(m.group(1)) if m else None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""


def main():
    orig_text = TARGET.read_text()
    orig_sha = sha(TARGET)
    rc, n_base, tail = run_suite()
    print(f"target {TARGET.name} sha256 {orig_sha}")
    print(f"suite test_valid_region.py sha256 {sha(HERE / 'test_valid_region.py')}; python {sys.version.split()[0]}")
    print(f"baseline: rc {rc}, ran {n_base}, '{tail}'")
    if rc != 0 or not n_base:
        print("BASELINE FAILS: no mutant is meaningful")
        return 3
    survivors, rows = [], []
    try:
        for mid, old, new in MUTANTS:
            k = orig_text.count(old)
            if k != 1:
                rows.append((mid, "NOT-APPLIED", f"snippet occurs {k} times"))
                survivors.append(mid)
                continue
            TARGET.write_text(orig_text.replace(old, new))
            rc, n, tail = run_suite()
            if rc == 0 and n == n_base:
                verdict = "SURVIVED"
                survivors.append(mid)
            elif rc != 0:
                verdict = "KILLED"
            else:
                verdict = f"SUSPECT (rc 0, ran {n} != {n_base})"
                survivors.append(mid)
            rows.append((mid, verdict, tail))
    finally:
        TARGET.write_text(orig_text)
    after = sha(TARGET)
    for r in rows:
        print("\t".join(r))
    print(f"restored sha256 {after} {'== original' if after == orig_sha else '!= ORIGINAL'}")
    print(f"mutants {len(MUTANTS)}; killed {len(MUTANTS) - len(survivors)}; survivors {survivors}")
    return 0 if not survivors and after == orig_sha else 3


if __name__ == "__main__":
    sys.exit(main())
