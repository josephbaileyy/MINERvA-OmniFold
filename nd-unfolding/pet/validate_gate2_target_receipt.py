#!/usr/bin/env python3
"""Independent, read-only Gate-2 runtime-product validator.

This deliberately does not import the construction loader or runtime validator.
It recomputes file/configuration hashes, signed-target identity, weight invariants,
and the extended-grid binned telemetry directly from the frozen NPZ and products.
"""

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np


PT_EDGES = np.array(
    [0, .07, .15, .25, .33, .4, .47, .55, .7, .85, 1., 1.25, 1.5, 2.5, 4.5, 30.],
    dtype=np.float64,
)
PPAR_EDGES = np.array(
    [0, .75, 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5., 6., 7., 8., 9., 10., 15., 20., 40., 60., 120.],
    dtype=np.float64,
)
EXPECTED_CONFIG = {
    "target_mode": "negweight-refined",
    "estimator": "exact",
    "device": "cpu",
    "features": ["pt", "pparallel"],
    "master_seed": 42,
    "refinement_random_state": 45,
    "bootstrap_seed": None,
    "max_mc_events": 200000,
    "full_measured_inventory": True,
    "normalization_factor": 1_000_000.0,
    "dataloader_import_mode": "target-only exact NumPy source; no TensorFlow/PET training",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def inventory_hash(array) -> str:
    value = np.ascontiguousarray(np.asarray(array))
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode())
    digest.update(repr(value.shape).encode())
    digest.update(value.tobytes())
    return digest.hexdigest()


def close(a, b, *, rtol=2e-11, atol=1e-5) -> bool:
    return bool(np.isclose(float(a), float(b), rtol=rtol, atol=atol))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    receipt = json.loads(args.receipt.read_text())
    failures = []
    require = lambda condition, message: failures.append(message) if not condition else None

    require(receipt.get("status") == "PASS", "runtime receipt is not PASS")
    require(receipt.get("pet_training_started") is False, "runtime claims PET training started")
    require(receipt.get("configuration") == EXPECTED_CONFIG, "configuration differs from locked exact nominal")
    config_sha = sha256_json(receipt.get("configuration"))
    require(config_sha == receipt.get("configuration_sha256"), "configuration hash mismatch")

    actual_hashes = {
        "input": sha256_file(args.input),
        "weights": sha256_file(args.weights),
    }
    require(actual_hashes["input"] == receipt["input_preflight"]["sha256"], "frozen input hash mismatch")
    require(args.input.stat().st_size == receipt["input_preflight"]["size_bytes"], "frozen input size mismatch")
    require(actual_hashes["weights"] == receipt["step1_feed"]["weights"]["sha256"], "weights hash mismatch")
    require(args.weights.stat().st_size == receipt["step1_feed"]["weights"]["size_bytes"], "weights size mismatch")
    for label, record in receipt["code"].items():
        path = Path(record["path"])
        actual_hashes[label] = sha256_file(path)
        require(actual_hashes[label] == record["sha256"], f"{label} code hash mismatch")

    weights = np.load(args.weights, allow_pickle=False)
    require(weights.dtype == np.float32, "published weights dtype is not float32")
    require(weights.shape == (4_680_719,), "published weights row count mismatch")
    require(bool(np.all(np.isfinite(weights))), "published weights contain non-finite values")
    require(not bool(np.any(weights < 0)), "published weights contain negative values")
    require(int(np.count_nonzero(weights == 0)) == 20, "published zero-weight count mismatch")
    normalized_sum = float(weights.sum(dtype=np.float64))
    require(close(normalized_sum, 1_000_000.0, rtol=3e-6, atol=2.0), "published weights not normalized")

    with np.load(args.input, allow_pickle=True) as source:
        measured = np.asarray(source["measured_scalars"], dtype=np.float64)[:, :2] / 1000.0
        background = np.asarray(source["bkg_reco_scalars"], dtype=np.float64)[:, :2] / 1000.0
        w_bkg = np.asarray(source["w_bkg"], dtype=np.float64)
        pot_scale = float(np.asarray(source["pot_scale"]).item())
    require(measured.shape == (4_116_128, 2), "data scalar inventory mismatch")
    require(background.shape == (564_591, 2), "background scalar inventory mismatch")
    require(w_bkg.shape == (564_591,), "background weight inventory mismatch")

    signed = np.concatenate([np.ones(measured.shape[0]), -(w_bkg * pot_scale)])
    signed_hash = inventory_hash(signed)
    require(signed_hash == receipt["runtime_target"]["signed_target_hash"], "signed-target order/hash mismatch")
    require(close(np.abs(signed[signed < 0]).sum(), receipt["runtime_target"]["raw_negative_sum"]), "raw negative sum mismatch")

    data_hist = np.histogram2d(measured[:, 0], measured[:, 1], bins=(PT_EDGES, PPAR_EDGES))[0]
    bkg_hist = np.histogram2d(
        background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=w_bkg * pot_scale
    )[0]
    refined_hist = np.histogram2d(
        measured[:, 0], measured[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=weights[: measured.shape[0]]
    )[0]
    refined_hist += np.histogram2d(
        background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=weights[measured.shape[0] :]
    )[0]
    signed_hist = data_hist - bkg_hist
    clipped = np.clip(signed_hist, 0.0, None)
    clipped_norm = clipped * (1_000_000.0 / clipped.sum())
    occupied = (clipped_norm > 0) | (refined_hist > 0)
    denom = np.maximum(clipped_norm, 1e-12)
    telemetry = {
        "grid_shape": list(signed_hist.shape),
        "data_rows_in_grid": int(data_hist.sum()),
        "background_rows_in_grid": int(np.histogram2d(background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES))[0].sum()),
        "raw_data_sum": float(data_hist.sum()),
        "raw_background_pot_scaled_sum": float(bkg_hist.sum()),
        "raw_signed_sum": float(signed_hist.sum()),
        "negative_signed_cells": int(np.count_nonzero(signed_hist < 0)),
        "closed_form_clipped_sum": float(clipped.sum()),
        "learned_refined_normalized_sum": float(refined_hist.sum()),
        "learned_vs_normalized_clipped_l1_fraction": float(np.abs(refined_hist - clipped_norm).sum() / 1_000_000.0),
        "learned_vs_normalized_clipped_max_relative": float(np.max(np.abs(refined_hist[occupied] - clipped_norm[occupied]) / denom[occupied])),
        "learned_vs_normalized_clipped_cosine": float(np.vdot(refined_hist.ravel(), clipped_norm.ravel()) / (np.linalg.norm(refined_hist) * np.linalg.norm(clipped_norm))),
    }
    recorded = receipt["independent_binned_checks"]
    key_map = {"data_rows_in_grid": "in_domain_data_rows", "background_rows_in_grid": "in_domain_background_rows"}
    for key, value in telemetry.items():
        recorded_key = key_map.get(key, key)
        if isinstance(value, list):
            require(value == recorded[recorded_key], f"binned telemetry mismatch: {key}")
        else:
            require(close(value, recorded[recorded_key], rtol=5e-12, atol=1e-6), f"binned telemetry mismatch: {key}")
    require(telemetry["data_rows_in_grid"] == measured.shape[0], "data outside extended grid")
    require(telemetry["background_rows_in_grid"] == background.shape[0], "background outside extended grid")
    require(telemetry["negative_signed_cells"] == 0, "negative signed extended-grid cells")
    require(close(telemetry["learned_refined_normalized_sum"], normalized_sum), "binned/unbinned normalized sums differ")
    require(receipt["runtime_target"].get("refinement_backend") == "u2d.refine_stay_positive", "noncanonical refinement backend")
    require(receipt["runtime_target"].get("refinement_is_learned_production") is True, "learned production refinement not proven")

    result = {
        "schema_version": 1,
        "validation_schema": "g2-gate2-runtime-independent-v1",
        "validated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS" if not failures else "BLOCK",
        "failures": failures,
        "runtime_receipt": {"path": str(args.receipt.resolve()), "sha256": sha256_file(args.receipt)},
        "artifact_hashes": actual_hashes,
        "configuration_sha256": config_sha,
        "signed_target_hash": signed_hash,
        "weights": {
            "dtype": str(weights.dtype), "rows": int(weights.size), "sum": normalized_sum,
            "min": float(weights.min()), "max": float(weights.max()),
            "zero_rows": int(np.count_nonzero(weights == 0)),
        },
        "runtime_target": {
            "mode": receipt["runtime_target"]["target_mode"],
            "backend": receipt["runtime_target"]["refinement_backend"],
            "learned_production": receipt["runtime_target"]["refinement_is_learned_production"],
            "data_rows": receipt["runtime_target"]["n_data_rows"],
            "background_rows": receipt["runtime_target"]["n_bkg_rows"],
            "floored_zero": receipt["runtime_target"]["n_floored_zero"],
        },
        "binned_telemetry": telemetry,
        "pet_training_started": False,
        "verdict": "GATE2_RUNTIME_INDEPENDENT_PASS" if not failures else "GATE2_RUNTIME_INDEPENDENT_BLOCK",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
