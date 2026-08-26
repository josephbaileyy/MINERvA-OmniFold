#!/usr/bin/env python3
"""Deterministic CPU machinery fixture for PET-v2 fixed-draw equivalence.

This is deliberately not PET training.  It validates the bookkeeping needed to
compare retained-row Poisson sample weights with literal delete/duplicate
materialization while assigning unique-event train/validation membership before
duplication.  The synthetic optimizer trace is a positive control showing that
related aggregate objectives need not produce the same finite-batch Adam path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping

import numpy as np


REPO = Path(__file__).resolve().parents[2]
DEFAULT_RECEIPT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-fixture-result-20260825.json"
)
CONTRACT_ID = "PET-V2-FIXED-DRAW-EQUIVALENCE-FIXTURE-20260825"
BATCH_SIZE = 4
TOY_EPOCHS = 4
TOY_ADAM = {
    "learning_rate": 0.05,
    "beta_1": 0.9,
    "beta_2": 0.999,
    "epsilon": 1.0e-8,
    "initial_theta": 0.2,
    "shuffle_seed_base": 20260825,
}

EXPECTED_SOURCE_SHA256 = {
    "omnifold_nn/omnifold/net.py":
        "f793e53749d5754e11a7877a743ed6090b45e941c29c6162927fce74894cb953",
    "omnifold_nn/omnifold/omnifold.py":
        "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa",
    "omnifold_nn/omnifold/dataloader.py":
        "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a",
    "nd-unfolding/pet/fullevent_fps_dataloader.py":
        "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1",
    "nd-unfolding/pet/train_fullevent_replica.py":
        "c92c9cc06033f195ac48cddc86eea95a67b3038ae12fcffcd3cc966540b4e75f",
    "nd-unfolding/pet/train_fullevent_nominal.py":
        "91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc",
}

PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
)


def fixed_unique_rows() -> Dict[str, np.ndarray]:
    """Return one immutable-by-convention synthetic fixed draw over unique rows."""
    p_parallel = np.asarray([2.0, 4.0, 5.0, 5.5, 7.0, 9.0, 12.0, 18.0,
                             22.0, 30.0, 60.0, 80.0], dtype=np.float64)
    region = np.where(
        p_parallel < 6.0,
        "low_p_parallel_lt_6",
        np.where(p_parallel <= 20.0, "mid_p_parallel_6_to_20", "high_p_parallel_gt_20"),
    )
    return {
        "event_id": np.arange(1001, 1013, dtype=np.int64),
        "multiplicity": np.asarray([0, 1, 2, 3, 1, 0, 4, 2, 1, 0, 3, 2], dtype=np.int64),
        # The split is frozen on unique IDs and is copied to every literal duplicate.
        "is_train": np.asarray(
            [True, True, True, True, False, False, True, True, False, False, True, False],
            dtype=bool,
        ),
        "feature": np.asarray(
            [-1.4, -1.0, -0.7, -0.3, 0.1, 0.4, 0.8, 1.1, 1.5, 1.9, 2.4, 2.9],
            dtype=np.float64,
        ),
        "label": np.asarray([0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0], dtype=np.float64),
        "base_weight": np.asarray(
            [0.8, 1.1, 0.9, 1.2, 1.0, 0.7, 1.3, 0.6, 1.4, 0.5, 0.95, 1.05],
            dtype=np.float64,
        ),
        "fixed_logit": np.asarray(
            [-0.9, -0.5, 0.3, -0.1, 0.6, -0.2, 1.0, 0.7, -0.4, 0.8, 1.2, -0.6],
            dtype=np.float64,
        ),
        "p_parallel_gev": p_parallel,
        "region": region,
        "push": np.asarray(
            [0.90, 1.05, 1.20, 0.82, 1.15, 0.95, 1.40, 1.08, 0.75, 1.22, 0.68, 1.31],
            dtype=np.float64,
        ),
        "extraction_factor": np.asarray(
            [1.1, 1.0, 0.9, 1.2, 0.8, 1.3, 1.0, 0.7, 1.4, 1.1, 0.6, 0.5],
            dtype=np.float64,
        ),
    }


def _validate_unique_rows(rows: Mapping[str, np.ndarray]) -> int:
    lengths = {key: np.asarray(value).shape[0] for key, value in rows.items()}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"fixture fields are not row-aligned: {lengths}")
    n_rows = next(iter(lengths.values()))
    event_id = np.asarray(rows["event_id"])
    multiplicity = np.asarray(rows["multiplicity"])
    if np.unique(event_id).size != n_rows:
        raise ValueError("event_id must be unique before literal materialization")
    if not np.issubdtype(multiplicity.dtype, np.integer):
        raise ValueError("multiplicity must be an integer array")
    if np.any(multiplicity < 0):
        raise ValueError("multiplicity must be non-negative")
    if not np.all(np.isfinite(np.asarray(rows["base_weight"], dtype=float))):
        raise ValueError("base weights must be finite")
    return n_rows


def weighted_arm(rows: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Current representation: retain every row and multiply its sample weight by k."""
    n_rows = _validate_unique_rows(rows)
    arm = {key: np.asarray(value).copy() for key, value in rows.items()}
    arm["source_index"] = np.arange(n_rows, dtype=np.int64)
    arm["copy_index"] = np.zeros(n_rows, dtype=np.int64)
    arm["sample_weight"] = (
        np.asarray(rows["base_weight"], dtype=np.float64)
        * np.asarray(rows["multiplicity"], dtype=np.float64)
    )
    return arm


def literal_arm(rows: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Literal representation: delete k=0 and materialize exactly k copies otherwise."""
    n_rows = _validate_unique_rows(rows)
    multiplicity = np.asarray(rows["multiplicity"], dtype=np.int64)
    source_index = np.repeat(np.arange(n_rows, dtype=np.int64), multiplicity)
    copy_parts = [np.arange(int(k), dtype=np.int64) for k in multiplicity if k]
    copy_index = np.concatenate(copy_parts) if copy_parts else np.empty(0, dtype=np.int64)
    arm = {key: np.asarray(value)[source_index].copy() for key, value in rows.items()}
    arm["source_index"] = source_index
    arm["copy_index"] = copy_index
    # Each literal copy carries the original event weight, not k times that weight.
    arm["sample_weight"] = np.asarray(rows["base_weight"], dtype=np.float64)[source_index]
    return arm


def validate_literal_materialization(
    unique: Mapping[str, np.ndarray], literal: Mapping[str, np.ndarray]
) -> None:
    """Fail closed on count, identity, or split leakage in a literal materialization."""
    n_rows = _validate_unique_rows(unique)
    source_index = np.asarray(literal["source_index"], dtype=np.int64)
    if np.any((source_index < 0) | (source_index >= n_rows)):
        raise ValueError("literal source_index is out of range")
    observed = np.bincount(source_index, minlength=n_rows)
    expected = np.asarray(unique["multiplicity"], dtype=np.int64)
    if not np.array_equal(observed, expected):
        raise ValueError(f"literal copy counts do not replay the draw: {observed} != {expected}")
    if not np.array_equal(
        np.asarray(literal["event_id"]), np.asarray(unique["event_id"])[source_index]
    ):
        raise ValueError("literal event identity is not inherited from source_index")
    if not np.array_equal(
        np.asarray(literal["is_train"]), np.asarray(unique["is_train"])[source_index]
    ):
        raise ValueError("literal split membership changed after duplication")
    ids = np.asarray(literal["event_id"])
    split = np.asarray(literal["is_train"], dtype=bool)
    train_ids = set(ids[split].tolist())
    validation_ids = set(ids[~split].tolist())
    if train_ids & validation_ids:
        raise ValueError("a unique event crosses train and validation after duplication")


def binary_crossentropy(logit: np.ndarray, label: np.ndarray) -> np.ndarray:
    logit = np.asarray(logit, dtype=np.float64)
    label = np.asarray(label, dtype=np.float64)
    return np.logaddexp(0.0, logit) - label * logit


def _aggregate_by_source(values: np.ndarray, source_index: np.ndarray, n_unique: int) -> np.ndarray:
    return np.bincount(
        np.asarray(source_index, dtype=np.int64),
        weights=np.asarray(values, dtype=np.float64),
        minlength=n_unique,
    )


def _batch_means(arm: Mapping[str, np.ndarray], batch_size: int, train: bool) -> list[float]:
    mask = np.asarray(arm["is_train"], dtype=bool) == bool(train)
    loss = (
        np.asarray(arm["sample_weight"], dtype=np.float64)
        * binary_crossentropy(arm["fixed_logit"], arm["label"])
    )[mask]
    return [float(np.mean(loss[start:start + batch_size]))
            for start in range(0, loss.size, batch_size)]


def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return np.where(x >= 0.0, 1.0 / (1.0 + np.exp(-x)), np.exp(x) / (1.0 + np.exp(x)))


def toy_adam_trace(arm: Mapping[str, np.ndarray]) -> dict:
    """Run a scalar logistic positive control; this is not a PET surrogate or result."""
    theta = float(TOY_ADAM["initial_theta"])
    m = 0.0
    v = 0.0
    update = 0
    epoch_rows = []
    train_idx = np.flatnonzero(np.asarray(arm["is_train"], dtype=bool))
    validation_idx = np.flatnonzero(~np.asarray(arm["is_train"], dtype=bool))
    for epoch in range(TOY_EPOCHS):
        rng = np.random.default_rng(int(TOY_ADAM["shuffle_seed_base"]) + epoch)
        order = train_idx[rng.permutation(train_idx.size)]
        for start in range(0, order.size, BATCH_SIZE):
            idx = order[start:start + BATCH_SIZE]
            x = np.asarray(arm["feature"], dtype=np.float64)[idx]
            y = np.asarray(arm["label"], dtype=np.float64)[idx]
            weight = np.asarray(arm["sample_weight"], dtype=np.float64)[idx]
            gradient = float(np.mean(weight * (_sigmoid(theta * x) - y) * x))
            update += 1
            beta_1 = float(TOY_ADAM["beta_1"])
            beta_2 = float(TOY_ADAM["beta_2"])
            m = beta_1 * m + (1.0 - beta_1) * gradient
            v = beta_2 * v + (1.0 - beta_2) * gradient * gradient
            m_hat = m / (1.0 - beta_1 ** update)
            v_hat = v / (1.0 - beta_2 ** update)
            theta -= float(TOY_ADAM["learning_rate"]) * m_hat / (
                np.sqrt(v_hat) + float(TOY_ADAM["epsilon"])
            )
        x_val = np.asarray(arm["feature"], dtype=np.float64)[validation_idx]
        y_val = np.asarray(arm["label"], dtype=np.float64)[validation_idx]
        w_val = np.asarray(arm["sample_weight"], dtype=np.float64)[validation_idx]
        val_loss = float(np.mean(w_val * binary_crossentropy(theta * x_val, y_val)))
        epoch_rows.append({
            "epoch": epoch + 1,
            "updates_cumulative": update,
            "theta": theta,
            "adam_m": m,
            "adam_v": v,
            "validation_reduce_mean": val_loss,
        })
    return {"epochs": epoch_rows, "final": epoch_rows[-1]}


def _projection_sums(arm: Mapping[str, np.ndarray]) -> dict:
    sample_weight = np.asarray(arm["sample_weight"], dtype=np.float64)
    push = sample_weight * np.asarray(arm["push"], dtype=np.float64)
    extracted = push * np.asarray(arm["extraction_factor"], dtype=np.float64)
    region = np.asarray(arm["region"])
    result = {}
    for name in ("low_p_parallel_lt_6", "mid_p_parallel_6_to_20", "high_p_parallel_gt_20"):
        mask = region == name
        result[name] = {
            "push_sum": float(push[mask].sum()),
            "extracted_sum": float(extracted[mask].sum()),
        }
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_hashes() -> dict[str, str]:
    observed = {name: _sha256(REPO / name) for name in EXPECTED_SOURCE_SHA256}
    if observed != EXPECTED_SOURCE_SHA256:
        mismatch = {
            name: {"expected": EXPECTED_SOURCE_SHA256[name], "observed": observed[name]}
            for name in observed
            if observed[name] != EXPECTED_SOURCE_SHA256[name]
        }
        raise RuntimeError(f"governing source hashes changed; re-audit before use: {mismatch}")
    return observed


def _canonical_digest(fields: Mapping[str, Iterable]) -> str:
    text = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean(value):
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.floating, float)):
        return float(np.round(float(value), 15))
    if isinstance(value, (np.integer, int)):
        return int(value)
    return value


def build_receipt() -> dict:
    unique = fixed_unique_rows()
    weighted = weighted_arm(unique)
    literal = literal_arm(unique)
    validate_literal_materialization(unique, literal)
    n_unique = _validate_unique_rows(unique)

    loss_weighted = (
        weighted["sample_weight"] * binary_crossentropy(weighted["fixed_logit"], weighted["label"])
    )
    loss_literal = (
        literal["sample_weight"] * binary_crossentropy(literal["fixed_logit"], literal["label"])
    )
    per_event_weighted = _aggregate_by_source(loss_weighted, weighted["source_index"], n_unique)
    per_event_literal = _aggregate_by_source(loss_literal, literal["source_index"], n_unique)
    projection_weighted = _projection_sums(weighted)
    projection_literal = _projection_sums(literal)
    projection_delta = {
        region: {
            field: projection_weighted[region][field] - projection_literal[region][field]
            for field in projection_weighted[region]
        }
        for region in projection_weighted
    }
    adam_weighted = toy_adam_trace(weighted)
    adam_literal = toy_adam_trace(literal)

    draw_fields = {
        "event_id": unique["event_id"].tolist(),
        "multiplicity": unique["multiplicity"].tolist(),
        "is_train": unique["is_train"].astype(int).tolist(),
    }
    zero_ids = unique["event_id"][unique["multiplicity"] == 0]
    split_overlap = sorted(
        set(literal["event_id"][literal["is_train"]].tolist())
        & set(literal["event_id"][~literal["is_train"]].tolist())
    )
    optimizer_paths_differ = not np.isclose(
        adam_weighted["final"]["theta"], adam_literal["final"]["theta"], rtol=0.0, atol=1e-12
    )
    validation_paths_differ = not np.allclose(
        [row["validation_reduce_mean"] for row in adam_weighted["epochs"]],
        [row["validation_reduce_mean"] for row in adam_literal["epochs"]],
        rtol=0.0,
        atol=1e-12,
    )

    receipt = {
        "schema_version": 1,
        "contract_id": CONTRACT_ID,
        "status": "PASS_MACHINERY_VALIDATION_ONLY",
        "scientific_pet_equivalence": "NOT_MEASURED",
        "interval_coverage": "NOT_MEASURED",
        "scope": (
            "Synthetic CPU fixture for factor replay, split-before-duplication, aggregate push/"
            "extraction identity, and a finite-batch Adam positive control. No PET model is trained."
        ),
        "governing_source_sha256": source_hashes(),
        "fixed_draw": {
            **draw_fields,
            "canonical_sha256": _canonical_digest(draw_fields),
            "n_unique_rows": n_unique,
            "sum_multiplicity": int(unique["multiplicity"].sum()),
            "zero_multiplicity_event_ids": zero_ids.tolist(),
        },
        "split": {
            "assignment": "explicit unique-event membership before literal duplication",
            "train_unique_event_ids": unique["event_id"][unique["is_train"]].tolist(),
            "validation_unique_event_ids": unique["event_id"][~unique["is_train"]].tolist(),
            "cross_partition_event_ids_after_duplication": split_overlap,
        },
        "arms": {
            "weighted_retained_rows": {
                "n_rows": int(weighted["event_id"].size),
                "n_zero_sample_weight_rows": int((weighted["sample_weight"] == 0.0).sum()),
                "loss_reduce_mean_all_rows": float(np.mean(loss_weighted)),
                "train_batch_reduce_means_in_fixed_row_order": _batch_means(
                    weighted, BATCH_SIZE, train=True
                ),
                "validation_batch_reduce_means_in_fixed_row_order": _batch_means(
                    weighted, BATCH_SIZE, train=False
                ),
            },
            "literal_delete_duplicate": {
                "n_rows": int(literal["event_id"].size),
                "n_zero_sample_weight_rows": int((literal["sample_weight"] == 0.0).sum()),
                "loss_reduce_mean_all_rows": float(np.mean(loss_literal)),
                "train_batch_reduce_means_in_fixed_row_order": _batch_means(
                    literal, BATCH_SIZE, train=True
                ),
                "validation_batch_reduce_means_in_fixed_row_order": _batch_means(
                    literal, BATCH_SIZE, train=False
                ),
            },
        },
        "mechanical_equalities": {
            "literal_copy_counts_equal_fixed_multiplicity": True,
            "weighted_arm_retains_all_zero_multiplicity_rows": bool(
                set(zero_ids.tolist()).issubset(set(weighted["event_id"].tolist()))
            ),
            "literal_arm_deletes_all_zero_multiplicity_rows": bool(
                not set(zero_ids.tolist()) & set(literal["event_id"].tolist())
            ),
            "no_unique_event_crosses_train_validation": not split_overlap,
            "loss_numerator_weighted": float(loss_weighted.sum()),
            "loss_numerator_literal": float(loss_literal.sum()),
            "per_event_loss_contribution_max_abs_delta": float(
                np.max(np.abs(per_event_weighted - per_event_literal))
            ),
            "projection_weighted": projection_weighted,
            "projection_literal": projection_literal,
            "projection_delta": projection_delta,
            "projection_max_abs_delta": float(max(
                abs(value)
                for region in projection_delta.values()
                for value in region.values()
            )),
        },
        "optimization_positive_control": {
            "purpose": (
                "Demonstrate mechanism only: unequal row/batch counts can produce different Adam "
                "and validation-loss paths despite equal aggregate loss numerators."
            ),
            "batch_size": BATCH_SIZE,
            "epochs": TOY_EPOCHS,
            "adam": TOY_ADAM,
            "weighted_trace": adam_weighted,
            "literal_trace": adam_literal,
            "optimizer_paths_differ": optimizer_paths_differ,
            "validation_monitor_paths_differ": validation_paths_differ,
            "is_pet_training_or_pet_bias_measurement": False,
        },
        "predeclared_projection_regions": [
            "p_parallel < 6 GeV",
            "6 GeV <= p_parallel <= 20 GeV",
            "p_parallel > 20 GeV",
        ],
        "prohibitions_applied": {name: True for name in PROHIBITIONS},
        "terminal_result_cannot_authorize": [
            "selection of a passing Gate-6 subset",
            "construction of C_stat or C_ML",
            "movement of the PET central estimator",
            "Gate-6 Leg 2 or any unchanged retry",
            "a full fixed-draw PET equivalence run",
            "a convergence, estimator-equivalence, or interval-coverage claim",
            "publication adoption or a publication uncertainty claim",
            "Slurm, srun, GPU training, or a pseudoexperiment count",
        ],
    }

    checks = receipt["mechanical_equalities"]
    if not (
        checks["literal_copy_counts_equal_fixed_multiplicity"]
        and checks["weighted_arm_retains_all_zero_multiplicity_rows"]
        and checks["literal_arm_deletes_all_zero_multiplicity_rows"]
        and checks["no_unique_event_crosses_train_validation"]
        and checks["per_event_loss_contribution_max_abs_delta"] <= 1e-12
        and checks["projection_max_abs_delta"] <= 1e-12
        and optimizer_paths_differ
        and validation_paths_differ
    ):
        raise RuntimeError("fixture did not realize every predeclared machinery control")
    return _clean(receipt)


def render_receipt() -> str:
    return json.dumps(build_receipt(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_receipt()
    if args.stdout:
        print(rendered, end="")
    if args.check:
        if not args.output.exists():
            raise SystemExit(f"FAIL: receipt does not exist: {args.output}")
        if args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"FAIL: committed receipt differs from deterministic render: {args.output}")
        print("PASS: PET-v2 CPU fixture receipt is deterministic and source-bound")
    if not args.stdout and not args.check:
        raise SystemExit("refusing implicit write; use --stdout and land generated output via apply_patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
