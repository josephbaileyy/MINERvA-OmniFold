#!/usr/bin/env python3
"""Reviewer's mutation round on COPIES of fd_ct_readers.py (mirrors under this scratch dir; the worktree is never
written). Each mutant is one textual change; the whole test module runs against the mutated copy. KILLED = the suite
fails; SURVIVED = the suite passes with the defect in place.

    python3 -B review_mutants.py
"""
import concurrent.futures as cf
import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIRRORS = [HERE / f"mirror{i}" for i in range(6)]
ORIG = (Path(str(HERE).replace("review-ct-notes", "review-ct")) / "nd-unfolding/fd_ct_readers.py").read_text()

MUTANTS = [
    # ---- shared / S
    ("S: 'U is S1's float32 functional matrix' unchecked", "np.array_equal(U32, U.astype(np.float32))", "True"),
    ("S: 'f is positive' unchecked", "bool(f.shape == (N_CELLS,) and np.all(f > 0))", "True"),
    ("S: 'C_total = C_e + C_model_abs' unchecked",
     'np.allclose(s["C_e"] + s["C_model_abs"], s["C_total"], rtol=TOL, atol=TOL * scale)', "True"),
    ("S: C_resp pin unchecked", 'f0.require("S", a.cresp, PINS["cresp"], "C_resp")', "pass"),
    # ---- 3a
    ("R0: shape/non-finite refusal removed", "    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):\n",
     "    if False:\n"),
    ("3a: curvature ratio wrong (numerator = denominator)",
     "curv = float(np.linalg.norm(s_plus + s_minus) / np.linalg.norm(s_plus - s_minus))",
     "curv = float(np.linalg.norm(s_plus - s_minus) / np.linalg.norm(s_plus - s_minus))"),
    ("3a: |d|/sigma_resp divides by sigma_total_resp",
     "r_resp, r_m = np.abs(d) / sig_resp, np.abs(d) / sig_m", "r_resp, r_m = np.abs(d) / sig_m, np.abs(d) / sig_m"),
    ("3a: quadratic form 'C_total' uses C_total + C_resp", '"C_total": quad(d, Ct_rel),', '"C_total": quad(d, M_rel),'),
    ("3a: sigma_rel C_total is C_total + C_resp's",
     'rel_sigma(S["C_resp"], f), rel_sigma(S["C_total"], f), rel_sigma(S["M"], f)',
     'rel_sigma(S["C_resp"], f), rel_sigma(S["M"], f), rel_sigma(S["M"], f)'),
    ("3a: half_span_summary_abs drops abs", '"half_span_summary_abs": summary(np.abs(d)),',
     '"half_span_summary_abs": summary(d),'),
    ("3a: guard table carries no W2b integral", "guard = f0.LeakGuard(f, list(X.values()))", "guard = f0.LeakGuard(f, [])"),
    # ---- 4C
    ("C0: F0b readout pin unchecked", 'f0.require("C0", a.f0b_readout, PINS["f0b_readout"], "F0b readout")', "pass"),
    ("C1: repeated-seed refusal removed", ' or len({m["pseudo_seed"] for m in metas[name]}) != n:', ":"),
    ("C4: decomposition refusal removed",
     "                if gap > 1e-9 * max(1.0, float(w @ c2t / w.sum())):\n", "                if False:\n"),
    ("4C: about-b~ distribution unweighted", '"about_weighted_mean": distribution(c2c, w, len(idx)),',
     '"about_weighted_mean": distribution(c2c, np.ones_like(w), len(idx)),'),
    ("4C: written B_eff is the unweighted count",
     '"B_eff": float(w.sum() ** 2 / (w ** 2).sum()), "matrices": {}}', '"B_eff": float(r.shape[0]), "matrices": {}}'),
    ("4C: width_ratio_summary from C_e", '"width_ratio_summary": summary(sd / np.sqrt(np.diag(Mi)))}',
     '"width_ratio_summary": summary(sd / np.sqrt(np.diag(mats["C_e"][np.ix_(idx, idx)])))}'),
    ("4C: guard table carries no calibration integral", "guard = f0.LeakGuard(f, ints)", "guard = f0.LeakGuard(f, [])"),
    ("4C: weighted 5th percentile one order statistic high",
     "return [float(v[o][min(int(np.searchsorted(c, p / 100.0 - 1e-15)), v.size - 1)]) for p in ps]",
     "return [float(v[o][min(int(np.searchsorted(c, p / 100.0 - 1e-15)) + (p == 5.0), v.size - 1)]) for p in ps]"),
    # ---- 5A
    ("P0: 'e_X sum to 1' unchecked", "abs(sum(e.values()) - 1.0) <= TOL", "True"),
    ("P0: '205 distinct 2D cells' unchecked",
     "bool(n2 == 205 and np.unique(support).size == n2\n                                                          and support.min() >= 0 and support.max() < 14 * NPZ_2D)",
     "True"),
    ("P0: 'one entry per cell' unchecked", 'all(z[f"{q}_{X}"].shape == (n2,) for q in "egr" for X in PERIODS)', "True"),
    ("P1: central pin unchecked", 'f0.require("P1", a.central, PINS["central"], "the (e) central value")', "pass"),
    ("P1: central meta unchecked", 'f0.sa_call("P1", sa.check_meta, a.central,', '(lambda *q: None)("P1", sa.check_meta, a.central,'),
    ("P2: prior pin unchecked", 'f0.require("P2", a.prior, PINS["prior"], "MnvTune v1 prediction")', "pass"),
    ("P2: edges unchecked", 'pm.get("schema") == "s5p-mc-truth-pred/1" and edges_ok and', 'pm.get("schema") == "s5p-mc-truth-pred/1" and'),
    ("P4: PSD/rank refusal removed",
     "    if rank > 2 or lam.min() < -TOL * max(lam.max(), 1e-300):\n", "    if False:\n"),
    ("5A: guard table carries no prior integral", "guard = f0.LeakGuard(f, [U @ xp])", "guard = f0.LeakGuard(f, [])"),
    ("5A: S_ref16 from the linearly projected relative offset",
     'Sref = sum(np.outer(e[X] * (r[X] / r["PA"] - 1.0), e[X] * (r[X] / r["PA"] - 1.0)) for X in ("PB", "PC"))',
     'Sref = sum(np.outer(e[X] * (om @ (z[f"r_{X}"] / z["r_PA"] - 1.0)), e[X] * (om @ (z[f"r_{X}"] / z["r_PA"] - 1.0))) for X in ("PB", "PC"))'),
    ("5A: planted data/prior ratio (U@xc)/(U@xp)-1 written, guard as is",
     '"variants": variants,', '"variants": variants, "planted": ((U @ xc) / (U @ xp) - 1.0).tolist(),'),
    ("5A: planted supported-footprint share of f (1 - outside) written, guard as is",
     '"extrapolated_cells": [f"R{c:02d}" for c in range(N_CELLS) if outside[c] > EXTRAPOLATED]}',
     '"extrapolated_cells": [f"R{c:02d}" for c in range(N_CELLS) if outside[c] > EXTRAPOLATED], "planted_inside": (1.0 - outside).tolist()}'),
]


def run(job):
    i, (name, old, new) = job
    M = MIRRORS[i % len(MIRRORS)]
    tool = M / "nd-unfolding/fd_ct_readers.py"
    if ORIG.count(old) != 1:
        return f"NOT APPLIED  {name}: found {ORIG.count(old)} times"
    tool.write_text(ORIG.replace(old, new))
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["TMPDIR"] = str(HERE)
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_ct_readers"], cwd=M / "nd-unfolding/tests",
                       env=env, capture_output=True, text=True, timeout=3000)
    tool.write_text(ORIG)
    tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
    fails = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
    return f"{'KILLED  ' if r.returncode else 'SURVIVED'}  {name}  ({'; '.join(tail)}) {' | '.join(fails)}"


if __name__ == "__main__":
    print(f"original tool sha256 {hashlib.sha256(ORIG.encode()).hexdigest()}  mutants {len(MUTANTS)}", flush=True)
    jobs = list(enumerate(MUTANTS))
    results = [None] * len(jobs)
    # one job per mirror at a time
    with cf.ThreadPoolExecutor(len(MIRRORS)) as ex:
        lanes = [[j for j in jobs if j[0] % len(MIRRORS) == k] for k in range(len(MIRRORS))]

        def lane(js):
            return [(j[0], run(j)) for j in js]
        for out in ex.map(lane, lanes):
            for k, line in out:
                results[k] = line
    for line in results:
        print(line)
    print(f"survived {sum(l.startswith('SURVIVED') for l in results)} of {len(results)}; "
          f"not applied {sum(l.startswith('NOT') for l in results)}")
