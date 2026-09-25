"""Decompose the gap between the historical reference (0.695 at k=3) and what its OWN assumptions
give on the scored seven-bin marginal.

The historical reference `reference_calibration.ceiling(a, |d|, k)` weights each (pT, p_par) cell's
`1-(1-a)^k` by that cell's share of the injected displacement OF THE (pT, p_par) SPECTRUM. The
endpoint is scored on a different object: the seven-bin E_avail marginal, renormalized. This script
evaluates the reference model -- acceptance only, zero smearing, misses carried, i.e.
``t_k = T - (1-a)^k (T - t0)`` per truth bin -- analytically (no estimator, no sampling
difference between halves: prior and target are the SAME half-B events, target = prior x tilt)
on successively closer approximations to the scored object:

1. ``cells285``        the historical construction on half B (should be ~0.695 at k=3);
2. ``bins1995``        the same ceiling on (cell x E_avail bin) truth bins with THEIR displacement;
3. ``marginal7_abs``   the law applied per 1995 bin, summed to the seven E_avail bins, L1 recovery
                       on absolute (unnormalized) spectra;
4. ``marginal7_score`` the same with the score's renormalization (historical `recovery`).

Every step is a property of the reference model's assumptions, not of any estimator; the realized
estimator versions (`diag` in `ibu.json`) add the half-A/half-B sampling difference and the engine's
pseudo-data normalization on top.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

import run_ibu
import scalar_common as scm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    sources = scm.verify_historical_sources()
    mods = scm.historical_modules()
    rc, rae, cp, fd = mods["rc"], mods["rae"], mods["cp"], mods["fd"]

    pop = scm.load_populations(args.populations)
    bins = run_ibu.build_bins(pop)
    pg = pop["b_pass_truth"].astype(bool)
    s1 = pg & pop["b_pass_reco"].astype(bool)
    w = pop["b_w_truth"]
    tilt = np.ones(pg.size)
    tilt[pg], spec = cp.clipped_exponential_tilt(
        pop["b_truth"][pg, 2], amplitude=float(fd.ENDPOINT["amplitude"]),
        clip_z=float(fd.ENDPOINT["clip"]))
    n_eav = run_ibu.N_EAV
    tb = bins["b"]["truth"]
    nt = bins["n_truth"]
    cell = tb // n_eav

    def hist(idx, mask, weights, n):
        return np.bincount(idx[mask], weights=weights[mask], minlength=n)

    # truth mass (w_truth), accepted mass, tilted mass per 1995 bin and per 286 cells
    t0_b, acc_b, T_b = hist(tb, pg, w, nt), hist(tb, s1, w, nt), hist(tb, pg, w * tilt, nt)
    nc = bins["n_cells"] + 1
    t0_c, acc_c, T_c = hist(cell, pg, w, nc), hist(cell, s1, w, nc), hist(cell, pg, w * tilt, nc)
    a_b = np.where(t0_b > 0, acc_b / np.where(t0_b > 0, t0_b, 1), 0.0)
    a_c = np.where(t0_c > 0, acc_c / np.where(t0_c > 0, t0_c, 1), 0.0)
    # displacement of NORMALIZED spectra, as the historical maps define it
    d_c = np.abs(T_c / T_c.sum() - t0_c / t0_c.sum())
    d_b = np.abs(T_b / T_b.sum() - t0_b / t0_b.sum())
    # the law needs a rate-preserving target: rescale T to the prior's total. NOT a no-op: the
    # historical tilt is normalized by its UNWEIGHTED mean, so on w_truth-weighted mass it is not
    # rate-preserving (measured factor 0.9713 on half B, recorded below). The score renormalizes,
    # so this affects only the absolute-spectrum variant's bookkeeping.
    rescale = t0_b.sum() / T_b.sum()
    T_b = T_b * rescale

    ks = list(range(1, args.iterations + 1))
    rows = []
    t0_m = np.array([t0_b[eav_bin::n_eav].sum() for eav_bin in range(n_eav)])
    T_m = np.array([T_b[eav_bin::n_eav].sum() for eav_bin in range(n_eav)])
    for k in ks:
        tk = T_b - (1.0 - a_b) ** k * (T_b - t0_b)
        tk_m = np.array([tk[eav_bin::n_eav].sum() for eav_bin in range(n_eav)])
        rows.append({
            "k": k,
            "cells285": float(rc.ceiling(a_c, d_c, k)),
            "bins1995": float(rc.ceiling(a_b, d_b, k)),
            "marginal7_abs": float(1.0 - np.abs(T_m - tk_m).sum() / np.abs(T_m - t0_m).sum()),
            "marginal7_score": float(rae.recovery(t0_m, tk_m, T_m)["recovery"]),
        })
    k3 = rows[2]
    print("[decomposition] k=3 " + " ".join(f"{k}={v:.4f}" for k, v in k3.items() if k != "k"))
    # where the scored displacement sits, by acceptance region (half-B cell acceptance)
    region_of_cell = {}
    for name, lo, hi in mods["cr"].SAFEGUARD_REGIONS:
        region_of_cell[name] = (a_c >= lo) & (a_c < hi)
    by_region = {}
    for name, cmask in region_of_cell.items():
        bmask = cmask[np.arange(nt) // n_eav]
        disp_m = np.array([(T_b[bmask][e::n_eav].sum() - t0_b[bmask][e::n_eav].sum())
                           for e in range(n_eav)]) / t0_b.sum()
        by_region[name] = {
            "truth_mass_fraction": float(t0_b[bmask].sum() / t0_b.sum()),
            "share_of_cell_displacement_d285": float(d_c[cmask].sum() / d_c.sum()),
            "signed_marginal_displacement_per_eavail_bin": disp_m.tolist(),
            "share_of_top_bin_displacement": None,
        }
    top = n_eav - 1
    total_top = sum(v["signed_marginal_displacement_per_eavail_bin"][top] for v in by_region.values())
    for v in by_region.values():
        v["share_of_top_bin_displacement"] = (v["signed_marginal_displacement_per_eavail_bin"][top]
                                             / total_top)
    payload = {
        "schema": "phase-b1-reference-decomposition/1",
        "label": ("analytic evaluation of the historical reference MODEL's assumptions on the "
                  "scored object; not an estimator and not a bound"),
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "inputs": {"populations_npz": str(args.populations),
                   "populations_npz_sha256": scm.sha256_file(args.populations)},
        "population": "half B truth-passing rows; target = the same rows x tilt (half-B spec)",
        "tilt_spec_half_B": spec, "target_rescale_to_prior_total": float(rescale),
        "curve": rows,
        "displacement_by_region": by_region,
        "seconds": time.perf_counter() - started,
    }
    scm.write_json(args.output, payload)
    for name, v in by_region.items():
        print(f"[decomposition] {name:15s} mass={v['truth_mass_fraction']:.4f} "
              f"d285_share={v['share_of_cell_displacement_d285']:.4f} "
              f"top_bin_share={v['share_of_top_bin_displacement']:.4f}")


if __name__ == "__main__":
    main()
