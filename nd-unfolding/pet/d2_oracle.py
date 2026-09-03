#!/usr/bin/env python3
"""D2 statistical oracle: score a KNOWN-PERFECT estimator with the criterion code unmodified.

Joseph's memo, item 2. Changing 0.80 because we measured 0.5469 is tolerance-fitting. Proving the bar
sits above the metric's own CEILING is a specification bug report. The oracle gets the second for free.

CONSTRUCTION, read off closure_powered_truth_reweight.py:338-344 rather than assumed:
    h_prior  = unit_spectrum(B, w_truth)              gap      = l1(h_prior, h_target)
    h_target = unit_spectrum(A, w_truth * tilt_a)     floor    = l1(h_prior, h_untilt)
    h_unfold = unit_spectrum(B, w_truth * push)       residual = l1(h_unfold, h_target)
    h_untilt = unit_spectrum(A, w_truth)              recovery = 1 - residual/gap
with masks ma = pass_gen[A], mb = pass_gen[B].

A PERFECT estimator pushes half B to exactly the injected shape, so its h_unfold is
unit_spectrum(B, w_truth * tilt_b). Then residual is the pure A/B SAMPLING difference at the TILTED
operating point, and 1 - that/gap is the highest recovery any estimator can achieve.

  oracle recovery <  0.80  =>  D2 is unpassable by ANY estimator. Not tolerance-raising: a fact.
  oracle recovery >= 0.80  =>  the estimator really is short and the redesign argument dies free.

It also measures the memo's defect (a) directly: `floor` is the A/B difference measured UNTILTED,
while `residual` is measured TILTED, so floor/gap <= 0.10 under-bounds the thing it exists to bound.
The oracle residual IS the tilted counterpart, so oracle_residual/floor is that understatement.

TWO CHOICES I REFUSE TO MAKE SILENTLY. "The same tilt applied to B" is ambiguous: the tilt's quantiles
and its mean-normalisation are taken over the rows it is applied to (:116-128). So variant 1 recomputes
the tilt on B's own truth-passing rows through the UNMODIFIED function; variant 2 freezes A's quantiles
(from the report's injection block) and applies them to B's pt. Both are reported. If they agree, the
choice does not matter and the conclusion is robust to it.

NO LOADER RE-RUN. The artifact stores dump_rows_a/dump_rows_b (:351), so the exact halves come from
disk rather than from reproducing a subsample seed. And before trusting any of it, the script REBUILDS
gap/floor/residual and asserts they match the committed report -- if the reconstruction is wrong, that
check fails and the oracle number is never printed.
"""
import json
import os
import sys

import numpy as np

ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
# OI-136: root derived from __file__, never the hardcoded cluster root
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_CODE_ROOT, "nd-unfolding", "pet"))
PC = os.path.join(ND, "pet/powered_closure")
ART = os.path.join(PC, "POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz")
REP = os.path.join(PC, "POWERED_CLOSURE_REPORT.slurm-56381674.json")
DUMP = os.path.join(ND, "g2_fullevent/input/G2_FPS_MEFHC_P12.npz")

import closure_powered_truth_reweight as C  # noqa: E402  the criterion code, UNMODIFIED
import fullevent_fps_dataloader as fe       # noqa: E402


def main():
    rep = json.load(open(REP))
    inj, met = rep["injection"], rep["metrics"]
    e_pt = np.asarray(rep["edges_pt"], float)
    e_pp = np.asarray(rep["edges_pparallel"], float)

    with np.load(ART, allow_pickle=True) as d:
        ra = np.asarray(d["dump_rows_a"]).astype(np.int64)
        rb = np.asarray(d["dump_rows_b"]).astype(np.int64)
        push = np.asarray(d["weights_push"], float)
    print(f"halves from the artifact: A {ra.size} rows, B {rb.size} rows, push {push.shape}")

    with np.load(DUMP, allow_pickle=True) as d:
        ts = np.asarray(d["truth_scalars"], np.float64)
        pt_all = ts[:, fe.SCALAR_COLS["pt"]]
        pp_all = ts[:, fe.SCALAR_COLS["pparallel"]]
        del ts
        w_all = np.asarray(d["w_truth"], np.float64)
        pg_all = np.asarray(d["pass_truth"]).astype(bool)

    ptA, ppA, wA, mA = pt_all[ra], pp_all[ra], w_all[ra], pg_all[ra]
    ptB, ppB, wB, mB = pt_all[rb], pp_all[rb], w_all[rb], pg_all[rb]
    print(f"truth-passing: A {int(mA.sum())}  B {int(mB.sum())}   "
          f"report says A {rep['samples'].get('n_truth_a')} B {rep['samples'].get('n_truth_b')}")

    # --- the injection on A, exactly as the driver builds it (:288-292) -------------------
    tilt_A = np.ones(ra.size)
    t_on, spec = C.clipped_exponential_tilt(ptA[mA], amplitude=float(inj["amplitude"]),
                                            clip_z=float(inj["clip_z"]))
    tilt_A[mA] = t_on

    h_prior = C.unit_spectrum(ptB[mB], ppB[mB], wB[mB], e_pt, e_pp)
    h_target = C.unit_spectrum(ptA[mA], ppA[mA], (wA * tilt_A)[mA], e_pt, e_pp)
    h_untilt = C.unit_spectrum(ptA[mA], ppA[mA], wA[mA], e_pt, e_pp)
    h_unfold = C.unit_spectrum(ptB[mB], ppB[mB], (wB * push)[mB], e_pt, e_pp)

    gap, floor, residual = C.l1(h_prior, h_target), C.l1(h_prior, h_untilt), C.l1(h_unfold, h_target)

    print()
    print("=== GATE ON MY OWN RECONSTRUCTION (must match the committed report) ===")
    # Threshold 1e-7, and the justification matters because the memo rightly forbids reconciling a
    # gate by loosening it. That warning is about Gate B, whose 1e-6 is justified by the failure mode
    # it guards: a wrong z-score moves logits by ORDER UNITY. This gate compares a SUM OF 285 float64
    # absolute differences of ~1e-2 quantities, where the failure mode -- wrong halves, wrong masks,
    # wrong weight leg -- would shift the result by 1e-2 to 1, not by 1e-9. At 1e-7 the gate keeps
    # five orders of margin against what it exists to catch while not failing on summation noise.
    # An initial 1e-9 fired on floor at 2.17e-09, which is accumulation noise, not a defect.
    # The population check below is the structural half and is EXACT, not toleranced.
    TOL = 1e-7
    n_a_rep, n_b_rep = rep["samples"].get("n_truth_a"), rep["samples"].get("n_truth_b")
    if n_a_rep is not None and (int(mA.sum()) != int(n_a_rep) or int(mB.sum()) != int(n_b_rep)):
        raise SystemExit(f"[oracle] truth-passing counts differ from the report "
                         f"({int(mA.sum())},{int(mB.sum())}) vs ({n_a_rep},{n_b_rep}) -- wrong "
                         f"halves or mask (fail closed, no tolerance)")
    print(f"  population check EXACT: truth-passing A {int(mA.sum())} B {int(mB.sum())} "
          f"== report ({n_a_rep}, {n_b_rep})")
    ok = True
    for name, mine, theirs in (("gap", gap, met["gap"]), ("floor", floor, met["floor"]),
                               ("residual", residual, met["residual"]),
                               ("recovery", 1 - residual / gap, met["recovery"])):
        rel = abs(mine - theirs) / max(abs(theirs), 1e-300)
        flag = "OK" if rel < TOL else "*** MISMATCH ***"
        if rel >= TOL:
            ok = False
        print(f"  {name:9s} mine {mine:.12f}   report {theirs:.12f}   rel {rel:.2e}  {flag}")
    if not ok:
        raise SystemExit("[oracle] reconstruction does NOT reproduce the report; refusing to print an "
                         "oracle number built on it (fail closed)")
    print("  reconstruction verified -- the oracle below is built on the same objects the gate scored.")
    print()

    # --- the oracle: a perfect estimator reproduces the injected shape on B ---------------
    print("=== ORACLE: known-perfect estimator, criterion code UNMODIFIED ===")
    results = {}

    tilt_B1 = np.ones(rb.size)
    tB1, specB = C.clipped_exponential_tilt(ptB[mB], amplitude=float(inj["amplitude"]),
                                            clip_z=float(inj["clip_z"]))
    tilt_B1[mB] = tB1
    results["variant 1: tilt recomputed on B"] = tilt_B1

    # variant 2: freeze A's quantiles, apply to B's pt, normalise over B's truth-passing rows
    p50, iqr = float(inj["pt_p50"]), float(inj["pt_iqr"])
    A_, Z_ = float(inj["amplitude"]), float(inj["clip_z"])
    u = np.clip((ptB[mB] - p50) / iqr, -Z_, Z_)
    raw = np.exp(A_ * u)
    tilt_B2 = np.ones(rb.size)
    tilt_B2[mB] = raw / raw.mean()
    results["variant 2: A's quantiles on B"] = tilt_B2

    for label, tB in results.items():
        h_or = C.unit_spectrum(ptB[mB], ppB[mB], (wB * tB)[mB], e_pt, e_pp)
        res_or = C.l1(h_or, h_target)
        rec_or = 1 - res_or / gap
        verdict = ("UNPASSABLE BY ANY ESTIMATOR" if rec_or < 0.80
                   else "criterion is achievable; the estimator is short")
        print(f"  {label}")
        print(f"    oracle residual {res_or:.6f}   oracle recovery {rec_or:.6f}   vs bar 0.80")
        print(f"    -> {verdict}")

    print()
    print("=== memo defect (a): floor is measured UNTILTED, residual TILTED ===")
    h_or = C.unit_spectrum(ptB[mB], ppB[mB], (wB * tilt_B1)[mB], e_pt, e_pp)
    res_or = C.l1(h_or, h_target)
    print(f"  floor (A/B, untilted)          {floor:.6f}   floor/gap {floor/gap:.6f} vs bar 0.10")
    print(f"  oracle residual (A/B, tilted)  {res_or:.6f}   /gap      {res_or/gap:.6f}")
    print(f"  understatement factor          {res_or/floor:.3f}x")
    print(f"  measured residual              {residual:.6f}   of which sampling is "
          f"{100.0*res_or/residual:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
