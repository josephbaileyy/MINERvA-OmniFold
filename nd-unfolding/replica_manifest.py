#!/usr/bin/env python3
"""Strict replica-manifest validation for bootstrap and seedscan combiners."""

from pathlib import Path

import numpy as np


ID_KEYS = ("seed", "split_seed", "replica_id")


def load_replica_manifest(paths, expected_ids=None, value_key="xsec_flat"):
    paths = [Path(p) for p in paths]
    if not paths:
        raise ValueError("replica manifest is empty")
    rows = []
    ids = []
    expected_shape = None
    for path in paths:
        if not path.is_file():
            raise ValueError(f"missing replica file: {path}")
        with np.load(path, allow_pickle=False) as z:
            if value_key not in z.files:
                raise ValueError(f"{path}: missing {value_key}")
            found = [k for k in ID_KEYS if k in z.files]
            if len(found) != 1:
                raise ValueError(f"{path}: expected exactly one replica id key, found {found}")
            rid = int(np.asarray(z[found[0]]).item())
            x = np.asarray(z[value_key], dtype=float)
            declared = tuple(int(v) for v in np.asarray(z["shape"]).ravel()) if "shape" in z.files else x.shape
            if int(np.prod(declared)) != x.size:
                raise ValueError(f"{path}: declared shape {declared} does not match {x.size} values")
            if expected_shape is None:
                expected_shape = x.shape
            elif x.shape != expected_shape:
                raise ValueError(f"{path}: wrong shape {x.shape}, expected {expected_shape}")
            if not np.all(np.isfinite(x)):
                raise ValueError(f"{path}: non-finite {value_key}")
            ids.append(rid)
            rows.append(x)
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"duplicate replica ids: {dup}")
    if expected_ids is not None:
        expected_ids = set(int(i) for i in expected_ids)
        got = set(ids)
        if got != expected_ids:
            raise ValueError(f"replica id mismatch: missing={sorted(expected_ids-got)} extra={sorted(got-expected_ids)}")
    order = np.argsort(ids)
    return np.stack([rows[i] for i in order]), np.asarray([ids[i] for i in order])
