#!/usr/bin/env python3
"""
Read-only, independent standard-p4 cross-object audit:

    C4_stored ?= M C5 M^T

No pipeline modules are imported. M is reconstructed solely from hard-coded
analysis edges and the positive supports of the two central products.

The projection is evaluated in row blocks using M's sparse structure. This
avoids materialising the full 4825x10694 dense M while still streaming its
dense C-order bytes through SHA-256. Per-block hashes and additive checksums
make truncation or an incomplete run visible from stdout alone.

Dependencies: standard library, NumPy, PyROOT.
Writes: none.
"""

import datetime as dt
import hashlib
import json
import math
import os
import platform
import sys
import traceback
from pathlib import Path

import numpy as np
import ROOT


SCRIPT_ID = "standard-p4-cross-object-projection-audit-v1-2026-08-10"
PREFIX = "AUDITP4X"
BASE = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding")

INPUTS = {
    "C5_file": {
        "path": BASE / "active_universe_5d/standard/candidate/std_final5_candidate.root",
        "key": "hCov_stdcombined5d_total_candidate",
        "expected_file_sha256":
            "602bbcf26606844941b8a6295f47e080507c20097a80f42cdf202bd8c567f037",
        "expected_content_sha256":
            "f26b3bfeaaa2dce14a8c39e22795b85facb93d89e78b2c312fe28c3ba38dded4",
    },
    "C4_file": {
        "path": BASE / "active_universe_5d/standard/candidate/std_proj4d_candidate.root",
        "key": "hCov_std_proj4d_candidate",
        # No prior whole-file digest was supplied. The expected array-content
        # digest below binds this ROOT object to the already-audited 4D NPZ.
        "expected_file_sha256": None,
        "expected_content_sha256":
            "c1fe11b17e3c3819b3e3f4b089301dddf7871c7790b914dccc303f4914756cbf",
    },
    "central5_file": {
        "path": BASE / "products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
        "key": "hXSecND_flat",
        "expected_file_sha256":
            "630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8",
        "expected_content_sha256":
            "d94daca9251d095115f20808a84052bd9b38ad2534da10ae32e48588531a5968",
    },
    "central4_file": {
        "path": BASE / "products/4d/xsec_4d_MEFHC_5iter_lgbm.root",
        "key": "hXSecND_flat",
        "expected_file_sha256":
            "1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2",
        "expected_content_sha256":
            "b1d3f9d1992017bf4cca8db48401305dddb2a6ade20d617fea637836138bf1da",
    },
}

AXIS_NAMES_5D = ("pt", "pz", "eavail", "q3", "W")
W_AXIS = 4

EDGES = {
    "pt": np.array(
        [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
         0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50],
        dtype=np.float64,
    ),
    "pz": np.array(
        [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
         6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0],
        dtype=np.float64,
    ),
    "eavail": np.array(
        [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0],
        dtype=np.float64,
    ),
    "q3": np.array(
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0],
        dtype=np.float64,
    ),
    "W": np.array(
        [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0],
        dtype=np.float64,
    ),
}

EXPECTED_COUNTS = {
    "full5": 65856,
    "reported5": 10694,
    "full4": 10976,
    "reported4": 4830,
    "reachable4": 4825,
    "unreachable4": 5,
}

EXPECTED_MASK_INDEX_SHA256 = {
    # SHA-256 over sorted C-order global indices encoded as little-endian int64.
    "reported5":
        "61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08",
    "reported4":
        "11e5482f6ff2bf92f17e08b4f6274cdf119ea9a54f24d709e0cea8bea6f452d4",
    "reachable4":
        "de966d2a16bc695ff2077b20f7293420a67fdae03b2e62b3591426edcad67427",
    "effective4":
        "de966d2a16bc695ff2077b20f7293420a67fdae03b2e62b3591426edcad67427",
    "unreachable4":
        "0ee3a98a7559990a16c8ea743cbd3387e6236ac762e6d31e7cb844e62dc8a5ad",
}

PREVIOUS_UNREACHABLE_4D = np.array(
    [9679, 9686, 9714, 9721, 10169], dtype=np.int64
)

# Diagnostic comparison only: never used to build M or decide the identity.
PIPELINE_M_CONTENT_SHA256_CLAIM = (
    "2f042f760c3550a52e2d56d3a78ff09320eed4666e6254d5f3c3c60581066362"
)
PIPELINE_PROJECTION_RELERR_CLAIM = 9.392172637224931e-17

BLOCK_ROWS = 256
IDENTITY_RTOL = 1.0e-12

CURRENT_STAGE = "startup"
COMPLETED_STAGES = []


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot JSON-encode {type(value)!r}")


def emit(kind, **fields):
    payload = {
        "utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        **fields,
    }
    print(
        PREFIX + "|" + kind + "|" +
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=json_default,
        ),
        flush=True,
    )


def begin_stage(number, name):
    global CURRENT_STAGE
    CURRENT_STAGE = f"{number}:{name}"
    emit("STAGE_BEGIN", number=number, name=name)


def finish_stage(number, name):
    COMPLETED_STAGES.append(f"{number}:{name}")
    emit(
        "STAGE_DONE",
        number=number,
        name=name,
        completed_stages=list(COMPLETED_STAGES),
    )


def array_sha256(array):
    contiguous = np.ascontiguousarray(array)
    return hashlib.sha256(memoryview(contiguous).cast("B")).hexdigest()


def index_fingerprint(indices):
    encoded = np.asarray(indices, dtype="<i8")
    return hashlib.sha256(encoded.tobytes()).hexdigest()


def relative_difference(a, b):
    denom = max(abs(float(a)), abs(float(b)), np.finfo(np.float64).tiny)
    return abs(float(a) - float(b)) / denom


def hash_path(label, path, claimed_sha256=None, progress_bytes=4 << 30):
    path = Path(path)
    resolved = path.resolve(strict=True)
    size = resolved.stat().st_size
    digest = hashlib.sha256()
    done = 0
    next_progress = progress_bytes

    emit(
        "FILE_HASH_BEGIN",
        label=label,
        path=str(path),
        resolved_path=str(resolved),
        size_bytes=size,
        claimed_sha256=claimed_sha256,
    )

    with resolved.open("rb") as stream:
        while True:
            block = stream.read(32 << 20)
            if not block:
                break
            digest.update(block)
            done += len(block)
            if done >= next_progress:
                emit(
                    "FILE_HASH_PROGRESS",
                    label=label,
                    bytes_read=done,
                    size_bytes=size,
                    fraction=done / size,
                )
                while next_progress <= done:
                    next_progress += progress_bytes

    actual = digest.hexdigest()
    holds = None if claimed_sha256 is None else actual == claimed_sha256
    emit(
        "FILE_HASH_END",
        label=label,
        path=str(path),
        resolved_path=str(resolved),
        size_bytes=size,
        bytes_read=done,
        sha256=actual,
        claimed_sha256=claimed_sha256,
        claim_holds=holds,
    )
    return {
        "path": str(resolved),
        "size_bytes": size,
        "bytes_read": done,
        "sha256": actual,
        "claimed_sha256": claimed_sha256,
        "claim_holds": holds,
    }


def open_root(path):
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"cannot open ROOT file: {path}")
    if root_file.TestBit(ROOT.TFile.kRecovered):
        root_file.Close()
        raise RuntimeError(f"ROOT file is marked recovered: {path}")
    return root_file


def histogram_dtype(histogram):
    if histogram.InheritsFrom("TH2D") or histogram.InheritsFrom("TH1D"):
        return np.float64
    if histogram.InheritsFrom("TH2F") or histogram.InheritsFrom("TH1F"):
        return np.float32
    raise TypeError(f"unsupported histogram class {histogram.ClassName()}")


def root_buffer(histogram, dtype, count):
    try:
        return np.frombuffer(histogram.GetArray(), dtype=dtype, count=count)
    except Exception:
        view = histogram.GetArray()
        try:
            view.reshape((count,))
        except TypeError:
            view.reshape(count)
        array = np.asarray(view, dtype=dtype)
        if array.size < count:
            raise RuntimeError(
                f"ROOT buffer exposes {array.size} cells; expected {count}"
            )
        return array[:count]


def load_th1(path, key, label, expected_content_sha256):
    root_file = open_root(path)
    histogram = root_file.Get(key)
    if not histogram:
        root_file.Close()
        raise KeyError(f"{path}:{key} is missing")
    if not histogram.InheritsFrom("TH1") or int(histogram.GetDimension()) != 1:
        class_name = histogram.ClassName()
        root_file.Close()
        raise TypeError(f"{path}:{key} is {class_name}, expected one-dimensional TH1")

    dtype = histogram_dtype(histogram)
    nx = int(histogram.GetNbinsX())
    storage_count = nx + 2
    raw = root_buffer(histogram, dtype, storage_count)
    core = np.array(raw[1:-1], dtype=np.float64, order="C", copy=True)
    underflow = float(raw[0])
    overflow = float(raw[-1])
    class_name = histogram.ClassName()
    root_file.Close()

    content_hash = array_sha256(core)
    content_holds = content_hash == expected_content_sha256
    emit(
        "ARRAY_LOADED",
        label=label,
        path=str(path),
        key=key,
        root_class=class_name,
        storage_shape=[storage_count],
        core_shape=list(core.shape),
        dtype=str(core.dtype),
        nbytes=int(core.nbytes),
        underflow=underflow,
        overflow=overflow,
        finite_count=int(np.count_nonzero(np.isfinite(core))),
        positive_count=int(np.count_nonzero(core > 0)),
        zero_count=int(np.count_nonzero(core == 0)),
        negative_count=int(np.count_nonzero(core < 0)),
        content_sha256=content_hash,
        expected_content_sha256=expected_content_sha256,
        content_claim_holds=content_holds,
    )
    if not content_holds:
        raise RuntimeError(f"{label} content SHA-256 differs from prior audited array")
    return core


def load_th2(path, key, label, expected_content_sha256):
    root_file = open_root(path)
    histogram = root_file.Get(key)
    if not histogram:
        root_file.Close()
        raise KeyError(f"{path}:{key} is missing")
    if not histogram.InheritsFrom("TH2") or int(histogram.GetDimension()) != 2:
        class_name = histogram.ClassName()
        root_file.Close()
        raise TypeError(f"{path}:{key} is {class_name}, expected TH2")

    dtype = histogram_dtype(histogram)
    nx = int(histogram.GetNbinsX())
    ny = int(histogram.GetNbinsY())
    storage_count = (nx + 2) * (ny + 2)
    raw = root_buffer(histogram, dtype, storage_count)
    storage = raw.reshape(ny + 2, nx + 2)

    border_max = max(
        float(np.max(np.abs(storage[0, :]))),
        float(np.max(np.abs(storage[-1, :]))),
        float(np.max(np.abs(storage[:, 0]))),
        float(np.max(np.abs(storage[:, -1]))),
    )
    core = np.array(
        storage[1:-1, 1:-1],
        dtype=np.float64,
        order="C",
        copy=True,
    )
    class_name = histogram.ClassName()
    root_file.Close()

    content_hash = array_sha256(core)
    content_holds = content_hash == expected_content_sha256
    emit(
        "ARRAY_LOADED",
        label=label,
        path=str(path),
        key=key,
        root_class=class_name,
        root_nbins_x=nx,
        root_nbins_y=ny,
        storage_shape=[ny + 2, nx + 2],
        core_shape=list(core.shape),
        dtype=str(core.dtype),
        nbytes=int(core.nbytes),
        C_contiguous=bool(core.flags.c_contiguous),
        border_max_abs=border_max,
        finite_count=int(np.count_nonzero(np.isfinite(core))),
        content_sha256=content_hash,
        expected_content_sha256=expected_content_sha256,
        content_claim_holds=content_holds,
    )
    if not content_holds:
        raise RuntimeError(f"{label} content SHA-256 differs from prior audited array")
    return core


def mask_record(label, mask):
    indices = np.flatnonzero(np.asarray(mask, dtype=bool)).astype("<i8", copy=False)
    fingerprint = index_fingerprint(indices)
    expected = EXPECTED_MASK_INDEX_SHA256.get(label)
    record = {
        "label": label,
        "definition": "sorted C-order global indices encoded as little-endian int64",
        "full_mask_size": int(np.asarray(mask).size),
        "count_by_count_nonzero": int(np.count_nonzero(mask)),
        "count_by_index_length": int(indices.size),
        "index_sha256": fingerprint,
        "expected_index_sha256": expected,
        "fingerprint_claim_holds": None if expected is None else fingerprint == expected,
        "first_20_indices": indices[:20].tolist(),
        "last_20_indices": indices[-20:].tolist(),
    }
    emit("MASK_DERIVED", **record)
    return indices, record


def bin_descriptor(global_index, shape, axis_names):
    multi = tuple(
        int(i) for i in np.unravel_index(int(global_index), shape, order="C")
    )
    ranges = {}
    for axis_name, axis_bin in zip(axis_names, multi):
        edge = EDGES[axis_name]
        ranges[axis_name] = [float(edge[axis_bin]), float(edge[axis_bin + 1])]
    return {
        "global_index": int(global_index),
        "multi_index": list(multi),
        "ranges": ranges,
    }


def matrix_spectrum(label, matrix):
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{label} is not square: {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{label} contains non-finite entries")

    n = int(matrix.shape[0])
    symmetric = (matrix + matrix.T) * 0.5
    trace_entries = float(np.trace(symmetric))
    frobenius_entries = float(np.linalg.norm(symmetric, "fro"))

    start = dt.datetime.now(dt.timezone.utc)
    emit(
        "EIGENSOLVER_BEGIN",
        label=label,
        shape=list(matrix.shape),
        matrix_definition="(A + A.T)/2",
        start_utc=start.isoformat().replace("+00:00", "Z"),
    )
    eigenvalues = np.linalg.eigvalsh(symmetric)
    end = dt.datetime.now(dt.timezone.utc)
    del symmetric

    eig_min = float(eigenvalues[0])
    eig_max = float(eigenvalues[-1])
    abs_eigenvalues = np.abs(eigenvalues)
    scale = max(abs(eig_min), abs(eig_max))
    tolerance = n * np.finfo(np.float64).eps * scale

    effective_positive = eigenvalues[eigenvalues > tolerance]
    effective_absolute = abs_eigenvalues[abs_eigenvalues > tolerance]
    exact_negative = eigenvalues[eigenvalues < 0]
    nonzero_abs = abs_eigenvalues[abs_eigenvalues > 0]

    trace_spectrum = float(np.sum(eigenvalues, dtype=np.float64))
    frobenius_spectrum = float(np.sqrt(np.dot(eigenvalues, eigenvalues)))

    raw_condition = (
        float(np.max(abs_eigenvalues) / np.min(nonzero_abs))
        if nonzero_abs.size else math.inf
    )
    effective_condition = (
        float(eig_max / effective_positive[0])
        if effective_positive.size else math.inf
    )

    result = {
        "label": label,
        "shape": list(matrix.shape),
        "elapsed_seconds": (end - start).total_seconds(),
        "n_eigenvalues": int(eigenvalues.size),
        "min_eigenvalue": eig_min,
        "max_eigenvalue": eig_max,
        "min_over_max": eig_min / eig_max if eig_max else math.nan,
        "exact_negative_count": int(exact_negative.size),
        "max_absolute_negative": (
            float(np.max(np.abs(exact_negative)))
            if exact_negative.size else 0.0
        ),
        "significant_negative_count": int(
            np.count_nonzero(eigenvalues < -tolerance)
        ),
        "rank_tolerance_definition": "n * float64_epsilon * max_abs_eigenvalue",
        "rank_tolerance": tolerance,
        "effective_positive_rank": int(effective_positive.size),
        "effective_absolute_rank": int(effective_absolute.size),
        "numerical_null_count": int(n - effective_absolute.size),
        "raw_floating_point_condition_2norm": raw_condition,
        "numerical_condition_2norm": (
            "infinity" if effective_absolute.size < n else raw_condition
        ),
        "effective_nonnull_condition": effective_condition,
        "trace_from_diagonal": trace_entries,
        "trace_from_eigenvalues": trace_spectrum,
        "trace_redundancy_relative":
            relative_difference(trace_entries, trace_spectrum),
        "frobenius_from_entries": frobenius_entries,
        "frobenius_from_eigenvalues": frobenius_spectrum,
        "frobenius_redundancy_relative":
            relative_difference(frobenius_entries, frobenius_spectrum),
        "eigenvalue_quantiles": {
            str(q): float(np.quantile(eigenvalues, q))
            for q in (0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1)
        },
    }
    emit("FULL_SPECTRUM", **result)
    return result


def main():
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)

    script_path = Path(__file__).resolve(strict=True)
    emit(
        "BEGIN",
        script_id=SCRIPT_ID,
        script_path=str(script_path),
        argv=sys.argv,
        cwd=os.getcwd(),
        hostname=platform.node(),
        platform=platform.platform(),
        python=sys.version,
        numpy=np.__version__,
        root=ROOT.gROOT.GetVersion(),
        pid=os.getpid(),
        block_rows=BLOCK_ROWS,
        identity_rtol=IDENTITY_RTOL,
        expected_stage_count=7,
        expected_end_sentinel=PREFIX + '|END|...status="COMPLETE"',
    )

    # ------------------------------------------------------------------ stage 1
    begin_stage(1, "hash_script_and_every_scientific_input")

    script_receipt = hash_path("executed_script", script_path)
    file_receipts = {}
    file_hash_failures = []

    for label, spec in INPUTS.items():
        emit(
            "INPUT_DECLARED",
            label=label,
            path=str(spec["path"]),
            key=spec["key"],
            expected_file_sha256=spec["expected_file_sha256"],
            expected_content_sha256=spec["expected_content_sha256"],
        )
        receipt = hash_path(
            label,
            spec["path"],
            spec["expected_file_sha256"],
        )
        file_receipts[label] = receipt
        if receipt["claim_holds"] is False:
            file_hash_failures.append(label)

    emit(
        "FILE_HASH_GATE",
        scientific_input_count=len(INPUTS),
        all_inputs_hashed=(len(file_receipts) == len(INPUTS)),
        claimed_hash_failure_count=len(file_hash_failures),
        claimed_hash_failures=file_hash_failures,
        note=(
            "C4 has no prior whole-file digest, but its loaded array is bound "
            "below to the content digest of the already-audited 4D object."
        ),
    )
    if file_hash_failures:
        raise RuntimeError(
            "known input file SHA-256 mismatch: " + ", ".join(file_hash_failures)
        )
    finish_stage(1, "hash_script_and_every_scientific_input")

    # ------------------------------------------------------------------ stage 2
    begin_stage(2, "load_centrals_and_derive_geometry_support_and_M")

    edge_arrays = [EDGES[name] for name in AXIS_NAMES_5D]
    grid5 = tuple(int(edge.size - 1) for edge in edge_arrays)
    grid4 = tuple(grid5[i] for i in range(len(grid5)) if i != W_AXIS)
    full5 = int(np.prod(grid5, dtype=np.int64))
    full4 = int(np.prod(grid4, dtype=np.int64))

    edge_concat = b"".join(
        np.ascontiguousarray(edge).tobytes() for edge in edge_arrays
    )
    edge_pipe = b"|".join(
        np.ascontiguousarray(edge).tobytes() for edge in edge_arrays
    )
    emit(
        "GEOMETRY_DERIVED",
        axis_names_5d=list(AXIS_NAMES_5D),
        W_axis=W_AXIS,
        edge_shapes={name: list(EDGES[name].shape) for name in AXIS_NAMES_5D},
        edges={name: EDGES[name].tolist() for name in AXIS_NAMES_5D},
        bin_counts_5d=list(grid5),
        bin_counts_4d=list(grid4),
        full_bin_count_5d=full5,
        full_bin_count_4d=full4,
        product_check_5d=full5,
        product_check_4d=full4,
        expected_full_bin_count_5d=EXPECTED_COUNTS["full5"],
        expected_full_bin_count_4d=EXPECTED_COUNTS["full4"],
        concatenated_edge_sha256=hashlib.sha256(edge_concat).hexdigest(),
        pipe_separated_edge_sha256=hashlib.sha256(edge_pipe).hexdigest(),
    )
    if full5 != EXPECTED_COUNTS["full5"] or full4 != EXPECTED_COUNTS["full4"]:
        raise RuntimeError("independently derived full-grid size is unexpected")

    x5 = load_th1(
        INPUTS["central5_file"]["path"],
        INPUTS["central5_file"]["key"],
        "x5_central_full_grid",
        INPUTS["central5_file"]["expected_content_sha256"],
    )
    x4 = load_th1(
        INPUTS["central4_file"]["path"],
        INPUTS["central4_file"]["key"],
        "x4_central_full_grid",
        INPUTS["central4_file"]["expected_content_sha256"],
    )
    if x5.shape != (full5,) or x4.shape != (full4,):
        raise RuntimeError(
            f"central shapes {x5.shape}, {x4.shape} disagree with edge products"
        )
    if not np.all(np.isfinite(x5)) or not np.all(np.isfinite(x4)):
        raise RuntimeError("central product contains non-finite values")

    mask5 = x5 > 0
    mask4 = x4 > 0
    reported5, mask5_record = mask_record("reported5", mask5)
    reported4, mask4_record = mask_record("reported4", mask4)

    # Generic C-order high-to-low mapping derived from the edge-implied shapes.
    strides5 = np.array(
        [int(np.prod(grid5[i + 1:], dtype=np.int64)) for i in range(5)],
        dtype=np.int64,
    )
    strides4 = np.array(
        [int(np.prod(grid4[i + 1:], dtype=np.int64)) for i in range(4)],
        dtype=np.int64,
    )
    multi5 = (
        reported5[:, None] // strides5[None, :]
    ) % np.asarray(grid5, dtype=np.int64)[None, :]
    W_bin_for_column = multi5[:, W_AXIS].astype(np.int64, copy=False)
    low_multi = np.delete(multi5, W_AXIS, axis=1)
    low_global_for_column = np.sum(
        low_multi * strides4[None, :],
        axis=1,
        dtype=np.int64,
    )

    reachable4_mask = np.zeros(full4, dtype=bool)
    reachable4_mask[np.unique(low_global_for_column)] = True
    effective4_mask = mask4 & reachable4_mask
    unreachable4_mask = mask4 & ~reachable4_mask
    reachable_outside_reported4_mask = reachable4_mask & ~mask4

    reachable4, reachable_record = mask_record(
        "reachable4", reachable4_mask
    )
    effective4, effective_record = mask_record(
        "effective4", effective4_mask
    )
    unreachable4, unreachable_record = mask_record(
        "unreachable4", unreachable4_mask
    )
    reachable_outside_reported4 = np.flatnonzero(
        reachable_outside_reported4_mask
    )

    widths = {
        name: np.diff(EDGES[name]) for name in AXIS_NAMES_5D
    }
    volume4_tensor = np.ones(grid4, dtype=np.float64)
    for axis, name in enumerate(AXIS_NAMES_5D[:4]):
        shape = [1] * 4
        shape[axis] = widths[name].size
        volume4_tensor *= widths[name].reshape(shape)
    volume4 = volume4_tensor.ravel(order="C")

    reported4_physical_total = float(np.sum(
        x4[reported4] * volume4[reported4],
        dtype=np.float64,
    ))
    unreachable4_physical_total = float(np.sum(
        x4[unreachable4] * volume4[unreachable4],
        dtype=np.float64,
    ))
    unreachable4_percent = (
        100.0 * unreachable4_physical_total / reported4_physical_total
        if reported4_physical_total else math.nan
    )

    unreachable_descriptors = [
        bin_descriptor(index, grid4, AXIS_NAMES_5D[:4])
        for index in unreachable4
    ]
    exact_previous_unreachable_match = np.array_equal(
        unreachable4.astype(np.int64),
        PREVIOUS_UNREACHABLE_4D,
    )
    emit(
        "UNREACHABLE_4D_CHECK",
        independently_derived_count=int(unreachable4.size),
        independently_derived_global_indices=unreachable4.tolist(),
        independently_derived_bin_descriptors=unreachable_descriptors,
        previous_audit_global_indices=PREVIOUS_UNREACHABLE_4D.tolist(),
        exact_previous_audit_match=exact_previous_unreachable_match,
        reported4_physical_total=reported4_physical_total,
        unreachable4_physical_total=unreachable4_physical_total,
        unreachable4_percent_of_reported4_total=unreachable4_percent,
        reachable_but_not_reported4_count=int(
            reachable_outside_reported4.size
        ),
        reachable_but_not_reported4_indices=
            reachable_outside_reported4[:20].tolist(),
    )

    independently_derived_counts = {
        "full5": full5,
        "reported5": int(reported5.size),
        "full4": full4,
        "reported4": int(reported4.size),
        "reachable4": int(reachable4.size),
        "effective4": int(effective4.size),
        "unreachable4": int(unreachable4.size),
        "reachable_outside_reported4":
            int(reachable_outside_reported4.size),
    }
    emit(
        "COUNT_GATE",
        independently_derived=independently_derived_counts,
        prior_claims=EXPECTED_COUNTS,
        all_claimed_counts_hold=(
            full5 == EXPECTED_COUNTS["full5"]
            and reported5.size == EXPECTED_COUNTS["reported5"]
            and full4 == EXPECTED_COUNTS["full4"]
            and reported4.size == EXPECTED_COUNTS["reported4"]
            and effective4.size == EXPECTED_COUNTS["reachable4"]
            and unreachable4.size == EXPECTED_COUNTS["unreachable4"]
        ),
    )

    if reachable_outside_reported4.size:
        raise RuntimeError(
            "a reported 5D bin maps to a non-reported 4D destination"
        )
    if not exact_previous_unreachable_match:
        raise RuntimeError("unreachable 4D bins differ from the previous audit")

    low_position = np.full(full4, -1, dtype=np.int64)
    low_position[effective4] = np.arange(effective4.size, dtype=np.int64)
    row_for_column = low_position[low_global_for_column]
    if np.any(row_for_column < 0):
        bad = np.flatnonzero(row_for_column < 0)
        raise RuntimeError(
            f"{bad.size} reported 5D columns have no effective 4D row"
        )

    W_widths = widths["W"]
    weight_for_column = W_widths[W_bin_for_column]

    # At most one high-grid cell exists for a given effective 4D row and W bin.
    high_column_by_low_row_and_W = np.full(
        (effective4.size, W_widths.size),
        -1,
        dtype=np.int64,
    )
    for column in range(reported5.size):
        row = int(row_for_column[column])
        W_bin = int(W_bin_for_column[column])
        if high_column_by_low_row_and_W[row, W_bin] != -1:
            raise RuntimeError(
                f"duplicate high cell for low row {row}, W bin {W_bin}"
            )
        high_column_by_low_row_and_W[row, W_bin] = column

    row_nnz = np.count_nonzero(
        high_column_by_low_row_and_W >= 0,
        axis=1,
    )
    row_nnz_values, row_nnz_counts = np.unique(
        row_nnz,
        return_counts=True,
    )
    W_bin_counts = np.bincount(
        W_bin_for_column,
        minlength=W_widths.size,
    )

    mapping_hasher = hashlib.sha256()
    for array in (
        reported5.astype("<i8", copy=False),
        low_global_for_column.astype("<i8", copy=False),
        row_for_column.astype("<i8", copy=False),
        W_bin_for_column.astype("<i8", copy=False),
    ):
        mapping_hasher.update(array.tobytes())

    emit(
        "M_SPARSE_CONSTRUCTION",
        construction=(
            "one nonzero per reported 5D column; row is sorted effective "
            "4D C-order support, value is width of that column's W bin"
        ),
        M_shape=[int(effective4.size), int(reported5.size)],
        sparse_nnz_by_column_count=int(reported5.size),
        sparse_nnz_by_slot_count=int(np.count_nonzero(
            high_column_by_low_row_and_W >= 0
        )),
        W_widths=W_widths.tolist(),
        reported_columns_by_W_bin=W_bin_counts.tolist(),
        row_nnz_distribution={
            str(int(value)): int(count)
            for value, count in zip(row_nnz_values, row_nnz_counts)
        },
        min_row_nnz=int(np.min(row_nnz)),
        max_row_nnz=int(np.max(row_nnz)),
        high_to_low_mapping_sha256=mapping_hasher.hexdigest(),
        first_20_effective4_global_indices=effective4[:20].tolist(),
        last_20_effective4_global_indices=effective4[-20:].tolist(),
        first_10_row_descriptors=[
            bin_descriptor(index, grid4, AXIS_NAMES_5D[:4])
            for index in effective4[:10]
        ],
        last_10_row_descriptors=[
            bin_descriptor(index, grid4, AXIS_NAMES_5D[:4])
            for index in effective4[-10:]
        ],
    )

    # Redundant central projection:
    # A: sparse row accumulation using the independently built M map.
    # B: reshape full 5D central and contract its W axis directly.
    marginal_sparse = np.bincount(
        row_for_column,
        weights=weight_for_column * x5[reported5],
        minlength=effective4.size,
    ).astype(np.float64, copy=False)
    marginal_tensor_full = np.tensordot(
        x5.reshape(grid5, order="C"),
        W_widths,
        axes=([W_AXIS], [0]),
    ).ravel(order="C")
    marginal_tensor = marginal_tensor_full[effective4]
    marginal_difference = marginal_sparse - marginal_tensor
    marginal_scale = max(
        float(np.max(np.abs(marginal_sparse))),
        float(np.max(np.abs(marginal_tensor))),
        np.finfo(np.float64).tiny,
    )
    emit(
        "REDUNDANT_CENTRAL_MARGINAL",
        route_A="sparse M row accumulation over reported 5D support",
        route_B="full 5D tensor contraction over W axis",
        route_A_shape=list(marginal_sparse.shape),
        route_B_shape=list(marginal_tensor.shape),
        route_A_sha256=array_sha256(marginal_sparse),
        route_B_sha256=array_sha256(marginal_tensor),
        max_abs_difference=float(np.max(np.abs(marginal_difference))),
        max_relative_to_marginal_scale=float(
            np.max(np.abs(marginal_difference)) / marginal_scale
        ),
        L2_relative=float(
            np.linalg.norm(marginal_difference) /
            max(np.linalg.norm(marginal_tensor), np.finfo(np.float64).tiny)
        ),
        sum_route_A=float(np.sum(marginal_sparse, dtype=np.float64)),
        sum_route_B=float(np.sum(marginal_tensor, dtype=np.float64)),
    )

    finish_stage(2, "load_centrals_and_derive_geometry_support_and_M")

    # ------------------------------------------------------------------ stage 3
    begin_stage(3, "load_covariances_and_bind_to_prior_product_audits")

    C5 = load_th2(
        INPUTS["C5_file"]["path"],
        INPUTS["C5_file"]["key"],
        "C5_stored",
        INPUTS["C5_file"]["expected_content_sha256"],
    )
    C4_stored = load_th2(
        INPUTS["C4_file"]["path"],
        INPUTS["C4_file"]["key"],
        "C4_stored",
        INPUTS["C4_file"]["expected_content_sha256"],
    )

    expected_C5_shape = (reported5.size, reported5.size)
    expected_C4_shape = (effective4.size, effective4.size)
    shape_holds = (
        C5.shape == expected_C5_shape
        and C4_stored.shape == expected_C4_shape
    )
    emit(
        "COVARIANCE_SHAPE_GATE",
        C5_shape=list(C5.shape),
        expected_C5_shape=list(expected_C5_shape),
        C4_stored_shape=list(C4_stored.shape),
        expected_C4_shape=list(expected_C4_shape),
        M_shape=[int(effective4.size), int(reported5.size)],
        holds=shape_holds,
    )
    if not shape_holds:
        raise RuntimeError("covariance dimensions disagree with reconstructed supports")
    if not np.all(np.isfinite(C5)) or not np.all(np.isfinite(C4_stored)):
        raise RuntimeError("covariance contains non-finite entries")

    finish_stage(3, "load_covariances_and_bind_to_prior_product_audits")

    # ------------------------------------------------------------------ stage 4
    begin_stage(4, "blocked_projection_and_dense_M_fingerprint")

    n5 = int(reported5.size)
    n4 = int(effective4.size)
    expected_blocks = int(math.ceil(n4 / BLOCK_ROWS))
    emit(
        "BLOCK_PLAN",
        M_shape=[n4, n5],
        C5_shape=list(C5.shape),
        C4_output_shape=[n4, n4],
        block_rows=BLOCK_ROWS,
        expected_block_count=expected_blocks,
        projection_formula="C4[a,b] = sum_i_in_a sum_j_in_b w_i*C5[i,j]*w_j",
        note=(
            "M is represented by row_for_column and weight_for_column. "
            "Each dense M row block is nevertheless constructed and hashed."
        ),
    )

    C4_recomputed = np.empty((n4, n4), dtype=np.float64, order="C")

    # Reproduce a deterministic dense-M content digest without retaining full M.
    M_raw_hasher = hashlib.sha256()
    M_content_hasher = hashlib.sha256()
    M_content_hasher.update(repr((n4, n5)).encode())
    M_content_hasher.update(b"|C|f8|")

    C4_stream_hasher = hashlib.sha256()
    completed_blocks = 0
    dense_M_nnz_total = 0
    dense_M_columns_total = 0
    projected_element_total = 0
    projected_sum_from_blocks = 0.0
    projected_trace_from_blocks = 0.0
    projected_ssq_from_blocks = 0.0
    block_hashes = []

    for block_number, low in enumerate(range(0, n4, BLOCK_ROWS), start=1):
        high = min(n4, low + BLOCK_ROWS)
        block_height = high - low

        columns = np.flatnonzero(
            (row_for_column >= low) & (row_for_column < high)
        )
        M_block = np.zeros((block_height, n5), dtype=np.float64, order="C")
        M_block[
            row_for_column[columns] - low,
            columns,
        ] = weight_for_column[columns]

        M_block_hash = array_sha256(M_block)
        M_raw_hasher.update(memoryview(M_block).cast("B"))
        M_content_hasher.update(memoryview(M_block).cast("B"))
        M_block_nnz = int(np.count_nonzero(M_block))
        dense_M_nnz_total += M_block_nnz
        dense_M_columns_total += int(columns.size)

        # left = M_block @ C5, using the fact that each row has at most
        # one source column for each of the six W bins.
        left = np.zeros((block_height, n5), dtype=np.float64, order="C")
        for W_bin, W_width in enumerate(W_widths):
            source_columns = high_column_by_low_row_and_W[
                low:high, W_bin
            ]
            valid_local_rows = np.flatnonzero(source_columns >= 0)
            if valid_local_rows.size:
                left[valid_local_rows, :] += (
                    W_width *
                    C5[source_columns[valid_local_rows], :]
                )

        # output_block = left @ M.T, again grouped by W bin.
        output_block = np.zeros(
            (block_height, n4),
            dtype=np.float64,
            order="C",
        )
        for W_bin, W_width in enumerate(W_widths):
            source_columns = high_column_by_low_row_and_W[:, W_bin]
            valid_destinations = np.flatnonzero(source_columns >= 0)
            if valid_destinations.size:
                output_block[:, valid_destinations] += (
                    W_width *
                    left[:, source_columns[valid_destinations]]
                )

        C4_recomputed[low:high, :] = output_block
        C4_stream_hasher.update(memoryview(output_block).cast("B"))

        output_block_hash = array_sha256(output_block)
        block_sum = float(np.sum(output_block, dtype=np.float64))
        block_trace = float(np.sum(
            output_block[
                np.arange(block_height),
                np.arange(low, high),
            ],
            dtype=np.float64,
        ))
        block_ssq = float(np.dot(
            output_block.ravel(),
            output_block.ravel(),
        ))

        projected_element_total += int(output_block.size)
        projected_sum_from_blocks += block_sum
        projected_trace_from_blocks += block_trace
        projected_ssq_from_blocks += block_ssq
        completed_blocks += 1
        block_hashes.append(output_block_hash)

        emit(
            "PROJECTION_BLOCK",
            block_number=block_number,
            expected_block_count=expected_blocks,
            low_row_inclusive=low,
            high_row_exclusive=high,
            block_height=block_height,
            dense_M_block_shape=list(M_block.shape),
            dense_M_block_nnz=M_block_nnz,
            source_high_columns=int(columns.size),
            dense_M_block_sha256=M_block_hash,
            left_shape=list(left.shape),
            output_block_shape=list(output_block.shape),
            output_block_elements=int(output_block.size),
            output_block_sha256=output_block_hash,
            output_block_sum=block_sum,
            output_block_trace_contribution=block_trace,
            output_block_sum_squares=block_ssq,
            running_completed_blocks=completed_blocks,
            running_M_nnz=dense_M_nnz_total,
            running_source_high_columns=dense_M_columns_total,
            running_projected_elements=projected_element_total,
            running_projected_sum=projected_sum_from_blocks,
            running_projected_trace=projected_trace_from_blocks,
            running_projected_sum_squares=projected_ssq_from_blocks,
        )

        del M_block, left, output_block

    M_raw_sha256 = M_raw_hasher.hexdigest()
    M_content_sha256 = M_content_hasher.hexdigest()
    C4_stream_sha256 = C4_stream_hasher.hexdigest()
    C4_final_sha256 = array_sha256(C4_recomputed)

    C4_sum_final = float(np.sum(C4_recomputed, dtype=np.float64))
    C4_trace_final = float(np.trace(C4_recomputed))
    C4_ssq_final = float(np.dot(
        C4_recomputed.ravel(),
        C4_recomputed.ravel(),
    ))

    emit(
        "BLOCK_RECONCILIATION",
        expected_block_count=expected_blocks,
        completed_block_count=completed_blocks,
        all_blocks_completed=(completed_blocks == expected_blocks),
        block_hash_count=len(block_hashes),
        block_hash_list=block_hashes,
        expected_M_nnz=n5,
        dense_M_nnz_from_blocks=dense_M_nnz_total,
        source_high_columns_from_blocks=dense_M_columns_total,
        sparse_mapping_columns=n5,
        M_raw_dense_bytes_sha256=M_raw_sha256,
        M_content_sha256_definition=(
            "sha256(repr(shape) + b'|C|f8|' + dense C-order float64 bytes)"
        ),
        M_content_sha256=M_content_sha256,
        pipeline_M_content_sha256_claim=PIPELINE_M_CONTENT_SHA256_CLAIM,
        pipeline_M_hash_claim_holds=(
            M_content_sha256 == PIPELINE_M_CONTENT_SHA256_CLAIM
        ),
        projected_elements_from_blocks=projected_element_total,
        expected_projected_elements=n4 * n4,
        projected_stream_sha256=C4_stream_sha256,
        projected_final_array_sha256=C4_final_sha256,
        stream_and_final_hash_agree=(
            C4_stream_sha256 == C4_final_sha256
        ),
        projected_sum_from_blocks=projected_sum_from_blocks,
        projected_sum_from_final_array=C4_sum_final,
        projected_sum_relative_redundancy=relative_difference(
            projected_sum_from_blocks, C4_sum_final
        ),
        projected_trace_from_blocks=projected_trace_from_blocks,
        projected_trace_from_final_array=C4_trace_final,
        projected_trace_relative_redundancy=relative_difference(
            projected_trace_from_blocks, C4_trace_final
        ),
        projected_ssq_from_blocks=projected_ssq_from_blocks,
        projected_ssq_from_final_array=C4_ssq_final,
        projected_ssq_relative_redundancy=relative_difference(
            projected_ssq_from_blocks, C4_ssq_final
        ),
    )

    if completed_blocks != expected_blocks:
        raise RuntimeError("not every declared projection block completed")
    if dense_M_nnz_total != n5 or dense_M_columns_total != n5:
        raise RuntimeError("dense M block census disagrees with sparse construction")
    if projected_element_total != n4 * n4:
        raise RuntimeError("projected block element census is incomplete")
    if C4_stream_sha256 != C4_final_sha256:
        raise RuntimeError("streamed and final projected-array hashes disagree")

    finish_stage(4, "blocked_projection_and_dense_M_fingerprint")

    # ------------------------------------------------------------------ stage 5
    begin_stage(5, "independent_element_probes_and_cross_object_identity")

    probe_rows = np.unique(np.array(
        [0, 1, n4 // 11, n4 // 7, n4 // 3,
         n4 // 2, (2 * n4) // 3, n4 - 2, n4 - 1],
        dtype=np.int64,
    ))
    probe_pairs = []
    for position, row_a in enumerate(probe_rows):
        probe_pairs.append((int(row_a), int(row_a)))
        row_b = int(probe_rows[(3 * position + 1) % probe_rows.size])
        if row_b != row_a:
            probe_pairs.append((int(row_a), row_b))

    probe_results = []
    probe_max_abs = 0.0
    probe_max_relative = 0.0

    for row_a, row_b in probe_pairs:
        columns_a = high_column_by_low_row_and_W[row_a]
        columns_b = high_column_by_low_row_and_W[row_b]
        columns_a = columns_a[columns_a >= 0]
        columns_b = columns_b[columns_b >= 0]
        weights_a = weight_for_column[columns_a]
        weights_b = weight_for_column[columns_b]

        direct = float(
            weights_a @ C5[np.ix_(columns_a, columns_b)] @ weights_b
        )
        blocked = float(C4_recomputed[row_a, row_b])
        absolute = abs(direct - blocked)
        denominator = max(
            abs(direct),
            abs(blocked),
            np.finfo(np.float64).tiny,
        )
        relative = absolute / denominator
        probe_max_abs = max(probe_max_abs, absolute)
        probe_max_relative = max(probe_max_relative, relative)

        probe_results.append({
            "row_a": row_a,
            "row_b": row_b,
            "row_a_global4": int(effective4[row_a]),
            "row_b_global4": int(effective4[row_b]),
            "n_high_a": int(columns_a.size),
            "n_high_b": int(columns_b.size),
            "direct_double_sum": direct,
            "blocked_projection": blocked,
            "absolute_difference": absolute,
            "relative_difference": relative,
        })

    emit(
        "DIRECT_ELEMENT_PROBES",
        route_A="explicit small double sum over source W cells",
        route_B="blocked whole-matrix projection",
        probe_count=len(probe_results),
        max_abs_difference=probe_max_abs,
        max_relative_difference=probe_max_relative,
        probes=probe_results,
    )

    difference = C4_recomputed - C4_stored
    recomputed_scale = float(np.max(np.abs(C4_recomputed)))
    stored_scale = float(np.max(np.abs(C4_stored)))
    comparison_scale = max(
        recomputed_scale,
        stored_scale,
        np.finfo(np.float64).tiny,
    )
    max_abs_difference = float(np.max(np.abs(difference)))
    max_scale_relative = max_abs_difference / comparison_scale
    frobenius_difference = float(np.linalg.norm(difference, "fro"))
    stored_frobenius = float(np.linalg.norm(C4_stored, "fro"))
    frobenius_relative = frobenius_difference / stored_frobenius

    diagonal_difference = (
        np.diag(C4_recomputed) - np.diag(C4_stored)
    )
    diagonal_scale = max(
        float(np.max(np.abs(np.diag(C4_stored)))),
        np.finfo(np.float64).tiny,
    )
    diagonal_max_scale_relative = (
        float(np.max(np.abs(diagonal_difference))) / diagonal_scale
    )

    trace_recomputed = float(np.trace(C4_recomputed))
    trace_stored = float(np.trace(C4_stored))
    sum_recomputed = float(np.sum(C4_recomputed, dtype=np.float64))
    sum_stored = float(np.sum(C4_stored, dtype=np.float64))

    identity_holds = (
        max_scale_relative <= IDENTITY_RTOL
        and frobenius_relative <= IDENTITY_RTOL
    )
    identity_result = (
        "ESTABLISHED_WITHIN_DECLARED_NUMERICAL_TOLERANCE"
        if identity_holds
        else "REFUTED_AT_DECLARED_NUMERICAL_TOLERANCE"
    )

    identity_metrics = {
        "formula_tested": "C4_stored = M C5 M^T",
        "C4_recomputed_shape": list(C4_recomputed.shape),
        "C4_stored_shape": list(C4_stored.shape),
        "C4_recomputed_content_sha256": C4_final_sha256,
        "C4_stored_content_sha256": array_sha256(C4_stored),
        "C4_recomputed_scale_max_abs": recomputed_scale,
        "C4_stored_scale_max_abs": stored_scale,
        "comparison_scale": comparison_scale,
        "max_abs_difference": max_abs_difference,
        "max_relative_to_matrix_scale": max_scale_relative,
        "frobenius_difference": frobenius_difference,
        "frobenius_relative": frobenius_relative,
        "diagonal_max_relative_to_stored_diagonal_scale":
            diagonal_max_scale_relative,
        "trace_recomputed": trace_recomputed,
        "trace_stored": trace_stored,
        "trace_relative_difference":
            relative_difference(trace_recomputed, trace_stored),
        "all_entries_sum_recomputed": sum_recomputed,
        "all_entries_sum_stored": sum_stored,
        "all_entries_sum_relative_difference":
            relative_difference(sum_recomputed, sum_stored),
        "exactly_equal_entry_count": int(np.count_nonzero(
            C4_recomputed == C4_stored
        )),
        "unequal_entry_count": int(np.count_nonzero(
            C4_recomputed != C4_stored
        )),
        "total_entry_count": int(C4_stored.size),
        "difference_absolute_quantiles": {
            str(q): float(np.quantile(np.abs(difference), q))
            for q in (0, 0.5, 0.9, 0.99, 0.999, 1)
        },
        "float64_epsilon": float(np.finfo(np.float64).eps),
        "max_scale_relative_in_float64_eps":
            max_scale_relative / np.finfo(np.float64).eps,
        "n5_times_float64_epsilon":
            n5 * np.finfo(np.float64).eps,
        "declared_identity_rtol": IDENTITY_RTOL,
        "identity_holds": identity_holds,
        "identity_result": identity_result,
        "pipeline_projection_identity_relerr_claim":
            PIPELINE_PROJECTION_RELERR_CLAIM,
        "observed_max_scale_relerr_over_pipeline_claim": (
            max_scale_relative / PIPELINE_PROJECTION_RELERR_CLAIM
            if PIPELINE_PROJECTION_RELERR_CLAIM else math.nan
        ),
        "note": (
            "The pipeline claim is printed only as a target. It is not used "
            "to construct M, compute the projection, or decide identity_holds."
        ),
    }
    emit("CROSS_OBJECT_IDENTITY", **identity_metrics)
    del difference, diagonal_difference

    finish_stage(
        5,
        "independent_element_probes_and_cross_object_identity",
    )

    # ------------------------------------------------------------------ stage 6
    begin_stage(6, "recompute_C5_and_both_C4_numerical_ranks")

    spectrum_C5 = matrix_spectrum("C5_stored", C5)
    del C5

    spectrum_C4_recomputed = matrix_spectrum(
        "C4_recomputed_from_M_C5_MT",
        C4_recomputed,
    )
    spectrum_C4_stored = matrix_spectrum(
        "C4_stored",
        C4_stored,
    )

    rank_preserved = (
        spectrum_C5["effective_positive_rank"]
        == spectrum_C4_recomputed["effective_positive_rank"]
        == spectrum_C4_stored["effective_positive_rank"]
    )
    all_numerically_singular = all(
        spectrum["numerical_condition_2norm"] == "infinity"
        for spectrum in (
            spectrum_C5,
            spectrum_C4_recomputed,
            spectrum_C4_stored,
        )
    )
    emit(
        "RANK_COMPARISON",
        rank_definition="positive eigenvalues > n*eps*max_abs_eigenvalue",
        C5_effective_positive_rank=
            spectrum_C5["effective_positive_rank"],
        C4_recomputed_effective_positive_rank=
            spectrum_C4_recomputed["effective_positive_rank"],
        C4_stored_effective_positive_rank=
            spectrum_C4_stored["effective_positive_rank"],
        C5_dimension=n5,
        C4_recomputed_dimension=n4,
        C4_stored_dimension=n4,
        rank_preserved_from_C5_through_projection=rank_preserved,
        C5_numerical_condition_2norm=
            spectrum_C5["numerical_condition_2norm"],
        C4_recomputed_numerical_condition_2norm=
            spectrum_C4_recomputed["numerical_condition_2norm"],
        C4_stored_numerical_condition_2norm=
            spectrum_C4_stored["numerical_condition_2norm"],
        all_three_numerically_singular=all_numerically_singular,
        C4_recomputed_effective_nonnull_condition=
            spectrum_C4_recomputed["effective_nonnull_condition"],
        C4_stored_effective_nonnull_condition=
            spectrum_C4_stored["effective_nonnull_condition"],
        structure_verdict=(
            "PRESERVED"
            if rank_preserved and all_numerically_singular
            else "NOT_PRESERVED"
        ),
    )

    finish_stage(6, "recompute_C5_and_both_C4_numerical_ranks")

    # ------------------------------------------------------------------ stage 7
    begin_stage(7, "completion_receipt")

    final_summary = {
        "script_id": SCRIPT_ID,
        "executed_script_sha256": script_receipt["sha256"],
        "scientific_input_file_sha256": {
            label: receipt["sha256"]
            for label, receipt in file_receipts.items()
        },
        "scientific_input_file_sizes": {
            label: receipt["size_bytes"]
            for label, receipt in file_receipts.items()
        },
        "grid5": list(grid5),
        "grid4": list(grid4),
        "independently_derived_counts": independently_derived_counts,
        "mask_index_sha256": {
            "reported5": mask5_record["index_sha256"],
            "reported4": mask4_record["index_sha256"],
            "reachable4": reachable_record["index_sha256"],
            "effective4": effective_record["index_sha256"],
            "unreachable4": unreachable_record["index_sha256"],
        },
        "unreachable4_global_indices": unreachable4.tolist(),
        "exact_previous_unreachable_match":
            exact_previous_unreachable_match,
        "unreachable4_percent_of_reported4_total":
            unreachable4_percent,
        "M_shape": [n4, n5],
        "M_nnz": dense_M_nnz_total,
        "M_content_sha256": M_content_sha256,
        "pipeline_M_hash_claim_holds": (
            M_content_sha256 == PIPELINE_M_CONTENT_SHA256_CLAIM
        ),
        "projection_block_rows": BLOCK_ROWS,
        "projection_expected_blocks": expected_blocks,
        "projection_completed_blocks": completed_blocks,
        "C4_recomputed_sha256": C4_final_sha256,
        "C4_stored_sha256": array_sha256(C4_stored),
        "identity_metrics": identity_metrics,
        "rank_summary": {
            "C5": spectrum_C5["effective_positive_rank"],
            "C4_recomputed":
                spectrum_C4_recomputed["effective_positive_rank"],
            "C4_stored":
                spectrum_C4_stored["effective_positive_rank"],
            "rank_preserved": rank_preserved,
            "all_numerical_conditions_infinite":
                all_numerically_singular,
        },
        "identity_result": identity_result,
        "completed_stages_before_summary": list(COMPLETED_STAGES),
    }
    emit("SUMMARY", **final_summary)

    finish_stage(7, "completion_receipt")

    emit(
        "END",
        status="COMPLETE",
        script_id=SCRIPT_ID,
        audit_outcome=identity_result,
        completed_stage_count=len(COMPLETED_STAGES),
        expected_stage_count=7,
        completed_stages=list(COMPLETED_STAGES),
        expected_block_count=expected_blocks,
        completed_block_count=completed_blocks,
        required_begin_seen=True,
        required_end_seen=True,
    )


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        emit(
            "ABORT_DETAIL",
            script_id=SCRIPT_ID,
            failed_stage=CURRENT_STAGE,
            completed_stages=list(COMPLETED_STAGES),
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            traceback=traceback.format_exc(),
        )
        emit(
            "END",
            status="ABORTED",
            script_id=SCRIPT_ID,
            failed_stage=CURRENT_STAGE,
            completed_stage_count=len(COMPLETED_STAGES),
            completed_stages=list(COMPLETED_STAGES),
            required_end_seen=True,
        )
        sys.exit(1)
