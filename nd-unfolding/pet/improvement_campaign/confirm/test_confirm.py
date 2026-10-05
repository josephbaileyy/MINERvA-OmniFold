"""Tests of the confirmatory-stage input path (numpy only; no TensorFlow, no real inventory).

The loader and closure positive controls run on a SYNTHETIC g2-fullevent-v1 fixture
(`make_synthetic_g2_fullevent.py`): the historical loader and `closure_data.build_closure_inputs`
on one side, this path with the historical rows forced in on the other, byte for byte. Tests
marked `perlmutter` read the cached historical populations / pool codes and skip elsewhere; the
same comparison on the real inventory runs inside the GPU control job
(`--crosscheck-closure-data`).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
PET = CAMPAIGN.parent
REPO = PET.parents[1]
# Highest priority first: `configuration_comparison` has its OWN `authorization_scope.py`, so
# the campaign's directories must precede it.
for _p in reversed((HERE, CAMPAIGN, CAMPAIGN / "phase_e", CAMPAIGN / "phase_b" / "scalar",
                    PET / "configuration_comparison", PET, REPO / "omnifold_nn")):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import replicate_inputs as ri  # noqa: E402
import replicates as rp  # noqa: E402

B1_POPULATIONS = Path("/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/"
                      "populations.npz")
POOLS_NPZ = Path("/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz")
MANIFEST = CAMPAIGN / "pools" / "POOL_MANIFEST.json"
SIDECAR = Path("/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz")
HISTORICAL_OUT = "/pscratch/sd/j/josephrb/campaign-20260920"


# ------------------------------------------------------------------------------------------- #
# Fixtures
# ------------------------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def synthetic(tmp_path_factory):
    """A synthetic G2 inventory and an identity sidecar for it."""
    d = tmp_path_factory.mktemp("g2")
    npz = d / "G2_SYNTH.npz"
    subprocess.run([sys.executable, str(PET / "make_synthetic_g2_fullevent.py"), "--out",
                    str(npz), "--n-sig", "12000", "--n-data", "300"], check=True,
                   capture_output=True)
    with np.load(npz, allow_pickle=True) as blob:
        n = blob["pass_reco"].shape[0]
    rng = np.random.default_rng(7)
    ident = np.stack([rng.integers(1, 10**6, n), rng.integers(0, 10**4, n), np.arange(n)], 1)
    sidecar = d / "identity.npz"
    np.savez(sidecar, sig_event_id=ident.astype(np.int64))
    return SimpleNamespace(npz=npz, sidecar=sidecar, n=n)


@pytest.fixture(scope="module")
def historical_mods():
    # OI-136 order (as `closure_data.import_historical`): the engine from THIS checkout first,
    # then the loader, which inserts the hardcoded tree at sys.path[0]; then remove that entry.
    from omnifold.dataloader import DataLoader
    import fullevent_fps_dataloader as ffd
    hardcoded = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
    sys.path[:] = [p for p in sys.path if not p.startswith(hardcoded)]
    import closure_powered_truth_reweight as cp
    import run_arm_evaluation as rae
    import stage_splits as ss
    return {"ffd": ffd, "cp": cp, "rae": rae, "ss": ss, "DataLoader": DataLoader}


def events(max_events=8000):
    from recipe import EventSplitSpec, EndpointSpec
    return (EventSplitSpec(stage="final", max_events=max_events, subsample_seed=0,
                           split_seed=20260920), EndpointSpec(amplitude=0.35, clip=3.0))


# ------------------------------------------------------------------------------------------- #
# 4. Scope: real data and the historical output directory, on this path
# ------------------------------------------------------------------------------------------- #
def test_signal_only_npz_refuses_every_real_data_member(synthetic):
    with np.load(synthetic.npz, allow_pickle=True) as raw:
        view = scope.SignalOnlyNpz(raw)
        for key in ("measured_scalars", "measured_pc", "data_muon", "data_vertex", "data_view",
                    "data_time", "data_pot", "data_identity_hash"):
            assert key in view.files
            with pytest.raises(scope.ScopeViolation):
                view[key]
        assert view["w_truth"].shape[0] == synthetic.n
        assert view.keys_read == ["w_truth"]


def test_real_data_prefixes_are_refused_without_a_list_edit():
    for key in ("data_something_new", "measured_extra"):
        with pytest.raises(scope.ScopeViolation):
            scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                          npz_keys_read=[key])
    scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                  npz_keys_read=list(ri.SIGNAL_MEMBERS))


def test_loader_reads_no_real_data_member(synthetic, historical_mods):
    rows = np.arange(0, synthetic.n, 3)
    loaded = ri.load_signal_rows(historical_mods["ffd"], historical_mods["DataLoader"],
                                 synthetic.npz, rows)
    assert set(loaded.keys_read) <= set(ri.SIGNAL_MEMBERS)
    assert not any(k.startswith(scope.REAL_DATA_NPZ_PREFIXES) for k in loaded.keys_read)


def _run_args(tmp_path, **over):
    cfg = CAMPAIGN / "phase_b" / "pet" / "configs" / "b2e3-H-K10-s1.json"
    args = {"--config": str(cfg), "--config-hash": "x", "--repo": str(REPO),
            "--out": str(tmp_path / "out"), "--inputs-npz": str(tmp_path / "G2.npz"),
            "--identity-sidecar": str(tmp_path / "id.npz"),
            "--populations": str(tmp_path / "pop.npz"), "--historical-halves": None}
    args.update(over)
    argv = []
    for k, v in args.items():
        argv += [k] if v is None else [k, v]
    return argv


def test_run_entry_refuses_the_historical_output_dir_before_reading(tmp_path):
    import run_replicate as rr
    link = tmp_path / "innocent-looking"
    link.symlink_to(HISTORICAL_OUT)
    for out in (HISTORICAL_OUT, HISTORICAL_OUT + "/final/x",
                HISTORICAL_OUT + "-new/../campaign-20260920/confirm", str(link / "run")):
        with pytest.raises(scope.ScopeViolation):
            rr.main(_run_args(tmp_path, **{"--out": out}))
    assert not (tmp_path / "out").exists()


def test_run_entry_refuses_real_data_input_paths(tmp_path):
    import run_replicate as rr
    with pytest.raises(scope.ScopeViolation):
        rr.main(_run_args(tmp_path, **{"--inputs-npz": "/x/1A_Data/G2.npz"}))
    with pytest.raises(SystemExit):     # config hash mismatch is refused before any read
        rr.main(_run_args(tmp_path))


def test_population_target_and_scores_refuse_the_historical_output_dir(tmp_path):
    import scalar_common as scm
    with pytest.raises((scope.ScopeViolation, SystemExit)):
        scope.refuse_historical_output(HISTORICAL_OUT + "/confirm/target.json")
    with pytest.raises(SystemExit):
        scm.refuse_historical_output(HISTORICAL_OUT + "/x/scores.json")


def test_sealed_pools_need_amendment_2(tmp_path):
    text = ri.PROTOCOL.read_text()
    before = text.split("### Amendment 2")[0]            # the protocol as it was before the freeze
    unamended = tmp_path / "PROTOCOL-unamended.md"
    unamended.write_text(before)
    for pool in ("P", "F"):
        with pytest.raises(scope.ScopeViolation):
            ri.refuse_sealed_pool(pool, unamended)
    assert ri.refuse_sealed_pool("S", unamended)["sealed"] is False
    amended = tmp_path / "PROTOCOL.md"
    amended.write_text(before + "\n### Amendment 2 (test) -- frozen candidates\n")
    assert ri.refuse_sealed_pool("F", amended)["amendment_2_present"] is True
    assert ri.refuse_sealed_pool("P")["amendment_2_present"] is True   # the committed protocol
    # a mention in prose is not an amendment
    prose = tmp_path / "P2.md"
    prose.write_text(before + "\nsee Amendment 2 later\n")
    with pytest.raises(scope.ScopeViolation):
        ri.refuse_sealed_pool("P", prose)


# ------------------------------------------------------------------------------------------- #
# 5a. Positive control: the historical rows through this path == closure_data, byte for byte
# ------------------------------------------------------------------------------------------- #
def test_loader_on_forced_rows_equals_the_historical_loader(synthetic, historical_mods):
    ffd = historical_mods["ffd"]
    _d, mc_ref, imc, cr, cg, meta_ref = ffd.build_fullevent_loaders(
        str(synthetic.npz), max_events=8000, seed=0, bkg_mode="mc-only")
    loaded = ri.load_signal_rows(ffd, historical_mods["DataLoader"], synthetic.npz, imc)
    for f in ("reco", "gen", "reco_evt", "gen_evt", "weight", "weight_reco", "pass_reco",
              "pass_gen"):
        a, b = np.asarray(getattr(loaded.mc, f)), np.asarray(getattr(mc_ref, f))
        assert a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes(), f
    assert (loaded.coord_reco, loaded.coord_gen) == (tuple(cr), tuple(cg))
    for k in ("reco_norm_mean", "reco_norm_std", "truth_norm_mean", "truth_norm_std",
              "n_evt_reco", "n_evt_truth"):
        assert loaded.meta[k] == meta_ref[k], k


def test_closure_on_forced_halves_equals_closure_data(synthetic, historical_mods):
    import closure_data as cd
    ev, ep = events()
    mods = dict(historical_mods)
    ref = cd.build_closure_inputs(mods, np, arm="ours", events=ev, endpoint=ep,
                                  inputs_npz=synthetic.npz, identity_sidecar=synthetic.sidecar,
                                  theirs_index=None, theirs_cache=None)
    sel = ri.historical_selection(mods, ev, synthetic.npz, synthetic.sidecar)
    assert np.array_equal(sel.pseudo_rows, ref.meta["dump_rows_a"])
    assert np.array_equal(sel.prior_rows, ref.meta["dump_rows_b"])
    assert np.array_equal(sel.load_rows, ref.meta["mc_indices"])
    # The synthetic half A has its own quantiles; the frozen-constant tilt takes them as its
    # constants here (on the real inventory they ARE the historical constants -- checked in the
    # GPU control's crosscheck and in test_frozen_tilt_reproduces_the_recorded_half_a_tilt).
    spec = dict(ri.historical_tilt_spec())
    spec.update({"p50": ref.meta["tilt_spec"]["pt_p50"], "iqr": ref.meta["tilt_spec"]["pt_iqr"]})
    distortion = ri.DistortionSpec("dev", spec,
                                   lambda t: ri.development_tilt_raw(t["eavail"], spec))
    loaded = ri.load_signal_rows(mods["ffd"], mods["DataLoader"], synthetic.npz, sel.load_rows)
    ours, arrays = ri.assemble_closure(mods["ffd"], loaded, sel, distortion, cd.ClosureInputs)
    cmp = ri.compare_inputs(np, ours, ref)
    assert cmp["all_equal"], cmp
    assert ours.digests(np) == ref.digests(np)
    assert np.array_equal(arrays["pseudo_distortion"], ref.meta["tilt_a"])


# ------------------------------------------------------------------------------------------- #
# 5c. The tilt reproduces the historical function
# ------------------------------------------------------------------------------------------- #
def test_historical_tilt_constants_are_read_not_retyped():
    import distortions as dist
    spec = ri.historical_tilt_spec()
    record = json.loads(ri.POPULATIONS_JSON.read_text())["tilt_spec_half_A"]
    assert (spec["p50"], spec["iqr"]) == (record["pt_p50"], record["pt_iqr"])
    assert (spec["amplitude"], spec["clip_z"]) == (0.35, 3.0)
    assert (spec["p50"], spec["iqr"]) == (dist.D1_P50_GEV, dist.D1_IQR_GEV)


def test_frozen_tilt_equals_the_historical_function_given_its_quantiles(historical_mods):
    cp = historical_mods["cp"]
    rng = np.random.default_rng(3)
    e = rng.gamma(1.5, 1.4, 200_001)
    tilt, hist = cp.clipped_exponential_tilt(e, amplitude=0.35, clip_z=3.0)
    spec = {"p50": hist["pt_p50"], "iqr": hist["pt_iqr"], "amplitude": 0.35, "clip_z": 3.0}
    ours, mean = ri.unit_mean(ri.development_tilt_raw(e, spec))
    assert ours.tobytes() == tilt.tobytes()
    assert mean == hist["pre_normalization_mean"]


def test_dev_distortion_equals_phase_e_d1_at_the_development_point():
    import distortions as dist
    rng = np.random.default_rng(4)
    e = rng.gamma(1.5, 1.4, 50_000)
    dev = ri.get_distortion("dev", 0.35, 3.0)
    d1 = dist.registry()["D1_p0.350"]
    a, _ = ri.unit_mean(dev.raw({"eavail": e}))
    b = dist.normalize_unit_mean(d1.truth_weight({"eavail": e}))
    np.testing.assert_allclose(a, b, rtol=1e-14, atol=0)
    with pytest.raises(SystemExit):
        ri.get_distortion("dev", 0.70, 3.0)         # a config endpoint that is not historical
    with pytest.raises(SystemExit):
        ri.get_distortion("R2_x1.01")               # R2/R3: refused, not approximated
    assert ri.get_distortion("D4c_p_up").needs_species


@pytest.mark.skipif(not B1_POPULATIONS.exists(), reason="perlmutter: B1 populations.npz")
def test_frozen_tilt_reproduces_the_recorded_half_a_tilt():
    with np.load(B1_POPULATIONS) as pop:
        pga = pop["a_pass_truth"].astype(bool)
        eav, tilt = pop["a_truth"][pga, 2].astype(np.float64), pop["a_tilt"][pga]
    ours, mean = ri.unit_mean(ri.development_tilt_raw(eav, ri.historical_tilt_spec()))
    assert ours.tobytes() == np.asarray(tilt, np.float64).tobytes()
    assert mean == ri.historical_tilt_spec()["historical_pre_normalization_mean"]


# ------------------------------------------------------------------------------------------- #
# 5b. Replicate disjointness and independence
# ------------------------------------------------------------------------------------------- #
def _pool(n=60_000, seed=11):
    rng = np.random.default_rng(seed)
    rows = np.sort(rng.choice(10 * n, n, replace=False)).astype(np.int64)
    ident = np.stack([rng.integers(1, 10**6, n), rng.integers(0, 10**4, n),
                      np.arange(n)], 1).astype(np.int64)
    return rows, ident


def test_replicates_are_disjoint_and_prior_pseudo_disjoint():
    rows, ident = _pool()
    design = rp.ReplicateDesign("S", ri.FAMILY, 6_000, 5_000)
    reps, record = rp.draw_replicates(design, range(5), rows, ident)
    allrows = [np.union1d(r.prior_rows, r.pseudo_rows) for r in reps]
    for r in reps:
        assert r.prior_rows.size == 6_000 and r.pseudo_rows.size == 5_000
        assert np.intersect1d(r.prior_rows, r.pseudo_rows).size == 0
    for i in range(5):
        for j in range(i + 1, 5):
            assert np.intersect1d(allrows[i], allrows[j]).size == 0
    assert record["overlap"]["max_pairwise_fraction"] == 0.0


def test_a_replicate_does_not_depend_on_which_others_are_drawn():
    rows, ident = _pool()
    design = rp.ReplicateDesign("S", ri.FAMILY, 6_000, 5_000)
    alone, _ = rp.draw_replicates(design, [3], rows, ident)
    joint, _ = rp.draw_replicates(design, range(5), rows, ident)
    assert np.array_equal(alone[0].prior_rows, joint[3].prior_rows)
    assert np.array_equal(alone[0].pseudo_rows, joint[3].pseudo_rows)
    # ... nor on the row order of the pool (identity-keyed, not position-keyed)
    perm = np.random.default_rng(1).permutation(rows.size)
    shuffled, _ = rp.draw_replicates(design, [3], rows[perm], ident[perm])
    assert np.array_equal(np.sort(shuffled[0].prior_rows), np.sort(alone[0].prior_rows))


def test_replicates_are_independent_draws_not_a_partition_pattern():
    """Across replicates the prior/pseudodata assignment is a fresh hash: the overlap of a
    replicate's prior with another family's prior matches the independent-draw expectation."""
    rows, ident = _pool(n=100_000)
    a, _ = rp.draw_replicates(rp.ReplicateDesign("S", "fam-a", 20_000, 20_000), [0], rows, ident)
    b, _ = rp.draw_replicates(rp.ReplicateDesign("S", "fam-b", 20_000, 20_000), [0], rows, ident)
    shared = np.intersect1d(a[0].prior_rows, b[0].prior_rows).size
    expected = 20_000 * 20_000 / 100_000
    assert abs(shared - expected) < 5 * np.sqrt(expected)


def test_historical_size_capacity_per_pool():
    """PROTOCOL 5.2/5.3: at the protocol's sizes the committed pools support this many disjoint
    replicates (PILOT's 4 do NOT fit disjointly in pool P)."""
    manifest = json.loads(MANIFEST.read_text())
    design = rp.ReplicateDesign("P", ri.FAMILY, ri.N_PRIOR, ri.N_PSEUDO)
    cap = {k: design.capacity(int(v["count"])) for k, v in manifest["pools"].items()}
    assert cap == {"P": 3, "F": 12, "S": 15, "T": 6, "R": 1}


@pytest.mark.skipif(not (POOLS_NPZ.exists() and SIDECAR.exists()),
                    reason="perlmutter: pool codes and identity sidecar")
def test_real_pool_s_replicates_are_disjoint():
    s0 = ri.replicate_selection("S", 0, pools_npz=POOLS_NPZ, manifest=MANIFEST,
                                identity_sidecar=SIDECAR)
    s1 = ri.replicate_selection("S", 1, pools_npz=POOLS_NPZ, manifest=MANIFEST,
                                identity_sidecar=SIDECAR)
    for s in (s0, s1):
        assert s.prior_rows.size == ri.N_PRIOR and s.pseudo_rows.size == ri.N_PSEUDO
        assert np.intersect1d(s.prior_rows, s.pseudo_rows).size == 0
    assert np.intersect1d(s0.load_rows, s1.load_rows).size == 0


# ------------------------------------------------------------------------------------------- #
# Scorer mechanics on a synthetic run directory
# ------------------------------------------------------------------------------------------- #
def test_scorer_anchors(tmp_path):
    import score_replicate as sr
    rng = np.random.default_rng(5)
    n = 40_000

    def side():
        truth = np.stack([rng.uniform(0.05, 2.0, n), rng.uniform(2.0, 15.0, n),
                          rng.gamma(1.5, 1.2, n), rng.uniform(0.1, 3, n)], 1)
        return truth, rng.uniform(0.5, 1.5, n), rng.random(n) < 0.42
    ta, wa, ra = side()
    tb, wb, rb = side()
    spec = ri.historical_tilt_spec()
    dist_a, _ = ri.unit_mean(ri.development_tilt_raw(ta[:, 2], spec))
    oracle, _ = ri.unit_mean(ri.development_tilt_raw(tb[:, 2], spec))
    arrays = {"pseudo_rows": np.arange(n), "prior_rows": np.arange(n, 2 * n),
              "pseudo_pass_truth": np.ones(n, bool), "prior_pass_truth": np.ones(n, bool),
              "pseudo_pass_reco": ra, "prior_pass_reco": rb, "pseudo_truth": ta,
              "prior_truth": tb, "pseudo_reco_eavail": ta[:, 2] * 0.9,
              "prior_reco_eavail": tb[:, 2] * 0.9, "pseudo_w_truth": wa, "prior_w_truth": wb,
              "pseudo_w_reco": wa * 0.95, "prior_w_reco": wb * 0.95,
              "pseudo_distortion": dist_a, "prior_oracle": oracle,
              "pseudo_region": rng.choice([0, 1, 2, 3], n).astype(np.int8),
              "prior_region": rng.choice([0, 1, 2, 3], n).astype(np.int8)}
    run = tmp_path / "run"
    (run / "iterations").mkdir(parents=True)
    np.savez(run / "replicate_arrays.npz", **arrays)
    np.savez(run / "halves.npz", dump_rows_a=arrays["pseudo_rows"],
             dump_rows_b=arrays["prior_rows"])
    np.savez(run / "iterations" / "iter00.npz", push=np.ones(n, np.float32),
             pull=np.ones(n, np.float32))
    np.savez(run / "iterations" / "iter01.npz", push=oracle.astype(np.float32),
             pull=oracle.astype(np.float32))
    res = sr.RunScorer(run).score()
    k0, k1 = res["iterations"]
    assert k0["push"]["recovery"] == 0.0                       # the prior recovers nothing
    assert k1["push"]["recovery"] == pytest.approx(
        res["constants"]["oracle_vs_replicate_target"]["recovery"], abs=1e-6)
    assert 0.8 < k1["push"]["recovery"] <= 1.0                 # a finite-sample ceiling
    assert set(k1["push"]["recovery_by_region"]) == {"low_acceptance", "moderate", "good"}
    assert len(k1["push"]["aggregate"]["signed_residual_per_bin"]) == 7
    assert k0["final_truth_weights_ess"]["ess"] == pytest.approx(
        k0["final_truth_weights_ess"]["ess_prior_only"])


# ------------------------------------------------------------------------------------------- #
# R1 on the PET path (amendment 3 item 3)
# ------------------------------------------------------------------------------------------- #
def test_r1_scales_pseudodata_cluster_energies_and_reco_eavail_only(synthetic, historical_mods):
    ffd, DL = historical_mods["ffd"], historical_mods["DataLoader"]
    rows = np.arange(0, synthetic.n, 2)
    pseudo = rows[::3]
    base = ri.load_signal_rows(ffd, DL, synthetic.npz, rows)
    r1 = ri.load_signal_rows(ffd, DL, synthetic.npz, rows, reco_energy_scale=(pseudo, 1.05))
    hit = np.isin(rows, pseudo) & np.asarray(base.mc.pass_reco, bool)
    assert r1.meta["reco_energy_scale"] == {"factor": 1.05, "rows_scaled": int(hit.sum())}
    e0, e1 = np.asarray(base.mc.reco)[..., 0], np.asarray(r1.mc.reco)[..., 0]
    np.testing.assert_allclose(e1[hit], e0[hit] * 1.05, rtol=2e-7)
    assert e1[~hit].tobytes() == e0[~hit].tobytes()                 # prior / non-reco rows
    assert np.asarray(r1.mc.reco)[..., 1:].tobytes() == np.asarray(base.mc.reco)[..., 1:].tobytes()
    for f in ("reco_evt", "gen", "gen_evt", "weight", "weight_reco", "pass_reco", "pass_gen"):
        assert np.asarray(getattr(r1.mc, f)).tobytes() == np.asarray(getattr(base.mc, f)).tobytes(), f
    col = ffd.SCALAR_COLS["eavail"]
    np.testing.assert_allclose(r1.reco_scalars[hit, col], base.reco_scalars[hit, col] * 1.05,
                               rtol=2e-7)
    others = [c for c in range(base.reco_scalars.shape[1]) if c != col]
    assert r1.reco_scalars[:, others].tobytes() == base.reco_scalars[:, others].tobytes()
    assert r1.reco_scalars[~hit].tobytes() == base.reco_scalars[~hit].tobytes()


def test_r1_distortion_parsing_and_arm_reader():
    d = ri.get_distortion("R1_x1.05+D1_p0.350")
    assert d.reco_energy_scale == 1.05 and d.record["truth"]["name"] == "D1_p0.350"
    e = np.linspace(0.0, 8.0, 101)
    np.testing.assert_array_equal(d.raw({"eavail": e}), ri.get_distortion("D1_p0.350").raw(
        {"eavail": e}))
    assert ri.get_distortion("R1_x0.95").reco_energy_scale == 0.95
    for bad in ("R2_x1.01+D1_p0.350", "R3_s0.10", "R1_x1.05+R1_x0.95"):
        with pytest.raises(SystemExit):
            ri.get_distortion(bad)
    base = lambda which, column, rows: np.full(len(rows), 2.0)          # noqa: E731
    read = ri.scaled_reader(np, base, (np.array([3, 5]), 1.05))
    got = read("reco", "eavail", np.array([1, 3, 5, 7]))
    np.testing.assert_allclose(got, [2.0, 2.1, 2.1, 2.0], rtol=1e-7)
    assert np.all(read("reco", "q3", np.array([3, 5])) == 2.0)
    assert np.all(read("truth", "eavail", np.array([3, 5])) == 2.0)


def test_frozen_configs_generate_with_only_seed_name_note_changed(tmp_path):
    import freeze_runs as fr
    from recipe import RunConfig
    for cand in fr.CANDIDATES:
        frozen, path, sha = fr.load_frozen(cand)
        cfg = fr.reseed(frozen, fr.seed_for("P", 1), "x", "y")
        rec = fr.verify_generated(cfg, path, sha)
        assert rec["frozen_sha256"] == sha and rec["seed"] == fr.seed_for("P", 1)
        bad = cfg.replace(iterations=3)
        with pytest.raises(SystemExit):
            fr.verify_generated(bad, path, sha)
    assert len({fr.seed_for(p, r) for p in "PFT" for r in range(12)}) == 36
