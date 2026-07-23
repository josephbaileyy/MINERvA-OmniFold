"""NumPy-only tensor and inventory contracts for the PET2 experiment."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

import numpy as np

from .utils import array_hash, fingerprint

PAD_CATEGORY = 0


def _as_array(value: Any, dtype: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=dtype)
    if array.ndim == 0:
        raise ValueError(f"{name} must not be scalar")
    return array


def _finite(array: np.ndarray, name: str) -> None:
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains NaN or infinity")


def _weights(value: Any, n: int, name: str) -> np.ndarray:
    array = _as_array(value, np.float64, name)
    if array.shape != (n,):
        raise ValueError(f"{name} shape {array.shape} != ({n},)")
    _finite(array, name)
    if np.any(array < 0):
        raise ValueError(f"{name} contains negative training weights")
    return array


@dataclass(frozen=True)
class TokenBatch:
    """One aligned token/global inventory with an explicit boolean mask."""

    continuous: np.ndarray
    coords: np.ndarray
    token_mask: np.ndarray
    type_id: np.ndarray
    view_id: np.ndarray
    globals: np.ndarray
    row_index: np.ndarray
    global_names: tuple[str, ...]
    provenance: str
    overflow_energy: np.ndarray | None = None
    muon_continuous: np.ndarray | None = None
    muon_coords: np.ndarray | None = None
    muon_present: np.ndarray | None = None

    def validated(
        self,
        *,
        max_type: int | None = None,
        max_view: int | None = None,
    ) -> "TokenBatch":
        continuous = _as_array(self.continuous, np.float32, "continuous")
        coords = _as_array(self.coords, np.float32, "coords")
        mask = _as_array(self.token_mask, bool, "token_mask")
        type_id = _as_array(self.type_id, np.int64, "type_id")
        view_id = _as_array(self.view_id, np.int64, "view_id")
        globals_ = _as_array(self.globals, np.float32, "globals")
        rows = _as_array(self.row_index, np.int64, "row_index")
        if continuous.ndim != 3:
            raise ValueError("continuous must have shape (N,P,F)")
        n, p, _ = continuous.shape
        if coords.ndim != 3 or coords.shape[:2] != (n, p):
            raise ValueError("coords must have shape (N,P,K) aligned with continuous")
        for name, value in (
            ("token_mask", mask),
            ("type_id", type_id),
            ("view_id", view_id),
        ):
            if value.shape != (n, p):
                raise ValueError(f"{name} shape {value.shape} != {(n, p)}")
        if globals_.shape != (n, len(self.global_names)):
            raise ValueError(
                f"globals shape {globals_.shape} != {(n, len(self.global_names))}"
            )
        if rows.shape != (n,) or len(np.unique(rows)) != n:
            raise ValueError("row_index must be unique with shape (N,)")
        _finite(continuous, "continuous")
        _finite(coords, "coords")
        _finite(globals_, "globals")
        if np.any(type_id < 0) or np.any(view_id < 0):
            raise ValueError("categorical IDs must be nonnegative")
        if np.any(type_id[mask] == PAD_CATEGORY):
            raise ValueError("real tokens must have type_id >= 1; category 0 is pad/unknown")
        if np.any(type_id[~mask] != PAD_CATEGORY):
            raise ValueError("padded tokens must have type_id == 0")
        if np.any(view_id[~mask] != PAD_CATEGORY):
            raise ValueError("padded tokens must have view_id == 0")
        if max_type is not None and np.any(type_id > max_type):
            raise ValueError(f"type_id exceeds configured vocabulary {max_type}")
        if max_view is not None and np.any(view_id > max_view):
            raise ValueError(f"view_id exceeds configured vocabulary {max_view}")
        # Pads are canonicalized instead of trusted.  This prevents arbitrary pad
        # values from entering a model even though attention masks them.
        continuous = continuous.copy()
        coords = coords.copy()
        continuous[~mask] = 0.0
        coords[~mask] = 0.0
        overflow = None
        if self.overflow_energy is not None:
            overflow = _as_array(self.overflow_energy, np.float64, "overflow_energy")
            if overflow.shape != (n,):
                raise ValueError("overflow_energy must have shape (N,)")
            _finite(overflow, "overflow_energy")
            if np.any(overflow < 0):
                raise ValueError("overflow_energy must be nonnegative")
        muon_cont = muon_coords = muon_present = None
        supplied = (
            self.muon_continuous is not None,
            self.muon_coords is not None,
            self.muon_present is not None,
        )
        if any(supplied) and not all(supplied):
            raise ValueError("muon token fields must be supplied together")
        if all(supplied):
            muon_cont = _as_array(self.muon_continuous, np.float32, "muon_continuous")
            muon_coords = _as_array(self.muon_coords, np.float32, "muon_coords")
            muon_present = _as_array(self.muon_present, bool, "muon_present")
            if muon_cont.ndim != 2 or muon_cont.shape[0] != n:
                raise ValueError("muon_continuous must have shape (N,F)")
            if muon_cont.shape[1] != continuous.shape[2]:
                raise ValueError("muon and cloud continuous dimensions must match")
            if muon_coords.shape != (n, coords.shape[2]):
                raise ValueError("muon_coords must have shape (N,K)")
            if muon_present.shape != (n,):
                raise ValueError("muon_present must have shape (N,)")
            _finite(muon_cont[muon_present], "real muon_continuous")
            _finite(muon_coords[muon_present], "real muon_coords")
            muon_cont = muon_cont.copy()
            muon_coords = muon_coords.copy()
            muon_cont[~muon_present] = 0.0
            muon_coords[~muon_present] = 0.0
        return replace(
            self,
            continuous=continuous,
            coords=coords,
            token_mask=mask,
            type_id=type_id,
            view_id=view_id,
            globals=globals_,
            row_index=rows,
            overflow_energy=overflow,
            muon_continuous=muon_cont,
            muon_coords=muon_coords,
            muon_present=muon_present,
        )

    @property
    def n_rows(self) -> int:
        return int(self.continuous.shape[0])

    def subset(self, selection: np.ndarray) -> "TokenBatch":
        selection = np.asarray(selection)
        kwargs: dict[str, Any] = {}
        for name in (
            "continuous",
            "coords",
            "token_mask",
            "type_id",
            "view_id",
            "globals",
            "row_index",
            "overflow_energy",
            "muon_continuous",
            "muon_coords",
            "muon_present",
        ):
            value = getattr(self, name)
            kwargs[name] = None if value is None else value[selection]
        kwargs["global_names"] = self.global_names
        kwargs["provenance"] = self.provenance
        return TokenBatch(**kwargs)

    def manifest(self) -> dict[str, Any]:
        type_values, type_counts = np.unique(self.type_id, return_counts=True)
        view_values, view_counts = np.unique(self.view_id, return_counts=True)
        return {
            "n_rows": self.n_rows,
            "n_tokens": int(self.continuous.shape[1]),
            "continuous_dim": int(self.continuous.shape[2]),
            "coord_dim": int(self.coords.shape[2]),
            "global_names": list(self.global_names),
            "provenance": self.provenance,
            "has_muon_token_seam": self.muon_present is not None,
            "has_overflow_energy": self.overflow_energy is not None,
            "real_token_count": int(self.token_mask.sum()),
            "padding_token_count": int((~self.token_mask).sum()),
            "all_padding_row_count": int(np.sum(~self.token_mask.any(axis=1))),
            "type_counts": {
                str(int(key)): int(value) for key, value in zip(type_values, type_counts)
            },
            "view_counts": {
                str(int(key)): int(value) for key, value in zip(view_values, view_counts)
            },
            "overflow": (
                None
                if self.overflow_energy is None
                else {
                    "row_count": int(np.count_nonzero(self.overflow_energy)),
                    "energy_sum": float(self.overflow_energy.sum()),
                    "energy_max": float(self.overflow_energy.max(initial=0.0)),
                }
            ),
            "row_hash": array_hash(self.row_index),
        }


def concatenate_batches(parts: Sequence[TokenBatch], provenance: str) -> TokenBatch:
    if not parts:
        raise ValueError("cannot concatenate an empty batch sequence")
    checked = [part.validated() for part in parts]
    reference = checked[0]
    fields = ("continuous", "coords", "token_mask", "type_id", "view_id", "globals")
    for part in checked[1:]:
        if part.continuous.shape[1:] != reference.continuous.shape[1:]:
            raise ValueError("token continuous schemas differ")
        if part.coords.shape[1:] != reference.coords.shape[1:]:
            raise ValueError("coordinate schemas differ")
        if part.global_names != reference.global_names:
            raise ValueError("global schemas differ")
        if (part.muon_present is None) != (reference.muon_present is None):
            raise ValueError("muon token seams differ")
    kwargs = {name: np.concatenate([getattr(p, name) for p in checked]) for name in fields}
    kwargs["row_index"] = np.arange(sum(p.n_rows for p in checked), dtype=np.int64)
    kwargs["global_names"] = reference.global_names
    kwargs["provenance"] = provenance
    for name in ("overflow_energy", "muon_continuous", "muon_coords", "muon_present"):
        values = [getattr(p, name) for p in checked]
        kwargs[name] = None if values[0] is None else np.concatenate(values)
    return TokenBatch(**kwargs).validated()


@dataclass(frozen=True)
class SignalInventory:
    reco: TokenBatch
    truth: TokenBatch
    pass_reco: np.ndarray
    pass_truth: np.ndarray
    w_reco: np.ndarray
    w_truth: np.ndarray
    identity_hash: str
    event_key: np.ndarray | None = None

    def validated(self) -> "SignalInventory":
        reco = self.reco.validated()
        truth = self.truth.validated()
        if reco.n_rows != truth.n_rows:
            raise ValueError("signal reco/truth row counts differ")
        n = reco.n_rows
        pass_reco = _as_array(self.pass_reco, bool, "pass_reco")
        pass_truth = _as_array(self.pass_truth, bool, "pass_truth")
        if pass_reco.shape != (n,) or pass_truth.shape != (n,):
            raise ValueError("signal pass masks must have shape (N,)")
        w_reco = _weights(self.w_reco, n, "w_reco")
        w_truth = _weights(self.w_truth, n, "w_truth")
        if not np.array_equal(reco.row_index, truth.row_index):
            raise ValueError("signal reco/truth row order differs")
        if np.any(reco.token_mask[~pass_reco]):
            raise ValueError("native reco misses must not contain real reco tokens")
        if np.any(pass_reco & ~pass_truth):
            raise ValueError(
                "pass_reco & !pass_truth signal fakes require an audited subtraction policy"
            )
        event_key = None
        if self.event_key is not None:
            event_key = _as_array(self.event_key, np.int64, "event_key")
            if event_key.shape[0] != n or event_key.ndim != 2:
                raise ValueError("event_key must have shape (N,K)")
            if len(np.unique(event_key, axis=0)) != n:
                raise ValueError("event_key contains duplicates")
        computed = array_hash(w_truth, pass_truth, reco.row_index)
        if self.identity_hash and self.identity_hash != computed:
            raise ValueError("signal identity hash mismatch")
        return replace(
            self,
            reco=reco,
            truth=truth,
            pass_reco=pass_reco,
            pass_truth=pass_truth,
            w_reco=w_reco,
            w_truth=w_truth,
            identity_hash=computed,
            event_key=event_key,
        )


@dataclass(frozen=True)
class MeasuredInventory:
    data: TokenBatch
    background: TokenBatch
    refined_weights: np.ndarray
    raw_signed_weights: np.ndarray
    data_identity_hash: str
    background_identity_hash: str
    target_receipt: Mapping[str, Any]
    aligned_signal_row: np.ndarray | None = None

    def validated(self) -> "MeasuredInventory":
        data = self.data.validated()
        background = self.background.validated()
        # This is the literal-alignment contract: both inventories must expose
        # the same detector-observable tensor schema.
        concatenate_batches((data, background), "data_then_literal_background")
        n = data.n_rows + background.n_rows
        refined = _weights(self.refined_weights, n, "refined_weights")
        signed = _as_array(self.raw_signed_weights, np.float64, "raw_signed_weights")
        if signed.shape != (n,) or not np.all(np.isfinite(signed)):
            raise ValueError("raw_signed_weights must be finite with shape (Ndata+Nbkg,)")
        if np.any(signed[: data.n_rows] < 0):
            raise ValueError("data raw target provenance must be nonnegative")
        if np.any(signed[data.n_rows :] > 0):
            raise ValueError("background raw target provenance must be nonpositive")
        if not self.target_receipt:
            raise ValueError("canonical Stay-Positive target receipt is required")
        aligned_signal_row = None
        if self.aligned_signal_row is not None:
            aligned_signal_row = _as_array(
                self.aligned_signal_row, np.int64, "aligned_signal_row"
            )
            if aligned_signal_row.shape != (n,) or np.any(aligned_signal_row < -1):
                raise ValueError(
                    "aligned_signal_row must have shape (Ndata+Nbkg,) with -1 for unpaired rows"
                )
            if np.any(aligned_signal_row[data.n_rows :] != -1):
                raise ValueError("literal backgrounds cannot claim signal-row alignment")
        data_hash = array_hash(data.row_index, data.continuous)
        bkg_hash = array_hash(background.row_index, background.continuous)
        if self.data_identity_hash and self.data_identity_hash != data_hash:
            raise ValueError("data identity hash mismatch")
        if self.background_identity_hash and self.background_identity_hash != bkg_hash:
            raise ValueError("background identity hash mismatch")
        return replace(
            self,
            data=data,
            background=background,
            refined_weights=refined,
            raw_signed_weights=signed,
            data_identity_hash=data_hash,
            background_identity_hash=bkg_hash,
            aligned_signal_row=aligned_signal_row,
        )

    def literal_target(self) -> TokenBatch:
        return concatenate_batches(
            (self.data, self.background), "data_then_literal_background"
        )


@dataclass(frozen=True)
class CanonicalDataset:
    signal: SignalInventory
    measured: MeasuredInventory
    estimator_fingerprint: str
    schema: Mapping[str, Any]
    pot_scale: float
    pot_scale_source: str

    def validated(self) -> "CanonicalDataset":
        signal = self.signal.validated()
        measured = self.measured.validated()
        target = measured.literal_target()
        if signal.reco.continuous.shape[1:] != target.continuous.shape[1:]:
            raise ValueError("signal reco and measured token schemas differ")
        if signal.reco.coords.shape[1:] != target.coords.shape[1:]:
            raise ValueError("signal reco and measured coordinate schemas differ")
        if signal.reco.global_names != target.global_names:
            raise ValueError("signal reco and measured global schemas differ")
        if measured.aligned_signal_row is not None:
            aligned = measured.aligned_signal_row
            if np.any(aligned >= signal.reco.n_rows):
                raise ValueError("measured aligned_signal_row exceeds signal inventory")
        if not self.estimator_fingerprint:
            raise ValueError("estimator_fingerprint is required")
        pot_scale = float(self.pot_scale)
        if not np.isfinite(pot_scale) or pot_scale <= 0:
            raise ValueError("dataset pot_scale must be finite and positive")
        if not self.pot_scale_source:
            raise ValueError("dataset pot_scale_source is required")
        return replace(self, signal=signal, measured=measured, pot_scale=pot_scale)

    def manifest(self) -> dict[str, Any]:
        valid = self.validated()
        payload = {
            "estimator_fingerprint": valid.estimator_fingerprint,
            "schema": dict(valid.schema),
            "pot_scale": valid.pot_scale,
            "pot_scale_source": valid.pot_scale_source,
            "signal_reco": valid.signal.reco.manifest(),
            "signal_truth": valid.signal.truth.manifest(),
            "measured_data": valid.measured.data.manifest(),
            "measured_background": valid.measured.background.manifest(),
            "signal_identity_hash": valid.signal.identity_hash,
            "data_identity_hash": valid.measured.data_identity_hash,
            "background_identity_hash": valid.measured.background_identity_hash,
            "target_receipt_fingerprint": fingerprint(valid.measured.target_receipt),
            "measured_signal_alignment": (
                None
                if valid.measured.aligned_signal_row is None
                else {
                    "aligned_count": int(
                        np.sum(valid.measured.aligned_signal_row >= 0)
                    ),
                    "sha256": array_hash(valid.measured.aligned_signal_row),
                }
            ),
        }
        payload["fingerprint"] = fingerprint(payload)
        return payload
