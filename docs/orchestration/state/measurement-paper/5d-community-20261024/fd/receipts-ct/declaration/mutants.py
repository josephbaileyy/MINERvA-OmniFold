#!/usr/bin/env python3
"""Mutation run for fd_ct_readers.py (FD-CT-READERS-DECLARATION.md section 6.3): each mutant is one textual change to
the tool, applied in place; the whole test module runs against it, and the tool is restored (its sha256 is checked after
every mutant and at the end). A mutant is killed if the run fails. A mutant whose text is not found exactly once is
reported as NOT APPLIED and counts as a failure of this receipt.

    python3 -I -B mutants.py <repo>
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
TOOL = REPO / "nd-unfolding/fd_ct_readers.py"
TESTS = REPO / "nd-unfolding/tests"
MUTANTS = [
    # shared
    ("S1 pin unchecked", 'f0.require("S", a.s1_npz, PINS["s1_npz"], "S1 assembly")', "pass"),
    ("S species sum unchecked", "np.allclose(sum(species), Cr, rtol=TOL, atol=TOL * scale)", "True"),
    ("S C_total_resp unchecked", 'np.allclose(s["C_total"] + Cr, Ctr, rtol=TOL, atol=TOL * scale)', "True"),
    ("M is C_total", '"C_resp": Cr, "M": Ctr}', '"C_resp": Cr, "M": s["C_total"]}'),
    ("leak guard off", '    guard.check("readout", out)\n', "    pass\n"),
    ("overwrite allowed", "    if a.out_json.exists():\n", "    if False:\n"),
    # 3a
    ("R0 digest unchecked", 'f0.require("R0", p, sha, f"W2b {v}")', "pass"),
    ("R0 meta unchecked", 'f0.sa_call("R0", sa.check_meta, p,', '(lambda *q: None)("R0", sa.check_meta, p,'),
    ("R1 positivity unchecked", "all(bool(np.all(X[v] > 0)) for v in W2B)", "True"),
    ("shifts swapped", 's_minus, s_plus = X["rr0"] / z - 1.0, X["rr1"] / z - 1.0',
     's_minus, s_plus = X["rr1"] / z - 1.0, X["rr0"] / z - 1.0'),
    ("half span not halved", 'd = (X["rr1"] - X["rr0"]) / (2.0 * z)', 'd = (X["rr1"] - X["rr0"]) / z'),
    ("half span relative to f", 'd = (X["rr1"] - X["rr0"]) / (2.0 * z)', 'd = (X["rr1"] - X["rr0"]) / (2.0 * f)'),
    ("sigma_resp from C_total", 'sig_resp, sig_tot, sig_m = rel_sigma(S["C_resp"], f)',
     'sig_resp, sig_tot, sig_m = rel_sigma(S["C_total"], f)'),
    ("span projector on every eigenvector", "keep = lam > TOL * lam.max()", "keep = lam > -1.0"),
    ("quadratic form against C_total", '"C_total_resp": quad(d, M_rel)', '"C_total_resp": quad(d, Ct_rel)'),
    # 4C
    ("C0 product digest unchecked", 'f0.require("C0", p, man[str(p)], name)', "pass"),
    ("C0 manifest pin unchecked", 'f0.require("C0", a.s5p_sums, PINS["s5p_sums"], "s5p archive sums")', "pass"),
    ("C1 meta unchecked", 'bad = f0.meta_problems(p, m, "cal", {"hyp": hyp})', "bad = []"),
    ("C1 count unchecked", 'n != f0.COUNTS["cal"][cal] or len(', "False or len("),
    ("C2 B_eff unchecked", "abs(beff / f0b[name] - 1.0) <= TOL", "True"),
    ("C3 positivity unchecked", "        if not np.all(Xt > 0):\n", "        if False:\n"),
    ("r relative to f", "R[name] = Xh / Xt - 1.0", "R[name] = Xh / f - 1.0"),
    ("about-mean uses the unweighted mean", "b = (w[:, None] * ri).sum(axis=0) / w.sum()", "b = ri.mean(axis=0)"),
    ("weighted percentiles unweighted", "weighted_percentiles(c2, w, PERCENTILES)",
     "weighted_percentiles(c2, np.ones_like(w), PERCENTILES)"),
    ("reference percentiles from the tail", '"percentiles": {str(p): chi2_quantile(p / 100.0, ndf) for p in PERCENTILES}}}',
     '"percentiles": {str(p): chi2_quantile(1.0 - p / 100.0, ndf) for p in PERCENTILES}}}'),
    ("C_e matrix is C_total", '"C_e": S["C_e"] / ff}', '"C_e": S["C_total"] / ff}'),
    ("eight cells for every truth", 'if name == "A7_gibuu":', "if True:"),
    ("width ratio with Bessel", "sd = np.sqrt((w[:, None] * (ri - b) ** 2).sum(axis=0) / w.sum())",
     "sd = np.sqrt((w[:, None] * (ri - b) ** 2).sum(axis=0) / (w.sum() - 1))"),
    ("chi2 quantile from the tail", "if 1.0 - f0.chi2_sf_even(mid, ndf) < q:", "if f0.chi2_sf_even(mid, ndf) < q:"),
    # 5A
    ("P0 C_PL rebuild unchecked", 'float(np.max(np.abs(C_re - z["C_PL"])) / np.max(np.abs(z["C_PL"]))) <= TOL,', "True,"),
    ("P0 e constancy unchecked", "all(np.ptp(e_vec[X]) <= TOL * e[X] for X in PERIODS)", "True"),
    ("P0 cancellation unchecked", 'float(np.max(np.abs(sum(e_vec[X] * z[f"g_{X}"] for X in PERIODS)))) <= TOL', "True"),
    ("P0 json unchecked", 'pj.get("npz", {}).get("sha256") == PINS["playlist_npz"]', "True"),
    ("P1 f unchecked", "bool(np.allclose(U @ xc, f, rtol=TOL, atol=0))", "True"),
    ("P2 schema unchecked", 'pm.get("schema") == "s5p-mc-truth-pred/1" and ', ""),
    ("P3 unchecked", "        if not sup > 0:\n", "        if False:\n"),
    ("P4 cancellation unchecked", "    if ident > TOL:\n", "    if False:\n"),
    ("k without 1 - V2", "k = V2 / (1.0 - V2)", "k = V2"),
    ("footprint without volume", "contrib = x * sa.s1.fine_volume()", "contrib = x"),
    ("footprint normalized over the whole cell", "om[R, pos[int(b)]] = contrib[inside & (c2 == b)].sum() / sup",
     "om[R, pos[int(b)]] = contrib[inside & (c2 == b)].sum() / tot"),
    ("outside share over the support", "outside[R] = (tot - sup) / tot", "outside[R] = (tot - sup) / sup"),
    ("S_ref without PC", 'for X in ("PB", "PC"))', 'for X in ("PB",))'),
    ("extrapolation threshold 0.5", "EXTRAPOLATED = 0.10", "EXTRAPOLATED = 0.5"),
    ("prior weights for the central variant", '(("central", xc), ("prior", xp))', '(("central", xp), ("prior", xp))'),
    # round 2: the independent review's surviving mutants (review/review_mutants.log), rewritten for the code as it
    # now stands, and the code the review's dispositions added
    ("S U unchecked", "np.array_equal(U32, U.astype(np.float32))", "True"),
    ("S f positivity unchecked", "bool(f.shape == (N_CELLS,) and np.all(f > 0))", "True"),
    ("S C_total = C_e + C_model_abs unchecked",
     'np.allclose(s["C_e"] + s["C_model_abs"], s["C_total"], rtol=TOL, atol=TOL * scale)', "True"),
    ("S C_resp pin unchecked", 'f0.require("S", a.cresp, PINS["cresp"], "C_resp")', "pass"),
    ("R0 shape check removed", "    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):\n",
     "    if False:\n"),
    ("curvature numerator is the span", 'np.linalg.norm(X["rr1"] + X["rr0"] - 2.0 * z) / np.linalg.norm(X["rr1"] - X["rr0"])',
     'np.linalg.norm(X["rr1"] - X["rr0"]) / np.linalg.norm(X["rr1"] - X["rr0"])'),
    ("|d|/sigma_resp divides by sigma_total_resp", "r_resp, r_m = np.abs(d) / sig_resp, np.abs(d) / sig_m",
     "r_resp, r_m = np.abs(d) / sig_m, np.abs(d) / sig_m"),
    ("C_total quadratic form on C_total + C_resp", '"C_total": quad(d, Ct_rel),', '"C_total": quad(d, M_rel),'),
    ("sigma_rel C_total is C_total + C_resp's", '"sigma_rel": {"C_resp": sig_resp.tolist(), "C_total": sig_tot.tolist(),',
     '"sigma_rel": {"C_resp": sig_resp.tolist(), "C_total": sig_m.tolist(),'),
    ("half-span summary without abs", '"half_span_summary_abs": summary(np.abs(d)),', '"half_span_summary_abs": summary(d),'),
    ("3a guard table empty", "guard = f0.LeakGuard(f, list(X.values()))", "guard = f0.LeakGuard(f, [])"),
    ("random-direction expectation wrong", '"random_direction_expectation": float(keep.sum()) / N_CELLS,',
     '"random_direction_expectation": 1.0,'),
    ("C0 F0b pin unchecked", 'f0.require("C0", a.f0b_readout, PINS["f0b_readout"], "F0b readout")', "pass"),
    ("C1 repeated-seed check removed", ' or len({m["pseudo_seed"] for m in metas[name]}) != n:', ":"),
    ("C1 GiBUU cells from the definition unchecked", 'lo == list(f0.GIBUU_CELLS),', "True,"),
    ("about-b~ distribution unweighted", '"about_weighted_mean": distribution(c2c, w, len(idx)),',
     '"about_weighted_mean": distribution(c2c, np.ones_like(w), len(idx)),'),
    ("written B_eff is the count", '"B_eff": float(w.sum() ** 2 / (w ** 2).sum()), "matrices": {}}',
     '"B_eff": float(len(w)), "matrices": {}}'),
    ("width-ratio summary against C_e", '"width_ratio_summary": summary(sd / np.sqrt(np.diag(Mi)))}',
     '"width_ratio_summary": summary(sd / np.sqrt(np.diag(mats["C_e"][np.ix_(idx, idx)])))}'),
    ("4C guard table empty", "guard = f0.LeakGuard(f, ints)", "guard = f0.LeakGuard(f, [])"),
    ("weighted percentile one order statistic high", "min(int(np.searchsorted(c, p / 100.0 - 1e-15)), v.size - 1)",
     "min(int(np.searchsorted(c, p / 100.0 - 1e-15)) + 1, v.size - 1)"),
    ("unweighted percentiles by numpy linear", "weighted_percentiles(c2, np.ones_like(w), PERCENTILES)))}",
     "np.percentile(c2, PERCENTILES).tolist()))}"),
    ("P0 e sum unchecked", "abs(sum(e.values()) - 1.0) <= TOL", "True"),
    ("P0 distinct cells unchecked", "n2 == 205 and np.unique(support).size == n2", "n2 == 205"),
    ("P0 one entry per cell unchecked", 'all(z[f"{q}_{X}"].shape == (n2,) for q in "egr" for X in PERIODS)', "True"),
    ("P0 grid edges unchecked", 'np.array_equal(sa.s1.FINE["pt"], PT_2D) and np.array_equal(sa.s1.FINE["pz"], PZ_2D)', "True"),
    ("P1 central pin unchecked", 'f0.require("P1", a.central, PINS["central"], "the (e) central value")', "pass"),
    ("P1 central meta unchecked", 'f0.sa_call("P1", sa.check_meta, a.central,', '(lambda *q: None)("P1", sa.check_meta, a.central,'),
    ("P2 prior pin unchecked", 'f0.require("P2", a.prior, PINS["prior"], "MnvTune v1 prediction")', "pass"),
    ("P2 edges unchecked", 'pm.get("schema") == "s5p-mc-truth-pred/1" and edges_ok and', 'pm.get("schema") == "s5p-mc-truth-pred/1" and'),
    ("5A guard without the partial integrals", "guard = f0.LeakGuard(f, [U @ xp, *partial])", "guard = f0.LeakGuard(f, [U @ xp])"),
    ("5A guard empty", "guard = f0.LeakGuard(f, [U @ xp, *partial])", "guard = f0.LeakGuard(f, [])"),
    ("central outside share written", 'write_outside=vn == "prior"', "write_outside=True"),
    ("S_ref from projected r", 'bref = {X: om @ (e[X] * (z[f"r_{X}"] / z["r_PA"] - 1.0)) for X in ("PB", "PC")}',
     'bref = {X: e[X] * ((om @ z[f"r_{X}"]) / (om @ z["r_PA"]) - 1.0) for X in ("PB", "PC")}'),
    ("negative counts never counted", "        negative[R] = int(np.sum(om[R] < 0))\n", "        pass\n"),
    # amendment 1: the near-f masking of the central partial integrals
    ("near-f masking reverted to the outside-share rule", 'np.where(near_f(sup_int, f), np.nan, sup_int)',
     'np.where(outside > 0, sup_int, np.nan)'),
    ("near_f threshold zero", "return np.abs(x / f - 1.0) < f0.LEAK_REL", "return np.abs(x / f - 1.0) < 0.0"),
    ("near_f threshold 1 (drops off-f integrals too)", "return np.abs(x / f - 1.0) < f0.LEAK_REL",
     "return np.abs(x / f - 1.0) < 1.0"),
    ("every central partial dropped", 'np.where(near_f(sup_int, f), np.nan, sup_int)', 'np.full_like(sup_int, np.nan)'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig_text = TOOL.read_text()
orig = sha(TOOL)
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
killed = survived = unapplied = 0
print(f"tool {orig}  mutants {len(MUTANTS)}", flush=True)
try:
    for name, old, new in MUTANTS:
        if orig_text.count(old) != 1:
            unapplied += 1
            print(f"NOT APPLIED  {name}: found {orig_text.count(old)} times", flush=True)
            continue
        TOOL.write_text(orig_text.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_ct_readers"], cwd=TESTS, env=env,
                           capture_output=True, text=True, timeout=1800)
        TOOL.write_text(orig_text)
        if sha(TOOL) != orig:
            raise SystemExit("the tool was not restored")
        ok = r.returncode != 0
        killed += ok
        survived += not ok
        tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
        print(f"{'KILLED  ' if ok else 'SURVIVED'}  {name}  ({'; '.join(tail)})", flush=True)
finally:
    TOOL.write_text(orig_text)
print(f"killed {killed} of {len(MUTANTS)}; survived {survived}; not applied {unapplied}; tool restored {sha(TOOL) == orig}")
raise SystemExit(0 if survived == 0 and unapplied == 0 and sha(TOOL) == orig else 1)
