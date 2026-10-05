"""Tests for the fixed-truth 2D coverage toy design and scorer (no ROOT needed)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_coverage as sc  # noqa: E402
import toy_design as td  # noqa: E402

N_PT, N_PZ = 14, 16


def synthetic(n_toys=200, band_over_scatter=1.0, rho=0.5, seed=0, n_reported=205):
    """Toys with a known scatter: U = T + scatter * z, z an AR(1)-correlated normal."""
    rng = np.random.default_rng(seed)
    reported = np.zeros(N_PT * N_PZ, dtype=bool)
    reported[:n_reported] = True
    reported = reported.reshape(N_PT, N_PZ)
    T = rng.uniform(1.0, 5.0, size=(N_PT, N_PZ))
    prod_mean = T * rng.uniform(0.95, 1.05, size=T.shape)
    rel = rng.uniform(0.003, 0.02, size=T.shape)
    prod_sigma = rel * prod_mean
    n = N_PT * N_PZ
    z = np.empty((n_toys, n))
    z[:, 0] = rng.standard_normal(n_toys)
    for j in range(1, n):
        z[:, j] = rho * z[:, j - 1] + np.sqrt(1 - rho * rho) * rng.standard_normal(n_toys)
    scatter = rel * T / band_over_scatter
    U = T[None] + scatter[None] * z.reshape(n_toys, N_PT, N_PZ)
    return U, T, prod_mean, prod_sigma, reported


def test_seed_namespace_is_disjoint():
    used = set()
    for r in (td.PRODUCTION_DATA_SEEDS, td.PRODUCTION_MC_SEEDS,
              td.OLD_TOY_DATA_SEEDS, td.OLD_TOY_MC_SEEDS):
        used.update(r)
    new = set()
    for t in list(range(1, 201)) + [9001, 9002, 9003]:
        d, m = td.toy_seeds(t)
        new.update((d, m))
    assert len(new) == 2 * 203
    assert not new & used
    with pytest.raises(ValueError):
        td.toy_seeds(0)


def test_pseudo_data_counts_are_poisson_in_the_weights():
    w = np.full(200_000, 0.2)
    k = td.draw_pseudo_data_counts(w, td.toy_seeds(1)[0])
    assert np.array_equal(k, td.draw_pseudo_data_counts(w, td.toy_seeds(1)[0]))
    assert abs(k.mean() - 0.2) < 0.005 and abs(k.var() - 0.2) < 0.005
    with pytest.raises(ValueError):
        td.draw_pseudo_data_counts(np.array([0.1, -0.1]), 1)
    with pytest.raises(ValueError):
        td.draw_pseudo_data_counts(np.array([0.1, np.nan]), 1)


def test_mc_stream_matches_the_production_bootstrap_draw():
    # Production: np.random.default_rng(seed + 10_000_000).poisson(1.0, size=n).
    seed = 17
    ref = np.random.default_rng(seed + 10_000_000).poisson(1.0, size=1000).astype(float)
    assert np.array_equal(td.draw_mc_bootstrap(1000, seed + 10_000_000), ref)


def test_compress_keeps_selected_events_and_total():
    pt, pz = np.arange(6.0), np.arange(6.0) + 10
    k = np.array([0, 2, 0, 1, 3, 0], dtype=float)
    cpt, cpz, cw = td.compress_pseudo_data(pt, pz, k)
    assert cpt.tolist() == [1, 3, 4] and cpz.tolist() == [11, 13, 14]
    assert cw.tolist() == [2, 1, 3] and cw.sum() == k.sum()


def test_windows_and_nominal():
    assert sc.NOMINAL[1] == pytest.approx(0.682689, abs=1e-6)
    assert sc.NOMINAL[2] == pytest.approx(0.954500, abs=1e-6)
    assert sc.WINDOWS[1] == pytest.approx((0.631880, 0.728668), abs=1e-6)
    assert sc.WINDOWS[2] == pytest.approx((0.928139, 0.972193), abs=1e-6)


def test_calibrated_band_passes_and_controls_flag_it():
    U, T, m, s, rep = synthetic()
    base = sc.score(U, T, m, s, rep)
    assert base["verdict"] == "PASS"
    assert base["C1"] == pytest.approx(sc.NOMINAL[1], abs=0.02)
    scaled = {k: sc.score(U, T, m, s, rep, scale=k) for k in sc.CONTROL_SCALES}
    assert scaled[0.7]["verdict"] == "FAIL-undercoverage"
    assert scaled[1.3]["verdict"] == "FAIL-overcoverage"
    assert sc.positive_control(base, scaled)["passes"]


@pytest.mark.parametrize("ratio,expected", [(0.75, "FAIL-undercoverage"),
                                            (1.3, "FAIL-overcoverage")])
def test_miscalibrated_band_fails(ratio, expected):
    U, T, m, s, rep = synthetic(band_over_scatter=ratio, seed=3)
    assert sc.score(U, T, m, s, rep)["verdict"] == expected


def test_correlated_bins_widen_the_toy_interval():
    widths = []
    for rho in (0.0, 0.99):
        U, T, m, s, rep = synthetic(rho=rho, seed=5)
        ci = sc.score(U, T, m, s, rep)["intervals"]["C1"]
        widths.append(ci[1] - ci[0])
    assert widths[1] > 3 * widths[0]


def test_classify_and_verdict():
    w = sc.WINDOWS
    assert sc.classify([0.65, 0.70], w[1]) == "inside"
    assert sc.classify([0.50, 0.60], w[1]) == "below"
    assert sc.classify([0.75, 0.80], w[1]) == "above"
    assert sc.classify([0.60, 0.65], w[1]) == "overlap"
    inside2 = [0.94, 0.96]
    assert sc.verdict({"C1": [0.65, 0.70], "C2": inside2})[0] == "PASS"
    assert sc.verdict({"C1": [0.50, 0.60], "C2": inside2})[0] == "FAIL-undercoverage"
    assert sc.verdict({"C1": [0.50, 0.60], "C2": [0.98, 0.99]})[0] == "FAIL-mixed"
    assert sc.verdict({"C1": [0.60, 0.65], "C2": inside2})[0] == "INCONCLUSIVE"


def _write_npz(path, U, T, m, s, rep, dT=None, idx=None):
    n = U.shape[0]
    np.savez(path, toy_index=np.arange(1, n + 1) if idx is None else idx, U=U, T=T,
             T_max_abs_diff=np.zeros(n) if dT is None else dT,
             prod_mean=m, prod_sigma=s, reported=rep)


def test_run_refuses_a_fluctuating_truth(tmp_path):
    U, T, m, s, rep = synthetic()
    dT = np.zeros(U.shape[0])
    dT[7] = 1e-30
    _write_npz(tmp_path / "x.npz", U, T, m, s, rep, dT=dT)
    with pytest.raises(sc.InvalidInput, match="truth differs"):
        sc.run(tmp_path / "x.npz", "final")


def test_run_enforces_minimum_toy_count(tmp_path):
    U, T, m, s, rep = synthetic(n_toys=149)
    _write_npz(tmp_path / "x.npz", U, T, m, s, rep)
    with pytest.raises(sc.InsufficientToys, match="minimum 150"):
        sc.run(tmp_path / "x.npz", "final")
    assert sc.run(tmp_path / "x.npz", "interim")["decision"] == "CONTINUE"


def test_run_interim_stops_on_clear_failure(tmp_path):
    U, T, m, s, rep = synthetic(n_toys=100, band_over_scatter=0.6, seed=9)
    _write_npz(tmp_path / "x.npz", U, T, m, s, rep)
    assert sc.run(tmp_path / "x.npz", "interim")["decision"] == \
        "STOP: FAIL-undercoverage (futility)"


def test_run_rejects_nonpositive_truth_in_a_reported_bin(tmp_path):
    U, T, m, s, rep = synthetic()
    T = T.copy()
    T[0, 0] = 0.0
    _write_npz(tmp_path / "x.npz", U, T, m, s, rep)
    with pytest.raises(sc.InvalidInput, match="positive"):
        sc.run(tmp_path / "x.npz", "final")


def test_replica_form_divides_by_prior_over_truth(tmp_path):
    U, T, m, s, rep = synthetic()
    P = np.broadcast_to(T * 1.02, U.shape).copy()
    out = sc.replica_form(U, P, T, rep)
    assert np.allclose(out[:, rep], U[:, rep] / 1.02)
    assert np.array_equal(out[:, ~rep], U[:, ~rep])
    np.savez(tmp_path / "x.npz", toy_index=np.arange(1, 201), U=U, P=np.broadcast_to(T, U.shape),
             T=T, T_max_abs_diff=np.zeros(200), prod_mean=m, prod_sigma=s, reported=rep)
    res = sc.run(tmp_path / "x.npz", "final")
    assert res["secondary_replica_form"]["C1"] == res["result"]["C1"]
