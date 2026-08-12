#!/usr/bin/env python3
"""Do the nominal's fold-forward deficit and the D2 dispersion share a cause? Test: acceptance.

Two independent failures are on the table and nobody knows whether they are one problem:

  * the nominal's folded-forward ratio is 0.7465 where the identity requires R = 1.1241, with the
    deficit carried by a low tail -- 24% of pass_reco rows holding 26% of reco weight at mean push
    0.2254;
  * the D2 powered closure misses by per-cell DISPERSION that reproduces to r = 0.99994 across runs,
    so it is deterministic structure rather than noise.

If the suppressed push mass sits in LOW-ACCEPTANCE cells, both are the same acceptance-driven story and
should be fixed together. If push is uncorrelated with acceptance, they are separate problems and
chasing one will not move the other. That is worth knowing before anyone spends GPU on either.

Cheap and safe by construction: it joins three things already on disk -- the artifact's `weights_push`
and `mc_indices`, the dump's truth coordinates and `pass_reco`, and the committed per-cell acceptance
map -- with nothing but numpy. No inference, no GPU, so it cannot produce a plausible-but-wrong number
the way a reconstructed forward pass could.

Uses the SAME canonical grid and pt-major ravel order as the acceptance map and the closure reports, so
cell indices are directly comparable across all three.
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
#   1.0840529829474115  2026-08-10 annealed (now canonical by designation)
EXPECTED_FOLD_FORWARD = 0.7367462501305516


def _assert_artifact_identity(d, tol=1e-9):
    """Fail loudly if this is not the 08-08 artifact. A wrong number is worse than an exception."""
    got = float(d["fold_forward_sum_w_push_reco"]) / float(d["fold_forward_sum_w_reco"])
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
        w_reco = np.asarray(d["w_reco"], float)[imc]
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)[imc]

    pt_e = np.asarray(fe.CANONICAL_PT_EDGES, float)
    pp_e = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    n_pp = pp_e.size - 1
    m = json.load(open(AMAP))
    acc = np.asarray(m["acceptance_cells_pt_major"], float)

    # cell index on the canonical grid, pt-major row-major -- same order as the acceptance map
    ipt = np.clip(np.digitize(pt, pt_e) - 1, 0, pt_e.size - 2)
    ipp = np.clip(np.digitize(pp, pp_e) - 1, 0, n_pp - 1)
    cell = ipt * n_pp + ipp

    sel = pass_reco
    print(f"pass_reco rows {int(sel.sum())}   cells on grid {acc.size}")
    print()

    # per-cell reco-weighted mean push, over pass_reco only (the identity's domain)
    num = np.bincount(cell[sel], weights=(push * w_reco)[sel], minlength=acc.size)
    den = np.bincount(cell[sel], weights=w_reco[sel], minlength=acc.size)
    live = den > 0
    mean_push = np.full(acc.size, np.nan)
    mean_push[live] = num[live] / den[live]

    ok = live & np.isfinite(acc) & (acc > 0)
    print("=== do per-cell mean push and per-cell ACCEPTANCE co-vary? ===")
    print(f"  cells with both defined      {int(ok.sum())}")
    r_lin = float(np.corrcoef(acc[ok], mean_push[ok])[0, 1])
    # weight by reco weight too, since the identity is weighted
    wsum = den[ok]
    r_w = float(np.cov(np.vstack([acc[ok], mean_push[ok]]), aweights=wsum)[0, 1] /
                np.sqrt(np.cov(acc[ok], aweights=wsum) * np.cov(mean_push[ok], aweights=wsum)))
    print(f"  Pearson r(acceptance, mean push)          {r_lin:+.4f}")
    print(f"  reco-weight-weighted r                    {r_w:+.4f}")
    print()

    print("=== mean push by acceptance band (weighted by reco weight) ===")
    bands = [(0.0, 0.01), (0.01, 0.05), (0.05, 0.20), (0.20, 0.40),
             (0.40, 0.60), (0.60, 0.80), (0.80, 1.01)]
    print(f"  {'band':>12s} {'cells':>6s} {'reco wt %':>10s} {'mean push':>10s}")
    tot = den[ok].sum()
    for lo, hi in bands:
        b = ok & (acc >= lo) & (acc < hi)
        if not b.any():
            continue
        mp = float(num[b].sum() / den[b].sum())
        print(f"  [{lo:.2f},{hi:.2f}) {int(b.sum()):6d} {100*den[b].sum()/tot:9.2f}% {mp:10.4f}")
    print()
    print(f"  required weighted mean over all cells: R = {R:.6f}")
    print(f"  achieved                               {float(num[ok].sum()/den[ok].sum()):.6f}")
    print()
    print("=== interpretation guide ===")
    print("  strong POSITIVE r  -> low-acceptance cells are the suppressed ones; the fold-forward")
    print("                        deficit and the D2 dispersion are the same acceptance story.")
    print("  r near 0           -> push suppression is NOT acceptance-driven; two separate problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
