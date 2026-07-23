#!/usr/bin/env python3
"""Bounded recoil-only PET2 engine pilot on the staged xps2 memmaps.

This deliberately does not upgrade xps2 into a full-event or publication
input. It uses the old recoil tensors to test runtime, extraction, ratios, and
tails while recording every missing contract leg.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from .artifacts import atomic_run_directory, save_iteration_result, write_json
from .contracts import (
    CanonicalDataset,
    MeasuredInventory,
    SignalInventory,
    TokenBatch,
)
from .density_ratio import RatioTrainingConfig
from .engine import OneIterationConfig, run_iterations
from .features import ArmManifest, TYPE_GENERIC
from .utils import array_hash, environment_receipt, fingerprint, seed_everything
from .xps2_adapter import _bounded_indices, open_xps2_memmap

RECO_GLOBAL_NAMES = ("no_event_globals_available",)


def _reco_batch(
    cloud: np.ndarray,
    *,
    valid_rows: np.ndarray,
    provenance: str,
) -> TokenBatch:
    cloud = np.asarray(cloud, dtype=np.float32)
    valid_rows = np.asarray(valid_rows, dtype=bool)
    if cloud.ndim != 3 or cloud.shape[2] != 3:
        raise ValueError("xps2 reco cloud must have shape (N,P,3)")
    if valid_rows.shape != (cloud.shape[0],):
        raise ValueError("xps2 reco valid_rows shape mismatch")
    if not np.all(np.isfinite(cloud)):
        raise ValueError("xps2 reco cloud contains NaN or infinity")
    # Historical xps2 has no explicit mask. Its producer zero-padded every
    # absent token, so this downgrade derives and then persists a bool mask.
    mask = np.any(cloud != 0.0, axis=2) & valid_rows[:, None]
    continuous = cloud / 1000.0
    continuous[~mask] = 0.0
    coords = continuous[:, :, 1:3].copy()
    type_id = np.where(mask, TYPE_GENERIC, 0).astype(np.int64)
    view_id = np.zeros(mask.shape, dtype=np.int64)
    return TokenBatch(
        continuous=continuous,
        coords=coords,
        token_mask=mask,
        type_id=type_id,
        view_id=view_id,
        globals=np.zeros((cloud.shape[0], 1), dtype=np.float32),
        row_index=np.arange(cloud.shape[0], dtype=np.int64),
        global_names=RECO_GLOBAL_NAMES,
        provenance=provenance,
    ).validated()


def _truth_batch(cloud: np.ndarray, valid_rows: np.ndarray) -> TokenBatch:
    cloud = np.asarray(cloud, dtype=np.float32)
    valid_rows = np.asarray(valid_rows, dtype=bool)
    if cloud.ndim != 3 or cloud.shape[2] != 5:
        raise ValueError("xps2 truth cloud must have shape (N,P,5)")
    if not np.all(np.isfinite(cloud)):
        raise ValueError("xps2 truth cloud contains NaN or infinity")
    energy = cloud[:, :, 0] / 1000.0
    px = cloud[:, :, 1] / 1000.0
    py = cloud[:, :, 2] / 1000.0
    pz = cloud[:, :, 3] / 1000.0
    pdg = cloud[:, :, 4]
    mask = (pdg != 0) & valid_rows[:, None]
    continuous = np.stack((energy, np.hypot(px, py), pz), axis=2).astype(
        np.float32
    )
    theta = np.arctan2(np.hypot(px, py), pz)
    phi = np.arctan2(py, px)
    coords = np.stack((theta, np.cos(phi), np.sin(phi)), axis=2).astype(
        np.float32
    )
    continuous[~mask] = 0.0
    coords[~mask] = 0.0
    return TokenBatch(
        continuous=continuous,
        coords=coords,
        token_mask=mask,
        type_id=np.where(mask, TYPE_GENERIC, 0).astype(np.int64),
        view_id=np.zeros(mask.shape, dtype=np.int64),
        globals=np.zeros((cloud.shape[0], 1), dtype=np.float32),
        row_index=np.arange(cloud.shape[0], dtype=np.int64),
        global_names=RECO_GLOBAL_NAMES,
        provenance="xps2_truth_bounded_recoil_pilot",
    ).validated()


def build_xps2_recoil_dataset(
    directory: str | Path,
    *,
    max_mc_rows: int,
    max_data_rows: int,
    seed: int,
) -> CanonicalDataset:
    inventory = open_xps2_memmap(
        directory, max_rows=max_mc_rows, seed=seed
    )
    root = inventory.directory
    measured_path = root / "measured_pc.npy"
    measured_weight_path = root / "measured_weights.npy"
    if not measured_path.is_file() or not measured_weight_path.is_file():
        raise FileNotFoundError("xps2 measured_pc/measured_weights memmaps are required")
    measured_pc = np.load(measured_path, mmap_mode="r", allow_pickle=False)
    measured_weights = np.load(
        measured_weight_path, mmap_mode="r", allow_pickle=False
    )
    if not isinstance(measured_pc, np.memmap) or not isinstance(
        measured_weights, np.memmap
    ):
        raise ValueError("xps2 measured arrays must open read-only as memmaps")
    if measured_pc.shape[0] != measured_weights.shape[0]:
        raise ValueError("xps2 measured arrays have different row counts")
    data_rows = _bounded_indices(
        int(measured_pc.shape[0]),
        min(int(max_data_rows), int(measured_pc.shape[0])),
        seed + 1,
    )
    packet = inventory.read_packet()
    pass_truth = np.asarray(packet["pass_truth"], dtype=bool)
    # The publication contract's signal inventory is truth-denominator
    # authoritative. Drop the tiny xps2 rows outside that old denominator
    # before constructing native misses; do not fabricate a fake policy.
    keep = pass_truth
    if not np.any(keep):
        raise ValueError("bounded xps2 packet has no truth-denominator rows")
    part_reco = np.asarray(packet["part_reco"][keep])
    part_gen = np.asarray(packet["part_gen"][keep])
    pass_reco = np.asarray(packet["pass_reco"][keep], dtype=bool)
    pass_truth = np.ones(int(keep.sum()), dtype=bool)
    w_truth = np.asarray(packet["w_truth"][keep], dtype=np.float64)
    data_cloud = np.asarray(measured_pc[data_rows])
    data_weights = np.asarray(measured_weights[data_rows], dtype=np.float64)
    if (
        np.any(w_truth < 0)
        or np.any(data_weights < 0)
        or not np.all(np.isfinite(w_truth))
        or not np.all(np.isfinite(data_weights))
    ):
        raise ValueError("xps2 pilot requires finite nonnegative staged weights")
    reco = _reco_batch(
        part_reco,
        valid_rows=pass_reco,
        provenance="xps2_signal_reco_bounded_recoil_pilot",
    )
    truth = _truth_batch(part_gen, pass_truth)
    data = _reco_batch(
        data_cloud,
        valid_rows=np.ones(data_cloud.shape[0], dtype=bool),
        provenance="xps2_measured_bounded_recoil_pilot",
    )
    background = data.subset(np.empty(0, dtype=np.int64))
    background = TokenBatch(
        **{
            **background.__dict__,
            "provenance": "xps2_background_unavailable_empty_downgrade",
        }
    ).validated()
    receipt = {
        "kind": "xps2_precomputed_measured_weights_bounded_pilot",
        "source_inventory": inventory.receipt,
        "measured_inventory_rows": int(measured_pc.shape[0]),
        "selected_data_rows": int(data_rows.size),
        "selected_data_rows_sha256": array_hash(data_rows),
        "selected_mc_rows_before_truth_gate": int(inventory.selected_rows.size),
        "selected_mc_rows_after_truth_gate": int(keep.sum()),
        "truth_gate_dropped_rows": int((~keep).sum()),
        "w_reco_available": False,
        "w_reco_proxy": "w_truth",
        "literal_background_inventory_available": False,
        "measured_weight_semantics": "precomputed upstream xps2 target; no Gate-2 receipt",
        "explicit_source_mask_available": False,
        "mask_downgrade": "derived from producer-zero-padded recoil tensors",
        "not_publication_eligible": True,
    }
    dataset = CanonicalDataset(
        signal=SignalInventory(
            reco=reco,
            truth=truth,
            pass_reco=pass_reco,
            pass_truth=pass_truth,
            w_reco=w_truth,
            w_truth=w_truth,
            identity_hash="",
            event_key=None,
        ),
        measured=MeasuredInventory(
            data=data,
            background=background,
            refined_weights=data_weights,
            raw_signed_weights=data_weights,
            data_identity_hash="",
            background_identity_hash="",
            target_receipt=receipt,
        ),
        estimator_fingerprint="pet2-xps2-bounded-recoil-proxy-v1",
        schema={
            "source": "recoil_xps2_proxy",
            "evidence_class": "recoil-input-pilot",
            "input_directory": str(root),
            "feature_semantics": {
                "reco": "historical xps2 (E,pos,z), source MeV/mm, adapter GeV/m",
                "truth": "historical xps2 (E,px,py,pz,PDG), PDG mask only",
                "globals": "unavailable; one zero capacity-preserving placeholder",
            },
            "contract_downgrades": receipt,
            "full_event_evidence": False,
            "typed_object_evidence": False,
            "g2_validation_claim": False,
        },
        pot_scale=1.0,
        pot_scale_source="xps2_proxy_footing_explicit_unity",
    ).validated()
    return dataset


def _arm() -> ArmManifest:
    return ArmManifest(
        arm="XPS2-recoil-proxy",
        comparison_parent="TF-A-recoil",
        initialization="random",
        use_real_types=False,
        use_detector_view=False,
        muon_representation="disabled",
        use_overflow_aggregate=False,
        active_globals=(),
        disabled_features={
            "object_type": "unavailable",
            "detector_view": "unavailable",
            "muon": "unavailable",
            "rich_globals": "unavailable",
            "overflow": "pre-truncation inventory unavailable",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-mc-rows", type=int, default=100000)
    parser.add_argument("--max-data-rows", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--split-seed", type=int, default=424242)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    seed_everything(args.seed, deterministic=True)
    dataset = build_xps2_recoil_dataset(
        args.directory,
        max_mc_rows=args.max_mc_rows,
        max_data_rows=args.max_data_rows,
        seed=args.seed,
    )
    ratio = RatioTrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=1e-4,
        weight_decay=1e-2,
        seed=args.seed,
        device=args.device,
    )
    config = OneIterationConfig(ratio=ratio, split_seed=args.split_seed)
    destination = Path(args.out).expanduser().resolve()
    with atomic_run_directory(destination) as temporary:
        result, receipts = run_iterations(
            dataset, _arm(), config, iterations=args.iterations
        )
        run_path = temporary / "result"
        save_iteration_result(
            run_path,
            result,
            config={**config.payload(), "iterations": args.iterations},
            arm_manifest=_arm().payload(),
        )
        summary: dict[str, Any] = {
            "status": "complete_bounded_xps2_recoil_pilot",
            "evidence_class": "recoil-input-pilot",
            "dataset_manifest": dataset.manifest(),
            "arm_manifest": _arm().payload(),
            "seed": args.seed,
            "split_seed": args.split_seed,
            "iterations": args.iterations,
            "epochs_per_step": args.epochs,
            "result_relative_path": "result",
            "recipe_fingerprint": result.receipt["recipe_fingerprint"],
            "push": result.receipt["push"],
            "pull": result.receipt["pull"],
            "runtime_seconds": float(
                sum(item["runtime_seconds"] for item in receipts)
            ),
            "environment": environment_receipt(),
            "contract_downgrades": dataset.measured.target_receipt,
            "full_event_evidence": False,
            "typed_object_evidence": False,
            "g2_validation_claim": False,
            "publication_promotion_permitted": False,
        }
        summary["fingerprint"] = fingerprint(summary)
        write_json(temporary / "summary.json", summary)
        print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
