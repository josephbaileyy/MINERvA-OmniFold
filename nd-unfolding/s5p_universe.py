#!/usr/bin/env python3
"""s5p Stage 4: weight-only systematic universes on the negweight-refined npz path.

For each requested universe ``BAND:IDX`` of the background-aware vertical bank (``sweep_bank_5d.py
--dump``, directory ``--bank``: per-universe POT-scaled signal truth/reco weights ``{tag}_wt/_wr``,
truth-denominator weights ``{tag}_tdw`` and background event weights ``{tag}_bkgw``, row-aligned with
``of_inputs_5d.npz`` and with the s5c background dump), the real data are unfolded with EVERY universe
weight in place of its CV counterpart:

* the unfolding MC's ``w_truth`` / ``w_reco`` -> the universe's signal weights;
* the completeness denominator -> the universe's truth-denominator histogram (``cv.npz`` truth-denominator
  coordinates weighted by ``{tag}_tdw``);
* the background template (the s5c dump's reco coordinates) -> the universe's background weights, so the
  signed sample {data at +1} U {template at -w_bkg,u} and its Stay-Positive refinement are REFIT per
  universe (handoff Stage 4);
* a ``Flux`` universe divides by its own integrated flux (``flux_universe.flux_universe_bins``, the J28
  rule), every other band by the CV flux.

The estimator is the declared configuration (R plus optional OmniFold capacity and iteration count, as in
``s5p_numerics``), the measured side ``s5e_trace.measured_side`` and the unfold ``s5c_unfold.unfold``.
``--universe CV`` runs the same code with the npz's own CV weights, denominator and background weights: it
must reproduce the configuration's central product bitwise (the construction's matched-CV control).

Row alignment is CHECKED before any unfold: the bank's ``cv.npz`` must match the npz in MC reco
coordinates, pass flags and measured events, and its MC truth coordinates everywhere except the declared
2,801 sentinel rows (NaN in the bank, -9999 in the npz); its background columns must equal the dump's.

MEASURES: one universe's unfolded real-data cross section on the negweight-refined footing. CANNOT
AUTHORIZE: a covariance, its assembly or interpretation, or any adoption by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

SENTINEL_ROWS = 2801


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def check_alignment(bank_cv, inputs: dict, bkg: dict) -> dict:
    """The bank must describe the npz's rows; returns the evidence or raises."""
    g_b, g_n = np.asarray(bank_cv["MCgen"]), np.asarray(inputs["MCgen"])
    if g_b.shape != g_n.shape:
        raise RuntimeError(f"bank MC rows {g_b.shape} != npz {g_n.shape}")
    for key in ("MCreco", "pass_reco", "pass_truth", "measured"):
        if not np.array_equal(np.asarray(bank_cv[key]), np.asarray(inputs[key])):
            raise RuntimeError(f"bank {key} differs from the npz")
    differ = np.any(g_b != g_n, axis=1)
    sentinel = np.any(np.isnan(g_b), axis=1) & np.any(g_n < -9000, axis=1)
    if np.any(differ & ~sentinel) or int(sentinel.sum()) != SENTINEL_ROWS:
        raise RuntimeError(f"bank MCgen differs outside the sentinel rows ({int((differ & ~sentinel).sum())} rows; "
                           f"{int(sentinel.sum())} sentinel rows, expected {SENTINEL_ROWS})")
    if not np.array_equal(np.asarray(bank_cv["bkg_cols"]), np.asarray(bkg["bkg_reco"])):
        raise RuntimeError("bank background columns differ from the background dump")
    return {"mc_rows": int(g_b.shape[0]), "sentinel_rows": int(sentinel.sum()), "measured_rows": int(inputs["measured"].shape[0]),
            "bkg_rows": int(bkg["bkg_reco"].shape[0])}


def weight_keys(bank: Path, tag: str) -> tuple[str, ...]:
    """A vertical-bank universe carries truth-denominator event weights (tdw); a detector-dump universe
    (s5p_input_dumps.py detector) carries its denominator histogram (denom_nd) instead."""
    return ("wt", "wr", "denom_nd", "bkgw") if (bank / f"{tag}_denom_nd.npy").exists() else ("wt", "wr", "tdw", "bkgw")


def weights(bank: Path, tag: str) -> dict:
    out = {}
    for key in weight_keys(bank, tag):
        w = np.load(bank / f"{tag}_{key}.npy", mmap_mode="r").astype(np.float64)
        np.nan_to_num(w, copy=False, nan=0.0, posinf=0.0, neginf=0.0)  # sweep_bank_5d.do_run's rule
        out[key] = w
    return out


def denominator(bank_cv, tdw: np.ndarray, edges: list) -> np.ndarray:
    coords = np.column_stack([np.asarray(bank_cv[k], np.float64) for k in ("td_pt", "td_pz", "td_ea", "td_q3", "td_w")])
    dn, _ = np.histogramdd(coords, bins=[np.asarray(e, float) for e in edges], weights=tdw)
    return dn


def universe_inputs(inputs: dict, bkg: dict, bank_cv, w: dict, band: str, idx: str, flux_file: Path | None) -> tuple[dict, dict, dict]:
    ui = dict(inputs)
    ui["w_truth"], ui["w_reco"] = w["wt"], w["wr"]
    ui["denom_nd"] = w["denom_nd"] if "denom_nd" in w else denominator(bank_cv, w["tdw"], inputs["edges"])
    ub = dict(bkg)
    ub["bkg_w"] = w["bkgw"]
    info = {}
    if band == "Flux":
        if flux_file is None:
            raise RuntimeError("a Flux universe needs --flux-universe-file")
        import flux_universe
        cv_flux = np.asarray(inputs["flux"], float)
        ui["flux"] = flux_universe.flux_universe_bins(str(flux_file), idx, np.asarray(inputs["edges"][0], float), cv_flux)
        info["flux_ratio_mean"] = float(np.mean(ui["flux"] / cv_flux))
    pt = np.asarray(inputs["pass_truth"], bool)
    ratio = w["wt"][pt] / np.where(np.asarray(inputs["w_truth"], float)[pt] > 0, np.asarray(inputs["w_truth"], float)[pt], np.nan)
    info["wt_over_cv_median"] = float(np.nanmedian(ratio))
    info["denom_over_cv_total"] = float(ui["denom_nd"].sum() / np.asarray(inputs["denom_nd"], float).sum())
    info["bkgw_over_cv_total"] = float(w["bkgw"].sum() / np.asarray(bkg["bkg_w"], float).sum())
    return ui, ub, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--bank", type=Path, required=True, help="the vertical bank (its cv.npz is the alignment reference)")
    ap.add_argument("--weights-dir", type=Path, default=None,
                    help="where the universe weight files live (default --bank; a detector dump directory)")
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--universes", required=True, help="BAND:IDX[,BAND:IDX...] or CV")
    ap.add_argument("--flux-universe-file", type=Path, default=None)
    ap.add_argument("--config", choices=("R",), default="R")
    ap.add_argument("--capacity", default=None)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", type=Path, required=True, help="output directory")
    a = ap.parse_args(argv)
    s5e_candidate.install(a.config)
    capacity = s5e_trace.parse_pair(a.capacity)
    t0 = time.time()
    npz_sha, bkg_sha = s5n_pseudo.sha256_path(a.npz), s5n_pseudo.sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print(f"input digests {npz_sha} / {bkg_sha} differ from the expected ones", file=sys.stderr)
        return 4
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bank_cv = np.load(a.bank / "cv.npz", allow_pickle=True)
    alignment = check_alignment(bank_cv, inputs, bkg)
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for item in a.universes.split(","):
        tag = "CV" if item == "CV" else item.replace(":", "_")
        target = a.out / f"{a.tag}_{tag}.npz"
        if target.exists():
            continue
        t1 = time.time()
        if item == "CV":
            ui, ub, info, digests = inputs, bkg, {"cv_control": True}, {}
        else:
            band, _, idx = item.partition(":")
            wdir = a.weights_dir or a.bank
            w = weights(wdir, tag)
            ui, ub, info = universe_inputs(inputs, bkg, bank_cv, w, band, idx, a.flux_universe_file)
            digests = {k: file_sha(wdir / f"{tag}_{k}.npy") for k in weight_keys(wdir, tag)}
        exp = s5n_pseudo.build_data(ui, ub)
        with s5p_numerics.omnifold_capacity(capacity):
            xs, ev = s5p_numerics.unfold_one(exp, np.float32, a.estimator_seed, a.threads, a.iters)
        meta = {"schema": "s5p-universe/1", "universe": item, "config": a.config, "capacity": capacity, "iters": a.iters,
                "estimator_seed": a.estimator_seed, "threads": a.threads, "input_npz_sha256": npz_sha,
                "bkg_dump_sha256": bkg_sha, "bank": str(a.bank), "bank_weight_sha256": digests,
                "flux_universe_file": None if a.flux_universe_file is None else str(a.flux_universe_file),
                "alignment": alignment, "universe_info": info, **ev,
                "code_sha256": {**s5n_pseudo.code_digests(), "s5p_universe.py": s5n_pseudo.sha256_path(Path(__file__).resolve()),
                                "s5p_numerics.py": s5n_pseudo.sha256_path(_ND / "s5p_numerics.py"),
                                "s5e_trace.py": s5n_pseudo.sha256_path(_ND / "s5e_trace.py")},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
                "seconds_load": round(t1 - t0, 3), "seconds_unfold": round(time.time() - t1, 3)}
        rc = s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"), "shape": np.array(xs.shape)}, meta)
        status |= rc
        print(json.dumps({"out": target.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"], **info}))
        t0 = time.time()
    return status


if __name__ == "__main__":
    sys.exit(main())
