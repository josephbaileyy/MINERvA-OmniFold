#!/usr/bin/env python3
"""Build a reduced-scale row cache for the event-feature ranking arms (B-3 evidence).

WHY A CACHE: `of_inputs_pc_fps_xps2.npz` is 8.41 GB compressed and `part_gen` alone is
49,152,885 x 12 x 5 float32 = 11.8 GB uncompressed. npz members decompress WHOLE, so every
arm that touched the full file would pay ~20 GB of decompression before training a single
step. One prep pass writes an uncompressed subsample; the arms then mmap it and start
instantly. This is a methodology-scale cache, NOT a publication input.

ROW SELECTION: a uniform random subsample of ALL rows, so the natural pass_reco/pass_truth
fractions (and therefore the acceptance structure the estimator has to cope with) are
preserved. Do NOT pre-filter to pass_reco -- that would silently delete the miss population
the step-2 prior has to carry, and the ranking would be measured on an easier problem than
the real one.

WHAT IS NOT HERE: `measured_scalars`. The xps2 pc npz does not carry it (CLM-007,
FULL_EVENT_FEATURE_CONTRACT.md:135-141) and the sidecar `of_inputs_5d_fps_xps2.npz` is not on
this host. The arms therefore run as a CLOSURE (pseudo-data built from MC) -- see
feature_rank_arms.py. Real-data arms need the sidecar.
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if f"{_REPO}/nd-unfolding" not in sys.path:
    sys.path.insert(0, f"{_REPO}/nd-unfolding")

# Arrays copied verbatim (subsampled on axis 0) and the small ones copied whole.
_ROW_KEYS = ("part_reco", "part_gen", "reco_scalars", "truth_scalars",
             "pass_reco", "pass_truth", "w_truth", "w_reco")
_WHOLE_KEYS = ("edges_0", "edges_1", "data_pot", "num_part")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="of_inputs_pc_fps_xps2.npz")
    ap.add_argument("--out", default="feature_rank_cache_400k.npz")
    ap.add_argument("--n-events", type=int, default=400_000,
                    help="rows to retain; uniform over ALL rows (pass fractions preserved)")
    ap.add_argument("--seed", type=int, default=20260730,
                    help="row-selection seed; FIXED across arms so every arm sees identical rows")
    args = ap.parse_args()

    d = np.load(args.inputs, allow_pickle=True)
    n_all = int(np.asarray(d["pass_reco"]).shape[0])
    if args.n_events > n_all:
        raise SystemExit(f"--n-events {args.n_events} exceeds inventory {n_all}")

    # One global draw with a fixed seed: the row set is a property of (seed, n_events) only,
    # so arms are comparable by construction and the cache is reproducible.
    rng = np.random.default_rng(args.seed)
    idx = np.sort(rng.choice(n_all, size=args.n_events, replace=False))

    out = {"row_index": idx.astype(np.int64)}
    for k in _ROW_KEYS:
        a = np.asarray(d[k])                      # decompresses this member once
        if a.shape[0] != n_all:
            raise SystemExit(f"{k}: leading axis {a.shape[0]} != {n_all} (row misalignment)")
        out[k] = a[idx].copy()
        print(f"[prep] {k:16s} {str(a.shape):24s} -> {out[k].shape} {out[k].dtype}", flush=True)
        del a
    for k in _WHOLE_KEYS:
        if k in d.files:
            out[k] = np.asarray(d[k])

    pr = out["pass_reco"].astype(bool)
    pt_ = out["pass_truth"].astype(bool)
    print(f"[prep] retained {args.n_events} rows of {n_all} "
          f"({100.0*args.n_events/n_all:.4f}%); pass_reco {pr.sum()} ({100.0*pr.mean():.2f}%), "
          f"pass_truth {pt_.sum()} ({100.0*pt_.mean():.2f}%), both {(pr & pt_).sum()}")

    np.savez(args.out, **out)                     # uncompressed on purpose: load speed
    meta = {"inputs": os.path.abspath(args.inputs), "n_all": n_all,
            "n_events": args.n_events, "row_seed": args.seed,
            "pass_reco_frac": float(pr.mean()), "pass_truth_frac": float(pt_.mean()),
            "cache_bytes": os.path.getsize(args.out)}
    with open(os.path.splitext(args.out)[0] + "_meta.json", "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"[prep] wrote {args.out} ({meta['cache_bytes']/2**20:.1f} MiB)")


if __name__ == "__main__":
    main()
