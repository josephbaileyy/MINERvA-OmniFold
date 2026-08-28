#!/usr/bin/env python3
"""D2 ACCEPTANCE-LIMITED oracle: the best recovery an estimator can reach when reco-space information
reaches each truth cell only through that cell's acceptance.

WHY THIS AND NOT `d2_oracle.py`. `d2_oracle.py` (151db63) scores a perfect estimator that reproduces the
injected shape on half B exactly, and gets 0.9542 against the 0.80 bar. It states its own limit in §"Limit"
and that limit is the whole reason this file exists: **it bounds recovery given SAMPLING only.** It says
nothing about whether a real estimator can reach 0.80 given that most truth cells are observed in reco only
fractionally. Joseph's framing, 2026-08-07: ~0.63 here means the 0.80 bar was specified without accounting
for dilution -- a specification finding -- and ~0.9 means the estimator is genuinely deficient.

THE CONSTRUCTION. OmniFold learns its reweighting in reco space (step 1) and transports it to truth space
(step 2). A truth cell `b` with acceptance `a_b` has only the fraction `a_b` of its events visible in reco,
so one iteration can correct at most that fraction and `(1 - a_b)` stays at the prior. After k iterations
the corrected fraction is the standard dilution response

    r_b = 1 - (1 - a_b)^k

and an estimator limited by exactly that, and by nothing else, applies per EVENT

    push_event = 1 + r_{cell(event)} * (tilt_event - 1)

i.e. the right correction, attenuated per cell by how much of that cell reco can actually see. Scoring that
through the criterion code UNMODIFIED gives the acceptance-limited ceiling *in the criterion's own units*,
including its per-cell absolute value and the A/B sampling difference -- none of which a mean-response
number like 0.63321 carries.

WHAT THIS IS NOT, stated up front because BEN-038 already refuted the strong version. `(1 - a_b)^k` assumes
step 2 resolves cells INDEPENDENTLY. `omnifold.py:218-220` evaluates the truth classifier on all `pass_gen`
rows, so a smooth learner can transport the injected `f(pT)` from high-acceptance cells into low-acceptance
ones and BEAT this curve; BEN-038 measured the top acceptance band overshooting at `E_w[r] = 1.0333`. So
this is a REFERENCE CURVE, not a proof of impossibility. What makes it decision-relevant anyway is the
empirical bridge measured below: the real estimator's signed mean response sits *below* this curve, so no
net transport gain is occurring in practice.

VERIFICATION FIRST, because Joseph asked for his own comparison to be checked rather than taken from his
mail. Two things are checked before any oracle number prints:
  1. the reconstruction reproduces the committed report's gap/floor/residual/recovery (same gate as
     `d2_oracle.py`, same 1e-7 with the same justification, plus an EXACT population check);
  2. `E_w[r] = 0.63129` (BEN-038) and the dilution ideal `E_w[1-(1-a_b)^k] = 0.63321` are recomputed here
     from the artifact and the committed acceptance map. **The weighting is load-bearing and the map carries
     two of them:** `ideal_recovery_percell_truthmass_weighted_by_k` is TRUTH-MASS weighted (0.6095 at k=3,
     the CLM-011 number) while BEN-038's 0.63321 is TILT weighted. Comparing across weightings would be
     meaningless, so both are printed and the one that matches BEN-038 is identified rather than assumed.

Same footing as `d2_oracle.py`: halves from the artifact's own `dump_rows_a`/`dump_rows_b`, so no loader
re-run and no subsample-seed reproduction risk; criterion functions imported, never reimplemented.
"""
import json
import os
import sys

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))
PC = os.path.join(ND, "pet/powered_closure")
ART = os.path.join(PC, "POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz")
REP = os.path.join(PC, "POWERED_CLOSURE_REPORT.slurm-56381674.json")
AMAP = os.path.join(ND, "products/pet/fullevent_fps/acceptance_map_fullevent_fps.json")
DUMP = os.path.join(ND, "g2_fullevent/input/G2_FPS_MEFHC_P12.npz")

import closure_powered_truth_reweight as C  # noqa: E402  the criterion code, UNMODIFIED
import fullevent_fps_dataloader as fe       # noqa: E402

BAR = 0.80
PUB_E_R = 0.63129        # BEN-038 signed mean response
PUB_IDEAL_K3 = 0.63321   # BEN-038 dilution ideal, tilt-weighted
NITER = 3


def response_split(P, T, U, cut=0.0):
    """BEN-038's decomposition. w_b = |T-P|, r_b = (U-P)/(T-P), all weight-normalised."""
    disp = T - P
    live = np.abs(disp) > cut
    w = np.abs(disp[live])
    ww = w / w.sum()
    r = (U[live] - P[live]) / disp[live]
    x = 1.0 - r
    E_r = float((ww * r).sum())
    E_abs = float((ww * np.abs(x)).sum())
    return {"live": int(live.sum()), "E_r": E_r, "E_abs": E_abs, "recovery": 1.0 - E_abs,
            "coherent": abs(1.0 - E_r), "mad": float((ww * np.abs(x - (1.0 - E_r))).sum()),
            "overshoot": int((r > 1.0).sum()), "mask": live, "w": w, "ww": ww, "r": r}


def main():
    rep = json.load(open(REP))
    inj, met = rep["injection"], rep["metrics"]
    e_pt = np.asarray(rep["edges_pt"], float)
    e_pp = np.asarray(rep["edges_pparallel"], float)
    n_i, n_j = e_pt.size - 1, e_pp.size - 1

    with np.load(ART, allow_pickle=True) as d:
        ra = np.asarray(d["dump_rows_a"]).astype(np.int64)
        rb = np.asarray(d["dump_rows_b"]).astype(np.int64)
        push = np.asarray(d["weights_push"], float)

    with np.load(DUMP, allow_pickle=True) as d:
        ts = np.asarray(d["truth_scalars"], np.float64)
        pt_all = ts[:, fe.SCALAR_COLS["pt"]]
        pp_all = ts[:, fe.SCALAR_COLS["pparallel"]]
        del ts
        w_all = np.asarray(d["w_truth"], np.float64)
        pg_all = np.asarray(d["pass_truth"]).astype(bool)

    ptA, ppA, wA, mA = pt_all[ra], pp_all[ra], w_all[ra], pg_all[ra]
    ptB, ppB, wB, mB = pt_all[rb], pp_all[rb], w_all[rb], pg_all[rb]

    tilt_A = np.ones(ra.size)
    t_on, _ = C.clipped_exponential_tilt(ptA[mA], amplitude=float(inj["amplitude"]),
                                         clip_z=float(inj["clip_z"]))
    tilt_A[mA] = t_on

    h_prior = C.unit_spectrum(ptB[mB], ppB[mB], wB[mB], e_pt, e_pp)
    h_target = C.unit_spectrum(ptA[mA], ppA[mA], (wA * tilt_A)[mA], e_pt, e_pp)
    h_untilt = C.unit_spectrum(ptA[mA], ppA[mA], wA[mA], e_pt, e_pp)
    h_unfold = C.unit_spectrum(ptB[mB], ppB[mB], (wB * push)[mB], e_pt, e_pp)
    gap, floor, residual = C.l1(h_prior, h_target), C.l1(h_prior, h_untilt), C.l1(h_unfold, h_target)

    # ---------------- GATE 1: the reconstruction ------------------------------------------------
    print("=== GATE 1: reconstruction must match the committed report ===")
    TOL = 1e-7          # same threshold and same justification as d2_oracle.py; see its header
    n_a_rep, n_b_rep = rep["samples"].get("n_truth_a"), rep["samples"].get("n_truth_b")
    if n_a_rep is not None and (int(mA.sum()) != int(n_a_rep) or int(mB.sum()) != int(n_b_rep)):
        raise SystemExit(f"[acc-oracle] truth-passing counts {(int(mA.sum()), int(mB.sum()))} != report "
                         f"{(n_a_rep, n_b_rep)} -- wrong halves or mask (fail closed, no tolerance)")
    print(f"  population EXACT: A {int(mA.sum())} B {int(mB.sum())} == report ({n_a_rep}, {n_b_rep})")
    ok = True
    for name, mine, theirs in (("gap", gap, met["gap"]), ("floor", floor, met["floor"]),
                               ("residual", residual, met["residual"]),
                               ("recovery", 1 - residual / gap, met["recovery"])):
        rel = abs(mine - theirs) / max(abs(theirs), 1e-300)
        ok &= rel < TOL
        print(f"  {name:9s} mine {mine:.12f}  report {theirs:.12f}  rel {rel:.2e} "
              f"{'OK' if rel < TOL else '*** MISMATCH ***'}")
    if not ok:
        raise SystemExit("[acc-oracle] reconstruction does not reproduce the report; refusing to print "
                         "an oracle number built on it (fail closed)")

    # ---------------- GATE 2: verify Joseph's stated comparison ---------------------------------
    print()
    print("=== GATE 2: verify the 0.63129 vs 0.63321 comparison FROM THE ARTIFACTS ===")
    meas = response_split(h_prior, h_target, h_unfold)
    print(f"  E_w[r] measured here        {meas['E_r']:.6f}   BEN-038 published {PUB_E_R}")
    e_r_ok = abs(meas["E_r"] - PUB_E_R) <= 5e-4
    print(f"    -> {'MATCHES' if e_r_ok else '*** DOES NOT MATCH ***'}  "
          f"(live bins {meas['live']}, overshoot {meas['overshoot']})")

    amap = json.load(open(AMAP))
    if amap["bin_order"] != rep["bin_order"]:
        raise SystemExit(f"[acc-oracle] acceptance map bin_order {amap['bin_order']!r} != report "
                         f"{rep['bin_order']!r} (fail closed)")
    a_b = np.asarray(amap["acceptance_cells_pt_major"], float)
    if a_b.size != h_prior.size:
        raise SystemExit(f"[acc-oracle] acceptance map has {a_b.size} cells, spectra have {h_prior.size}")
    a_safe = np.where(np.isfinite(a_b), np.clip(a_b, 0.0, 1.0), 0.0)
    r_dil = 1.0 - (1.0 - a_safe) ** NITER

    # the two weightings the map itself distinguishes -- do NOT mix them
    live = meas["mask"]
    ww = meas["ww"]
    ideal_tilt = float((ww * r_dil[live]).sum())
    tm = np.asarray(amap["truth_mass_cells_pt_major"], float)
    tm_live = tm[live]
    ideal_tm = float((tm_live * r_dil[live]).sum() / tm_live.sum())
    pub_tm = amap["ideal_recovery_percell_truthmass_weighted_by_k"].get(str(NITER))
    print(f"  dilution ideal, TILT-weighted (BEN-038's weighting)   {ideal_tilt:.6f}   "
          f"published {PUB_IDEAL_K3}")
    ideal_ok = abs(ideal_tilt - PUB_IDEAL_K3) <= 5e-4
    print(f"    -> {'MATCHES' if ideal_ok else '*** DOES NOT MATCH ***'}")
    print(f"  dilution ideal, TRUTH-MASS weighted (the CLM-011 curve) {ideal_tm:.6f}   "
          f"map says {pub_tm}")
    print(f"  bias, measured minus ideal (tilt-weighted)            {meas['E_r']-ideal_tilt:+.6f}   "
          f"Joseph's mail said -0.0019")
    print(f"  -> the two weightings differ by {abs(ideal_tilt-ideal_tm):.4f}; quoting one against the "
          f"other would be a {100*abs(ideal_tilt-ideal_tm)/ideal_tilt:.1f}% error")
    if not (e_r_ok and ideal_ok):
        raise SystemExit("[acc-oracle] could not reproduce the published comparison; the oracle below "
                         "would be describing different objects (fail closed)")
    print("  BOTH reproduced. Joseph's description of the comparison is confirmed against the artifacts.")

    # ---------------- THE ACCEPTANCE-LIMITED ORACLE ---------------------------------------------
    print()
    print("=== ACCEPTANCE-LIMITED ORACLE, criterion code UNMODIFIED ===")
    tilt_B = np.ones(rb.size)
    tB, _ = C.clipped_exponential_tilt(ptB[mB], amplitude=float(inj["amplitude"]),
                                       clip_z=float(inj["clip_z"]))
    tilt_B[mB] = tB

    iptB = np.clip(np.digitize(ptB, e_pt) - 1, 0, n_i - 1)
    ippB = np.clip(np.digitize(ppB, e_pp) - 1, 0, n_j - 1)
    cellB = iptB * n_j + ippB

    print(f"  {'k':>2} {'oracle recovery':>16} {'E_w[r]':>9} {'coherent':>9} {'MAD':>9} "
          f"{'vs bar':>8}")
    out = {}
    for k in (1, 2, 3, 4, 5, 6):
        r_k = 1.0 - (1.0 - a_safe) ** k
        push_or = 1.0 + r_k[cellB] * (tilt_B - 1.0)
        h_or = C.unit_spectrum(ptB[mB], ppB[mB], (wB * push_or)[mB], e_pt, e_pp)
        rec_or = 1.0 - C.l1(h_or, h_target) / gap
        sp = response_split(h_prior, h_target, h_or)
        out[k] = (rec_or, sp)
        print(f"  {k:>2} {rec_or:16.6f} {sp['E_r']:9.5f} {sp['coherent']:9.6f} {sp['mad']:9.6f} "
              f"{'PASS' if rec_or >= BAR else 'FAIL':>8}")

    # ---- BRACKET: the same limit built in SPECTRUM space, with no sampling term ---------------
    # The per-event construction above goes through `unit_spectrum` and therefore pays the A/B
    # sampling difference, exactly as the criterion does for the real estimator. The spectrum-space
    # version applies the same per-cell response directly to the histograms, so it is sampling-free.
    # Reporting BOTH brackets the ceiling instead of resting the conclusion on one construction, and
    # their difference IS the sampling+within-cell term rather than an unexplained residual.
    print()
    print("=== BRACKET: spectrum-space (sampling-free) vs per-event (pays A/B sampling) ===")
    print(f"  {'k':>2} {'per-event':>12} {'spectrum-space':>16} {'difference':>12}")
    for k in (2, 3, 4):
        r_k = 1.0 - (1.0 - a_safe) ** k
        h_sp = h_prior + r_k * (h_target - h_prior)
        rec_sp = 1.0 - C.l1(h_sp, h_target) / gap
        print(f"  {k:>2} {out[k][0]:12.6f} {rec_sp:16.6f} {rec_sp-out[k][0]:12.6f}")
        if k == NITER:
            rec_sp3 = rec_sp
    print(f"  the spectrum-space value at k={NITER} is {rec_sp3:.6f}; it equals the tilt-weighted mean")
    print(f"  response {ideal_tilt:.6f} to {abs(rec_sp3-ideal_tilt):.1e}, which is the algebraic check that")
    print("  the |.| penalty is INERT on a one-sided response (r_b <= 1 for all b, so |1-r|=1-r).")

    rec3, sp3 = out[NITER]
    print()
    print(f"=== VERDICT at the nominal k={NITER} ===")
    print(f"  acceptance-limited oracle recovery   {rec3:.6f}   (per-event, pays sampling)")
    print(f"                          bracketed by {rec_sp3:.6f}   (spectrum-space, sampling-free)")
    print(f"  the bar                              {BAR}")
    print("  statistical oracle (151db63)          0.954204   <- sampling only")
    print(f"  measured estimator                    {met['recovery']:.6f}")
    frac = met["recovery"] / rec3
    print()
    print("  DECOMPOSITION OF THE 0.80 SHORTFALL:")
    tot = BAR - met["recovery"]
    spec = BAR - rec3
    est = rec3 - met["recovery"]
    print(f"    total   0.80 - {met['recovery']:.4f} = {tot:.4f}")
    print(f"    SPECIFICATION  0.80 - {rec3:.4f} = {spec:.4f}  ({100*spec/tot:.1f}% of it) "
          f"<- no estimator choice removes this")
    print(f"    ESTIMATOR      {rec3:.4f} - {met['recovery']:.4f} = {est:.4f}  ({100*est/tot:.1f}%)")
    print(f"    so the estimator reaches {100*frac:.1f}% of the ceiling acceptance permits")
    print(f"  dilution ideal (mean response)        {ideal_tilt:.6f}")
    if rec3 < BAR:
        print("  -> the bar sits ABOVE what an estimator limited only by acceptance can reach.")
        print("     The 0.80 bar was specified without accounting for dilution. That is a")
        print("     SPECIFICATION finding, not a tolerance question.")
    else:
        print("  -> acceptance does NOT explain the shortfall; the estimator is genuinely deficient.")

    print()
    print("=== THE EMPIRICAL BRIDGE: is cross-cell transport actually helping? ===")
    print("  This oracle assumes cells resolve INDEPENDENTLY, which omnifold.py:218-220 lets a smooth")
    print("  learner beat -- so it is a reference curve, not a proof of impossibility (BEN-038).")
    print(f"  But the real estimator's mean response is {meas['E_r']:.5f} against the curve's "
          f"{ideal_tilt:.5f},")
    print(f"  i.e. {meas['E_r']-ideal_tilt:+.5f}. The estimator is BELOW the curve, so no NET transport")
    print("  gain is occurring; the curve is where this estimator actually operates, not a hypothetical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
