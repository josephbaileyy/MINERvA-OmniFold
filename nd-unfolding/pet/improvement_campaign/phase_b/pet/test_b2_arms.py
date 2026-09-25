"""Tests of the B2 input arms (numpy only; no TensorFlow)."""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b2_arms  # noqa: E402


def test_step1_refuses_truth_sources() -> None:
    bad = dataclasses.replace(b2_arms.get("reco_summaries"), step1_reco_scalars=("true_eavail",))
    with pytest.raises(ValueError):
        b2_arms.assert_step1_reco_only(bad)
    bad2 = dataclasses.replace(b2_arms.get("reco_summaries"), step1_cloud_summaries=("gen_sumE",))
    with pytest.raises(ValueError):
        b2_arms.assert_step1_reco_only(bad2)
    for arm in b2_arms.REGISTRY.values():
        b2_arms.assert_step1_reco_only(arm)


def test_step1_reads_only_reco() -> None:
    """Every step-1 value comes through read_reco or the reco cloud, never read_truth."""
    n = 50
    rng = np.random.default_rng(0)

    def cloud():
        c = rng.random((n, 12, 5)).astype(np.float32)
        c[np.arange(12)[None, :] >= rng.integers(1, 13, n)[:, None]] = 0.0   # padding
        return c

    blocks = {
        "pdata_reco": cloud(),
        "pdata_reco_evt": np.zeros((n, 13), np.float32),
        "mc_reco": cloud(),
        "mc_reco_evt": np.zeros((n, 13), np.float32),
        "mc_gen": np.zeros((n, 12, 8), np.float32), "mc_gen_evt": np.zeros((n, 2), np.float32),
        "coord_gen": (5, 6, 7), "pdata_rows": np.arange(n), "mc_rows": np.arange(n),
        "pdata_pass_reco": np.ones(n, bool), "mc_pass_reco": np.ones(n, bool),
        "mc_pass_gen": np.ones(n, bool)}

    def read_truth(col, rows):
        raise AssertionError("step 1 read a truth column")

    out = b2_arms.apply(b2_arms.get("reco_summaries"), blocks,
                        lambda col, rows: rng.random(len(rows)), read_truth, np)
    assert out["mc_reco_evt"].shape == (n, 17)
    assert out["record"]["step1"] == ["reco_scalars:eavail", "reco_scalars:q3",
                                      "reco_cloud:stored_sumE", "reco_cloud:stored_n"]
    assert out["mc_gen"] is blocks["mc_gen"]


def test_pdg_categories_and_onehot() -> None:
    codes = np.array([[2212, 2112, 211, -211, 111, 22, 321, 130, -2212, 3122, 11,
                       1000060120, 221, 0]], dtype=np.float32)
    idx = b2_arms.pdg_category_index(np, codes)
    names = [c for c, _ in b2_arms.PDG_CATEGORIES]
    got = [names[i] if i >= 0 else None for i in idx[0]]
    assert got == ["proton", "neutron", "pi_plus", "pi_minus", "pi_zero", "photon",
                   "kaon_charged", "kaon_neutral", "antinucleon", "hyperon", "electron",
                   "nucleus", "other", None]
    n_tok = codes.shape[1]
    cloud = np.zeros((1, n_tok, 8), np.float32)
    cloud[0, :, 0] = np.where(codes[0] != 0, 1.0, 0.0)
    cloud[0, :, 4] = codes[0]
    cloud[0, :, 5:] = 0.5
    out, coord, census = b2_arms.pdg_onehot_cloud(np, cloud, (5, 6, 7))
    assert out.shape == (1, n_tok, 7 + len(names))
    assert coord == (4, 5, 6)
    assert np.all(out[0, :, 4:7] == cloud[0, :, 5:8])
    assert np.all(out[0, :-1, 7:].sum(axis=1) == 1) and out[0, -1, 7:].sum() == 0
    assert census["other_codes"] == {221: 1}


def test_truth_scalars_median_fill_and_standardization() -> None:
    n = 20
    vals = np.arange(n, dtype=np.float64)
    vals[3] = np.nan
    blocks = {
        "pdata_reco": np.zeros((n, 12, 5), np.float32), "pdata_reco_evt": np.zeros((n, 1)),
        "mc_reco": np.zeros((n, 12, 5), np.float32), "mc_reco_evt": np.zeros((n, 1)),
        "mc_gen": np.zeros((n, 12, 8), np.float32), "mc_gen_evt": np.zeros((n, 2), np.float32),
        "coord_gen": (5, 6, 7), "pdata_rows": np.arange(n), "mc_rows": np.arange(n),
        "pdata_pass_reco": np.ones(n, bool), "mc_pass_reco": np.ones(n, bool),
        "mc_pass_gen": np.ones(n, bool),
        "extra_gen": {"half_a": (np.zeros((n, 12, 8), np.float32), np.zeros((n, 2), np.float32),
                                 np.arange(n), np.ones(n, bool))}}
    arm = dataclasses.replace(b2_arms.get("truthglobals"), step2_truth_scalars=("q3",))
    out = b2_arms.apply(arm, blocks, lambda c, r: None, lambda c, r: vals[r], np)
    assert out["record"]["nonfinite_filled"]["truth_scalars:q3"] == {"mc": 1, "half_a": 1}
    z = out["mc_gen_evt"][:, 2]
    assert np.isfinite(z).all() and abs(z.mean()) < 1e-6
    assert np.array_equal(out["extra_gen"]["half_a"][1][:, 2], z)


def test_hash_distinguishes_arms_and_is_stable() -> None:
    hashes = {a.content_hash() for a in b2_arms.REGISTRY.values()}
    assert len(hashes) == len(b2_arms.REGISTRY)
    assert b2_arms.get("baseline").content_hash() == b2_arms.get("baseline").content_hash()
