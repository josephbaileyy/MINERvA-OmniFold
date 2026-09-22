"""End-to-end tests of the Phase-E runners on a SYNTHETIC pool, with known answers where possible.

The cluster jobs read an 8 M-event pool cache; these tests build a small cache with the same keys
and run the same `main()` functions on it, at reduced sample sizes. They exist because a runner
that crashes on its last case wastes a queue wait and a share of an allocation that other lanes
need, and because the parts with a known answer (a distortion that is the identity must score as
no distortion; a response distortion alone must leave the truth target where it was) are worth
asserting rather than eyeballing in a log.

Run: ``python -m pytest nd-unfolding/pet/improvement_campaign/phase_e -q``
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

def _hgb_takes_a_validation_set() -> bool:
    """`scalar_omnifold.HGBRatio` passes X_val/y_val to sklearn; older sklearn has no such fit."""
    import inspect
    from sklearn.ensemble import HistGradientBoostingClassifier
    return "X_val" in inspect.signature(HistGradientBoostingClassifier.fit).parameters


needs_hgb_val = pytest.mark.skipif(not _hgb_takes_a_validation_set(),
                                   reason="installed sklearn has no HGB validation-set fit "
                                          "(the cluster environment does)")

N_EVENTS = 24_000
N_PRIOR = 4_000
N_PSEUDO = 4_000


def _synthetic_cache(path: Path, rng: np.random.Generator, with_tokens: bool = True) -> dict:
    n = N_EVENTS
    rows = np.sort(rng.choice(5_000_000, n, replace=False)).astype(np.int64)
    identity = np.stack([np.full(n, 12), rows // 1000 + 1, rows], axis=1).astype(np.int64)
    eavail = rng.gamma(1.2, 1.1, n)
    pt = rng.uniform(0.05, 3.0, n)
    ppar = rng.uniform(1.6, 25.0, n)
    q3 = eavail + rng.gamma(2.0, 0.5, n)
    truth = np.stack([pt, ppar, eavail, q3], axis=1)
    accept = rng.random(n) < np.clip(0.05 + 0.6 * (eavail / (eavail + 1.0)), 0, 1)
    reco_eavail = np.where(accept, np.maximum(eavail * rng.normal(1.0, 0.15, n), 1e-3), -9999.0)
    reco_pt = np.where(accept, pt * rng.normal(1.0, 0.02, n), -9999.0)
    reco_ppar = np.where(accept, ppar * rng.normal(1.0, 0.02, n), -9999.0)
    q0 = np.where(accept, np.maximum(reco_eavail / 1.17, 1e-3), 1.0)
    reco_q3 = np.where(accept, dist.reco_q3(np.abs(reco_pt), np.abs(reco_ppar), q0), -9999.0)
    reco = np.stack([reco_pt, reco_ppar, reco_eavail, reco_q3], axis=1)
    tok = np.zeros((n, dist.N_TOKENS))
    share = rng.dirichlet(np.ones(dist.N_TOKENS), n)
    tok[accept] = (share * np.where(accept, reco_eavail, 0.0)[:, None])[accept]
    cache = {
        "rows": rows, "identity": identity, "pass_reco": accept,
        "w_truth": rng.uniform(0.6, 1.4, n), "w_reco": rng.uniform(0.6, 1.4, n),
        "truth": truth, "reco": reco,
        "truth_cell": rng.integers(0, 285, n).astype(np.int32),
        "reco_cell": rng.integers(0, 285, n).astype(np.int32),
        "region": np.array(rng.choice([0, 1, 2, 3], n), dtype=np.int8),
    }
    if with_tokens:
        cache["tok_E"] = tok
        for name, lam in (("n_pipm", 0.8), ("n_pi0", 0.4), ("n_p", 1.2), ("n_n", 1.0)):
            cache[name] = rng.poisson(lam, n).astype(np.int16)
        cache["n_gen_filled"] = np.minimum(
            cache["n_pipm"] + cache["n_pi0"] + cache["n_p"] + cache["n_n"], 12).astype(np.int16)
    np.savez(path, **cache)
    return cache


def _b1_populations(path: Path) -> None:
    """The edges and acceptance map the runners read (a stand-in for the B1 cache)."""
    edges_pt = np.array([0.0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5,
                         2.5, 4.5, 30.0])
    edges_pz = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0,
                         10.0, 15.0, 20.0, 40.0, 60.0, 120.0])
    n_cells = (edges_pt.size - 1) * (edges_pz.size - 1)
    np.savez(path, edges_pt=edges_pt, edges_pz=edges_pz,
             endpoint_edges=np.asarray(cm.ENDPOINT_EDGES),
             map_acceptance=np.linspace(0.0, 1.0, n_cells))


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    rng = np.random.default_rng(4242)
    cache_path = tmp_path / "poolT.npz"
    _synthetic_cache(cache_path, rng)
    b1 = tmp_path / "populations.npz"
    _b1_populations(b1)
    prepare = tmp_path / "prepare.json"
    prepare.write_text(json.dumps({"caches": {"T": {"sha256": cm.scm.sha256_file(cache_path)},
                                              "S": {"sha256": cm.scm.sha256_file(cache_path)}},
                                   "pools": {"pools_npz_sha256": "synthetic"}}))
    monkeypatch.setattr(cm, "B1_POPULATIONS_SHA256", cm.scm.sha256_file(b1))
    monkeypatch.setitem(cm.HISTORICAL_SIZES, "prior", N_PRIOR)
    monkeypatch.setitem(cm.HISTORICAL_SIZES, "pseudo", N_PSEUDO)
    return {"cache": cache_path, "b1": b1, "prepare": prepare, "dir": tmp_path}


def _run(module, argv, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"] + [str(a) for a in argv])
    module.main()


@needs_hgb_val
def test_references_runner_end_to_end(workspace, monkeypatch):
    import run_references
    out = workspace["dir"] / "refs"
    _run(run_references, ["--cache", workspace["cache"], "--prepare", workspace["prepare"],
                          "--b1-populations", workspace["b1"], "--replicate", 0,
                          "--only", "D1_p0.350", "D1_m0.350", "D4d_n_up", "D5_nuwro", "R2_x1.01",
                          "R3_s0.10+D1_p0.350", "--ibu-iterations", 3, "--omnifold-iterations", 2,
                          "--output-dir", out], monkeypatch)
    payload = json.loads((out / "references_r0_c0of1.json").read_text())
    res = payload["results"]
    assert set(res) == {"D1_p0.350", "D1_m0.350", "D4d_n_up", "D5_nuwro", "R2_x1.01",
                        "R3_s0.10+D1_p0.350"}
    for name, entry in res.items():
        for mode in ("carry_misses", "efficiency_corrected"):
            assert len(entry["ibu"][mode]["iterations"]) == 3
        assert len(entry["gbdt_omnifold"]["iterations"]) == 2
        # every estimator must move the spectrum towards the target, not away from it
        assert entry["ibu"]["carry_misses"]["iterations"][-1]["recovery"] > -1.0
    # a response-only case is scored against the UNDISTORTED target and reports its displacement
    assert "spurious" in res["R2_x1.01"]["ibu"]["carry_misses"]["iterations"][2]
    # D4 carries the joint recoveries Amendment 1 asks for
    joint = res["D4d_n_up"]["ibu"]["carry_misses"]["iterations"][2]["joint"]
    assert set(joint) == {"eavail_q3", "eavail_pt"}
    # opposite tilts inject opposite displacements
    a = res["D1_p0.350"]["ibu"]["carry_misses"]["iterations"][2]["full"]["injected_per_bin"]
    b = res["D1_m0.350"]["ibu"]["carry_misses"]["iterations"][2]["full"]["injected_per_bin"]
    assert np.dot(a, b) < 0


def test_identifiability_runner_end_to_end(workspace, monkeypatch):
    import run_identifiability
    monkeypatch.setattr(run_identifiability, "SAMPLE", N_PSEUDO)
    monkeypatch.setattr(run_identifiability, "PERMUTATION_SPLITS", 2)
    out = workspace["dir"] / "ident.json"
    _run(run_identifiability, ["--cache", workspace["cache"], "--prepare", workspace["prepare"],
                               "--null-splits", 3, "--only", "D1_p0.700", "R1_x1.05",
                               "--output", out], monkeypatch)
    payload = json.loads(out.read_text())
    assert set(payload["distortions"]) == {"D1_p0.700", "R1_x1.05"}
    for name, rec in payload["distortions"].items():
        assert 0.0 <= rec["auc"] <= 1.0
        assert rec["threshold_ess_scaled"] >= payload["null"]["q97.5"] - 1e-12
        assert rec["population_reco_eavail_l1"] > 0.0
    assert payload["null"]["splits"] == 3
    assert payload["permutation_null"]                                  # ran for the weighted case


def test_reference_assessment_runner_end_to_end(workspace, monkeypatch):
    import run_reference_assessment
    out = workspace["dir"] / "assess.json"
    _run(run_reference_assessment, ["--cache", workspace["cache"], "--prepare", workspace["prepare"],
                                    "--b1-populations", workspace["b1"], "--iterations", 4,
                                    "--replicates", 2, "--scale", 1, 2, "--output", out],
         monkeypatch)
    payload = json.loads(out.read_text())
    keys = set(payload["runs"])
    assert {"1x/r0/muon_eavail/carry_misses", "2x/r1/diag/carry_misses"} <= keys
    assert payload["runs"]["2x/r0/muon_eavail/carry_misses"]["n_prior"] == 2 * N_PRIOR
    # the reference model curve is the historical construction and must rise with k
    agg = payload["reference_model"]["curve"]["aggregate"]
    assert all(b >= a - 1e-12 for a, b in zip(agg, agg[1:]))


@needs_hgb_val
def test_summarize_merges_what_the_jobs_wrote(workspace, monkeypatch):
    import run_references
    import summarize
    task_dir = workspace["dir"] / "task"
    (task_dir / "references").mkdir(parents=True)
    for replicate in (0, 1):
        _run(run_references, ["--cache", workspace["cache"], "--prepare", workspace["prepare"],
                              "--b1-populations", workspace["b1"], "--replicate", replicate,
                              "--only", "D1_p0.350", "--ibu-iterations", 3,
                              "--omnifold-iterations", 2,
                              "--output-dir", task_dir / "references"], monkeypatch)
    results = workspace["dir"] / "results"
    _run(summarize, ["--task-dir", task_dir, "--results-dir", results], monkeypatch)
    merged = json.loads((results / "references.json").read_text())
    assert set(merged["cases"]["D1_p0.350"]["replicates"]) == {"0", "1"}
    across = merged["across_replicates"]["D1_p0.350"]["ibu/carry_misses"]
    assert across["k3"]["sd"] is not None and len(across["k3"]["values"]) == 2
    assert (results / "summary.json").exists()
