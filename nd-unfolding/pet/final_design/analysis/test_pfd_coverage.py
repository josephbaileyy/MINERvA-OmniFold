"""coverage.py: a procedure calibrated by construction covers at nominal; C1-C5 edge cases."""
from __future__ import annotations

import json

import numpy as np
import pytest

import coverage as cov
import inference as inf


def calibrated(R, nb=7, B=6, sigma=0.01, scale=1.0, seed=0):
    """members = target + delta + sigma z_b, delta ~ N(0, sigma^2 (1 - 1/B)): then
    (mean - target) / member-sd is exactly t(B-1), so mean +/- t x sd covers at nominal.
    `scale` multiplies the member spread only (scale > 1 over-covers, < 1 under-covers)."""
    rng = np.random.default_rng(seed)
    target = rng.dirichlet(np.ones(nb) * 20, size=R)
    delta = rng.normal(0, sigma * np.sqrt(1 - 1 / B), (R, 1, nb))
    z = rng.normal(0, sigma, (R, B, nb))
    z = z - z.mean(axis=1, keepdims=True)
    zbar = rng.normal(0, sigma / np.sqrt(B), (R, 1, nb))
    members = target[:, None, :] + delta + zbar + scale * z
    prior = np.repeat((target - 0.02)[:, None, :], B, axis=1)
    return members, target, prior


def test_calibrated_procedure_covers_at_nominal():
    m, t, p = calibrated(3000)
    out = cov.coverage_arrays(m, t, 0.05, p)
    for level in ("0.68", "0.95"):
        pooled = out["levels"][level]["pooled"]["point"]
        assert pooled == pytest.approx(float(level), abs=0.01), level
        assert np.allclose(out["levels"][level]["per_bin_coverage"], float(level), atol=0.03)
    assert np.allclose(out["per_bin_pull_sd"], np.sqrt(5 / 3), rtol=0.08)   # t(5) sd
    assert np.allclose(out["per_bin_bias"], 0, atol=1e-3)


def test_half_width_is_t_times_member_sd_not_sd_of_mean():
    m = np.zeros((2, 6, 1))
    m[:, :, 0] = [0, 1, 2, 3, 4, 5]
    out = cov.coverage_arrays(m, np.full((2, 1), 2.5), 0.05)
    sd = np.std([0, 1, 2, 3, 4, 5], ddof=1)
    from scipy import stats
    assert out["levels"]["0.95"]["per_bin_mean_half_width"][0] == pytest.approx(
        stats.t.ppf(0.975, 5) * sd)


def rules_for(m, t, p, look=1, looks=2):
    dev = cov.coverage_arrays(m, t, inf.per_bound_alpha(1, looks), p)
    regions = {r: dev for r in ("low_acceptance", "moderate", "good")}
    return cov.rules(dev, regions, dev, look, looks)


def test_rules_pass_for_calibrated_and_fail_otherwise():
    r = rules_for(*calibrated(120, seed=1))
    assert r["C1"]["verdict"] == "PASS", r["C1"]
    assert r["C2"]["verdict"] == "PASS" and r["C3"]["verdict"] == "PASS"
    assert r["C5"]["verdict"] == "PASS"
    over = rules_for(*calibrated(120, scale=3.0, seed=1))      # trivially conservative
    assert over["C1"]["verdict"] == "FAIL"
    under = rules_for(*calibrated(120, scale=0.4, seed=1))     # under-covering
    assert under["C1"]["verdict"] == "FAIL" and under["C2"]["verdict"] == "FAIL"


def test_c4_width_and_top_bin_rule():
    m, t, p = calibrated(120, seed=2)
    r = rules_for(m, t, p)
    c4 = r["C4"]
    # injected displacement of every bin is 0.02 by construction -> top-bin bound 0.01
    assert c4["numbers"]["top_bin_bound_from_rule"] == pytest.approx(0.01)
    hw_top = c4["numbers"]["per_bin_mean_half_width_95"][-1]
    assert (c4["verdict"] == "PASS") == (hw_top <= 0.01 and all(
        h <= 2.5 * s for h, s in zip(c4["numbers"]["per_bin_mean_half_width_95"],
                                     c4["numbers"]["per_bin_empirical_sd"])))
    assert hw_top > 0.01 and c4["verdict"] == "FAIL"           # sigma 0.01 -> hw ~ 0.026


def test_missing_inputs_are_incomplete_and_carry_over():
    r = cov.rules(None, None, None, 1, 2)
    assert all(v["verdict"] == "INCOMPLETE" for v in r.values())
    prev = {"C1": {"verdict": "PASS", "rule": "C1"}, "C2": {"verdict": "CONTINUE"}}
    cur = cov.carry_over({"C1": {"verdict": "FAIL"}, "C2": {"verdict": "PASS"}}, prev)
    assert cur["C1"]["verdict"] == "PASS" and cur["C1"]["carried_from_look"] == 1
    assert cur["C2"]["verdict"] == "PASS"


def member_doc(path, case, k, hists, rows="a0"):
    doc = {"run_name": path.stem, "case": {"case": case}, "identity": {"pseudo_rows_sha256": rows},
           "iterations": [{"k": k, "histograms": hists}]}
    path.write_text(json.dumps(doc))
    return str(path)


def test_load_replicates_checks_members(tmp_path):
    m, t, p = calibrated(2, B=6, seed=3)
    entries = []
    for r in range(2):
        files = [member_doc(tmp_path / f"r{r}b{b}.json", "D1_p0.350", 3,
                            {"eavail": {"unfolded_norm": m[r, b].tolist(),
                                        "target_norm": t[r].tolist(),
                                        "prior_norm": p[r, b].tolist()}}) for b in range(6)]
        entries.append({"replicate": f"c{r}", "members": files})
    L = cov.load_replicates(entries, 3, "eavail", "dev")
    assert L["members"].shape == (2, 6, 7)
    with pytest.raises(ValueError, match="members"):
        cov.load_replicates([{"replicate": "x", "members": entries[0]["members"][:5]}], 3,
                            "eavail", "D1_p0.350")
    bad = entries[0]["members"][:5] + [member_doc(
        tmp_path / "bad.json", "D1_p0.350", 3,
        {"eavail": {"unfolded_norm": m[0, 0].tolist(), "target_norm": (t[0] * 1.01).tolist(),
                    "prior_norm": p[0, 0].tolist()}})]
    with pytest.raises(ValueError, match="targets differ"):
        cov.load_replicates([{"replicate": "x", "members": bad}], 3, "eavail", "D1_p0.350")
    with pytest.raises(ValueError, match="cases"):
        cov.load_replicates(entries, 3, "eavail", "D4c_p_up")
