"""Tests of the generalized loaders, the efficiency-corrected OmniFold loop, the scorer and the
extractor's member guard (synthetic arrays; no cluster data needed).

    python -m pytest nd-unfolding/pet/final_design/scalar/test_scalar_matched.py -q
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import extract_selections as ex  # noqa: E402
import selection_data as sd  # noqa: E402
import scalar_estimators as se  # noqa: E402
import binned_unfolding as bu  # noqa: E402
import scalar_omnifold as so  # noqa: E402


def _unit_mean(raw: np.ndarray, mask: np.ndarray) -> np.ndarray:
    w = np.ones(raw.size)
    w[mask] = raw[mask] / raw[mask].mean()
    return w


def synthetic_selection(n: int = 4000, seed: int = 0, cases=("D1_m0.350", "R1_x1.05_D1_p0.350"),
                        overlap: bool = False) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    out: dict[str, np.ndarray] = {}
    for i, side in enumerate(("prior", "pseudo")):
        rows = np.arange(n) * 2 + i
        if overlap and side == "pseudo":
            rows[:5] = np.arange(5) * 2
        t = np.stack([rng.gamma(2, 0.2, n), rng.gamma(4, 1.0, n), rng.exponential(0.4, n),
                      rng.gamma(2, 0.3, n)], axis=1).astype(np.float32)
        r = (t * rng.normal(1, 0.1, t.shape)).astype(np.float32)
        out[f"{side}_rows"] = rows.astype(np.int64)
        out[f"{side}_truth_scalars"] = t
        out[f"{side}_reco_scalars"] = r
        out[f"{side}_w_truth"] = rng.uniform(0.8, 1.2, n).astype(np.float32)
        out[f"{side}_w_reco"] = rng.uniform(0.8, 1.2, n).astype(np.float32)
        out[f"{side}_pass_truth"] = rng.random(n) < 0.95
        out[f"{side}_pass_reco"] = rng.random(n) < 0.8
        out[f"{side}_region"] = rng.choice(np.array([0, 1, 2, 3, -1], np.int8), n)
        out[f"{side}_rc_n_valid"] = rng.integers(0, 13, n).astype(np.int8)
        out[f"{side}_rc_E_sum"] = rng.exponential(0.5, n).astype(np.float32)
        for k in sd.SPECIES:
            out[f"{side}_tr_n_{k}"] = rng.integers(0, 5, n).astype(np.int8)
    for c in cases:
        e_d = out["pseudo_truth_scalars"][:, 2].astype(float)
        e_p = out["prior_truth_scalars"][:, 2].astype(float)
        out[f"case__{c}__pseudo_distortion"] = _unit_mean(np.exp(0.8 * e_d),
                                                          out["pseudo_pass_truth"])
        out[f"case__{c}__prior_oracle"] = _unit_mean(np.exp(0.8 * e_p), out["prior_pass_truth"])
    return out


# ------------------------------------------------------------------------------------------- #
# Loaders
# ------------------------------------------------------------------------------------------- #
def test_library_units_and_cases():
    lib = sd.library()
    assert len(lib) == 16
    assert ("F0", "dev") in lib and ("F1", "dev") in lib
    assert ("T1", "D1_p0.350") in lib and ("T0", "R1_x1.05_D1_p0.350") in lib
    with pytest.raises(ValueError):
        sd.build_problem(synthetic_selection(), "F0", "D1_m0.350")


def test_r1_scales_pseudodata_reco_energy_only_on_reco_passing_rows():
    sel = synthetic_selection()
    base = sd.build_problem(sel, "T0", "D1_m0.350")
    r1 = sd.build_problem(sel, "T0", "R1_x1.05_D1_p0.350")
    hit = sel["pseudo_pass_reco"]
    f = np.float32(1.05)
    np.testing.assert_array_equal(r1.pseudo["reco_eavail"][hit],
                                  (sel["pseudo_reco_scalars"][hit, 2] * f).astype(np.float64))
    np.testing.assert_array_equal(r1.pseudo["reco_eavail"][~hit], base.pseudo["reco_eavail"][~hit])
    np.testing.assert_array_equal(r1.pseudo["rc_E_sum"][hit],
                                  (sel["pseudo_rc_E_sum"][hit] * f).astype(np.float64))
    # prior, muon, q3 and cluster count untouched
    np.testing.assert_array_equal(r1.prior["reco_eavail"], base.prior["reco_eavail"])
    Xr, _ = r1.reco_matrix("pseudo")
    Xb, _ = base.reco_matrix("pseudo")
    for j in (0, 1, 3, 5):
        np.testing.assert_array_equal(Xr[:, j], Xb[:, j])
    assert r1.r1_factor == 1.05


def test_derived_control_uses_r1_weights_without_scaling():
    sel = synthetic_selection()
    ctl = sd.build_problem(sel, "T0", "D1_p0.350")
    r1 = sd.build_problem(sel, "T0", "R1_x1.05_D1_p0.350")
    np.testing.assert_array_equal(ctl.distortion, r1.distortion)
    np.testing.assert_array_equal(ctl.oracle, r1.oracle)
    np.testing.assert_array_equal(ctl.pseudo["reco_eavail"],
                                  sel["pseudo_reco_scalars"][:, 2].astype(np.float64))
    assert ctl.r1_factor is None and ctl.record["derived_control"]


def test_selections_weights_and_feature_order():
    sel = synthetic_selection()
    p = sd.build_problem(sel, "T1", "D1_m0.350")
    np.testing.assert_array_equal(p.s1_prior, sel["prior_pass_reco"] & sel["prior_pass_truth"])
    np.testing.assert_array_equal(
        p.w_data, (sel["pseudo_w_reco"].astype(float)
                   * sel["case__D1_m0.350__pseudo_distortion"])[p.s1_pseudo])
    X, _ = p.reco_matrix("prior")
    assert X.shape == (sel["prior_rows"].size, 6)
    np.testing.assert_array_equal(X[:, 4], sel["prior_rc_E_sum"].astype(np.float64))
    T4, _ = p.truth_matrix("truth4")
    T9, _ = p.truth_matrix("truth4_species")
    np.testing.assert_array_equal(T4[:, 0], sel["prior_truth_scalars"][:, 2].astype(np.float64))
    assert T9.shape[1] == 9
    np.testing.assert_array_equal(T9[:, 4], sel["prior_tr_n_p"].astype(np.float64))


def test_nonfinite_inputs_are_filled_and_counted_on_used_rows():
    sel = synthetic_selection()
    sel["prior_truth_scalars"][np.flatnonzero(sel["prior_pass_truth"])[:3], 3] = np.nan
    p = sd.build_problem(sel, "T0", "D1_m0.350")
    T, rec = p.truth_matrix("truth4")
    assert np.isfinite(T[p.pg_prior]).all()
    assert rec["true_q3"]["filled_rows"] == 3


def test_refusals():
    sel = synthetic_selection()
    bad = dict(sel)
    bad["case__D1_m0.350__pseudo_distortion"] = sel["case__D1_m0.350__pseudo_distortion"] * 1.1
    with pytest.raises(ValueError, match="unit-mean"):
        sd.build_problem(bad, "T0", "D1_m0.350")
    with pytest.raises(ValueError, match="share rows"):
        sd.build_problem(synthetic_selection(overlap=True), "T0", "D1_m0.350")
    with pytest.raises(KeyError):
        sd.build_problem(sel, "T0", "D5_nuwro")


# ------------------------------------------------------------------------------------------- #
# Efficiency-corrected OmniFold == efficiency-corrected binned IBU with a binned oracle classifier
# ------------------------------------------------------------------------------------------- #
@pytest.mark.parametrize("rule", ["carry", "efficiency_corrected"])
def test_omnifold_rules_match_binned_unfolding_with_oracle_classifier(rule):
    rng = np.random.default_rng(3)
    n, nd = 3000, 2500
    truth = rng.integers(0, 6, n)
    reco = np.clip(truth + rng.integers(-1, 2, n), 0, 4)
    pg = rng.random(n) < 0.9
    s1 = pg & (rng.random(n) < 0.3 + 0.1 * truth)
    w_t, w_r = rng.uniform(0.5, 1.5, n), rng.uniform(0.5, 1.5, n)
    r_d = rng.integers(0, 5, nd)
    w_d = rng.uniform(0.5, 2.0, nd)
    mode = se.IBU_MODE[rule]
    expected = list(bu.binned_omnifold(
        reco_bin_mc=reco, truth_bin_mc=truth, pass_reco_mc=s1, pass_gen_mc=pg, w_truth_mc=w_t,
        w_reco_mc=w_r, reco_bin_data=r_d, w_data=w_d, n_reco_bins=5, n_truth_bins=6,
        iterations=5, mode=mode))
    seen = []
    se.omnifold(X_reco_mc=reco[:, None].astype(float), X_reco_data=r_d[:, None].astype(float),
                X_gen_mc=truth[:, None].astype(float), pass_reco_mc=s1, pass_gen_mc=pg,
                w_truth_mc=w_t, w_reco_mc=w_r, w_data=w_d,
                make_step1=lambda k: so.BinnedOracleRatio(5),
                make_step2=lambda k: so.BinnedOracleRatio(6), iterations=5, seed=0,
                miss_rule=rule, callback=lambda r: seen.append((r["pull"].copy(),
                                                                r["push"].copy())))
    assert len(seen) == 5
    for (pull, push), ref in zip(seen, expected):
        np.testing.assert_allclose(pull, ref["pull"], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(push, ref["push"], rtol=1e-10, atol=1e-12)


# ------------------------------------------------------------------------------------------- #
# Scorer
# ------------------------------------------------------------------------------------------- #
def test_scorer_anchors_and_moves_away_direction():
    import scalar_scoring as ss
    sel = synthetic_selection(n=20000)
    p = sd.build_problem(sel, "T0", "D1_m0.350")
    sc = ss.Scorer(p)
    ones = np.ones(p.prior["rows"].size)
    s0 = sc.score(ones)
    assert s0["eavail"]["recovery"] == pytest.approx(0.0, abs=1e-12)
    assert s0["eavail"]["moves_away"] is False              # residual == injected, not greater
    # the exact distortion on the prior: the finite-sample oracle, far better than doing nothing
    assert sc.oracle["eavail"]["recovery"] > 0.8
    # pushing AGAINST the injected direction must be flagged
    wrong = np.where(p.pg_prior, 1.0 / p.oracle, 1.0)
    assert sc.score(wrong)["eavail"]["moves_away"] is True
    top = sc.score(p.oracle)["topology"]
    assert set(top) == {"class_p", "class_n", "joint_eavail_p", "joint_eavail_n"}
    with pytest.raises(ValueError):
        sc.score(ones[:-1])


def test_topology_recovery_form():
    import scalar_scoring as ss
    h_prior = np.array([1.0, 1.0])
    h_target = np.array([1.0, 3.0])
    r = ss.posthoc_recovery(h_target * 2, h_prior, h_target)
    assert r["recovery"] == pytest.approx(1.0)
    r = ss.posthoc_recovery(np.array([3.0, 1.0]), h_prior, h_target)
    assert r["moves_away"] and r["recovery"] < 0
    assert ss.posthoc_recovery(h_prior, h_prior, h_prior + 1e-9)["recovery"] is None


# ------------------------------------------------------------------------------------------- #
# Estimator wrappers on a small problem
# ------------------------------------------------------------------------------------------- #
def test_aussie_and_ibu_wrappers_return_aligned_pushes():
    pytest.importorskip("torch")
    sel = synthetic_selection(n=3000)
    p = sd.build_problem(sel, "T0", "D1_m0.350")
    push, info = se.run_aussie(p, truth_set="truth4_species", lam=1000.0, seed=1, lr=1e-3,
                               epochs=2)
    assert push.shape == p.prior["rows"].shape
    assert np.all(push[~p.pg_prior] == 1.0) and np.isfinite(push).all()
    steps = list(se.run_ibu_iter(p, "efficiency_corrected", 2))
    assert len(steps) == 2 and steps[-1]["push"].shape == p.prior["rows"].shape


# ------------------------------------------------------------------------------------------- #
# Extractor member guard and gather
# ------------------------------------------------------------------------------------------- #
def test_extractor_gathers_rows_and_refuses_real_data_members(tmp_path, monkeypatch):
    monkeypatch.setattr(ex, "CHUNK_ROWS", 7)
    x = np.arange(400, dtype=np.float32).reshape(100, 4)
    path = tmp_path / "inv.npz"
    np.savez_compressed(path, reco_scalars=x, data_muon=x, bkg_reco_scalars=x)
    rows = np.array([0, 3, 6, 7, 8, 50, 99])
    with zipfile.ZipFile(path) as zf:
        np.testing.assert_array_equal(ex.gather_member(zf, "reco_scalars", rows), x[rows])
        for name in ("data_muon", "bkg_reco_scalars", "measured_scalars"):
            with pytest.raises(PermissionError):
                ex.gather_member(zf, name, rows)
