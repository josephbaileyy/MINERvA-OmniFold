#!/usr/bin/env python3
"""Runtime benchmark and fail-closed validator for the G2 negweight target.

This is deliberately target-only: it executes the canonical learned
``u2d.refine_stay_positive`` construction on the complete data+background
inventory, but it does not start PET training or advance another remediation
gate.  ``benchmark`` writes only to a run-ID-specific namespace. ``validate``
writes a normalized step-1 target plus a hash-bound receipt to caller-supplied
staging paths; publication is owned by ``run_gate2_target_validator.sh``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import resource
import socket
import struct
import subprocess
import sys
import time
import types
import zipfile

import numpy as np


REPO = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold")
EXPECTED_SCHEMA = {
    "petSchemaVersion": "g2-fullevent-v1",
    "hasFullEventSchema": 1,
    "fullPhaseSpace": 1,
}
EXPECTED_ROWS = {"signal": 49_152_885, "data": 4_116_128, "background": 564_591}
EXPECTED_NPZ_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_NPZ_SIZE = 9_897_374_636
EXPECTED_IDENTITY = {
    "sig": "5ade9c49a026cfa619ba71870087990fbbddc5dcad4c95f0f459c3c893783af1",
    "data": "fd2b14c6f3dbbd7c8747edfd36fcf24c35f29a629350cac84e07027d398e3fc7",
    "bkg": "d79848885f177259e5934c70ddcfc1bb3dea39272da0e67759a5d1b596ca024b",
}
FEATURE_NAMES = ("pt", "pparallel")
MASTER_SEED = 42
REFINEMENT_SEED = MASTER_SEED + 3
NORMALIZATION = 1_000_000.0


def die(message: str) -> None:
    raise RuntimeError(message)


def sha256_file(path: Path, block: int = 16 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(block)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_json(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def write_json_fsync(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_symlink() or not path.is_file() or path.stat().st_size != 0:
            die(f"refuse nonempty/non-regular JSON staging path: {path}")
        mode = "w"
    else:
        mode = "x"
    with path.open(mode) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_npy_fsync(path: Path, value: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_symlink() or not path.is_file() or path.stat().st_size != 0:
            die(f"refuse nonempty/non-regular NPY staging path: {path}")
        mode = "wb"
    else:
        mode = "xb"
    with path.open(mode) as handle:
        np.save(handle, value, allow_pickle=False)
        handle.flush()
        os.fsync(handle.fileno())


def require_available_staging(path: Path) -> None:
    """Accept an absent path or an empty regular mktemp file; reject all else."""
    if not path.exists():
        if path.is_symlink():
            die(f"refuse dangling-symlink staging path: {path}")
        return
    if path.is_symlink() or not path.is_file() or path.stat().st_size != 0:
        die(f"refuse occupied/non-regular validator staging path: {path}")


def _npy_header(zf: zipfile.ZipFile, member: str):
    with zf.open(member + ".npy") as handle:
        version = np.lib.format.read_magic(handle)
        shape, fortran, dtype = np.lib.format._read_array_header(handle, version)
    return {"shape": list(shape), "dtype": str(dtype), "fortran_order": bool(fortran)}


def _npy_scalar(zf: zipfile.ZipFile, member: str):
    with zf.open(member + ".npy") as handle:
        return np.lib.format.read_array(handle, allow_pickle=True).item()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def full_input_preflight(inputs: Path, producer_receipt: Path, independent_receipt: Path):
    started = time.monotonic()
    if not inputs.is_file() or inputs.is_symlink():
        die(f"input is missing/not a regular file or is a symlink: {inputs}")
    size = inputs.stat().st_size
    if size != EXPECTED_NPZ_SIZE:
        die(f"input size {size} != frozen {EXPECTED_NPZ_SIZE}")
    digest = sha256_file(inputs)
    if digest != EXPECTED_NPZ_SHA256:
        die(f"input sha256 {digest} != frozen {EXPECTED_NPZ_SHA256}")

    producer = json.loads(producer_receipt.read_text())
    independent = json.loads(independent_receipt.read_text())
    if producer.get("status") != "PASS" or independent.get("status") != "PASS":
        die("Gate-1 producer/independent receipt is not PASS")
    for label, record in (("producer", producer), ("independent", independent)):
        npz = record.get("npz", {})
        if npz.get("sha256") != digest or int(npz.get("size_bytes", -1)) != size:
            die(f"{label} receipt does not bind the frozen input")

    with zipfile.ZipFile(inputs) as zf:
        keys = sorted(x[:-4] for x in zf.namelist() if x.endswith(".npy"))
        headers = {k: _npy_header(zf, k) for k in keys}
        markers = {k: _npy_scalar(zf, k) for k in EXPECTED_SCHEMA}
    for key, expected in EXPECTED_SCHEMA.items():
        got = markers.get(key)
        if str(got) != str(expected):
            die(f"schema marker {key}={got!r} != {expected!r}")
    rows = {
        "signal": int(headers["part_gen"]["shape"][0]),
        "data": int(headers["measured_pc"]["shape"][0]),
        "background": int(headers["bkg_part_reco"]["shape"][0]),
    }
    if rows != EXPECTED_ROWS:
        die(f"inventory rows {rows} != frozen {EXPECTED_ROWS}")
    return {
        "path": str(inputs),
        "sha256": digest,
        "size_bytes": size,
        "member_count": len(headers),
        "schema_markers": markers,
        "inventory_rows": rows,
        "producer_receipt": {
            "path": str(producer_receipt), "sha256": sha256_file(producer_receipt)
        },
        "independent_receipt": {
            "path": str(independent_receipt), "sha256": sha256_file(independent_receipt)
        },
        "elapsed_seconds": time.monotonic() - started,
    }


def load_refiner():
    for value in (REPO / "2d-unfolding", REPO / "nd-unfolding"):
        if str(value) not in sys.path:
            sys.path.insert(0, str(value))
    from unfold_2d_omnifold_unbinned import refine_stay_positive

    return refine_stay_positive


def install_target_only_dataloader():
    """Load the exact NumPy DataLoader source without importing PET/TensorFlow.

    ``omnifold.dataloader`` itself depends only on NumPy, but normal package
    import first executes ``omnifold/__init__.py`` and imports the TensorFlow
    training engine. Gate 2 is a target-construction/interface gate, not PET
    training, so bind only the exact committed DataLoader module under its
    canonical name. The later ``from omnifold.dataloader import DataLoader``
    in the production loader then consumes this source byte-for-byte.
    """
    name = "omnifold.dataloader"
    if name in sys.modules:
        return sys.modules[name]
    source = REPO / "omnifold_nn/omnifold/dataloader.py"
    if not source.is_file() or source.is_symlink():
        die(f"canonical NumPy DataLoader source missing/invalid: {source}")
    parent = sys.modules.get("omnifold")
    if parent is None:
        parent = types.ModuleType("omnifold")
        parent.__package__ = "omnifold"
        parent.__path__ = [str(source.parent)]
        sys.modules["omnifold"] = parent
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        die(f"cannot construct import spec for {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    setattr(parent, "dataloader", module)
    if Path(module.__file__).resolve() != source.resolve() or not hasattr(module, "DataLoader"):
        die("target-only DataLoader did not bind the canonical source/class")
    return module


def run_benchmark(args) -> int:
    inputs = Path(args.inputs).resolve()
    output = Path(args.output).resolve()
    preflight = full_input_preflight(
        inputs, Path(args.producer_receipt).resolve(), Path(args.independent_receipt).resolve()
    )
    if output.exists() or output.is_symlink():
        die(f"refuse occupied benchmark output: {output}")

    with np.load(inputs, allow_pickle=True) as data:
        measured = np.asarray(data["measured_scalars"], dtype=np.float64)[:, :2]
        background = np.asarray(data["bkg_reco_scalars"], dtype=np.float64)[:, :2]
        w_bkg = np.asarray(data["w_bkg"], dtype=np.float64)
        if "pot_scale" in data.files:
            pot_scale = float(np.asarray(data["pot_scale"]).item())
        else:
            pot_scale = float(np.asarray(data["data_pot"]).item()) / float(
                np.asarray(data["mc_pot"]).item()
            )

    n_full = measured.shape[0] + background.shape[0]
    n_sample = min(int(args.sample_rows), n_full)
    n_data = max(1, round(n_sample * measured.shape[0] / n_full))
    n_bkg = max(1, n_sample - n_data)
    rng = np.random.default_rng(int(args.sample_seed))
    idx_data = np.sort(rng.choice(measured.shape[0], n_data, replace=False))
    idx_bkg = np.sort(rng.choice(background.shape[0], n_bkg, replace=False))
    feat = np.vstack((measured[idx_data], background[idx_bkg]))
    signed = np.concatenate(
        (
            np.full(n_data, measured.shape[0] / n_data, dtype=np.float64),
            -w_bkg[idx_bkg] * pot_scale * (background.shape[0] / n_bkg),
        )
    )
    del measured, background, w_bkg

    import_started = time.monotonic()
    refiner = load_refiner()
    import_seconds = time.monotonic() - import_started
    fit_started = time.monotonic()
    w_ref, g, frac_clip = refiner(
        feat,
        signed,
        estimator="exact",
        device="cpu",
        params={"random_state": REFINEMENT_SEED},
        verbose=True,
    )
    fit_seconds = time.monotonic() - fit_started
    if w_ref.shape != signed.shape or not np.all(np.isfinite(w_ref)) or np.any(w_ref < 0):
        die("benchmark refinement violated finite/non-negative/alignment gate")

    ratio = n_full / n_sample
    # Exact sklearn GBDT cost is approximately N log N for fixed trees/features.
    scale = ratio * (math.log2(max(n_full, 2)) / math.log2(max(n_sample, 2)))
    projected = fit_seconds * scale
    fixed_overhead = 1800.0
    safety_factor = float(args.safety_factor)
    projected_safe = projected * safety_factor + fixed_overhead
    result = {
        "schema_version": 1,
        "status": "PASS",
        "mode": "benchmark-only-no-final-writer",
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "head": git_head(),
        "input_preflight": preflight,
        "configuration": {
            "estimator": "exact",
            "device": "cpu",
            "features": list(FEATURE_NAMES),
            "master_seed": MASTER_SEED,
            "refinement_random_state": REFINEMENT_SEED,
            "sample_seed": int(args.sample_seed),
            "sample_rows": n_sample,
            "sample_data_rows": n_data,
            "sample_background_rows": n_bkg,
            "full_refinement_rows": n_full,
            "class_weight_rescaling": "inverse sampling fraction per inventory",
        },
        "timing": {
            "refiner_import_seconds": import_seconds,
            "sample_fit_predict_seconds": fit_seconds,
            "projection_scale_nlogn": scale,
            "projected_full_seconds_central": projected,
            "projection_safety_factor": safety_factor,
            "fixed_full_loader_overhead_seconds": fixed_overhead,
            "projected_full_seconds_safe": projected_safe,
        },
        "sample_telemetry": {
            "raw_positive_sum": float(signed[signed > 0].sum()),
            "raw_negative_abs_sum": float(np.abs(signed[signed < 0]).sum()),
            "refined_sum": float(w_ref.sum()),
            "refined_min": float(w_ref.min()),
            "refined_max": float(w_ref.max()),
            "g_min": float(g.min()),
            "g_max": float(g.max()),
            "frac_clipped": float(frac_clip),
        },
        "max_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    }
    result["configuration_sha256"] = sha256_json(result["configuration"])
    write_json_fsync(output, result)
    print(json.dumps({"status": "PASS", "output": str(output), **result["timing"]}, sort_keys=True))
    return 0


def _hist2(values, edges_pt, edges_ppar, weights=None):
    return np.histogram2d(values[:, 0], values[:, 1], bins=(edges_pt, edges_ppar), weights=weights)[0]


def run_validate(args) -> int:
    inputs = Path(args.inputs).resolve()
    output = Path(args.output).resolve()
    weights_output = Path(args.weights_output).resolve()
    require_available_staging(output)
    require_available_staging(weights_output)
    start_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    overall_started = time.monotonic()
    preflight = full_input_preflight(
        inputs, Path(args.producer_receipt).resolve(), Path(args.independent_receipt).resolve()
    )

    for value in (REPO / "2d-unfolding", REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
        if str(value) not in sys.path:
            sys.path.insert(0, str(value))
    import fullevent_fps_dataloader as fed
    dataloader_module = install_target_only_dataloader()

    config = {
        "target_mode": "negweight-refined",
        "estimator": "exact",
        "device": "cpu",
        "features": list(FEATURE_NAMES),
        "master_seed": MASTER_SEED,
        "refinement_random_state": REFINEMENT_SEED,
        "bootstrap_seed": None,
        "max_mc_events": int(args.max_mc_events),
        "full_measured_inventory": True,
        "normalization_factor": NORMALIZATION,
        "dataloader_import_mode": "target-only exact NumPy source; no TensorFlow/PET training",
    }
    build_started = time.monotonic()
    data, mc, imc, coord_reco, coord_gen, meta = fed.build_fullevent_loaders(
        str(inputs),
        max_events=int(args.max_mc_events),
        seed=MASTER_SEED,
        bootstrap_seed=None,
        feature_names=FEATURE_NAMES,
        enforce_fps_edges=True,
        bkg_mode="negweight-refined",
        refine_fn=None,
        refine_kwargs={
            "estimator": "exact",
            "device": "cpu",
            "params": {"random_state": REFINEMENT_SEED},
            "verbose": True,
        },
        verify_identities=True,
    )
    build_seconds = time.monotonic() - build_started
    target = dict(meta.get("target") or {})
    if target.get("target_mode") != "negweight-refined":
        die("runtime target mode is not negweight-refined")
    if not target.get("refinement_is_learned_production"):
        die("runtime did not use the canonical deferred production refiner")
    if target.get("refinement_backend") != "u2d.refine_stay_positive":
        die(f"unexpected refinement backend {target.get('refinement_backend')!r}")
    if target.get("input_identity_hashes") != EXPECTED_IDENTITY:
        die(f"runtime identity hashes differ from Gate-1 evidence: {target.get('input_identity_hashes')}")

    weights = np.asarray(data.weight, dtype=np.float32)
    expected_measured = EXPECTED_ROWS["data"] + EXPECTED_ROWS["background"]
    if weights.shape != (expected_measured,):
        die(f"step-1 target rows {weights.shape} != {(expected_measured,)}")
    if not np.all(np.isfinite(weights)) or np.any(weights < 0):
        die("normalized step-1 target is non-finite or negative")
    if not np.isclose(float(weights.sum(dtype=np.float64)), NORMALIZATION, rtol=3e-6, atol=2.0):
        die(f"normalized step-1 sum {weights.sum(dtype=np.float64)} != {NORMALIZATION}")
    if data.reco.shape[0] != expected_measured or data.reco_evt.shape[0] != expected_measured:
        die("step-1 DataLoader cloud/event-feature target is not row-aligned")
    if mc.reco.shape[0] != int(args.max_mc_events) or mc.gen.shape[0] != int(args.max_mc_events):
        die("bounded MC loader did not consume the requested validation subset")

    # Independent binned checks use raw input scalars and the normalized weights
    # actually carried by the step-1 DataLoader; they do not call the refiner.
    with np.load(inputs, allow_pickle=True) as source:
        measured = np.asarray(source["measured_scalars"], dtype=np.float64)[:, :2] / 1000.0
        background = np.asarray(source["bkg_reco_scalars"], dtype=np.float64)[:, :2] / 1000.0
        w_bkg = np.asarray(source["w_bkg"], dtype=np.float64)
    edges_pt = np.asarray(fed.CANONICAL_PT_EDGES, dtype=np.float64)
    edges_ppar = np.asarray(fed.CANONICAL_PPARALLEL_EDGES, dtype=np.float64)
    data_hist = _hist2(measured, edges_pt, edges_ppar)
    bkg_hist = _hist2(background, edges_pt, edges_ppar, w_bkg * float(target["pot_scale"]))
    signed_hist = data_hist - bkg_hist
    clipped_hist = np.clip(signed_hist, 0.0, None)
    refined_hist = _hist2(measured, edges_pt, edges_ppar, weights[: measured.shape[0]])
    refined_hist += _hist2(background, edges_pt, edges_ppar, weights[measured.shape[0] :])
    in_domain_data = int(_hist2(measured, edges_pt, edges_ppar).sum())
    in_domain_bkg = int(_hist2(background, edges_pt, edges_ppar).sum())
    if in_domain_data != measured.shape[0] or in_domain_bkg != background.shape[0]:
        die("retained measured/background inventory is outside the canonical FPS grid")
    raw_signed_sum = float(signed_hist.sum())
    target_raw_signed = float(target["raw_positive_sum"]) - float(target["raw_negative_sum"])
    if not np.isclose(raw_signed_sum, target_raw_signed, rtol=2e-11, atol=1e-5):
        die("independent signed binned sum does not reproduce runtime construction telemetry")
    if not np.all(np.isfinite(refined_hist)) or np.any(refined_hist < 0):
        die("independent refined binned projection is non-finite or negative")
    if not np.isclose(float(refined_hist.sum()), NORMALIZATION, rtol=3e-6, atol=2.0):
        die("independent refined binned projection does not reproduce DataLoader normalization")

    clipped_norm = clipped_hist * (NORMALIZATION / clipped_hist.sum())
    denom = np.maximum(clipped_norm, 1e-12)
    occupied = (clipped_norm > 0) | (refined_hist > 0)
    rel_l1 = float(np.abs(refined_hist - clipped_norm).sum() / NORMALIZATION)
    max_rel = float(np.max(np.abs(refined_hist[occupied] - clipped_norm[occupied]) / denom[occupied]))
    cosine = float(
        np.vdot(refined_hist.ravel(), clipped_norm.ravel())
        / (np.linalg.norm(refined_hist) * np.linalg.norm(clipped_norm))
    )

    write_npy_fsync(weights_output, weights)
    weights_sha = sha256_file(weights_output)
    loader_path = Path(fed.__file__).resolve()
    dataloader_path = Path(dataloader_module.__file__).resolve()
    u2d_path = REPO / "2d-unfolding/unfold_2d_omnifold_unbinned.py"
    script_path = Path(__file__).resolve()
    end_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": "GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING",
        "pet_training_started": False,
        "started_at_utc": start_utc,
        "completed_at_utc": end_utc,
        "execution": {
            "route": args.execution_route,
            "run_id": args.run_id,
            "slurm_job_id": args.slurm_job_id,
            "host": socket.gethostname(),
            "head_at_runtime": git_head(),
            "command": "gate2_target_runtime.py validate (canonical exact target-only gate)",
        },
        "input_preflight": preflight,
        "configuration": config,
        "configuration_sha256": sha256_json(config),
        "code": {
            "validator": {"path": str(script_path), "sha256": sha256_file(script_path)},
            "loader": {"path": str(loader_path), "sha256": sha256_file(loader_path)},
            "numpy_dataloader": {
                "path": str(dataloader_path), "sha256": sha256_file(dataloader_path)
            },
            "canonical_u2d": {"path": str(u2d_path), "sha256": sha256_file(u2d_path)},
        },
        "runtime_target": target,
        "step1_feed": {
            "rows": int(weights.size),
            "cloud_shape": list(data.reco.shape),
            "event_feature_shape": list(data.reco_evt.shape),
            "normalized_sum": float(weights.sum(dtype=np.float64)),
            "min": float(weights.min()),
            "max": float(weights.max()),
            "zero_rows": int((weights == 0).sum()),
            "weights": {
                "published_path": args.published_weights_path,
                "staging_path": str(weights_output),
                "sha256": weights_sha,
                "size_bytes": weights_output.stat().st_size,
                "dtype": str(weights.dtype),
            },
            "bounded_mc_validation_rows": int(len(imc)),
            "mc_reco_shape": list(mc.reco.shape),
            "mc_gen_shape": list(mc.gen.shape),
            "coord_reco": list(coord_reco),
            "coord_gen": list(coord_gen),
        },
        "independent_binned_checks": {
            "grid_shape": list(signed_hist.shape),
            "in_domain_data_rows": in_domain_data,
            "in_domain_background_rows": in_domain_bkg,
            "raw_data_sum": float(data_hist.sum()),
            "raw_background_pot_scaled_sum": float(bkg_hist.sum()),
            "raw_signed_sum": raw_signed_sum,
            "negative_signed_cells": int((signed_hist < 0).sum()),
            "closed_form_clipped_sum": float(clipped_hist.sum()),
            "learned_refined_normalized_sum": float(refined_hist.sum()),
            "learned_vs_normalized_clipped_l1_fraction": rel_l1,
            "learned_vs_normalized_clipped_max_relative": max_rel,
            "learned_vs_normalized_clipped_cosine": cosine,
            "interpretation": (
                "signed totals and normalized refined projection are hard gates; learned-vs-binned "
                "shape metrics are decision telemetry, not an invented equality threshold"
            ),
        },
        "timing": {
            "loader_and_full_refinement_seconds": build_seconds,
            "total_seconds": time.monotonic() - overall_started,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sklearn": __import__("sklearn").__version__,
            "platform": platform.platform(),
            "tensorflow": "not imported/not required for target-only Gate-2 validation",
            "max_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        },
        "promotion_requirements": [
            "independent receipt review of hashes, exact configuration, and binned telemetry",
            "ledger + RUN_LOG + STATUS update committed with launcher and product summary",
        ],
    }
    write_json_fsync(output, receipt)
    print(
        json.dumps(
            {
                "status": "PASS",
                "verdict": receipt["verdict"],
                "receipt_staging": str(output),
                "weights_staging": str(weights_output),
                "weights_sha256": weights_sha,
                "runtime_seconds": receipt["timing"]["total_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--inputs", required=True)
    common.add_argument("--producer-receipt", required=True)
    common.add_argument("--independent-receipt", required=True)
    sub = parser.add_subparsers(dest="mode", required=True)

    benchmark = sub.add_parser("benchmark", parents=[common])
    benchmark.add_argument("--output", required=True)
    benchmark.add_argument("--sample-rows", type=int, default=250_000)
    benchmark.add_argument("--sample-seed", type=int, default=20260719)
    benchmark.add_argument("--safety-factor", type=float, default=2.0)
    benchmark.set_defaults(func=run_benchmark)

    validate = sub.add_parser("validate", parents=[common])
    validate.add_argument("--output", required=True)
    validate.add_argument("--weights-output", required=True)
    validate.add_argument("--published-weights-path", required=True)
    validate.add_argument("--execution-route", choices=("batch", "interactive"), required=True)
    validate.add_argument("--run-id", required=True)
    validate.add_argument("--slurm-job-id", default="none")
    validate.add_argument("--max-mc-events", type=int, default=200_000)
    validate.set_defaults(func=run_validate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[gate2-runtime][FAIL] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise
