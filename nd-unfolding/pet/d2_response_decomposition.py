#!/usr/bin/env python3
"""Decompose the D2 powered-closure miss into signed response + dispersion, and price each term.

WHY THIS TOOL EXISTS. The campaign's standing reading of the D2 failure is
FINDING-20260806-niter4-decision.md 2b / FINDING-20260807-d2-underfitting-probe.md:

    "the shortfall is 97.8% per-bin scatter, not bias ... even a perfect-bias estimator sitting exactly
     on the ideal fails the 0.80 bar, because the scatter penalty alone (0.08443) exceeds the entire
     residual headroom (residual_budget_abs = 0.046854). Variance is reduced by data, averaging or
     ensembling -- not by more iterations."

The CONCLUSION is right. Two things about how it is reached are not, and both change what the remedy
discussion should be about, so this tool recomputes the decomposition from the committed reports and
prices both terms in consistent units.

  (i) REFERENCE POINT. "97.8% scatter" is measured against the DILUTION IDEAL 0.63321, not against the
      criterion's own reference. The 0.80 bar compares to full recovery, and against THAT reference the
      miss is 81.4% coherent under-application of the injected tilt and 18.6% dispersion. Both
      statements are true of the same numbers; only the second is what the gate is asking.

 (ii) THE SCATTER PENALTY IS NOT THE COST OF THE DISPERSION. With x_b = 1 - r_b,
          actual cost         E_w[|x|]                       = 1 - recovery
          published penalty   E_w[|x|] - |E_w[x]|            = 0.08443
          perfect-mean cost   E_w[|x - E_w[x]|]  (a weighted MAD)
      and the second is not the third, because |.| is nonlinear under a shift: if every x_b shared a
      sign the penalty would be 0 while the MAD would not. Measured here, MAD/penalty = 4.38. So the
      counterfactual "what if the mean response were perfect" must be RECOMPUTED after the shift, not
      read off the decomposition -- and the published penalty is additionally compared against an
      ABSOLUTE L1 headroom while being itself weight-normalised (a fraction of the gap).

      Doing it correctly makes 2b's conclusion STRONGER, not weaker: the honest counterfactual is
      recovery 0.6302, and the dispersion alone is 1.85x the entire headroom rather than 2.37x inside
      it. This tool exists partly so that the next agent to notice the unit mismatch does not "fix" it
      into a false refutation, which is the mistake this file was written after making.

WHAT IT ESTABLISHES, and why it closes the remedy question rather than opening it. Each term ALONE
exceeds the headroom:
      perfect mean response, measured dispersion  -> recovery 0.6302  FAIL
      zero dispersion, measured mean response     -> recovery 0.6313  FAIL
So no single-axis remedy passes D2, and in particular seed-ensembling -- which can only touch the
dispersion term, never the mean -- caps out at 0.6313 for ANY number of seeds. That is a number to put
against "N ~ 16-25 seeds", and it is why this tool is the argument for NOT buying that ensemble.

GATED. Every number 2b published is reproduced first (E_w[r], the scatter penalty, the live-bin and
overshoot counts) and the script refuses to print anything downstream if it cannot. A decomposition that
cannot reproduce the published one is a different decomposition, and would refute nothing.

Reads only the committed reports' own 285-cell spectra. No loader, no artifact, no GPU -- so it cannot
manufacture a plausible-but-wrong number the way a reconstructed forward pass could, and it is safe to
run anywhere.

Usage:  python3 d2_response_decomposition.py [--reports-dir DIR]
"""
import argparse
import glob
import json
import os

import numpy as np

DEFAULT_PC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "powered_closure")
BIN_ORDER = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"

# Published in FINDING-20260806-niter4-decision.md 2b, from the concurrent session's probe (2113130).
# These are the GATE: reproduce them or print nothing.
PUB = {"E_r": 0.63129, "scatter": 0.08443, "live": 262, "overshoot": 87}
DILUTION_IDEAL_K3 = 0.63321          # 2b, tilt-weighted per-cell 1-(1-a_b)^k at k=3
DILUTION_IDEAL_BY_K = {2: 0.5759, 3: 0.6332, 4: 0.6629, 5: 0.6808, 6: 0.6929}   # section 2's table
BAR = 0.80                            # recovery_min; NOT a knob -- quoted, never modified
RESID_OVER_GAP_MAX = 0.20             # the same criterion in the units the decomposition lives in


def load_report(path):
    d = json.load(open(path))
    if d["bin_order"] != BIN_ORDER:
        raise SystemExit(f"[d2resp] bin_order changed: {d['bin_order']!r}\n"
                         f"  every reshape below assumes pt-major; refusing to guess (fail closed)")
    n_i, n_j = len(d["edges_pt"]) - 1, len(d["edges_pparallel"]) - 1
    out = {}
    for k in ("h_prior", "h_target", "h_unfolded", "h_untilted"):
        a = np.asarray(d[k], float)
        if a.size != n_i * n_j:
            raise SystemExit(f"[d2resp] {k}: {a.size} cells != {n_i}x{n_j}")
        out[k] = a
    return d, out, n_i, n_j


def decompose(h, n_i, n_j):
    """Signed response + dispersion, in the weighting 2b used: w_b = |h_target - h_prior|."""
    P, T, U = h["h_prior"], h["h_target"], h["h_unfolded"]
    disp = T - P
    live = np.abs(disp) > 0.0                 # 2b's 262 live bins are exactly the nonzero-gap cells
    w = np.abs(disp[live])
    ww = w / w.sum()
    r = (U[live] - P[live]) / disp[live]
    x = 1.0 - r                                # per-cell shortfall in response units

    E_r = float((ww * r).sum())
    E_abs = float((ww * np.abs(x)).sum())      # == residual/gap == 1 - recovery
    coherent = abs(1.0 - E_r)
    mad = float((ww * np.abs(x - (1.0 - E_r))).sum())

    # An independent read on the same split, in SPECTRUM space rather than response space: marginalise
    # over p_parallel. The injection is a function of pt alone, so whatever survives the marginal is
    # coherent with the thing being measured. This is algebraically the same object as `coherent`
    # whenever sign(T-P) is constant across a pt row (true here: the tilt is monotone in pt), so the
    # two agreeing is a CHECK on the construction, not a second result.
    gap = float(np.abs(disp).sum())
    l1_marg = float(np.abs((U - T).reshape(n_i, n_j).sum(axis=1)).sum())

    return {"live": int(live.sum()), "overshoot": int((r > 1.0).sum()),
            "E_r": E_r, "E_abs": E_abs, "recovery": 1.0 - E_abs,
            "coherent": coherent, "scatter_penalty": E_abs - coherent, "mad": mad,
            "rec_if_perfect_mean": 1.0 - mad, "rec_if_zero_dispersion": 1.0 - coherent,
            "coherent_frac": coherent / E_abs, "gap": gap,
            "l1_marginal_over_gap": l1_marg / gap}


def gate(m, d):
    print("=== GATE: reproduce FINDING-20260806-niter4-decision.md 2b before using this tool ===")
    ok = True
    checks = [("E_w[r]", m["E_r"], PUB["E_r"], 5e-4),
              ("scatter penalty", m["scatter_penalty"], PUB["scatter"], 5e-4),
              ("live bins", m["live"], PUB["live"], 0),
              ("overshoot bins", m["overshoot"], PUB["overshoot"], 0),
              ("recovery", m["recovery"], d["metrics"]["recovery"], 1e-9)]
    for name, mine, pub, tol in checks:
        good = (mine == pub) if tol == 0 else abs(mine - pub) <= tol
        ok &= good
        print(f"  {name:18s} mine {mine!s:>14.14s}  published {pub!s:>12.12s}  "
              f"{'OK' if good else '*** MISMATCH ***'}")
    if not ok:
        raise SystemExit("[d2resp] cannot reproduce the published decomposition; every statement below "
                         "would be about a different quantity (fail closed)")
    # The construction check: response-space and spectrum-space must agree.
    d_ = abs(m["coherent"] - m["l1_marginal_over_gap"])
    print(f"  construction check: |1-E_w[r]| {m['coherent']:.6f} vs pt-marginal/gap "
          f"{m['l1_marginal_over_gap']:.6f}  (delta {d_:.1e})")
    if d_ > 1e-3:
        raise SystemExit("[d2resp] response-space and spectrum-space splits disagree; one of the two "
                         "is mis-weighted (fail closed)")
    print("  reproduced, and the two independent constructions agree.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reports-dir", default=DEFAULT_PC)
    a = ap.parse_args()

    gate_report = os.path.join(a.reports_dir, "POWERED_CLOSURE_REPORT.slurm-56381674.json")
    arms = []
    if os.path.exists(gate_report):
        arms.append(("56381674 gate", gate_report))
    for p in sorted(glob.glob(os.path.join(a.reports_dir, "underfit_probe",
                                           "POWERED_CLOSURE_PROBE_REPORT.probe-*.json"))):
        arms.append((os.path.basename(p).split(".")[1].replace("probe-", "").split("-")[0], p))
    if not arms:
        raise SystemExit(f"[d2resp] no reports under {a.reports_dir}")

    d0, h0, n_i, n_j = load_report(arms[0][1])
    m0 = decompose(h0, n_i, n_j)
    gate(m0, d0)

    print("=== THE SAME NUMBERS, TWO REFERENCE POINTS ===")
    short_of_ideal = DILUTION_IDEAL_K3 - m0["recovery"]
    print(f"  against the DILUTION IDEAL {DILUTION_IDEAL_K3:.5f}:")
    print(f"    mean response off by {m0['E_r'] - DILUTION_IDEAL_K3:+.5f}; of the {short_of_ideal:.6f} "
          f"left over, {100*m0['scatter_penalty']/short_of_ideal:.1f}% is the scatter penalty")
    print("    -> '97.8% scatter, no bias left to remove'   [2b's framing]")
    print(f"  against FULL RECOVERY 1.0, which is what the {BAR} bar compares to:")
    print(f"    coherent under-application {m0['coherent']:.6f} of the {m0['E_abs']:.6f} miss "
          f"= {100*m0['coherent_frac']:.1f}%")
    print(f"    dispersion                 {m0['scatter_penalty']:.6f} "
          f"= {100*(1-m0['coherent_frac']):.1f}%")
    print(f"    -> 'the estimator applies {100*m0['E_r']:.1f}% of the injected tilt'   [the gate's framing]")
    print()

    print("=== PRICING EACH TERM AGAINST THE HEADROOM (consistent units) ===")
    print(f"  headroom on the miss: residual/gap <= {RESID_OVER_GAP_MAX:.2f} "
          f"(equivalently residual <= {RESID_OVER_GAP_MAX*m0['gap']:.6f} L1)")
    print(f"  published penalty {m0['scatter_penalty']:.6f} is INSIDE that by "
          f"{RESID_OVER_GAP_MAX/m0['scatter_penalty']:.2f}x -- which is why comparing it to the")
    print("    ABSOLUTE 0.046854 (and getting 'exceeds by 1.80x') is a unit mismatch.")
    print(f"  but the penalty is NOT the dispersion's cost. MAD {m0['mad']:.6f} is "
          f"{m0['mad']/m0['scatter_penalty']:.2f}x the penalty and EXCEEDS the headroom by "
          f"{m0['mad']/RESID_OVER_GAP_MAX:.2f}x.")
    print("  so 2b's conclusion holds, by a route its own arithmetic did not take.")
    print()

    print("=== WHAT WOULD IT TAKE? each term alone, then jointly ===")
    print(f"  {'arm':<14} {'recovery':>9} {'E_w[r]':>8} {'coherent':>9} {'MAD':>9} "
          f"{'perfect mean':>13} {'zero disp':>10}")
    rows = []
    for label, path in arms:
        d, h, ni, nj = load_report(path)
        m = decompose(h, ni, nj)
        m["epochs"] = d.get("configuration", {}).get("epochs")
        rows.append((label, m))
        print(f"  {label:<14} {m['recovery']:9.6f} {m['E_r']:8.5f} {m['coherent']:9.6f} "
              f"{m['mad']:9.6f} {m['rec_if_perfect_mean']:13.6f} "
              f"{m['rec_if_zero_dispersion']:10.6f}")
    print()
    print(f"  bar {BAR}. BOTH single-axis counterfactuals FAIL on every arm, so no one-axis remedy")
    print("  passes D2. In particular seed-ensembling can only reduce dispersion, so its ceiling is")
    print(f"  the 'zero disp' column -- {rows[0][1]['rec_if_zero_dispersion']:.4f} for ANY N.")
    need = m0["mad"] / RESID_OVER_GAP_MAX
    print(f"  and if dispersion fell like 1/sqrt(N) with perfectly independent seeds, reaching the "
          f"headroom needs N >= {need**2:.1f} -- while ALSO fixing the mean, which ensembling cannot.")
    print()
    print("  mean response required for the bar, against the dilution ideal by k:")
    for k, v in sorted(DILUTION_IDEAL_BY_K.items()):
        print(f"    k={k}: ideal mean response {v:.4f} -> zero-dispersion recovery {v:.4f} "
              f"{'PASS' if v >= BAR else 'FAIL'}")
    print(f"  no tabulated k reaches {BAR} even at zero dispersion; that is section 2's point, and it")
    print("  is unaffected by anything here.")

    if len(rows) >= 3:
        print()
        print("=== THE BUDGET LADDER: which term did more training actually move? ===")
        base = rows[1]
        for label, m in rows[2:]:
            b = base[1]
            print(f"  {base[0]} (ep{b['epochs']}) -> {label} (ep{m['epochs']}):")
            print(f"    recovery                   {b['recovery']:.6f} -> {m['recovery']:.6f} "
                  f"({100*(m['recovery']/b['recovery']-1):+.2f}%)")
            print(f"    mean response E_w[r]       {b['E_r']:.5f} -> {m['E_r']:.5f} "
                  f"({m['E_r']-b['E_r']:+.5f})")
            print(f"    coherent under-application {b['coherent']:.6f} -> {m['coherent']:.6f} "
                  f"({100*(m['coherent']/b['coherent']-1):+.1f}%)")
            print(f"    dispersion, MAD            {b['mad']:.6f} -> {m['mad']:.6f} "
                  f"({100*(m['mad']/b['mad']-1):+.1f}%)")
            print(f"    published scatter penalty  {b['scatter_penalty']:.6f} -> "
                  f"{m['scatter_penalty']:.6f} ({100*(m['scatter_penalty']/b['scatter_penalty']-1):+.1f}%)")
        print()
        print("  NOTE the last two lines disagree violently in magnitude. The penalty is not a")
        print("  dispersion measure: it depends on how many cells' responses straddle r=1, so it can")
        print("  collapse while the actual spread barely moves. A ladder 'read on the scatter axis'")
        print("  via the penalty would report a large win that the MAD says did not happen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
