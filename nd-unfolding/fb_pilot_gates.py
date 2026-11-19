#!/usr/bin/env python3
"""PILOT-FB §5.1: the per-unfold gates J, G2 and G3, as functions of captured arrays and fitted models.

Declaration: .../rounding-stability-20261106/pilot-fb/PILOT-FB-DECLARATION.md rev 3 (§2 items 9-10, §5.1), bound by
PILOT-FB-BINDING-1 at M_PFB 522ac0b6.

  G2  every fit and scored row's intended bin index (the first intended upper bound >= the value, bin.h:631) is the
      E-set base's;
  G3  (a) a LightGBM Dataset built from the role's exact fit matrix and its own Dataset parameters, dumped with
      Dataset._dump_text (dataset.cpp:1188-1238), gives every training row its intended index; (b) every numerical
      split threshold in the fitted model's text, parsed at its printed {:.17g} (tree.cpp:351-352), equals an element of
      the intended list exactly; (c) every split's decision_type records missing type None and no categorical split
      (tree.h:274-276). feature_num_bin = n + z + 1 is recorded, not relied on;
  J   (J1) the run's jittered source arrays equal an independent recomputation, bitwise; (J2) each role's received
      matrices equal its rebuilt selection, bitwise (fb_pilot_probe.role_matrices); (J3) each source array moved off the
      analysis-grid edges and nothing on an edge moved. A base's role matrices compare as float64 values.

MEASURES: whether one unfold's boundaries were the intended ones. CANNOT AUTHORIZE: a reading.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np

DATASET_KEYS = ("max_bin", "forcedbins_filename", "bin_construct_sample_cnt", "min_data_in_bin", "feature_pre_filter",
                "min_data_in_leaf", "min_child_samples", "use_missing", "zero_as_missing", "num_threads",
                "deterministic", "force_row_wise", "verbose")


def intended_index(X: np.ndarray, intended: list) -> np.ndarray:
    """Per feature, the index of the first intended upper bound >= the value (LightGBM's ValueToBin, bin.h:631)."""
    X = np.asarray(X, np.float64)
    return np.column_stack([np.searchsorted(np.asarray(b, np.float64), X[:, f], side="left") for f, b in enumerate(intended)])


def g2(received: dict, base: dict, intended: dict) -> dict:
    """received/base = {role: (fit, scored or None)}; intended = {role: [5 lists]}. Changed-row counts per role,
    matrix and feature; PASS iff all are 0."""
    out, ok = {}, True
    for r, (fit, scored) in received.items():
        bf, bs = base[r]
        rec = {}
        for name, a, b in (("fit", fit, bf), ("scored", scored, bs)):
            if a is None and b is None:
                continue
            if a is None or b is None or np.shape(a) != np.shape(b):
                rec[name] = "row sets differ"
                ok = False
                continue
            d = (intended_index(a, intended[r]) != intended_index(b, intended[r])).sum(axis=0)
            rec[name] = d.astype(int).tolist()
            ok &= not d.any()
        out[r] = rec
    return {"pass": bool(ok), "changed_rows": out}


def dataset_params(est_params: dict) -> dict:
    """The keys that decide LightGBM's bins, taken from the estimator's own parameters at its fit."""
    return {k: est_params[k] for k in DATASET_KEYS if k in est_params}


def parse_dump(path: Path, n_features: int) -> np.ndarray:
    """Every training row's bin indices from a DumpTextFile, as an int array [rows, features]."""
    lines = Path(path).read_text().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("feature ") and ln.split(":")[0] == f"feature {n_features - 1}")
    block = "\n".join(lines[start + 1:])
    vals = np.array(block.replace(",", " ").split(), dtype=np.int64)
    if vals.size % n_features:
        raise ValueError("the dump's row block is not a whole number of rows")
    return vals.reshape(-1, n_features)


def g3a(X: np.ndarray, params: dict, intended: list, workdir: Path | None = None) -> dict:
    """G3 (a): the rebuilt Dataset's training partition against the intended indices."""
    import lightgbm as lgb
    X = np.asarray(X)
    ds = lgb.Dataset(X, label=np.zeros(X.shape[0]), params=dataset_params(params), free_raw_data=True).construct()
    nbin = [int(ds.feature_num_bin(f)) for f in range(X.shape[1])]
    with tempfile.TemporaryDirectory(dir=workdir) as d:
        p = Path(d) / "dump.txt"
        ds._dump_text(str(p))
        got = parse_dump(p, X.shape[1])
        os.remove(p)
    want = intended_index(X, intended)
    if got.shape != want.shape:
        return {"pass": False, "why": f"dump rows {got.shape} != matrix {want.shape}", "feature_num_bin": nbin}
    bad = (got != want).sum(axis=0).astype(int).tolist()
    return {"pass": not any(bad), "mismatched_rows": bad, "feature_num_bin": nbin,
            "expected_num_bin": [len(b) for b in intended]}


def model_splits(model_text: str) -> list:
    """[(feature, threshold, decision_type)] for every split of every tree in a LightGBM model text."""
    out = []
    tree = {}

    def flush():
        if "split_feature" in tree:
            sf, th, dt = tree["split_feature"], tree["threshold"], tree["decision_type"]
            if not (len(sf) == len(th) == len(dt)):
                raise ValueError("a tree's split arrays differ in length")
            out.extend(zip(sf, th, dt))
        tree.clear()

    for ln in model_text.splitlines():
        if ln.startswith("Tree="):
            flush()
        elif ln.startswith("split_feature="):
            tree["split_feature"] = [int(v) for v in ln.split("=", 1)[1].split()]
        elif ln.startswith("threshold="):
            tree["threshold"] = [float(v) for v in ln.split("=", 1)[1].split()]
        elif ln.startswith("decision_type="):
            tree["decision_type"] = [int(v) for v in ln.split("=", 1)[1].split()]
        elif ln.startswith("end of trees"):
            flush()
    flush()
    return out


def g3bc(model_text: str, intended: list) -> dict:
    """G3 (b) and (c) on one fitted model's text."""
    sets = [set(float(v) for v in b) for b in intended]
    splits = model_splits(model_text)
    off = [(f, t) for f, t, _ in splits if f >= len(sets) or t not in sets[f]]
    missing = [(f, d) for f, _, d in splits if (d >> 2) & 3 != 0 or d & 1]
    return {"pass": not off and not missing, "splits": len(splits), "thresholds_not_intended": len(off),
            "first_not_intended": [list(map(float, x)) for x in off[:3]], "missing_or_categorical": len(missing)}


def j_compare(name: str, received: np.ndarray, rebuilt: np.ndarray, base: bool) -> str | None:
    """J1/J2: bitwise for a jittered unfold; as float64 values for a base (float32 sources)."""
    a, b = np.asarray(received), np.asarray(rebuilt)
    if a.shape != b.shape:
        return f"{name}: shape {a.shape} != rebuilt {b.shape}"
    if base:
        if not np.array_equal(a.astype(np.float64), b.astype(np.float64)):
            return f"{name}: values differ from the float32 base's selection"
    elif a.dtype != b.dtype or a.tobytes() != b.tobytes():
        return f"{name}: not bitwise the rebuilt selection"
    return None


def j3_moved(jittered: np.ndarray, base32: np.ndarray, edges: list) -> dict:
    """J3 on one source array: moved entries off the grid edges, and moved entries on them (must be 0)."""
    j = np.asarray(jittered, np.float64)
    b = np.asarray(base32, np.float32).astype(np.float64)
    on_edge = np.zeros(b.shape, bool)
    for k, e in enumerate(edges):
        on_edge[:, k] = np.isin(b[:, k], np.asarray(e, np.float32).astype(np.float64))
    moved = j != b
    return {"moved_off_edge": int((moved & ~on_edge).sum()), "moved_on_edge": int((moved & on_edge).sum())}
