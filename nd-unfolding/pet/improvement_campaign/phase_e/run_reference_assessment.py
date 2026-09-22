"""Reference assessment (b): response-aware references at the historical size and at 8x, pool S.

Amendment 1 (b): binned IBU with reco E_avail at the historical sample size and at 8x larger
samples, "separating the finite-sample from the definitional part" of the gap between the
historical reference (0.695 at k = 3) and what a response-aware estimator reaches.

Three things are computed on the SAME pool-S draws, at k = 1..K:

* **IBU, reco = (p_T, p_par) cells x reco E_avail**, both miss-handling modes (misses carried, the
  engine's rule; and textbook efficiency-corrected) -- the response-aware reference;
* **`diag`** -- the event's own truth bin used as its reco bin. Not an estimator: it is the
  reference model's own assumptions (acceptance only, no smearing, misses carried) realized on
  this population and scored by the actual statistic;
* the **analytic reference model** `1-(1-a)^k` (`reference_calibration.ceiling`) on pool S's own
  acceptance and displacement maps, built exactly as `report_campaign.build_endpoint` builds the
  historical ones.

The difference between the 1x and 8x runs is the finite-sample part; what survives at 8x is
definitional (binning, smearing, miss handling, normalization). Prospective recommendations only:
none of this changes the historical reference, floor or verdict.

Pool S holds 18.86 M events, so three 8x replicates (9.60 M events each) cannot be disjoint. That
family declares `disjoint=False` and its measured pairwise overlap is reported with every number
that comes from it.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

import common as cm
import distortions as dist
import replicates as rp

if str(cm.SCALAR_DIR) not in sys.path:
    sys.path.insert(0, str(cm.SCALAR_DIR))
import binned_unfolding as bu       # noqa: E402
import run_ibu                       # noqa: E402

scm = cm.scm
N_EAV = 7
INJECTION = "D1_p0.350"
FULL_AT = (1, 2, 3, 5, 10, 20, 30)


def pool_maps(cache: dict[str, np.ndarray], weight: np.ndarray, edges_pt: np.ndarray,
              edges_pz: np.ndarray) -> dict[str, np.ndarray]:
    """The acceptance / prior-mass / displacement cell maps of a whole pool, built exactly as
    `report_campaign.build_endpoint` builds the historical ones (w_truth on both legs)."""
    pt, pz = cache["truth"][:, 0], cache["truth"][:, 1]
    w = cache["w_truth"]
    both = cache["pass_reco"]
    denom, _, _ = np.histogram2d(pt, pz, bins=[edges_pt, edges_pz], weights=w)
    numer, _, _ = np.histogram2d(pt[both], pz[both], bins=[edges_pt, edges_pz], weights=w[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acceptance = np.where(denom > 0, numer / denom, 0.0)
    prior_f = (denom / denom.sum()).ravel()
    target, _, _ = np.histogram2d(pt, pz, bins=[edges_pt, edges_pz], weights=w * weight)
    return {"acceptance": acceptance.ravel(), "prior_mass": prior_f,
            "displacement": np.abs((target / target.sum()).ravel() - prior_f)}


def run_ibu_variant(prior: dict[str, np.ndarray], pseudo: dict[str, np.ndarray],
                    w_dist: np.ndarray, targets: dict[str, np.ndarray], binning: str, mode: str,
                    n_cells: int, edges: np.ndarray, iterations: int) -> dict[str, Any]:
    s1p, s1d = prior["pass_reco"], pseudo["pass_reco"]
    tcell = np.where(prior["truth_cell"] >= 0, prior["truth_cell"], n_cells).astype(np.int64)
    truth_bin = tcell * N_EAV + run_ibu.eavail_bin(prior["truth"][:, 2], edges)
    if binning == "muon_eavail":
        rcell = np.where(prior["reco_cell"] >= 0, prior["reco_cell"], n_cells).astype(np.int64)
        reco_bin = rcell * N_EAV + run_ibu.eavail_bin(prior["reco"][:, 2], edges)
        dcell = np.where(pseudo["reco_cell"] >= 0, pseudo["reco_cell"], n_cells).astype(np.int64)
        data_bin = (dcell * N_EAV + run_ibu.eavail_bin(pseudo["reco"][:, 2], edges))[s1d]
    else:                                     # diag: the truth bin used as the reco bin
        reco_bin = truth_bin
        dtcell = np.where(pseudo["truth_cell"] >= 0, pseudo["truth_cell"], n_cells).astype(np.int64)
        data_bin = (dtcell * N_EAV + run_ibu.eavail_bin(pseudo["truth"][:, 2], edges))[s1d]
    n_bins = (n_cells + 1) * N_EAV
    rows = []
    for step in bu.binned_omnifold(
            reco_bin_mc=reco_bin, truth_bin_mc=truth_bin, pass_reco_mc=s1p,
            pass_gen_mc=np.ones(prior["rows"].size, bool), w_truth_mc=prior["w_truth"],
            w_reco_mc=prior["w_reco"], reco_bin_data=data_bin,
            w_data=pseudo["w_reco"][s1d] * w_dist[s1d], n_reco_bins=n_bins, n_truth_bins=n_bins,
            iterations=iterations, mode=mode):
        full = cm.score(prior["truth"][:, 2], prior["w_truth"], step["push"], prior["region"],
                        targets)
        row = {"iteration": step["iteration"], "recovery": full["recovery"],
               "recovery_by_region": full["recovery_by_region"],
               "overshoot_projection": full["aggregate"]["overshoot_projection"],
               "lost_data_weight": step["lost_data"]}
        if step["iteration"] in FULL_AT:
            row["full"] = cm.compact_score(full)
        rows.append(row)
    best = max(rows, key=lambda r: r["recovery"])
    return {"binning": binning, "mode": mode, "n_bins": n_bins, "iterations": rows,
            "best": {"iteration": best["iteration"], "recovery": best["recovery"]},
            "is_estimator": binning != "diag"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--prepare", type=Path, required=True)
    ap.add_argument("--b1-populations", type=Path, required=True)
    ap.add_argument("--iterations", type=int, default=30)
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--scale", type=int, nargs="*", default=[1, 8])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    t0 = time.perf_counter()
    prep = json.loads(args.prepare.read_text())
    cache = cm.load_cache(args.cache, prep["caches"]["S"]["sha256"])
    b1_sha = scm.sha256_file(args.b1_populations)
    if b1_sha != cm.B1_POPULATIONS_SHA256:
        raise SystemExit("[assess] B1 populations.npz sha256 differs from the committed one")
    with np.load(args.b1_populations, allow_pickle=False) as b1:
        edges_pt = np.asarray(b1["edges_pt"], float)
        edges_pz = np.asarray(b1["edges_pz"], float)
        endpoint_edges = np.asarray(b1["endpoint_edges"], float)
    n_cells = (edges_pt.size - 1) * (edges_pz.size - 1)

    injection = dist.registry()[INJECTION]
    pool_w = dist.normalize_unit_mean(injection.truth_weight(cm.truth_view(cache)))
    targets = cm.target_spectra(cache["truth"][:, 2], cache["w_truth"], pool_w, cache["region"])
    maps = pool_maps(cache, pool_w, edges_pt, edges_pz)
    ks = list(range(1, args.iterations + 1))
    reference = scm.reference_curve(maps["acceptance"], maps["displacement"], ks)

    runs: dict[str, Any] = {}
    draws: dict[str, Any] = {}
    for scale in args.scale:
        n_prior = cm.HISTORICAL_SIZES["prior"] * scale
        n_pseudo = cm.HISTORICAL_SIZES["pseudo"] * scale
        design = rp.ReplicateDesign("S", f"E1-assessment-{scale}x", n_prior=n_prior,
                                    n_pseudo=n_pseudo,
                                    disjoint=(args.replicates * (n_prior + n_pseudo)
                                              <= cache["rows"].size))
        reps, record = rp.draw_replicates(design, list(range(args.replicates)), cache["rows"],
                                          cache["identity"])
        draws[f"{scale}x"] = record
        for rep in reps:
            prior = cm.take(cache, rep.prior_rows)
            pseudo = cm.take(cache, rep.pseudo_rows)
            w_dist = dist.normalize_unit_mean(injection.truth_weight(cm.truth_view(pseudo)))
            variants = [("muon_eavail", bu.MODE_CARRY_MISSES),
                        ("muon_eavail", bu.MODE_EFFICIENCY_CORRECTED),
                        ("diag", bu.MODE_CARRY_MISSES)]
            for binning, mode in variants:
                key = f"{scale}x/r{rep.replicate}/{binning}/{mode}"
                t1 = time.perf_counter()
                runs[key] = run_ibu_variant(prior, pseudo, w_dist, targets, binning, mode,
                                            n_cells, endpoint_edges, args.iterations)
                runs[key].update({"scale": scale, "replicate": rep.replicate,
                                  "n_prior": int(prior["rows"].size),
                                  "n_pseudo": int(pseudo["rows"].size),
                                  "seconds": time.perf_counter() - t1})
                r = runs[key]["iterations"]
                shown = " ".join(f"k{k}={r[k - 1]['recovery']:.4f}" for k in (1, 3, 10)
                                 if k <= len(r))
                print(f"[assess] {key:44s} {shown} best={runs[key]['best']['recovery']:.4f}"
                      f"@{runs[key]['best']['iteration']} ({runs[key]['seconds']:.0f}s)",
                      flush=True)

    def across(scale: int, binning: str, mode: str, k: int) -> dict[str, float]:
        vals = [runs[f"{scale}x/r{r}/{binning}/{mode}"]["iterations"][k - 1]["recovery"]
                for r in range(args.replicates)
                if f"{scale}x/r{r}/{binning}/{mode}" in runs
                and k <= len(runs[f"{scale}x/r{r}/{binning}/{mode}"]["iterations"])]
        if not vals:
            return None
        return {"mean": float(np.mean(vals)), "sd": float(np.std(vals, ddof=1)) if len(vals) > 1
                else None, "values": vals}

    summary = {f"{binning}/{mode}": {
        f"{scale}x": {f"k{k}": across(scale, binning, mode, k)
                      for k in (1, 2, 3, 5, 10, 20, 30) if k <= args.iterations}
        for scale in args.scale}
        for binning, mode in (("muon_eavail", bu.MODE_CARRY_MISSES),
                              ("muon_eavail", bu.MODE_EFFICIENCY_CORRECTED),
                              ("diag", bu.MODE_CARRY_MISSES))}

    payload = {
        "schema": "phase-e-reference-assessment/1", "commit": scm.repo_commit(),
        "historical_sources": getattr(cm.historical, "_verified", None),
        "pool": "S", "pool_rows": int(cache["rows"].size),
        "injection": {"id": INJECTION, "spec": injection.spec(),
                      "content_hash": injection.content_hash(),
                      "pool_weight_summary": scm.weight_summary(pool_w)},
        "reference_model": {"curve": reference,
                            "construction": "reference_calibration.ceiling on pool S's own "
                                            "acceptance and displacement cell maps, built as "
                                            "report_campaign.build_endpoint builds them"},
        "target": {"source": "all of pool S", "aggregate_hist": targets["aggregate"].tolist()},
        "draws": draws, "summary": summary, "runs": runs,
        "inputs": {"cache": str(args.cache), "cache_sha256": prep["caches"]["S"]["sha256"],
                   "b1_populations_sha256": b1_sha},
        "environment": cm.environment(), "seconds": time.perf_counter() - t0,
        "scope": ("simulation-only reference assessment on pool S; a prospective recommendation "
                  "only, never a change to the historical reference, floor or verdict"),
    }
    cm.write_json(args.output, payload)
    print(f"[assess] wrote {args.output} in {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
