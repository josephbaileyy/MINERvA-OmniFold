"""The scalar references under every predeclared distortion (Amendment 1), on pool T.

For one replicate of the `E1-references` family (prior 600,130 events, pseudodata 600,111 events,
disjoint, drawn by identity hash) and a chunk of the predeclared cases, this runs the two Phase-B1
scalar references that see reco E_avail:

* **binned IBU** -- the engine's own algorithm on bins (`phase_b/scalar/binned_unfolding.py`),
  reco binning = the historical (p_T, p_par) reporting cells x the seven reco E_avail bins, misses
  carried, the engine's pseudodata normalization -- at k = 1..K, so k = 3, k = 10 and IBU's best k
  are all measured on the same run;
* **GBDT OmniFold** -- the scalar OmniFold loop (`phase_b/scalar/scalar_omnifold.py`) with a
  HistGradientBoosting ratio on (reco p_T, p_par, E_avail) at step 1 and the four truth scalars at
  step 2, at k = 1..10.

The target is the distorted truth spectrum over ALL of pool T (8.0 M events), so an estimator is
scored against the population it should recover, not against a second sample. For a response-only
case (R1-R3 with no truth distortion) the target is the UNDISTORTED pool-T spectrum: the correct
answer is to do nothing, and what is reported is the spurious displacement, with the prior's own
distance to the target as the finite-sample baseline. For D3 and D4 the joint (E_avail, q3) and
(E_avail, p_T) recoveries on the reporting grid are reported too, as Amendment 1 requires.

These are the yardsticks PET candidates will later be compared against under the same distortions.
Nothing here is an attainability bound, a threshold, or a publication product.
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
import scalar_omnifold as so         # noqa: E402

scm = cm.scm
N_EAV = 7
FULL_AT = (3, 10)


def build_bins(cache_like: dict[str, np.ndarray], n_cells: int, edges: np.ndarray,
               reco: dict[str, np.ndarray] | None = None, reco_cell: np.ndarray | None = None
               ) -> dict[str, np.ndarray]:
    """Truth and reco bin indices: (cell, +1 off-grid cell) x the seven endpoint E_avail bins."""
    tcell = np.where(cache_like["truth_cell"] >= 0, cache_like["truth_cell"], n_cells)
    teav = run_ibu.eavail_bin(cache_like["truth"][:, 2], edges)
    out = {"truth": tcell.astype(np.int64) * N_EAV + teav}
    if reco is not None:
        rc = np.where(reco_cell >= 0, reco_cell, n_cells)
        out["reco"] = rc.astype(np.int64) * N_EAV + run_ibu.eavail_bin(reco["eavail"], edges)
        out["reco_eavail7"] = run_ibu.eavail_bin(reco["eavail"], edges)
    return out


def case_weights(case: dist.Case, pseudo: dict[str, np.ndarray], cache: dict[str, np.ndarray]
                 ) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, Any]]:
    """(pseudodata truth weight, pool-level target spectra, record) for one case."""
    if case.truth is None:
        w = np.ones(pseudo["rows"].size)
        pool_w = np.ones(cache["rows"].size)
        rec = {"truth_distortion": None}
    else:
        w = dist.normalize_unit_mean(case.truth.truth_weight(cm.truth_view(pseudo)))
        pool_w = dist.normalize_unit_mean(case.truth.truth_weight(cm.truth_view(cache)))
        rec = {"truth_distortion": case.truth.spec(),
               "truth_hash": case.truth.content_hash(),
               "pseudodata_weight_summary": scm.weight_summary(w),
               "pool_weight_summary": scm.weight_summary(pool_w)}
    targets = cm.target_spectra(cache["truth"][:, 2], cache["w_truth"], pool_w, cache["region"])
    return w, targets, rec


def transformed_reco(case: dist.Case, pseudo: dict[str, np.ndarray], mask: np.ndarray,
                     edges_pt: np.ndarray, edges_pz: np.ndarray
                     ) -> tuple[dict[str, np.ndarray], np.ndarray, dict[str, Any]]:
    """The pseudodata's reco quantities after the case's response distortion (if any), with the
    reco cell recomputed (R2 moves the muon, so it moves the cell)."""
    cr = cm.historical()["cr"]
    base = cm.reco_view(pseudo, mask)
    if case.reco is None:
        return base, pseudo["reco_cell"][mask], {"reco_distortion": None}
    noise = dist.token_noise(pseudo["identity"][mask]) if case.reco.family == "R3" else None
    moved = case.reco.transform(base, noise)
    cell = cr.cell_index_of_events(moved["pt"], moved["ppar"], edges_pt, edges_pz)
    rec = {"reco_distortion": case.reco.spec(), "reco_hash": case.reco.content_hash(),
           "moved_reco_cells": int((cell != pseudo["reco_cell"][mask]).sum()),
           "reco_eavail_mean_ratio": float(np.mean(moved["eavail"] / base["eavail"]))}
    return moved, cell, rec


def joint_scores(case: dist.Case, prior: dict[str, np.ndarray], push: np.ndarray,
                 cache: dict[str, np.ndarray], pool_w: np.ndarray, edges_pt: np.ndarray
                 ) -> dict[str, Any]:
    """Recovery of the joint (E_avail, q3) and (E_avail, p_T) histograms on the reporting grid."""
    out = {}
    for name, y_prior, y_pool, ey in (("eavail_q3", prior["truth"][:, 3], cache["truth"][:, 3],
                                       cm.Q3_EDGES),
                                      ("eavail_pt", prior["truth"][:, 0], cache["truth"][:, 0],
                                       edges_pt)):
        x_prior, x_pool = prior["truth"][:, 2], cache["truth"][:, 2]
        h_prior = cm.joint_hist(x_prior, y_prior, prior["w_truth"], cm.ENDPOINT_EDGES, ey)
        h_unf = cm.joint_hist(x_prior, y_prior, prior["w_truth"] * push, cm.ENDPOINT_EDGES, ey)
        h_tgt = cm.joint_hist(x_pool, y_pool, cache["w_truth"] * pool_w, cm.ENDPOINT_EDGES, ey)
        out[name] = cm.joint_recovery(h_prior, h_unf, h_tgt)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--prepare", type=Path, required=True)
    ap.add_argument("--b1-populations", type=Path, required=True)
    ap.add_argument("--replicate", type=int, required=True)
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--chunks", type=int, default=1)
    ap.add_argument("--ibu-iterations", type=int, default=30)
    ap.add_argument("--omnifold-iterations", type=int, default=10)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--stop-after-seconds", type=float, default=0.0,
                    help="start no further case once this much time has passed (0 = no limit); "
                         "for short `debug`-QOS jobs, so a chunk ends cleanly and names what is "
                         "left instead of being killed")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    t0 = time.perf_counter()
    args.output_dir = scm.refuse_historical_output(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prep = json.loads(args.prepare.read_text())
    cache = cm.load_cache(args.cache, prep["caches"]["T"]["sha256"])
    b1_sha = scm.sha256_file(args.b1_populations)
    if b1_sha != cm.B1_POPULATIONS_SHA256:
        raise SystemExit("[refs] B1 populations.npz sha256 differs from the committed one")
    with np.load(args.b1_populations, allow_pickle=False) as b1:
        edges_pt = np.asarray(b1["edges_pt"], float)
        edges_pz = np.asarray(b1["edges_pz"], float)
        endpoint_edges = np.asarray(b1["endpoint_edges"], float)
    n_cells = (edges_pt.size - 1) * (edges_pz.size - 1)
    if int(cache["truth_cell"].max()) >= n_cells:
        raise SystemExit("[refs] cached cell index outside the historical reporting grid")

    reg = dist.registry()
    all_cases = dist.cases(reg)
    names = sorted(all_cases) if args.only is None else list(args.only)
    names = [n for i, n in enumerate(names) if i % args.chunks == args.chunk]

    design = rp.ReplicateDesign("T", "E1-references", n_prior=cm.HISTORICAL_SIZES["prior"],
                                n_pseudo=cm.HISTORICAL_SIZES["pseudo"])
    reps, draw_record = rp.draw_replicates(design, [args.replicate], cache["rows"],
                                           cache["identity"])
    prior = cm.take(cache, reps[0].prior_rows)
    pseudo = cm.take(cache, reps[0].pseudo_rows)
    s1p = prior["pass_reco"]
    s1d = pseudo["pass_reco"]
    prior_bins = build_bins(prior, n_cells, endpoint_edges,
                            reco=cm.reco_view(prior), reco_cell=prior["reco_cell"])
    n_bins = (n_cells + 1) * N_EAV
    X_gen_prior = np.stack([prior["truth"][:, 2], prior["truth"][:, 0], prior["truth"][:, 1],
                            prior["truth"][:, 3]], axis=1)
    bad = ~np.isfinite(X_gen_prior)
    gen_fill = {}
    if bad.any():
        for j in range(X_gen_prior.shape[1]):
            col = X_gen_prior[:, j]
            if (~np.isfinite(col)).any():
                gen_fill[str(j)] = {"rows": int((~np.isfinite(col)).sum()),
                                    "value": float(np.median(col[np.isfinite(col)]))}
                col[~np.isfinite(col)] = gen_fill[str(j)]["value"]
    X_reco_prior = np.stack([prior["reco"][:, 0], prior["reco"][:, 1], prior["reco"][:, 2]], axis=1)
    if not np.isfinite(X_reco_prior[s1p]).all() or not np.isfinite(X_gen_prior).all():
        raise SystemExit("[refs] non-finite inputs on rows a step uses (fail closed)")

    results: dict[str, Any] = {}
    path = args.output_dir / f"references_r{args.replicate}_c{args.chunk}of{args.chunks}.json"

    def payload() -> dict[str, Any]:
        return {
            "schema": "phase-e-references/1", "commit": scm.repo_commit(),
            "historical_sources": getattr(cm.historical, "_verified", None),
            "replicate": args.replicate, "chunk": [args.chunk, args.chunks], "cases": names,
            "cases_done": sorted(results), "cases_remaining": [n for n in names if n not in results],
            "design": {"draw": draw_record, "prior_rows": int(prior["rows"].size),
                       "pseudodata_rows": int(pseudo["rows"].size),
                       "prior_pass_reco": int(s1p.sum()),
                       "pseudodata_pass_reco": int(s1d.sum()),
                       "ibu": {"reco_binning": "(p_T,p_par) cell x 7 reco E_avail bins",
                               "n_bins": n_bins, "modes": list(bu.MODES),
                               "normalization": "engine (both legs to 1e6)"},
                       "gbdt": {"classifier": so.HGBRatio(seed=0).params,
                                "reco_features": ["reco_pt", "reco_pparallel", "reco_eavail"],
                                "truth_features": ["true_eavail", "true_pt", "true_pparallel",
                                                   "true_q3"],
                                "truth_median_fills": gen_fill},
                       "endpoint_edges": endpoint_edges.tolist()},
            "inputs": {"cache": str(args.cache), "cache_sha256": prep["caches"]["T"]["sha256"],
                       "prepare": str(args.prepare), "b1_populations_sha256": b1_sha},
            "results": results, "environment": cm.environment(),
            "seconds": time.perf_counter() - t0,
            "scope": ("simulation-only scalar references under predeclared distortions on pool T; "
                      "not a bound, not a threshold; PET is diagnostic method development"),
        }

    for name in names:
        if args.stop_after_seconds and time.perf_counter() - t0 > args.stop_after_seconds:
            print(f"[refs] time budget reached; {len(names) - len(results)} cases left", flush=True)
            break
        case = all_cases[name]
        t_case = time.perf_counter()
        w_dist, targets, rec = case_weights(case, pseudo, cache)
        reco_d, cell_d, rec_reco = transformed_reco(case, pseudo, s1d, edges_pt, edges_pz)
        rec.update(rec_reco)
        data_bins = (np.where(cell_d >= 0, cell_d, n_cells).astype(np.int64) * N_EAV
                     + run_ibu.eavail_bin(reco_d["eavail"], endpoint_edges))
        data_eav7 = run_ibu.eavail_bin(reco_d["eavail"], endpoint_edges)
        w_data = pseudo["w_reco"][s1d] * w_dist[s1d]
        pool_w = (np.ones(cache["rows"].size) if case.truth is None
                  else dist.normalize_unit_mean(case.truth.truth_weight(cm.truth_view(cache))))

        def scored(push: np.ndarray, k: int) -> dict[str, Any]:
            full = cm.score(prior["truth"][:, 2], prior["w_truth"], push, prior["region"], targets)
            row = {"iteration": k, "recovery": full["recovery"],
                   "recovery_by_region": full["recovery_by_region"],
                   "overshoot_projection": full["aggregate"]["overshoot_projection"],
                   "injected_l1": full["aggregate"]["injected_l1"],
                   "residual_l1": full["aggregate"]["residual_l1"]}
            if k in FULL_AT:
                row["full"] = cm.compact_score(full)
                if case.truth is None:
                    row["spurious"] = cm.spurious_displacement(
                        prior["truth"][:, 2], prior["w_truth"], push, targets["aggregate"])
                if case.truth is not None and case.truth.family in ("D3", "D4"):
                    row["joint"] = joint_scores(case, prior, push, cache, pool_w, edges_pt)
            return row

        # ---- binned IBU, BOTH miss-handling modes -----------------------------------------
        # Phase F measured that miss handling dominates at scalar level (carry-misses k=50 0.582
        # vs efficiency-corrected 0.783 on the historical halves), and D4d (neutrons, invisible in
        # E_avail) is exactly where an efficiency correction built on the undistorted acceptance
        # should break. Both modes are therefore run under every distortion.
        ibu: dict[str, Any] = {}
        for mode in (bu.MODE_CARRY_MISSES, bu.MODE_EFFICIENCY_CORRECTED):
            rows_mode, prev = [], np.ones(prior["rows"].size)
            for step in bu.binned_omnifold(
                    reco_bin_mc=prior_bins["reco"], truth_bin_mc=prior_bins["truth"],
                    pass_reco_mc=s1p, pass_gen_mc=np.ones(prior["rows"].size, bool),
                    w_truth_mc=prior["w_truth"], w_reco_mc=prior["w_reco"],
                    reco_bin_data=data_bins, w_data=w_data, n_reco_bins=n_bins,
                    n_truth_bins=n_bins, iterations=args.ibu_iterations, mode=mode):
                row = scored(step["push"], step["iteration"])
                row["step1_reco_eavail7_recovery"] = bu.reco_level_recovery(
                    prior_bins["reco_eavail7"], s1p, prior["w_reco"], prev, step["pull"],
                    data_eav7, w_data, N_EAV)
                row["lost_data_weight"] = step["lost_data"]
                rows_mode.append(row)
                prev = step["push"]
            best = max(rows_mode, key=lambda r: r["recovery"])
            ibu[mode] = {"variant": f"muon x reco E_avail cells, {mode}, engine normalization",
                         "iterations": rows_mode,
                         "best": {"iteration": best["iteration"], "recovery": best["recovery"]}}
        ibu_rows = ibu[bu.MODE_CARRY_MISSES]["iterations"]
        ibu_eff = ibu[bu.MODE_EFFICIENCY_CORRECTED]["iterations"]

        # ---- GBDT OmniFold ---------------------------------------------------------------
        seed = 1000 + 17 * args.replicate
        of_rows: list[dict[str, Any]] = []

        def on_iteration(r: dict[str, Any]) -> None:
            row = scored(r["push"], r["iteration"])
            row["step1"] = {k: r["step1"][k] for k in ("n_iter", "val_logloss", "seconds")}
            row["step2"] = {k: r["step2"][k] for k in ("n_iter", "val_logloss", "seconds")}
            row["step1_reco_eavail7_recovery"] = bu.reco_level_recovery(
                prior_bins["reco_eavail7"], s1p, prior["w_reco"], r["prev_push"], r["pull"],
                data_eav7, w_data, N_EAV)
            row["push_summary"] = scm.weight_summary(r["push"])
            of_rows.append(row)
            print(f"[refs] {name:26s} r{args.replicate} gbdt k={r['iteration']:2d} "
                  f"R={row['recovery']:.4f}", flush=True)

        so.run_scalar_omnifold(
            X_reco_mc=X_reco_prior,
            X_reco_data=np.stack([reco_d["pt"], reco_d["ppar"], reco_d["eavail"]], axis=1),
            X_gen_mc=X_gen_prior, pass_reco_mc=s1p,
            pass_gen_mc=np.ones(prior["rows"].size, bool), w_truth_mc=prior["w_truth"],
            w_reco_mc=prior["w_reco"], w_data=w_data,
            make_step1=lambda k: so.HGBRatio(seed=seed * 1000 + k),
            make_step2=lambda k: so.HGBRatio(seed=(seed + 500) * 1000 + k),
            iterations=args.omnifold_iterations, seed=seed, callback=on_iteration)

        results[name] = {
            "case": case.spec(), "content_hash": case.content_hash(), **rec,
            "predeclared": not name.startswith("D5p_"),
            "target": {"source": "all of pool T", "rows": int(cache["rows"].size),
                       "aggregate_hist": targets["aggregate"].tolist()},
            "ibu": ibu,
            "gbdt_omnifold": {"variant": "HGB, reco (p_T, p_par, E_avail) -> truth4",
                              "seed": seed, "iterations": of_rows},
            "seconds": time.perf_counter() - t_case}
        print(f"[refs] {name:26s} r{args.replicate} IBUcarry k3={ibu_rows[2]['recovery']:.4f} "
              f"k10={ibu_rows[9]['recovery']:.4f} "
              f"IBUeff k3={ibu_eff[2]['recovery']:.4f} k10={ibu_eff[9]['recovery']:.4f} "
              f"GBDT k3={of_rows[2]['recovery']:.4f} k10={of_rows[-1]['recovery']:.4f} "
              f"({time.perf_counter() - t_case:.0f}s)", flush=True)
        cm.write_json(path, payload())           # after every case: a killed job loses one case

    cm.write_json(path, payload())
    print(f"[refs] wrote {path} in {time.perf_counter() - t0:.0f}s; "
          f"{len(results)}/{len(names)} cases", flush=True)


if __name__ == "__main__":
    main()
