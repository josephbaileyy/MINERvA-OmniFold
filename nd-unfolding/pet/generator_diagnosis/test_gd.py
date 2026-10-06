"""The diagnosis reductions on synthetic inputs, in both directions (they must separate a perfect unfolding from
a null one, and a wrong-direction move from a right one)."""
from __future__ import annotations

import numpy as np
import pytest

import gd_analyze as gd


def test_movement_perfect_null_and_half():
    p = np.array([0.2, 0.3, 0.5])
    t = np.array([0.3, 0.3, 0.4])
    assert gd.movement(p, t, t)["m"] == pytest.approx(1.0)
    assert gd.movement(p, t, t)["orth"] == pytest.approx(0.0, abs=1e-12)
    assert gd.movement(p, p, t)["m"] == pytest.approx(0.0, abs=1e-12)
    assert gd.movement(p, (p + t) / 2, t)["m"] == pytest.approx(0.5)


def test_movement_detects_wrong_direction():
    p = np.array([0.2, 0.3, 0.5])
    t = np.array([0.3, 0.3, 0.4])                       # injected: +0.1, 0, -0.1
    u = np.array([0.2, 0.4, 0.4])                       # moved:     0, +0.1, -0.1 (partly orthogonal)
    r = gd.movement(p, u, t)
    assert 0 < r["m"] < 1 and r["orth"] > 0.5


def test_weight_agreement_full_none_and_half_strength():
    rng = np.random.default_rng(1)
    o = np.exp(rng.normal(0, 0.5, 5000))
    mask, base = np.ones(o.size, bool), np.ones(o.size)
    assert gd.weight_agreement(o, o, mask, base)["slope"] == pytest.approx(1.0)
    assert gd.weight_agreement(np.sqrt(o), o, mask, base)["slope"] == pytest.approx(0.5)
    flat = gd.weight_agreement(np.exp(rng.normal(0, 0.01, o.size)), o, mask, base)
    assert abs(flat["slope"]) < 0.05


def test_d5_bins_cover_and_overflow():
    b = gd.D5Bins(gd.D5T)
    truth = np.array([[0.1, 3.0, 0.5, 1.0], [99.0, 3.0, 0.5, 1.0], [0.1, np.nan, 0.5, 1.0]])
    c = b.codes(truth)
    assert 0 <= c["d5_3d"][0] < b.n
    assert c["d5_3d"][1] == b.n and c["d5_3d"][2] == b.n          # out of range / non-finite -> overflow
    assert c["pt"][1] == c["_n"]["pt"] - 1 and c["ppar"][2] == c["_n"]["ppar"] - 1
