"""Portable synthetic fixtures for contract, closure, and Delta pilot tests."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from .contracts import CanonicalDataset, MeasuredInventory, SignalInventory, TokenBatch
from .features import (
    FeatureCapabilities,
    TYPE_OVERFLOW,
    TYPE_RECO_CLUSTER,
    TYPE_TRACK,
    VIEW_AGGREGATE,
)

GLOBAL_NAMES = (
    "mu_pt",
    "mu_pparallel",
    "mu_energy",
    "mu_cos_phi",
    "mu_sin_phi",
    "eavail",
    "q3",
    "mu_charge",
    "minos_ok",
    "vertex_x",
    "vertex_y",
    "vertex_z",
)


@dataclass(frozen=True)
class ConditionalClosureFixture:
    """Canonical dataset plus analytic aligned event-ratio evidence."""

    dataset: CanonicalDataset
    capabilities: FeatureCapabilities
    data_to_signal_row: np.ndarray
    analytic_reco_ratio: np.ndarray
    expected_truth_ratio: np.ndarray
    declared_tail_mask: np.ndarray
    specification: dict[str, Any]


def truncate_with_overflow(
    continuous: np.ndarray,
    type_id: np.ndarray,
    view_id: np.ndarray,
    object_mask: np.ndarray,
    max_tokens: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Energy-sort objects while conserving all discarded energy in one aggregate token."""
    continuous = np.asarray(continuous, dtype=np.float32)
    type_id = np.asarray(type_id, dtype=np.int64)
    view_id = np.asarray(view_id, dtype=np.int64)
    object_mask = np.asarray(object_mask, dtype=bool)
    if continuous.ndim != 3 or continuous.shape[:2] != type_id.shape:
        raise ValueError("raw object arrays are misaligned")
    if type_id.shape != view_id.shape or type_id.shape != object_mask.shape:
        raise ValueError("raw categorical/mask arrays are misaligned")
    if max_tokens < 2:
        raise ValueError("max_tokens must leave room for a physical and aggregate token")
    if not np.all(np.isfinite(continuous)):
        raise ValueError("raw objects contain NaN or infinity")
    if np.any(continuous[:, :, 0][object_mask] <= 0):
        raise ValueError("real fixture objects require positive energy")
    n, _, features = continuous.shape
    out = np.zeros((n, max_tokens, features), dtype=np.float32)
    out_type = np.zeros((n, max_tokens), dtype=np.int64)
    out_view = np.zeros((n, max_tokens), dtype=np.int64)
    out_mask = np.zeros((n, max_tokens), dtype=bool)
    overflow_energy = np.zeros(n, dtype=np.float64)
    for row in range(n):
        valid = np.flatnonzero(object_mask[row])
        order = valid[np.argsort(continuous[row, valid, 0])[::-1]]
        if len(order) <= max_tokens:
            keep = order
            out[row, : len(keep)] = continuous[row, keep]
            out_type[row, : len(keep)] = type_id[row, keep]
            out_view[row, : len(keep)] = view_id[row, keep]
            out_mask[row, : len(keep)] = True
        else:
            keep = order[: max_tokens - 1]
            discarded = order[max_tokens - 1 :]
            out[row, : len(keep)] = continuous[row, keep]
            out_type[row, : len(keep)] = type_id[row, keep]
            out_view[row, : len(keep)] = view_id[row, keep]
            out_mask[row, : len(keep)] = True
            energy = continuous[row, discarded, 0].astype(np.float64)
            aggregate = np.average(
                continuous[row, discarded].astype(np.float64),
                axis=0,
                weights=energy,
            )
            aggregate[0] = energy.sum()
            out[row, -1] = aggregate
            out_type[row, -1] = TYPE_OVERFLOW
            out_view[row, -1] = VIEW_AGGREGATE
            out_mask[row, -1] = True
            overflow_energy[row] = energy.sum()
    original_energy = np.sum(
        np.where(object_mask, continuous[:, :, 0], 0.0), axis=1, dtype=np.float64
    )
    output_energy = np.sum(out[:, :, 0], axis=1, dtype=np.float64)
    if not np.allclose(original_energy, output_energy, rtol=2e-6, atol=1e-6):
        raise AssertionError("overflow aggregate failed energy conservation")
    return out, out_type, out_view, out_mask, overflow_energy


def _raw_objects(
    rng: np.random.Generator,
    n: int,
    raw_tokens: int,
    latent: np.ndarray,
    conditional_shift: float = 0.0,
):
    count = rng.integers(2, raw_tokens + 1, size=n)
    object_mask = np.arange(raw_tokens)[None, :] < count[:, None]
    base = np.exp(
        0.25 * latent[:, None]
        + rng.normal(0.0, 0.45, size=(n, raw_tokens))
        + conditional_shift * (latent[:, None] > 0)
    )
    continuous = np.zeros((n, raw_tokens, 4), dtype=np.float32)
    continuous[:, :, 0] = base
    continuous[:, :, 1] = rng.normal(latent[:, None], 0.7, size=(n, raw_tokens))
    continuous[:, :, 2] = rng.normal(0.4 * latent[:, None], 0.8, size=(n, raw_tokens))
    continuous[:, :, 3] = rng.normal(0.0, 0.25, size=(n, raw_tokens))
    continuous[~object_mask] = 0.0
    type_id = rng.choice(
        np.asarray([TYPE_RECO_CLUSTER, TYPE_TRACK]),
        size=(n, raw_tokens),
        p=[0.7, 0.3],
    ).astype(np.int64)
    view_id = rng.integers(1, 4, size=(n, raw_tokens), dtype=np.int64)
    type_id[~object_mask] = 0
    view_id[~object_mask] = 0
    return continuous, type_id, view_id, object_mask


def _globals(rng, latent, distortion=0.0):
    mu_pt = np.exp(0.15 * latent + distortion * (latent > 0))
    mu_pparallel = 3.0 + 0.5 * latent + rng.normal(0, 0.1, len(latent))
    mu_energy = np.sqrt(np.square(mu_pt) + np.square(mu_pparallel) + 0.105**2)
    mu_phi = rng.uniform(-np.pi, np.pi, len(latent))
    eavail = np.exp(0.3 * latent + rng.normal(0, 0.15, len(latent)))
    q3 = np.sqrt(np.square(mu_pt) + np.square(eavail))
    charge = np.where(rng.random(len(latent)) > 0.05, -1.0, 1.0)
    minos = np.ones(len(latent))
    vertex = rng.normal(0, 0.3, size=(len(latent), 3))
    return np.column_stack(
        (
            mu_pt,
            mu_pparallel,
            mu_energy,
            np.cos(mu_phi),
            np.sin(mu_phi),
            eavail,
            q3,
            charge,
            minos,
            vertex,
        )
    ).astype(np.float32)


def _batch(
    rng,
    latent,
    max_tokens,
    provenance,
    *,
    distortion=0.0,
    valid_rows=None,
):
    n = len(latent)
    raw = _raw_objects(rng, n, max_tokens + 4, latent, distortion)
    continuous, type_id, view_id, mask, overflow = truncate_with_overflow(
        *raw, max_tokens=max_tokens
    )
    globals_ = _globals(rng, latent, distortion)
    muon = np.zeros((n, continuous.shape[2]), dtype=np.float32)
    muon[:, 0] = globals_[:, 2]
    muon[:, 1] = globals_[:, 0]
    muon[:, 2] = globals_[:, 1]
    muon[:, 3] = np.arctan2(globals_[:, 4], globals_[:, 3])
    muon_present = np.ones(n, dtype=bool)
    if valid_rows is not None:
        valid_rows = np.asarray(valid_rows, bool)
        continuous[~valid_rows] = 0.0
        type_id[~valid_rows] = 0
        view_id[~valid_rows] = 0
        mask[~valid_rows] = False
        globals_[~valid_rows] = 0.0
        muon[~valid_rows] = 0.0
        muon_present = valid_rows.copy()
        overflow[~valid_rows] = 0.0
    return TokenBatch(
        continuous=continuous,
        coords=continuous[:, :, 1:3].copy(),
        token_mask=mask,
        type_id=type_id,
        view_id=view_id,
        globals=globals_,
        row_index=np.arange(n, dtype=np.int64),
        global_names=GLOBAL_NAMES,
        provenance=provenance,
        overflow_energy=overflow,
        muon_continuous=muon,
        # Synthetic detector-plane coordinates are generated with the same
        # event vertex and are explicitly fixture-only evidence.
        muon_coords=globals_[:, [9, 11]].copy(),
        muon_present=muon_present,
    ).validated(max_type=TYPE_OVERFLOW, max_view=VIEW_AGGREGATE)


def make_synthetic_dataset(
    n_signal: int = 192,
    n_data: int = 128,
    n_background: int = 40,
    max_tokens: int = 7,
    seed: int = 101,
) -> tuple[CanonicalDataset, FeatureCapabilities]:
    """Build a complete three-inventory fixture with misses and a known distortion."""
    if min(n_signal, n_data, n_background) < 8:
        raise ValueError("fixture inventories must each contain at least eight rows")
    rng = np.random.default_rng(seed)
    latent_truth = rng.normal(size=n_signal)
    pass_truth = np.ones(n_signal, dtype=bool)
    pass_truth[: max(1, n_signal // 50)] = False
    reco_probability = 1.0 / (1.0 + np.exp(-(0.3 + 0.6 * latent_truth)))
    pass_reco = (rng.random(n_signal) < reco_probability) & pass_truth
    # Guarantee both selected events and native misses for small deterministic fixtures.
    pass_reco[pass_truth] = pass_reco[pass_truth]
    truth_indices = np.flatnonzero(pass_truth)
    pass_reco[truth_indices[0]] = True
    pass_reco[truth_indices[1]] = False
    latent_reco = latent_truth + rng.normal(0.0, 0.25, n_signal)
    reco = _batch(
        rng,
        latent_reco,
        max_tokens,
        "synthetic_signal_reco",
        valid_rows=pass_reco,
    )
    truth = _batch(
        rng,
        latent_truth,
        max_tokens,
        "synthetic_signal_truth",
        valid_rows=pass_truth,
    )
    latent_data = rng.normal(0.25, 1.0, n_data)
    # Conditional shift is deliberately not a one-dimensional marginal tilt.
    data = _batch(
        rng,
        latent_data,
        max_tokens,
        "synthetic_data_conditional_distortion",
        distortion=0.32,
    )
    latent_bkg = rng.normal(-0.8, 1.2, n_background)
    background = _batch(
        rng,
        latent_bkg,
        max_tokens,
        "synthetic_literal_background",
        distortion=-0.12,
    )
    w_truth = np.exp(rng.normal(0.0, 0.55, n_signal)).astype(np.float64)
    w_reco = (w_truth * np.exp(rng.normal(0.0, 0.12, n_signal))).astype(np.float64)
    data_raw = np.exp(rng.normal(0.0, 0.25, n_data)).astype(np.float64)
    bkg_raw = np.exp(rng.normal(-0.3, 0.35, n_background)).astype(np.float64)
    # A deterministic fixture analogue of a receipt-bound Stay-Positive target:
    # negative provenance is retained, while only nonnegative refined weights
    # reach the density-ratio trainer.
    bkg_refined = bkg_raw * np.clip(
        0.30 + 0.15 * (latent_bkg > 0), 0.0, 1.0
    )
    refined = np.concatenate((data_raw, bkg_refined))
    raw_signed = np.concatenate((data_raw, -bkg_raw))
    event_key = np.column_stack(
        (
            np.full(n_signal, 999001, dtype=np.int64),
            np.zeros(n_signal, dtype=np.int64),
            np.arange(n_signal, dtype=np.int64),
        )
    )
    dataset = CanonicalDataset(
        signal=SignalInventory(
            reco=reco,
            truth=truth,
            pass_reco=pass_reco,
            pass_truth=pass_truth,
            w_reco=w_reco,
            w_truth=w_truth,
            identity_hash="",
            event_key=event_key,
        ),
        measured=MeasuredInventory(
            data=data,
            background=background,
            refined_weights=refined,
            raw_signed_weights=raw_signed,
            data_identity_hash="",
            background_identity_hash="",
            target_receipt={
                "kind": "synthetic_stay_positive_fixture_v1",
                "canonical_nonnegative": True,
                "ordering": "data_then_literal_background",
                "negative_weight_provenance_retained": True,
                "not_publication_gate2": True,
                "seed": seed,
            },
        ),
        estimator_fingerprint="pet2-synthetic-three-inventory-v1",
        schema={
            "source": "portable_synthetic",
            "seed": seed,
            "known_conditional_distortion": {
                "data_positive_latent_log_energy_shift": 0.32,
                "data_positive_latent_mu_pt_shift": 0.32,
            },
            "object_types": "reconstructed fixture labels, never truth-derived on reco side",
            "overflow": "pre-truncation energy-conserving aggregate",
            "g2_validation_claim": False,
        },
        pot_scale=1.0,
        pot_scale_source="synthetic_fixture_explicit_unity",
    ).validated()
    capabilities = FeatureCapabilities(
        real_object_types=True,
        object_type_source="synthetic reconstructed object generator",
        detector_view=True,
        muon_token=True,
        muon_token_coordinates_audited=True,
        overflow_aggregate=True,
        audited_globals=GLOBAL_NAMES,
        unsupported_reasons={
            "dedx": "not part of the portable fixture",
            "michel": "not part of the portable fixture",
            "photon_label": "not required for the generic typed-object test",
        },
        source_kind="portable_synthetic",
    )
    return dataset, capabilities


def make_known_ratio_closure_dataset(
    n_signal: int = 256,
    n_background: int = 40,
    max_tokens: int = 7,
    seed: int = 424242,
) -> ConditionalClosureFixture:
    """Build aligned pseudo-data with a known conditional event-weight ratio.

    Pseudo-data rows are exact copies of selected simulated reco rows.  Their
    nonnegative target mass is ``w_reco * r(reco)`` with an analytic ratio that
    depends jointly on muon and recoil observables.  Literal backgrounds remain
    present with signed negative provenance but zero Stay-Positive training
    mass, so they cannot alter the known target measure.
    """
    dataset, capabilities = make_synthetic_dataset(
        n_signal=n_signal,
        n_data=max(16, n_signal // 2),
        n_background=n_background,
        max_tokens=max_tokens,
        seed=seed,
    )
    signal = dataset.signal
    selected = np.flatnonzero(signal.pass_reco)
    if selected.size < 12:
        raise ValueError("known-ratio fixture requires at least twelve selected reco rows")
    reco = signal.reco
    token_energy = np.sum(
        np.where(reco.token_mask, reco.continuous[:, :, 0], 0.0), axis=1
    )
    mu_pt = reco.globals[:, reco.global_names.index("mu_pt")]
    selected_energy = np.log1p(token_energy[selected])
    selected_mu = np.log(np.maximum(mu_pt[selected], 1e-8))
    z_energy = (selected_energy - selected_energy.mean()) / max(
        float(selected_energy.std()), 1e-8
    )
    z_mu = (selected_mu - selected_mu.mean()) / max(float(selected_mu.std()), 1e-8)
    log_ratio = 0.42 * z_mu + 0.38 * z_mu * np.tanh(z_energy)
    analytic_ratio = np.exp(np.clip(log_ratio, -2.0, 2.0))
    # Unit weighted mean removes an overall normalization tilt while preserving
    # the conditional shape.  Uneven MC event masses remain explicit.
    analytic_ratio /= np.average(analytic_ratio, weights=signal.w_reco[selected])

    data = signal.reco.subset(selected)
    data = replace(
        data,
        row_index=np.arange(selected.size, dtype=np.int64),
        provenance="synthetic_aligned_known_ratio_pseudodata",
    ).validated()
    background = dataset.measured.background
    data_weights = signal.w_reco[selected] * analytic_ratio
    background_abs = np.abs(
        dataset.measured.raw_signed_weights[-background.n_rows :]
    )
    refined = np.concatenate(
        (data_weights.astype(np.float64), np.zeros(background.n_rows, dtype=np.float64))
    )
    raw_signed = np.concatenate((data_weights, -background_abs))
    measured = MeasuredInventory(
        data=data,
        background=background,
        refined_weights=refined,
        raw_signed_weights=raw_signed,
        data_identity_hash="",
        background_identity_hash="",
        target_receipt={
            "kind": "synthetic_aligned_analytic_ratio_v1",
            "canonical_nonnegative": True,
            "ordering": "aligned_data_then_literal_background",
            "negative_weight_provenance_retained": True,
            "background_refined_training_mass": 0.0,
            "analytic_formula": (
                "exp(0.42*z(log(mu_pt)) + "
                "0.38*z(log(mu_pt))*tanh(z(log1p(token_energy))))"
            ),
            "normalization": "w_reco-weighted selected-event mean ratio equals one",
            "seed": seed,
            "not_publication_gate2": True,
        },
        aligned_signal_row=np.concatenate(
            (selected.astype(np.int64), -np.ones(background.n_rows, dtype=np.int64))
        ),
    ).validated()
    expected = np.ones(n_signal, dtype=np.float64)
    expected[selected] = analytic_ratio
    q3_index = signal.truth.global_names.index("q3")
    truth_valid = signal.pass_truth
    tail_threshold = float(
        np.quantile(signal.truth.globals[truth_valid, q3_index], 0.8)
    )
    tail = truth_valid & (signal.truth.globals[:, q3_index] >= tail_threshold)
    closure_dataset = replace(
        dataset,
        measured=measured,
        estimator_fingerprint="pet2-synthetic-known-ratio-closure-v1",
        schema={
            **dict(dataset.schema),
            "source": "portable_synthetic_known_ratio_closure",
            "pseudo_data_alignment": "exact selected signal reco rows",
            "known_conditional_ratio": measured.target_receipt["analytic_formula"],
            "background_training_role": (
                "literal aligned rows retained; zero refined mass with signed provenance"
            ),
        },
    ).validated()
    return ConditionalClosureFixture(
        dataset=closure_dataset,
        capabilities=capabilities,
        data_to_signal_row=selected.astype(np.int64),
        analytic_reco_ratio=analytic_ratio.astype(np.float64),
        expected_truth_ratio=expected,
        declared_tail_mask=tail,
        specification={
            "evidence_class": "portable_synthetic_known_ratio",
            "fixture_seed": seed,
            "selected_rows": int(selected.size),
            "native_misses": int(np.sum(signal.pass_truth & ~signal.pass_reco)),
            "ratio_quantiles": np.quantile(
                analytic_ratio, [0, 0.01, 0.5, 0.99, 1]
            ).tolist(),
            "tail_definition": {
                "feature": "truth_q3",
                "quantile": 0.8,
                "threshold": tail_threshold,
                "count": int(tail.sum()),
            },
            "g2_validation_claim": False,
        },
    )


def analytic_gaussian_problem(
    points: np.ndarray,
    *,
    mean0: float = -0.5,
    mean1: float = 0.75,
    sigma: float = 1.2,
    mass0: float = 3.0,
    mass1: float = 11.0,
) -> dict[str, Any]:
    """Known balanced logit and physical ratio for unequal weighted masses."""
    x = np.asarray(points, dtype=np.float64)
    log_p1_over_p0 = (
        -0.5 * np.square((x - mean1) / sigma)
        + 0.5 * np.square((x - mean0) / sigma)
    )
    physical_ratio = np.exp(log_p1_over_p0) * mass1 / mass0
    return {
        "points": x,
        "balanced_logit": log_p1_over_p0,
        "physical_ratio": physical_ratio,
        "mass0": mass0,
        "mass1": mass1,
    }
