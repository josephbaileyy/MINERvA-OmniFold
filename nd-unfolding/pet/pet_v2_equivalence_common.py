#!/usr/bin/env python3
"""Shared fail-closed primitives for the PET-v2 fixed-draw equivalence diagnostic.

This module is deliberately TensorFlow- and ROOT-free.  It defines identities,
splits, distance reducers, and terminal classification; it does not submit work
or construct an uncertainty product.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import numpy as np


CONTRACT_ID = "PET-V2-FIXED-DRAW-EQUIVALENCE-PREDECLARATION-20260825"
AUTHORIZATION_TOKEN = "JOSEPH-20260826-PETV2-FIXED-DRAW-EQUIVALENCE-AUTHORIZED"
BOOTSTRAP_SEED = 50000
ESTIMATOR_SEED = 42
SUBSAMPLE_SEED = 0
MAX_EVENTS = 2_000_000
NITER = 3
EPOCHS_RECO = 8
EPOCHS_TRUTH = 8
BATCH_SIZE = 512
TRAIN_FRACTION = 0.8
EARLY_STOPPING_PATIENCE = 10
SAME_ARM_CAP = 0.0251
MATERIALITY_MARGIN = 0.0502
REQUIRED_CLASS_RATIO = 1.1253110723074478
EXPECTED_INPUT_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_INPUT_SIZE = 9_897_374_636
EXPECTED_WEIGHTED_TARGET_SHA256 = (
    "13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03"
)
EXPECTED_FACTOR_HASHES = {
    "data": "d151dd197c9662da4604c9609d761887d38437d510484efdf851c8de1028ca37",
    "signal": "892d1531b7db788a9782ce2dad470b1514b13c1f1f393af9a0f84f32ea68642f",
    "background": "9e967dc2ff1a977c4940b83171204a41deb200e5d7c6ecb819c63c15c335e84e",
}
PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
)
DETERMINISTIC_ENV = {
    "PYTHONHASHSEED": "42",
    "TF_DETERMINISTIC_OPS": "1",
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
}


def sha256_file(path, chunk=16 << 20):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_array(value):
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def scalar(store, key):
    value = store[key]
    if isinstance(value, np.ndarray) and value.ndim == 0:
        value = value.item()
    if isinstance(value, bytes):
        value = value.decode()
    return value


def git_head(root):
    return subprocess.check_output(
        ["git", "-C", os.fspath(root), "rev-parse", "HEAD"], text=True
    ).strip()


def assert_clean_code_root(root, expected_head=None):
    root = Path(root).resolve()
    if not (root / ".git").exists():
        # Linked worktrees have a .git file, ordinary clones a directory.
        if not (root / ".git").is_file():
            raise SystemExit(f"[pet-v2] code root is not a git checkout: {root}")
    status = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain"], text=True
    )
    if status:
        raise SystemExit(f"[pet-v2] immutable code root is dirty: {root}")
    head = git_head(root)
    if expected_head is not None and head != expected_head:
        raise SystemExit(f"[pet-v2] code HEAD {head} != expected {expected_head}")
    return head


def assert_regular_file(path, *, sha256=None, size=None, label="file"):
    path = Path(path).resolve()
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"[pet-v2] {label} is missing, non-regular, or symlinked: {path}")
    if size is not None and path.stat().st_size != int(size):
        raise SystemExit(
            f"[pet-v2] {label} size {path.stat().st_size} != expected {int(size)}"
        )
    if sha256 is not None:
        observed = sha256_file(path)
        if observed != sha256:
            raise SystemExit(f"[pet-v2] {label} SHA-256 {observed} != expected {sha256}")
    return path


def assert_deterministic_environment():
    wrong = {key: {"expected": value, "observed": os.environ.get(key)}
             for key, value in DETERMINISTIC_ENV.items() if os.environ.get(key) != value}
    if wrong:
        raise SystemExit(f"[pet-v2] deterministic environment mismatch: {wrong}")


def fixed_factors(n_data, n_signal, n_background):
    data = np.random.default_rng(BOOTSTRAP_SEED).poisson(1.0, n_data).astype(np.uint8)
    signal = np.random.default_rng(BOOTSTRAP_SEED + 10_000_000).poisson(
        1.0, n_signal
    ).astype(np.uint8)
    background = np.random.default_rng(BOOTSTRAP_SEED + 20_000_000).poisson(
        1.0, n_background
    ).astype(np.uint8)
    factors = {"data": data, "signal": signal, "background": background}
    bad = {name: {"expected": EXPECTED_FACTOR_HASHES[name], "observed": hash_array(value)}
           for name, value in factors.items()
           if hash_array(value) != EXPECTED_FACTOR_HASHES[name]}
    if bad:
        raise SystemExit(f"[pet-v2] fixed factor replay drifted: {bad}")
    return data, signal, background


def splitmix64(values, key):
    """Vectorized SplitMix64 permutation hash, with intentional uint64 wraparound."""
    x = np.asarray(values, dtype=np.uint64) + np.uint64(key)
    with np.errstate(over="ignore"):
        z = x + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


def deterministic_train_mask(n_rows, stream_key, fraction=TRAIN_FRACTION):
    if not (0.0 < float(fraction) < 1.0) or int(n_rows) <= 1:
        raise ValueError("split requires n_rows > 1 and 0 < fraction < 1")
    hashed = splitmix64(np.arange(int(n_rows), dtype=np.uint64), int(stream_key))
    # Use the top 53 bits so the threshold is exactly representable independently of float ABI.
    threshold = int(float(fraction) * (1 << 53))
    mask = (hashed >> np.uint64(11)) < np.uint64(threshold)
    if not mask.any() or mask.all():
        raise RuntimeError("deterministic split produced an empty partition")
    return mask


def literal_source_index(factor):
    factor = np.asarray(factor)
    if factor.ndim != 1 or factor.dtype.kind not in "ui" or np.any(factor < 0):
        raise ValueError("literal multiplicity must be a nonnegative integer vector")
    return np.repeat(np.arange(factor.size, dtype=np.int64), factor.astype(np.int64))


def symrel(a, b):
    a, b = float(a), float(b)
    denom = abs(a) + abs(b)
    if denom == 0.0:
        return 0.0
    return 2.0 * abs(a - b) / denom


def weighted_push_distance(a, b, analysis_weight):
    a = np.asarray(a, np.float64)
    b = np.asarray(b, np.float64)
    weight = np.asarray(analysis_weight, np.float64)
    if not (a.shape == b.shape == weight.shape):
        raise ValueError("push distance operands are not row-aligned")
    if not (np.isfinite(a).all() and np.isfinite(b).all() and
            np.isfinite(weight).all() and np.all(weight >= 0.0)):
        raise ValueError("push distance operands are non-finite or carry negative analysis weight")
    denom = float(np.sum(weight * (np.abs(a) + np.abs(b)) / 2.0, dtype=np.float64))
    if denom <= 0.0:
        raise ValueError("push distance denominator is not positive")
    return float(np.sum(weight * np.abs(a - b), dtype=np.float64) / denom)


def classify(primary, controls_valid=True):
    required = {"D_same", "D_cross_max", "D_cross_min"}
    if not controls_valid or not primary or any(
        set(values) != required or not all(np.isfinite(list(values.values())))
        for values in primary.values()
    ):
        return "INVALID_OR_NOISY"
    if any(values["D_same"] > SAME_ARM_CAP for values in primary.values()):
        return "INVALID_OR_NOISY"
    if all(values["D_cross_max"] <= MATERIALITY_MARGIN for values in primary.values()):
        return "EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION"
    if any(values["D_cross_min"] > MATERIALITY_MARGIN and
           values["D_cross_min"] > 2.0 * values["D_same"]
           for values in primary.values()):
        return "MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW"
    return "MIXED_OR_UNRESOLVED"
