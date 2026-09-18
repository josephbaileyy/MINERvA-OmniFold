"""Characterize the candidate E_avail endpoint from the existing input npz.

Reads **only** `G2_FPS_MEFHC_P12.npz`, which the campaign already owns and has already
read. No tuple, no new source read, no new branch, no training, no estimator.

What it produces, all of it promised in advance by
`CANDIDATE_ENDPOINT_CHOICES-20260918.json`:

* the truth `E_avail` distribution over truth-passing rows, with the quantiles the tilt
  standardizes on;
* per-bin reco acceptance `a_b` on the candidate `E_avail` domain, by the committed
  formula `sum(w_truth | pass_truth & pass_reco) / sum(w_truth | pass_truth)`;
* the **injected displacement field** for the candidate tilt, on the `E_avail` domain and
  on the canonical (pT, p‖) grid, so the dilution of scoring off-variable is measured
  rather than argued;
* the **reference value** implied on both domains at k = 1…4;
* an acceptance-stratified census, so poorly accepted regions are visible.

**The tilt is imported, not reimplemented.** `clipped_exponential_tilt` comes from the
frozen `closure_powered_truth_reweight.py`, so the candidate injection is the *same
function* as the pT one with a different argument. A copy here could drift from the
predeclared protocol, and the whole point of the candidate is that it differs in exactly
one thing.

**This characterizes; it does not ratify.** Every threshold stays unratified, and the
reference value it reports is a **reference model, not a proven bound** -- a smooth
learner can transport a tilt across cells, and BEN-038 measured a band above the modelled
reachable value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

# Candidate choices, committed before this ran.
EAVAIL_EDGES = (0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0)
TILT_AMPLITUDE = 0.35
TILT_CLIP_Z = 3.0
ITERATIONS = (1, 2, 3, 4)
ACCEPTANCE_STRATA = ((0.0, 0.01), (0.01, 0.05), (0.05, 0.5), (0.5, 1.0000001))

EXPECTED_NPZ_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"


def _install(repo: Path) -> None:
    for sub in ("nd-unfolding/pet", "nd-unfolding/pet/configuration_comparison"):
        path = str(repo / sub)
        if path not in sys.path:
            sys.path.insert(0, path)


def _digest(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            h.update(block)
    return h.hexdigest()


def _acceptance(values, weights, pass_truth, pass_reco, edges) -> dict[str, Any]:
    """Per-bin reco acceptance by the committed formula, plus the truth mass."""
    edges = np.asarray(edges, dtype=np.float64)
    truth_sel = np.asarray(pass_truth, dtype=bool)
    both = truth_sel & np.asarray(pass_reco, dtype=bool)
    v = np.asarray(values, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    denom, _ = np.histogram(v[truth_sel], bins=edges, weights=w[truth_sel])
    numer, _ = np.histogram(v[both], bins=edges, weights=w[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acceptance = np.where(denom > 0, numer / denom, 0.0)
    return {
        "edges": edges.tolist(),
        "acceptance": acceptance.tolist(),
        "truth_mass": denom.tolist(),
        "reco_matched_mass": numer.tolist(),
        "populated_bins": int((denom > 0).sum()),
    }


def _displacement(values, weights, tilt, pass_truth, edges) -> dict[str, Any]:
    """|target_b - prior_b| on normalized densities: the weight the L1 statistic applies."""
    edges = np.asarray(edges, dtype=np.float64)
    sel = np.asarray(pass_truth, dtype=bool)
    v = np.asarray(values, dtype=np.float64)[sel]
    w = np.asarray(weights, dtype=np.float64)[sel]
    t = np.asarray(tilt, dtype=np.float64)
    prior, _ = np.histogram(v, bins=edges, weights=w)
    target, _ = np.histogram(v, bins=edges, weights=w * t)
    prior = prior / prior.sum() if prior.sum() > 0 else prior
    target = target / target.sum() if target.sum() > 0 else target
    displacement = np.abs(target - prior)
    return {
        "prior": prior.tolist(),
        "target": target.tolist(),
        "displacement": displacement.tolist(),
        "total_displacement": float(displacement.sum()),
        "max_bin_displacement": float(displacement.max()) if displacement.size else 0.0,
    }


def _strata_census(acceptance, truth_mass) -> list[dict[str, Any]]:
    """Make poorly accepted regions visible instead of letting them average away."""
    a = np.asarray(acceptance, dtype=np.float64)
    m = np.asarray(truth_mass, dtype=np.float64)
    total = m.sum()
    rows = []
    for lo, hi in ACCEPTANCE_STRATA:
        inside = (a >= lo) & (a < hi)
        rows.append({
            "acceptance_range": [lo, min(hi, 1.0)],
            "bins": int(inside.sum()),
            "truth_mass_fraction": float(m[inside].sum() / total) if total > 0 else 0.0,
            "mean_acceptance": float(a[inside].mean()) if inside.any() else None,
        })
    return rows


def main() -> None:
    """Characterize the candidate endpoint and write one receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-digest", action="store_true",
                        help="skip the 9.9 GB rehash; the receipt records that it was skipped")
    args = parser.parse_args()

    _install(args.repo)
    import reference_calibration as rc
    from closure_powered_truth_reweight import clipped_exponential_tilt

    digest = None if args.skip_digest else _digest(args.inputs)
    if digest is not None and digest != EXPECTED_NPZ_SHA256:
        raise SystemExit(
            f"[eavail] input digest {digest} != expected {EXPECTED_NPZ_SHA256} (fail closed)"
        )

    with np.load(args.inputs, allow_pickle=False) as handle:
        truth_scalars = np.asarray(handle["truth_scalars"], dtype=np.float64)
        pass_truth = np.asarray(handle["pass_truth"], dtype=bool)
        pass_reco = np.asarray(handle["pass_reco"], dtype=bool)
        w_truth = np.asarray(handle["w_truth"], dtype=np.float64)
        edges_pt = np.asarray(handle["edges_0"], dtype=np.float64)
        edges_pz = np.asarray(handle["edges_1"], dtype=np.float64)

    # truth_scalars columns are (pt, p_parallel, eavail, q3) -- dump_pointcloud_inputs.py:79
    eavail = truth_scalars[:, 2]
    pt, pz = truth_scalars[:, 0], truth_scalars[:, 1]
    finite = np.isfinite(eavail)
    if not finite.all():
        # Reported, never silently dropped: a non-finite truth quantity is a data fact.
        pass_truth = pass_truth & finite

    injected = eavail[pass_truth]
    tilt, tilt_spec = clipped_exponential_tilt(injected, TILT_AMPLITUDE, TILT_CLIP_Z)

    eavail_acc = _acceptance(eavail, w_truth, pass_truth, pass_reco, EAVAIL_EDGES)
    eavail_disp = _displacement(eavail, w_truth, tilt, pass_truth, EAVAIL_EDGES)

    # The (pT, p-parallel) grid, flattened pt-major exactly as the acceptance-map product
    # orders it, so the two are comparable cell for cell.
    grid_cells = (edges_pt.size - 1) * (edges_pz.size - 1)
    truth_sel = pass_truth
    both = pass_truth & pass_reco
    denom2, _, _ = np.histogram2d(pt[truth_sel], pz[truth_sel], bins=[edges_pt, edges_pz],
                                  weights=w_truth[truth_sel])
    numer2, _, _ = np.histogram2d(pt[both], pz[both], bins=[edges_pt, edges_pz],
                                  weights=w_truth[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acc2 = np.where(denom2 > 0, numer2 / denom2, 0.0)
    prior2, _, _ = np.histogram2d(pt[truth_sel], pz[truth_sel], bins=[edges_pt, edges_pz],
                                  weights=w_truth[truth_sel])
    target2, _, _ = np.histogram2d(pt[truth_sel], pz[truth_sel], bins=[edges_pt, edges_pz],
                                   weights=w_truth[truth_sel] * tilt)
    prior2f = (prior2 / prior2.sum()).ravel()
    target2f = (target2 / target2.sum()).ravel()
    disp2 = np.abs(target2f - prior2f)
    acc2f = acc2.ravel()

    receipt: dict[str, Any] = {
        "scope": (
            "characterization of the CANDIDATE E_avail endpoint from the existing input "
            "npz. No tuple read, no new branch, no training, no estimator, no threshold "
            "ratified."
        ),
        "candidate_choices": "CANDIDATE_ENDPOINT_CHOICES-20260918.json, committed before this ran",
        "inputs": {
            "path": str(args.inputs),
            "sha256": digest,
            "sha256_verified": digest is not None,
            "expected_sha256": EXPECTED_NPZ_SHA256,
            "rows": int(pass_truth.size),
            "pass_truth_rows": int(pass_truth.sum()),
            "pass_reco_rows": int(pass_reco.sum()),
            "non_finite_eavail_rows": int((~finite).sum()),
        },
        "injection": {
            "variable": "truth E_avail (truth_scalars col 2, MC_eavail)",
            "tilt_function": "closure_powered_truth_reweight.clipped_exponential_tilt (IMPORTED, not reimplemented)",
            "spec": tilt_spec,
            "spec_key_naming_note": (
                "The imported function names its quantile keys pt_p25/pt_p50/pt_p75/"
                "pt_iqr because it was written for the pT injection. Here they are "
                "E_avail quantiles in GeV. The names are an artifact of sharing the "
                "frozen function rather than copying it; the relabelled values are in "
                "`quantiles_gev` below so nothing is read as a pT quantile."
            ),
            "quantiles_gev": {
                "p25": tilt_spec.get("pt_p25"), "p50": tilt_spec.get("pt_p50"),
                "p75": tilt_spec.get("pt_p75"), "iqr": tilt_spec.get("pt_iqr"),
            },
            "weight_range": [float(tilt.min()), float(tilt.max())],
        },
        "primary_domain_eavail": {
            **eavail_acc,
            "displacement": eavail_disp,
            "reference_model_by_k": {
                str(k): rc.ceiling(eavail_acc["acceptance"], eavail_disp["displacement"], k)
                for k in ITERATIONS
            },
            "reference_model_truth_mass_weighted_by_k": {
                str(k): rc.ceiling(eavail_acc["acceptance"], eavail_acc["truth_mass"], k)
                for k in ITERATIONS
            },
            "acceptance_strata": _strata_census(eavail_acc["acceptance"], eavail_acc["truth_mass"]),
        },
        "secondary_domain_pt_pparallel": {
            "role": "CO-REPORTED DIAGNOSTIC ONLY, no decision weight",
            "n_cells": int(grid_cells),
            "total_displacement": float(disp2.sum()),
            "max_cell_displacement": float(disp2.max()),
            "reference_model_by_k": {
                str(k): rc.ceiling(acc2f, disp2, k) for k in ITERATIONS
            },
            "dilution_note": (
                "Total displacement here against the primary domain's measures how much "
                "of an E_avail tilt survives projection onto muon kinematics. A small "
                "value is the quantitative form of 'scoring off-variable dilutes the "
                "endpoint'."
            ),
        },
        "reference_model_not_a_proven_bound": (
            "Every reference value above assumes displacement reaches a cell only through "
            "that cell's acceptance. omnifold.py:218-220 lets a smooth learner transport a "
            "tilt across cells, and BEN-038 measured a band at E_w[r] = 1.0333, above the "
            "modelled reachable value. Graded ASSUMED in "
            "FINDING-20260806-niter4-decision.md. Recovery is quoted relative to a "
            "reference; exceeding it is possible."
        ),
        "does_not_ratify": [
            "No acceptance threshold, non-inferiority margin or switching threshold.",
            "No binning or amplitude is adopted by having been characterized.",
            "Low-acceptance bins are RETAINED and reported, not removed to raise the reference.",
        ],
    }
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")

    print(f"pass_truth rows: {receipt['inputs']['pass_truth_rows']:,}")
    print(f"E_avail quantiles p25/p50/p75 (GeV): {tilt_spec.get('pt_p25'):.4f}, "
          f"{tilt_spec.get('pt_p50'):.4f}, {tilt_spec.get('pt_p75'):.4f}")
    print("E_avail bin acceptance: " +
          ", ".join(f"{a:.3f}" for a in eavail_acc["acceptance"]))
    print("E_avail displacement:   " +
          ", ".join(f"{d:.4f}" for d in eavail_disp["displacement"]))
    for k in ITERATIONS:
        print(f"  reference model k={k}: "
              f"E_avail {receipt['primary_domain_eavail']['reference_model_by_k'][str(k)]:.6f}  "
              f"(pT,pz) {receipt['secondary_domain_pt_pparallel']['reference_model_by_k'][str(k)]:.6f}")
    print(f"total displacement: E_avail {eavail_disp['total_displacement']:.4f} vs "
          f"(pT,pz) {float(disp2.sum()):.4f}")


if __name__ == "__main__":
    main()
