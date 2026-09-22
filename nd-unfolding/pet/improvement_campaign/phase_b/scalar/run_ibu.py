"""Binned iterative unfolding on the historical endpoint, k = 1..K, beside the reference curve.

Truth bins are the seven endpoint `E_avail` bins crossed with the 15 x 19 (pT, p_parallel)
reporting cells the historical regions are defined on (1995 bins). The response comes from the
prior half (half B); the pseudo-data is half A's pass_reco & pass_gen rows at ``w_reco * tilt``,
normalized as the historical driver did. Variants (see `VARIANTS`):

* reco binning ``muon``         -- reco (pT, p_parallel) cells (+1 off-grid bin): muon kinematics only;
* reco binning ``muon_eavail``  -- the same crossed with reco E_avail in the endpoint's seven bins;
* reco binning ``eavail_only``  -- reco E_avail alone, seven bins (informational);
* reco binning ``diag``         -- the event's own TRUTH bin used as its reco bin. This is NOT an
  estimator anyone could run: it is the historical reference model (acceptance only, no smearing)
  realized on the actual populations and the actual seven-bin score, so the reference can be
  compared with what its own assumptions predict for the endpoint it was used to judge.

Each is run with misses carried at their prior weight (the engine's treatment, `carry_misses`) and
most also with textbook efficiency correction (`efficiency_corrected`), and under the engine's
pseudo-data normalization (``engine``) and the rate-matched one (``rate_matched``; in a real
measurement POT normalization supplies it, in this closure it is known because the tilt is).
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import numpy as np

import binned_unfolding as bu
import scalar_common as scm

SCOREABLE = ("low_acceptance", "moderate", "good")
INFORMATIONAL = ("poor",)
N_EAV = 7

# (reco binning, mode, normalization)
VARIANTS = [
    ("muon", bu.MODE_CARRY_MISSES, "engine"),
    ("muon", bu.MODE_CARRY_MISSES, "rate_matched"),
    ("muon", bu.MODE_EFFICIENCY_CORRECTED, "engine"),
    ("muon_eavail", bu.MODE_CARRY_MISSES, "engine"),
    ("muon_eavail", bu.MODE_CARRY_MISSES, "rate_matched"),
    ("muon_eavail", bu.MODE_EFFICIENCY_CORRECTED, "engine"),
    ("eavail_only", bu.MODE_CARRY_MISSES, "engine"),
    ("diag", bu.MODE_CARRY_MISSES, "engine"),
    ("diag", bu.MODE_CARRY_MISSES, "rate_matched"),
    ("diag", bu.MODE_EFFICIENCY_CORRECTED, "engine"),
]


def eavail_bin(x: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Endpoint E_avail bin, with anything below/above the range folded into the edge bins.
    (The SCORE uses np.histogram, which drops out-of-range events; folding only affects which
    truth/reco bin a response entry lands in, and the census reports how many were folded.)"""
    return np.clip(np.digitize(np.asarray(x, dtype=np.float64), edges) - 1, 0, len(edges) - 2)


def build_bins(pop: dict[str, np.ndarray]) -> dict[str, Any]:
    edges = pop["endpoint_edges"]
    n_cells = (len(pop["edges_pt"]) - 1) * (len(pop["edges_pz"]) - 1)
    out: dict[str, Any] = {"n_cells": n_cells}
    for side in ("a", "b"):
        tcell = pop[f"{side}_truth_cell"].astype(np.int64)
        tcell = np.where(tcell >= 0, tcell, n_cells)                 # off-grid -> its own cell
        teav = eavail_bin(pop[f"{side}_truth"][:, 2], edges)
        rcell = pop[f"{side}_reco_cell"].astype(np.int64)
        rcell = np.where(rcell >= 0, rcell, n_cells)
        reav = eavail_bin(pop[f"{side}_reco"][:, 2], edges)
        out[side] = {
            "truth": tcell * N_EAV + teav,
            "muon": rcell,
            "muon_eavail": rcell * N_EAV + reav,
            "eavail_only": reav,
            "diag": tcell * N_EAV + teav,
            "reco_eavail7": reav,
        }
    out["n_truth"] = (n_cells + 1) * N_EAV
    out["n_reco"] = {"muon": n_cells + 1, "muon_eavail": (n_cells + 1) * N_EAV,
                     "eavail_only": N_EAV, "diag": (n_cells + 1) * N_EAV}
    return out


def census(pop: dict[str, np.ndarray], bins: dict[str, Any]) -> dict[str, Any]:
    edges = pop["endpoint_edges"]
    out = {}
    for side in ("a", "b"):
        pg = pop[f"{side}_pass_truth"].astype(bool)
        s1 = pg & pop[f"{side}_pass_reco"].astype(bool)
        te = pop[f"{side}_truth"][:, 2]
        re = pop[f"{side}_reco"][:, 2]
        out[side] = {
            "truth_eavail_below_range_on_pg": int((te[pg] < edges[0]).sum()),
            "truth_eavail_above_range_on_pg": int((te[pg] > edges[-1]).sum()),
            "reco_eavail_below_range_on_s1": int((re[s1] < edges[0]).sum()),
            "reco_eavail_above_range_on_s1": int((re[s1] > edges[-1]).sum()),
            "truth_off_grid_on_pg": int((pop[f"{side}_truth_cell"][pg] < 0).sum()),
            "reco_off_grid_on_s1": int((pop[f"{side}_reco_cell"][s1] < 0).sum()),
        }
    pg = pop["b_pass_truth"].astype(bool)
    s1 = pg & pop["b_pass_reco"].astype(bool)
    out["populated_truth_bins_B"] = int(np.unique(bins["b"]["truth"][pg]).size)
    for name in ("muon", "muon_eavail", "eavail_only", "diag"):
        out[f"populated_reco_bins_B/{name}"] = int(np.unique(bins["b"][name][s1]).size)
    return out


def rate_matched_total(pop: dict[str, np.ndarray]) -> tuple[float, dict[str, float]]:
    """1e6 x f_A(tilted) / f_B: the pseudo-data total whose accepted fraction matches its truth."""
    pga = pop["a_pass_truth"].astype(bool)
    s1a = pga & pop["a_pass_reco"].astype(bool)
    pgb = pop["b_pass_truth"].astype(bool)
    s1b = pgb & pop["b_pass_reco"].astype(bool)
    tilt = pop["a_tilt"]
    f_a = (pop["a_w_reco"][s1a] * tilt[s1a]).sum() / (pop["a_w_truth"][pga] * tilt[pga]).sum()
    f_b = pop["b_w_reco"][s1b].sum() / pop["b_w_truth"][pgb].sum()
    return float(bu.ENGINE_NORMALIZATION * f_a / f_b), {"f_A_tilted": float(f_a),
                                                          "f_B": float(f_b),
                                                          "ratio": float(f_a / f_b)}


def compact_score(scored: dict[str, Any]) -> dict[str, Any]:
    return {"recovery": scored["recovery"],
            "overshoot_projection": scored["aggregate"]["overshoot_projection"],
            "recovery_by_region": scored["recovery_by_region"],
            "informational": {k: v["recovery"] for k, v in
                              scored["informational_regions"].items()}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    sources = scm.verify_historical_sources()

    pop = scm.load_populations(args.populations)
    endpoint = scm.endpoint_from_populations(pop)
    bins = build_bins(pop)
    total_rate, fractions = rate_matched_total(pop)

    pga = pop["a_pass_truth"].astype(bool)
    s1a = pga & pop["a_pass_reco"].astype(bool)
    w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]
    pgb = pop["b_pass_truth"].astype(bool)
    s1b = pgb & pop["b_pass_reco"].astype(bool)

    # the historical pushes, scored here too so every table carries its own anchor
    anchors = {name: scm.score_push(endpoint, pop[f"hist_push_{name}"], SCOREABLE, INFORMATIONAL)
               for name in ("ours127", "theirs127")}

    ks = list(range(1, args.iterations + 1))
    reference = scm.reference_curve(pop["map_acceptance"], pop["map_displacement"], ks)

    runs = []
    for reco_name, mode, norm in VARIANTS:
        t0 = time.perf_counter()
        n_reco = bins["n_reco"][reco_name]
        records = []
        prev = np.ones(pgb.size)
        for step in bu.binned_omnifold(
                reco_bin_mc=bins["b"][reco_name], truth_bin_mc=bins["b"]["truth"],
                pass_reco_mc=s1b, pass_gen_mc=pgb,
                w_truth_mc=pop["b_w_truth"], w_reco_mc=pop["b_w_reco"],
                reco_bin_data=bins["a"][reco_name][s1a], w_data=w_data,
                n_reco_bins=n_reco, n_truth_bins=bins["n_truth"], iterations=args.iterations,
                mode=mode, data_total=(total_rate if norm == "rate_matched" else None)):
            push, pull = step["push"], step["pull"]
            reco_check = bu.reco_level_recovery(
                bins["b"]["reco_eavail7"], s1b, pop["b_w_reco"], prev, pull,
                bins["a"]["reco_eavail7"][s1a], w_data, N_EAV)
            reco_check_own = bu.reco_level_recovery(
                bins["b"][reco_name], s1b, pop["b_w_reco"], prev, pull,
                bins["a"][reco_name][s1a], w_data, n_reco)
            records.append({
                "iteration": step["iteration"],
                "push": scm.score_push(endpoint, push, SCOREABLE, INFORMATIONAL),
                "pull": compact_score(scm.score_push(endpoint, pull, SCOREABLE, INFORMATIONAL)),
                "step1_reco_eavail7_recovery": reco_check,
                "step1_own_reco_bins_recovery": reco_check_own,
                "lost_data_weight": step["lost_data"],
                "data_total": step["data_total"],
                "push_summary": scm.weight_summary(push[pgb]),
            })
            prev = push
        runs.append({"reco_binning": reco_name, "mode": mode, "normalization": norm,
                     "n_reco_bins": n_reco, "n_truth_bins": bins["n_truth"],
                     "is_estimator": reco_name != "diag",
                     "label": ("REFERENCE-MODEL REALIZATION (truth bin used as reco bin); not "
                               "an estimator" if reco_name == "diag" else "binned estimator"),
                     "seconds": time.perf_counter() - t0, "iterations": records})
        print(f"[ibu] {reco_name:12s} {mode:21s} {norm:12s} "
              + " ".join(f"k{r['iteration']}={r['push']['recovery']:.4f}"
                         for r in records if r["iteration"] in (1, 3, 5, 10, 20, 50)))

    summary = {f"{r['reco_binning']}/{r['mode']}/{r['normalization']}": {
        str(rec["iteration"]): {"aggregate": rec["push"]["recovery"],
                                **rec["push"]["recovery_by_region"]}
        for rec in r["iterations"] if rec["iteration"] in (1, 2, 3, 4, 5, 10, 20, 30, 50)}
        for r in runs}
    payload = {
        "schema": "phase-b1-ibu/1",
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "inputs": {"populations_npz": str(args.populations),
                   "populations_npz_sha256": scm.sha256_file(args.populations)},
        "endpoint": {"edges_gev": pop["endpoint_edges"].tolist(),
                     "scoreable_regions": list(SCOREABLE),
                     "informational_regions": list(INFORMATIONAL),
                     "n_prior_scored": int(endpoint.n_prior),
                     "n_target_scored": int(np.asarray(endpoint.eavail_a).size)},
        "event_counts": {"prior_rows": int(pgb.size), "prior_pass_gen": int(pgb.sum()),
                         "prior_pass_reco_and_gen": int(s1b.sum()),
                         "pseudodata_rows": int(s1a.sum())},
        "binning": {"truth": "7 endpoint E_avail bins x 285 (pT,p_par) cells (+1 off-grid cell)",
                    "n_truth_bins": bins["n_truth"], "n_reco_bins": bins["n_reco"],
                    "census": census(pop, bins)},
        "accepted_fraction": fractions,
        "rate_matched_data_total": total_rate,
        "reference_curve": reference,
        "historical_anchors": anchors,
        "summary": summary,
        "runs": runs,
        "seconds": time.perf_counter() - started,
        "scope": ("simulation-only diagnostic of the historical closure endpoint; PET is "
                  "diagnostic method development; the diag rows are a reference-model "
                  "realization, not an attainability bound and not an estimator"),
    }
    scm.write_json(args.output, payload, compact=True)
    print(f"[ibu] wrote {args.output} in {time.perf_counter() - started:.1f}s")


if __name__ == "__main__":
    main()
