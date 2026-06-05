#!/usr/bin/env python3
"""One train/test-split OmniFold run -> full flat xsec (for the ML-split band).

Prepub item #2 (LITERATURE_NOTES.md sec C): a seedscan that ALSO varies the train/test
split, with an ensemble-mean central value. LightGBM at the production settings is nearly
deterministic in the estimator seed alone, so the genuine ML/optimization variance is
exposed by re-fitting each OmniFold classifier on a random `train_frac` subset
(omnifold_loop train_frac/split_seed) and evaluating on all events. Running many
`--split-seed` values and combining (combine_seedscan_split.py) gives the ensemble-mean
CV + the ML-split covariance, the seedscan analogue of uq_cov_ml_3d.

ROOT-free; reuses the validated omnifold_loop + xsec_nd. Run per split seed (CPU/lgbm):
  python seedscan_split.py --npz of_inputs_3d.npz --split-seed 7 --train-frac 0.8 \
      --iters 5 --out seedscan_split/res_split_7.npz
"""
import argparse
import sys

import numpy as np

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)
from omnifold_nn_core import omnifold_loop          # noqa: E402
from xsec_nd import (extract_cross_section_nd,       # noqa: E402
                     project_axis, total_xsec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default="of_inputs_3d.npz")
    ap.add_argument("--kind", default="lgbm", choices=["lgbm", "nn"])
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--split-seed", type=int, required=True)
    ap.add_argument("--train-frac", type=float, default=0.8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    nedges = int(d["nedges"])
    edges = [d[f"edges_{i}"] for i in range(nedges)]
    names = list(d["axes"])
    axis_names = ["pt", "pz"] + names

    print(f"[split {args.split_seed}] train_frac={args.train_frac} kind={args.kind} "
          f"iters={args.iters}", flush=True)
    # estimator seed tied to split seed too, so any seed-sensitivity is folded in.
    try:
        w_pull, w_push = omnifold_loop(
            d["MCgen"], d["MCreco"], d["measured"],
            d["pass_reco"], d["pass_truth"], np.ones(len(d["measured"]), bool),
            args.iters, kind=args.kind,
            MCgen_weights=d["w_truth"], MCreco_weights=d["w_reco"],
            measured_weights=d["measured_weights"], seed=args.split_seed,
            train_frac=args.train_frac, split_seed=args.split_seed, verbose=False)
    except Exception as e:   # skip a pathological split (exit 0) so afterok combine isn't blocked
        print(f"[split {args.split_seed}] SKIPPED ({type(e).__name__}: {e})"); return

    m = d["pass_truth"]
    sample = np.column_stack([d["MCgen"][m, a] for a in range(d["MCgen"].shape[1])])
    tw = d["w_truth"][m]
    bins = [np.asarray(e, float) for e in edges]
    unfold_nd, _ = np.histogramdd(sample, bins=bins, weights=w_push * tw)
    of_in, _ = np.histogramdd(sample, bins=bins, weights=tw)
    denom_nd = d["denom_nd"]
    completeness = np.zeros_like(of_in)
    nz = denom_nd > 0
    completeness[nz] = of_in[nz] / denom_nd[nz]
    xsec, _ = extract_cross_section_nd(unfold_nd, completeness, d["flux"],
                                       float(d["data_pot"]), float(d["n_nucleons"]), edges)
    tot = total_xsec(xsec, edges)

    proj = {}
    for ai, nm in enumerate(axis_names):
        e, y = project_axis(xsec, edges, ai)
        proj[f"proj_{nm}"] = y
        proj[f"edges_{nm}"] = e

    # full flat xsec (C order) for the covariance build (combine step masks to CV>0 bins)
    np.savez_compressed(args.out, split_seed=args.split_seed, train_frac=args.train_frac,
                        total_xsec=tot, xsec_flat=xsec.ravel(order="C"),
                        shape=np.array(xsec.shape), **proj)
    print(f"[OK split {args.split_seed}] total_xsec={tot:.4e} -> {args.out}")


if __name__ == "__main__":
    main()
