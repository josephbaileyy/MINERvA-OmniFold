"""inference.py and sizing.py against scipy / closed forms, and the sequential rule."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

import inference as inf
import sizing


def test_per_bound_alpha():
    assert inf.per_bound_alpha(1) == 0.05
    assert inf.per_bound_alpha(3) == pytest.approx(0.05 / 3)
    assert inf.per_bound_alpha(3, 2) == pytest.approx(0.05 / 6)
    with pytest.raises(ValueError):
        inf.per_bound_alpha(0)
    with pytest.raises(ValueError):
        inf.per_bound_alpha(2, 3)


@pytest.mark.parametrize("m", [1, 3, 5])
def test_bonferroni_t_bounds_match_scipy(m):
    rng = np.random.default_rng(m)
    x = rng.normal(0.6, 0.05, 24)
    a = 0.05 / m
    tb = inf.t_bounds(x, a)
    lo, hi = stats.t.interval(1 - 2 * a, x.size - 1, loc=x.mean(), scale=stats.sem(x))
    assert tb.lb == pytest.approx(lo, abs=1e-13) and tb.ub == pytest.approx(hi, abs=1e-13)
    # the LB is the value at which the one-sided t test is exactly at level a
    p = stats.ttest_1samp(x, tb.lb, alternative="greater").pvalue
    assert p == pytest.approx(a, rel=1e-9)


def test_t_bounds_single_value_has_no_interval():
    tb = inf.t_bounds([0.5], 0.05)
    assert tb.lb is None and tb.ub is None and tb.mean == 0.5


@pytest.mark.parametrize("x,n", [(0, 8), (0, 200), (3, 40), (40, 40), (17, 96)])
@pytest.mark.parametrize("alpha", [0.05, 0.05 / 3])
def test_clopper_pearson_matches_scipy_exact(x, n, alpha):
    lo, hi = inf.clopper_pearson(x, n, alpha)
    ci = stats.binomtest(x, n).proportion_ci(confidence_level=1 - 2 * alpha, method="exact")
    assert lo == pytest.approx(ci.low, abs=1e-12) and hi == pytest.approx(ci.high, abs=1e-12)
    if x == 0:
        assert hi == pytest.approx(1 - alpha ** (1 / n), abs=1e-12)


def test_clopper_pearson_b1_zero_failures_needs_29_units():
    # with 0 failures the 95 % UB is <= 0.10 only from n = 29 units: zero observed is not zero
    assert inf.clopper_pearson(0, 28, 0.05)[1] > 0.10
    assert inf.clopper_pearson(0, 29, 0.05)[1] <= 0.10


def test_cluster_bootstrap_bounds():
    rng = np.random.default_rng(0)
    hits = (rng.random((120, 7)) < 0.95).astype(float)
    b = inf.cluster_bootstrap_bounds(hits, 0.05)
    assert b["point"] == pytest.approx(hits.mean())
    assert b["lb"] < b["point"] < b["ub"]
    # ~ binomial se for independent cells
    se = math.sqrt(0.95 * 0.05 / hits.size)
    assert b["point"] - b["lb"] == pytest.approx(1.645 * se, rel=0.25)
    with_nan = hits.copy()
    with_nan[0, 0] = np.nan
    assert inf.cluster_bootstrap_bounds(with_nan, 0.05)["n_cells"] == hits.size - 1


def test_cost_ratio_delta_method():
    large = [2.0, 2.2, 1.8, 2.1]
    small = [0.5, 0.55, 0.45, 0.5]
    r = inf.cost_ratio_lb(large, small, 0.05, 6, 6)
    assert r["ratio"] == pytest.approx(np.mean(large) / np.mean(small))
    se = math.hypot(np.std(large, ddof=1) / 2 / np.mean(large),
                    np.std(small, ddof=1) / 2 / np.mean(small))
    assert r["lb"] == pytest.approx(r["ratio"] * math.exp(-stats.norm.ppf(0.95) * se))
    const = inf.cost_ratio_lb([2, 2], [1, 1], 0.05)
    assert const["lb"] == pytest.approx(2.0)
    with pytest.raises(ValueError):
        inf.cost_ratio_lb([1.0], [1.0, 1.0], 0.05)


def P(op, thr, kind, est=None, lb=None, ub=None):
    return inf.Part("x", op, thr, kind, est, lb, ub)


def test_sequential_rule_pass_fail_continue():
    # straddling LB at look 1 -> CONTINUE; same at look 2 -> FAIL
    straddle = [P(">=", 0.5, "bound", 0.52, 0.48, 0.56)]
    assert inf.decide("U", straddle, 1, 2).verdict == inf.CONTINUE
    assert inf.decide("U", straddle, 2, 2).verdict == inf.FAIL
    # wholly below -> decisive FAIL at look 1
    assert inf.decide("U", [P(">=", 0.5, "bound", 0.4, 0.38, 0.45)], 1, 2).verdict == inf.FAIL
    assert inf.decide("U", [P(">=", 0.5, "bound", 0.6, 0.55, 0.65)], 1, 2).verdict == inf.PASS
    # a fixed-sample (single-look) straddle fails
    assert inf.decide("U", straddle, 1, 1).verdict == inf.FAIL
    # pure point rules are decided at look 1
    assert inf.decide("U", [P(">=", 0.5, "point", 0.49)], 1, 2).verdict == inf.FAIL
    # strict > at the threshold fails
    assert inf.decide("U", [P(">", 0.1, "bound", 0.2, 0.1, 0.3)], 2, 2).verdict == inf.FAIL
    # <= parts: point above threshold with LB above -> decisive
    assert inf.decide("C", [P("<=", 0.99, "point", 0.995, 0.991, 0.999)], 1, 2).verdict == inf.FAIL
    assert inf.decide("C", [P("<=", 0.99, "point", 0.995, 0.98, 0.999)], 1, 2).verdict == inf.CONTINUE
    with pytest.raises(ValueError):
        inf.decide("U", straddle, 3, 2)


def test_ucb80_sd():
    assert inf.ucb80_sd(1.0, 7) == pytest.approx(math.sqrt(7 / stats.chi2.ppf(0.2, 7)))
    assert inf.ucb80_sd(1.0, 7) > 1.0


# ------------------------------------------------------------------------------------------- #
# sizing
# ------------------------------------------------------------------------------------------- #
def test_smallest_n_is_exact():
    a = 0.05 / 6
    n = sizing.smallest_n(0.0, -0.02, 0.03, a)
    assert sizing.power(np.array([n]), 0.0, -0.02, 0.03, a)[0] >= 0.8
    assert sizing.power(np.array([n - 1]), 0.0, -0.02, 0.03, a)[0] < 0.8


def test_smallest_n_agrees_with_predecessor_search():
    confirm = Path(__file__).resolve().parents[2] / "improvement_campaign" / "confirm"
    sys.path.insert(0, str(confirm))
    import analyze_confirm
    for sigma in (0.01, 0.02, 0.035):
        assert sizing.smallest_n(0.0, -0.02, sigma, 0.05 / 3) == \
            analyze_confirm.n_for_power(sigma, 0.02, 0.05 / 3)


def test_sizing_floor_cap_and_unattainable():
    rng = np.random.default_rng(0)
    easy = {"id": "NI_E0", "values": rng.normal(0.01, 0.005, 6).tolist(), "margin": -0.02}
    r = sizing.size([easy])
    assert r["n_F"] == 24 and not r["capped"] and r["contrasts"]["NI_E0"]["status"] == "OK"
    hard = {"id": "NI_E4", "values": (np.array([0.0, 0.04, -0.04, 0.02, -0.02, 0.0])).tolist(),
            "margin": -0.02}
    r = sizing.size([easy, hard])
    assert r["alpha_one_sided_per_contrast"] == pytest.approx(0.05 / 2 / 2)
    assert r["contrasts"]["NI_E4"]["status"] in ("EXCEEDS_CAP", "OK")
    if r["contrasts"]["NI_E4"]["status"] == "EXCEEDS_CAP":
        assert r["n_F"] == 60 and r["capped"] and r["n_required_uncapped"] > 60
    bad = {"id": "U1", "values": [0.50, 0.52, 0.51, 0.49], "margin": 0.5559785255}
    r = sizing.size([easy, bad])
    assert r["contrasts"]["U1"]["status"] == "UNATTAINABLE"
    assert r["n_F"] == 60 and r["capped"] and r["n_required_uncapped"] is None
    assert "U1" in r["binding_contrasts"]


def test_sizing_single_look_needs_fewer():
    v = {"id": "NI", "values": [0.0, 0.03, -0.03, 0.01, -0.01, 0.02, -0.02, 0.0], "margin": -0.02}
    r = sizing.size([v])
    c = r["contrasts"]["NI"]
    assert c["n_for_power_if_single_look"] <= c["n_for_power"]
