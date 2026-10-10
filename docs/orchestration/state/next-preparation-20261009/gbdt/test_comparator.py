"""Synthetic controls for the comparator and for the saved-output design arithmetic.

Each discriminant is shown to fire on the defect it targets and stay silent on the clean case.
Run from the repository root:

    python3 -m pytest -q docs/orchestration/state/next-preparation-20261009/gbdt/test_comparator.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"gbdt_lane_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


comparator = _load("comparator")
reductions = _load("reduce_saved_outputs")


def _smearing(n_truth: int, n_reco: int, width: float, efficiency: float = 0.8) -> np.ndarray:
    centers_t = (np.arange(n_truth) + 0.5) / n_truth
    centers_r = (np.arange(n_reco) + 0.5) / n_reco
    kernel = np.exp(-0.5 * ((centers_r[:, None] - centers_t[None, :]) / width) ** 2)
    return efficiency * kernel / kernel.sum(axis=0, keepdims=True)


def _fixture():
    rng = np.random.default_rng(20261009)
    response = _smearing(12, 18, 0.06)
    prior = 1e4 * (1.0 + 0.5 * np.sin(np.linspace(0, 3, 12)))
    truth = prior * (1.0 + 0.3 * np.cos(np.linspace(0, 6, 12)))
    return rng, response, prior, truth


def test_exact_ibu_misfit_is_monotone_and_falls():
    _, response, prior, truth = _fixture()
    data = response @ truth
    trace = comparator.ibu(response, data, prior, 400)
    misfit = [comparator.chi2_fold(response, t, truth) for t in trace]
    assert all(b <= a * (1 + 1e-9) for a, b in zip(misfit, misfit[1:]))
    assert misfit[-1] < 1e-3 * misfit[0]


def test_approximate_step_stalls_at_detectable_misfit():
    """Negative control: an iteration whose response is wrong cannot reach the data."""
    _, response, prior, truth = _fixture()
    data = response @ truth
    wrong = _smearing(12, 18, 0.09)  # the 'classifier' smooths more than the detector does
    trace = comparator.ibu(wrong, data, prior, 400)
    misfit = [comparator.chi2_fold(response, t, truth) for t in trace]
    exact = comparator.ibu(response, data, prior, 400)
    exact_misfit = comparator.chi2_fold(response, exact[-1], truth)
    assert misfit[-1] > 100 * exact_misfit
    assert abs(misfit[-1] - misfit[-50]) < 0.05 * misfit[-1]  # stalled, not converging


def test_null_space_functional_is_flagged_weak():
    _, response, prior, truth = _fixture()
    degenerate = response.copy()
    degenerate[:, 7] = degenerate[:, 6]  # cells 6 and 7 indistinguishable at reco
    maps = np.zeros((3, 12))
    maps[0, 6], maps[0, 7] = 1.0, -1.0  # their difference: unidentifiable
    maps[1, 6] = maps[1, 7] = 1.0  # their sum: identifiable
    maps[2, 0] = 1.0
    width = comparator.cr_width(degenerate, truth, maps)
    assert np.isinf(width.sigma[0]) and width.null_fraction[0] > 0.99
    assert np.isfinite(width.sigma[1]) and np.isfinite(width.sigma[2])
    clean = comparator.cr_width(response, truth, maps)
    assert np.all(np.isfinite(clean.sigma))


def test_invisible_share_separates_weak_from_visible_residual():
    _, response, _, truth = _fixture()
    values, vectors = np.linalg.eigh(comparator.fisher(response, truth))
    weakest, strongest = vectors[:, 0], vectors[:, -1]
    amplitude = 500.0  # chi-square contributions: weakest mode < 1, strongest mode > 1
    assert values[0] * amplitude**2 < 1.0 < values[-1] * amplitude**2
    maps = np.eye(12)
    weak = comparator.invisible_share(response, truth, amplitude * weakest, maps)
    strong = comparator.invisible_share(response, truth, amplitude * strongest, maps)
    hit = np.abs(maps @ weakest) > 1e-3
    assert np.allclose(weak[hit], 1.0) and np.allclose(strong[np.abs(maps @ strongest) > 1e-3], 0.0)


def test_classify_labels_both_directions():
    labels = comparator.classify(
        np.array([0.10, 0.10, 0.10]), np.array([0.02, 0.11, 0.06]), np.array([0.01, 0.2, 0.05])
    )
    assert [x["iteration"] for x in labels] == ["approximation-dominated", "iteration-faithful", "mixed"]
    assert [x["identifiability"] for x in labels] == [
        "identified-at-target", "weakly-identified", "intermediate"]


def test_linear_prior_pull_identity():
    """Documents the algebra behind E5 (an identity of an affine estimator, not a lane-code test)."""
    rng, response, prior, truth = _fixture()
    a = np.linalg.pinv(response) * 0.6  # a deliberately regularized linear unfolding
    kernel = a @ response
    est = lambda y, p: a @ y + (np.eye(12) - kernel) @ p
    data_truth = prior * (1 + 0.05 * rng.standard_normal(12))
    y_data = response @ data_truth
    closure = est(response @ truth, prior) - truth
    shift = est(y_data, truth) - est(y_data, prior)
    assert np.allclose(closure, -shift)


def test_recovered_fraction_detects_cross_talk():
    """Documents the E3 reading (no lane code): cross-talk gives rho < 0, a diagonal kernel never."""
    kernel = np.array([[0.6, 0.5], [0.5, 0.6]])
    departure = np.array([1.0, -0.4])
    rho = (kernel @ departure) / departure
    assert rho[1] < 0 < rho[0]
    assert np.all((np.diag([0.7, 0.4]) @ departure) / departure >= 0)


def test_lower_bound_design_against_brute_force():
    design = reductions.lower_bound_design(4, 0.05, 0.63, 0.682689492137, 0.80)
    n, h = design["N"], design["min_hits"]
    alpha = 0.05 / 4
    assert stats.beta.ppf(alpha, h, n - h + 1) >= 0.63 > stats.beta.ppf(alpha, h - 1, n - h + 2)
    assert 1 - 4 * stats.binom.cdf(h - 1, n, 0.682689492137) >= 0.80
    smaller = n - 1
    h2 = reductions.min_hits_for_lower(smaller, alpha, 0.63)
    assert 1 - 4 * stats.binom.cdf(h2 - 1, smaller, 0.682689492137) < 0.80


def _labels(spec):
    return [{"iteration": i, "identifiability": d} for i, d in spec]


def test_branch_outcome_reaches_every_branch():
    weak, ident = "weakly-identified", "identified-at-target"
    approx, faithful = "approximation-dominated", "iteration-faithful"
    r = np.full(4, 0.10)
    none = np.zeros(4, bool)
    c = comparator.branch_outcome(_labels([(faithful, weak)] * 3 + [(approx, ident)]), r,
                                  np.full(4, 0.09), none)
    a = comparator.branch_outcome(_labels([(approx, ident)] * 3 + [(faithful, weak)]), r,
                                  np.full(4, 0.09), none)
    b = comparator.branch_outcome(_labels([(faithful, ident)] * 4), r, np.full(4, 0.01), none)
    not_b = comparator.branch_outcome(_labels([(faithful, ident)] * 4), r, np.full(4, 0.09), none)
    mixed = comparator.branch_outcome(
        _labels([(faithful, weak), (approx, ident), (faithful, ident), ("mixed", "intermediate")]),
        r, np.array([0.09, 0.09, 0.01, 0.09]), none)
    assert (c["branch"], a["branch"], b["branch"], not_b["branch"], mixed["branch"]) == (
        "C", "A", "B", "mixed", "mixed")
    small = comparator.branch_outcome(_labels([(approx, ident)] * 4), np.full(4, 0.01),
                                      np.zeros(4), none)
    assert small["branch"] == "no-eligible-functional"
    flagged = comparator.branch_outcome(_labels([(approx, ident)] * 4), r, np.zeros(4),
                                        np.array([True, True, True, False]))
    assert flagged["n_eligible"] == 1 and flagged["branch"] == "A"


def test_missed_concentration_both_directions():
    rng = np.random.default_rng(7)
    missed = rng.uniform(0, 0.5, 300)
    concentrated = np.where(missed >= np.quantile(missed, 2 / 3), 0.1, 0.005)
    unrelated = rng.normal(0, 0.05, 300)
    assert comparator.missed_concentration(concentrated, missed)["bookkeeping_implicated"]
    out = comparator.missed_concentration(unrelated, missed)
    assert not out["bookkeeping_implicated"] and 0.2 < out["share_top_tercile"] < 0.5
