"""score_design.py on synthetic runs with known truth, and on real predecessor runs if present."""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest

import score_design as sd
from conftest import make_run


def score(run, rf, ks=(1, 2), **kw):
    return sd.DesignScorer(run, sd.RowFeatures(rf), **kw).score(list(ks))


def by_k(res, k):
    return next(r for r in res["iterations"] if r["k"] == k)


def test_oracle_on_same_events_recovers_exactly_and_identity_scores_zero(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r", same_events=True)
    res = score(tmp_path / "r", rf)
    ident, orc = by_k(res, 1)["histograms"], by_k(res, 2)["histograms"]
    for name in ("eavail", "eavail_x_proton", "eavail_x_q3", "eavail@moderate", "eavail@good"):
        assert ident[name]["recovery"] == pytest.approx(0.0, abs=1e-12), name
        assert orc[name]["recovery"] == pytest.approx(1.0, abs=1e-12), name
        assert orc[name]["residual_l1"] == pytest.approx(0.0, abs=1e-12)
    # the E0 endpoint block is the aggregate E_avail histogram
    assert by_k(res, 2)["endpoints"]["E0"]["recovery"] == orc["eavail"]["recovery"]
    assert set(by_k(res, 2)["endpoints"]["E1"]) == set(sd.SCOREABLE_REGIONS)


def test_oracle_on_independent_events_is_below_one_and_matches_anchor(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r", same_events=False)
    res = score(tmp_path / "r", rf)
    r2 = by_k(res, 2)["histograms"]["eavail"]["recovery"]
    assert 0.5 < r2 < 1.0
    assert res["oracle_anchor"]["eavail"]["recovery"] == pytest.approx(r2, abs=1e-12)


def test_recovery_matches_historical_function():
    import common as cm
    rae = cm.historical()["rae"]
    rng = np.random.default_rng(3)
    for _ in range(20):
        p, u, t = (rng.uniform(0.1, 1, 7) for _ in range(3))
        ours = sd.recovery_stats(p, u, t)
        ref = rae.recovery(p, u, t)
        assert ours["recovery_raw"] == pytest.approx(ref["recovery"], abs=1e-14)
        assert ours["injected_l1"] == pytest.approx(ref["injected_l1"], abs=1e-15)


def test_undefined_below_three_floors():
    p = np.array([0.5, 0.5])
    t = np.array([0.5 + 0.0058, 0.5 - 0.0058])                  # injected L1 = 0.0116 < 0.012
    s = sd.recovery_stats(p, p, t)
    assert s["defined"] is False and s["recovery"] is None
    assert s["recovery_raw"] == pytest.approx(0.0)
    assert s["residual_l1"] == pytest.approx(0.0116)
    t2 = np.array([0.5 + 0.0062, 0.5 - 0.0062])                 # 0.0124 >= 0.012
    assert sd.recovery_stats(p, p, t2)["recovery"] == pytest.approx(0.0)


def test_null_case_reports_spurious_residuals(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "n", case="null", same_events=False)
    res = score(tmp_path / "n", rf)
    e7 = by_k(res, 2)["endpoints"]["E7"]
    h = by_k(res, 2)["histograms"]
    assert e7["eavail_spurious_l1"] == h["eavail"]["residual_l1"]
    assert e7["eavail_prior_l1"] == h["eavail"]["injected_l1"]
    # null: the oracle is the identity, so the oracle residual is the prior residual (null floor)
    assert res["oracle_anchor"]["eavail_x_proton"]["residual_l1"] == pytest.approx(
        e7["eavail_x_proton_prior_l1"], abs=1e-15)
    # a do-nothing injection is pure sampling noise; R is defined only above 3F
    assert (h["eavail"]["recovery"] is None) == (h["eavail"]["injected_l1"] < sd.UNDEFINED_BELOW)


def test_eavail_codes_follow_numpy_histogram():
    rng = np.random.default_rng(0)
    e = np.concatenate([rng.uniform(-1, 120, 10_000), sd.EAVAIL_EDGES, [np.nan, np.inf]])
    w = rng.uniform(0, 2, e.size)
    ref, _ = np.histogram(e[np.isfinite(e)], bins=sd.EAVAIL_EDGES, weights=w[np.isfinite(e)])
    ours = sd.hist(sd.eavail_codes(e), w, sd.N_EAV)
    np.testing.assert_allclose(ours, ref, rtol=1e-12)


def test_joint_histograms_marginalize_to_eavail(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r")
    res = score(tmp_path / "r", rf)
    h = by_k(res, 2)["histograms"]
    for name, (_, top) in sd.SPECIES.items():
        u = np.array(h[f"eavail_x_{name}"]["unfolded_norm"]).reshape(sd.N_EAV, top + 1)
        np.testing.assert_allclose(u.sum(1), h["eavail"]["unfolded_norm"], atol=1e-12)


def test_d4c_run_feeds_E4_on_the_proton_joint_histogram(tmp_path, features):
    rf, cols = features
    make_run(tmp_path / "d", case="D4c_p_up", same_events=True, features=cols)
    res = score(tmp_path / "d", rf)
    assert res["case"]["endpoint"] == "E4" and res["case"]["natural"] == "eavail_x_proton"
    e4 = by_k(res, 2)["endpoints"]["E4"]
    assert e4["recovery"] == pytest.approx(1.0, abs=1e-12)
    assert by_k(res, 1)["endpoints"]["E4"]["recovery"] == pytest.approx(0.0, abs=1e-12)


def test_classify_case_covers_the_library_and_refuses_unknown():
    lib = {"dev": ("E0", "eavail"), "D1_p0.350": ("E0", "eavail"), "D1_m0.350": ("E3", "eavail"),
           "D1_m0.700": ("E6", "eavail"), "D1_p0.175": ("E6", "eavail"),
           "D2_bump_c0.3": ("E6", "eavail"), "D2_bump_c1.0": ("E6", "eavail"),
           "D3_p0.35": ("E5", "eavail_x_q3"), "D3_m0.35": ("E6", "eavail_x_q3"),
           "D4a_pipm_up": ("E6", "eavail_x_pipm"), "D4b_pi0_up": ("E6", "eavail_x_pi0"),
           "D4c_p_up": ("E4", "eavail_x_proton"), "D4c_p_down": ("E6", "eavail_x_proton"),
           "D4d_n_up": ("E6", "eavail_x_neutron"), "D4d_n_down": ("E6", "eavail_x_neutron"),
           "D5_nuwro": ("E6", "eavail"), "D5_gibuu": ("E6", "eavail"),
           "D5p_nuwro": ("E6", "eavail"), "R1_x1.05+D1_p0.350": ("E6", "eavail"),
           "R1_x1.05_D1_p0.350": ("E6", "eavail"), "R1_x0.95+D1_p0.350": ("E6", "eavail"),
           "R2_x1.01+D1_p0.350": ("E6", "eavail"), "D1_p0.350+D4c_p_up": ("E6", "eavail_x_proton"),
           "null": ("E7", "eavail")}
    for case, (ep, nat) in lib.items():
        c = sd.classify_case(case)
        assert (c["endpoint"], c["natural"]) == (ep, nat), case
    with pytest.raises(ValueError):
        sd.classify_case("X9_whatever")
    with pytest.raises(ValueError):
        sd.classify_case("D4a_pipm_up+D4c_p_up")


def test_cross_check_passes_on_equal_and_refuses_on_differing_scores(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r")
    res = score(tmp_path / "r", rf)
    h2 = by_k(res, 2)["histograms"]

    def write_scores(delta):
        its = [{"k": k, "push": {
            "recovery": by_k(res, k)["histograms"]["eavail"]["recovery_raw"] + (delta if k == 2 else 0),
            "recovery_by_region": {r: by_k(res, k)["histograms"][f"eavail@{r}"]["recovery_raw"]
                                   for r in sd.SCOREABLE_REGIONS}}} for k in (1, 2)]
        (tmp_path / "r" / "scores.json").write_text(json.dumps({"iterations": its}))

    write_scores(1e-11)
    ok = sd.DesignScorer(tmp_path / "r", sd.RowFeatures(rf)).score([1, 2], True)
    assert ok["cross_check"]["performed"] and ok["cross_check"]["max_abs_diff"] <= 1e-9
    write_scores(2e-9)
    with pytest.raises(AssertionError):
        sd.DesignScorer(tmp_path / "r", sd.RowFeatures(rf)).score([1, 2])
    (tmp_path / "r" / "scores.json").unlink()
    with pytest.raises(ValueError):
        sd.DesignScorer(tmp_path / "r", sd.RowFeatures(rf)).score([1, 2], True)
    assert h2["eavail"]["recovery"] is not None


def test_bootstrap_member_target_excludes_pseudodata_poisson_weights(tmp_path, features):
    rf, _ = features
    info = make_run(tmp_path / "b", bootstrap=True)
    res = score(tmp_path / "b", rf)
    A = info["arrays"]
    keep = A["pseudo_pass_truth"] & np.isfinite(A["pseudo_truth"][:, 2])
    t, _ = np.histogram(A["pseudo_truth"][keep, 2], bins=sd.EAVAIL_EDGES,
                        weights=(A["pseudo_w_truth"] * A["pseudo_distortion"])[keep])
    np.testing.assert_allclose(by_k(res, 1)["histograms"]["eavail"]["target_norm"], t / t.sum(),
                               atol=1e-14)
    kb = A["prior_pass_truth"] & np.isfinite(A["prior_truth"][:, 2])
    p, _ = np.histogram(A["prior_truth"][kb, 2], bins=sd.EAVAIL_EDGES,
                        weights=(A["prior_w_truth"] * A["prior_bootstrap_weight"])[kb])
    np.testing.assert_allclose(by_k(res, 1)["histograms"]["eavail"]["unfolded_norm"], p / p.sum(),
                               atol=1e-14)
    assert res["cross_check"]["performed"] is False


def test_nonfinite_push_is_reported_not_scored(tmp_path, features):
    rf, _ = features
    n = 20_000
    bad = np.ones(n)
    bad[5] = np.nan
    bad[6] = -1.0
    make_run(tmp_path / "x", pushes={1: np.ones(n), 2: bad})
    res = score(tmp_path / "x", rf)
    r = by_k(res, 2)
    assert r["histograms"] is None and "non-finite" in r["not_scored"]
    assert r["stability"]["n_nonfinite_push_all_rows"] == 1
    assert r["stability"]["n_negative_truth_passing"] + r["stability"][
        "n_nonfinite_truth_passing"] >= 1


def test_missing_k_is_refused(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r")
    with pytest.raises(ValueError, match="not written"):
        score(tmp_path / "r", rf, ks=(3,))


# ------------------------------------------------------------------------------------------- #
# Real predecessor runs (rsynced locally; skipped when absent)
# ------------------------------------------------------------------------------------------- #
REAL = Path(os.environ.get("PFD_REAL_RUNS", "/private/tmp/claude-501/pfd-analysis"))
REAL_RUNS = ("final-C-F0", "stress-C-T0-D4c_p_up", "stress-CTL-T0-R1_x1.05_D1_p0.350")


@pytest.mark.skipif(not (REAL / "rf_extract.npz").exists(), reason="real runs not present")
@pytest.mark.parametrize("name", REAL_RUNS)
def test_real_run_reproduces_predecessor_scores(name):
    run = REAL / "runs" / name
    if not (run / "scores.json").exists():
        pytest.skip(f"{run} absent")
    res = sd.DesignScorer(run, sd.RowFeatures(REAL / "rf_extract.npz")).score([1, 2, 3], True)
    cc = res["cross_check"]
    assert cc["performed"] and len(cc["iterations"]) == 3
    assert cc["max_abs_diff"] <= 1e-9


def test_cli_main_writes_one_json_per_run(tmp_path, features):
    rf, _ = features
    make_run(tmp_path / "r1")
    make_run(tmp_path / "r2", seed=5)
    out = tmp_path / "out"
    assert sd.main(["--run", str(tmp_path / "r1"), str(tmp_path / "r2"), "--k", "1", "2",
                    "--row-features", str(rf), "--out-dir", str(out)]) == 0
    for n in ("r1", "r2"):
        doc = json.loads((out / f"{n}.design_scores.json").read_text())
        assert doc["schema"] == sd.SCHEMA and [r["k"] for r in doc["iterations"]] == [1, 2]
