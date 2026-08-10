#!/usr/bin/env python3
"""
Read-only standard-p4 5D PRODUCT audit.

Standard library + NumPy + PyROOT only. It writes no files. Output is
self-identifying, hashes every data input, prints all loaded shapes, derives
its own support mask, performs redundant full-matrix identities, and ends
with an explicit COMPLETE or ABORTED sentinel.
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

SCRIPT_ID = "standard-p4-5d-product-audit-v1-2026-08-10"
BASE = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding")

INPUTS = {
    "candidate": {
        "path": BASE / "active_universe_5d/standard/candidate/std_final5_candidate.root",
        "sha256_claim": "602bbcf26606844941b8a6295f47e080507c20097a80f42cdf202bd8c567f037",
    },
    "central": {
        "path": BASE / "products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
        "sha256_claim": "630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8",
    },
    "stat": {
        "path": BASE / "uq_cov_stat_5d.root",
        "sha256_claim": "6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934",
    },
    "ml": {
        "path": BASE / "uq_cov_mlsplit_5d.root",
        "sha256_claim": "27b2e456f80e15d8a5c4da1bcd3b01a201b80385341af68614c85b6b7f8f5374",
    },
}

KEYS = {
    "central": "hXSecND_flat",
    "total": "hCov_stdcombined5d_total_candidate",
    "syst": "hCov_stdsyst5d_total_candidate",
    "active_total": "hCov_active5d_total",
    "stat": "hCov_stat5d_reported",
    "ml": "hCov_mlsplit5d_reported",
}

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
        "AUDIT5D|" + kind + "|" +
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   default=json_default),
        flush=True,
    )


def stage(number, name):
    global CURRENT_STAGE
    CURRENT_STAGE = f"{number}:{name}"
    emit("STAGE_BEGIN", number=number, name=name)


def finish_stage(number, name):
    COMPLETED_STAGES.append(f"{number}:{name}")
    emit("STAGE_DONE", number=number, name=name,
         completed_stages=list(COMPLETED_STAGES))


def array_sha256(array):
    a = np.ascontiguousarray(array)
    return hashlib.sha256(memoryview(a).cast("B")).hexdigest()


def hash_file(label, path, progress_bytes=4 << 30):
    path = Path(path)
    resolved = path.resolve(strict=True)
    size = resolved.stat().st_size
    digest = hashlib.sha256()
    done = 0
    next_progress = progress_bytes

    emit("FILE_HASH_BEGIN", label=label, path=str(path),
         resolved_path=str(resolved), size_bytes=size)

    with resolved.open("rb") as stream:
        while True:
            block = stream.read(32 << 20)
            if not block:
                break
            digest.update(block)
            done += len(block)
            if done >= next_progress:
                emit("FILE_HASH_PROGRESS", label=label,
                     bytes_read=done, size_bytes=size,
                     fraction=done / size)
                while next_progress <= done:
                    next_progress += progress_bytes

    value = digest.hexdigest()
    claim = INPUTS[label]["sha256_claim"]
    emit("FILE_HASH_END", label=label, path=str(path),
         resolved_path=str(resolved), size_bytes=size,
         bytes_read=done, sha256=value,
         claimed_sha256=claim, claim_holds=(value == claim))
    return value, size


def open_root(path):
    f = ROOT.TFile.Open(str(path), "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open ROOT file: {path}")
    if f.TestBit(ROOT.TFile.kRecovered):
        f.Close()
        raise RuntimeError(f"ROOT file is marked recovered: {path}")
    return f


def inventory_root(label, path):
    f = open_root(path)
    objects = []
    for key in f.GetListOfKeys():
        objects.append({
            "name": key.GetName(),
            "class": key.GetClassName(),
            "cycle": int(key.GetCycle()),
            "nbytes": int(key.GetNbytes()),
            "objlen": int(key.GetObjlen()),
        })
    f.Close()
    emit("ROOT_INVENTORY", label=label, path=str(path),
         n_keys=len(objects), objects=objects)
    return objects


def root_array_dtype(obj):
    if obj.InheritsFrom("TH2D") or obj.InheritsFrom("TH1D"):
        return np.float64
    if obj.InheritsFrom("TH2F") or obj.InheritsFrom("TH1F"):
        return np.float32
    raise TypeError(f"unsupported ROOT histogram class {obj.ClassName()}")


def root_buffer(obj, dtype):
    count = int(obj.GetNcells())
    try:
        return np.frombuffer(obj.GetArray(), dtype=dtype, count=count)
    except Exception:
        view = obj.GetArray()
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


def load_th1(path, key, label):
    f = open_root(path)
    h = f.Get(key)
    if not h:
        f.Close()
        raise KeyError(f"{path}:{key} is missing")
    if not h.InheritsFrom("TH1") or int(h.GetDimension()) != 1:
        cls = h.ClassName()
        f.Close()
        raise TypeError(f"{path}:{key} is {cls}, expected one-dimensional TH1")

    dtype = root_array_dtype(h)
    nx = int(h.GetNbinsX())
    raw = root_buffer(h, dtype)
    expected_storage = nx + 2
    if raw.size != expected_storage:
        f.Close()
        raise RuntimeError(
            f"{path}:{key} storage has {raw.size} cells; "
            f"expected {expected_storage}"
        )

    flow = [float(raw[0]), float(raw[-1])]
    core = np.array(raw[1:-1], dtype=np.float64, order="C", copy=True)
    cls = h.ClassName()
    f.Close()

    emit("ARRAY_LOADED", label=label, path=str(path), key=key,
         root_class=cls, storage_shape=[expected_storage],
         core_shape=list(core.shape), dtype=str(core.dtype),
         nbytes=int(core.nbytes), underflow=flow[0], overflow=flow[1],
         content_sha256=array_sha256(core))
    return core


def load_th2(path, key, label):
    f = open_root(path)
    h = f.Get(key)
    if not h:
        f.Close()
        raise KeyError(f"{path}:{key} is missing")
    if not h.InheritsFrom("TH2") or int(h.GetDimension()) != 2:
        cls = h.ClassName()
        f.Close()
        raise TypeError(f"{path}:{key} is {cls}, expected TH2")

    dtype = root_array_dtype(h)
    nx = int(h.GetNbinsX())
    ny = int(h.GetNbinsY())
    raw = root_buffer(h, dtype)
    expected_storage = (nx + 2) * (ny + 2)
    if raw.size != expected_storage:
        f.Close()
        raise RuntimeError(
            f"{path}:{key} storage has {raw.size} cells; "
            f"expected {expected_storage}"
        )

    storage = raw.reshape(ny + 2, nx + 2)
    border_max = max(
        float(np.max(np.abs(storage[0, :]))),
        float(np.max(np.abs(storage[-1, :]))),
        float(np.max(np.abs(storage[:, 0]))),
        float(np.max(np.abs(storage[:, -1]))),
    )
    core = np.array(storage[1:-1, 1:-1],
                    dtype=np.float64, order="C", copy=True)
    cls = h.ClassName()
    f.Close()

    emit("ARRAY_LOADED", label=label, path=str(path), key=key,
         root_class=cls, storage_shape=[ny + 2, nx + 2],
         core_shape=list(core.shape), dtype=str(core.dtype),
         nbytes=int(core.nbytes), border_max_abs=border_max,
         content_sha256=array_sha256(core))
    return core


def matrix_basic(label, matrix, block=256):
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{label} is not square: {matrix.shape}")

    n = matrix.shape[0]
    finite_count = 0
    nan_count = 0
    posinf_count = 0
    neginf_count = 0
    scale = 0.0
    asym_abs = 0.0

    for lo in range(0, n, block):
        hi = min(n, lo + block)
        part = matrix[lo:hi, :]
        finite_count += int(np.count_nonzero(np.isfinite(part)))
        nan_count += int(np.count_nonzero(np.isnan(part)))
        posinf_count += int(np.count_nonzero(np.isposinf(part)))
        neginf_count += int(np.count_nonzero(np.isneginf(part)))

        finite_values = part[np.isfinite(part)]
        if finite_values.size:
            scale = max(scale, float(np.max(np.abs(finite_values))))

        difference = part - matrix.T[lo:hi, :]
        finite_difference = difference[np.isfinite(difference)]
        if finite_difference.size:
            asym_abs = max(
                asym_abs, float(np.max(np.abs(finite_difference)))
            )

    diagonal = np.diag(matrix)
    result = {
        "label": label,
        "shape": list(matrix.shape),
        "size": int(matrix.size),
        "finite_count": finite_count,
        "nan_count": nan_count,
        "positive_inf_count": posinf_count,
        "negative_inf_count": neginf_count,
        "scale_max_abs": scale,
        "symmetry_max_abs": asym_abs,
        "symmetry_relative": asym_abs / scale if scale else 0.0,
        "diag_finite_count": int(np.count_nonzero(np.isfinite(diagonal))),
        "diag_negative_count": int(np.count_nonzero(diagonal < 0)),
        "diag_min": float(np.min(diagonal)),
        "diag_median": float(np.median(diagonal)),
        "diag_max": float(np.max(diagonal)),
        "trace": float(np.sum(diagonal, dtype=np.float64)),
    }
    emit("MATRIX_BASIC", **result)
    return result


def compare_matrix_sum(label, reference, terms, block=128):
    if any(term.shape != reference.shape for term in terms):
        raise ValueError(f"{label}: matrix shapes differ")

    n = reference.shape[0]
    max_abs_difference = 0.0
    reference_max_abs = 0.0
    difference_ss = 0.0
    reference_ss = 0.0
    nonzero_difference_count = 0

    for lo in range(0, n, block):
        hi = min(n, lo + block)
        ref = reference[lo:hi, :]
        diff = ref.copy()
        for term in terms:
            diff -= term[lo:hi, :]

        max_abs_difference = max(
            max_abs_difference, float(np.max(np.abs(diff)))
        )
        reference_max_abs = max(
            reference_max_abs, float(np.max(np.abs(ref)))
        )
        difference_ss += float(np.dot(diff.ravel(), diff.ravel()))
        reference_ss += float(np.dot(ref.ravel(), ref.ravel()))
        nonzero_difference_count += int(np.count_nonzero(diff))

    result = {
        "label": label,
        "reference_shape": list(reference.shape),
        "n_terms": len(terms),
        "term_shapes": [list(term.shape) for term in terms],
        "max_abs_difference": max_abs_difference,
        "max_relative_to_reference_scale":
            max_abs_difference / reference_max_abs
            if reference_max_abs else 0.0,
        "frobenius_relative":
            math.sqrt(difference_ss / reference_ss)
            if reference_ss else 0.0,
        "nonzero_difference_count": nonzero_difference_count,
    }
    emit("REDUNDANT_MATRIX_SUM", **result)
    return result


def quantiles(values):
    values = np.asarray(values)
    return {
        "min": float(np.min(values)),
        "p01": float(np.quantile(values, 0.01)),
        "median": float(np.median(values)),
        "p90": float(np.quantile(values, 0.90)),
        "p99": float(np.quantile(values, 0.99)),
        "max": float(np.max(values)),
    }


def main():
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)

    emit(
        "BEGIN",
        script_id=SCRIPT_ID,
        argv=sys.argv,
        cwd=os.getcwd(),
        hostname=platform.node(),
        platform=platform.platform(),
        python=sys.version,
        numpy=np.__version__,
        root=ROOT.gROOT.GetVersion(),
        pid=os.getpid(),
        expected_end_sentinel='AUDIT5D|END|...status="COMPLETE"',
    )

    stage(1, "hash_every_input")
    for label, spec in INPUTS.items():
        emit("INPUT_DECLARED", label=label, path=str(spec["path"]),
             claimed_sha256=spec["sha256_claim"])
        hash_file(label, spec["path"])
    finish_stage(1, "hash_every_input")

    stage(2, "derive_central_grid_and_support")
    central_inventory = inventory_root("central", INPUTS["central"]["path"])
    x5 = load_th1(
        INPUTS["central"]["path"], KEYS["central"], "x5_central_full_grid"
    )

    axis_names = list(EDGES)
    bin_counts = [len(EDGES[name]) - 1 for name in axis_names]
    grid_shape = tuple(bin_counts)
    full_bin_count = int(np.prod(grid_shape, dtype=np.int64))
    edge_bytes = b"".join(
        np.ascontiguousarray(EDGES[name]).tobytes() for name in axis_names
    )

    emit("GRID_DERIVED", axis_names=axis_names,
         bin_counts=bin_counts, grid_shape=list(grid_shape),
         product_bin_count=full_bin_count,
         central_array_count=int(x5.size),
         product_matches_central=(full_bin_count == x5.size),
         W_axis_derived=axis_names.index("W"),
         edges={name: EDGES[name].tolist() for name in axis_names},
         concatenated_edge_sha256=hashlib.sha256(edge_bytes).hexdigest(),
         central_root_n_keys=len(central_inventory))

    if x5.size != full_bin_count:
        raise RuntimeError(
            f"central has {x5.size} bins; edges derive {full_bin_count}"
        )

    mask = x5 > 0
    reported_indices = np.flatnonzero(mask).astype("<i8", copy=False)
    mask_fingerprint = hashlib.sha256(
        reported_indices.tobytes()
    ).hexdigest()

    emit("MASK_DERIVED",
         definition="x5_central_full_grid > 0",
         full_bin_count=int(x5.size),
         reported_count=int(reported_indices.size),
         zero_count=int(np.count_nonzero(x5 == 0)),
         negative_count=int(np.count_nonzero(x5 < 0)),
         finite_count=int(np.count_nonzero(np.isfinite(x5))),
         fingerprint_algorithm="sha256(sorted C-order flat indices as little-endian int64 bytes)",
         reported_index_sha256=mask_fingerprint,
         first_20_reported_indices=reported_indices[:20].tolist(),
         last_20_reported_indices=reported_indices[-20:].tolist())

    widths = [np.diff(EDGES[name]) for name in axis_names]
    volume = np.ones(grid_shape, dtype=np.float64)
    for axis, width in enumerate(widths):
        reshape = [1] * len(grid_shape)
        reshape[axis] = width.size
        volume *= width.reshape(reshape)
    volume = volume.ravel(order="C")

    total_dense = float(np.sum(x5 * volume, dtype=np.float64))
    total_reported = float(np.sum(
        x5[reported_indices] * volume[reported_indices],
        dtype=np.float64,
    ))
    emit("REDUNDANT_CENTRAL_TOTAL",
         route_A="sum over every full-grid bin",
         route_B="sum over independently derived positive support",
         total_route_A=total_dense,
         total_route_B=total_reported,
         absolute_difference=abs(total_dense - total_reported),
         relative_difference=(
             abs(total_dense - total_reported) / abs(total_dense)
             if total_dense else 0.0
         ))
    finish_stage(2, "derive_central_grid_and_support")

    stage(3, "load_and_check_total_covariance")
    candidate_inventory = inventory_root(
        "candidate", INPUTS["candidate"]["path"]
    )
    candidate_names = sorted({item["name"] for item in candidate_inventory})
    emit("CANDIDATE_KEYS_DERIVED",
         n_keys=len(candidate_names), keys=candidate_names)

    total = load_th2(
        INPUTS["candidate"]["path"], KEYS["total"], "C5_total"
    )
    support_dimension_holds = (
        total.shape ==
        (reported_indices.size, reported_indices.size)
    )
    emit("SUPPORT_DIMENSION_CHECK",
         covariance_shape=list(total.shape),
         derived_reported_count=int(reported_indices.size),
         expected_shape=[
             int(reported_indices.size), int(reported_indices.size)
         ],
         holds=support_dimension_holds,
         row_order_assumption=(
             "sorted C-order flat reported-bin indices; exact row labels "
             "must be supplied separately to prove this rather than infer it"
         ))
    if not support_dimension_holds:
        raise RuntimeError("covariance dimension does not match derived support")

    basic = matrix_basic("C5_total", total)
    if basic["finite_count"] != total.size:
        raise RuntimeError("total covariance contains non-finite entries")

    diagonal = np.diag(total)
    n = total.shape[0]
    max_abs_corr = 0.0
    cauchy_gt_one = 0
    cauchy_gt_tolerance = 0
    for lo in range(0, n, 128):
        hi = min(n, lo + 128)
        denominator = np.sqrt(
            diagonal[lo:hi, None] * diagonal[None, :]
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.divide(
                np.abs(total[lo:hi, :]),
                denominator,
                out=np.full_like(denominator, np.inf),
                where=denominator > 0,
            )
        zero_zero = (
            (denominator == 0) &
            (total[lo:hi, :] == 0)
        )
        ratio[zero_zero] = 0.0
        max_abs_corr = max(max_abs_corr, float(np.max(ratio)))
        cauchy_gt_one += int(np.count_nonzero(ratio > 1.0))
        cauchy_gt_tolerance += int(
            np.count_nonzero(ratio > 1.0 + 1e-12)
        )

    emit("CAUCHY_SCHWARZ_ALL_PAIRS",
         pairs_checked=int(total.size),
         max_abs_cov_over_sqrt_variances=max_abs_corr,
         count_greater_than_one=cauchy_gt_one,
         count_greater_than_one_plus_1e_12=cauchy_gt_tolerance)
    finish_stage(3, "load_and_check_total_covariance")

    stage(4, "full_eigenspectrum_and_redundant_invariants")
    symmetric = (total + total.T) * 0.5
    eig_start = dt.datetime.now(dt.timezone.utc)
    emit("EIGENSOLVER_BEGIN", shape=list(symmetric.shape),
         matrix="(C5_total + C5_total.T)/2",
         start_utc=eig_start.isoformat().replace("+00:00", "Z"))
    eigenvalues = np.linalg.eigvalsh(symmetric)
    eig_end = dt.datetime.now(dt.timezone.utc)
    emit("EIGENSOLVER_END",
         elapsed_seconds=(eig_end - eig_start).total_seconds(),
         end_utc=eig_end.isoformat().replace("+00:00", "Z"))

    eig_min = float(eigenvalues[0])
    eig_max = float(eigenvalues[-1])
    abs_eigenvalues = np.abs(eigenvalues)
    exact_negative = eigenvalues[eigenvalues < 0]
    exact_positive = eigenvalues[eigenvalues > 0]
    nonzero_abs = abs_eigenvalues[abs_eigenvalues > 0]
    numerical_tolerance = (
        n * np.finfo(np.float64).eps *
        max(abs(eig_min), abs(eig_max))
    )
    effective_positive = eigenvalues[
        eigenvalues > numerical_tolerance
    ]

    raw_condition = (
        float(np.max(abs_eigenvalues) / np.min(nonzero_abs))
        if nonzero_abs.size else math.inf
    )
    effective_condition = (
        float(eig_max / effective_positive[0])
        if effective_positive.size else math.inf
    )

    trace_diagonal = float(np.trace(symmetric))
    trace_spectrum = float(np.sum(eigenvalues, dtype=np.float64))
    frobenius_entries = float(np.linalg.norm(symmetric, "fro"))
    frobenius_spectrum = float(np.sqrt(
        np.dot(eigenvalues, eigenvalues)
    ))

    emit("FULL_SPECTRUM",
         n_eigenvalues=int(eigenvalues.size),
         min_eigenvalue=eig_min,
         max_eigenvalue=eig_max,
         min_over_max=eig_min / eig_max,
         exact_negative_count=int(exact_negative.size),
         exact_zero_count=int(np.count_nonzero(eigenvalues == 0)),
         exact_positive_count=int(exact_positive.size),
         max_absolute_negative=(
             float(np.max(np.abs(exact_negative)))
             if exact_negative.size else 0.0
         ),
         sum_absolute_negative=(
             float(np.sum(np.abs(exact_negative)))
             if exact_negative.size else 0.0
         ),
         numerical_tolerance_n_eps_lmax=numerical_tolerance,
         significant_negative_count=int(np.count_nonzero(
             eigenvalues < -numerical_tolerance
         )),
         numerical_null_count=int(np.count_nonzero(
             abs_eigenvalues <= numerical_tolerance
         )),
         effective_positive_rank=int(effective_positive.size),
         raw_floating_point_condition_2norm=raw_condition,
         numerical_condition_2norm=(
             "infinity" if np.any(
                 abs_eigenvalues <= numerical_tolerance
             ) else raw_condition
         ),
         effective_nonnull_condition=effective_condition,
         quantiles={
             str(q): float(np.quantile(eigenvalues, q))
             for q in (0, 0.001, 0.01, 0.1, 0.5,
                       0.9, 0.99, 0.999, 1)
         })

    emit("REDUNDANT_TRACE",
         route_A="sum of stored diagonal",
         route_B="sum of full eigenspectrum",
         route_A_value=trace_diagonal,
         route_B_value=trace_spectrum,
         absolute_difference=abs(trace_diagonal - trace_spectrum),
         relative_difference=(
             abs(trace_diagonal - trace_spectrum) /
             abs(trace_diagonal)
         ))

    emit("REDUNDANT_FROBENIUS",
         route_A="sqrt(sum of squares of every symmetrized matrix entry)",
         route_B="sqrt(sum of squared full-spectrum eigenvalues)",
         route_A_value=frobenius_entries,
         route_B_value=frobenius_spectrum,
         absolute_difference=abs(
             frobenius_entries - frobenius_spectrum
         ),
         relative_difference=(
             abs(frobenius_entries - frobenius_spectrum) /
             frobenius_entries
         ))
    del symmetric
    finish_stage(4, "full_eigenspectrum_and_redundant_invariants")

    stage(5, "scale_and_order_sanity")
    x_reported = x5[reported_indices]
    sigma = np.sqrt(np.maximum(diagonal, 0.0))
    relative_uncertainty = sigma / x_reported
    log_scale_correlation = float(np.corrcoef(
        np.log10(sigma), np.log10(x_reported)
    )[0, 1])

    volume_reported = volume[reported_indices]
    total_variance = float(
        volume_reported @ (total @ volume_reported)
    )
    total_sigma = math.sqrt(max(total_variance, 0.0))

    emit("SCALE_SANITY",
         central_reported_quantiles=quantiles(x_reported),
         sigma_quantiles=quantiles(sigma),
         relative_uncertainty_quantiles=quantiles(
             relative_uncertainty
         ),
         relative_uncertainty_count_gt_1=int(np.count_nonzero(
             relative_uncertainty > 1.0
         )),
         relative_uncertainty_count_gt_2=int(np.count_nonzero(
             relative_uncertainty > 2.0
         )),
         log10_sigma_vs_log10_central_correlation=
             log_scale_correlation,
         central_physical_total=total_reported,
         total_variance=total_variance,
         total_sigma=total_sigma,
         total_relative_uncertainty=total_sigma / total_reported)
    finish_stage(5, "scale_and_order_sanity")

    stage(6, "derive_component_inventory_and_reconstruct_systematics")
    retained_keys = sorted(
        name for name in candidate_names
        if name.startswith("hCov_retained5d_")
    )
    active_keys = sorted(
        name for name in candidate_names
        if name.startswith("hCov_active5d_")
        and name != KEYS["active_total"]
    )

    emit("COMPONENT_COUNTS_DERIVED",
         retained_count=len(retained_keys),
         active_component_count=len(active_keys),
         retained_keys=retained_keys,
         active_component_keys=active_keys,
         claimed_retained_count=40,
         claimed_active_component_count=5,
         retained_claim_holds=(len(retained_keys) == 40),
         active_claim_holds=(len(active_keys) == 5))

    if len(retained_keys) != 40 or len(active_keys) != 5:
        raise RuntimeError("candidate component census differs from claim")

    retained_sum = np.zeros_like(total)
    retained_trace_sum = 0.0
    for number, key in enumerate(retained_keys, start=1):
        component = load_th2(
            INPUTS["candidate"]["path"], key,
            f"retained_component_{number:02d}"
        )
        summary = matrix_basic(key, component)
        retained_sum += component
        retained_trace_sum += summary["trace"]
        emit("COMPONENT_ACCUMULATION_PROGRESS",
             family="retained", completed=number,
             expected=len(retained_keys), key=key,
             running_trace_sum=retained_trace_sum)
        del component

    active_sum = np.zeros_like(total)
    active_trace_sum = 0.0
    for number, key in enumerate(active_keys, start=1):
        component = load_th2(
            INPUTS["candidate"]["path"], key,
            f"active_component_{number:02d}"
        )
        summary = matrix_basic(key, component)
        active_sum += component
        active_trace_sum += summary["trace"]
        emit("COMPONENT_ACCUMULATION_PROGRESS",
             family="active", completed=number,
             expected=len(active_keys), key=key,
             running_trace_sum=active_trace_sum)
        del component

    active_stored = load_th2(
        INPUTS["candidate"]["path"], KEYS["active_total"],
        "active_total_stored"
    )
    active_stored_summary = matrix_basic(
        KEYS["active_total"], active_stored
    )
    compare_matrix_sum(
        "active_total_equals_sum_of_five_active_components",
        active_stored, [active_sum]
    )

    syst_stored = load_th2(
        INPUTS["candidate"]["path"], KEYS["syst"],
        "systematic_total_stored"
    )
    syst_stored_summary = matrix_basic(KEYS["syst"], syst_stored)

    compare_matrix_sum(
        "systematic_total_equals_retained_sum_plus_active_sum",
        syst_stored, [retained_sum, active_sum]
    )
    compare_matrix_sum(
        "systematic_total_equals_retained_sum_plus_stored_active_total",
        syst_stored, [retained_sum, active_stored]
    )

    emit("REDUNDANT_SYSTEMATIC_TRACE",
         retained_component_trace_sum=retained_trace_sum,
         active_component_trace_sum=active_trace_sum,
         active_stored_trace=active_stored_summary["trace"],
         systematic_stored_trace=syst_stored_summary["trace"],
         components_trace_total=(
             retained_trace_sum + active_trace_sum
         ),
         stored_minus_components_trace=(
             syst_stored_summary["trace"] -
             retained_trace_sum - active_trace_sum
         ))

    del retained_sum, active_sum, active_stored
    finish_stage(
        6, "derive_component_inventory_and_reconstruct_systematics"
    )

    stage(7, "reconstruct_full_total_from_syst_stat_ml")
    inventory_root("stat", INPUTS["stat"]["path"])
    inventory_root("ml", INPUTS["ml"]["path"])

    stat_cov = load_th2(
        INPUTS["stat"]["path"], KEYS["stat"], "stat_covariance"
    )
    ml_cov = load_th2(
        INPUTS["ml"]["path"], KEYS["ml"], "ml_covariance"
    )
    stat_summary = matrix_basic(KEYS["stat"], stat_cov)
    ml_summary = matrix_basic(KEYS["ml"], ml_cov)

    full_identity = compare_matrix_sum(
        "full_total_equals_systematic_plus_stat_plus_ml",
        total, [syst_stored, stat_cov, ml_cov]
    )

    emit("REDUNDANT_FULL_TRACE",
         total_trace=float(np.trace(total)),
         systematic_trace=float(np.trace(syst_stored)),
         stat_trace=stat_summary["trace"],
         ml_trace=ml_summary["trace"],
         component_trace_sum=(
             float(np.trace(syst_stored)) +
             stat_summary["trace"] +
             ml_summary["trace"]
         ),
         total_minus_component_trace=(
             float(np.trace(total)) -
             float(np.trace(syst_stored)) -
             stat_summary["trace"] -
             ml_summary["trace"]
         ),
         exact_matrix_identity_nonzero_count=
             full_identity["nonzero_difference_count"])
    finish_stage(7, "reconstruct_full_total_from_syst_stat_ml")

    stage(8, "completion_receipt")
    emit("SUMMARY_INGREDIENTS",
         script_id=SCRIPT_ID,
         completed_stages=list(COMPLETED_STAGES),
         derived_grid_shape=list(grid_shape),
         derived_full_bin_count=full_bin_count,
         derived_reported_count=int(reported_indices.size),
         mask_fingerprint=mask_fingerprint,
         covariance_shape=list(total.shape),
         covariance_content_sha256=array_sha256(total),
         covariance_trace=float(np.trace(total)),
         eigenvalue_sum=float(np.sum(eigenvalues)),
         eigenvalue_min=float(eigenvalues[0]),
         eigenvalue_max=float(eigenvalues[-1]),
         physical_central_total=total_reported,
         physical_total_relative_uncertainty=
             total_sigma / total_reported)
    finish_stage(8, "completion_receipt")

    emit("END", status="COMPLETE", script_id=SCRIPT_ID,
         completed_stage_count=len(COMPLETED_STAGES),
         completed_stages=list(COMPLETED_STAGES),
         required_begin_seen=True,
         required_end_seen=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        emit("END", status="ABORTED", script_id=SCRIPT_ID,
             failed_stage=CURRENT_STAGE,
             completed_stages=list(COMPLETED_STAGES),
             exception_type=type(exc).__name__,
             exception_message=str(exc),
             required_end_seen=True)
        traceback.print_exc()
        raise
