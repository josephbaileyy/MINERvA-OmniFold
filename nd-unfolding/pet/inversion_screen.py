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
# OI-136: root derived from __file__, never the hardcoded cluster root
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_CODE_ROOT, "nd-unfolding", "pet"))
import fullevent_fps_dataloader as fe  # noqa: E402

ART = os.path.join(ND, "pet/fullevent_nominal/pet_fullevent_nominal_weights.npz")
DUMP = os.path.join(ND, "g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
AMAP = os.path.join(ND, "products/pet/fullevent_fps/acceptance_map_fullevent_fps.json")
R = 1.1240802949941018

# --- CLASS-5 RUNTIME IDENTITY GUARD (added 2026-08-12) -------------------------------------------
# This diagnostic is ABOUT the 2026-08-08 artifact and was deliberately NOT retargeted when job
# 56563761 was promoted by designation. `canonical` no longer means "whatever is at
# fullevent_nominal/", so a path alone no longer proves which estimator this is reading.  # NS-EXEMPT: prose
#
# No source-text checker can catch the way this breaks: the artifact's own inference_contract carries
# ABSOLUTE checkpoint paths written at training time and read back at inference time, so a relocated
# or swapped artifact resolves silently to a different network (BEN-133; live instance in
# fullevent_nominal/superseded-20260806/NOTE.md). The mitigation is to assert the artifact's IDENTITY  # NS-EXEMPT: prose
# from its own contents before use, which is cheap and fails LOUDLY.
#
# Fold-forward fingerprints, all measured 2026-08-11/12:
#   0.7367462501305516  2026-08-08 canonical-at-the-time  <- what this diagnostic requires
#   0.7464834064182863  2026-08-06 superseded
#   1.0840529523112135  2026-08-10 annealed (now canonical by designation)
#
# OI-82 RESOLVED 2026-08-17 (lane E). This line read 1.0840529829474115 until now -- a THIRD value
# for the annealed ratio, 3.064e-8 from both committed measurements, i.e. 2,070x further away than
# they are from each other and 30.6x this file's own tol=1e-9. It was NOT a measurement of another
# artifact. Recomputed from the annealed NPZ's own stored fields on a login node, per the item's
# prescribed close (sha256 559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e):
#     fold_forward_sum_w_push_reco = 1084052.9829474115
#     fold_forward_sum_w_reco      = 1000000.0282607947
#     ratio                        = 1.0840529523112135   == the production 56563761 receipt, exactly
# The old value is that NUMERATOR over a ROUNDED denominator: 1084052.9829474115 / 1e6 reproduces
# 1.0840529829474115 bit-for-bit, and 1e6 vs 1000000.0282607947 is 2.826e-8 relative -- which is the
# 3.064e-8 gap to the last digit. So the operator-facing reference was an arithmetic slip, not a
# disagreement between artifacts, and correcting it removes a number rather than adding a fourth.
EXPECTED_FOLD_FORWARD = 0.7367462501305516


def _assert_artifact_identity(d, tol=1e-9):
    """Fail loudly if this is not the 08-08 artifact. A wrong number is worse than an exception."""
    # REFUSE, DO NOT TRACEBACK, when the fields are absent or unusable (added 2026-08-14, BEN-244).
    # A missing field is a SCHEMA difference, not a typo: lane C measured that the pre-anneal and
    # annealed artifacts differ by schema and not merely by field value, so "no fold-forward fields"
    # is a real artifact this guard can be handed. A KeyError from inside a guard reports the
    # DIAGNOSTIC as broken; an unverifiable artifact must report the ARTIFACT as unverifiable.
    try:
        _num = float(d["fold_forward_sum_w_push_reco"])
        _den = float(d["fold_forward_sum_w_reco"])
    except KeyError as exc:
        raise SystemExit(
            f"[identity] REFUSING TO RUN: the loaded artifact carries no {exc.args[0]!r}, so its "
            f"identity cannot be asserted from its own contents. An artifact whose identity cannot "
            f"be established is refused, not assumed.\n"
            f"           artifact: {ART}")
    if _den == 0.0:
        raise SystemExit(
            f"[identity] REFUSING TO RUN: fold_forward_sum_w_reco is zero, so the fold-forward ratio "
            f"is undefined and identity cannot be asserted.\n"
            f"           artifact: {ART}")
    got = _num / _den
    if abs(got - EXPECTED_FOLD_FORWARD) > tol:
        raise SystemExit(
            f"[identity] REFUSING TO RUN: this diagnostic is about the 2026-08-08 artifact "
            f"(fold-forward {EXPECTED_FOLD_FORWARD!r}) but the loaded artifact has {got!r}.\n"
            f"           artifact: {ART}\n"
            f"           0.746483 = 08-06 superseded; 1.084053 = 08-10 annealed (canonical by "
            f"designation since 2026-08-12).\n"
            f"           If retargeting this diagnostic is intended, that is a decision with a "
            f"disposition in check_canonical_designation.py, not an edit.")
    return got



def main():
    with np.load(ART, allow_pickle=True) as d:
        _assert_artifact_identity(d)
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
