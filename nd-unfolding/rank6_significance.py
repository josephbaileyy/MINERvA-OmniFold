#!/usr/bin/env python3
"""The replacement significance consumer for the adopted scalar-5D trunk.

WHY THIS IS NEW CODE AND NOT A PATCH. The two existing consumers cannot be repaired into the claim.
`eavailW_covariance.py` builds its OWN component sum and spreads 4D lateral bands over W as a
self-documented "flat-in-W fractional -- documented approximation", and `AGENTS.md:30` lists the
(E_avail,W) covariance itself as QUARANTINED and unquotable; `AGENTS.md:27` requires the quotable
covariance to be PROJECTED from the adopted, selection-complete trunk. Re-pointing an input path
would leave every inference assumption unresolved, which is the audit's rank-6 finding.

WHAT IT REFUSES, and each refusal is one of the eight declarations of
docs/orchestration/CONTRACT-20260918-rank6-significance-consumer.md:

  rc 3  --rcond absent. Both existing consumers call pinv with NO explicit rcond, and one of them
        already comments that the matrix "can be near-singular -> pinv amplifies shape directions".
        C_Z is heavily rank-deficient (lambda_min = -1.275e-90, 5214 negative eigenvalues of
        10694), so an undeclared rcond chooses the hypothesis silently. There is no default here.
  rc 4  ndf would be the bin count. The existing header reads literally `chi2/ndf(all7)`. The
        retained RANK is the ndf candidate; a bin count is not. A rank is a property of the matrix
        and a calibrated ndf is a property of the null distribution, so the rank is reported as the
        ndf INPUT with that distinction stated, and no generic Hartlap factor is applied.
  rc 5  the region is not fully prespecified and no selection-aware calibration is declared. THIS
        IS D5 ENFORCED IN CODE. Measured from the repository: "open question 6" -- the high-E_avail
        excess as a QUESTION -- is recorded 2026-06-03 (de84c61e), before the W axis existed; the
        first (E_avail,W) excess test ran 2026-06-07 (95ce2950); and `W >= 1.8` first appears in
        code 2026-06-09 (b64cf582), two days later, with HIGHER_DIM_OMNIFOLD_DESIGN.md:169 saying
        the W axis "localizes open question 6 to the high-W DIS corner". A localization claim is
        honest at central-value level; a SIGNIFICANCE on the boundary the data chose is not the
        same object.
  rc 6  no claim threshold. Without the significance at which the claim is asserted, a number here
        decides nothing -- and deriving the threshold afterwards from the number would be a
        threshold placed to obtain a verdict.
  rc 7  the central estimate does not come from the same product as the covariance. The pairing is
        M1 x_5D, the MARGINALISED central value, NOT an independently unfolded 2D estimator; those
        differ by ~3% by construction and that difference is not an error.

WHAT A TERMINAL RESULT CANNOT AUTHORIZE: it does not establish coverage of the reported band, does
not validate any other projection, does not promote any historical number, and does not license an
event-level fit. Computing a significance is not adopting one.

NOTHING HERE IS APPROVED. The contract is a DRAFT and D3/D5 are open, which is exactly why the
threshold and the region are REQUIRED INPUTS rather than values baked in. The core is pure numpy so
it is fully testable without ROOT; only the CLI touches ROOT.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

import numpy as np


class Refusal(SystemExit):
    def __init__(self, code: int, msg: str):
        super().__init__(code)
        self.code, self.msg = code, msg
        print(f"REFUSED (rc {code}) -- {msg}", file=sys.stderr)


PRESPEC_CHOICES = ("both", "eavail-only", "neither")


@dataclass
class Declarations:
    """The eight contract declarations, as data. Absent ones refuse; none has a default."""
    rcond: float
    claim_threshold_sigma: float
    region_eavail_min: float
    region_w_min: float
    region_prespecified: str
    selection_aware: str | None
    generators: dict = field(default_factory=dict)

    def check(self):
        if self.rcond is None:
            raise Refusal(3, "no --rcond. An undeclared rcond on a rank-deficient matrix chooses "
                             "the retained subspace, and therefore the hypothesis, silently.")
        if not (0.0 < self.rcond < 1.0):
            raise Refusal(3, f"--rcond must lie in (0,1), got {self.rcond}")
        if self.claim_threshold_sigma is None:
            raise Refusal(6, "no --claim-threshold-sigma. Deriving it afterwards from the computed "
                             "significance would be a threshold placed to obtain a verdict.")
        if self.region_prespecified not in PRESPEC_CHOICES:
            raise Refusal(5, f"--region-prespecified must be one of {PRESPEC_CHOICES}")
        if self.region_prespecified != "both" and not self.selection_aware:
            raise Refusal(5,
                          f"the region is declared {self.region_prespecified!r}, so at least one "
                          f"boundary was localized from the data. Either declare a "
                          f"--selection-aware calibration, or restrict the claim to the "
                          f"prespecified region and keep the rest at central-value level. "
                          f"Measured: W >= 1.8 first appears in code 2026-06-09, two days after "
                          f"the first (E_avail,W) excess test.")


def retained_subspace(C: np.ndarray, rcond: float):
    """Eigendecomposition with the retained rank DECLARED, plus the pseudo-inverse it implies."""
    C = 0.5 * (np.asarray(C, float) + np.asarray(C, float).T)
    w, V = np.linalg.eigh(C)
    if w.size == 0 or w.max() <= 0:
        raise Refusal(4, "the projected covariance has no positive eigenvalue")
    cut = rcond * w.max()
    keep = w > cut
    rank = int(keep.sum())
    if rank == 0:
        raise Refusal(4, f"rcond={rcond:g} retains zero directions of {w.size}; nothing to test")
    w_inv = np.zeros_like(w)
    w_inv[keep] = 1.0 / w[keep]
    return {
        "eigenvalues": w, "retained_rank": rank, "n_bins": int(w.size),
        "cut_absolute": float(cut), "lambda_max": float(w.max()), "lambda_min": float(w.min()),
        "Cinv": (V * w_inv) @ V.T,
        "ndf_basis": ("ndf INPUT is the RETAINED RANK, not the bin count. A rank is a property of "
                      "the matrix; a calibrated ndf is a property of the null distribution. No "
                      "generic Hartlap factor is applied and rank alone is not called calibrated."),
    }


def chi2_and_sigma(resid: np.ndarray, Cinv: np.ndarray, ndf: int):
    from scipy import stats
    chi2 = float(resid @ Cinv @ resid)
    p = float(stats.chi2.sf(chi2, ndf)) if ndf > 0 else float("nan")
    z = float(stats.norm.isf(p / 2.0)) if 0.0 < p <= 1.0 else float("inf")
    return {"chi2": chi2, "ndf": int(ndf), "chi2_per_ndf": chi2 / ndf if ndf else float("nan"),
            "p_two_sided": p, "n_sigma": z}


def truncation_scan(resid, C, ndf_from_rank=True, rconds=None):
    """Declaration 3's scan: the significance AS A FUNCTION of the retained subspace.
    A single undeclared pinv hides exactly this dependence."""
    rconds = rconds if rconds is not None else [1e-14, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]
    rows = []
    for rc in rconds:
        try:
            sub = retained_subspace(C, rc)
        except SystemExit:
            rows.append({"rcond": rc, "retained_rank": 0, "refused": True})
            continue
        ndf = sub["retained_rank"] if ndf_from_rank else sub["n_bins"]
        rows.append({"rcond": rc, "retained_rank": sub["retained_rank"],
                     **chi2_and_sigma(resid, sub["Cinv"], ndf)})
    return rows


def region_mask(eavail_lo, w_lo, eavail_min, w_min):
    """The region as an EXPLICIT declaration. Both cuts are named; neither is hardcoded."""
    return (np.asarray(eavail_lo) >= eavail_min)[:, None] & (np.asarray(w_lo) >= w_min)[None, :]


def evaluate(C, central, generator, decl: Declarations, eavail_lo, w_lo,
             central_provenance=None, cov_provenance=None):
    decl.check()
    if central_provenance is not None and cov_provenance is not None:
        if central_provenance != cov_provenance:
            raise Refusal(7, f"the central estimate comes from {central_provenance!r} and the "
                             f"covariance from {cov_provenance!r}. The pairing must be M1 x_5D "
                             f"from the SAME product, not an independently unfolded estimator.")
    C = np.asarray(C, float)
    resid_full = np.asarray(central, float) - np.asarray(generator, float)
    mask = region_mask(eavail_lo, w_lo, decl.region_eavail_min, decl.region_w_min)
    idx = np.flatnonzero(mask.ravel(order="C"))
    if idx.size == 0:
        raise Refusal(5, "the declared region selects no cell")
    sub = retained_subspace(C[np.ix_(idx, idx)], decl.rcond)
    res = chi2_and_sigma(resid_full[idx], sub["Cinv"], sub["retained_rank"])
    return {
        "region": {"eavail_min": decl.region_eavail_min, "w_min": decl.region_w_min,
                   "n_cells": int(idx.size), "prespecified": decl.region_prespecified,
                   "selection_aware": decl.selection_aware},
        "retained": {k: sub[k] for k in
                     ("retained_rank", "n_bins", "cut_absolute", "lambda_max", "lambda_min",
                      "ndf_basis")},
        "result": res,
        "claim_threshold_sigma": decl.claim_threshold_sigma,
        "claim_supported_at_threshold": bool(res["n_sigma"] >= decl.claim_threshold_sigma),
        "truncation_scan": truncation_scan(resid_full[idx], C[np.ix_(idx, idx)]),
        "cannot_authorize": [
            "coverage of the reported scalar-5D band",
            "validity of any other projection",
            "promotion of any historical significance",
            "arbitrary event-level fits",
            "adoption -- computing a significance is not adopting one",
        ],
        "status": "CANDIDATE -- nothing here is approved; the consumer contract is a DRAFT",
    }


def _cli(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rcond", type=float, default=None)
    ap.add_argument("--claim-threshold-sigma", type=float, default=None)
    ap.add_argument("--region-eavail-min", type=float, required=True)
    ap.add_argument("--region-w-min", type=float, required=True)
    ap.add_argument("--region-prespecified", default=None)
    ap.add_argument("--selection-aware", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    Declarations(a.rcond, a.claim_threshold_sigma, a.region_eavail_min, a.region_w_min,
                 a.region_prespecified, a.selection_aware).check()
    raise Refusal(2, "the CLI payload path is deliberately not wired: the trunk is not adopted, "
                     "M1 does not exist, and the consumer contract is a DRAFT awaiting D3 and D5. "
                     "The declaration checks above are live and the core is importable and tested.")


if __name__ == "__main__":
    _cli()
