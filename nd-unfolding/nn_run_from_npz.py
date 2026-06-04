#!/usr/bin/env python3
"""Run OmniFold from a dumped .npz with a chosen estimator (ROOT-free).

Step 2 of the NN-vs-GBDT cross-check. Loads nn_dump_inputs.py output, runs the
IDENTICAL two-step loop (omnifold_nn_core.omnifold_loop) with --kind nn (keras MLP,
TF env) or --kind lgbm (LightGBM, ROOT env), bins the unfolded truth, extracts the
cross section with xsec_nd, and writes the per-axis projections + total to an output
.npz. Because both kinds go through the same loop on the same inputs, differences
isolate the classifier (MLP vs GBDT), not the pipeline.

Usage:
  # GBDT baseline (ROOT/lightgbm env):
  python nn_run_from_npz.py --npz of_inputs_3d.npz --kind lgbm --iters 5 --out res_lgbm.npz
  # NN (after `module load tensorflow/2.15.0`):
  python nn_run_from_npz.py --npz of_inputs_3d.npz --kind nn   --iters 5 --out res_nn.npz
"""
import argparse
import sys

import numpy as np

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)
from omnifold_nn_core import omnifold_loop          # noqa: E402
from xsec_nd import (extract_cross_section_nd,       # noqa: E402
                     project_axis, project_marginal, total_xsec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--kind", required=True, choices=["nn", "lgbm"])
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    nedges = int(d["nedges"])
    edges = [d[f"edges_{i}"] for i in range(nedges)]
    names = list(d["axes"])
    axis_names = ["pt", "pz"] + names

    print(f"[run] kind={args.kind} iters={args.iters} "
          f"MCgen={d['MCgen'].shape} measured={d['measured'].shape}", flush=True)
    w_pull, w_push = omnifold_loop(
        d["MCgen"], d["MCreco"], d["measured"],
        d["pass_reco"], d["pass_truth"], np.ones(len(d["measured"]), bool),
        args.iters, kind=args.kind,
        MCgen_weights=d["w_truth"], MCreco_weights=d["w_reco"],
        measured_weights=d["measured_weights"], seed=args.seed)

    # bin truth-pass with step2 (push) weights
    m = d["pass_truth"]
    tcols = [d["MCgen"][m, a] for a in range(d["MCgen"].shape[1])]
    tw = d["w_truth"][m]
    sample = np.column_stack(tcols)
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
    marg2d = project_marginal(xsec, edges, drop_axes=list(range(2, nedges)))
    marg_tot = (marg2d * np.diff(edges[0])[:, None] * np.diff(edges[1])[None, :]).sum()

    np.savez_compressed(args.out, kind=args.kind, total_xsec=tot,
                        marg2d_total=marg_tot, step2_mean=float(w_push.mean()),
                        **proj)
    print(f"[OK] kind={args.kind} total_xsec={tot:.4e}  2D-marginal={marg_tot:.4e}")
    for nm in axis_names:
        y = proj[f"proj_{nm}"]
        print(f"     d#sigma/d{nm}: " + " ".join(f"{v:.3e}" for v in y))


if __name__ == "__main__":
    main()
