"""Train-only fitted preprocessing for reco/data/background and truth views."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from .contracts import TokenBatch
from .utils import fingerprint


@dataclass(frozen=True)
class FittedPreprocessor:
    token_mean: np.ndarray
    token_scale: np.ndarray
    token_count: np.ndarray
    global_mean: np.ndarray
    global_scale: np.ndarray
    global_count: int
    global_names: tuple[str, ...]
    fit_rows_hash: str
    units: dict[str, str]

    def payload(self) -> dict[str, Any]:
        payload = {
            "token_mean": self.token_mean.tolist(),
            "token_scale": self.token_scale.tolist(),
            "token_count": self.token_count.tolist(),
            "global_mean": self.global_mean.tolist(),
            "global_scale": self.global_scale.tolist(),
            "global_count": self.global_count,
            "global_names": list(self.global_names),
            "fit_rows_hash": self.fit_rows_hash,
            "units": dict(self.units),
        }
        payload["fingerprint"] = fingerprint(payload)
        return payload

    def transform(self, batch: TokenBatch) -> TokenBatch:
        batch = batch.validated()
        if batch.global_names != self.global_names:
            raise ValueError("preprocessor global schema mismatch")
        if batch.continuous.shape[2] != self.token_mean.size:
            raise ValueError("preprocessor token dimension mismatch")
        continuous = (batch.continuous - self.token_mean) / self.token_scale
        continuous = continuous.astype(np.float32)
        continuous[~batch.token_mask] = 0.0
        globals_ = ((batch.globals - self.global_mean) / self.global_scale).astype(np.float32)
        muon = batch.muon_continuous
        if muon is not None:
            muon = ((muon - self.token_mean) / self.token_scale).astype(np.float32)
            muon[~batch.muon_present] = 0.0
        return replace(
            batch,
            continuous=continuous,
            globals=globals_,
            muon_continuous=muon,
            provenance=f"{batch.provenance}|normalized",
        ).validated()


def fit_preprocessor(
    batch: TokenBatch,
    fit_rows: np.ndarray,
    *,
    units: dict[str, str] | None = None,
    epsilon: float = 1e-6,
) -> FittedPreprocessor:
    batch = batch.validated()
    fit_rows = np.asarray(fit_rows, dtype=bool)
    if fit_rows.shape != (batch.n_rows,) or not np.any(fit_rows):
        raise ValueError("fit_rows must select at least one aligned row")
    selected_mask = batch.token_mask & fit_rows[:, None]
    if not np.any(selected_mask):
        raise ValueError("normalizer fit has no real tokens")
    token_values = batch.continuous[selected_mask]
    token_mean = token_values.mean(axis=0, dtype=np.float64)
    token_scale = token_values.std(axis=0, dtype=np.float64)
    if not np.all(np.isfinite(token_mean)) or not np.all(np.isfinite(token_scale)):
        raise ValueError("nonfinite token normalization statistics")
    token_scale = np.where(token_scale < epsilon, 1.0, token_scale)
    global_values = batch.globals[fit_rows]
    if not np.all(np.isfinite(global_values)):
        raise ValueError("nonfinite globals in normalization fit")
    global_mean = global_values.mean(axis=0, dtype=np.float64)
    global_scale = global_values.std(axis=0, dtype=np.float64)
    global_scale = np.where(global_scale < epsilon, 1.0, global_scale)
    from .utils import array_hash

    return FittedPreprocessor(
        token_mean=token_mean.astype(np.float32),
        token_scale=token_scale.astype(np.float32),
        token_count=np.full(token_mean.shape, int(token_values.shape[0]), dtype=np.int64),
        global_mean=global_mean.astype(np.float32),
        global_scale=global_scale.astype(np.float32),
        global_count=int(global_values.shape[0]),
        global_names=batch.global_names,
        fit_rows_hash=array_hash(batch.row_index[fit_rows]),
        units=units or {"continuous": "adapter-declared", "globals": "adapter-declared"},
    )


def preprocessor_from_payload(payload: dict[str, Any]) -> FittedPreprocessor:
    expected = payload.get("fingerprint")
    clean = {key: value for key, value in payload.items() if key != "fingerprint"}
    if expected != fingerprint(clean):
        raise ValueError("preprocessor fingerprint mismatch")
    return FittedPreprocessor(
        token_mean=np.asarray(clean["token_mean"], dtype=np.float32),
        token_scale=np.asarray(clean["token_scale"], dtype=np.float32),
        token_count=np.asarray(clean["token_count"], dtype=np.int64),
        global_mean=np.asarray(clean["global_mean"], dtype=np.float32),
        global_scale=np.asarray(clean["global_scale"], dtype=np.float32),
        global_count=int(clean["global_count"]),
        global_names=tuple(clean["global_names"]),
        fit_rows_hash=str(clean["fit_rows_hash"]),
        units=dict(clean["units"]),
    )
