#!/usr/bin/env python3
"""Synthetic timing of D-ID's linear-algebra kernels at the proposed shapes (no MINERvA data).

Random sparse responses with the proposed reco/truth dimensions stand in for the real ones; only the
shapes and the sparsity assumption matter. Run with two threads:

    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
        python3 synthetic_timing.py --out synthetic_timing.json
"""

from __future__ import annotations

import argparse
import json
import platform
import resource
import time
from pathlib import Path

import numpy as np
import scipy
from scipy import sparse

N_RECO = 10_499
SHAPES = {"T1": 243, "T2": 7_776, "T3": 65_856}
NNZ = {"T1": 400_000, "T2": 3_000_000, "T3": 8_000_000}  # assumed occupancy; see REPORT.md section 6


def response(n_truth: int, nnz: int, seed: int) -> sparse.csr_matrix:
    rng = np.random.default_rng(seed)
    rows = rng.integers(0, N_RECO, nnz)
    cols = np.concatenate([np.arange(n_truth), rng.integers(0, n_truth, nnz - n_truth)])
    r = sparse.csr_matrix((rng.uniform(0.1, 1.0, nnz), (rows, cols)), shape=(N_RECO, n_truth))
    return r.multiply(0.8 / np.asarray(r.sum(axis=0)).ravel()).tocsr()


def ibu_seconds(r: sparse.csr_matrix, iterations: int) -> float:
    truth = np.full(r.shape[1], 100.0)
    data = r @ (truth * 1.1)
    eff = np.asarray(r.sum(axis=0)).ravel()
    rt = r.T.tocsr()
    start = time.perf_counter()
    for _ in range(iterations):
        folded = r @ truth
        truth = truth * (rt @ (data / folded)) / eff
    return (time.perf_counter() - start) / iterations


def fisher_eigh_seconds(r: sparse.csr_matrix) -> dict[str, float]:
    truth = np.full(r.shape[1], 100.0)
    y = r @ truth
    start = time.perf_counter()
    w = sparse.diags(1.0 / np.sqrt(y)) @ r
    f = (w.T @ w).toarray()
    built = time.perf_counter() - start
    start = time.perf_counter()
    np.linalg.eigh(f)
    return {"fisher_build_s": built, "eigh_s": time.perf_counter() - start, "fisher_bytes": f.nbytes}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = {"platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__,
           "n_reco": N_RECO, "nnz_assumed": NNZ, "per_grid": {}}
    cpu0 = time.process_time()
    for name, n in SHAPES.items():
        r = response(n, NNZ[name], seed=n)
        row = {"n_truth": n, "ibu_seconds_per_iteration": ibu_seconds(r, 50)}
        if name != "T3":
            row.update(fisher_eigh_seconds(r))
        out["per_grid"][name] = row
    out["process_cpu_s"] = time.process_time() - cpu0
    out["max_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
