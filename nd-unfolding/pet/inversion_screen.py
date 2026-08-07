#!/usr/bin/env python3
"""Plausibility screen on the inverted-correction hypothesis. NOT a proof either way -- read the caveat.

The nominal's folded-forward ratio is 0.7465 where the identity requires R = 1.1241, and the deficit is
monotonic in acceptance, worst (0.518) in the best-measured cells. That is the shape an inverted
correction would make: where acceptance is high step 1 discriminates most and applies the largest
correction, so a wrong sense hurts most there and fades toward prior-dominated cells.

WHY THIS IS A SCREEN AND NOT A PROOF, stated up front because it limits what any result here means.
`weights_push` is a PRODUCT over three iterations, and step 2 is a regression that pins off-acceptance
rows. So an inverted step-1 likelihood ratio does NOT propagate to `1/push` by algebra -- the pull step
would not invert consistently. None of the candidates below is the exact algebraic inverse of anything.
A candidate landing on R is therefore SUGGESTIVE, not conclusive; and none landing near R weakens the
hypothesis without killing it.

Testing a FAMILY rather than one form on purpose. Picking a single inversion and finding it reproduces R
would be the easiest way to manufacture a clean-looking answer, so every candidate is reported and the
reader can see which, if any, is special.

All candidates are evaluated the way the gate evaluates the real one: reco-weighted mean over pass_reco,
compared to R.
"""
import json
import os
import sys

import numpy as np

ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
sys.path.insert(0, os.path.join(ND, "pet"))
import fullevent_fps_dataloader as fe  # noqa: E402

ART = os.path.join(ND, "pet/fullevent_nominal/pet_fullevent_nominal_weights.npz")
DUMP = os.path.join(ND, "g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
AMAP = os.path.join(ND, "products/pet/fullevent_fps/acceptance_map_fullevent_fps.json")
R = 1.1240802949941018


def main():
    with np.load(ART, allow_pickle=True) as d:
        push = np.asarray(d["weights_push"], float)
        imc = np.asarray(d["mc_indices"])
    with np.load(DUMP, allow_pickle=True) as d:
        ts = np.asarray(d["truth_scalars"], np.float64)
        pt = ts[:, fe.SCALAR_COLS["pt"]][imc]
        pp = ts[:, fe.SCALAR_COLS["pparallel"]][imc]
        del ts
        w = np.asarray(d["w_reco"], float)[imc]
        pr = np.asarray(d["pass_reco"]).astype(bool)[imc]

    p, wr = push[pr], w[pr]
    eps = 1e-12
    cands = {
        "push (observed)": p,
        "1/push": 1.0 / np.maximum(p, eps),
        "2 - push": 2.0 - p,
        "R^2/push": R * R / np.maximum(p, eps),
        "R/push": R / np.maximum(p, eps),
        "push * R/mean": p * (R / float(np.average(p, weights=wr))),
    }
    print(f"pass_reco rows {p.size};  target R = {R:.6f}")
    print()
    print(f"  {'candidate':>18s} {'reco-wtd mean':>14s} {'dev vs R':>10s} {'p99':>10s} {'max':>12s}")
    for name, v in cands.items():
        m = float(np.average(v, weights=wr))
        print(f"  {name:>18s} {m:14.6f} {abs(m/R-1):10.4f} {np.percentile(v,99):10.4f} "
              f"{v.max():12.4g}")
    print()
    print("  note: 1/push and R^2/push are dominated by the small-push tail (min push 0.0432,")
    print("        so 1/push reaches ~23), which is itself diagnostic -- a naive inversion does not")
    print("        merely shift the mean, it produces a wildly heavy tail the data cannot support.")
    print()

    # Does any candidate FLATTEN the acceptance profile? That is the real question, since the
    # monotonic profile is the evidence -- a candidate that fixes the mean but keeps the slope has
    # not explained anything.
    pt_e = np.asarray(fe.CANONICAL_PT_EDGES, float)
    pp_e = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    n_pp = pp_e.size - 1
    acc = np.asarray(json.load(open(AMAP))["acceptance_cells_pt_major"], float)
    cell = (np.clip(np.digitize(pt, pt_e) - 1, 0, pt_e.size - 2) * n_pp
            + np.clip(np.digitize(pp, pp_e) - 1, 0, n_pp - 1))[pr]

    print("=== does any candidate remove the acceptance SLOPE? (the actual evidence) ===")
    print(f"  {'candidate':>18s} {'r(acc, mean)':>14s}   {'low-acc band':>13s} {'high-acc band':>14s}")
    for name, v in cands.items():
        num = np.bincount(cell, weights=v * wr, minlength=acc.size)
        den = np.bincount(cell, weights=wr, minlength=acc.size)
        ok = (den > 0) & np.isfinite(acc) & (acc > 0)
        mp = num[ok] / den[ok]
        r = float(np.corrcoef(acc[ok], mp)[0, 1])
        lo = ok & (acc < 0.2)
        hi = ok & (acc >= 0.8)
        lo_m = float(num[lo].sum() / den[lo].sum()) if lo.any() else float("nan")
        hi_m = float(num[hi].sum() / den[hi].sum()) if hi.any() else float("nan")
        print(f"  {name:>18s} {r:+14.4f}   {lo_m:13.4f} {hi_m:14.4f}")
    print()
    print("  A genuine explanation must put BOTH bands near R and flatten r toward 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
