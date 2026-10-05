"""Define the safeguard's regions from the reporting CELLS, and measure what each holds.

WHY THIS IS A NEW FILE AND NOT AN EDIT. `characterize_eavail_endpoint.py` is bound
by the guard receipt of job 58527254, which recorded the sha256 of the script it
ran. Editing it in place would make that receipt describe a script that no longer
exists -- the same discipline that kept the `OI-125` recorder out of the pinned
closure driver. The binding caught the attempt; this file is the correct shape.

WHAT IT ADDS. The seven-bin `E_avail` census reported no bin below 0.05 acceptance,
which reads as reassuring and is an artifact of marginalisation: those bins average
over `(pT, p-parallel)` cells whose acceptance spans 0.004 to 0.89. A safeguard
defined on the marginal cannot see a failure the marginal hides, so regions are
defined on the underlying reporting cells instead.

Three quantities per region, because they answer different questions. **Truth mass**
says how much of the measurement lives there. **Injected displacement** says how
much signal the closure puts there -- a region the injection never perturbed cannot
yield a recovery figure, so demanding one would block on noise. **Acceptance** says
how much of it the detector returns.

A region carrying less than `MIN_REGION_DISPLACEMENT_SHARE` of the injected
displacement is EXEMPT and reported as such, and the total exempt mass is reported
too, so the exemption cannot quietly swallow the failure it was meant to isolate.

NOT CITABLE FOR any ratified threshold. It measures; it decides nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

# Transcribed from characterize_eavail_endpoint.py rather than imported, because
# that module is guarded and importing it would drag its sys.path assumptions in.
# The values are asserted equal to it in test_regions.py, so a drift is caught.
TILT_AMPLITUDE = 0.35
TILT_CLIP_Z = 3.0
EXPECTED_NPZ_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"

# Region names are DESCRIPTIONS OF ACCEPTANCE, not predictions about what can be
# recovered there. The lowest band was called "unresolvable", which asserted an
# impossibility the census cannot establish: acceptance is a property of the
# detector and the k=3 reference is a property of one iteration count, and neither
# is a bound on what an estimator can achieve. Joseph, 2026-09-20: "The acceptance
# reference is not an impossibility bound; do not call low-acceptance regions
# fundamentally unresolvable."
#
# These events are RETAINED in the analysis. The band exists so their mass,
# displacement and per-arm results can be reported separately, not so they can be
# set aside.
SAFEGUARD_REGIONS = (
    ("low_acceptance", 0.0, 0.05),
    ("poor", 0.05, 0.25),
    ("moderate", 0.25, 0.50),
    ("good", 0.50, 1.0000001),
)
MIN_REGION_DISPLACEMENT_SHARE = 0.02


def region_census(acceptance_cells, truth_mass_cells, displacement_cells) -> dict[str, Any]:
    """Partition the reporting cells into regions and report what each carries."""
    a = np.asarray(acceptance_cells, dtype=np.float64).ravel()
    m = np.asarray(truth_mass_cells, dtype=np.float64).ravel()
    d = np.asarray(displacement_cells, dtype=np.float64).ravel()
    if not (a.shape == m.shape == d.shape):
        raise ValueError(f"cell arrays disagree: {a.shape}, {m.shape}, {d.shape}")
    mass_total, disp_total = m.sum(), d.sum()
    rows = []
    for name, lo, hi in SAFEGUARD_REGIONS:
        inside = (a >= lo) & (a < hi)
        share = float(d[inside].sum() / disp_total) if disp_total > 0 else 0.0
        rows.append({
            "region": name,
            "acceptance_range": [lo, min(hi, 1.0)],
            "cells": int(inside.sum()),
            "truth_mass_fraction": float(m[inside].sum() / mass_total) if mass_total > 0 else 0.0,
            "injected_displacement_share": share,
            "mean_acceptance": float(a[inside].mean()) if inside.any() else None,
            "min_acceptance": float(a[inside].min()) if inside.any() else None,
            "max_acceptance": float(a[inside].max()) if inside.any() else None,
            "scoreable": bool(share >= MIN_REGION_DISPLACEMENT_SHARE),
            "exempt_reason": (
                None if share >= MIN_REGION_DISPLACEMENT_SHARE
                else f"injected displacement share {share:.4f} < {MIN_REGION_DISPLACEMENT_SHARE}"
            ),
        })
    return {
        "regions": rows,
        "min_displacement_share_to_be_scoreable": MIN_REGION_DISPLACEMENT_SHARE,
        "exempt_truth_mass_fraction": sum(
            r["truth_mass_fraction"] for r in rows if not r["scoreable"]),
        "exempt_displacement_share": sum(
            r["injected_displacement_share"] for r in rows if not r["scoreable"]),
        "scoreable_regions": [r["region"] for r in rows if r["scoreable"]],
        "reading": (
            "Every scoreable region must clear the regional floor for a "
            "recommendation to be possible. Exempt regions are reported with the "
            "mass they hold so the exemption is auditable; a large exempt mass means "
            "the endpoint is not adequate, and the safeguard says so rather than "
            "passing quietly."
        ),
    }


UNASSIGNED = "outside_the_reporting_grid"


def cell_index_of_events(pt, pz, edges_pt, edges_pz):
    """Flat cell index per event, matching `np.histogram2d`'s binning exactly.

    `histogram2d` closes the LAST bin on the right and silently DROPS anything
    outside the grid. A per-event assignment has to reproduce both, or the
    regional safeguard would be computed over a different population than the
    cells its references were built from. Events off the grid get -1 rather than
    being folded into an edge bin: pretending they sit in the nearest cell would
    move mass into a region that never held it.

    Checked against `histogram2d` itself in `test_regions.py`, not against a
    second hand-rolled binning.
    """
    pt = np.asarray(pt, dtype=np.float64)
    pz = np.asarray(pz, dtype=np.float64)
    ex = np.asarray(edges_pt, dtype=np.float64)
    ey = np.asarray(edges_pz, dtype=np.float64)
    nx, ny = ex.size - 1, ey.size - 1
    ix = np.digitize(pt, ex) - 1
    iy = np.digitize(pz, ey) - 1
    ix = np.where(pt == ex[-1], nx - 1, ix)   # histogram2d closes the last bin
    iy = np.where(pz == ey[-1], ny - 1, iy)
    inside = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny) \
        & np.isfinite(pt) & np.isfinite(pz)
    return np.where(inside, ix * ny + iy, -1)


def region_labels_for_events(pt, pz, edges_pt, edges_pz, acceptance_cells):
    """Label each event with the region of ITS reporting cell.

    A region is a set of cells, so an event's region is its cell's. Deriving one
    by stratifying the seven marginal `E_avail` bins by average acceptance is the
    mistake the frozen design names explicitly, and it is not available here
    because this function never sees the marginal.
    """
    a = np.asarray(acceptance_cells, dtype=np.float64).ravel()
    flat = cell_index_of_events(pt, pz, edges_pt, edges_pz)
    if flat.size and flat.max() >= a.size:
        raise ValueError(
            f"cell index {int(flat.max())} exceeds the {a.size} acceptance cells; "
            "the edges and the acceptance map are from different grids"
        )
    labels = np.full(flat.shape, UNASSIGNED, dtype=object)
    for name, lo, hi in SAFEGUARD_REGIONS:
        chosen = (flat >= 0)
        band = np.zeros_like(chosen)
        band[chosen] = (a[flat[chosen]] >= lo) & (a[flat[chosen]] < hi)
        labels[band] = name
    return np.asarray(labels, dtype="<U32"), flat


def regional_reference(acceptance_cells, displacement_cells, iterations: int = 3):
    """The reference model restricted to each region, weighted as the L1 statistic is.

    A single absolute floor across regions would be a different standard in each,
    because regions differ in acceptance by construction. Each region is therefore
    scored against its own `ceiling(k)`.
    """
    import reference_calibration as rc

    a = np.asarray(acceptance_cells, dtype=np.float64).ravel()
    d = np.asarray(displacement_cells, dtype=np.float64).ravel()
    out = {}
    for name, lo, hi in SAFEGUARD_REGIONS:
        inside = (a >= lo) & (a < hi)
        if not inside.any() or d[inside].sum() <= 0:
            out[name] = None
            continue
        out[name] = float(rc.ceiling(a[inside], d[inside], iterations))
    return out


def _digest(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-digest", action="store_true")
    args = parser.parse_args()

    root = args.repo / "nd-unfolding" / "pet"
    for path in (root, root / "configuration_comparison"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from closure_powered_truth_reweight import clipped_exponential_tilt

    digest = None if args.skip_digest else _digest(args.inputs)
    if digest is not None and digest != EXPECTED_NPZ_SHA256:
        raise SystemExit(f"[regions] digest {digest} != expected (fail closed)")

    with np.load(args.inputs, allow_pickle=False) as handle:
        truth_scalars = np.asarray(handle["truth_scalars"], dtype=np.float64)
        pass_truth = np.asarray(handle["pass_truth"], dtype=bool)
        pass_reco = np.asarray(handle["pass_reco"], dtype=bool)
        w_truth = np.asarray(handle["w_truth"], dtype=np.float64)
        edges_pt = np.asarray(handle["edges_0"], dtype=np.float64)
        edges_pz = np.asarray(handle["edges_1"], dtype=np.float64)

    pt, pz, eavail = truth_scalars[:, 0], truth_scalars[:, 1], truth_scalars[:, 2]
    finite = np.isfinite(eavail)
    pass_truth = pass_truth & finite
    tilt, tilt_spec = clipped_exponential_tilt(
        eavail[pass_truth], TILT_AMPLITUDE, TILT_CLIP_Z)

    both = pass_truth & pass_reco
    denom, _, _ = np.histogram2d(pt[pass_truth], pz[pass_truth], bins=[edges_pt, edges_pz],
                                 weights=w_truth[pass_truth])
    numer, _, _ = np.histogram2d(pt[both], pz[both], bins=[edges_pt, edges_pz],
                                 weights=w_truth[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acceptance = np.where(denom > 0, numer / denom, 0.0)
    target, _, _ = np.histogram2d(pt[pass_truth], pz[pass_truth], bins=[edges_pt, edges_pz],
                                  weights=w_truth[pass_truth] * tilt)
    prior_f = (denom / denom.sum()).ravel()
    target_f = (target / target.sum()).ravel()
    displacement = np.abs(target_f - prior_f)

    census = region_census(acceptance.ravel(), prior_f, displacement)
    receipt = {
        "scope": ("regions for the safeguard, defined on the (pT, p-parallel) reporting "
                  "CELLS. Measures only; ratifies no threshold."),
        "why_not_the_marginal": (
            "the seven E_avail bins report no bin below 0.05 acceptance while the cells "
            "they average over span 0.004 to 0.89. A region defined on the marginal "
            "cannot detect a failure the marginal hides."
        ),
        "inputs": {"path": str(args.inputs), "sha256": digest,
                   "sha256_verified": digest is not None,
                   "cells": int(displacement.size),
                   "pass_truth_rows": int(pass_truth.sum())},
        "injection": {"variable": "truth E_avail", "amplitude": TILT_AMPLITUDE,
                      "clip": TILT_CLIP_Z, "spec": tilt_spec},
        "census": census,
        "regional_reference_k3": regional_reference(acceptance.ravel(), displacement, 3),
        "total_l1_displacement_on_cells": float(displacement.sum()),
        "non_claim": "No acceptance threshold, margin or regional floor is ratified here.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    for row in census["regions"]:
        print(f"{row['region']:13s} cells {row['cells']:>5}  mass {row['truth_mass_fraction']:6.4f}  "
              f"disp {row['injected_displacement_share']:6.4f}  "
              f"a[{row['min_acceptance'] if row['min_acceptance'] is None else round(row['min_acceptance'],3)}"
              f",{row['max_acceptance'] if row['max_acceptance'] is None else round(row['max_acceptance'],3)}]  "
              f"{'SCOREABLE' if row['scoreable'] else 'exempt'}")
    print(f"exempt mass {census['exempt_truth_mass_fraction']:.4f}  "
          f"exempt displacement {census['exempt_displacement_share']:.4f}")
    print("regional reference k=3:", receipt["regional_reference_k3"])


if __name__ == "__main__":
    main()
