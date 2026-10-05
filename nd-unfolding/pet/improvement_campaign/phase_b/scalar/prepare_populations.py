"""Reproduce the historical closure populations and cache the scalar inputs for Phase B1.

WHAT IS REPRODUCED, AND FROM WHAT. The halves are the rows the historical runs recorded about
themselves (`dump_rows_a`, `dump_rows_b`, `tilt_a` in a final-stage weights file), taken through
`report_campaign.build_endpoint` exactly as the report took them. They are then REPLAYED from the
historical split functions -- `stage_splits.rows_for_stage` / `usable_half_size` on the identity
sidecar, `closure_powered_truth_reweight.deterministic_halves` with `frozen_design.SPLITS`, and
`clipped_exponential_tilt` for the tilt -- and the replay must agree with the recorded rows bit for
bit. One line is re-derived rather than imported: the 2,000,000-row subsample
`np.sort(default_rng(0).choice(N, 2_000_000, replace=False))`, which lives inline in
`fullevent_fps_dataloader.build_fullevent_loaders` and is not callable without building every
point cloud; it is checked against the `mc_indices` the run recorded.

Then the report's own numbers are re-measured and a difference is a refusal: half sizes
(600130 / 600111, 32 dropped), the regional references, the aggregate reference 0.6949731569 at
k = 3, and the recovery the report gives two historical runs (scored both with the historical
`score_run` and with this lane's `score_push`).

WHAT IS CACHED. For every row of each half, in the recorded order: pass flags, both weight legs,
the four truth scalars, the four reco scalars, and two summaries of the STORED reco tokens (the
dump keeps at most 12 clusters, energy-descending, so these are post-truncation). Plus the
historical Endpoint arrays, the acceptance / prior-mass / displacement maps, and the two
historical pushes. Only signal-MC members of the closure npz are opened (`ALLOWED_NPZ_MEMBERS`).
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import numpy as np

import scalar_common as scm

SUBSAMPLE_MAX_EVENTS = 2_000_000       # run_arm_evaluation --max-events default; launcher passes none
STAGE = "final"
TOL = 1e-12

TRUTH_FIELDS = {
    "columns": ["pt", "pparallel", "eavail", "q3"],
    "units": "GeV",
    "npz_member": "truth_scalars",
    "branches": ["MC", "MC_pz", "MC_eavail", "MC_q3"],
    "definitions": {
        "eavail": "CVUniverse::GetEAvailableTrue()/1000 (runEventLoopOmniFold.cpp:589)",
        "q3": "CVUniverse::Getq3True()/1000 (runEventLoopOmniFold.cpp:590)",
    },
}
RECO_FIELDS = {
    "columns": ["pt", "pparallel", "eavail", "q3"],
    "units": "GeV",
    "npz_member": "reco_scalars",
    "branches": ["sim", "sim_pz", "sim_eavail", "sim_q3"],
    "definitions": {
        "pt, pparallel": "reconstructed muon transverse / longitudinal momentum",
        "eavail": ("reconstructed available energy NewEavail() -- the 3D E_avail pipeline's reco "
                   "definition (3d-unfolding/3D_OMNIFOLD_STATUS.md, stage C1)"),
        "q3": "RecoQ3(): Q^2 from the reco muon + recoil_E (runEventLoopOmniFold.cpp:246-249)",
    },
    "sentinel_on_not_pass_reco": -9999.0,
}
TOKEN_FIELDS = {
    "npz_member": "part_reco[..., 0] (cluster energy, MeV), via fullevent_fps_dataloader.build_reco_cloud",
    "tok_sumE": "sum of stored reco-cluster energies, GeV (post-truncation: at most 12 stored)",
    "tok_n": "number of stored reco clusters with nonzero energy (<= 12)",
}


def _load_members(npz: Path, names: list[str], row_sets: list[np.ndarray]
                  ) -> list[dict[str, np.ndarray]]:
    """Each named signal-MC member, read once and indexed by every row set."""
    unknown = set(names) - scm.ALLOWED_NPZ_MEMBERS
    if unknown:
        raise SystemExit(f"[prepare] refusing to open non-signal-MC members {sorted(unknown)}")
    out: list[dict[str, np.ndarray]] = [{} for _ in row_sets]
    with np.load(npz, allow_pickle=False) as handle:
        for name in names:
            arr = handle[name]
            for slot, rows in zip(out, row_sets):
                slot[name] = np.asarray(arr[rows])
            del arr
    return out


def _replay_split(mods: dict[str, Any], weights_npz: Path, identity_sidecar: Path,
                  n_rows: int) -> dict[str, Any]:
    """Replay the subsample, the stage split and the halves from the historical functions."""
    cp, fd, ss = mods["cp"], mods["fd"], mods["ss"]
    with np.load(weights_npz) as run:
        mc_indices = np.asarray(run["mc_indices"]).astype(np.int64)
        rows_a = np.asarray(run["dump_rows_a"]).astype(np.int64)
        rows_b = np.asarray(run["dump_rows_b"]).astype(np.int64)
    # Re-derived line (fullevent_fps_dataloader.build_fullevent_loaders, the `imc` draw).
    imc = np.sort(np.random.default_rng(0).choice(n_rows, min(SUBSAMPLE_MAX_EVENTS, n_rows),
                                                  replace=False))
    with np.load(identity_sidecar, mmap_mode="r") as blob:
        identity = np.asarray(blob["sig_event_id"]).astype(np.int64)[imc]
    stage_pos = ss.rows_for_stage(identity, STAGE)
    half = ss.usable_half_size(identity, STAGE)
    ja, jb = cp.deterministic_halves(stage_pos.size, half=half,
                                     seed=int(fd.SPLITS["split_seed"]))
    replay_a, replay_b = imc[stage_pos[ja]], imc[stage_pos[jb]]
    record = {
        "subsample_max_events": SUBSAMPLE_MAX_EVENTS,
        "subsample_seed": 0,
        "imc_replay_equals_recorded_mc_indices": bool(np.array_equal(imc, mc_indices)),
        "stage": STAGE,
        "stage_rows": int(stage_pos.size),
        "half_size": int(half),
        "split_seed": int(fd.SPLITS["split_seed"]),
        "stage_census": ss.census(identity),
        "replay_rows_a_equal_recorded": bool(np.array_equal(replay_a, rows_a)),
        "replay_rows_b_equal_recorded": bool(np.array_equal(replay_b, rows_b)),
        "halves_disjoint": bool(np.intersect1d(rows_a, rows_b).size == 0),
    }
    failed = [k for k in ("imc_replay_equals_recorded_mc_indices",
                          "replay_rows_a_equal_recorded", "replay_rows_b_equal_recorded",
                          "halves_disjoint") if not record[k]]
    if failed:
        raise SystemExit(f"[prepare] split replay disagrees with the recorded run: {failed}")
    return record


def _check(name: str, got: float, want: float, checks: dict[str, Any]) -> None:
    dev = abs(float(got) - float(want))
    checks[name] = {"recomputed": float(got), "report": float(want), "abs_deviation": dev,
                    "agrees": dev <= TOL}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure-npz", type=Path, required=True)
    parser.add_argument("--identity-sidecar", type=Path, required=True)
    parser.add_argument("--campaign-dir", type=Path, default=Path(scm.HISTORICAL_CAMPAIGN_DIR),
                        help="historical campaign outputs (READ ONLY)")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    out_dir = scm.refuse_historical_output(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = scm.verify_historical_sources(extra=["fullevent_fps_dataloader"])
    mods = scm.historical_modules()
    cr, rc, sc, fd, cp = mods["cr"], mods["rc"], mods["sc"], mods["fd"], mods["cp"]
    import fullevent_fps_dataloader as ffd

    w_ours = args.campaign_dir / scm.HISTORICAL_WEIGHTS[("ours", 127)]
    w_theirs = args.campaign_dir / scm.HISTORICAL_WEIGHTS[("theirs", 127)]

    # ---- 1. the historical endpoint, with its internal maps ------------------------------
    endpoint, context, maps = scm.capture_endpoint(args.closure_npz, w_ours)
    exp = scm.REPORT_EXPECTATIONS
    checks: dict[str, Any] = {}
    checks["closure_npz_sha256"] = {"recomputed": context["closure_npz"]["sha256"],
                                    "report": exp["closure_npz_sha256"],
                                    "agrees": context["closure_npz"]["sha256"]
                                    == exp["closure_npz_sha256"]}
    for key in ("half_a_rows", "half_b_rows", "half_b_rows_dropped_not_truth_passing"):
        checks[key] = {"recomputed": context[key], "report": exp[key],
                       "agrees": context[key] == exp[key]}
    for name, want in exp["regional_reference"].items():
        _check(f"regional_reference_k3/{name}", context["regional_reference"][name], want, checks)
    _check("aggregate_reference_k3",
           rc.ceiling(maps["acceptance"], maps["displacement"], 3), exp["aggregate_reference"],
           checks)
    _check("frozen_design_REFERENCE_aggregate", fd.REFERENCE["aggregate"],
           exp["aggregate_reference"], checks)
    for k, want in fd.REFERENCE["by_iterations"].items():
        _check(f"frozen_design_REFERENCE_by_iterations/{k}",
               rc.ceiling(maps["acceptance"], maps["displacement"], int(k)), want, checks)
    checks["scoreable_regions"] = {"recomputed": list(context["scoreable_regions"]),
                                   "report": exp["scoreable_regions"],
                                   "agrees": list(context["scoreable_regions"])
                                   == exp["scoreable_regions"]}

    # ---- 2. the historical runs, scored by the historical scorer AND by score_push -------
    historical_pushes = {}
    for (arm, seed), path in ((("ours", 127), w_ours), (("theirs", 127), w_theirs)):
        run = sc.load_run(path)
        hist = sc.score_run(run, endpoint, scoreable_regions=context["scoreable_regions"])
        mine = scm.score_push(endpoint, run.weights, context["scoreable_regions"])
        _check(f"historical_score_run/{arm}{seed}", hist["recovery"],
               exp["per_run_recovery"][(arm, seed)], checks)
        _check(f"score_push_mirror/{arm}{seed}", mine["recovery"], hist["recovery"], checks)
        for region, value in hist["recovery_by_region"].items():
            _check(f"score_push_mirror/{arm}{seed}/{region}",
                   mine["recovery_by_region"][region], value, checks)
        historical_pushes[f"{arm}{seed}"] = np.asarray(run.weights, dtype=np.float64)

    # ---- 3. every final run shares these halves (report_campaign's own requirement) -------
    same_halves = {}
    ref = scm.historical_modules()["rpt"]._halves_of(w_ours)
    for path in sorted((args.campaign_dir / "final").rglob("weights_*.npz")):
        same_halves[str(path.relative_to(args.campaign_dir))] = (
            scm.historical_modules()["rpt"]._halves_of(path) == ref)
    checks["all_final_runs_share_halves"] = {"n_runs": len(same_halves),
                                             "agrees": all(same_halves.values()) and
                                             len(same_halves) == 16}

    # ---- 4. replay the split from the historical functions ------------------------------
    with np.load(args.closure_npz, allow_pickle=False) as handle:
        n_rows = int(handle["pass_reco"].shape[0])
    split = _replay_split(mods, w_ours, args.identity_sidecar, n_rows)
    sidecar_sha = scm.sha256_file(args.identity_sidecar)
    checks["identity_sidecar_sha256"] = {
        "recomputed": sidecar_sha, "frozen_design": fd.PINNED_HASHES["identity_sidecar"],
        "agrees": sidecar_sha == fd.PINNED_HASHES["identity_sidecar"]}

    with np.load(w_ours) as run:
        rows_a = np.asarray(run["dump_rows_a"]).astype(np.int64)
        rows_b = np.asarray(run["dump_rows_b"]).astype(np.int64)
        tilt_a = np.asarray(run["tilt_a"]).astype(np.float64)
        pass_gen_a_rec = np.asarray(run["pass_gen_a"]).astype(bool)
        pass_gen_b_rec = np.asarray(run["pass_gen_b"]).astype(bool)

    # ---- 5. per-event arrays for both halves ----------------------------------------------
    scalar_names = ["truth_scalars", "reco_scalars", "pass_reco", "pass_truth", "w_truth",
                    "w_reco"]
    a, b = _load_members(args.closure_npz, scalar_names, [rows_a, rows_b])
    with np.load(args.closure_npz, allow_pickle=False) as handle:
        edges_pt = np.asarray(handle["edges_0"], dtype=np.float64)
        edges_pz = np.asarray(handle["edges_1"], dtype=np.float64)
    ffd.assert_extended_fps_edges(edges_pt, edges_pz)
    (parts,) = _load_members(args.closure_npz, ["part_reco"],
                             [np.concatenate([rows_a, rows_b])])
    cloud, _coord = ffd.build_reco_cloud(parts.pop("part_reco"))
    energy = cloud[:, :, 0].astype(np.float64)
    tok_sum = energy.sum(axis=1)
    tok_n = (energy != 0.0).sum(axis=1).astype(np.int16)
    del cloud, energy

    checks["pass_gen_a_recorded_equals_npz"] = {
        "agrees": bool(np.array_equal(pass_gen_a_rec, a["pass_truth"].astype(bool)))}
    checks["pass_gen_b_recorded_equals_npz"] = {
        "agrees": bool(np.array_equal(pass_gen_b_rec, b["pass_truth"].astype(bool)))}
    pg_a = a["pass_truth"].astype(bool)
    replay_tilt, tilt_spec = cp.clipped_exponential_tilt(
        a["truth_scalars"][:, 2].astype(np.float64)[pg_a],
        amplitude=float(fd.ENDPOINT["amplitude"]), clip_z=float(fd.ENDPOINT["clip"]))
    checks["tilt_replay_equals_recorded"] = {
        "max_abs_deviation": float(np.abs(replay_tilt - tilt_a[pg_a]).max()),
        "non_truth_rows_are_one": bool(np.all(tilt_a[~pg_a] == 1.0)),
        "agrees": bool(np.abs(replay_tilt - tilt_a[pg_a]).max() <= TOL
                       and np.all(tilt_a[~pg_a] == 1.0))}

    failures = sorted(k for k, v in checks.items() if not v.get("agrees", False))
    if failures:
        scm.write_json(out_dir / "populations-FAILED.json",
                       {"checks": checks, "split_replay": split, "sources": sources})
        raise SystemExit(f"[prepare] reproduction checks failed: {failures}")

    # ---- 6. census of the inputs on the rows each step uses -----------------------------
    census = {}
    for side, d in (("A", a), ("B", b)):
        pr = d["pass_reco"].astype(bool)
        pg = d["pass_truth"].astype(bool)
        s1 = pr & pg
        reco = d["reco_scalars"].astype(np.float64)
        truth = d["truth_scalars"].astype(np.float64)
        census[side] = {
            "rows": int(pr.size), "pass_reco": int(pr.sum()), "pass_truth": int(pg.sum()),
            "pass_reco_and_truth": int(s1.sum()), "reco_only_fakes": int((pr & ~pg).sum()),
            "truth_only_misses": int((~pr & pg).sum()), "neither": int((~pr & ~pg).sum()),
            "reco_scalar_nonfinite_on_s1": {c: int((~np.isfinite(reco[s1, i])).sum())
                                            for i, c in enumerate(RECO_FIELDS["columns"])},
            "reco_scalar_sentinel_on_s1": {c: int((reco[s1, i] == -9999.0).sum())
                                           for i, c in enumerate(RECO_FIELDS["columns"])},
            "reco_scalar_negative_on_s1": {c: int((reco[s1, i] < 0).sum())
                                           for i, c in enumerate(RECO_FIELDS["columns"])},
            "truth_scalar_nonfinite_on_pg": {c: int((~np.isfinite(truth[pg, i])).sum())
                                             for i, c in enumerate(TRUTH_FIELDS["columns"])},
            "sum_w_truth_on_pg": float(d["w_truth"][pg].astype(np.float64).sum()),
            "sum_w_reco_on_s1": float(d["w_reco"][s1].astype(np.float64).sum()),
            "w_reco_over_w_truth_on_s1": {
                "min": float((d["w_reco"][s1] / d["w_truth"][s1]).min()),
                "max": float((d["w_reco"][s1] / d["w_truth"][s1]).max())},
        }
    na = rows_a.size
    truth_cell_a = cr.cell_index_of_events(a["truth_scalars"][:, 0], a["truth_scalars"][:, 1],
                                           edges_pt, edges_pz)
    truth_cell_b = cr.cell_index_of_events(b["truth_scalars"][:, 0], b["truth_scalars"][:, 1],
                                           edges_pt, edges_pz)
    reco_cell_a = cr.cell_index_of_events(a["reco_scalars"][:, 0], a["reco_scalars"][:, 1],
                                          edges_pt, edges_pz)
    reco_cell_b = cr.cell_index_of_events(b["reco_scalars"][:, 0], b["reco_scalars"][:, 1],
                                          edges_pt, edges_pz)
    for side, cell, d in (("A", truth_cell_a, a), ("B", truth_cell_b, b)):
        pg = d["pass_truth"].astype(bool)
        census[side]["truth_off_grid_on_pg"] = int((cell[pg] < 0).sum())
    for side, cell, d in (("A", reco_cell_a, a), ("B", reco_cell_b, b)):
        s1 = d["pass_reco"].astype(bool) & d["pass_truth"].astype(bool)
        census[side]["reco_off_grid_on_s1"] = int((cell[s1] < 0).sum())
    # f = accepted fraction (reco leg over truth leg). The engine normalizes the pseudo-data to
    # the prior's ACCEPTED total, i.e. it assumes f_A(tilted) == f_B; the ratio is measured here.
    s1a = a["pass_reco"].astype(bool) & pg_a
    pgb = b["pass_truth"].astype(bool)
    s1b = b["pass_reco"].astype(bool) & pgb
    f_a = float((a["w_reco"][s1a] * tilt_a[s1a]).sum() / (a["w_truth"][pg_a] * tilt_a[pg_a]).sum())
    f_b = float(b["w_reco"][s1b].astype(np.float64).sum()
                / b["w_truth"][pgb].astype(np.float64).sum())
    f_a_untilted = float(a["w_reco"][s1a].astype(np.float64).sum()
                         / a["w_truth"][pg_a].astype(np.float64).sum())
    accepted_fraction = {"f_A_tilted": f_a, "f_A_untilted": f_a_untilted, "f_B": f_b,
                         "ratio_f_A_tilted_over_f_B": f_a / f_b,
                         "reading": ("the historical closure normalizes pseudo-data to the "
                                     "prior's accepted total, which is equivalent to assuming "
                                     "this ratio is 1")}

    pop_path = out_dir / "populations.npz"
    np.savez(
        pop_path,
        a_rows=rows_a, b_rows=rows_b,
        a_pass_reco=a["pass_reco"].astype(bool), a_pass_truth=pg_a,
        a_w_truth=a["w_truth"].astype(np.float64), a_w_reco=a["w_reco"].astype(np.float64),
        a_tilt=tilt_a, a_truth=a["truth_scalars"].astype(np.float64),
        a_reco=a["reco_scalars"].astype(np.float64),
        a_tok_sumE=tok_sum[:na], a_tok_n=tok_n[:na],
        a_truth_cell=truth_cell_a, a_reco_cell=reco_cell_a,
        b_pass_reco=b["pass_reco"].astype(bool), b_pass_truth=pgb,
        b_w_truth=b["w_truth"].astype(np.float64), b_w_reco=b["w_reco"].astype(np.float64),
        b_truth=b["truth_scalars"].astype(np.float64),
        b_reco=b["reco_scalars"].astype(np.float64),
        b_tok_sumE=tok_sum[na:], b_tok_n=tok_n[na:],
        b_truth_cell=truth_cell_b, b_reco_cell=reco_cell_b,
        ep_eavail_a=np.asarray(endpoint.eavail_a), ep_w_truth_a=np.asarray(endpoint.w_truth_a),
        ep_tilt_a=np.asarray(endpoint.tilt_a), ep_region_a=np.asarray(endpoint.region_a),
        ep_eavail_b=np.asarray(endpoint.eavail_b), ep_w_truth_b=np.asarray(endpoint.w_truth_b),
        ep_region_b=np.asarray(endpoint.region_b),
        ep_prior_selector=np.asarray(endpoint.prior_selector, dtype=bool),
        map_acceptance=maps["acceptance"], map_prior_mass=maps["prior_mass"],
        map_displacement=maps["displacement"],
        edges_pt=edges_pt, edges_pz=edges_pz,
        endpoint_edges=np.asarray(fd.ENDPOINT["bin_edges_gev"], dtype=np.float64),
        hist_push_ours127=historical_pushes["ours127"],
        hist_push_theirs127=historical_pushes["theirs127"],
    )
    # Endpoint reconstructed from the cache must score the historical push identically.
    rebuilt = scm.endpoint_from_populations(scm.load_populations(pop_path))
    again = scm.score_push(rebuilt, historical_pushes["ours127"], context["scoreable_regions"])
    _check("cache_roundtrip_score/ours127", again["recovery"],
           exp["per_run_recovery"][("ours", 127)], checks)
    if not checks["cache_roundtrip_score/ours127"]["agrees"]:
        raise SystemExit("[prepare] the cached endpoint does not reproduce the historical score")

    record = {
        "schema": "phase-b1-populations/1",
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "inputs": {"closure_npz": str(args.closure_npz),
                   "closure_npz_sha256": context["closure_npz"]["sha256"],
                   "identity_sidecar": str(args.identity_sidecar),
                   "identity_sidecar_sha256": sidecar_sha,
                   "weights_defining_halves": str(w_ours),
                   "weights_defining_halves_sha256": scm.sha256_file(w_ours)},
        "checks": checks,
        "all_checks_agree": True,
        "split_replay": split,
        "tilt_spec_half_A": tilt_spec,
        "context_from_build_endpoint": {k: v for k, v in context.items() if k != "census"},
        "region_census": context["census"],
        "census": census,
        "accepted_fraction": accepted_fraction,
        "fields": {"truth": TRUTH_FIELDS, "reco": RECO_FIELDS, "tokens": TOKEN_FIELDS},
        "populations_npz": {"path": str(pop_path), "sha256": scm.sha256_file(pop_path)},
        "seconds": time.perf_counter() - started,
        "scope": ("simulation-only reproduction of the historical closure populations; PET is "
                  "diagnostic method development; no real data read"),
    }
    scm.write_json(out_dir / "populations.json", record)
    print(f"[prepare] all {len(checks)} reproduction checks agree; wrote {pop_path}")
    print(f"[prepare] accepted-fraction ratio f_A(tilted)/f_B = {f_a / f_b:.6f}")


if __name__ == "__main__":
    main()
