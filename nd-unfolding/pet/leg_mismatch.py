#!/usr/bin/env python3
"""Is the fold-forward deficit a LEG MISMATCH rather than a step-1 failure? Free check, no inference.

Joseph's memo, item 1: step 2 trains `mc.weight*pass_gen` against `mc.weight*pull*pass_gen` -- the
TRUTH leg, deliberately `w_truth` (omnifold.py:210-213). The Gate-4 fold-forward evaluates push
weighted by `w_reco` over `pass_reco` (train_fullevent_nominal.py:461-462). D1 established the two
legs differ on all 20,573,521 rows. So step 2 guarantees a normalization under one functional while
the gate demands another, and the mismatch would be acceptance-structured because both the leg ratio
and the pass_reco n pass_gen overlap vary with acceptance -- which fits "worst at highest acceptance",
the one reading that inverts against every difficulty-based explanation.

If the TRUTH-leg mean is healthy and only the RECO-leg one is short, "step-1 under-achievement" is the
wrong hypothesis and the whole step-1 harness is unnecessary. That is why this runs first: it is the
only item on the list that can delete work rather than add it.

Everything here comes from stored arrays. Also settles, for free:
  * the memo's claim that stored push is EXACTLY 1.0 on truth-failing rows -- which is Gate B part
    (ii) in advance, and which my earlier push anatomy got the mask wrong on: I split on pass_reco,
    but the pinning is on pass_gen/pass_truth. Different masks, and the distinction matters.
  * the memo's point that the deficit is WORSE than 0.7465, because rows with push==1 that pass reco
    but fail truth pull the average UP. Computed directly AND via the memo's (0.7465-f)/(1-f), as a
    cross-check on both.
"""
import os
import sys

import numpy as np

ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
ART = os.path.join(ND, "pet/fullevent_nominal/pet_fullevent_nominal_weights.npz")
DUMP = os.path.join(ND, "g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
R = 1.1240802949941018


def wmean(x, w):
    return float((x * w).sum() / w.sum()) if w.sum() else float("nan")


def main():
    with np.load(ART, allow_pickle=True) as d:
        push = np.asarray(d["weights_push"], float)
        imc = np.asarray(d["mc_indices"])
    with np.load(DUMP, allow_pickle=True) as d:
        keys = set(d.files)
        gen_key = "pass_truth" if "pass_truth" in keys else "pass_gen"
        print(f"dump truth-acceptance key: {gen_key!r}   (pass_gen and pass_truth both checked)")
        w_truth = np.asarray(d["w_truth"], float)[imc]
        w_reco = np.asarray(d["w_reco"], float)[imc]
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)[imc]
        pass_gen = np.asarray(d[gen_key]).astype(bool)[imc]

    print(f"subsample {push.size}   pass_reco {int(pass_reco.sum())}   "
          f"{gen_key} {int(pass_gen.sum())}   both {int((pass_reco & pass_gen).sum())}")
    print()

    print("=== THE COMPARISON: which leg is short? ===")
    truth_leg = wmean(push[pass_gen], w_truth[pass_gen])
    reco_leg = wmean(push[pass_reco], w_reco[pass_reco])
    print(f"  mean_w_truth(push | {gen_key})   = {truth_leg:.6f}   dev vs R = {abs(truth_leg/R-1):.6f}")
    print(f"  mean_w_reco (push | pass_reco)  = {reco_leg:.6f}   dev vs R = {abs(reco_leg/R-1):.6f}")
    print(f"  ratio truth-leg / reco-leg      = {truth_leg/reco_leg:.6f}")
    print()
    print("  READING (predeclared before running, per BEN-038):")
    print("    truth leg near 1.0 and reco leg short -> step 2 normalised the TRUTH functional;")
    print("      the gate demands the RECO one. Leg mismatch, NOT step-1 under-achievement.")
    print("    both short by the same amount -> the deficit is upstream of the leg choice;")
    print("      the step-1 harness is still needed.")
    print()

    print("=== is stored push EXACTLY 1.0 on truth-failing rows? (Gate B part ii, in advance) ===")
    off = push[~pass_gen]
    print(f"  ~{gen_key} rows            {off.size}")
    print(f"  exactly == 1.0             {int((off == 1.0).sum())}  "
          f"({100.0*(off == 1.0).mean() if off.size else float('nan'):.2f}%)")
    if off.size:
        print(f"  max |push-1| off-truth     {np.abs(off - 1.0).max():.3e}")
    print()

    print("=== the deficit is worse than 0.7465: strip the push==1 passengers ===")
    both = pass_reco & pass_gen
    reco_only = pass_reco & ~pass_gen
    f = float(w_reco[reco_only].sum() / w_reco[pass_reco].sum())
    direct = wmean(push[both], w_reco[both])
    formula = (reco_leg - f) / (1.0 - f) if f < 1 else float("nan")
    print(f"  f = w_reco share of pass_reco rows failing truth   {f:.6f}")
    print(f"  truth-passing subset ratio, computed DIRECTLY      {direct:.6f}")
    print(f"  same via the memo's (ratio - f)/(1 - f)            {formula:.6f}")
    print(f"  agreement                                          {abs(direct-formula):.3e}")
    print(f"  so on the rows step 2 actually fits, the mean push is {direct:.4f} against R={R:.4f}")
    print(f"  dev vs R                                           {abs(direct/R-1):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
