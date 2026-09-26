"""Synthetic fixtures for the analysis tests: run directories and score documents whose truth is
known by construction (simulation-free; nothing here reads an inventory)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import score_design as sd  # noqa: E402

N_ROWS_INVENTORY = 50_000


def tilt(eavail: np.ndarray, a: float = 0.35) -> np.ndarray:
    z = np.clip((eavail - 1.4653696417808533) / 2.6336711198091507, -3, 3)
    return np.exp(a * z)


def unit_mean(w: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return w / w[mask].mean()


def make_features(path: Path, seed: int = 1) -> dict[str, np.ndarray]:
    """An `extract_row_features.py`-style npz over rows 0..N_ROWS_INVENTORY-1."""
    rng = np.random.default_rng(seed)
    rows = np.arange(N_ROWS_INVENTORY, dtype=np.int64)
    cols = {c: rng.integers(0, 5, N_ROWS_INVENTORY).astype(np.int8)
            for c, _ in sd.SPECIES.values()}
    np.savez(path, rows=rows, **cols)
    return cols


def make_run(path: Path, *, case: str = "D1_p0.350", same_events: bool = False,
             amplitude: float = 0.35, n: int = 20_000, seed: int = 0,
             pushes: dict[int, np.ndarray] | None = None, push_kind: str = "oracle",
             bootstrap: bool = False, features: dict[str, np.ndarray] | None = None) -> dict:
    """A predecessor-format run directory. The truth-level distortion is the D1-style tilt of
    `amplitude` on E_avail, or a proton-multiplicity weight 1.3^N for D4c cases. With
    `same_events` the pseudodata ARE the prior events (then the oracle push reproduces the
    target exactly)."""
    rng = np.random.default_rng(seed)
    path.mkdir(parents=True, exist_ok=True)
    perm = rng.permutation(N_ROWS_INVENTORY)
    prior_rows = np.sort(perm[:n])
    pseudo_rows = prior_rows.copy() if same_events else np.sort(perm[n:2 * n])

    def side(rows):
        r = np.random.default_rng(rows[0] + 17)
        m = rows.size
        truth = np.column_stack([r.gamma(2, 0.3, m), r.gamma(3, 1.5, m),
                                 r.gamma(1.2, 1.2, m), r.gamma(2, 1.2, m)])
        truth[::997, 3] = np.nan                               # some non-finite q3
        pass_truth = r.random(m) > 0.01
        region = r.choice([0, 1, 2, 3, -1], size=m, p=[0.25, 0.1, 0.3, 0.3, 0.05]).astype(np.int8)
        return {"truth": truth, "pass_truth": pass_truth, "pass_reco": r.random(m) > 0.5,
                "w_truth": r.uniform(0.5, 1.5, m), "w_reco": r.uniform(0.5, 1.5, m),
                "region": region, "reco_eavail": truth[:, 2] * r.uniform(0.8, 1.2, m)}

    A, B = side(pseudo_rows), side(prior_rows)
    if same_events:
        A = {k: v.copy() for k, v in B.items()}

    def weight(s, rows):
        if case.startswith("D4c"):
            np_ = features["tr_n_p"][rows] if features is not None else np.zeros(rows.size)
            return np.power(1.3, np_.astype(float))
        if case == "null":
            return np.ones(rows.size)
        return tilt(s["truth"][:, 2], amplitude)

    keep_a = A["pass_truth"] & np.isfinite(A["truth"][:, 2])
    keep_b = B["pass_truth"] & np.isfinite(B["truth"][:, 2])
    dist = unit_mean(weight(A, pseudo_rows), keep_a)
    oracle = unit_mean(weight(B, prior_rows), keep_b)
    arrays = {"pseudo_rows": pseudo_rows, "prior_rows": prior_rows}
    for pre, s in (("pseudo", A), ("prior", B)):
        arrays.update({f"{pre}_pass_truth": s["pass_truth"], f"{pre}_pass_reco": s["pass_reco"],
                       f"{pre}_truth": s["truth"], f"{pre}_reco_eavail": s["reco_eavail"],
                       f"{pre}_w_truth": s["w_truth"], f"{pre}_w_reco": s["w_reco"],
                       f"{pre}_region": s["region"]})
    arrays["pseudo_distortion"] = dist
    arrays["prior_oracle"] = oracle
    if bootstrap:
        k = rng.poisson(1.0, n).astype(np.float64)
        # as runner/design_inputs.apply_bootstrap writes a member: w x k, and w kept aside
        arrays["prior_w_truth_unresampled"] = arrays["prior_w_truth"]
        arrays["prior_w_truth"] = arrays["prior_w_truth"] * k
        arrays["prior_bootstrap_weight"] = k
        arrays["pseudo_bootstrap_weight"] = rng.poisson(1.0, n).astype(np.float64)
    np.savez(path / "replicate_arrays.npz", **arrays)
    (path / "iterations").mkdir(exist_ok=True)
    if pushes is None:
        pushes = {1: np.ones(n), 2: oracle if push_kind == "oracle" else np.ones(n)}
    for k, push in pushes.items():
        np.savez(path / "iterations" / f"iter{k - 1:02d}.npz", push=push, pull=push)
    (path / "run_identity.json").write_text(json.dumps({
        "distortion": case, "prior_rows_sha256": f"p{seed}", "pseudo_rows_sha256": f"a{seed}"}))
    (path / "receipt.json").write_text(json.dumps({"complete": True, "config_hash": "x"}))
    return {"arrays": arrays, "oracle": oracle, "dist": dist}


@pytest.fixture
def features(tmp_path):
    p = tmp_path / "rf.npz"
    cols = make_features(p)
    return p, cols
