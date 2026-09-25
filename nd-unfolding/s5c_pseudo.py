#!/usr/bin/env python3
"""One end-to-end s5c pseudo-experiment: event-level pseudo-data -> background subtraction -> unfold.

Pilots P3/P4 of ``docs/orchestration/state/s5c/pilot-contract.json`` and, once the contract is frozen,
the unit of measurement coverage, null calibration and power. Sampling model, stated so nothing is
implicit:

* MC signal rows are split once into halves A and B by the parity of a keyed 64-bit hash of the row
  index (``--split-key``). A is the unfolding MC and B the pseudo-data source; both carry weights x2
  so each half has the full sample's normalization.
* Truth: a declared reweight ``r(truth)`` (``--truth``) applied to B. The pseudo-data's true cross
  section is B's own reweighted truth, ``dn * <r>_B`` per bin, extracted exactly as the analysis does.
* REGENERATED per experiment: the signal counts ``n_i ~ Poisson(2 w_reco_i r_i)`` of every
  reco-passing B row and the background counts ``m_j ~ Poisson(w_bkg_j)`` of every background MC row,
  from ``--pseudo-seed``; the per-reco-bin purity weights, rebuilt from the pseudo-data histogram and
  the nominal background prediction; the unfold.
* FIXED (conditional): the MC halves and their finite-sample fluctuations, the background MC sample
  and its prediction, the detector model and every systematic nuisance at its nominal setting.

MEASURES: one realization of the candidate estimator's output against a known truth. CANNOT
AUTHORIZE: a coverage, size or power claim by itself; any statement about observed data.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = str(Path(__file__).resolve().parent)
if _ND not in sys.path:
    sys.path.insert(0, _ND)
import s5c_unfold  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402

TRUTHS = ("nominal", "eavail_tilt")
AXIS = {"pt": 0, "pz": 1, "eavail": 2, "q3": 3, "W": 4}


def half_mask(n: int, key: int) -> np.ndarray:
    """True for half B: parity of splitmix64(row ^ key)."""
    with np.errstate(over="ignore"):
        z = (np.arange(n, dtype=np.uint64) ^ np.uint64(key)) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return (z & np.uint64(1)).astype(bool)


def truth_weight(name: str, gen: np.ndarray, edges: list, amplitude: float) -> np.ndarray:
    if name == "nominal":
        return np.ones(gen.shape[0])
    if name == "eavail_tilt":
        e = edges[AXIS["eavail"]]
        u = (gen[:, AXIS["eavail"]] - e[0]) / (e[-1] - e[0])
        return 1.0 + amplitude * (np.clip(u, 0.0, 1.0) - 0.5)
    raise ValueError(name)


def purity_weights(coords: np.ndarray, counts: np.ndarray, bkg_nd: np.ndarray, edges: list) -> np.ndarray:
    """Vectorized build_measured_training_nd for weighted (integer-count) events."""
    data_nd, _ = np.histogramdd(coords, bins=edges, weights=counts)
    idx = [np.digitize(coords[:, k], edges[k]) - 1 for k in range(coords.shape[1])]
    shape = np.array(data_nd.shape)
    inside = np.all([(i >= 0) & (i < s) for i, s in zip(idx, shape)], axis=0)
    flat = np.zeros(coords.shape[0], dtype=np.int64)
    flat[inside] = np.ravel_multi_index([i[inside] for i in idx], data_nd.shape)
    d = data_nd.ravel()[flat]
    b = bkg_nd.ravel()[flat]
    w = np.zeros(coords.shape[0])
    ok = inside & (d > 0)
    w[ok] = np.maximum(0.0, d[ok] - b[ok]) / d[ok]
    return counts * w


def build_experiment(inputs: dict, bkg: dict, truth: str, amplitude: float, split_key: int,
                     pseudo_seed: int) -> tuple[dict, np.ndarray, dict]:
    edges = inputs["edges"]
    n = inputs["MCgen"].shape[0]
    is_b = half_mask(n, split_key)
    rng = np.random.default_rng(pseudo_seed)
    r = truth_weight(truth, inputs["MCgen"], edges, amplitude)

    b_reco = is_b & inputs["pass_reco"]
    lam = 2.0 * inputs["w_reco"][b_reco] * r[b_reco]
    n_sig = rng.poisson(lam).astype(float)
    m_bkg = rng.poisson(bkg["bkg_w"]).astype(float)
    sig_keep, bkg_keep = n_sig > 0, m_bkg > 0
    coords = np.concatenate([inputs["MCreco"][b_reco][sig_keep], bkg["bkg_reco"][bkg_keep]]).astype(np.float32)
    counts = np.concatenate([n_sig[sig_keep], m_bkg[bkg_keep]])
    mw = purity_weights(coords.astype(float), counts, bkg["bkg_nd"], edges)

    a = ~is_b
    exp_inputs = {
        "MCgen": inputs["MCgen"][a], "MCreco": inputs["MCreco"][a],
        "pass_reco": inputs["pass_reco"][a], "pass_truth": inputs["pass_truth"][a],
        "w_truth": 2.0 * inputs["w_truth"][a], "w_reco": 2.0 * inputs["w_reco"][a],
        "measured": coords, "measured_weights": mw,
        "denom_nd": inputs["denom_nd"], "flux": inputs["flux"], "data_pot": inputs["data_pot"],
        "n_nucleons": inputs["n_nucleons"], "edges": edges,
    }
    # Truth of this pseudo-data: B's reweighted truth through the analysis's own extraction.
    gen_b = inputs["MCgen"][is_b & inputs["pass_truth"]]
    wt_b = 2.0 * inputs["w_truth"][is_b & inputs["pass_truth"]]
    rw_b = r[is_b & inputs["pass_truth"]]
    unf_b, _ = np.histogramdd(gen_b, bins=edges, weights=wt_b * rw_b)
    ofin_b, _ = np.histogramdd(gen_b, bins=edges, weights=wt_b)
    dn = inputs["denom_nd"]
    comp_b = np.zeros_like(ofin_b)
    nz = dn > 0
    comp_b[nz] = ofin_b[nz] / dn[nz]
    x_true, _ = extract_cross_section_nd(unf_b, comp_b, inputs["flux"], float(inputs["data_pot"]),
                                         float(inputs["n_nucleons"]), edges)
    info = {
        "n_half_a": int(a.sum()), "n_half_b": int(is_b.sum()),
        "pseudo_signal_events": float(n_sig.sum()), "pseudo_background_events": float(m_bkg.sum()),
        "expected_signal": float(lam.sum()), "expected_background": float(np.sum(bkg["bkg_w"])),
        "measured_weight_sum": float(mw.sum()),
    }
    return exp_inputs, x_true, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--config", choices=s5c_unfold.CONFIGS, required=True)
    ap.add_argument("--estimator-seed", type=int, required=True)
    ap.add_argument("--truth", choices=TRUTHS, required=True)
    ap.add_argument("--amplitude", type=float, default=0.0)
    ap.add_argument("--split-key", type=int, required=True)
    ap.add_argument("--pseudo-seed", type=int, required=True)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--expect-npz-sha256", default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    t0 = time.time()
    npz_sha = s5c_unfold.sha256_path(a.npz)
    if a.expect_npz_sha256 and npz_sha != a.expect_npz_sha256:
        print(f"input sha256 {npz_sha} != {a.expect_npz_sha256}", file=sys.stderr)
        return 4
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bkg_meta = json.loads(str(bz["meta"]))
    if bkg_meta["npz_sha256"] != npz_sha:
        print("refusing: background dump was made against a different npz", file=sys.stderr)
        return 4
    exp_inputs, x_true, info = build_experiment(inputs, bkg, a.truth, a.amplitude, a.split_key, a.pseudo_seed)
    t1 = time.time()
    xs, params = s5c_unfold.unfold(exp_inputs, a.config, a.estimator_seed, a.threads, a.iters)
    t2 = time.time()
    meta = {
        "schema": "s5c-pseudo/1", "config": a.config, "estimator_seed": a.estimator_seed,
        "truth": a.truth, "amplitude": a.amplitude, "split_key": a.split_key, "pseudo_seed": a.pseudo_seed,
        "threads": a.threads, "iters": a.iters, "input_npz_sha256": npz_sha,
        "bkg_dump_sha256": s5c_unfold.sha256_path(a.bkg),
        "code_sha256": {"s5c_pseudo.py": s5c_unfold.sha256_path(Path(__file__).resolve()),
                        "s5c_unfold.py": s5c_unfold.sha256_path(Path(s5c_unfold.__file__).resolve())},
        "experiment": info, "extra_params": s5c_unfold.config_params(a.config, a.threads),
        "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_array_task": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "seconds_build": round(t1 - t0, 3), "seconds_unfold": round(t2 - t1, 3),
    }
    tmp = a.out.with_name(a.out.name + ".partial.npz")
    np.savez_compressed(tmp, xsec_flat=xs.ravel(order="C"), xtrue_flat=x_true.ravel(order="C"),
                        shape=np.array(xs.shape), meta=json.dumps(meta, default=str))
    os.replace(tmp, a.out)
    print(json.dumps({k: meta[k] for k in ("truth", "pseudo_seed", "seconds_build", "seconds_unfold")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
