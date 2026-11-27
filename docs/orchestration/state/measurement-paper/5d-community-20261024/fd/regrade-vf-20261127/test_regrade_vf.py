"""Tests for regrade_vf.py (REGRADE-VF-DECLARATION.md rev 1).

Synthetic arrays test the split, the bootstrap, the readings and every STOP. The committed inputs are read only for the
controls (C-PIN, C-F, C-DF, C-GAP at the data, C-L, and C-A0 against the already-published regrade16.json); no test
computes or prints a reading on the committed draws.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import regrade_vf as rv  # noqa: E402

Stop = rv.Stop
PHI = {"R1": 1.09, "R2": 1.29, "R3": 2.98}


def spd(n: int = 16, seed: int = 0, lam: np.ndarray | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    Q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    if lam is None:
        lam = np.geomspace(10.0, 0.01, n)
    return (Q * lam) @ Q.T


def pinv_nonnull(C: np.ndarray) -> tuple[np.ndarray, int]:
    lam, V = np.linalg.eigh(C)
    keep = lam > 1e-12 * lam.max()
    return (V[:, keep] / lam[keep]) @ V[:, keep].T, int(keep.sum())


def draws(n: int = 300, seed: int = 1, shift: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    C = spd(seed=seed + 10)
    rng = np.random.default_rng(seed)
    E = rng.multivariate_normal(np.full(16, shift), C, size=n)
    return E, C


# ------------------------------------------------------------------------------------------- section 2
def test_band_L_applies_phi_per_rank_band_and_commutes():
    lam = np.geomspace(10.0, 0.01, 16)
    C = spd(lam=lam)
    L = rv.band_L(C, PHI)
    assert np.allclose(L @ C, C @ L, atol=1e-12)
    V = L @ C @ L.T
    w, U = rv.ranked_eig(C)
    for name, lo, hi in rv.BANDS:
        for i in range(lo, hi):
            assert math.isclose(U[:, i] @ V @ U[:, i], PHI[name] * w[i], rel_tol=1e-10)


def test_rule_ii_is_psd_and_zero_at_phi_one():
    C = spd()
    assert np.allclose(rv.dF_rule_ii(C, {"R1": 1.0, "R2": 1.0, "R3": 1.0}), 0.0, atol=1e-14)
    assert np.linalg.eigvalsh(rv.dF_rule_ii(C, PHI)).min() > -1e-12


def test_ranked_eig_descends():
    w, _ = rv.ranked_eig(spd())
    assert np.all(np.diff(w) < 0)


@pytest.mark.parametrize("tie", [4, 8])
def test_gap_check_refuses_a_tie_across_a_band_edge(tie):
    lam = np.geomspace(10.0, 0.01, 16)
    lam[tie] = lam[tie - 1]
    with pytest.raises(Stop, match="C-GAP"):
        rv.gap_check(spd(lam=lam), "t")


def test_gap_check_passes_a_tie_inside_a_band():
    lam = np.geomspace(10.0, 0.01, 16)
    lam[1] = lam[0]
    g = rv.gap_check(spd(lam=lam), "t")
    assert set(g) == {"l4/l5-1", "l8/l9-1"}


def test_check_psd_refuses_negative_and_asymmetric():
    C = spd()
    rv.check_psd(C, "ok")
    with pytest.raises(Stop, match="C-PSD"):
        rv.check_psd(C - 1.01 * np.linalg.eigvalsh(C).min() * 2 * np.eye(16) - 0.5 * np.eye(16), "neg")
    A = C.copy()
    A[0, 1] += 1e-6 * np.abs(C).max()
    with pytest.raises(Stop, match="C-PSD"):
        rv.check_psd(A, "asym")


def test_rule_i_is_the_identity_at_f():
    f = np.linspace(1.0, 2.0, 16)
    D = spd(seed=3)
    assert np.allclose(rv.rc.carry_frac(D, f, f), D, rtol=0, atol=1e-15 * np.abs(D).max())


# ------------------------------------------------------------------------------------------- section 3
def test_split_matches_a_direct_computation():
    E, C = draws(shift=0.3)
    C_add = 0.2 * spd(seed=5)
    C_base = C + 0.1 * spd(seed=6)
    idx = np.random.default_rng(0).integers(0, 300, size=(rv.N_BOOT, 300))
    s = rv.split(E, C_base, C_add, idx)
    A, ndf = pinv_nonnull(C_base + C_add)
    n = 300
    eb = E.mean(0)
    S1 = np.cov(E.T, ddof=1)
    F = np.trace(A @ S1) / ndf
    B = eb @ A @ eb / ndf - F / n
    tau = np.trace(A @ C_add) / ndf
    M = np.mean(np.einsum("si,ij,sj->s", E, A, E)) / ndf
    assert ndf == 16
    assert math.isclose(s["F"], F, rel_tol=1e-10) and math.isclose(s["B"], B, rel_tol=1e-9)
    assert math.isclose(s["tau"], tau, rel_tol=1e-10) and math.isclose(s["M_prime"], M, rel_tol=1e-10)
    assert math.isclose(s["M_prime"], s["B"] + s["F"], rel_tol=1e-12)
    assert math.isclose(s["M_full"], s["B"] + s["F"] + s["tau"], rel_tol=1e-12)
    assert math.isclose(sum(s["shares"].values()), 1.0, rel_tol=1e-12)
    chi2 = np.einsum("si,ij,sj->s", E, A, E)
    assert math.isclose(s["SE"], chi2.std(ddof=1) / math.sqrt(n) / ndf, rel_tol=1e-10)
    assert s["ndf"] == 16 and s["n"] == 300
    assert s["readings"] == rv.readings(s["B"], s["F"], s["M_full"], s["SE"], s["se_boot"])
    assert s["R_chi2_reading_regrade"] == rv.rc.r_chi2(E, C_base, C_add)["reading"]


def test_tau_covers_c_add_only_not_the_base_inflation():
    E, C = draws()
    C_add = 0.2 * spd(seed=5)
    dF = 0.5 * spd(seed=7)
    idx = np.zeros((rv.N_BOOT, 300), int) + np.arange(300)
    s = rv.split(E, C + dF, C_add, idx)
    A, ndf = pinv_nonnull(C + dF + C_add)
    assert math.isclose(s["tau"], np.trace(A @ C_add) / ndf, rel_tol=1e-10)
    assert not math.isclose(s["tau"], np.trace(A @ (C_add + dF)) / ndf, rel_tol=1e-3)


def test_debiased_bias_is_near_zero_without_a_mean_error():
    vals = []
    for k in range(40):
        E, C = draws(seed=100 + k)
        idx = np.zeros((2, 300), int) + np.arange(300)
        vals.append(rv.split(E, C, np.zeros((16, 16)), idx)["B"])
    assert abs(np.mean(vals)) < 3 * np.std(vals) / math.sqrt(len(vals))


def test_bootstrap_replicate_matches_a_direct_resample():
    E, C = draws(shift=0.2)
    C_add = 0.2 * spd(seed=5)
    rng = np.random.default_rng(42)
    idx = rng.integers(0, 300, size=(rv.N_BOOT, 300))
    s = rv.split(E, C, C_add, idx)
    A, ndf = pinv_nonnull(C + C_add)
    Bb, Fb = [], []
    for row in idx:
        X = E[row]
        xb = X.mean(0)
        F = np.trace(A @ np.cov(X.T, ddof=1)) / ndf
        Fb.append(F)
        Bb.append(xb @ A @ xb / ndf - F / 300)
    Bb, Fb = np.array(Bb), np.array(Fb)
    assert math.isclose(s["se_boot"]["B"], Bb.std(ddof=1), rel_tol=1e-8)
    assert math.isclose(s["se_boot"]["F"], Fb.std(ddof=1), rel_tol=1e-8)
    assert math.isclose(s["se_boot"]["B_minus_F"], (Bb - Fb).std(ddof=1), rel_tol=1e-8)


def test_split_refuses_a_rank_deficient_matrix():
    E, C = draws()
    lam = np.geomspace(10.0, 0.01, 16)
    lam[-1] = 0.0
    with pytest.raises(Stop, match="C-RANK"):
        rv.split(E, spd(lam=lam), np.zeros((16, 16)), np.zeros((2, 300), int))


def test_split_refuses_when_the_identity_fails(monkeypatch):
    E, C = draws()
    real = rv.rc.r_chi2

    def bent(*a):
        r = real(*a)
        r["mean_error_part"] *= 1.001
        return r
    monkeypatch.setattr(rv.rc, "r_chi2", bent)
    with pytest.raises(Stop, match="C-ID"):
        rv.split(E, C, np.zeros((16, 16)), np.zeros((2, 300), int))


# ------------------------------------------------------------------------------------------- section 4
SE = {"B": 0.125, "F": 0.125, "B_minus_F": 0.125}   # binary-exact: 3 SE = 0.375 exactly


@pytest.mark.parametrize("B,want", [(0.376, "yes"), (0.375, "not resolved"), (-1.0, "not resolved")])
def test_bias_resolved_is_strictly_above_three_se(B, want):
    assert rv.readings(B, 0.0, 2.0, 0.125, SE)["bias_resolved"] == want


@pytest.mark.parametrize("B,F,want", [(1.0, 0.6, "bias larger"), (1.0, 0.625, "not separated"),
                                      (0.6, 1.0, "fluctuation larger"), (0.625, 1.0, "not separated"),
                                      (1.0, 1.0, "not separated")])
def test_bias_vs_fluctuation_is_three_se_of_the_difference(B, F, want):
    assert rv.readings(B, F, 2.0, 0.125, SE)["bias_vs_fluctuation"] == want


@pytest.mark.parametrize("M,want", [(1.376, "under-describes on average"), (1.375, "not shown"), (0.5, "not shown")])
def test_r_chi2_reading_is_regrades_rule(M, want):
    assert rv.readings(0.0, 0.0, M, 0.125, SE)["R_chi2"] == want
    assert rv.rc.read_rule(M, 0.125) == (want != "not shown")


def test_carry_sensitive_names_the_differing_readings():
    a = {"readings": {"R_chi2": "x", "bias_resolved": "yes", "bias_vs_fluctuation": "y"}}
    b = {"readings": {"R_chi2": "x", "bias_resolved": "not resolved", "bias_vs_fluctuation": "z"}}
    assert rv.carry_sensitive(a, b) == ["bias_resolved", "bias_vs_fluctuation"]
    assert rv.carry_sensitive(a, a) == []


# ------------------------------------------------------------------------------------------- controls on the committed inputs
@pytest.fixture(scope="module")
def committed():
    ops, ctl = rv.global_controls()
    r16 = json.loads(rv.PINS["regrade16"][0].read_text())["evaluations"]
    return ops, ctl, r16


def test_global_controls_pass_on_the_committed_blocks(committed):
    _, ctl, _ = committed
    assert ctl["C_L"]["C_e_infl"] <= rv.L_REL and ctl["C_L"]["L"] <= rv.L_REL
    assert ctl["C_DF"]["DeltaC_e_vs_difference"] <= rv.DF_REL


def test_block_controls_refuse_each_perturbation(committed):
    ops, _, _ = committed
    with np.load(rv.PINS["vf_block"][0]) as z:
        f, C_e, C_i, D = (np.asarray(z[k], float) for k in ("f", "C_e", "C_e_infl", "DeltaC_e"))
    L5 = json.loads(rv.PINS["blocks5d"][0].read_text())["fluctuation"]["L"]
    phi = ops["phi"]
    rv.block_controls(ops["f"], f, C_e, C_i, D, phi, L5)
    f2 = f.copy()
    f2[3] *= 1 + 1e-9
    with pytest.raises(Stop, match="C-F"):
        rv.block_controls(ops["f"], f2, C_e, C_i, D, phi, L5)
    D2 = D.copy()
    D2[2, 2] *= 1 + 1e-6
    with pytest.raises(Stop, match="C-DF"):
        rv.block_controls(ops["f"], f, C_e, C_i, D2, phi, L5)
    with pytest.raises(Stop, match="C-L"):
        rv.block_controls(ops["f"], f, C_e, C_i, D, {**phi, "R3": phi["R3"] * 1.001}, L5)
    L6 = np.array(L5)
    L6[0, 0] += 1e-6
    with pytest.raises(Stop, match="C-L"):
        rv.block_controls(ops["f"], f, C_e, C_i, D, phi, L6)
    dlt = np.zeros((16, 16))
    dlt[5, 5] = 1e-6 * np.abs(C_i).max()
    with pytest.raises(Stop, match="C-L: builder vs C_e_infl"):   # C_e_infl and DeltaC_e moved together: C-DF holds
        rv.block_controls(ops["f"], f, C_e, C_i + dlt, D + dlt, phi, L5)


@pytest.mark.parametrize("e", rv.EVALS)
def test_evaluation_controls_pass_and_a0_reproduces_regrade16(committed, e):
    ops, _, r16 = committed
    t, rd = e.split("/")
    cap = rv.load_capture(rv.PINS[f"capture_{t}_{rd}"][0])
    c, C_add, dF = rv.evaluation_controls(e, cap, ops, r16[e]["R_chi2"])
    assert max(c["C_A0"].values()) <= rv.A0_REL
    assert set(dF) == {"rule_i", "rule_ii"}
    assert np.array_equal(dF["rule_i"], rv.rc.carry_frac(ops["DeltaC_e"], cap["X_T"], ops["f"]))
    assert np.array_equal(dF["rule_ii"], rv.dF_rule_ii(cap["C_e"], ops["phi"]))
    assert set(c["C_GAP_T"]) == {"l4/l5-1", "l8/l9-1"}
    want = rv.rc.carry_frac(ops["C_resp"], cap["X_T"], ops["f"]) + rv.rc.carry_rel(ops["P_rel"], cap["X_T"])
    assert np.array_equal(C_add, want)
    assert set(c["C_PSD"]) == {"dF_rule_i", "C_rep_rule_i", "dF_rule_ii", "C_rep_rule_ii", "C_prime"}


def test_evaluation_controls_refuse_a_moved_a0_or_f(committed):
    ops, _, r16 = committed
    cap = rv.load_capture(rv.PINS["capture_g18_minus2"][0])
    bad = dict(r16["g18/minus2"]["R_chi2"])
    bad["tau"] *= 1 + 1e-9
    with pytest.raises(Stop, match="C-A0"):
        rv.evaluation_controls("g18/minus2", cap, ops, bad)
    cap2 = dict(cap)
    cap2["f"] = cap["f"] * (1 + 1e-9)
    with pytest.raises(Stop, match="C-F"):
        rv.evaluation_controls("g18/minus2", cap2, ops, r16["g18/minus2"]["R_chi2"])


def test_pinned_refuses_a_changed_file(tmp_path, monkeypatch):
    p = tmp_path / "x.json"
    p.write_text("{}")
    monkeypatch.setitem(rv.PINS, "regrade16", (p, "0" * 64))
    with pytest.raises(Stop, match="C-PIN"):
        rv.pinned("regrade16")


def test_run_stops_every_evaluation_on_a_pin_failure(tmp_path, monkeypatch):
    p = tmp_path / "x.json"
    p.write_text("{}")
    monkeypatch.setitem(rv.PINS, "blocks5d", (p, "0" * 64))
    out = rv.run()
    assert all(v["status"] == "STOP" and "C-PIN" in v["stop"] for v in out["evaluations"].values())
    assert set(out["evaluations"]) == set(rv.EVALS)


def test_main_refuses_an_existing_out(tmp_path):
    p = tmp_path / "r.json"
    p.write_text("x")
    assert rv.main(["--out", str(p)]) == 2
    assert p.read_text() == "x"


def test_constants_are_the_declarations():
    assert rv.N_BOOT == 2000 and rv.K_SE == 3.0 and rv.NDF == 16
    assert rv.BOOT_SEED == {"g18/minus2": 9_991_271, "g18/all": 9_991_272, "ar23/minus2": 9_991_273,
                            "ar23/all": 9_991_274}
    assert rv.BANDS == (("R1", 0, 4), ("R2", 4, 8), ("R3", 8, 16))
    assert rv.PRIMARY == ("g18/minus2", "ar23/minus2")
    assert rv.EVALS == rv.rc.EVALS_16


def synthetic_case(seed: int = 3):
    rng = np.random.default_rng(seed)
    f = np.linspace(1.0, 2.0, 16)
    X_T = f * rng.uniform(0.9, 1.1, 16)
    C_e = spd(seed=seed)
    C_T = C_e + 0.5 * spd(seed=seed + 1)
    E = rng.multivariate_normal(np.full(16, 0.2), C_T, size=300)
    ops = {"f": f, "P_rel": 0.01 * spd(seed=seed + 2) / 10, "C_resp": 0.1 * spd(seed=seed + 3),
           "DeltaC_e": 0.3 * spd(seed=seed + 4), "phi": PHI}
    cap = {"E": E, "X_T": X_T, "f": f, "C_T": C_T, "C_e": C_e}
    C_add = rv.rc.carry_frac(ops["C_resp"], X_T, f) + rv.rc.carry_rel(ops["P_rel"], X_T)
    committed = rv.rc.r_chi2(E, C_T, C_add)
    return cap, ops, committed, C_add


def test_evaluate_arrays_uses_each_matrix_and_the_same_resamples():
    cap, ops, committed, C_add = synthetic_case()
    rec = rv.evaluate_arrays("g18/minus2", cap, ops, committed)
    idx = np.random.default_rng(rv.BOOT_SEED["g18/minus2"]).integers(0, 300, size=(rv.N_BOOT, 300))
    dF_i = rv.rc.carry_frac(ops["DeltaC_e"], cap["X_T"], ops["f"])
    dF_ii = rv.dF_rule_ii(cap["C_e"], PHI)
    assert rec["before"] == rv.split(cap["E"], cap["C_T"], C_add, idx)
    assert rec["rule_i"] == rv.split(cap["E"], cap["C_T"] + dF_i, C_add, idx)
    assert rec["rule_ii"] == rv.split(cap["E"], cap["C_T"] + dF_ii, C_add, idx)
    assert rec["carry_sensitive"] == rv.carry_sensitive(rec["rule_i"], rec["rule_ii"])
    assert rec["status"] == "done"


def test_global_controls_refuse_an_inactive_band(tmp_path, monkeypatch):
    b = json.loads(rv.PINS["blocks5d"][0].read_text())
    b["fluctuation"]["trigger"]["R2"]["active"] = False
    p = tmp_path / "blocks5d.json"
    p.write_text(json.dumps(b))
    monkeypatch.setitem(rv.PINS, "blocks5d", (p, rv.rc.sha256(p)))
    with pytest.raises(Stop, match="not ACTIVE"):
        rv.global_controls()


# ------------------------------------------------------------------------------------------- fail-closed (read 1)
@pytest.mark.parametrize("bad", ["negdef", "negsemi", "nan", "inf", "empty", "upper-nan"])
def test_check_psd_fails_closed(bad):
    C = spd()
    if bad == "negdef":
        C = -np.eye(16)
    elif bad == "negsemi":
        C = np.diag([0.0] + [-1.0] * 15)
    elif bad == "nan":
        C[0, 0] = np.nan
    elif bad == "inf":
        C[0, 0] = np.inf
    elif bad == "empty":
        C = np.zeros((0, 0))
    elif bad == "upper-nan":
        C[0, 1] = np.nan
    with pytest.raises(Stop):
        rv.check_psd(C, bad)


def test_check_psd_threshold_is_the_declarations():
    lam = np.geomspace(10.0, 0.01, 16)
    lam[-1] = -5e-12 * lam[0]
    with pytest.raises(Stop, match="C-PSD"):
        rv.check_psd(spd(lam=lam), "just-negative")
    lam[-1] = -0.5e-12 * lam[0]
    rv.check_psd(spd(lam=lam), "within")
    C = spd()
    A = C.copy()
    A[0, 1] += 5e-12 * np.abs(C).max()
    with pytest.raises(Stop, match="C-PSD"):
        rv.check_psd(A, "asym-just-over")


@pytest.mark.parametrize("bad", ["diag-nan", "upper-nan", "upper-asym", "rank8", "small"])
def test_gap_check_fails_closed(bad):
    C = np.diag(np.geomspace(10.0, 0.01, 16))
    if bad == "diag-nan":
        C[0, 0] = np.nan
    elif bad == "upper-nan":
        C[0, 1] = np.nan
    elif bad == "upper-asym":
        C[0, 1] = 1e-3
    elif bad == "rank8":
        C = np.diag([10, 8, 6, 4, 2, 1.5, 1.2, 1.0] + [0.0] * 8)
    elif bad == "small":
        C = np.eye(4)
    with pytest.raises(Stop):
        rv.gap_check(C, bad)


def test_gap_threshold_is_the_declarations():
    lam = np.geomspace(10.0, 0.01, 16)
    lam[4] = lam[3] / (1 + 5e-10)
    with pytest.raises(Stop, match="C-GAP"):
        rv.gap_check(spd(lam=lam), "just-tied")
    lam[4] = lam[3] / (1 + 5e-9)
    rv.gap_check(spd(lam=lam), "just-separated")


@pytest.mark.parametrize("phi", [{"R1": float("nan"), "R2": 1.2, "R3": 2.0}, {"R1": 0.9, "R2": 1.2, "R3": 2.0}])
def test_band_L_refuses_a_bad_phi(phi):
    with pytest.raises(Stop, match="C-L"):
        rv.band_L(spd(), phi)


@pytest.mark.parametrize("bad", ["nan", "n1", "zero"])
def test_split_fails_closed(bad):
    E, C = draws()
    Z = np.zeros((16, 16))
    if bad == "nan":
        E[0, 0] = np.nan
    elif bad == "n1":
        E = E[:1]
    elif bad == "zero":
        E = np.zeros_like(E)
    with pytest.raises(Stop, match="C-FINITE"):
        rv.split(E, C, Z, np.zeros((2, E.shape[0]), int))


def test_split_shares_are_each_term_over_m_full():
    E, C = draws(shift=0.3)
    s = rv.split(E, C, 0.2 * spd(seed=5), np.random.default_rng(1).integers(0, 300, size=(50, 300)))
    for k in ("B", "F", "tau"):
        assert s["shares"][k] == s[k] / s["M_full"]
    assert s["B_raw"] - s["F"] / 300 == s["B"]


def test_readings_use_their_own_se_keys():
    se = {"B": 0.125, "F": 100.0, "B_minus_F": 0.25}
    r = rv.readings(0.5, 0.0, 1.25, 0.0625, se)
    assert r["bias_resolved"] == "yes"                     # 0.5 > 3*0.125, not 3*100 or 3*0.25
    assert r["bias_vs_fluctuation"] == "not separated"     # 0.5 < 3*0.25, though > 3*0.125
    assert r["R_chi2"] == "under-describes on average"     # 0.25 > 3*0.0625, though < 3*0.125
    r = rv.readings(0.7, 0.0, 1.1, 0.0625, {"B": 0.25, "F": 0.0, "B_minus_F": 0.125})
    assert r["bias_resolved"] == "not resolved" and r["bias_vs_fluctuation"] == "bias larger"
    assert r["R_chi2"] == "not shown"


def synthetic_blocks(lam=None):
    C_e = spd(seed=21, lam=lam)
    L = rv.band_L(C_e, PHI)
    C_i = L @ C_e @ L.T
    f = np.linspace(1.0, 2.0, 16)
    return f, C_e, C_i, C_i - C_e, L


def test_block_controls_pass_on_consistent_synthetic_blocks():
    f, C_e, C_i, D, L = synthetic_blocks()
    ctl = rv.block_controls(f, f, C_e, C_i, D, PHI, L)
    assert set(ctl["C_GAP_data"]) == {"l4/l5-1", "l8/l9-1"}


def test_block_controls_refuse_a_tie_at_the_data():
    lam = np.geomspace(10.0, 0.01, 16)
    lam[8] = lam[7]
    with pytest.raises(Stop, match="C-GAP"):
        rv.block_controls(*synthetic_blocks(lam)[:1], *synthetic_blocks(lam)[:1],
                          *synthetic_blocks(lam)[1:4], PHI, synthetic_blocks(lam)[4])


@pytest.mark.parametrize("which", ["f-nan", "f-zero", "Ci-nan", "L5-nan", "D-nan"])
def test_block_controls_fail_closed(which):
    f, C_e, C_i, D, L = synthetic_blocks()
    fv = f.copy()
    if which == "f-nan":
        fv[0] = np.nan
    elif which == "f-zero":
        f = f.copy()
        f[0] = 0.0
        fv = f.copy()
    elif which == "Ci-nan":
        C_i = C_i.copy()
        C_i[0, 0] = np.nan
    elif which == "L5-nan":
        L = L.copy()
        L[0, 0] = np.nan
    elif which == "D-nan":
        D = D.copy()
        D[0, 0] = np.nan
    with pytest.raises(Stop):
        rv.block_controls(f, fv, C_e, C_i, D, PHI, L)


def test_block_control_tolerances_are_the_declarations():
    f, C_e, C_i, D, L = synthetic_blocks()
    fv = f.copy()
    fv[2] *= 1 + 5e-12
    with pytest.raises(Stop, match="C-F"):
        rv.block_controls(f, fv, C_e, C_i, D, PHI, L)
    fv = f.copy()
    fv[2] *= 1 + 5e-13
    rv.block_controls(f, fv, C_e, C_i, D, PHI, L)
    d = np.zeros((16, 16))
    d[3, 3] = 5e-12 * np.abs(C_i).max()
    with pytest.raises(Stop, match="C-DF"):
        rv.block_controls(f, f, C_e, C_i, D + d, PHI, L)
    d[3, 3] = 5e-10 * np.abs(C_i).max()
    with pytest.raises(Stop, match="C-L: builder vs C_e_infl"):
        rv.block_controls(f, f, C_e, C_i + d, D + d, PHI, L)
    d[3, 3] = 5e-11 * np.abs(C_i).max()                # below L_REL: C-L holds (C-DF moves with it)
    rv.block_controls(f, f, C_e, C_i + d, D + d, PHI, L)
    L2 = L.copy()
    L2[0, 0] += 5e-10 * np.abs(L).max()
    with pytest.raises(Stop, match="C-L"):
        rv.block_controls(f, f, C_e, C_i, D, PHI, L2)
    L2 = L.copy()
    L2[0, 0] += 5e-11 * np.abs(L).max()
    rv.block_controls(f, f, C_e, C_i, D, PHI, L2)


def test_block_controls_check_carry_at_f(monkeypatch):
    f, C_e, C_i, D, L = synthetic_blocks()
    real = rv.rc.carry_frac
    monkeypatch.setattr(rv.rc, "carry_frac", lambda C, a, b: real(C, a, b) * (1 + 1e-9))
    with pytest.raises(Stop, match="C-DF"):
        rv.block_controls(f, f, C_e, C_i, D, PHI, L)


@pytest.mark.parametrize("field", rv.A0_FIELDS)
def test_a0_refuses_each_field_just_over_its_tolerance(committed, field):
    ops, _, r16 = committed
    cap = rv.load_capture(rv.PINS["capture_ar23_all"][0])
    bad = dict(r16["ar23/all"]["R_chi2"])
    bad[field] *= 1 + 5e-12
    with pytest.raises(Stop, match="C-A0"):
        rv.evaluation_controls("ar23/all", cap, ops, bad)


@pytest.mark.parametrize("bad", ["nan", "zero", "missing"])
def test_a0_refuses_a_bad_committed_field(committed, bad):
    ops, _, r16 = committed
    cap = rv.load_capture(rv.PINS["capture_ar23_all"][0])
    c = dict(r16["ar23/all"]["R_chi2"])
    if bad == "nan":
        c["SE"] = float("nan")
    elif bad == "zero":
        c["tau"] = 0.0
    else:
        del c["M_full"]
    with pytest.raises(Stop, match="C-A0"):
        rv.evaluation_controls("ar23/all", cap, ops, c)


def test_evaluation_controls_refuse_a_nan_capture(committed):
    ops, _, r16 = committed
    cap = dict(rv.load_capture(rv.PINS["capture_g18_all"][0]))
    cap["E"] = cap["E"].copy()
    cap["E"][3, 3] = np.nan
    with pytest.raises(Stop, match="C-FINITE"):
        rv.evaluation_controls("g18/all", cap, ops, r16["g18/all"]["R_chi2"])


def test_capture_f_tolerance_is_the_declarations(committed):
    ops, _, r16 = committed
    cap = dict(rv.load_capture(rv.PINS["capture_g18_all"][0]))
    cap["f"] = cap["f"].copy()
    cap["f"][5] *= 1 + 5e-12
    with pytest.raises(Stop, match="C-F"):
        rv.evaluation_controls("g18/all", cap, ops, r16["g18/all"]["R_chi2"])


def test_evaluation_controls_refuse_a_non_psd_rule_i():
    cap, ops, committed, _ = synthetic_case()
    ops = dict(ops)
    ops["DeltaC_e"] = -ops["DeltaC_e"]
    with pytest.raises(Stop, match="C-PSD: dF rule_i"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


def test_evaluation_controls_refuse_a_non_psd_c_rep(monkeypatch):
    cap, ops, committed, _ = synthetic_case()
    monkeypatch.setattr(rv, "dF_rule_ii", lambda C, phi: -2.0 * cap["C_T"] - 2.0 * spd(seed=9))
    with pytest.raises(Stop, match="C-PSD"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


def test_evaluation_controls_refuse_a_tie_at_t():
    cap, ops, committed, _ = synthetic_case()
    lam = np.geomspace(10.0, 0.01, 16)
    lam[4] = lam[3]
    cap = dict(cap)
    cap["C_e"] = spd(seed=3, lam=lam)
    with pytest.raises(Stop, match="C-GAP"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


def test_global_controls_refuse_a_string_active_or_bad_phi(tmp_path, monkeypatch):
    for mut in ({"active": "false"}, {"phi": float("nan")}, {"phi": 0.5}):
        b = json.loads(rv.PINS["blocks5d"][0].read_text())
        b["fluctuation"]["trigger"]["R1"].update(mut)
        p = tmp_path / "b.json"
        p.write_text(json.dumps(b))
        monkeypatch.setitem(rv.PINS, "blocks5d", (p, rv.rc.sha256(p)))
        with pytest.raises(Stop):
            rv.global_controls()


def test_run_isolates_an_evaluation_stop_and_writes_no_readings(monkeypatch):
    def fake(e, ops, committed):
        if e == "ar23/minus2":
            raise Stop("C-PSD: forced")
        return {"status": "done"}
    monkeypatch.setattr(rv, "evaluate", fake)
    out = rv.run()
    assert out["evaluations"]["ar23/minus2"] == {"status": "STOP", "stop": "C-PSD: forced"}
    assert all(out["evaluations"][e] == {"status": "done"} for e in rv.EVALS if e != "ar23/minus2")


def test_run_records_an_io_error_as_a_stop(monkeypatch):
    def fake(e, ops, committed):
        raise OSError("gone")
    monkeypatch.setattr(rv, "evaluate", fake)
    out = rv.run()
    assert all(v["status"] == "STOP" and "OSError" in v["stop"] for v in out["evaluations"].values())


def test_main_exit_codes_and_refuses_nan(tmp_path, monkeypatch):
    monkeypatch.setattr(rv, "run", lambda: {"evaluations": {e: {"status": "done"} for e in rv.EVALS}})
    assert rv.main(["--out", str(tmp_path / "a.json")]) == 0
    monkeypatch.setattr(rv, "run", lambda: {"evaluations": {"x": {"status": "STOP"}}})
    assert rv.main(["--out", str(tmp_path / "b.json")]) == 1
    monkeypatch.setattr(rv, "run", lambda: {"evaluations": {"x": {"status": "done", "v": float("nan")}}})
    with pytest.raises(ValueError):
        rv.main(["--out", str(tmp_path / "c.json")])


def test_main_refuses_a_dangling_symlink(tmp_path):
    p = tmp_path / "r.json"
    p.symlink_to(tmp_path / "nowhere.json")
    assert rv.main(["--out", str(p)]) == 2


def test_tolerances_are_the_declarations():
    assert (rv.A0_REL, rv.F_REL, rv.DF_REL, rv.L_REL, rv.GAP_MIN, rv.SYM_REL, rv.PSD_REL, rv.ID_REL) == \
        (1e-12, 1e-12, 1e-12, 1e-10, 1e-9, 1e-12, 1e-12, 1e-12)
    assert rv.A0_FIELDS == ("M_prime", "SE", "mean_error_part", "spread_part", "tau", "M_full")


def test_evaluation_controls_refuse_a_non_psd_c_prime(monkeypatch):
    cap, ops, committed, C_add = synthetic_case()
    w, U = np.linalg.eigh(cap["C_T"] + C_add)
    u = U[:, -1]
    cap = dict(cap)
    cap["C_T"] = cap["C_T"] - 2.0 * w[-1] * np.outer(u, u)        # C' gets one negative mode
    g = 4.0 * w[-1] * np.outer(u, u)                               # each dF covers it, so each C_rep is PSD
    r = cap["X_T"] / ops["f"]
    ops = dict(ops)
    ops["DeltaC_e"] = g / np.outer(r, r)
    monkeypatch.setattr(rv, "dF_rule_ii", lambda C, phi: g)
    committed = rv.rc.r_chi2(cap["E"], cap["C_T"], C_add)
    with pytest.raises(Stop, match="C-PSD: C'"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


def test_evaluation_controls_refuse_a_non_psd_c_rep_rule_i():
    cap, ops, committed, C_add = synthetic_case()
    w, U = np.linalg.eigh(cap["C_T"] + C_add)
    cap = dict(cap)
    cap["C_T"] = cap["C_T"] - 2.0 * w[-1] * np.outer(U[:, -1], U[:, -1])   # dF stays PSD; C_rep does not
    committed = rv.rc.r_chi2(cap["E"], cap["C_T"], C_add)
    with pytest.raises(Stop, match="C-PSD: C_rep rule_i"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


@pytest.mark.parametrize("x,want", [(0.5, True), (1.0, True), (1.5, False), (float("nan"), False),
                                    (float("inf"), False), (float("-inf"), False)])
def test_within_fails_closed(x, want):
    assert rv.within(x, 1.0) is want


def test_gap_check_names_a_non_positive_edge_eigenvalue():
    with pytest.raises(Stop, match="non-positive"):
        rv.gap_check(np.diag([10, 8, 6, 4, 2, 1.5, 1.2, 1.0] + [0.0] * 8), "rank8")


def test_evaluation_controls_refuse_a_degenerate_e():
    cap, ops, committed, _ = synthetic_case()
    cap = dict(cap)
    cap["E"] = np.zeros_like(cap["E"])
    with pytest.raises(Stop, match="C-FINITE"):
        rv.evaluation_controls("g18/minus2", cap, ops, committed)


def test_run_records_an_unreadable_regrade16_as_a_stop(monkeypatch):
    monkeypatch.setattr(rv, "global_controls", lambda: ({"phi": {}}, {}))
    monkeypatch.setitem(rv.PINS, "regrade16", (Path("/nonexistent/regrade16.json"), "0" * 64))
    out = rv.run()
    assert all(v["status"] == "STOP" for v in out["evaluations"].values())


def test_split_passes_its_own_terms_to_readings(monkeypatch):
    E, C = draws(shift=0.3)
    C_add = 0.2 * spd(seed=5)
    seen = {}
    real = rv.readings

    def spy(B, F, M_full, SE, se):
        seen.update(B=B, F=F, M_full=M_full, SE=SE, se=dict(se))
        return real(B, F, M_full, SE, se)
    monkeypatch.setattr(rv, "readings", spy)
    s = rv.split(E, C, C_add, np.random.default_rng(2).integers(0, 300, size=(50, 300)))
    r = rv.rc.r_chi2(E, C, C_add)
    assert seen == {"B": s["B"], "F": s["F"], "M_full": s["M_full"], "SE": r["SE"], "se": s["se_boot"]}
