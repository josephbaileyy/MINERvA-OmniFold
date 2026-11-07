#!/usr/bin/env python3
"""Mutation harness for per_period_benchmark.py (DECLARATION.md section 9): one mutant per control, bar, divisor,
noise term and combination weight. Every mutant must be KILLED by test_per_period_benchmark.py.

Each mutant replaces one exact snippet (which must occur exactly once) in the module, IN PLACE, runs the whole suite
in a child process, and restores the original in `finally`. The original's sha256 is checked before the first mutant
and after the last. The child runs with PYTHONDONTWRITEBYTECODE=1 and -B, so no stale .pyc can mask a mutant. A run
counts only if the runner printed "Ran N tests" with the baseline's N; "killed" means the suite failed or errored.

Usage (from this directory): python3 -B mutate_per_period.py > mutants.txt
Exit code: 0 if the baseline passes and every mutant is killed; 3 otherwise.
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "per_period_benchmark.py"

MUTANTS = [
    # N1: the seed term and the centring of the noise estimate
    ("N1-seed-undivided-noise_term", 'n += quad(g["seed"] - g["x"], lam, U, idx) / 2.0', 'n += quad(g["seed"] - g["x"], lam, U, idx)'),
    ("N1-seed-undivided-noise_var", "v += (fs - f0) ** 2 / 2.0", "v += (fs - f0) ** 2"),
    ("N1-centre-on-x", "c = reps - reps.mean(axis=0)", 'c = reps - g["x"]'),
    ("noise-ddof0", "v = float(np.var(fr, ddof=1))", "v = float(np.var(fr, ddof=0))"),
    ("noise-term-ddof0", "n = sum(quad(r, lam, U, idx) for r in c) / (len(reps) - 1)", "n = sum(quad(r, lam, U, idx) for r in c) / len(reps)"),
    ("debias-sign", 'out.update({"n": n, "T_debiased": T - n,', 'out.update({"n": n, "T_debiased": T + n,'),
    # bars and classes
    ("bar-POS-2.5", "POS, NULL = 3.0, 2.0", "POS, NULL = 2.5, 2.0"),
    ("bar-NULL-2.5", "POS, NULL = 3.0, 2.0", "POS, NULL = 3.0, 2.5"),
    ("r5-strict", "    if z >= POS:\n        return \"closer without 1G-1M\"", "    if z > POS:\n        return \"closer without 1G-1M\""),
    ("r2-drop-pair-condition", "if all(z(g, h) >= POS for h in o) and abs(z(o[0], o[1])) <= NULL:", "if all(z(g, h) >= POS for h in o):"),
    ("r3-precedence", "    if unresolved_by_groups:\n        return \"not resolved by the period groups\"\n", ""),
    ("merge-takes-first", "    return a if a == b else \"unresolved (noise model)\"", "    return a"),
    ("statement-drop-B-differs", 'r4_classes["PC"] == R4_MATCH and r4_classes["PB"] == "differs":', 'r4_classes["PC"] == R4_MATCH:'),
    ("zscore-zero-over-zero", "return 0.0 if delta == 0 else math.copysign(math.inf, delta)", "return math.copysign(math.inf, delta)"),
    # divisor and mode sets
    ("divisor-205", 'T = quad(g["x"] - p, lam, U, idx) / k', 'T = quad(g["x"] - p, lam, U, idx) / 205'),
    ("k-72", "K73 = 73  ", "K73 = 72  "),
    ("top-modes-smallest", "return np.argsort(lam)[::-1][:k]", "return np.argsort(lam)[:k]"),
    # controls
    ("C-PUB-tol", '"C-PUB": 1e-8', '"C-PUB": 1e-6'),
    ("C-SUM-tol", '"C-SUM": 1e-6', '"C-SUM": 1e-4'),
    ("C-CTRL-cells-tol", '"C-CTRL-cells": 1e-8', '"C-CTRL-cells": 1e-6'),
    ("C-STEP-tol", '"C-STEP": 1e-10', '"C-STEP": 1e-8'),
    ("C-K-drop-k", "ok = k == want_k and abs(per205 - want_per205) <= 5e-4", "ok = abs(per205 - want_per205) <= 5e-4"),
    ("C-M-drop-z", "good = abs(got_l - want_l) <= half * (1 + 1e-9) and abs(got_z - zabs) <= 0.005 * (1 + 1e-9)",
     "good = abs(got_l - want_l) <= half * (1 + 1e-9)"),
    ("C-COMB-drop-weights", "ok = wdev <= 1e-12 and abs(r) <= TOL[\"C-COMB\"]", "ok = abs(r) <= TOL[\"C-COMB\"]"),
    ("C-PARTC-drop-rowsum", "ok = (const and dev <= TOL[\"C-W\"] and rowsum <= 1e-12 and st == step_declared",
     "ok = (const and dev <= TOL[\"C-W\"] and st == step_declared"),
    ("C-GRAD-drop", 'return _ctl("C-GRAD", d <= TOL["C-GRAD"],', 'return _ctl("C-GRAD", True,'),
    ("C-IN-cells-drop", 'bad[name] = str(e)', 'pass'),
    ("verify-never-differs", "if got != want:\n            bad.append(src)", "if False:\n            bad.append(src)"),
    ("provenance-drop", "if not f.startswith(root + os.sep):", "if False:"),
    ("roles-drop-replica-check", "if sorted(roles[\"groups\"][g][\"boot\"]) != list(range(1, N_REPLICAS + 1)):", "if False:"),
    # weights, combination, the step's sigma
    ("weights-no-renorm", "return {X: np.asarray(shares_by_row[X])[ipt] / tot for X in subset}",
     "return {X: np.asarray(shares_by_row[X])[ipt] for X in subset}"),
    ("combine-seed-is-x", '"seed": sum(weights[X] * groups[X]["seed"] for X in names),', '"seed": sum(weights[X] * groups[X]["x"] for X in names),'),
    ("r5-unpaired", "zip(abc[\"reps\"], ac[\"reps\"])", "zip(abc[\"reps\"], ac[\"reps\"][::-1])"),
    ("sigma-pub-no-1+st", "grad = -(1.0 + st) * (w_hi", "grad = -(w_hi"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_suite():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_per_period_benchmark"], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=900)
    m = re.search(r"^Ran (\d+) tests? in", r.stderr, re.M)
    return r.returncode, int(m.group(1)) if m else None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""


def main():
    orig_text = TARGET.read_text()
    orig_sha = sha(TARGET)
    rc, n_base, tail = run_suite()
    print(f"target {TARGET.name} sha256 {orig_sha}")
    print(f"suite test_per_period_benchmark.py sha256 {sha(HERE / 'test_per_period_benchmark.py')}; "
          f"python {sys.version.split()[0]}")
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
