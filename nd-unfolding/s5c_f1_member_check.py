#!/usr/bin/env python3
"""Family F1 screen: projected-sigma movement of the existing fixed estimator on coarse partitions.

Uses the two graded members of the 2026-09-19 campaign (k=0 ``361090f9...``, k=1200
``7e4636a3...``), which differ only in estimator seed. For each functional set it reports the
relative movement of projected standard deviations, ``|sqrt(u'C1u) - sqrt(u'C0u)| / sqrt(u'C0u)``,
and the relative central-value shift on the same functionals.

CONTROL FIRST: on the 43 M1 functionals (``project_cov_nd.build_projection`` rows plus all-ones) it
must reproduce the graded ``s_proj = 0.06145`` (GRADE-20260920) before any other number is read.

SCOPE: two seeds. A movement above 5% is a definitive failure of the 5% gate for that functional
set (a maximum over more seed pairs can only be larger); a movement below 5% establishes nothing
(plan §6 requires at least ten seeds to estimate a seed distribution).

MEASURES: F1's two-member projected-sigma movement per functional set. CANNOT AUTHORIZE: a pass
of any stability gate, an adoption, or any re-grade of the Z candidates (Joseph's (B) stands).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import project_cov_nd as pc

AXES = ["pt", "pz", "eavail", "q3", "W"]


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_member(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    x = np.asarray(z["hXSecND_flat"], float)
    rows = np.asarray(z["hRowIndex5D"], np.int64)
    cov = np.asarray(z["hCov_combined5d_total_uthrow"], float)
    xr = x[rows] if x.size != rows.size else x  # CV on the full grid or already on the support
    return {"x": x, "xr": xr, "rows": rows, "C": cov}


def m1_functionals(rows: np.ndarray, shape: tuple) -> np.ndarray:
    dst_shape = (shape[2], shape[4])
    idx = np.unravel_index(rows, shape)
    hit = np.unique(np.ravel_multi_index((idx[2], idx[4]), dst_shape))
    dst_index_of = -np.ones(int(np.prod(dst_shape)), dtype=int)
    dst_index_of[hit] = np.arange(hit.size)
    M, _ = pc.build_projection(AXES, ["eavail", "W"], rows, shape, dst_shape, dst_index_of)
    return np.vstack([M, np.ones((1, rows.size))])


def partition_functionals(rows: np.ndarray, shape: tuple, coarse_edges: dict) -> tuple[np.ndarray, list]:
    """Integrated cross section per coarse cell: sum over fine cells of x * (5D bin volume)."""
    idx = np.unravel_index(rows, shape)
    vol = np.ones(rows.size)
    cell_axis = []
    for k, ax in enumerate(AXES):
        fine = np.asarray(pc.AXIS_EDGES[ax], float)
        vol *= np.diff(fine)[idx[k]]
        centers = 0.5 * (fine[:-1] + fine[1:])[idx[k]]
        ce = np.asarray(coarse_edges[ax], float)
        cell_axis.append(np.clip(np.searchsorted(ce, centers, side="right") - 1, 0, len(ce) - 2))
    cshape = tuple(len(coarse_edges[ax]) - 1 for ax in AXES)
    cell = np.ravel_multi_index(cell_axis, cshape)
    used = np.unique(cell)
    U = np.zeros((used.size, rows.size))
    U[np.searchsorted(used, cell), np.arange(rows.size)] = vol
    return U, used.tolist()


def movement(U: np.ndarray, m0: dict, m1: dict) -> dict:
    s0 = np.sqrt(((U @ m0["C"]) * U).sum(1))
    s1 = np.sqrt(((U @ m1["C"]) * U).sum(1))
    mv = np.abs(s1 - s0) / s0
    f0, f1 = U @ m0["xr"], U @ m1["xr"]
    cv = np.abs(f1 - f0) / np.abs(f0)
    return {"n": int(U.shape[0]), "sigma_movement_max": float(mv.max()), "argmax": int(mv.argmax()),
            "sigma_movement_median": float(np.median(mv)), "sigma_movement_all": mv.tolist(),
            "cv_shift_max": float(cv.max()), "cv_shift_median": float(np.median(cv)),
            "cv_shift_over_sigma_max": float(np.max(np.abs(f1 - f0) / s0))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--k0", type=Path, required=True)
    ap.add_argument("--k1200", type=Path, required=True)
    ap.add_argument("--partitions", type=Path, required=True, help="s5c_partition.py output")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = {"schema": "s5c-f1-member-check/1", "k0_sha256": sha256_path(a.k0), "k1200_sha256": sha256_path(a.k1200)}
    m0, m1 = load_member(a.k0), load_member(a.k1200)
    if not np.array_equal(m0["rows"], m1["rows"]):
        raise SystemExit("members disagree on their reported rows")
    shape = tuple(len(pc.AXIS_EDGES[ax]) - 1 for ax in AXES)
    res["control_m1"] = movement(m1_functionals(m0["rows"], shape), m0, m1)
    res["control_reproduces_graded_0p06145"] = abs(res["control_m1"]["sigma_movement_max"] - 0.06145) < 5e-5
    parts = json.loads(a.partitions.read_text())["levels"]
    res["partitions"] = {}
    for name, level in parts.items():
        U, cells = partition_functionals(m0["rows"], shape, level["edges"])
        res["partitions"][name] = {"cells_with_support": cells, **movement(U, m0, m1)}
    a.out.write_text(json.dumps(res, indent=1))
    print(json.dumps({"control": {k: res["control_m1"][k] for k in ("sigma_movement_max", "argmax")},
                      "control_ok": res["control_reproduces_graded_0p06145"],
                      **{n: {k: v[k] for k in ("n", "sigma_movement_max", "sigma_movement_median", "cv_shift_over_sigma_max")}
                         for n, v in res["partitions"].items()}}, indent=1))
    return 0 if res["control_reproduces_graded_0p06145"] else 6


if __name__ == "__main__":
    raise SystemExit(main())
