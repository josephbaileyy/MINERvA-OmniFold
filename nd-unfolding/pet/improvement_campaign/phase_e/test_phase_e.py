"""Tests for the Phase-E distortion library, replicate drawing and pool-level scoring.

Run: ``python -m pytest nd-unfolding/pet/improvement_campaign/phase_e -q``

Every distortion is checked for the four properties Amendment 1 needs to mean anything: the
identity at zero magnitude, the stated sign, the stated normalization, and determinism. The D5
merge rule is checked on hand-made columns with known answers, the replicate draws for exact
sizes, disjointness, reproducibility under row permutation and refusal past the pool's capacity,
and the pool-level scorer for bit-equality with the historical `score_campaign.score_run` mirror.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
for _p in (HERE, HERE.parent / "phase_b" / "scalar"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import common as cm  # noqa: E402
import distortions as dist  # noqa: E402
import replicates as rp  # noqa: E402
import scalar_common as scm  # noqa: E402

RNG = np.random.default_rng(20260922)


def _truth(n=5000):
    e = RNG.gamma(1.5, 1.2, n)
    q3 = e + RNG.gamma(2.0, 0.6, n)
    return {"eavail": e, "q3": q3, "pt": RNG.uniform(0, 4.0, n), "ppar": RNG.uniform(1.5, 20.0, n),
            "n_pipm": RNG.poisson(0.8, n), "n_pi0": RNG.poisson(0.4, n),
            "n_p": RNG.poisson(1.2, n), "n_n": RNG.poisson(1.0, n)}


def _reco(n=4000):
    pt = RNG.uniform(0.05, 3.5, n)
    ppar = RNG.uniform(1.6, 25.0, n)
    q0 = RNG.gamma(2.0, 0.8, n)
    tok = np.abs(RNG.normal(0.3, 0.2, (n, dist.N_TOKENS)))
    tok[RNG.random((n, dist.N_TOKENS)) < 0.3] = 0.0
    return {"pt": pt, "ppar": ppar, "eavail": 0.8 * q0, "q3": dist.reco_q3(pt, ppar, q0),
            "tok_E": tok}


def _identity(n, offset=0):
    return np.stack([np.full(n, 12), np.arange(n) // 100 + 1,
                     np.arange(n) + offset], axis=1).astype(np.int64)


# ------------------------------------------------------------------------------------------- #
# Distortion kernels
# ------------------------------------------------------------------------------------------- #
def test_zero_magnitude_is_the_identity():
    t = _truth()
    assert np.allclose(dist.clipped_exp_tilt(t["eavail"], 0.0, 1.0, 2.0), 1.0)
    assert np.allclose(dist.gaussian_bump(t["eavail"], 0.0, 0.3, 0.15), 1.0)
    assert np.allclose(dist.multiplicity_weight(t["n_pipm"], 1.0), 1.0)
    r = _reco()
    for out in (dist.hadronic_scale(r, 1.0), dist.muon_scale(r, 1.0),
                dist.cluster_smear(r, 0.0, dist.token_noise(_identity(len(r["pt"]))))):
        for key in ("pt", "ppar", "eavail", "tok_E"):
            assert np.allclose(out[key], r[key]), key
        assert np.allclose(out["q3"], r["q3"], rtol=1e-9, atol=1e-9)


def test_truth_weights_have_the_stated_sign_and_shape():
    t = _truth()
    up = dist.clipped_exp_tilt(t["eavail"], 0.35, dist.D1_P50_GEV, dist.D1_IQR_GEV)
    down = dist.clipped_exp_tilt(t["eavail"], -0.35, dist.D1_P50_GEV, dist.D1_IQR_GEV)
    assert np.corrcoef(t["eavail"], up)[0, 1] > 0.5
    assert np.corrcoef(t["eavail"], down)[0, 1] < -0.5
    assert np.allclose(up * down, 1.0, atol=1e-12)                    # exact opposites
    assert up.max() <= np.exp(0.35 * dist.TILT_CLIP_Z) + 1e-12        # the coordinate is clipped
    bump = dist.gaussian_bump(t["eavail"], 0.5, 1.0, 0.4)
    near = np.abs(t["eavail"] - 1.0) < 0.1
    assert bump[near].mean() > 1.45 and bump[t["eavail"] > 4.0].max() < 1.001
    assert np.all(np.diff(dist.multiplicity_weight(np.arange(6), 1.3)) > 0)
    assert np.all(np.diff(dist.multiplicity_weight(np.arange(6), 1 / 1.3)) < 0)


def test_d3_uses_the_ratio_and_ignores_unusable_q3():
    e = np.array([1.0, 2.0, 3.0, 4.0])
    q3 = np.array([2.0, 4.0, 0.0, np.nan])
    w = dist.clipped_exp_tilt(dist.eavail_over_q3(e, q3), 0.35, 0.5, 0.2)
    assert np.isclose(w[0], w[1])                    # same ratio -> same weight
    assert np.allclose(w[2:], 1.0)                   # q3 <= 0 / non-finite -> weight 1


def test_normalization_is_unit_mean_over_the_sample():
    t = _truth()
    w = dist.normalize_unit_mean(dist.clipped_exp_tilt(t["eavail"], 0.7, dist.D1_P50_GEV,
                                                       dist.D1_IQR_GEV))
    assert np.isclose(w.mean(), 1.0)
    with pytest.raises(ValueError):
        dist.normalize_unit_mean(np.array([1.0, -1.0]))


def test_determinism_and_identity_keying():
    t = _truth()
    a = dist.clipped_exp_tilt(t["eavail"], 0.35, dist.D1_P50_GEV, dist.D1_IQR_GEV)
    b = dist.clipped_exp_tilt(t["eavail"], 0.35, dist.D1_P50_GEV, dist.D1_IQR_GEV)
    assert np.array_equal(a, b)
    ident = _identity(4000)
    n1 = dist.token_noise(ident)
    perm = RNG.permutation(len(ident))
    n2 = dist.token_noise(ident[perm])
    assert np.array_equal(n1[perm], n2)              # keyed by identity, not by position
    assert n1.shape == (4000, dist.N_TOKENS)
    assert abs(n1.mean()) < 0.05 and abs(n1.std() - 1.0) < 0.05


def test_recoq3_inversion_roundtrips():
    r = _reco()
    q0, bad = dist.recoil_q0(r["pt"], r["ppar"], r["q3"])
    assert not bad.any()
    assert np.allclose(dist.reco_q3(r["pt"], r["ppar"], q0), r["q3"], rtol=1e-10, atol=1e-10)


def test_r1_r2_r3_scale_exactly_what_they_claim():
    r = _reco()
    q0, _ = dist.recoil_q0(r["pt"], r["ppar"], r["q3"])
    for s in (1.05, 0.95):
        out = dist.hadronic_scale(r, s)
        assert np.allclose(out["eavail"], s * r["eavail"])
        assert np.allclose(out["tok_E"], s * r["tok_E"])
        assert np.allclose(out["pt"], r["pt"]) and np.allclose(out["ppar"], r["ppar"])
        assert np.allclose(out["q3"], dist.reco_q3(r["pt"], r["ppar"], s * q0))
        assert ((out["q3"] > r["q3"]) == (s > 1)).all()
    for s in (1.01, 0.99):
        out = dist.muon_scale(r, s)
        assert np.allclose(out["pt"], s * r["pt"]) and np.allclose(out["ppar"], s * r["ppar"])
        assert np.allclose(out["eavail"], r["eavail"]) and np.allclose(out["tok_E"], r["tok_E"])
        assert np.allclose(out["q3"], dist.reco_q3(s * r["pt"], s * r["ppar"], q0))
    noise = dist.token_noise(_identity(len(r["pt"])))
    out = dist.cluster_smear(r, 0.10, noise)
    moved = r["tok_E"] != 0
    assert np.allclose(out["tok_E"][~moved], 0.0)                       # pads stay pads
    ratio = out["tok_E"][moved] / r["tok_E"][moved]
    assert abs(ratio.mean() - 1.0) < 0.01 and abs(ratio.std() - 0.10) < 0.01
    rho = np.where(r["tok_E"].sum(1) > 0, out["tok_E"].sum(1) / np.maximum(r["tok_E"].sum(1), 1e-12), 1.0)
    assert np.allclose(out["eavail"], rho * r["eavail"])


def test_r3_leaves_an_event_without_stored_energy_alone():
    r = _reco(10)
    r["tok_E"][:] = 0.0
    out = dist.cluster_smear(r, 0.10, dist.token_noise(_identity(10)))
    assert np.allclose(out["eavail"], r["eavail"]) and np.allclose(out["q3"], r["q3"])


# ------------------------------------------------------------------------------------------- #
# D5 table
# ------------------------------------------------------------------------------------------- #
def test_integer_counts_recovers_event_counts():
    counts = np.array([[[3.0, 0.0, 17.0]]])
    assert np.array_equal(dist.integer_counts(counts * 2.5e-40), counts)
    with pytest.raises(ValueError):
        dist.integer_counts(np.array([[[1.0, 1.5001]]]))


def test_merge_column_merges_only_what_fails_and_reports_the_unresolvable():
    good = np.array([100.0, 100.0, 100.0])
    err = good * 0.01
    groups, resolved = dist.merge_column(good, err, good, err)
    assert groups == [[0], [1], [2]] and resolved
    x = np.array([100.0, 100.0, 1.0])                      # top bin at 100% stat error
    ex = np.array([1.0, 1.0, 1.0])
    groups, resolved = dist.merge_column(x, ex, x, ex)
    assert groups == [[0], [1, 2]] and resolved
    bad = np.array([1.0, 1.0])
    groups, resolved = dist.merge_column(bad, bad, bad, bad)
    assert groups == [[0, 1]] and not resolved             # fully merged and still > 30 %
    zero = np.array([0.0, 100.0])
    groups, _ = dist.merge_column(zero, np.array([0.0, 1.0]), np.array([100.0, 100.0]),
                                  np.array([1.0, 1.0]))
    assert groups == [[0, 1]]                              # an empty bin cannot stand alone


def test_generator_weight_lookup_and_out_of_range():
    table = {"edges": {"pt": [0.0, 1.0, 2.0], "pparallel": [1.5, 3.0], "eavail": [0.0, 1.0]},
             "weight": [[[2.0]], [[3.0]]]}
    w, inside = dist.generator_weight(np.array([0.5, 1.5, 2.0, 2.5, np.nan]),
                                      np.array([2.0, 2.0, 2.0, 2.0, 2.0]),
                                      np.array([0.5, 0.5, 0.5, 0.5, 0.5]), table)
    assert np.array_equal(w, [2.0, 3.0, 3.0, 1.0, 1.0])    # last bin closes on the right
    assert np.array_equal(inside, [True, True, True, False, False])


@pytest.mark.skipif(not dist.D5_CALIBRATION.exists(), reason="no committed D5 tables")
def test_committed_d5_tables_are_self_consistent():
    payload = json.loads(dist.D5_CALIBRATION.read_text())
    for kind in ("tables", "tables_post_hoc"):
        for gen, t in payload[kind].items():
            w = np.asarray(t["weight"])
            assert w.shape == (14, 16, 7)
            assert w.min() >= dist.D5_CLIP[0] - 1e-12 and w.max() <= dist.D5_CLIP[1] + 1e-12
            assert t["table_sha256"] == dist._canonical_sha(t["weight"])
            for i, j in t["stats"]["unresolved_columns"]:
                assert np.allclose(w[i, j], 1.0)


# ------------------------------------------------------------------------------------------- #
# Registry
# ------------------------------------------------------------------------------------------- #
def test_registry_covers_amendment_1_and_hashes_its_parameters():
    reg = dist.registry()
    families = {d.family for d in reg.values()}
    assert {"D1", "D2", "D4", "R1", "R2", "R3"} <= families
    assert sum(d.family == "D1" for d in reg.values()) == 6
    assert sum(d.family == "D2" for d in reg.values()) == 2
    assert sum(d.family == "D4" for d in reg.values()) == 8
    assert sum(d.kind == "reco_transform" for d in reg.values()) == 5
    hashes = {d.id: d.content_hash() for d in reg.values()}
    assert len(set(hashes.values())) == len(hashes)
    assert hashes["D1_p0.350"] == reg["D1_p0.350"].content_hash()      # stable
    moved = dist.Distortion("D1_p0.350", "D1", "truth_weight",
                            dist._p(amplitude=0.3500001, p50=dist.D1_P50_GEV,
                                    iqr=dist.D1_IQR_GEV, clip_z=dist.TILT_CLIP_Z), "x")
    assert moved.content_hash() != hashes["D1_p0.350"]


def test_cases_pair_every_reco_distortion_with_the_null_and_with_d1():
    reg = dist.registry()
    cases = dist.cases(reg)
    for d in reg.values():
        if d.kind == "reco_transform":
            assert cases[d.id].truth is None
            combined = cases[f"{d.id}+{dist.COMBINED_WITH}"]
            assert combined.truth.id == dist.COMBINED_WITH and combined.reco.id == d.id
    assert len({c.content_hash() for c in cases.values()}) == len(cases)


def test_distortion_dispatch_matches_the_kernels():
    reg = dist.registry()
    t = _truth()
    assert np.allclose(reg["D1_p0.350"].truth_weight(t),
                       dist.clipped_exp_tilt(t["eavail"], 0.35, dist.D1_P50_GEV, dist.D1_IQR_GEV))
    assert np.allclose(reg["D4a_pipm_up"].truth_weight(t),
                       dist.multiplicity_weight(t["n_pipm"], 1.3))
    with pytest.raises(TypeError):
        reg["R1_x1.05"].truth_weight(t)
    with pytest.raises(TypeError):
        reg["D1_p0.350"].transform(_reco())
    with pytest.raises(ValueError):
        reg["R3_s0.10"].transform(_reco())            # R3 refuses to invent its own noise


# ------------------------------------------------------------------------------------------- #
# Replicates
# ------------------------------------------------------------------------------------------- #
def test_uniform_hash_is_the_campaign_hash():
    sys.path.insert(0, str(HERE.parent.parent / "configuration_comparison"))
    import stage_splits  # noqa: E402
    ident = _identity(500)
    for seed in (0, 12345, -7):
        assert np.array_equal(rp.uniform_hash(ident, seed), stage_splits.uniform_hash(ident, seed))


def _pool(n=20000):
    rows = np.sort(RNG.choice(10_000_000, n, replace=False)).astype(np.int64)
    return rows, _identity(n, offset=1000)


def test_draws_are_exact_disjoint_and_reproducible():
    rows, ident = _pool()
    design = rp.ReplicateDesign("T", "test", n_prior=3000, n_pseudo=2000)
    reps, record = rp.draw_replicates(design, [0, 1, 2], rows, ident)
    for rep in reps:
        assert rep.prior_rows.size == 3000 and rep.pseudo_rows.size == 2000
        assert np.intersect1d(rep.prior_rows, rep.pseudo_rows).size == 0
        assert np.isin(rep.prior_rows, rows).all() and np.isin(rep.pseudo_rows, rows).all()
    allrows = np.concatenate([np.concatenate([r.prior_rows, r.pseudo_rows]) for r in reps])
    assert np.unique(allrows).size == allrows.size                     # disjoint ACROSS replicates
    assert record["overlap"]["max_pairwise_fraction"] == 0.0
    perm = RNG.permutation(rows.size)
    again, _ = rp.draw_replicates(design, [0, 1, 2], rows[perm], ident[perm])
    for a, b in zip(reps, again):
        assert np.array_equal(np.sort(a.prior_rows), np.sort(b.prior_rows))
        assert np.array_equal(np.sort(a.pseudo_rows), np.sort(b.pseudo_rows))


def test_replicates_are_different_draws_and_the_salt_decides():
    rows, ident = _pool()
    design = rp.ReplicateDesign("T", "test", n_prior=3000, n_pseudo=2000)
    reps, _ = rp.draw_replicates(design, [0, 1], rows, ident)
    other, _ = rp.draw_replicates(rp.ReplicateDesign("T", "other", n_prior=3000, n_pseudo=2000),
                                  [0], rows, ident)
    assert np.intersect1d(reps[0].prior_rows, other[0].prior_rows).size < 3000
    assert rp.seed_from_salt(design.replicate_salt(0)) != rp.seed_from_salt(design.family_salt())


def test_capacity_is_refused_not_silently_overlapped():
    rows, ident = _pool(n=9000)
    design = rp.ReplicateDesign("T", "cap", n_prior=3000, n_pseudo=2000)
    assert design.capacity(9000) == 1
    with pytest.raises(SystemExit):
        rp.draw_replicates(design, [0, 1], rows, ident)
    loose = rp.ReplicateDesign("T", "cap", n_prior=3000, n_pseudo=2000, disjoint=False)
    reps, record = rp.draw_replicates(loose, [0, 1], rows, ident)
    assert record["overlap"]["pairwise"]["0-1"]["shared_events"] > 0
    for rep in reps:
        assert np.intersect1d(rep.prior_rows, rep.pseudo_rows).size == 0


def test_exclude_removes_rows_before_any_hash():
    rows, ident = _pool()
    mask = np.zeros(rows.size, bool)
    mask[:5000] = True
    design = rp.ReplicateDesign("S", "holdout", n_prior=3000, n_pseudo=2000)
    reps, record = rp.draw_replicates(design, [0], rows, ident, exclude=mask)
    assert record["n_available"] == rows.size - 5000
    assert not np.isin(reps[0].prior_rows, rows[mask]).any()
    assert not np.isin(reps[0].pseudo_rows, rows[mask]).any()


# ------------------------------------------------------------------------------------------- #
# Pool-level scoring
# ------------------------------------------------------------------------------------------- #
def test_pool_level_score_equals_the_historical_scorer():
    """`common.score` against a target histogram must reproduce `scalar_common.score_push`
    (itself bit-identical to `score_campaign.score_run`) when the target is the same spectrum."""
    sc = cm.historical()["sc"]
    n = 4000
    eav_b = RNG.gamma(1.5, 1.2, n)
    eav_a = RNG.gamma(1.5, 1.2, n)
    w_b, w_a = RNG.uniform(0.5, 1.5, n), RNG.uniform(0.5, 1.5, n)
    tilt = np.exp(0.35 * np.clip((eav_a - 1.46) / 2.63, -3, 3))
    regions = np.array(["low_acceptance", "moderate", "good"])[RNG.integers(0, 3, n)]
    regions_a = np.array(["low_acceptance", "moderate", "good"])[RNG.integers(0, 3, n)]
    endpoint = sc.Endpoint(eavail_a=eav_a, w_truth_a=w_a, tilt_a=tilt, region_a=regions_a,
                           eavail_b=eav_b, w_truth_b=w_b, region_b=regions, prior_selector=None)
    push = np.exp(RNG.normal(0, 0.2, n))
    historical = scm.score_push(endpoint, push, cm.SCOREABLE)
    code = np.array([cm.REGION_CODES[r] for r in regions], dtype=np.int8)
    code_a = np.array([cm.REGION_CODES[r] for r in regions_a], dtype=np.int8)
    targets = cm.target_spectra(eav_a, w_a, tilt, code_a)
    mine = cm.score(eav_b, w_b, push, code, targets)
    assert mine["recovery"] == historical["recovery"]
    for region in cm.SCOREABLE:
        assert mine["recovery_by_region"][region] == historical["recovery_by_region"][region]
        assert (mine["regions"][region]["signed_residual_per_bin"]
                == historical["regions"][region]["signed_residual_per_bin"])
    assert (mine["aggregate"]["overshoot_projection"]
            == historical["aggregate"]["overshoot_projection"])


def test_spurious_displacement_is_zero_for_a_perfect_do_nothing_estimator():
    n = 2000
    eav = RNG.gamma(1.5, 1.2, n)
    w = RNG.uniform(0.5, 1.5, n)
    code = np.zeros(n, np.int8)
    targets = cm.target_spectra(eav, w, np.ones(n), code)
    out = cm.spurious_displacement(eav, w, np.ones(n), targets["aggregate"])
    assert out["unfolded_minus_target_l1"] == 0.0 and out["prior_minus_target_l1"] == 0.0
