"""Tests for the Phase-B1 scalar references: toys with known answers, and bit-equality with the
historical scorer.

Run: ``python -m pytest nd-unfolding/pet/improvement_campaign/phase_b/scalar -q`` (the classifier
tests skip where the installed sklearn predates weighted MLP / HGB validation-set support).
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import binned_unfolding as bu  # noqa: E402
import features  # noqa: E402
import scalar_common as scm  # noqa: E402
import scalar_omnifold as so  # noqa: E402

MODS = scm.historical_modules()


def _diagonal_toy(acceptance, t0, target):
    """One accepted and one missed MC 'event' per truth bin, reco bin == truth bin."""
    a, t0, T = (np.asarray(x, dtype=np.float64) for x in (acceptance, t0, target))
    nb = a.size
    truth_bin = np.concatenate([np.arange(nb), np.arange(nb)])
    s1 = np.concatenate([np.ones(nb, bool), np.zeros(nb, bool)])
    w = np.concatenate([a * t0, (1 - a) * t0])
    keep = w > 0
    return dict(truth_bin=truth_bin[keep], s1=s1[keep], w=w[keep],
                data_bin=np.arange(nb)[a > 0], w_data=(a * T)[a > 0])


def _truth_spectrum(push, w, truth_bin, nb):
    return np.bincount(truth_bin, weights=w * push, minlength=nb)


def test_carry_misses_diagonal_reproduces_the_historical_reference_ceiling():
    """Zero smearing + rate-matched pseudo-data: the ABSOLUTE truth spectrum after k iterations is
    T - (1-a)^k (T - t0), so its unnormalized L1 recovery IS reference_calibration.ceiling(a,
    |injected|, k), for every k. The historical score renormalizes the spectra first, and the
    total drifts (sum t^k != sum T), so the SCORED recovery departs from the ceiling even in this
    ideal case -- the reference model does not account for renormalization."""
    a = np.array([0.9, 0.6, 0.3, 0.05, 0.0])
    t0 = np.array([1.0, 2.0, 3.0, 1.0, 1.0])
    T = np.array([1.5, 2.5, 2.0, 1.5, 0.5])          # same total: a rate-preserving tilt
    toy = _diagonal_toy(a, t0, T)
    total = bu.ENGINE_NORMALIZATION * (a * T).sum() / (a * t0).sum()
    rc, rae = MODS["rc"], MODS["rae"]
    departures = []
    for step in bu.binned_omnifold(
            reco_bin_mc=toy["truth_bin"], truth_bin_mc=toy["truth_bin"],
            pass_reco_mc=toy["s1"], pass_gen_mc=np.ones_like(toy["s1"]),
            w_truth_mc=toy["w"], w_reco_mc=toy["w"], reco_bin_data=toy["data_bin"],
            w_data=toy["w_data"], n_reco_bins=5, n_truth_bins=5, iterations=12,
            data_total=total):
        k = step["iteration"]
        got = _truth_spectrum(step["push"], toy["w"], toy["truth_bin"], 5)
        got = got * t0.sum() / toy["w"].sum()      # undo the engine's constant rescale
        law = T - (1 - a) ** k * (T - t0)
        np.testing.assert_allclose(got, law, rtol=0, atol=1e-12)
        unnormalized = 1.0 - np.abs(T - got).sum() / np.abs(T - t0).sum()
        ceiling = rc.ceiling(a, np.abs(T - t0), k)
        assert abs(unnormalized - ceiling) < 1e-12
        departures.append(rae.recovery(t0, got, T)["recovery"] - ceiling)
    assert max(abs(x) for x in departures) > 1e-3


def test_engine_normalization_breaks_the_law_when_acceptance_tracks_the_tilt():
    """Pseudo-data normalized to the prior's ACCEPTED total (the historical driver) departs from
    the reference law exactly when the tilt changes the accepted fraction."""
    a = np.array([0.9, 0.2])
    t0 = np.array([1.0, 1.0])
    T = np.array([0.5, 1.5])                          # moves mass to the low-acceptance bin
    toy = _diagonal_toy(a, t0, T)
    step = next(bu.binned_omnifold(
        reco_bin_mc=toy["truth_bin"], truth_bin_mc=toy["truth_bin"], pass_reco_mc=toy["s1"],
        pass_gen_mc=np.ones_like(toy["s1"]), w_truth_mc=toy["w"], w_reco_mc=toy["w"],
        reco_bin_data=toy["data_bin"], w_data=toy["w_data"], n_reco_bins=2, n_truth_bins=2,
        iterations=1))
    got = _truth_spectrum(step["push"], toy["w"], toy["truth_bin"], 2)
    law = T - (1 - a) * (T - t0)
    assert np.abs(got / got.sum() - law / law.sum()).max() > 1e-3


def test_efficiency_corrected_diagonal_is_exact_in_one_iteration():
    a = np.array([0.9, 0.6, 0.3, 0.05])
    t0 = np.array([1.0, 2.0, 3.0, 1.0])
    T = np.array([1.5, 2.5, 2.0, 1.0])
    toy = _diagonal_toy(a, t0, T)
    step = next(bu.binned_omnifold(
        reco_bin_mc=toy["truth_bin"], truth_bin_mc=toy["truth_bin"], pass_reco_mc=toy["s1"],
        pass_gen_mc=np.ones_like(toy["s1"]), w_truth_mc=toy["w"], w_reco_mc=toy["w"],
        reco_bin_data=toy["data_bin"], w_data=toy["w_data"], n_reco_bins=4, n_truth_bins=4,
        iterations=1, mode=bu.MODE_EFFICIENCY_CORRECTED))
    got = _truth_spectrum(step["push"], toy["w"], toy["truth_bin"], 4)
    np.testing.assert_allclose(got / got.sum(), T / T.sum(), rtol=0, atol=1e-12)


def test_full_acceptance_smearing_converges_to_the_truth_in_both_modes():
    R = np.array([[0.8, 0.15, 0.0], [0.2, 0.7, 0.25], [0.0, 0.15, 0.75]])  # P(reco i | truth j)
    t0 = np.array([1.0, 1.0, 1.0])
    T = np.array([0.6, 1.1, 1.3])
    ii, jj = np.meshgrid(np.arange(3), np.arange(3), indexing="ij")
    w = (R * t0[None, :]).ravel()
    reco_bin, truth_bin = ii.ravel(), jj.ravel()
    data = R @ T
    finals = {}
    for mode in bu.MODES:
        *_, last = bu.binned_omnifold(
            reco_bin_mc=reco_bin, truth_bin_mc=truth_bin, pass_reco_mc=np.ones(9, bool),
            pass_gen_mc=np.ones(9, bool), w_truth_mc=w, w_reco_mc=w,
            reco_bin_data=np.arange(3), w_data=data, n_reco_bins=3, n_truth_bins=3,
            iterations=4000, mode=mode)
        got = _truth_spectrum(last["push"], w, truth_bin, 3)
        np.testing.assert_allclose(got / got.sum(), T / T.sum(), atol=1e-6)
        finals[mode] = last["push"]
    np.testing.assert_allclose(finals[bu.MODE_CARRY_MISSES], finals[bu.MODE_EFFICIENCY_CORRECTED],
                               atol=1e-12)


def test_data_in_a_bin_without_prior_is_reported_as_lost():
    step = next(bu.binned_omnifold(
        reco_bin_mc=np.array([0, 0]), truth_bin_mc=np.array([0, 1]),
        pass_reco_mc=np.array([True, True]), pass_gen_mc=np.array([True, True]),
        w_truth_mc=np.ones(2), w_reco_mc=np.ones(2), reco_bin_data=np.array([0, 1]),
        w_data=np.array([3.0, 1.0]), n_reco_bins=2, n_truth_bins=2, iterations=1))
    assert step["lost_data"] == pytest.approx(0.25 * bu.ENGINE_NORMALIZATION)


def _random_toy(rng, n=4000, n_truth=6, n_reco=5):
    truth = rng.integers(0, n_truth, n)
    reco = np.clip(truth * n_reco // n_truth + rng.integers(-1, 2, n), 0, n_reco - 1)
    pg = rng.random(n) > 0.05
    pr = rng.random(n) < (0.2 + 0.6 * truth / n_truth)
    w_t = rng.uniform(0.5, 1.5, n)
    w_r = w_t * rng.uniform(0.93, 1.0, n)
    nd = 3000
    t_d = rng.integers(0, n_truth, nd)
    keep = rng.random(nd) < (0.2 + 0.6 * t_d / n_truth)
    r_d = np.clip(t_d * n_reco // n_truth + rng.integers(-1, 2, nd), 0, n_reco - 1)[keep]
    w_d = rng.uniform(0.5, 2.0, keep.sum()) * (1 + t_d[keep])
    return truth, reco, pg, pr & pg, w_t, w_r, r_d, w_d


def test_classifier_loop_with_a_binned_oracle_is_the_binned_unfolding():
    """The engine-mirroring loop and binned_omnifold are the same algorithm: plug the Bayes-optimal
    binned classifier into the loop and every pull and push agrees at every iteration."""
    rng = np.random.default_rng(3)
    truth, reco, pg, s1, w_t, w_r, r_d, w_d = _random_toy(rng)
    expected = list(bu.binned_omnifold(
        reco_bin_mc=reco, truth_bin_mc=truth, pass_reco_mc=s1, pass_gen_mc=pg, w_truth_mc=w_t,
        w_reco_mc=w_r, reco_bin_data=r_d, w_data=w_d, n_reco_bins=5, n_truth_bins=6,
        iterations=6))
    seen = []
    so.run_scalar_omnifold(
        X_reco_mc=reco[:, None].astype(float), X_reco_data=r_d[:, None].astype(float),
        X_gen_mc=truth[:, None].astype(float), pass_reco_mc=s1, pass_gen_mc=pg,
        w_truth_mc=w_t, w_reco_mc=w_r, w_data=w_d,
        make_step1=lambda k: so.BinnedOracleRatio(5), make_step2=lambda k: so.BinnedOracleRatio(6),
        iterations=6, seed=0, callback=lambda rec: seen.append(
            (rec["pull"].copy(), rec["push"].copy())))
    assert len(seen) == len(expected) == 6
    for (pull, push), ref in zip(seen, expected):
        np.testing.assert_allclose(pull, ref["pull"], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(push, ref["push"], rtol=1e-10, atol=1e-12)


def test_score_push_is_bit_identical_to_the_historical_score_run():
    sc, cr = MODS["sc"], MODS["cr"]
    rng = np.random.default_rng(11)
    names = [n for n, _lo, _hi in cr.SAFEGUARD_REGIONS]
    na, nb_all = 700, 610
    selector = np.ones(nb_all, bool)
    selector[rng.choice(nb_all, 10, replace=False)] = False
    nb = int(selector.sum())
    endpoint = sc.Endpoint(
        eavail_a=rng.exponential(0.6, na), w_truth_a=rng.uniform(0.5, 2, na),
        tilt_a=rng.uniform(0.7, 1.4, na), region_a=rng.choice(names, na),
        eavail_b=rng.exponential(0.6, nb), w_truth_b=rng.uniform(0.5, 2, nb),
        region_b=rng.choice(names, nb), prior_selector=selector)
    weights = rng.uniform(0.6, 1.6, nb_all)
    scoreable = ["low_acceptance", "moderate", "good"]
    hist = sc.score_run(sc.Run(arm="ours", stage="final", seed=127, weights=weights), endpoint,
                        scoreable_regions=scoreable)
    mine = scm.score_push(endpoint, weights, scoreable)
    assert mine["recovery"] == hist["recovery"]
    assert mine["aggregate"]["overshoot_projection"] == hist["overshoot_projection"]
    for name in scoreable:
        assert mine["recovery_by_region"][name] == hist["recovery_by_region"][name]
        assert mine["regions"][name]["residual_l1"] == hist["region_detail"][name]["residual_l1"]


def test_reference_curve_uses_the_historical_functions():
    a = np.array([0.0, 0.03, 0.3, 0.8])
    d = np.array([0.1, 0.2, 0.3, 0.4])
    curve = scm.reference_curve(a, d, [1, 3])
    assert curve["aggregate"][1] == MODS["rc"].ceiling(a, d, 3)


def test_reco_input_sets_read_no_truth_column():
    for name in features.RECO_SETS:
        features.assert_reco_only(name)
        assert all(key != "truth" for key, _c, _l in features.RECO_SETS[name])


def test_historical_modules_match_the_campaign_commit():
    record = scm.verify_historical_sources()
    assert record["all_match"]


def _gaussian_tilt_problem(n, rng):
    x = rng.normal(size=n)
    X = np.concatenate([x, x])[:, None]
    y = np.concatenate([np.zeros(n), np.ones(n)])
    w = np.concatenate([np.ones(n), np.exp(0.5 * x - 0.125)])
    return X, y, w


@pytest.mark.skipif("X_val" not in inspect.signature(
    __import__("sklearn.ensemble", fromlist=["x"]).HistGradientBoostingClassifier.fit).parameters,
    reason="installed sklearn has no HGB validation-set argument")
def test_hgb_ratio_learns_a_known_log_ratio():
    rng = np.random.default_rng(5)
    X, y, w = _gaussian_tilt_problem(100_000, rng)
    Xv, yv, wv = _gaussian_tilt_problem(25_000, rng)
    clf = so.HGBRatio(seed=1)
    clf.fit(X, y, w, Xv, yv, wv)
    grid = np.linspace(-1.5, 1.5, 61)[:, None]
    err = np.abs(clf.logit(grid) - (0.5 * grid[:, 0] - 0.125))
    assert err.mean() < 0.08


@pytest.mark.skipif("sample_weight" not in inspect.signature(
    __import__("sklearn.neural_network", fromlist=["x"]).MLPClassifier.partial_fit).parameters,
    reason="installed sklearn has no weighted MLP partial_fit")
def test_mlp_ratio_learns_a_known_log_ratio():
    rng = np.random.default_rng(6)
    X, y, w = _gaussian_tilt_problem(60_000, rng)
    Xv, yv, wv = _gaussian_tilt_problem(15_000, rng)
    clf = so.MLPRatio(seed=1, max_epochs=12)
    info = clf.fit(X, y, w, Xv, yv, wv)
    grid = np.linspace(-1.5, 1.5, 61)[:, None]
    err = np.abs(clf.logit(grid) - (0.5 * grid[:, 0] - 0.125))
    assert err.mean() < 0.08, info
