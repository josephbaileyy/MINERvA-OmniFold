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

TRUTHS = ("nominal", "eavail_tilt", "q3_given_eavail_w")
AXIS = {"pt": 0, "pz": 1, "eavail": 2, "q3": 3, "W": 4}


def half_mask(n: int, key: int) -> np.ndarray:
    """True for half B: parity of splitmix64(row ^ key)."""
    with np.errstate(over="ignore"):
        z = (np.arange(n, dtype=np.uint64) ^ np.uint64(key)) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return (z & np.uint64(1)).astype(bool)


def truth_weight(name: str, gen: np.ndarray, edges: list, amplitude: float,
                 w_truth: np.ndarray | None = None) -> np.ndarray:
    """Declared truth reweights r(truth). ``q3_given_eavail_w`` changes the q3 dependence inside every
    fine (E_avail, W) truth cell while preserving that cell's w_truth-weighted total exactly: within
    each cell r = 1 + a z, where z is the cell-standardized q3, clipped to [-2, 2] and re-centred to
    weighted mean zero (so the (E_avail, W) marginal of the reweighted truth equals the nominal one
    to rounding; r > 0 for |a| < 0.5)."""
    if name == "nominal":
        return np.ones(gen.shape[0])
    if name == "eavail_tilt":
        e = edges[AXIS["eavail"]]
        u = (gen[:, AXIS["eavail"]] - e[0]) / (e[-1] - e[0])
        return 1.0 + amplitude * (np.clip(u, 0.0, 1.0) - 0.5)
    if name == "q3_given_eavail_w":
        if w_truth is None or abs(amplitude) >= 0.5:
            raise ValueError("q3_given_eavail_w needs w_truth and |amplitude| < 0.5")
        ie = np.clip(np.searchsorted(edges[AXIS["eavail"]], gen[:, AXIS["eavail"]], side="right") - 1,
                     0, len(edges[AXIS["eavail"]]) - 2)
        iw = np.clip(np.searchsorted(edges[AXIS["W"]], gen[:, AXIS["W"]], side="right") - 1,
                     0, len(edges[AXIS["W"]]) - 2)
        cell = ie * (len(edges[AXIS["W"]]) - 1) + iw
        n = int(cell.max()) + 1
        w = np.asarray(w_truth, float)
        q = gen[:, AXIS["q3"]].astype(float)
        sw = np.bincount(cell, weights=w, minlength=n)
        mu = np.bincount(cell, weights=w * q, minlength=n) / np.where(sw > 0, sw, 1)
        var = np.bincount(cell, weights=w * (q - mu[cell]) ** 2, minlength=n) / np.where(sw > 0, sw, 1)
        z = np.clip((q - mu[cell]) / np.sqrt(np.where(var > 0, var, 1.0))[cell], -2.0, 2.0)
        z = z - (np.bincount(cell, weights=w * z, minlength=n) / np.where(sw > 0, sw, 1))[cell]
        return 1.0 + amplitude * z
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


def build_experiment(inputs: dict, bkg: dict, truth: str, amplitude: float, split_key: int | None,
                     pseudo_seed: int, no_background: bool = False) -> tuple[dict, np.ndarray, dict]:
    """split_key None = development diagnostic 'no split': the whole MC sample is both the
    pseudo-data source and the unfolding MC (weights x1), conditional on that sample."""
    edges = inputs["edges"]
    n = inputs["MCgen"].shape[0]
    no_split = split_key is None
    is_b = np.ones(n, bool) if no_split else half_mask(n, split_key)
    wscale = 1.0 if no_split else 2.0
    rng = np.random.default_rng(pseudo_seed)
    r = truth_weight(truth, inputs["MCgen"], edges, amplitude, w_truth=inputs["w_truth"])

    b_reco = is_b & inputs["pass_reco"]
    lam = wscale * inputs["w_reco"][b_reco] * r[b_reco]
    n_sig = rng.poisson(lam).astype(float)
    m_bkg = rng.poisson(bkg["bkg_w"]).astype(float)
    if no_background:  # development diagnostic: signal-only pseudo-data, nothing to subtract
        m_bkg = np.zeros_like(m_bkg)
    sig_keep, bkg_keep = n_sig > 0, m_bkg > 0
    coords = np.concatenate([inputs["MCreco"][b_reco][sig_keep], bkg["bkg_reco"][bkg_keep]]).astype(np.float32)
    counts = np.concatenate([n_sig[sig_keep], m_bkg[bkg_keep]])
    mw = purity_weights(coords.astype(float), counts,
                        np.zeros_like(bkg["bkg_nd"]) if no_background else bkg["bkg_nd"], edges)

    a = is_b if no_split else ~is_b
    exp_inputs = {
        "MCgen": inputs["MCgen"][a], "MCreco": inputs["MCreco"][a],
        "pass_reco": inputs["pass_reco"][a], "pass_truth": inputs["pass_truth"][a],
        "w_truth": wscale * inputs["w_truth"][a], "w_reco": wscale * inputs["w_reco"][a],
        "measured": coords, "measured_weights": mw,
        "denom_nd": inputs["denom_nd"], "flux": inputs["flux"], "data_pot": inputs["data_pot"],
        "n_nucleons": inputs["n_nucleons"], "edges": edges,
    }
    # Truth of this pseudo-data: B's reweighted truth through the analysis's own extraction.
    gen_b = inputs["MCgen"][is_b & inputs["pass_truth"]]
    wt_b = wscale * inputs["w_truth"][is_b & inputs["pass_truth"]]
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
    ap.add_argument("--split-key", type=int, default=None,
                    help="fixed MC split (single-experiment mode); batch mode derives one per seed")
    ap.add_argument("--no-background", action="store_true",
                    help="DEVELOPMENT DIAGNOSTIC ONLY: signal-only pseudo-data with no background subtraction")
    ap.add_argument("--no-split", action="store_true",
                    help="DEVELOPMENT DIAGNOSTIC ONLY: whole MC as pseudo-data source and unfolding MC")
    ap.add_argument("--pseudo-seed", type=int, default=None, help="one experiment")
    ap.add_argument("--pseudo-seeds", default=None,
                    help="first:last inclusive; one process runs each seed, writing <out>/<truth>_s<seed>.npz, "
                         "skipping seeds whose product exists; the split key is derived from each seed")
    ap.add_argument("--bootstrap-seeds", default=None,
                    help="first:last: statistical bootstrap of ONE experiment (--pseudo-seed/--split-key "
                         "fixed): each replica multiplies the pseudo-data event weights and the unfolding-"
                         "half MC weights by independent Poisson(1) draws, as bootstrap_nd.py does for data "
                         "and MC; writes <out>/boot_b<seed>.npz")
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--expect-npz-sha256", default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    batch = a.pseudo_seeds is not None
    if batch == (a.pseudo_seed is not None):
        print("give exactly one of --pseudo-seed and --pseudo-seeds", file=sys.stderr)
        return 2
    if not batch and a.split_key is None and not a.no_split:
        print("single-experiment mode needs --split-key or --no-split", file=sys.stderr)
        return 2
    if a.no_background and (batch or a.bootstrap_seeds):
        print("--no-background is a single-experiment development diagnostic", file=sys.stderr)
        return 2
    if a.no_split and (batch or a.split_key is not None or a.bootstrap_seeds):
        print("--no-split is a single-experiment development diagnostic", file=sys.stderr)
        return 2
    if not batch and a.bootstrap_seeds is None and a.out.exists():
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
    bkg_sha = s5c_unfold.sha256_path(a.bkg)
    if a.bootstrap_seeds is not None:
        if batch:
            print("bootstrap mode takes one experiment (--pseudo-seed and --split-key)", file=sys.stderr)
            return 2
        return run_bootstrap(a, inputs, bkg, npz_sha, bkg_sha)
    if batch:
        first, last = (int(v) for v in a.pseudo_seeds.split(":"))
        a.out.mkdir(parents=True, exist_ok=True)
        status = 0
        for seed in range(first, last + 1):
            target = a.out / f"{a.truth}_a{a.amplitude:g}_s{seed}.npz"
            if target.exists():
                continue
            status |= run_one(a, inputs, bkg, npz_sha, bkg_sha, seed, split_key_for(seed), target)
        return status
    return run_one(a, inputs, bkg, npz_sha, bkg_sha, a.pseudo_seed, None if a.no_split else a.split_key, a.out, t0)


def run_bootstrap(a, inputs, bkg, npz_sha, bkg_sha) -> int:
    exp_inputs, x_true, info = build_experiment(inputs, bkg, a.truth, a.amplitude, a.split_key, a.pseudo_seed)
    first, last = (int(v) for v in a.bootstrap_seeds.split(":"))
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for b in range(first, last + 1):
        target = a.out / f"boot_b{b}.npz"
        if target.exists():
            continue
        rng_d = np.random.default_rng(b)
        rng_m = np.random.default_rng(b + 10_000_000)  # bootstrap_nd.py's data/MC stream separation
        rep = dict(exp_inputs)
        rep["measured_weights"] = exp_inputs["measured_weights"] * rng_d.poisson(1.0, exp_inputs["measured_weights"].shape[0])
        pm = rng_m.poisson(1.0, exp_inputs["w_truth"].shape[0]).astype(float)
        rep["w_truth"] = exp_inputs["w_truth"] * pm
        rep["w_reco"] = exp_inputs["w_reco"] * pm
        t1 = time.time()
        xs, _ = s5c_unfold.unfold(rep, a.config, a.estimator_seed, a.threads, a.iters)
        meta = {"schema": "s5c-pseudo-boot/1", "config": a.config, "truth": a.truth, "amplitude": a.amplitude,
                "split_key": a.split_key, "pseudo_seed": a.pseudo_seed, "bootstrap_seed": b,
                "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "experiment": info,
                "code_sha256": {"s5c_pseudo.py": s5c_unfold.sha256_path(Path(__file__).resolve())},
                "seconds_unfold": round(time.time() - t1, 3)}
        tmp = target.with_name(target.name + f".partial-{os.getpid()}.npz")
        np.savez_compressed(tmp, xsec_flat=xs.ravel(order="C"), meta=json.dumps(meta, default=str))
        if target.exists():
            tmp.unlink()
            status |= 3
            continue
        os.replace(tmp, target)
        print(json.dumps({"bootstrap_seed": b, "seconds_unfold": meta["seconds_unfold"]}))
    return status


def split_key_for(seed: int) -> int:
    """Batch mode: an MC split per experiment, so the unfolding half's finite-sample fluctuation is
    regenerated with the data (declared in the contract); deterministic in the seed."""
    return (seed * 0x9E3779B1 + 0x5C5C) % (2**61 - 1)


def run_one(a, inputs, bkg, npz_sha, bkg_sha, seed, split_key, out, t0=None) -> int:
    t0 = time.time() if t0 is None else t0
    exp_inputs, x_true, info = build_experiment(inputs, bkg, a.truth, a.amplitude, split_key, seed,
                                                no_background=getattr(a, "no_background", False))
    t1 = time.time()
    xs, params = s5c_unfold.unfold(exp_inputs, a.config, a.estimator_seed, a.threads, a.iters)
    t2 = time.time()
    meta = {
        "schema": "s5c-pseudo/1", "config": a.config, "estimator_seed": a.estimator_seed,
        "truth": a.truth, "amplitude": a.amplitude, "split_key": split_key, "pseudo_seed": seed,
        "no_background": bool(getattr(a, "no_background", False)),
        "threads": a.threads, "iters": a.iters, "input_npz_sha256": npz_sha,
        "bkg_dump_sha256": bkg_sha,
        "code_sha256": {"s5c_pseudo.py": s5c_unfold.sha256_path(Path(__file__).resolve()),
                        "s5c_unfold.py": s5c_unfold.sha256_path(Path(s5c_unfold.__file__).resolve())},
        "experiment": info, "extra_params": s5c_unfold.config_params(a.config, a.threads),
        "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_array_task": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "seconds_build": round(t1 - t0, 3), "seconds_unfold": round(t2 - t1, 3),
    }
    tmp = out.with_name(out.name + f".partial-{os.getpid()}.npz")
    np.savez_compressed(tmp, xsec_flat=xs.ravel(order="C"), xtrue_flat=x_true.ravel(order="C"),
                        shape=np.array(xs.shape), meta=json.dumps(meta, default=str))
    if out.exists():  # another process finished it first: keep the first product, never overwrite
        tmp.unlink()
        return 3
    os.replace(tmp, out)
    print(json.dumps({k: meta[k] for k in ("truth", "pseudo_seed", "seconds_build", "seconds_unfold")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
