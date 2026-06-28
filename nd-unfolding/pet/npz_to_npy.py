#!/usr/bin/env python3
"""Convert of_inputs_pc.npz -> a directory of plain .npy files for memory-mapped loading.

The compressed .npz cannot be np.load(mmap_mode='r'); plain .npy can. This lets the
point-cloud dataloader materialize only a per-rank 1/size stride of the 32.8M-event
arrays instead of the full ~13 GB on every horovod rank (the OOM that capped training
at ~20M on a single 229 GB node). One-time, idempotent.

Usage: python3 pet/npz_to_npy.py [--inputs of_inputs_pc.npz] [--out of_inputs_pc_npy]
"""
import argparse, os, numpy as np

# Arrays the point-cloud build_loaders path consumes (everything else in the npz —
# scalars, bin edges — is not needed for training and stays in the npz).
KEEP = ["part_gen", "part_reco", "measured_pc",
        "pass_reco", "pass_truth", "w_truth", "measured_weights", "num_part"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="of_inputs_pc.npz")
    ap.add_argument("--out", default="of_inputs_pc_npy")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    d = np.load(args.inputs, allow_pickle=True)
    for k in KEEP:
        if k not in d.files:
            raise SystemExit(f"[npz->npy] missing array {k!r} in {args.inputs}")
        dst = os.path.join(args.out, f"{k}.npy")
        a = d[k]
        np.save(dst, a)
        print(f"[npz->npy] {k:18s} {str(a.shape):26s} {a.dtype} -> {dst} ({a.nbytes/1e9:.2f} GB)")
    print(f"[npz->npy] done -> {args.out}/")

if __name__ == "__main__":
    main()
