"""Tests for RPL check (i), the scale fit (nd-unfolding/rpl_scale_fit.py); local fixtures only, no cluster inputs.

The integration tests run RPD-RECO's own chain (pins .. d2) on its real-format fixture, with a continuous, falling
p_par spectrum in place of the fixture's ten discrete values, which a scale fit cannot resolve.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("RPL_SCALE_FIT_MODULE", str(REPO / "nd-unfolding/rpl_scale_fit.py")))
SPEC = importlib.util.spec_from_file_location("rpl_scale_fit_under_test", SOURCE)
assert SPEC is not None and SPEC.loader is not None
F = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = F
SPEC.loader.exec_module(F)
R = F.R  # the fd_rpd_reco instance the module under test imported

sys.path.insert(0, str(REPO / "nd-unfolding/tests"))
import test_fd_rpd_reco as T  # noqa: E402  (RPD-RECO's real-format fixture)

BAND = {
    "schema": "rpl-bandsize/1",
    "sigma_band": {
        "Muon_Energy_MINOS": {"overall": 0.0085, "p_par_lt_8": 0.0079, "p_par_ge_8": 0.0103},
        "Muon_Energy_MINERvA": {"overall": 0.0062, "p_par_lt_8": 0.0068, "p_par_ge_8": 0.0026},
    },
}


# --------------------------------------------------------------------------------------------- unit: the lattice


def test_lattice_equals_rpd_reco_binning_at_alpha_zero_including_edge_values() -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(1)
    pz = np.r_[rng.uniform(0.5, 80, 5000), R.PZ_EDGES, R.PZ_EDGES - 1e-12, [0.0, 1.4999999, 60.0, 61.0]]
    weights = rng.integers(0, 4, len(pz)).astype(float)
    histogram = np.bincount(lattice.index(pz), weights=weights, minlength=lattice.size)
    expected = np.bincount(R.bin_indices(pz, R.PZ_EDGES), weights=weights, minlength=F.NBINS)
    assert np.array_equal(lattice.bins(F.cumulative(histogram), 0), expected)


@pytest.mark.parametrize("j", [-1000, -999, -537, -50, -1, 1, 50, 263, 999, 1000])
def test_lattice_equals_direct_rescaling_on_the_grid(j: int) -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(j + 2000)
    pz = rng.uniform(0.5, 80, 20000)
    weights = rng.integers(0, 4, len(pz)).astype(float)
    histogram = np.bincount(lattice.index(pz), weights=weights, minlength=lattice.size)
    assert np.array_equal(
        lattice.bins(F.cumulative(histogram), j), F.direct_bins(pz, weights, j / 10000.0)
    )


def test_lattice_bins_conserve_the_total_and_broadcast_over_replicas() -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(3)
    histograms = rng.integers(0, 5, (4, lattice.size)).astype(float)
    binned = lattice.bins(F.cumulative(histograms), 417)
    assert binned.shape == (4, F.NBINS)
    assert np.array_equal(binned.sum(axis=1), histograms.sum(axis=1))
    for row in range(4):
        assert np.array_equal(binned[row], lattice.bins(F.cumulative(histograms[row]), 417))


def test_lattice_covers_the_declared_grid() -> None:
    assert F.ALPHAS[0] == -0.10 and F.ALPHAS[-1] == 0.10 and len(F.ALPHAS) == 2001
    assert F.ALPHAS[F.LATTICE_HALF] == 0.0
    assert np.allclose(np.diff(F.ALPHAS), 1e-4)


# ------------------------------------------------------------------------------------------ unit: the estimator


def test_profiled_chi2_matches_a_brute_force_minimum() -> None:
    rng = np.random.default_rng(4)
    d = rng.uniform(0.8, 1.2, 11)
    sigma = rng.uniform(0.01, 0.05, 11)
    used = np.ones(11, dtype=bool)
    used[[2, 10]] = False
    chi2, k = F.profiled_chi2(d, sigma, used)
    grid = np.linspace(0.5, 1.5, 200001)
    brute = ((grid[:, None] * d[used] - 1) ** 2 / sigma[used] ** 2).sum(axis=1)
    assert chi2 == pytest.approx(brute.min(), rel=1e-6)
    assert k == pytest.approx(grid[np.argmin(brute)], abs=1e-5)


def test_profiled_chi2_refuses_a_degenerate_fit() -> None:
    with pytest.raises(R.Refused, match="FIT_DEGENERATE"):
        F.profiled_chi2(np.zeros(5), np.ones(5), np.ones(5, dtype=bool))


def test_parabola_vertex_and_non_convex_fallback() -> None:
    x = np.array([0.01, 0.0101, 0.0102])
    vertex, convex = F.parabola_vertex(x, 3 * (x - 0.01013) ** 2 + 2)
    assert convex and vertex == pytest.approx(0.01013, abs=1e-12)
    vertex, convex = F.parabola_vertex(x, -((x - 0.01) ** 2))
    assert not convex and vertex == 0.0101


def test_scan_finds_an_interior_minimum_off_the_grid() -> None:
    result = F.scan(lambda j: 1e4 * (j / 10000.0 - 0.03371) ** 2 + 3)
    assert result["coarse_min_alpha"] == 0.035
    assert result["fine_min_alpha"] == 0.0337
    assert result["alpha_hat"] == pytest.approx(0.03371, abs=1e-12)
    assert result["parabola_convex"] and not F.at_scan_edge(result)


@pytest.mark.parametrize("minimum", [-0.2, 0.2, -0.1, 0.1])
def test_scan_edge_is_flagged(minimum: float) -> None:
    result = F.scan(lambda j: (j / 10000.0 - minimum) ** 2)
    assert abs(result["coarse_min_alpha"]) == 0.10
    assert F.at_scan_edge(result)


def test_scan_fine_window_at_the_lattice_edge_uses_three_inner_points() -> None:
    result = F.scan(lambda j: (j / 10000.0 + 0.0999) ** 2)
    assert result["coarse_min_alpha"] == -0.10
    assert result["parabola_points"][0] == -0.10 and len(result["parabola_points"]) == 3


def _fit(alpha: float, sigma: float, p: float, edge: bool = False) -> dict[str, Any]:
    return {
        "alpha_hat": alpha,
        "sigma_alpha": sigma,
        "p_alpha_hat": p,
        "coarse_min_alpha": 0.10 if edge else round(alpha, 3),
    }


@pytest.mark.parametrize(
    "reading,fit,expected",
    [
        ("NOT-SEEN-AT-3σ", _fit(0.05, 0.001, 0.5), "NO-STEP"),
        ("SEEN", _fit(0.05, 0.001, 0.5, edge=True), "AT-SCAN-EDGE"),
        ("SEEN", _fit(0.10, 0.001, 0.0), "AT-SCAN-EDGE"),
        ("SEEN", _fit(0.05, 0.001, 0.0099), "NOT-A-SCALE"),
        ("SEEN", _fit(0.05, 0.001, 0.01), "SCALE-BEYOND-BAND"),
        ("SEEN", _fit(-0.05, 0.001, 0.5), "SCALE-BEYOND-BAND"),
        ("SEEN", _fit(0.0105, 0.001, 0.5), "SCALE-UNRESOLVED-AGAINST-BAND"),
        ("SEEN", _fit(0.0065, 0.001, 0.5), "SCALE-WITHIN-BAND"),
        ("SEEN", _fit(-0.0065, 0.001, 0.5), "SCALE-WITHIN-BAND"),
        ("SEEN", _fit(0.0070, 0.001, 0.5), "SCALE-UNRESOLVED-AGAINST-BAND"),
    ],
)
def test_outcome_table_in_order(reading: str, fit: dict[str, Any], expected: str) -> None:
    assert F.classify(reading, fit, 0.0085) == expected


@pytest.mark.parametrize("reading", ["NOT-SEEN", "", "seen", "PARTIAL"])
def test_an_unexpected_d1_reading_is_refused_not_read_as_no_step(reading: str) -> None:
    with pytest.raises(R.Refused, match="D1_READING"):
        F.classify(reading, None, 0.0085)


def test_declared_constants() -> None:
    # RPL-DECLARATION.md check (i): the scan, the outcome bars and the planted-scale control's construction
    assert (F.LATTICE_HALF, F.COARSE_STRIDE, F.FINE_HALF) == (1000, 50, 50)
    assert (F.P_FIT_MIN, F.BAND_SIGMAS) == (0.01, 2.0)
    assert F.PLANTS == (0.01, 0.03) and F.PLANT_TOLERANCE == 3.5
    assert F.PLANT_SPLIT_WORDS == (20261110, 17, 1)
    assert F.REPRODUCTION_RTOL == 1e-12
    assert F.READINGS == ("SEEN", "NOT-SEEN-AT-3σ")
    assert F.PUBLISHED_SCALE == "1 % (iii/README.md, quote 3b), printed beside sigma_band"


def test_the_deciding_band_is_minos_overall_not_a_stratum() -> None:
    band = json.loads(json.dumps(BAND))
    assert F.deciding_band(band) == 0.0085
    band["sigma_band"]["Muon_Energy_MINOS"]["overall"] = 0.5
    assert F.deciding_band(band) == 0.5
    with pytest.raises(R.Refused, match="BAND"):
        F.deciding_band({**band, "schema": "other"})


def test_outcome_band_boundaries_are_inclusive_as_declared() -> None:
    # |a| + 2s <= band is WITHIN; |a| - 2s > band (strict) is BEYOND; equality goes to UNRESOLVED
    # dyadic values, so the sums are exact: 1/32 + 2/64 = 1/16 and 3/32 - 2/64 = 1/16
    assert F.classify("SEEN", _fit(0.03125, 0.015625, 0.5), 0.0625) == "SCALE-WITHIN-BAND"
    assert F.classify("SEEN", _fit(0.09375, 0.015625, 0.5), 0.0625) == "SCALE-UNRESOLVED-AGAINST-BAND"
    assert F.classify("SEEN", _fit(0.09376, 0.015625, 0.5), 0.0625) == "SCALE-BEYOND-BAND"


def test_step_histogram_regions() -> None:
    bins = np.arange(11, dtype=float)
    assert np.array_equal(F.step_histogram(bins), [0 + 1 + 2 + 3 + 4 + 5, 6 + 7, 8 + 9 + 10])


def test_group_fit_recovers_a_synthetic_scale_with_poisson_replicas() -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(5)
    mc_pz = 1.0 + rng.exponential(5.0, 400000)
    data_pz = (1.0 + rng.exponential(5.0, 400000)) * 1.04
    reference_pz = 1.0 + rng.exponential(5.0, 400000)
    draws = np.vstack([np.ones(400000), rng.poisson(1, (200, 400000))])
    p = np.stack([np.bincount(R.bin_indices(mc_pz, R.PZ_EDGES), weights=w, minlength=11) for w in draws])
    n_ref = np.stack([np.bincount(R.bin_indices(reference_pz, R.PZ_EDGES), weights=w, minlength=11) for w in draws])
    index = lattice.index(data_pz)
    data = np.stack([np.bincount(index, weights=w, minlength=lattice.size) for w in draws])
    fit = F.GroupFit(lattice, F.cumulative(data), p, n_ref, p).fit()
    assert abs(fit["alpha_hat"] - 0.04) <= 3.5 * fit["sigma_alpha"]
    assert 0 < fit["sigma_alpha"] < 0.01
    assert fit["ndf"] == len(fit["used_bins"]) - 2
    assert fit["chi2_alpha0"] > fit["chi2_alpha_hat"]


def test_group_fit_refuses_undefined_variance_and_too_few_bins() -> None:
    lattice = F.Lattice()
    flat = np.ones((201, lattice.size))
    p = np.full((201, 11), 100.0)
    p[1:, 3] = 0.0  # a used bin (nominal P >= 25) whose replicas have no prediction: an undefined ratio
    with pytest.raises(R.Refused, match="BOOTSTRAP_VARIANCE"):
        F.GroupFit(lattice, F.cumulative(flat), p, np.full((201, 11), 100.0), np.full((201, 11), 100.0))
    p_small = np.full((201, 11), 10.0)
    with pytest.raises(R.Refused, match="FIT_NDF"):
        F.GroupFit(lattice, F.cumulative(flat), p_small, p_small, p_small)


def test_a_bin_is_used_only_when_both_predictions_reach_the_minimum() -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(11)
    data = rng.poisson(50.0, (201, lattice.size)).astype(float)
    p_group = 100.0 + rng.uniform(0.0, 1.0, (201, 11))
    p_ref = 100.0 + rng.uniform(0.0, 1.0, (201, 11))
    n_ref = 100.0 + rng.uniform(0.0, 1.0, (201, 11))
    p_group[:, 2] = R.MIN_PREDICTION - 1.0  # the fitted group alone falls short
    p_ref[:, 5] = R.MIN_PREDICTION - 1.0  # the reference alone falls short
    p_group[:, 4] = p_ref[:, 4] = R.MIN_PREDICTION  # exactly at the minimum: used (P >= 25)
    group = F.GroupFit(lattice, F.cumulative(data), p_group, n_ref, p_ref)
    assert np.flatnonzero(group.used).tolist() == [0, 1, 3, 4, 6, 7, 8, 9, 10]
    assert group.ndf == 9 - 2


def _synthetic(rows: int, seed: int, scale: float, reference_shape: float = 5.0) -> tuple[Any, ...]:
    """A fitted group whose data are its MC scaled by (1 + scale), and a reference of another shape."""
    lattice = F.Lattice()
    rng = np.random.default_rng(seed)
    group_mc = 1.0 + rng.exponential(5.0, rows)
    group_data = (1.0 + rng.exponential(5.0, rows)) * (1.0 + scale)
    reference_mc = 1.0 + rng.exponential(reference_shape, rows)
    reference_data = 1.0 + rng.exponential(reference_shape, rows)
    draws = np.vstack([np.ones(rows), rng.poisson(1, (R.BOOTSTRAPS, rows))])

    def binned(pz: np.ndarray) -> np.ndarray:
        return np.stack([np.bincount(R.bin_indices(pz, R.PZ_EDGES), weights=w, minlength=11) for w in draws])

    data = np.stack([np.bincount(lattice.index(group_data), weights=w, minlength=lattice.size) for w in draws])
    return lattice, F.cumulative(data), binned(group_mc), binned(reference_data), binned(reference_mc)


def test_the_fit_uses_both_predictions_when_their_shapes_differ() -> None:
    # PB's and PA's spectra differ in shape: the double ratio needs P_group and P_ref, or the fit is biased
    lattice, c, p_group, n_ref, p_ref = _synthetic(60000, 9, 0.04, reference_shape=2.0)
    fit = F.GroupFit(lattice, c, p_group, n_ref, p_ref).fit()
    assert abs(fit["alpha_hat"] - 0.04) <= 3.5 * fit["sigma_alpha"]
    assert fit["p_alpha_hat"] > 0.01


def test_sigma_b_is_the_replica_sd_of_the_ratio_at_alpha_zero() -> None:
    lattice, c, p_group, n_ref, p_ref = _synthetic(20000, 12, 0.0)
    group = F.GroupFit(lattice, c, p_group, n_ref, p_ref)
    d = (lattice.bins(c, 0) / p_group) / (n_ref / p_ref)
    expected = np.std(d[1:], axis=0, ddof=1)  # replicas 1..200 only, sample SD
    assert np.array_equal(group.sigma[group.used], expected[group.used])
    assert not np.allclose(group.sigma[group.used], np.std(d, axis=0, ddof=1)[group.used], rtol=1e-6, atol=0)


def test_chi2_at_alpha_hat_comes_from_the_off_lattice_evaluation_and_the_wall_is_checked_per_scan() -> None:
    from scipy.stats import chi2 as chi2_distribution

    lattice, c, p_group, n_ref, p_ref = _synthetic(20000, 13, 0.02)
    calls: list[float] = []
    ticks: list[int] = []

    def nominal(alpha: float) -> float:
        calls.append(alpha)
        return 7.25

    fit = F.GroupFit(lattice, c, p_group, n_ref, p_ref).fit(nominal, lambda: ticks.append(1))
    assert calls == [fit["alpha_hat"]]
    assert fit["chi2_alpha_hat"] == 7.25
    assert fit["p_alpha_hat"] == float(chi2_distribution.sf(7.25, fit["ndf"]))
    assert len(ticks) == R.BOOTSTRAPS + 1  # before the nominal scan and before each replica refit

    def expired() -> None:
        if len(ticks) > 40:
            raise R.Refused("WALL_CLOCK", "wall budget exhausted")
        ticks.append(1)

    ticks.clear()
    with pytest.raises(R.Refused, match="WALL_CLOCK"):
        F.GroupFit(lattice, c, p_group, n_ref, p_ref).fit(None, expired)


def test_plant_control_applies_the_declared_rule_and_chi2_off_the_lattice(monkeypatch: pytest.MonkeyPatch) -> None:
    rng = np.random.default_rng(21)
    pz_rows = 1.0 + rng.exponential(5.0, 3000)
    weight_rows = 2.0 * rng.uniform(0.5, 1.5, 3000)
    p_pb = 100.0 + rng.uniform(0, 1, (201, 11))
    n_pa = 100.0 + rng.uniform(0, 1, (201, 11))
    p_pa = 100.0 + rng.uniform(0, 1, (201, 11))
    streamed = {
        "plant_rows": (pz_rows, weight_rows),
        "pseudo_p": {"PB": p_pb, "PA": p_pa},
        "pseudo_n_pa": n_pa,
        "plant_lattice": {alpha: np.ones((201, 4)) for alpha in F.PLANTS},
    }
    captured: dict[float, Any] = {}

    class Fake:  # an edge-pinned recovery whose pull is within 3.5: the declared rule passes it
        def __init__(self, *_args: Any) -> None:
            self.sigma = np.full(11, 0.05)
            self.used = np.ones(11, dtype=bool)

        def fit(self, nominal: Any, check: Any) -> dict[str, Any]:
            captured[len(captured)] = nominal
            return {"alpha_hat": 0.10, "coarse_min_alpha": 0.10, "sigma_alpha": 0.03, "chi2_alpha_hat": nominal(0.10),
                    "fine_min_chi2": 1.0, "p_alpha_hat": 0.5}

    monkeypatch.setattr(F, "GroupFit", Fake)
    results = F.plant_control(streamed, F.Lattice(), None)
    assert all(r["at_scan_edge"] and r["pass"] for r in results.values())
    for (alpha, nominal) in zip(F.PLANTS, captured.values()):
        n = F.direct_bins(pz_rows * (1.0 + alpha), weight_rows, 0.0123)
        d = (n / p_pb[0]) / (n_pa[0] / p_pa[0])
        assert nominal(0.0123) == F.profiled_chi2(d, np.full(11, 0.05), np.ones(11, dtype=bool))[0]
    assert results["+0.030"]["pull"] == pytest.approx((0.10 - 0.03) / 0.03)


def test_self_digest_turns_an_open_error_into_a_refusal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "record.json"
    target.write_text("{}")
    monkeypatch.setattr(os, "O_NOATIME", os.O_NONBLOCK, raising=False)

    def denied(*_args: Any, **_kwargs: Any) -> int:
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(F.os, "open", denied)
    with pytest.raises(R.Refused, match="NOATIME_OPEN"):
        F.self_digest(target)


def test_an_os_error_is_a_stop_record_and_cfs_output_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for key in R.THREAD_KEYS:
        monkeypatch.setenv(key, "1")
    monkeypatch.setattr(os, "getpriority", lambda *_args: 19)

    def failing(*_args: Any) -> Any:
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(F, "run", failing)
    arguments = ["--config", "c", "--config-sha256", "0" * 64, "--rpd-run", "r", "--d1-sha256", "0" * 64,
                 "--d2-sha256", "0" * 64, "--band", "b", "--band-sha256", "0" * 64, "--wall-seconds", "1"]
    out = tmp_path / "os-error"
    assert F.main(arguments + ["--out", str(out)]) == 4
    assert _stop(out)["guard"] == "OS_ERROR" and _stop(out)["readings"] is None
    cfs = Path("/global/cfs/cdirs/m3246/rpl-test-never-created")
    assert F.main(arguments + ["--out", str(cfs)]) == 4
    assert not cfs.exists()
    capsys.readouterr()

    def full(*_args: Any) -> None:
        raise OSError(28, "No space left on device")

    sealed = tmp_path / "sealed"
    sealed.mkdir()
    real_iterdir = Path.iterdir

    def unreadable(self: Path) -> Any:
        if self == sealed:
            raise PermissionError(13, "Permission denied")
        return real_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", unreadable)  # the directory cannot be inspected: STOP printed, rc 4
    assert F.main(arguments + ["--out", str(sealed)]) == 4
    assert "STOP OS_ERROR" in capsys.readouterr().out
    assert not (sealed / "rpl-scale-fit.STOP.json").exists()
    monkeypatch.setattr(Path, "iterdir", real_iterdir)

    monkeypatch.setattr(R, "write_json", full)  # the STOP record cannot be written: still a STOP, rc 4, no exception
    assert F.main(arguments + ["--out", str(tmp_path / "full-disk")]) == 4
    printed = capsys.readouterr().out
    assert "STOP record not written" in printed and "STOP OS_ERROR" in printed


def test_run_refuses_cfs_output_before_creating_anything(tmp_path: Path) -> None:
    import argparse

    cfs = Path("/global/cfs/cdirs/m3246/rpl-test-never-created")
    with pytest.raises(R.Refused, match="OUTPUT_LOCATION"):
        F.run(argparse.Namespace(out=cfs), [])
    assert not cfs.exists()


def test_sigma_alpha_is_the_spread_of_every_replica_refit(monkeypatch: pytest.MonkeyPatch) -> None:
    lattice = F.Lattice()
    rng = np.random.default_rng(7)
    rows = 40000
    mc_pz = 1.0 + rng.exponential(5.0, rows)
    data_pz = (1.0 + rng.exponential(5.0, rows)) * 1.02
    draws = np.vstack([np.ones(rows), rng.poisson(1, (R.BOOTSTRAPS, rows))])
    p = np.stack([np.bincount(R.bin_indices(mc_pz, R.PZ_EDGES), weights=w, minlength=11) for w in draws])
    data = np.stack([np.bincount(lattice.index(data_pz), weights=w, minlength=lattice.size) for w in draws])
    scans: list[float] = []
    original = F.scan

    def spy(chi2_at: Any) -> Any:
        result = original(chi2_at)
        scans.append(result["alpha_hat"])
        return result

    monkeypatch.setattr(F, "scan", spy)
    fit = F.GroupFit(lattice, F.cumulative(data), p, p, p).fit()
    assert len(scans) == R.BOOTSTRAPS + 1  # the nominal scan, then one refit per replica
    assert fit["alpha_hat"] == scans[0]
    assert fit["sigma_alpha"] == float(np.std(scans[1:], ddof=1))


def test_the_stream_checks_the_wall_clock_before_every_sample(
    quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []
    original = F.stream

    def spy(reader: Any, lattice: Any, plant_split: Any, check: Any) -> Any:
        def counted() -> None:
            calls.append(1)
            check()

        return original(reader, lattice, plant_split, counted)

    monkeypatch.setattr(F, "stream", spy)
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 0
    samples = sum(len(by_playlist) for by_playlist in _record(out)["rows"].values())
    assert samples == 3 * len(R.PLAYLISTS)
    assert len(calls) == samples


# ------------------------------------------------------------------------------------- integration: the real chain


def _continuous_reco(rows: int, planted: float) -> Any:
    """RPD-RECO's fixture rows with a continuous, falling p_par; PB's measured rows (rows + 6 .. rows + 8 long in the
    fixture's construction) carry a planted momentum scale."""

    def reco(count: int, rng: np.random.Generator) -> np.ndarray:
        values = np.column_stack(
            [
                rng.uniform(0.001, 4.499, count),
                1.0 + rng.exponential(5.0, count),
                rng.uniform(0.001, 1.6, count),
                rng.uniform(0.001, 4, count),
                rng.uniform(0.8, 3, count),
            ]
        )
        if count in (rows + 6, rows + 7, rows + 8):
            values[:, :2] *= 1.0 + planted
        return values

    return reco


def _chain(root: Path, rows: int, planted: float, seed: int = 17) -> T.Fixture:
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(T, "_reco", _continuous_reco(rows, planted))
        fixture = T.Fixture(root, seed=seed, rows=rows)
    prediction, sha = fixture.prepare_prediction()
    fixture.execute("step0")
    for step in ("c0", "d1", "d2"):
        fixture.execute(step, prediction=prediction, prediction_sha=sha)
    band = root / "band.json"
    band.write_text(json.dumps(BAND))
    return fixture


def _arguments(fixture: T.Fixture, out: Path, **override: str) -> list[str]:
    band = fixture.root / "band.json"
    values = {
        "--config": str(fixture.config_path),
        "--config-sha256": fixture.config_sha,
        "--rpd-run": str(fixture.run),
        "--d1-sha256": R.digest(fixture.run / "d1.json"),
        "--d2-sha256": R.digest(fixture.run / "d2.json"),
        "--band": str(band),
        "--band-sha256": R.digest(band),
        "--out": str(out),
        "--wall-seconds": "3600",
    }
    values.update(override)
    return [item for pair in values.items() for item in pair]


@pytest.fixture(scope="module")
def environment() -> Iterator[None]:
    with pytest.MonkeyPatch.context() as patch:
        if not hasattr(os, "O_NOATIME"):
            patch.setattr(os, "O_NOATIME", os.O_NONBLOCK, raising=False)
        for key in R.THREAD_KEYS:
            patch.setenv(key, "1")
        patch.setattr(os, "getpriority", lambda *_args: 19)
        yield


@pytest.fixture(scope="module")
def seen(tmp_path_factory: pytest.TempPathFactory, environment: None) -> T.Fixture:
    return _chain(tmp_path_factory.mktemp("seen"), rows=16384, planted=0.08)


@pytest.fixture(scope="module")
def quiet(tmp_path_factory: pytest.TempPathFactory, environment: None) -> T.Fixture:
    return _chain(tmp_path_factory.mktemp("quiet"), rows=2048, planted=0.0)


def _record(out: Path) -> dict[str, Any]:
    return json.loads((out / "rpl-scale-fit.json").read_text())


def _stop(out: Path) -> dict[str, Any]:
    return json.loads((out / "rpl-scale-fit.STOP.json").read_text())


def test_seen_chain_recovers_the_planted_data_scale(seen: T.Fixture, tmp_path: Path) -> None:
    d1 = json.loads((seen.run / "d1.json").read_text())["result"]["R-d1.0"]["PB"]
    assert d1["reading"] == "SEEN"
    out = tmp_path / "rpl"
    assert F.main(_arguments(seen, out)) == 0
    record = _record(out)
    primary = record["primary_PB"]
    assert abs(primary["alpha_hat"] - 0.08) <= 3.5 * primary["sigma_alpha"]
    assert record["outcome"] == "SCALE-BEYOND-BAND"
    assert primary["chi2_alpha0"] > primary["chi2_alpha_hat"]
    assert primary["ndf"] == len(primary["used_bins"]) - 2
    pc = record["descriptive_alpha_hat"]["PC"]
    assert abs(pc["alpha_hat"]) <= 3.5 * pc["sigma_alpha"]
    assert set(record["descriptive_alpha_hat"]) == {"PC", *R.PLAYLISTS}
    reproduction = record["controls"]["reproduction"]
    assert reproduction["histograms_equal"] and reproduction["step_N_equal_c0"]
    assert reproduction["s_PB_relative_difference"] <= 1e-12
    assert reproduction["sigma_PB_relative_difference"] <= 1e-12
    assert all(plant["pass"] for plant in record["controls"]["planted_scale"].values())
    assert record["sigma_band"]["Muon_Energy_MINOS_overall"] == 0.0085
    assert record["does_not_license"] == F.DOES_NOT_LICENSE
    assert record["rpd_reco_code_sha256"] == json.loads((seen.run / "d1.json").read_text())["code_sha256"]
    assert {row["key"] for row in record["keys_read"]} <= R.MC_KEYS | R.BKG_KEYS | {"measured"}


def _c0_prediction(fixture: T.Fixture) -> np.ndarray:
    product = json.loads((fixture.run / "c0.json").read_text())["result"]["product"]
    with np.load(fixture.run / product["path"]) as archive:
        return np.asarray(archive["pz__P"], dtype=float)  # (replica, variant, playlist, bin)


def test_seen_chain_inputs_and_leave_one_out_references(
    seen: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prediction = _c0_prediction(seen)
    assert not np.array_equal(prediction[:, 0], prediction[:, 1])  # the variant matters in this fixture
    p = prediction[:, 0]
    pb, pa = F.members("PB"), F.members("PA")
    constructed: list[dict[str, np.ndarray]] = []
    real = F.GroupFit

    class Spy(real):  # type: ignore[misc, valid-type]
        def __init__(self, lattice: Any, c: Any, p_group: Any, n_ref: Any, p_ref: Any) -> None:
            constructed.append({"p_group": p_group, "p_ref": p_ref})
            super().__init__(lattice, c, p_group, n_ref, p_ref)

    monkeypatch.setattr(F, "GroupFit", Spy)
    out = tmp_path / "rpl"
    assert F.main(_arguments(seen, out)) == 0
    record = _record(out)
    assert record["status"] == "PASS" and record["outcome"] == "SCALE-BEYOND-BAND"
    # the primary fit uses c0's variant-0 prediction for PB, against PA
    assert any(np.array_equal(c["p_group"], p[:, pb].sum(axis=1)) and np.array_equal(c["p_ref"], p[:, pa].sum(axis=1))
               for c in constructed)
    descriptive = record["descriptive_alpha_hat"]
    pa_names = [R.PLAYLISTS[x] for x in pa]
    for name in R.PLAYLISTS:  # leave-one-out: a PA member is fitted against the other five
        assert descriptive[name]["fitted"] == [name]
        assert descriptive[name]["reference"] == [x for x in pa_names if x != name]
    assert descriptive["PC"]["reference"] == pa_names
    assert record["primary_PB"]["fitted"] == [R.PLAYLISTS[x] for x in pb]
    assert record["published_muon_energy_scale"] == "1 % (iii/README.md, quote 3b), printed beside sigma_band"
    for plant in record["controls"]["planted_scale"].values():
        assert set(plant) >= {"chi2_alpha_hat", "fine_min_chi2", "at_scan_edge", "pull", "pass"}


@pytest.mark.parametrize("guard", ["FIT_NDF", "WALL_CLOCK"])
def test_a_refusal_in_a_descriptive_fit_is_a_stop(
    guard: str, seen: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # RPL-DECLARATION.md fixes no reading for a descriptive fit that cannot be formed (:112, :130), so it is a STOP
    p = _c0_prediction(seen)[:, 0]
    lone = R.PLAYLISTS.index("1L")
    real = F.GroupFit

    class Expiring(real):  # type: ignore[misc, valid-type]
        def __init__(self, lattice: Any, c: Any, p_group: Any, n_ref: Any, p_ref: Any) -> None:
            if np.array_equal(p_group, p[:, [lone]].sum(axis=1)):
                raise R.Refused(guard, "refused in 1L's descriptive fit")
            super().__init__(lattice, c, p_group, n_ref, p_ref)

    monkeypatch.setattr(F, "GroupFit", Expiring)
    out = tmp_path / "rpl"
    assert F.main(_arguments(seen, out)) == 4
    assert _stop(out)["guard"] == guard and not (out / "rpl-scale-fit.json").exists()


def test_the_pseudo_data_halves_are_doubled_to_c0s_prediction(
    quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: list[dict[str, Any]] = []
    real = F.stream

    def spy(*args: Any, **kwargs: Any) -> Any:
        captured.append(real(*args, **kwargs))
        return captured[-1]

    monkeypatch.setattr(F, "stream", spy)
    assert F.main(_arguments(quiet, tmp_path / "rpl")) == 0
    streamed = captured[0]
    p = _c0_prediction(quiet)[0, 0]  # nominal replica, variant 0: (playlist, bin)
    pa, pb = F.members("PA"), F.members("PB")
    # each simulated row lands in exactly one half and each half is weighted x 2, so the halves sum to 2 P
    assert np.allclose(streamed["pseudo_p"]["PA"][0] + streamed["pseudo_n_pa"][0], 2 * p[pa].sum(axis=0), rtol=1e-12, atol=0)
    pz_rows, weight_rows = streamed["plant_rows"]
    pb_pseudo = F.direct_bins(pz_rows, weight_rows, 0.0)
    assert np.allclose(streamed["pseudo_p"]["PB"][0] + pb_pseudo, 2 * p[pb].sum(axis=0), rtol=1e-12, atol=0)
    for alpha in F.PLANTS:  # the lattice plant and the off-lattice rows carry the same pseudo-data weight
        assert streamed["plant_lattice"][alpha][0].sum() == pytest.approx(weight_rows.sum(), rel=1e-12)


def test_quiet_chain_is_no_step_with_no_fit_read(quiet: T.Fixture, tmp_path: Path) -> None:
    d1 = json.loads((quiet.run / "d1.json").read_text())["result"]["R-d1.0"]["PB"]
    assert d1["reading"] != "SEEN"
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 0
    record = _record(out)
    assert record["outcome"] == "NO-STEP"
    assert record["primary_PB"] is None and record["descriptive_alpha_hat"] is None
    assert record["controls"]["reproduction"]["histograms_equal"]


def test_p_rpd_refuses_a_wrong_or_broken_record(quiet: T.Fixture, tmp_path: Path) -> None:
    out = tmp_path / "wrong-d1"
    assert F.main(_arguments(quiet, out, **{"--d1-sha256": "0" * 64})) == 4
    assert _stop(out)["readings"] is None
    copy = tmp_path / "run-copy"
    shutil.copytree(quiet.run, copy)
    step0 = json.loads((copy / "step0.json").read_text())
    step0["result"]["simulation_only"] = "altered"
    (copy / "step0.json").write_text(json.dumps(step0))
    out = tmp_path / "broken-chain"
    assert F.main(_arguments(quiet, out, **{"--rpd-run": str(copy)})) == 4
    assert _stop(out)["guard"] == "P_RPD"


def test_p_rpd_refuses_a_unit_test_c0_stand_in(tmp_path: Path, environment: None) -> None:
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(T, "_reco", _continuous_reco(512, 0.0))
        fixture = T.Fixture(tmp_path / "standin", seed=17, rows=512)
    prediction, sha = fixture.prepare_prediction()
    fixture.execute("step0")
    inputs = fixture.inputs()
    inputs.prediction = prediction, sha
    records = T.R.require_predecessors(inputs, "c0", dry_run=False)
    histograms, _ = T.R.aggregate(inputs, records["p0"]["result"], records["step0"]["result"], data=True)
    product = T.R._save_histograms(fixture.run, "c0", histograms)
    T.R.write_json(
        fixture.run / "c0.json",
        {
            "step": "c0",
            "status": "PASS",
            "code_sha256": T.R.digest(T.SOURCE),
            "config_sha256": fixture.config_sha,
            "predecessor_sha256": T.R.digest(fixture.run / "step0.json"),
            "dry_run": False,
            "result": {"product": product, "unit_test_predecessor_only": True},
        },
    )
    for step in ("d1", "d2"):
        fixture.execute(step, prediction=prediction, prediction_sha=sha)
    (fixture.root / "band.json").write_text(json.dumps(BAND))
    out = tmp_path / "rpl"
    assert F.main(_arguments(fixture, out)) == 4
    assert _stop(out)["guard"] == "P_RPD"


def test_reproduction_refuses_changed_draws(quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real = F.stream

    def shifted(*args: Any, **kwargs: Any) -> Any:
        result = real(*args, **kwargs)
        result["data_lattice"][3, 7, 100] += 1.0
        return result

    monkeypatch.setattr(F, "stream", shifted)
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 4
    assert _stop(out)["guard"] == "REPRODUCTION_HISTOGRAMS"


def test_reproduction_refuses_a_changed_step(quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real = F.step_histogram
    calls = []

    def perturbed(bins: Any) -> Any:  # 1G's high region only: a change common to every playlist would cancel
        calls.append(1)
        return real(bins) * (np.array([1.0, 1.0 + 1e-9, 1.0]) if len(calls) == 7 else 1.0)

    monkeypatch.setattr(F, "step_histogram", perturbed)
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 4
    assert _stop(out)["guard"] == "REPRODUCTION_S_PB"


def test_plant_failure_stops_before_any_reading(quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(F, "PLANT_TOLERANCE", 0.0)
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 4
    stop = _stop(out)
    assert stop["guard"] == "PLANT_RECOVERY" and stop["readings"] is None
    assert not (out / "rpl-scale-fit.json").exists()


def test_environment_must_equal_p0s(quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real = R.runtime_environment
    monkeypatch.setattr(R, "runtime_environment", lambda: {**real(), "numpy": "0.0.0"})
    out = tmp_path / "rpl"
    assert F.main(_arguments(quiet, out)) == 4
    assert _stop(out)["guard"] == "ENVIRONMENT"


def test_threads_nice_wall_and_output_guards(
    quiet: T.Fixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "wall"
    assert F.main(_arguments(quiet, out, **{"--wall-seconds": "0"})) == 4
    assert _stop(out)["guard"] == "WALL_CLOCK"
    for name, present in (("full", "x"), ("stopped", "rpl-scale-fit.STOP.json")):
        out = tmp_path / name
        out.mkdir()
        (out / present).write_text("left by an earlier run")
        assert F.main(_arguments(quiet, out)) == 4  # no FileExistsError, and no new file in someone's directory
        assert sorted(p.name for p in out.iterdir()) == [present]
        assert (out / present).read_text() == "left by an earlier run"
        assert "STOP OUTPUT_EXISTS" in capsys.readouterr().out
    monkeypatch.setenv("OMP_NUM_THREADS", "2")
    out = tmp_path / "threads"
    assert F.main(_arguments(quiet, out)) == 4
    assert _stop(out)["guard"] == "THREADS"
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setattr(os, "getpriority", lambda *_args: 0)
    out = tmp_path / "nice"
    assert F.main(_arguments(quiet, out)) == 4
    assert _stop(out)["guard"] == "NICE"


def test_band_and_config_digests_are_pinned(quiet: T.Fixture, tmp_path: Path) -> None:
    out = tmp_path / "band"
    assert F.main(_arguments(quiet, out, **{"--band-sha256": "0" * 64})) == 4
    assert _stop(out)["readings"] is None
    out = tmp_path / "config"
    assert F.main(_arguments(quiet, out, **{"--config-sha256": "0" * 64})) == 4
    assert _stop(out)["readings"] is None
