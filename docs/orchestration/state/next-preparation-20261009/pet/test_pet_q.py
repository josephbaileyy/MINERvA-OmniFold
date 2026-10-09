"""Synthetic tests and negative controls for the lane's reductions (no training, no new runs).

    python -m pytest test_pet_q.py -q
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design_cost as dc  # noqa: E402
import reduce_saved as rs  # noqa: E402

B = rs.B


def synth(R, sD, sP, sT, bias=0.0, nb=3, seed=0, R1=None):
    """members (R, B, nb), targets (R, nb), singles (R1, nb) under the components model."""
    rng = np.random.default_rng(seed)
    D = rng.normal(0, sD, (R, nb))
    mem = bias + D[:, None, :] + rng.normal(0, sP, (R, B, nb)) + rng.normal(0, sT, (R, B, nb))
    R1 = R1 or R
    single = bias + rng.normal(0, sD, (R1, nb)) + rng.normal(0, sT, (R1, nb))
    return mem, np.zeros((R, nb)), single


def test_components_recover_known_values():
    sD, sP, sT = 0.5, 1.0, 1.5
    mem, _, single = synth(20000, sD, sP, sT, seed=1)
    c = rs.components(mem, single)
    assert np.allclose(c["W"], sP ** 2 + sT ** 2, rtol=0.03)
    assert np.allclose(c["sD2"], sD ** 2, atol=0.03)
    assert np.allclose(c["sT2"], sT ** 2, rtol=0.05)
    assert np.allclose(c["sP2"], sP ** 2, rtol=0.1)


def test_section9_interval_overcovers_when_internal_randomness_dominates():
    """Positive control of the diagnosis: with s_D small and s_T, s_P large, the section-9 interval
    (sd x sqrt(1 + 1/B)) over-covers, and the components variance W_r/B + s_D^2 is close to nominal."""
    mem, t, single = synth(6000, 0.2, 1.0, 1.0, seed=2)
    c9 = rs.coverage(mem, t)
    assert c9["0.68"]["pooled"] > 0.90
    var = mem.var(axis=1, ddof=1) / B + rs.components(mem, single)["sD2"][None, :]
    cc = rs.coverage(mem, t, var)
    assert abs(cc["0.68"]["pooled"] - 0.68) < 0.03


def test_bias_defeats_a_variance_correct_interval():
    """Negative control: the same variance-correct interval under-covers once a bias of 1 sd of the
    member-mean error is added, and the misses become one-sided."""
    mem, t, single = synth(6000, 0.2, 1.0, 1.0, bias=0.0, seed=3)
    sde = math.sqrt(0.04 + 2.0 / B)
    mem_b = mem + sde
    var = mem.var(axis=1, ddof=1) / B + 0.04
    cc = rs.coverage(mem_b, t, var)
    assert cc["0.68"]["pooled"] < 0.55
    assert cc["0.68"]["miss_high_pooled"] > 10 * cc["0.68"]["miss_low_pooled"]


def test_coverage_function_is_monotone_in_half_width():
    """Checks the coverage FUNCTION (same centre, scaled half-width). The futility rule's scope, "no wider
    than section 9 with the same centre", is a statement of scope, not something this test proves."""
    mem, t, _ = synth(2000, 0.3, 1.0, 1.0, bias=0.8, seed=4)
    base = mem.var(axis=1, ddof=1) * (1 + 1 / B)
    covs = [rs.coverage(mem, t, base * f)["0.68"]["pooled"] for f in (0.25, 0.5, 1.0, 2.0)]
    assert covs == sorted(covs)


def test_loader_refuses_a_receipt_digest_mismatch(monkeypatch):
    real = rs.completeness

    def tampered(tsv):
        out = real(tsv)
        k = sorted(out)[0]
        out[k] = "0" * 64
        return out
    monkeypatch.setattr(rs, "completeness", tampered)
    with pytest.raises(SystemExit, match="receipt digest differs"):
        rs.load_s5(rs.Ledger())


def test_loader_refuses_a_missing_member(monkeypatch):
    real = rs.completeness

    def dropped(tsv):
        out = real(tsv)
        out.pop(sorted(out)[0])
        return out
    monkeypatch.setattr(rs, "completeness", dropped)
    with pytest.raises(SystemExit, match="members"):
        rs.load_s5(rs.Ledger())


def test_s4f_receipt_check_refuses_a_mismatch():
    look1 = rs.completeness(rs.FD / "freeze/COMPLETENESS-look1.tsv")
    rs.check_s4f_receipts([0, 1], look1)
    look1["S4F-H2S1T24K5-FB1"] = "0" * 64
    with pytest.raises(SystemExit, match="S4F FB1"):
        rs.check_s4f_receipts([0, 1], look1)


def test_completeness_parser_refuses_an_incomplete_row(tmp_path):
    p = tmp_path / "c.tsv"
    p.write_text("# manifest\trow\tstatus\treceipt_sha256\nm\tS5-X-FB0-b1\tRUNNING\tabc\n")
    with pytest.raises(SystemExit, match="RUNNING"):
        rs.completeness(p)


def test_bias_tolerance_hits_the_bound():
    t = dc.bias_tolerance()
    assert abs(dc.normal_coverage(t["0.68"]["max_abs_bias_over_sd"], 0.68) - 0.63) < 1e-9
    assert abs(dc.normal_coverage(t["0.95"]["max_abs_bias_over_sd"], 0.95) - 0.92) < 1e-9


def test_price_reserve_is_t_over_0p8_not_1p2_t():
    p = dc.price(100, 1.0)
    assert p["a100h_total_with_reserve"] == pytest.approx(100 * 1.05 / 0.8)
    assert p["a100h_total_with_reserve"] != pytest.approx(100 * 1.05 * 1.2)


def test_calibrated_futility_size_at_the_boundary():
    """The calibrated critical count holds the no-go rate at p = 0.63 (the boundary) to <= 0.0125 per case
    and look, re-measured on fresh simulation; and has power > 0.9 at E = 8 for the study-scale 0.26."""
    rng = np.random.default_rng(5)
    for E in (4, 8):
        r = dc.calibrated_futility(E, 2.23, rng)
        fresh = (dc.sim_hits(E, 0.63, 2.23, rng, 200000) <= r["k_crit"]).mean()
        assert fresh <= 0.0125 + 0.0015
    assert dc.calibrated_futility(8, 2.23, rng)["power"]["0.26"] > 0.9


def test_wilson_futility_is_anticonservative_at_the_boundary():
    """Records why the Wilson version was replaced: its boundary rate exceeds the nominal 0.0125."""
    rng = np.random.default_rng(6)
    assert dc.futility_power(4, 0.63, 2.23, rng) > 0.0125


@pytest.mark.parametrize("which", ["reductions", "design"])
def test_independent_checker_rejects_a_perturbed_number(tmp_path, which):
    red = json.loads((HERE / "results/saved_reductions.json").read_text())
    des = json.loads((HERE / "results/design_cost.json").read_text())
    if which == "reductions":
        red["histograms"]["eavail"]["components"]["W"][3] *= 1.001
    else:
        des["costs"]["E1_look1"]["data_2M_forecast"]["value"]["a100h_total_with_reserve"] *= 1.01
    (tmp_path / "r.json").write_text(json.dumps(red))
    (tmp_path / "d.json").write_text(json.dumps(des))
    out = subprocess.run([sys.executable, str(HERE / "check_independent.py"), str(tmp_path / "r.json"),
                          str(tmp_path / "d.json")], capture_output=True, text=True)
    assert out.returncode == 1 and "DISAGREE" in out.stdout
