"""Feature arms: hashing, leakage structure, standardization (no TensorFlow)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import feature_arms as fa  # noqa: E402


def _blocks(n_mc=50, n_pd=30):
    rng = np.random.default_rng(0)
    return {"pdata_reco_evt": rng.normal(size=(n_pd, 3)).astype(np.float32),
            "mc_reco_evt": rng.normal(size=(n_mc, 3)).astype(np.float32),
            "mc_gen_evt": rng.normal(size=(n_mc, 2)).astype(np.float32),
            "pdata_rows": np.arange(100, 100 + n_pd), "mc_rows": np.arange(n_mc),
            "pdata_pass_reco": np.ones(n_pd, bool), "mc_pass_reco": np.arange(n_mc) % 3 != 0,
            "mc_pass_gen": np.ones(n_mc, bool)}


def _reader(truth_offset=0.0):
    def read(which, column, rows):
        base = np.asarray(rows, dtype=float) * (2.0 if which == "reco" else 3.0)
        return base + (truth_offset if which == "truth" else 0.0)
    return read


def test_baseline_is_the_identity():
    blocks = _blocks()
    out = fa.apply(fa.get("baseline"), "ours", blocks, _reader(), np)
    for key in ("pdata_reco_evt", "mc_reco_evt", "mc_gen_evt"):
        assert np.array_equal(out[key], blocks[key])


def test_truth_never_reaches_step_one():
    """Perturbing every truth scalar leaves both step-1 event blocks bit-identical."""
    arm = fa.get("reco_and_truth_eavail")
    a = fa.apply(arm, "ours", _blocks(), _reader(0.0), np)
    b = fa.apply(arm, "ours", _blocks(), _reader(1e3), np)
    assert np.array_equal(a["mc_reco_evt"], b["mc_reco_evt"])
    assert np.array_equal(a["pdata_reco_evt"], b["pdata_reco_evt"])
    assert a["mc_reco_evt"].shape[1] == 4 and a["mc_gen_evt"].shape[1] == 3


def test_standardized_on_passing_mc_rows_and_zero_elsewhere():
    blocks = _blocks()
    out = fa.apply(fa.get("reco_eavail"), "ours", blocks, _reader(), np)
    col = out["mc_reco_evt"][:, -1]
    passing = blocks["mc_pass_reco"]
    assert abs(col[passing].mean()) < 1e-5 and abs(col[passing].std() - 1) < 1e-4
    assert np.all(col[~passing] == 0)


def test_step1_arms_refuse_his_arm_and_hashes_differ():
    with pytest.raises(ValueError):
        fa.apply(fa.get("reco_eavail"), "theirs", _blocks(), _reader(), np)
    hashes = {name: arm.content_hash() for name, arm in fa.REGISTRY.items()}
    assert len(set(hashes.values())) == len(hashes)
