"""Counterfactual feature-conditional stress fixtures.

Every direct-parent tensor occurs in an exact split-local pair.  Only the
declared enriched carrier distinguishes the pair members, so the parent
conditional ratio is analytically one while the enriched target is 0.5/1.5.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from .contracts import CanonicalDataset, MeasuredInventory, SignalInventory, TokenBatch
from .features import (
    ArmManifest,
    FeatureCapabilities,
    TYPE_OVERFLOW,
    TYPE_RECO_CLUSTER,
    TYPE_TRACK,
    VIEW_AGGREGATE,
    VIEW_U,
    VIEW_V,
    VIEW_X,
    build_arm_manifest,
    materialize_feature_view,
)
from .fixtures import ConditionalClosureFixture, make_synthetic_dataset
from .utils import array_hash, fingerprint, stable_partition

FAMILIES = ("view", "type", "rich", "muon-token", "overflow")
MODES = ("signal", "unity-sham", "carrier-shuffle")
TARGET_AMPLITUDE = 0.5
MODEL_TENSOR_FIELDS = frozenset(
    {"continuous", "coords", "token_mask", "type_id", "view_id", "globals"}
)
MUON_K_NEIGHBORS = 3
MIN_MUON_RECOIL_TOKENS = 2 * MUON_K_NEIGHBORS


@dataclass(frozen=True)
class StressArmPair:
    family: str
    parent_label: str
    child_label: str
    parent: ArmManifest
    child: ArmManifest


@dataclass(frozen=True)
class FeatureConditionalStressFixture(ConditionalClosureFixture):
    family: str
    mode: str
    pair_rows: np.ndarray
    hidden_sign: np.ndarray
    carrier_sign: np.ndarray
    arm_pair: StressArmPair
    exclusivity_certificate: dict[str, Any]


def stress_arm_pair(
    family: str, capabilities: FeatureCapabilities
) -> StressArmPair:
    if family == "view":
        parent = build_arm_manifest("C", capabilities)
        child = build_arm_manifest("D-view", capabilities)
        labels = ("C", "D-view")
    elif family == "type":
        parent = build_arm_manifest("C", capabilities)
        child = build_arm_manifest("D-typed", capabilities)
        labels = ("C", "D-typed")
    elif family == "rich":
        parent = build_arm_manifest("E-muon", capabilities)
        child = build_arm_manifest("E-rich-no-charge", capabilities)
        labels = ("E-muon", "E-rich-no-charge")
    elif family == "muon-token":
        parent = replace(
            build_arm_manifest(
                "E-muon", capabilities, muon_representation="global"
            ),
            arm="E-muon-global",
        )
        child = replace(
            build_arm_manifest(
                "E-muon", capabilities, muon_representation="global+token"
            ),
            arm="E-muon-global-plus-token",
            comparison_parent="E-muon-global",
        )
        labels = ("E-muon-global", "E-muon-global-plus-token")
    elif family == "overflow":
        parent = replace(
            build_arm_manifest(
                "C", capabilities, use_overflow_aggregate=False
            ),
            arm="C-truncated",
        )
        child = replace(
            build_arm_manifest(
                "C", capabilities, use_overflow_aggregate=True
            ),
            arm="C-plus-overflow",
            comparison_parent="C-truncated",
        )
        labels = ("C-truncated", "C-plus-overflow")
    else:
        raise ValueError(f"unknown conditional stress family: {family}")
    return StressArmPair(family, labels[0], labels[1], parent, child)


def _copy_rows(batch: TokenBatch, source: np.ndarray, destination: np.ndarray) -> TokenBatch:
    updates: dict[str, Any] = {}
    for name in (
        "continuous",
        "coords",
        "token_mask",
        "type_id",
        "view_id",
        "globals",
        "overflow_energy",
        "muon_continuous",
        "muon_coords",
        "muon_present",
    ):
        value = getattr(batch, name)
        if value is None:
            updates[name] = None
        else:
            copied = value.copy()
            copied[destination] = copied[source]
            updates[name] = copied
    return replace(batch, **updates).validated()


def _auc(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=bool)
    scores = np.asarray(scores, dtype=np.float64)
    if labels.shape != scores.shape or labels.ndim != 1:
        raise ValueError("AUC inputs must be aligned one-dimensional arrays")
    positive = int(labels.sum())
    negative = int((~labels).sum())
    if not positive or not negative:
        raise ValueError("AUC requires both classes")
    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(scores.size, dtype=np.float64)
    start = 0
    while start < scores.size:
        stop = start + 1
        while stop < scores.size and sorted_scores[stop] == sorted_scores[start]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + 1 + stop)
        start = stop
    return float(
        (ranks[labels].sum() - positive * (positive + 1) / 2)
        / (positive * negative)
    )


def _truth_tensor_hash(batch: TokenBatch) -> str:
    arrays = [
        batch.continuous,
        batch.coords,
        batch.token_mask,
        batch.type_id,
        batch.view_id,
        batch.globals,
        batch.row_index,
    ]
    for name in (
        "overflow_energy",
        "muon_continuous",
        "muon_coords",
        "muon_present",
    ):
        value = getattr(batch, name)
        if value is not None:
            arrays.append(value)
    return fingerprint(
        {
            "global_names": list(batch.global_names),
            "array_sha256": array_hash(*arrays),
            "optional_fields_present": {
                name: getattr(batch, name) is not None
                for name in (
                    "overflow_energy",
                    "muon_continuous",
                    "muon_coords",
                    "muon_present",
                )
            },
        }
    )


def _model_tensor_hash(batch: TokenBatch) -> str:
    return array_hash(
        batch.continuous,
        batch.coords,
        batch.token_mask,
        batch.type_id,
        batch.view_id,
        batch.globals,
    )


def _pair_rows(
    dataset: CanonicalDataset, *, split_seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    signal = dataset.signal
    partitions = stable_partition(
        signal.reco.row_index,
        split_seed,
        (0.7, 0.15, 0.15),
        identity=signal.event_key,
    )
    truth_mu_pt = signal.truth.globals[
        :, signal.truth.global_names.index("mu_pt")
    ]
    pairs: list[np.ndarray] = []
    hidden = np.zeros(signal.reco.n_rows, dtype=np.int8)
    for partition in range(3):
        rows = np.flatnonzero(signal.pass_reco & (partitions == partition))
        order = rows[np.argsort(truth_mu_pt[rows], kind="mergesort")]
        count = len(order) // 2
        lower = order[:count]
        upper = order[-count:]
        hidden[lower] = -1
        hidden[upper] = 1
        pairs.append(np.column_stack((lower, upper)))
    pair_rows = np.concatenate(pairs, axis=0).astype(np.int64)
    if pair_rows.shape[0] < 100:
        raise ValueError("conditional stress fixture has too few split-local pairs")
    return pair_rows, hidden, partitions


def _shuffle_carrier(
    hidden: np.ndarray,
    paired_rows: np.ndarray,
    partitions: np.ndarray,
    *,
    seed: int,
) -> tuple[np.ndarray, float, dict[str, float]]:
    carrier = hidden.copy()
    paired = paired_rows.reshape(-1)
    labels = hidden[paired] > 0
    for attempt in range(1000):
        candidate = hidden.copy()
        for partition in range(3):
            rows = paired[partitions[paired] == partition]
            rng = np.random.default_rng(seed + 1009 * attempt + partition)
            candidate[rows] = candidate[rows][rng.permutation(len(rows))]
        auc = _auc(labels, candidate[paired])
        by_partition = {
            str(partition): _auc(
                labels[partitions[paired] == partition],
                candidate[paired][partitions[paired] == partition],
            )
            for partition in range(3)
        }
        if abs(auc - 0.5) <= 0.02 and all(
            abs(value - 0.5) <= 0.02 for value in by_partition.values()
        ):
            return candidate, auc, by_partition
    raise RuntimeError("failed to construct a chance carrier shuffle")


def _assign_carrier(
    batch: TokenBatch,
    family: str,
    carrier_sign: np.ndarray,
    paired_rows: np.ndarray,
) -> TokenBatch:
    continuous = batch.continuous.copy()
    coords = batch.coords.copy()
    mask = batch.token_mask.copy()
    type_id = batch.type_id.copy()
    view_id = batch.view_id.copy()
    globals_ = batch.globals.copy()
    overflow = (
        None if batch.overflow_energy is None else batch.overflow_energy.copy()
    )
    muon_cont = (
        None if batch.muon_continuous is None else batch.muon_continuous.copy()
    )
    muon_coords = None if batch.muon_coords is None else batch.muon_coords.copy()
    muon_present = (
        None if batch.muon_present is None else batch.muon_present.copy()
    )
    rows = paired_rows.reshape(-1)
    for row in rows:
        valid = np.flatnonzero(mask[row] & (type_id[row] != TYPE_OVERFLOW))
        if family == "muon-token" and len(valid) < MIN_MUON_RECOIL_TOKENS:
            additions = np.flatnonzero(~mask[row])[
                : MIN_MUON_RECOIL_TOKENS - len(valid)
            ]
            if len(valid) + len(additions) < MIN_MUON_RECOIL_TOKENS:
                raise ValueError(
                    "muon carrier requires six recoil tokens so K=3 selects "
                    "one complete synthetic neighborhood"
                )
            mask[row, additions] = True
            type_id[row, additions] = TYPE_RECO_CLUSTER
            view_id[row, additions] = VIEW_X
            continuous[row, additions] = 0.0
            continuous[row, additions, 0] = 1.0
            coords[row, additions] = 0.0
            valid = np.flatnonzero(mask[row] & (type_id[row] != TYPE_OVERFLOW))
        if len(valid) < 2:
            raise ValueError("conditional carrier requires at least two retained tokens")
        first = valid[0]
        sign = int(carrier_sign[row])
        if family == "view":
            view_id[row, mask[row]] = 1
            view_id[row, first] = VIEW_U if sign > 0 else VIEW_V
        elif family == "type":
            type_id[row, mask[row]] = TYPE_RECO_CLUSTER
            type_id[row, first] = TYPE_TRACK if sign > 0 else TYPE_RECO_CLUSTER
        elif family == "rich":
            globals_[row, batch.global_names.index("vertex_z")] = float(sign)
        elif family == "muon-token":
            if muon_coords is None or muon_cont is None or muon_present is None:
                raise ValueError("muon carrier fields are unavailable")
            midpoint = len(valid) // 2
            left = valid[:midpoint]
            right = valid[midpoint:]
            coords[row, left] = np.asarray([0.0, 0.0], dtype=np.float32)
            continuous[row, left, 0] = 0.75
            if len(right):
                coords[row, right] = np.asarray([4.0, 0.0], dtype=np.float32)
                continuous[row, right, 0] = 2.25
            muon_coords[row] = (
                np.asarray([3.95, 0.0], dtype=np.float32)
                if sign > 0
                else np.asarray([0.05, 0.0], dtype=np.float32)
            )
            muon_present[row] = True
        elif family == "overflow":
            last = mask.shape[1] - 1
            mask[row, last] = True
            type_id[row, last] = TYPE_OVERFLOW
            view_id[row, last] = VIEW_AGGREGATE
            continuous[row, last] = 0.0
            continuous[row, last, 0] = 1.5 if sign > 0 else 0.5
            coords[row, last] = 0.0
            if overflow is None:
                raise ValueError("overflow evidence array is unavailable")
            overflow[row] = continuous[row, last, 0]
        else:  # pragma: no cover - guarded by public entry point
            raise ValueError(f"unknown conditional carrier: {family}")
    return replace(
        batch,
        continuous=continuous,
        coords=coords,
        token_mask=mask,
        type_id=type_id,
        view_id=view_id,
        globals=globals_,
        overflow_energy=overflow,
        muon_continuous=muon_cont,
        muon_coords=muon_coords,
        muon_present=muon_present,
        provenance=f"{batch.provenance}|conditional_carrier={family}",
    ).validated()


def _decode_carrier(batch: TokenBatch, family: str, rows: np.ndarray) -> np.ndarray:
    decoded = np.empty(len(rows), dtype=np.int8)
    for index, row in enumerate(rows):
        valid = np.flatnonzero(
            batch.token_mask[row] & (batch.type_id[row] != TYPE_OVERFLOW)
        )
        first = valid[0]
        if family == "view":
            decoded[index] = 1 if batch.view_id[row, first] == VIEW_U else -1
        elif family == "type":
            decoded[index] = 1 if batch.type_id[row, first] == TYPE_TRACK else -1
        elif family == "rich":
            decoded[index] = (
                1
                if batch.globals[row, batch.global_names.index("vertex_z")] > 0
                else -1
            )
        elif family == "muon-token":
            decoded[index] = 1 if batch.muon_coords[row, 0] > 2.0 else -1
        elif family == "overflow":
            decoded[index] = 1 if batch.overflow_energy[row] > 1.0 else -1
        else:  # pragma: no cover
            raise ValueError(f"unknown carrier family: {family}")
    return decoded


def _background_carrier(
    batch: TokenBatch, family: str
) -> TokenBatch:
    rows = np.arange(batch.n_rows, dtype=np.int64)
    if len(rows) % 2:
        rows = rows[:-1]
    paired = rows.reshape(-1, 2)
    carrier = np.zeros(batch.n_rows, dtype=np.int8)
    carrier[paired[:, 0]] = -1
    carrier[paired[:, 1]] = 1
    if len(paired):
        batch = _assign_carrier(batch, family, carrier, paired)
    return batch


def make_feature_conditional_stress_dataset(
    family: str,
    mode: str,
    *,
    n_signal: int = 100_000,
    n_background: int = 10_000,
    max_tokens: int = 7,
    seed: int = 424242,
    split_seed: int = 424242,
) -> FeatureConditionalStressFixture:
    if family not in FAMILIES:
        raise ValueError(f"family must be one of {FAMILIES}")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    dataset, capabilities = make_synthetic_dataset(
        n_signal=n_signal,
        n_data=max(16, n_signal // 2),
        n_background=n_background,
        max_tokens=max_tokens,
        seed=seed,
    )
    base_truth_tensor_sha256 = _truth_tensor_hash(dataset.signal.truth)
    pair_rows, hidden, partitions = _pair_rows(dataset, split_seed=split_seed)
    pair_members_same_partition = bool(
        np.array_equal(partitions[pair_rows[:, 0]], partitions[pair_rows[:, 1]])
    )
    if not pair_members_same_partition:
        raise AssertionError("counterfactual pair members cross a declared split")
    source = pair_rows[:, 0]
    destination = pair_rows[:, 1]
    paired_reco = _copy_rows(dataset.signal.reco, source, destination)
    carrier = hidden.copy()
    shuffle_auc = None
    shuffle_auc_by_partition = None
    if mode == "carrier-shuffle":
        carrier, shuffle_auc, shuffle_auc_by_partition = _shuffle_carrier(
            hidden,
            pair_rows,
            partitions,
            seed=seed + FAMILIES.index(family) * 10_000,
        )
    reco = _assign_carrier(paired_reco, family, carrier, pair_rows)
    pair = stress_arm_pair(family, capabilities)
    parent_view = materialize_feature_view(reco, pair.parent)
    pair_identical = {
        name: bool(
            np.array_equal(
                getattr(parent_view, name)[pair_rows[:, 0]],
                getattr(parent_view, name)[pair_rows[:, 1]],
            )
        )
        for name in (
            "continuous",
            "coords",
            "token_mask",
            "type_id",
            "view_id",
            "globals",
        )
    }
    if not all(pair_identical.values()):
        raise AssertionError(f"parent counterfactual tensors differ: {pair_identical}")
    paired_flat = pair_rows.reshape(-1)
    decoded = _decode_carrier(reco, family, paired_flat)
    if not np.array_equal(decoded, carrier[paired_flat]):
        raise AssertionError("enriched carrier decoder disagrees with constructed sign")
    labels = hidden[paired_flat] > 0
    carrier_auc = _auc(labels, decoded)
    carrier_auc_by_partition = {
        str(partition): _auc(
            labels[partitions[paired_flat] == partition],
            decoded[partitions[paired_flat] == partition],
        )
        for partition in range(3)
    }
    if mode != "carrier-shuffle" and carrier_auc != 1.0:
        raise AssertionError("signal carrier must decode hidden sign exactly")
    if mode == "carrier-shuffle" and (
        abs(carrier_auc - 0.5) > 0.02
        or any(
            abs(value - 0.5) > 0.02
            for value in carrier_auc_by_partition.values()
        )
    ):
        raise AssertionError(
            "shuffled carrier is not within the frozen chance band in every split"
        )
    muon_knn_relation_decodes_carrier = None
    if family == "muon-token":
        relation_decoded = np.empty(len(paired_flat), dtype=np.int8)
        for index, row in enumerate(paired_flat):
            valid = np.flatnonzero(
                reco.token_mask[row] & (reco.type_id[row] != TYPE_OVERFLOW)
            )
            if len(valid) < MIN_MUON_RECOIL_TOKENS:
                raise AssertionError("muon fixture has too few recoil neighbors")
            distances = np.linalg.norm(
                reco.coords[row, valid] - reco.muon_coords[row], axis=1
            )
            nearest = valid[
                np.argsort(distances, kind="mergesort")[:MUON_K_NEIGHBORS]
            ]
            mean_neighbor_energy = float(np.mean(reco.continuous[row, nearest, 0]))
            relation_decoded[index] = 1 if mean_neighbor_energy > 1.5 else -1
        muon_knn_relation_decodes_carrier = bool(
            np.array_equal(relation_decoded, carrier[paired_flat])
        )
        if not muon_knn_relation_decodes_carrier:
            raise AssertionError(
                "the model's K=3 coordinate neighborhood cannot decode the "
                "synthetic muon relation"
            )

    w_reco = dataset.signal.w_reco.copy()
    common = 0.5 * (w_reco[pair_rows[:, 0]] + w_reco[pair_rows[:, 1]])
    w_reco[pair_rows[:, 0]] = common
    w_reco[pair_rows[:, 1]] = common
    signal = replace(
        dataset.signal,
        reco=reco,
        w_reco=w_reco,
        identity_hash="",
    ).validated()
    selected = np.flatnonzero(signal.pass_reco)
    expected = np.ones(n_signal, dtype=np.float64)
    if mode != "unity-sham":
        expected[paired_flat] = 1.0 + TARGET_AMPLITUDE * hidden[paired_flat]
    data = replace(
        signal.reco.subset(selected),
        row_index=np.arange(len(selected), dtype=np.int64),
        provenance=f"conditional_{family}_{mode}_aligned_data",
    ).validated()
    background = _background_carrier(dataset.measured.background, family)
    data_weights = signal.w_reco[selected] * expected[selected]
    background_abs = np.abs(
        dataset.measured.raw_signed_weights[-background.n_rows :]
    )
    refined = np.concatenate(
        (data_weights, np.zeros(background.n_rows, dtype=np.float64))
    )
    raw_signed = np.concatenate((data_weights, -background_abs))
    target_receipt = {
        "kind": "synthetic_feature_conditional_stress_v1",
        "family": family,
        "mode": mode,
        "canonical_nonnegative": True,
        "ordering": "aligned_data_then_literal_background",
        "negative_weight_provenance_retained": True,
        "background_refined_training_mass": 0.0,
        "target_ratio": (
            "unity" if mode == "unity-sham" else "1 + 0.5 * hidden_sign"
        ),
        "refinement_carrier_dependence_unchanged": True,
        "background_carrier_distribution": (
            "balanced reconstructed-MC-like marginal; never data-tilted"
        ),
        "not_publication_gate2": True,
        "g2_validation_claim": False,
    }
    measured = MeasuredInventory(
        data=data,
        background=background,
        refined_weights=refined,
        raw_signed_weights=raw_signed,
        data_identity_hash="",
        background_identity_hash="",
        target_receipt=target_receipt,
        aligned_signal_row=np.concatenate(
            (selected.astype(np.int64), -np.ones(background.n_rows, dtype=np.int64))
        ),
    ).validated()
    stress_dataset = replace(
        dataset,
        signal=signal,
        measured=measured,
        estimator_fingerprint=f"pet2-feature-conditional-{family}-{mode}-v1",
        schema={
            **dict(dataset.schema),
            "source": "portable_synthetic_feature_conditional_stress",
            "family": family,
            "mode": mode,
            "ratio_carrier": "enriched_step1_feature_only",
            "truth_inventory_modified": False,
            "g2_validation_claim": False,
            "publication_promotion_permitted": False,
        },
    ).validated()
    stress_truth_tensor_sha256 = _truth_tensor_hash(
        stress_dataset.signal.truth
    )
    truth_unmodified = (
        stress_truth_tensor_sha256 == base_truth_tensor_sha256
    )
    if not truth_unmodified:
        raise AssertionError("reco-side carrier construction modified truth tensors")
    bookkeeping_names = {
        "row_index",
        "pair_rows",
        "pair_id",
        "hidden_sign",
        "carrier_sign",
        "expected",
        "target_ratio",
        "w_reco",
        "w_truth",
        "event_key",
        "pass_reco",
        "pass_truth",
        "source_label",
    }
    bookkeeping_excluded = not bool(bookkeeping_names & MODEL_TENSOR_FIELDS) and not bool(
        bookkeeping_names & set(stress_dataset.signal.reco.global_names)
    )
    if not bookkeeping_excluded:
        raise AssertionError("stress bookkeeping overlaps TokenBatch model fields")
    tail = stress_dataset.signal.pass_truth & (hidden > 0)
    parent_pair_hashes = {
        "low": _model_tensor_hash(parent_view.subset(pair_rows[:, 0])),
        "high": _model_tensor_hash(parent_view.subset(pair_rows[:, 1])),
    }
    if parent_pair_hashes["low"] != parent_pair_hashes["high"]:
        raise AssertionError("parent tensor hashes are not pair-identical")
    refined_ratio = measured.refined_weights[: len(selected)] / signal.w_reco[
        selected
    ]
    signed_data_ratio = measured.raw_signed_weights[: len(selected)] / signal.w_reco[
        selected
    ]
    refinement_matches = bool(
        np.array_equal(refined_ratio, signed_data_ratio)
        and np.allclose(
            refined_ratio,
            expected[selected],
            rtol=8.0 * np.finfo(np.float64).eps,
            atol=0.0,
        )
    )
    if not refinement_matches:
        raise AssertionError(
            "refined and signed targets transmit different conditional ratios"
        )
    balance_by_partition = {}
    for partition in range(3):
        rows = paired_flat[partitions[paired_flat] == partition]
        values, counts = np.unique(hidden[rows], return_counts=True)
        balance_by_partition[str(partition)] = {
            str(int(value)): int(count)
            for value, count in zip(values, counts)
        }
        if set(balance_by_partition[str(partition)].values()) != {
            len(rows) // 2
        }:
            raise AssertionError("hidden carrier is not balanced within a split")
    synthetic_overflow_matches = None
    if family == "overflow":
        rows = paired_flat
        overflow_tokens = reco.type_id[rows] == TYPE_OVERFLOW
        synthetic_overflow_matches = bool(
            np.all(overflow_tokens.sum(axis=1) == 1)
            and np.array_equal(
                reco.continuous[rows, :, 0][overflow_tokens],
                reco.overflow_energy[rows],
            )
        )
        if not synthetic_overflow_matches:
            raise AssertionError(
                "synthetic overflow aggregate disagrees with its declared energy"
            )
    parent_analytic_carrier_auc = _auc(
        labels, np.zeros(len(labels), dtype=np.float64)
    )
    parent_analytic_carrier_auc_by_partition = {
        str(partition): _auc(
            labels[partitions[paired_flat] == partition],
            np.zeros(np.sum(partitions[paired_flat] == partition), dtype=np.float64),
        )
        for partition in range(3)
    }
    if parent_analytic_carrier_auc != 0.5:
        raise AssertionError("pair-tied parent analytic carrier AUC is not 0.5")
    if any(
        value != 0.5
        for value in parent_analytic_carrier_auc_by_partition.values()
    ):
        raise AssertionError(
            "pair-tied parent analytic carrier AUC is not 0.5 in every split"
        )
    certificate = {
        "status": "pass",
        "family": family,
        "mode": mode,
        "pair_count": int(len(pair_rows)),
        "paired_row_count": int(len(paired_flat)),
        "partition_pair_counts": {
            str(partition): int(
                np.sum(partitions[pair_rows[:, 0]] == partition)
            )
            for partition in range(3)
        },
        "pair_members_same_partition": pair_members_same_partition,
        "hidden_sign_counts_by_partition": balance_by_partition,
        "parent_tensor_fields_pair_identical": pair_identical,
        "parent_pair_tensor_hash": parent_pair_hashes["low"],
        "parent_analytic_carrier_auc": parent_analytic_carrier_auc,
        "parent_analytic_carrier_auc_by_partition": (
            parent_analytic_carrier_auc_by_partition
        ),
        "enriched_carrier_auc": carrier_auc,
        "enriched_carrier_auc_by_partition": carrier_auc_by_partition,
        "shuffled_carrier_auc": shuffle_auc,
        "shuffled_carrier_auc_by_partition": shuffle_auc_by_partition,
        "target_ratio_values": sorted(np.unique(expected[paired_flat]).tolist()),
        "pair_target_weighted_mean_exact": bool(
            np.allclose(
                0.5
                * (
                    expected[pair_rows[:, 0]]
                    + expected[pair_rows[:, 1]]
                ),
                1.0,
                rtol=0.0,
                atol=1e-12,
            )
        ),
        "truth_tensor_sha256": stress_truth_tensor_sha256,
        "base_truth_tensor_sha256": base_truth_tensor_sha256,
        "truth_inventory_sha256": fingerprint(
            {
                "truth_tensor_sha256": _truth_tensor_hash(
                    stress_dataset.signal.truth
                ),
                "pass_truth_sha256": array_hash(
                    stress_dataset.signal.pass_truth
                ),
                "w_truth_sha256": array_hash(stress_dataset.signal.w_truth),
                "event_key_sha256": array_hash(
                    stress_dataset.signal.event_key
                ),
            }
        ),
        "row_footing": {
            "event_key_sha256": array_hash(stress_dataset.signal.event_key),
            "pass_masks_sha256": array_hash(
                stress_dataset.signal.pass_reco,
                stress_dataset.signal.pass_truth,
            ),
            "w_reco_sha256": array_hash(stress_dataset.signal.w_reco),
            "w_truth_sha256": array_hash(stress_dataset.signal.w_truth),
            "selected_row_sha256": array_hash(selected),
            "pair_rows_sha256": array_hash(pair_rows),
        },
        "truth_modified_by_carrier": not truth_unmodified,
        "bookkeeping_excluded_from_model_tensors": bookkeeping_excluded,
        "model_tensor_fields": sorted(MODEL_TENSOR_FIELDS),
        "bookkeeping_fields_checked": sorted(bookkeeping_names),
        "refinement_carrier_dependence_unchanged": refinement_matches,
        "muon_knn_contract": (
            None
            if family != "muon-token"
            else {
                "k_neighbors": MUON_K_NEIGHBORS,
                "minimum_recoil_tokens": MIN_MUON_RECOIL_TOKENS,
                "nonzero_finite_muon_coordinates": bool(
                    np.all(np.isfinite(reco.muon_coords[paired_flat]))
                    and np.any(reco.muon_coords[paired_flat] != 0.0)
                ),
                "relation_decodes_assigned_carrier": (
                    muon_knn_relation_decodes_carrier
                ),
            }
        ),
        "synthetic_declared_overflow_energy_matches_aggregate_token": (
            synthetic_overflow_matches
        ),
        "real_pretruncation_overflow_conservation_claim": False,
        "background_carrier_distribution": (
            "balanced reconstructed-MC-like marginal; never data-tilted"
        ),
        "fingerprint": "",
    }
    certificate["fingerprint"] = fingerprint(certificate)
    specification = {
        "evidence_class": "synthetic-fixture",
        "fixture_kind": "feature_conditional_counterfactual_pairs_v1",
        "family": family,
        "mode": mode,
        "fixture_seed": seed,
        "split_seed": split_seed,
        "signal_rows": n_signal,
        "background_rows": n_background,
        "selected_rows": int(signal.pass_reco.sum()),
        "native_misses": int(np.sum(signal.pass_truth & ~signal.pass_reco)),
        "pair_count": int(len(pair_rows)),
        "target_amplitude": TARGET_AMPLITUDE,
        "target_ratio_range": [
            float(expected[paired_flat].min()),
            float(expected[paired_flat].max()),
        ],
        "parent_expected_event_log_rmse": float(
            np.sqrt(np.mean(np.square(np.log(expected[paired_flat]))))
        ),
        "tail_definition": "paired truth rows with hidden_sign=+1",
        "g2_validation_claim": False,
        "publication_promotion_permitted": False,
    }
    return FeatureConditionalStressFixture(
        dataset=stress_dataset,
        capabilities=capabilities,
        data_to_signal_row=selected.astype(np.int64),
        analytic_reco_ratio=expected[selected],
        expected_truth_ratio=expected,
        declared_tail_mask=tail,
        specification=specification,
        family=family,
        mode=mode,
        pair_rows=pair_rows,
        hidden_sign=hidden,
        carrier_sign=carrier,
        arm_pair=pair,
        exclusivity_certificate=certificate,
    )
