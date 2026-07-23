"""Pure utility functions used by the experimental PET2 backend."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import numpy as np


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def canonical_json(value: Any) -> str:
    """Canonical serialization used by every recipe and manifest fingerprint."""
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def array_hash(*arrays: np.ndarray) -> str:
    """Hash ordered array evidence without coercing dtype or shape."""
    digest = hashlib.sha256()
    for value in arrays:
        arr = np.ascontiguousarray(np.asarray(value))
        digest.update(arr.dtype.str.encode("ascii"))
        digest.update(repr(arr.shape).encode("ascii"))
        digest.update(arr.tobytes())
    return digest.hexdigest()


def file_sha256(path: os.PathLike[str] | str, chunk_bytes: int = 8 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def stable_split(
    row_index: np.ndarray,
    seed: int,
    train_fraction: float = 0.7,
    identity: np.ndarray | None = None,
) -> np.ndarray:
    """Return a deterministic train mask independent of row traversal order.

    If physical identities are available they are hashed.  Otherwise the stable
    row index is used and the caller must label the result row-identity-only.
    """
    if not (0.0 < train_fraction < 1.0):
        raise ValueError("train_fraction must be strictly between zero and one")
    rows = np.asarray(row_index, dtype=np.int64)
    if rows.ndim != 1 or len(np.unique(rows)) != len(rows):
        raise ValueError("row_index must be a unique one-dimensional array")
    keys = rows[:, None] if identity is None else np.asarray(identity)
    if keys.shape[0] != rows.shape[0]:
        raise ValueError("identity and row_index lengths differ")
    if keys.ndim == 1:
        keys = keys[:, None]
    if keys.ndim != 2 or not np.issubdtype(keys.dtype, np.integer):
        raise ValueError("stable split identities must be a two-dimensional integer array")
    keys = np.ascontiguousarray(keys, dtype=np.int64)
    threshold = int(train_fraction * (1 << 64))
    values = _vectorized_identity_hash(keys, seed)
    out = values < np.uint64(threshold)
    if out.all() or (~out).all():
        raise ValueError("deterministic split produced an empty partition")
    return out


def _splitmix64(values: np.ndarray) -> np.ndarray:
    """Vectorized SplitMix64 finalizer with defined unsigned wraparound."""
    values = np.asarray(values, dtype=np.uint64)
    values = values + np.uint64(0x9E3779B97F4A7C15)
    values = (values ^ (values >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    values = (values ^ (values >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return values ^ (values >> np.uint64(31))


def _vectorized_identity_hash(keys: np.ndarray, seed: int) -> np.ndarray:
    """Hash every identity row without an O(N) Python event loop."""
    n = keys.shape[0]
    seed_u64 = np.asarray(np.int64(seed)).view(np.uint64)
    state = np.full(n, seed_u64 ^ np.uint64(0x7065743273706C74), dtype=np.uint64)
    unsigned = keys.view(np.uint64)
    # Identity width is tiny (normally run/subrun/event); only columns loop in
    # Python while all event rows are processed by NumPy at once.
    for column in range(unsigned.shape[1]):
        salt = np.uint64(
            (0xD1B54A32D192ED03 * (column + 1)) & ((1 << 64) - 1)
        )
        state = _splitmix64(state ^ _splitmix64(unsigned[:, column] ^ salt))
    return state


def stable_partition(
    row_index: np.ndarray,
    seed: int,
    fractions: tuple[float, ...] = (0.7, 0.15, 0.15),
    identity: np.ndarray | None = None,
) -> np.ndarray:
    """Assign stable integer partitions using the same vectorized identity hash."""
    fractions_array = np.asarray(fractions, dtype=np.float64)
    if (
        fractions_array.ndim != 1
        or fractions_array.size < 2
        or np.any(fractions_array <= 0)
        or not np.isclose(fractions_array.sum(), 1.0, rtol=0.0, atol=1e-12)
    ):
        raise ValueError("partition fractions must be positive and sum to one")
    rows = np.asarray(row_index, dtype=np.int64)
    if rows.ndim != 1 or len(np.unique(rows)) != len(rows):
        raise ValueError("row_index must be a unique one-dimensional array")
    keys = rows[:, None] if identity is None else np.asarray(identity)
    if keys.ndim == 1:
        keys = keys[:, None]
    if (
        keys.ndim != 2
        or keys.shape[0] != rows.shape[0]
        or not np.issubdtype(keys.dtype, np.integer)
    ):
        raise ValueError("partition identities must be an aligned integer matrix")
    values = _vectorized_identity_hash(np.ascontiguousarray(keys, dtype=np.int64), seed)
    # Long-double division avoids a lossy uint64->float64 threshold comparison.
    unit = values.astype(np.longdouble) / np.longdouble(1 << 64)
    boundaries = np.cumsum(fractions_array[:-1], dtype=np.float64)
    assignments = np.searchsorted(boundaries, unit, side="right").astype(np.uint8)
    if len(rows) >= len(fractions) and len(np.unique(assignments)) < len(fractions):
        raise ValueError("deterministic partition produced an empty declared partition")
    return assignments


def effective_sample_size(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=np.float64)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights < 0):
        raise ValueError("ESS requires one-dimensional finite nonnegative weights")
    total = float(weights.sum())
    square = float(np.square(weights).sum())
    return 0.0 if square == 0.0 else total * total / square


def weight_summary(weights: np.ndarray) -> dict[str, Any]:
    weights = np.asarray(weights, dtype=np.float64)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)):
        raise ValueError("weight summary requires finite one-dimensional weights")
    if np.any(weights < 0):
        raise ValueError("training-weight summary received negative weights")
    quantiles = np.quantile(weights, [0, 0.01, 0.5, 0.99, 1.0])
    return {
        "count": int(weights.size),
        "sum": float(weights.sum()),
        "nonzero": int(np.count_nonzero(weights)),
        "ess": effective_sample_size(weights),
        "quantiles": {
            key: float(value)
            for key, value in zip(("q0", "q01", "q50", "q99", "q100"), quantiles)
        },
        "sha256": array_hash(weights),
    }


def git_state(repo: os.PathLike[str] | str) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(
                ["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return "unavailable"

    status = run("status", "--porcelain")
    return {
        "commit": run("rev-parse", "HEAD"),
        "dirty": status not in ("", "unavailable"),
    }


def environment_receipt() -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "python_executable": sys.executable,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
    }
    try:
        import torch

        receipt["torch"] = torch.__version__
        receipt["cuda_available"] = bool(torch.cuda.is_available())
        receipt["cuda_version"] = torch.version.cuda
        if torch.cuda.is_available():
            receipt["gpu"] = torch.cuda.get_device_name(0)
    except Exception as exc:
        receipt["torch"] = None
        receipt["torch_unavailable_reason"] = f"{type(exc).__name__}: {exc}"
    try:
        import safetensors

        receipt["safetensors"] = safetensors.__version__
    except Exception as exc:
        receipt["safetensors"] = None
        receipt["safetensors_unavailable_reason"] = f"{type(exc).__name__}: {exc}"
    return receipt


def seed_everything(seed: int, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, NumPy, and (when available) PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    settings: dict[str, Any] = {"python": seed, "numpy": seed}
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
        if hasattr(torch.backends, "cuda") and hasattr(torch.backends.cuda, "matmul"):
            torch.backends.cuda.matmul.allow_tf32 = False
        settings.update(
            {
                "torch": seed,
                "deterministic_algorithms": bool(deterministic),
                "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
                "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
                "tf32": False,
            }
        )
    except ImportError:
        settings["torch"] = "unavailable"
    return settings
