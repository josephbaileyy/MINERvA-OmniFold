#!/usr/bin/env python3
"""Per-cell reco acceptance a_b for the full-event FPS grid, and the prior-weight table (1-a_b)^k.

WHY THIS EXISTS. Three separate open items were being argued from a single global acceptance number
(0.4186) when the quantity is strongly cell-dependent:

  * the D2 powered-closure criterion (`recovery >= 0.80`) was set without reference to what is
    achievable, and what is achievable is `1 - E_w[(1-a_b)^k]`, not `1 - (1-a_bar)^k`;
  * OPEN_ITEMS item (d), the niter=3 uncertainty budget, needs to know which cells are
    prior-dominated, because there the uncertainty is a model band and not a covariance;
  * OPEN_ITEMS item (e), the regularization justification, turns on whether more iterations can
    reach the low-acceptance cells at all -- and `(1-a_b)^k` says they cannot.

THE DECISION-RELEVANT NUMBER IS NOT THE ACCEPTANCE, IT IS `(1-a_b)^k`. OmniFold's step 2 pins
off-acceptance rows to exactly 1 (`omnifold_nn/omnifold/omnifold.py:218-220`), so in the
ideal-classifier limit `nu_k = (1-(1-a)^k) t + (1-a)^k * 1`. The coefficient `(1-a_b)^k` is therefore
the fraction of the answer in cell `b` that is **still the prior**, with no data correction at all.
That is the number a reader needs, and it is the number nothing in this repo recorded.

Also settles a disagreement: two independent reviews reported `a_b` for `p_parallel` 0.75-1.5 GeV as
0.012 and 0.00722. This script is the tiebreak, computed once and committed.

Definition, matching `extract_fullevent_fps.completeness_2d:390-404` exactly so the two cannot drift:
    a_b = sum(w_truth over pass_truth & pass_reco) / sum(w_truth over pass_truth)
NOTE that quantity is a reco EFFICIENCY. `KNOWN_ISSUES.md` records that the extractor wrongly divides
the cross section by it; this script computes it as a DIAGNOSTIC of where the estimator is blind, which
is a different use and is not affected by that defect.

Usage:  python3 nd-unfolding/pet/acceptance_map_fullevent_fps.py [--inputs PATH] [--json OUT]
Login-safe in principle but reads ~1.1 GB; prefer a compute node.

THE PRODUCT CREATES ONE LIVE HASH PIN, deliberately. `verify_hash_bindings.collect()` harvests the
`inputs` / `inputs_sha256` pair, so the committed JSON pins the exact G2 dump it was derived from
(`fa6b3463...`, the same digest `sbatch_powered_closure.sh` carries as `EXPECTED_INPUTS_SHA`). Verified
2026-08-06: it resolves and matches on compute, and is silently unresolved on a laptop where the 1 GB
dump is absent -- which is the intended asymmetry, not a gap. If the dump is ever re-staged, this
product must be regenerated rather than hand-edited.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fullevent_fps_dataloader as fe  # noqa: E402

DEFAULT_INPUTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "g2_fullevent", "input", "G2_FPS_MEFHC_P12.npz")


def sha256(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", default=DEFAULT_INPUTS)
    ap.add_argument("--json", default=None, help="write the product here")
    ap.add_argument("--kmax", type=int, default=4)
    a = ap.parse_args()

    pt_edges = np.asarray(fe.CANONICAL_PT_EDGES, float)
    pp_edges = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    n_pt, n_pp = pt_edges.size - 1, pp_edges.size - 1

    with np.load(a.inputs) as d:
        ts = np.asarray(d["truth_scalars"], np.float64)
        w = np.asarray(d["w_truth"], np.float64)
        pass_truth = np.asarray(d["pass_truth"]).astype(bool)
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)
    pt = ts[:, fe.SCALAR_COLS["pt"]]
    pp = ts[:, fe.SCALAR_COLS["pparallel"]]
    del ts

    both = pass_truth & pass_reco
    coords = np.column_stack([pt, pp])
    denom, _ = np.histogramdd(coords[pass_truth], bins=[pt_edges, pp_edges],
                              weights=w[pass_truth])
    numer, _ = np.histogramdd(coords[both], bins=[pt_edges, pp_edges], weights=w[both])
    acc = np.zeros_like(denom)
    nz = denom > 0
    acc[nz] = numer[nz] / denom[nz]

    # unweighted twin, so a weighting artefact cannot masquerade as physics
    d_u, _ = np.histogramdd(coords[pass_truth], bins=[pt_edges, pp_edges])
    n_u, _ = np.histogramdd(coords[both], bins=[pt_edges, pp_edges])
    acc_u = np.zeros_like(d_u)
    acc_u[d_u > 0] = n_u[d_u > 0] / d_u[d_u > 0]

    tot = float(w[pass_truth].sum())
    global_acc = float(w[both].sum() / tot)
    global_acc_u = float(both.sum() / pass_truth.sum())

    # p_parallel marginal: the axis the acceptance gradient actually lives on
    marg = []
    for j in range(n_pp):
        dj, nj = float(denom[:, j].sum()), float(numer[:, j].sum())
        aj = (nj / dj) if dj > 0 else 0.0
        marg.append({
            "i_pparallel": j,
            "pparallel_lo": float(pp_edges[j]), "pparallel_hi": float(pp_edges[j + 1]),
            "frac_of_fiducial_truth": dj / tot,
            "acceptance": aj,
            "prior_weight_by_k": {str(k): (1.0 - aj) ** k for k in range(1, a.kmax + 1)},
        })

    # the headline: displacement-unweighted cell census of prior domination
    flat = acc[denom > 0]
    below = {
        "cells_with_acceptance_below_0.01": int((flat < 0.01).sum()),
        "cells_with_acceptance_below_0.05": int((flat < 0.05).sum()),
        "n_populated_cells": int(flat.size),
        "truth_mass_fraction_in_cells_below_0.01":
            float(denom[(denom > 0) & (acc < 0.01)].sum() / tot),
        "truth_mass_fraction_with_prior_weight_above_0.9_at_k3":
            float(denom[(denom > 0) & ((1.0 - acc) ** 3 > 0.9)].sum() / tot),
    }

    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, cwd=os.path.dirname(a.inputs)).stdout.strip() or None
    except OSError:
        head = None

    out = {
        "product_schema": "pet-fullevent-fps-acceptance-map-v1",
        "what_this_is": ("per-cell reco acceptance a_b on the canonical extended-FPS grid, and the "
                        "prior weight (1-a_b)^k = the fraction of the answer still uncorrected by "
                        "data after k OmniFold iterations"),
        "definition": "a_b = sum(w_truth | pass_truth & pass_reco) / sum(w_truth | pass_truth)",
        "matches": "extract_fullevent_fps.completeness_2d:390-404 (same formula, diagnostic use)",
        "caveat": ("this quantity is a reco EFFICIENCY. KNOWN_ISSUES records that the extractor "
                   "wrongly divides the cross section by it. Using it as a blindness diagnostic is "
                   "unaffected by that defect."),
        "inputs": os.path.abspath(a.inputs),
        "inputs_sha256": sha256(a.inputs),
        "git_head": head,
        "n_pt_bins": n_pt, "n_pparallel_bins": n_pp, "n_cells": n_pt * n_pp,
        "edges_pt": [float(x) for x in pt_edges],
        "edges_pparallel": [float(x) for x in pp_edges],
        "global_acceptance_w_truth_weighted": global_acc,
        "global_acceptance_unweighted": global_acc_u,
        "gate2_receipt_acceptance_for_comparison": 20573521 / 49152885,
        # SCOPE MISLABEL, NOT A WRONG FORMULA -- and the distinction matters, so read on before
        # "fixing" anything else with it. `(1-x)^k` is convex in x, so by Jensen
        # `E_w[(1-a_b)^k] >= (1-E_w[a_b])^k`: evaluating at the GLOBAL acceptance overstates the
        # achievable PER-CELL recovery (+19.9 pp at k=3 here). For a DIFFERENTIAL criterion that is
        # simply the wrong quantity, and it read 0.8084 at k=3 -- essentially exactly the powered
        # closure's 0.80 bar -- which invites the conclusion that the bar is achievable and the
        # estimator broken, the opposite of the truth.
        #
        # BUT the global form is CORRECT for a SCALAR observable with a global acceptance, which is
        # exactly what the B1 rate closure uses: `structural_floor_worst_case = (1-a)^k (R-1)/R` with
        # the global a, and it matches measurement to 1.9% / 0.8% at k=2 / k=3. Do not "correct" B1
        # by analogy with this entry. Kept, renamed and labelled rather than deleted because it was
        # published in v1 and a reader needs to know what they read.
        # Same error class as the CLM-011 magnitudes (cell-by-cell 122.6x vs aggregate 2.36x).
        "ideal_recovery_from_global_acceptance_by_k__OVERSTATES_DIFFERENTIAL": {
            str(k): 1.0 - (1.0 - global_acc) ** k for k in range(1, a.kmax + 1)},
        # The per-cell average is the right FORM for any per-bin criterion. Note the WEIGHT still
        # has to match the criterion: an L1 shape criterion like the powered closure weights each
        # cell by its injected tilt |prior_b - target_b|, not by truth mass, so this field is a
        # reference curve and NOT the closure's ceiling. The closure-specific ceiling requires the
        # tilt from POWERED_CLOSURE_REPORT.*.json and is recorded with that finding.
        "ideal_recovery_percell_truthmass_weighted_by_k": {
            str(k): float(1.0 - np.average((1.0 - acc[np.isfinite(acc) & (denom > 0)]) ** k,
                                           weights=denom[np.isfinite(acc) & (denom > 0)]))
            for k in range(1, a.kmax + 1)},
        # Emitted by the PRODUCER, not hand-added. The 2026-08-06 fix was first applied by editing
        # the product in place, which left it no longer reproducible from this script and its
        # `git_head` pointing at the pre-fix commit. A product that its own producer cannot
        # regenerate is not a product; the note therefore lives here.
        "recovery_field_scope_note": (
            "ideal_recovery_from_global_acceptance_by_k__OVERSTATES_DIFFERENTIAL is the SCALAR-scope "
            "curve: 1-(1-a_global)^k. By Jensen it is an UPPER bound on per-cell recovery (+19.9 pp "
            "at k=3 here) and must not be compared with a differential criterion such as the powered "
            "closure's L1 recovery. ideal_recovery_percell_truthmass_weighted_by_k is the per-cell "
            "form but is TRUTH-MASS weighted, so it is a reference curve and NOT that closure's "
            "ceiling either: an L1 shape criterion weights each cell by its injected displacement "
            "|prior_b-target_b|, giving 0.6332 at k=3 and 0.6629 at k=4 "
            "(FINDING-20260806-niter4-decision.md, where it is graded ASSUMED because "
            "omnifold.py:218-220 lets a smooth learner transport the tilt across cells). The global "
            "form IS correct for a scalar observable, which is why B1's structural_floor_worst_case "
            "legitimately uses it."),
        "pparallel_marginal": marg,
        "prior_domination_census": below,
        "acceptance_cells_pt_major": [float(x) for x in acc.ravel(order="C")],
        "acceptance_cells_unweighted_pt_major": [float(x) for x in acc_u.ravel(order="C")],
        "truth_mass_cells_pt_major": [float(x) for x in denom.ravel(order="C")],
        "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
    }

    print(f"global acceptance  weighted {global_acc:.6f}   unweighted {global_acc_u:.6f}")
    print(f"Gate-2 receipt     {20573521/49152885:.6f}")
    print(f"populated cells    {below['n_populated_cells']} of {n_pt*n_pp}")
    print(f"cells a_b < 0.01   {below['cells_with_acceptance_below_0.01']}"
          f"   carrying {below['truth_mass_fraction_in_cells_below_0.01']*100:.2f}% of truth mass")
    print(f"truth mass with >90% prior weight at k=3: "
          f"{below['truth_mass_fraction_with_prior_weight_above_0.9_at_k3']*100:.2f}%")
    print()
    print(f"{'p_par (GeV)':>16} {'% fiducial':>11} {'a_b':>9} {'(1-a)^3':>9} {'(1-a)^4':>9}")
    for m in marg:
        print(f"{m['pparallel_lo']:7.2f}-{m['pparallel_hi']:<8.2f} "
              f"{m['frac_of_fiducial_truth']*100:10.2f}% {m['acceptance']:9.5f} "
              f"{m['prior_weight_by_k']['3']:9.4f} {m['prior_weight_by_k']['4']:9.4f}")

    if a.json:
        os.makedirs(os.path.dirname(a.json), exist_ok=True)
        tmp = a.json + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(out, fh, indent=1)
            fh.write("\n")
        os.replace(tmp, a.json)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
