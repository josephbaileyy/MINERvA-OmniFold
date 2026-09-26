"""Tests of the study runner's input path (numpy only; no TensorFlow training, no real inventory).

Synthetic g2-fullevent-v1 inventory (`make_synthetic_g2_fullevent.py`), synthetic identities, pool
codes and banks. (i) a predecessor pool selection yields byte-identical inputs through the study
runner and through the predecessor's; (ii) bank draws are disjoint, deterministic and within their
banks; (iii) FB/RB are refused without, and opened with, a committed release amendment; (iv)
bootstrap members are reproducible Poisson(1) weights that leave the score target unchanged; (v)
the null distortion's target is the undistorted truth; plus the counts arm and the miss rule.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PET = STUDY.parent
REPO = PET.parents[1]
CAMPAIGN = PET / "improvement_campaign"
CONFIRM = CAMPAIGN / "confirm"
for _p in reversed((HERE, STUDY / "banks", CONFIRM, CAMPAIGN, CAMPAIGN / "phase_e",
                    CAMPAIGN / "phase_b" / "pet", CAMPAIGN / "phase_b" / "scalar",
                    PET / "configuration_comparison", PET, REPO / "omnifold_nn")):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import build_banks as bb  # noqa: E402
import design_arms as da  # noqa: E402
import design_inputs as di  # noqa: E402
import replicate_inputs as ri  # noqa: E402
import replicates as rp  # noqa: E402
import run_design as rd  # noqa: E402
import run_replicate as rr  # noqa: E402
from recipe import RunConfig  # noqa: E402

DEV1_CONFIG = STUDY / "configs" / "dev1" / "dev1-H1-T0-D1_p0.350.json"


# ------------------------------------------------------------------------------------------- #
# Fixtures
# ------------------------------------------------------------------------------------------- #
def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def synthetic(tmp_path_factory):
    """Synthetic inventory + identity sidecar + pool codes/manifest + banks/manifest."""
    d = tmp_path_factory.mktemp("g2")
    npz = d / "G2_SYNTH.npz"
    subprocess.run([sys.executable, str(PET / "make_synthetic_g2_fullevent.py"), "--out",
                    str(npz), "--n-sig", "12000", "--n-data", "300", "--tokens", "12"],
                   check=True, capture_output=True)
    with np.load(npz, allow_pickle=True) as blob:
        n = blob["pass_reco"].shape[0]
        pass_truth = np.asarray(blob["pass_truth"], bool)
    rng = np.random.default_rng(7)
    ident = np.stack([rng.integers(1, 10**6, n), rng.integers(0, 10**4, n), np.arange(n)], 1)
    sidecar = d / "identity.npz"
    np.savez(sidecar, sig_event_id=ident.astype(np.int64))
    # pools over truth-passing rows (as the predecessor's builder assigns them)
    codes = np.full(n, -1, np.int8)
    u = rng.random(n)
    for code, (lo, hi) in enumerate(((0, .08), (.08, .4), (.4, .8), (.8, .97), (.97, 1.0))):
        codes[pass_truth & (u >= lo) & (u < hi)] = code
    pools = d / "pools.npz"
    np.savez(pools, pool_codes=codes)
    manifest = {"inputs": {"identity_npz": {"sha256": sha(sidecar)}},
                "pools": {k: {"code": v, "count": int((codes == v).sum())}
                          for k, v in rp.POOL_CODES.items()},
                "output": {"sha256": sha(pools)}, "commit": "synthetic"}
    pool_manifest = d / "POOL_MANIFEST.json"
    pool_manifest.write_text(json.dumps(manifest))
    # banks: DEV ~ 70 %, FB ~ 20 %, RB ~ 10 % of the truth-passing rows
    bank = np.full(n, -1, np.int8)
    v = rng.random(n)
    bank[pass_truth] = 0
    bank[pass_truth & (v > 0.7)] = 1
    bank[pass_truth & (v > 0.9)] = 2
    bank_dir = d / "banks"
    bb.write_outputs(bank_dir, bank, {"inputs": {"identity_sidecar_sha256": sha(sidecar)},
                                      "code": {"commit": "synthetic"}})
    return SimpleNamespace(npz=npz, sidecar=sidecar, n=n, ident=ident, pass_truth=pass_truth,
                           codes=codes, pools=pools, pool_manifest=pool_manifest, bank=bank,
                           banks_npz=bank_dir / "banks.npz",
                           bank_manifest=bank_dir / "BANK_MANIFEST.json")


@pytest.fixture(scope="module")
def historical_mods():
    from omnifold.dataloader import DataLoader
    import fullevent_fps_dataloader as ffd
    hardcoded = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
    sys.path[:] = [p for p in sys.path if not p.startswith(hardcoded)]
    import closure_data as cd
    return {"ffd": ffd, "DataLoader": DataLoader, "cd": cd}


@pytest.fixture
def stub_regions(monkeypatch):
    """The historical region map needs the committed B1 populations file (Perlmutter); the region
    code is the same function in both modules, so both get the same stand-in here."""
    def regions(cr, pt, ppar, populations):
        return (np.floor(np.asarray(pt) * 7 + np.asarray(ppar)) % 4).astype(np.int8)
    for mod in (ri, di):
        monkeypatch.setattr(mod, "historical_cr", lambda: None)
        monkeypatch.setattr(mod, "region_codes", regions)
    return regions


def small_sizes(monkeypatch, n_prior=900, n_pseudo=700):
    monkeypatch.setattr(di, "N_PRIOR", n_prior)
    monkeypatch.setattr(di, "N_PSEUDO", n_pseudo)
    return n_prior, n_pseudo


def run_args(synthetic, **over):
    base = dict(inputs_npz=synthetic.npz, identity_sidecar=synthetic.sidecar,
                populations=Path("/nonexistent/populations.npz"), bootstrap_member=None,
                bootstrap_seed=None)
    base.update(over)
    return SimpleNamespace(**base)


def predecessor_inputs(mods, synthetic, selection, distortion, regions):
    """`run_replicate.main`'s input sequence with the predecessor's module, verbatim order."""
    r1 = (None if distortion.reco_energy_scale is None
          else (selection.pseudo_rows, distortion.reco_energy_scale))
    loaded = ri.load_signal_rows(mods["ffd"], mods["DataLoader"], synthetic.npz,
                                 selection.load_rows, reco_energy_scale=r1)
    inputs, arrays = ri.assemble_closure(mods["ffd"], loaded, selection, distortion,
                                         mods["cd"].ClosureInputs)
    arrays["pseudo_region"] = regions(None, arrays["pseudo_truth"][:, 0],
                                      arrays["pseudo_truth"][:, 1], None)
    arrays["prior_region"] = regions(None, arrays["prior_truth"][:, 0],
                                     arrays["prior_truth"][:, 1], None)
    return inputs, arrays


def assert_same_inputs(a_inputs, a_arrays, b_inputs, b_arrays):
    cmp = ri.compare_inputs(np, a_inputs, b_inputs)
    assert cmp["all_equal"], cmp
    assert a_inputs.digests(np) == b_inputs.digests(np)
    assert sorted(a_arrays) == sorted(b_arrays)
    for k in a_arrays:
        x, y = np.asarray(a_arrays[k]), np.asarray(b_arrays[k])
        assert x.dtype == y.dtype and x.shape == y.shape and x.tobytes() == y.tobytes(), k


# ------------------------------------------------------------------------------------------- #
# (i) predecessor selections: byte-identical through the study runner
# ------------------------------------------------------------------------------------------- #
# DistortionSpec, _r1_distortion, load_signal_rows and scaled_reader gained the final library's
# R2 and product distortions (PROTOCOL-20260925 section 7); without them their outputs are
# byte-identical to the predecessor's, which the predecessor-selection parity test above checks.
UNCHANGED = ("sha256_bytes", "sha256_file", "refuse_sealed_pool", "_frozen_design",
             "historical_tilt_spec", "development_tilt_raw", "unit_mean",
             "Selection", "_sorted_unique", "historical_selection",
             "LoadedRows", "truth_mapping", "_subset", "assemble_closure",
             "historical_cr", "region_codes", "compare_inputs")


def test_unmarked_functions_are_the_predecessors_source():
    for name in UNCHANGED:
        assert inspect.getsource(getattr(di, name)) == inspect.getsource(getattr(ri, name)), name
    for name in ("write_json_atomic",):
        assert inspect.getsource(getattr(rd, name)) == inspect.getsource(getattr(rr, name)), name
    for name in ("SIGNAL_MEMBERS", "FAMILY", "N_PRIOR", "N_PSEUDO", "DEV", "SEALED_POOLS",
                 "PROTOCOL", "POPULATIONS_JSON"):
        assert getattr(di, name) == getattr(ri, name), name


@pytest.mark.parametrize("distortion", ["dev", "D4c_p_up", "R1_x1.05+D1_p0.350"])
def test_predecessor_selection_is_byte_identical(synthetic, historical_mods, stub_regions,
                                                 monkeypatch, distortion):
    n_prior, n_pseudo = small_sizes(monkeypatch)
    kw = dict(pools_npz=synthetic.pools, manifest=synthetic.pool_manifest,
              identity_sidecar=synthetic.sidecar, n_prior=n_prior, n_pseudo=n_pseudo)
    ref_sel = ri.replicate_selection("S", 0, **kw)
    args = run_args(synthetic, historical_halves=False, bank_draw=None, pool="S", replicate=0,
                    pools_npz=synthetic.pools, manifest=synthetic.pool_manifest, n_prior=n_prior,
                    n_pseudo=n_pseudo, family=di.FAMILY, banks_npz=None,
                    bank_manifest=synthetic.bank_manifest)
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    sel, bank_check = rd.select_rows(args, config, historical_mods)
    assert bank_check is None
    assert sel.record == ref_sel.record
    for f in ("load_rows", "prior_rows", "pseudo_rows"):
        assert getattr(sel, f).tobytes() == getattr(ref_sel, f).tobytes()
    d_new, d_old = di.get_distortion(distortion), ri.get_distortion(distortion)
    assert d_new.record == d_old.record and d_new.content_hash() == d_old.content_hash()
    inputs, arrays, _r1, boot = rd.build_inputs(args, config, d_new, sel, historical_mods,
                                                historical_mods["cd"].ClosureInputs)
    assert boot is None
    ref_inputs, ref_arrays = predecessor_inputs(historical_mods, synthetic, ref_sel, d_old,
                                                stub_regions)
    assert_same_inputs(inputs, arrays, ref_inputs, ref_arrays)
    arm = da.get(config.feature_arm)
    ident_new = rd.run_identity(config, arm, "efficiency_corrected", sel, d_new)
    ident_old = rr.run_identity(config, arm, "efficiency_corrected", ref_sel, d_old)
    assert ident_new == ident_old
    # with --banks-npz the pool rows are also checked against DEV
    args.banks_npz = synthetic.banks_npz
    in_dev = np.all(synthetic.bank[sel.load_rows] == 0)
    if in_dev:
        assert rd.select_rows(args, config, historical_mods)[1]["outside"] == 0
    else:
        with pytest.raises(scope.ScopeViolation, match="outside bank DEV"):
            rd.select_rows(args, config, historical_mods)


def test_pool_r_and_undrawn_replicates_are_refused(tmp_path):
    with pytest.raises(scope.ScopeViolation, match="reserve bank"):
        di.refuse_pool("R", 0)
    for pool, rep in (("S", 1), ("T", 2), ("F", 12), ("P", 3)):
        with pytest.raises(scope.ScopeViolation, match="not a predecessor-drawn"):
            di.refuse_pool(pool, rep)
    with pytest.raises(scope.ScopeViolation):
        di.refuse_pool("T", 0, family="E1-identifiability-null")
    with pytest.raises(scope.ScopeViolation):
        di.refuse_pool("T", 0, n_prior=di.N_PSEUDO)
    for pool, rep in (("P", 2), ("F", 11), ("S", 0), ("T", 1)):
        assert di.refuse_pool(pool, rep)["pool"] == pool


# ------------------------------------------------------------------------------------------- #
# (ii) bank draws
# ------------------------------------------------------------------------------------------- #
@pytest.mark.parametrize("bank", ["DEV", "FB", "RB"])
def test_bank_draws_disjoint_deterministic_within_banks(synthetic, bank):
    n_prior, n_pseudo = 1500, 1000
    prior, pseudo, rec = di.draw_from_banks(synthetic.bank, synthetic.ident, "S1", 0, bank,
                                            n_prior, n_pseudo)
    assert prior.size == n_prior and pseudo.size == n_pseudo
    assert np.intersect1d(prior, pseudo).size == 0
    assert np.all(synthetic.bank[pseudo] == di.BANK_CODES[bank])
    assert np.all(synthetic.bank[prior] == di.BANK_CODES["DEV"])
    assert np.all(np.diff(prior) > 0) and np.all(np.diff(pseudo) > 0)
    assert np.all(synthetic.pass_truth[prior]) and np.all(synthetic.pass_truth[pseudo])
    again = di.draw_from_banks(synthetic.bank, synthetic.ident, "S1", 0, bank, n_prior, n_pseudo)
    assert again[0].tobytes() == prior.tobytes() and again[1].tobytes() == pseudo.tobytes()
    assert rec["salts"] == {"pseudo": "pet-final-design-20260925/S1/0/pseudo",
                            "prior": "pet-final-design-20260925/S1/0/prior"}
    # other replicates / stages are fresh draws, overlapping only by chance
    for stage, rep in (("S1", 1), ("S3p", 0)):
        p2, q2, _ = di.draw_from_banks(synthetic.bank, synthetic.ident, stage, rep, bank,
                                       n_prior, n_pseudo)
        n_bank = int((synthetic.bank == di.BANK_CODES[bank]).sum())
        expected = n_pseudo * n_pseudo / n_bank
        shared = np.intersect1d(q2, pseudo).size
        assert shared < n_pseudo and abs(shared - expected) < 6 * np.sqrt(expected) + 3


def test_bank_draw_is_the_lowest_hash_subset_and_row_order_free(synthetic):
    prior, pseudo, rec = di.draw_from_banks(synthetic.bank, synthetic.ident, "S1", 3, "FB",
                                            800, 600)
    fb = np.flatnonzero(synthetic.bank == 1)
    u = rp.uniform_hash(synthetic.ident[fb], rp.seed_from_salt(rec["salts"]["pseudo"]))
    assert np.array_equal(pseudo, np.sort(fb[np.argsort(u, kind="stable")[:600]]))
    dev = np.flatnonzero(synthetic.bank == 0)
    u2 = rp.uniform_hash(synthetic.ident[dev], rp.seed_from_salt(rec["salts"]["prior"]))
    assert np.array_equal(prior, np.sort(dev[np.argsort(u2, kind="stable")[:800]]))
    # the choice depends on identities, not positions: hashing a permuted bank picks the same set
    perm = np.random.default_rng(0).permutation(fb.size)
    up = rp.uniform_hash(synthetic.ident[fb[perm]], rp.seed_from_salt(rec["salts"]["pseudo"]))
    assert np.array_equal(np.sort(fb[perm][np.argsort(up)[:600]]), pseudo)


def test_dev_pseudodata_is_excluded_from_the_prior(synthetic):
    prior, pseudo, rec = di.draw_from_banks(synthetic.bank, synthetic.ident, "S1", 0, "DEV",
                                            3000, 2500)
    assert rec["n_prior_candidates"] == int((synthetic.bank == 0).sum()) - 2500
    assert np.intersect1d(prior, pseudo).size == 0
    with pytest.raises(SystemExit):
        di.draw_from_banks(synthetic.bank, synthetic.ident, "S/1", 0, "DEV", 10, 10)
    with pytest.raises(SystemExit):
        di.draw_from_banks(synthetic.bank, synthetic.ident, "S1", 0, "RB", 10, 10**6)


def test_bank_selection_checks_the_manifest(synthetic, tmp_path):
    sel = di.bank_selection("S1", 0, "DEV", banks_npz=synthetic.banks_npz,
                            identity_sidecar=synthetic.sidecar,
                            bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)
    assert sel.mode == "bank" and sel.record["banks"]["banks_npz_sha256"] == sha(synthetic.banks_npz)
    assert sel.record["pseudo_rows_sha256"] == rp.rows_digest(sel.pseudo_rows)
    assert np.array_equal(sel.load_rows, np.union1d(sel.prior_rows, sel.pseudo_rows))
    tampered = tmp_path / "banks.npz"
    bank = synthetic.bank.copy()
    bank[np.flatnonzero(bank == 1)[0]] = 0
    np.savez(tampered, bank_code=bank)
    with pytest.raises(SystemExit, match="sha256"):
        di.bank_selection("S1", 0, "DEV", banks_npz=tampered, identity_sidecar=synthetic.sidecar,
                          bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)
    other = tmp_path / "id.npz"
    np.savez(other, sig_event_id=synthetic.ident[::-1].copy())
    with pytest.raises(SystemExit, match="bank manifest"):
        di.bank_selection("S1", 0, "DEV", banks_npz=synthetic.banks_npz, identity_sidecar=other,
                          bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)


def test_bank_draw_through_the_input_path(synthetic, historical_mods, stub_regions):
    sel = di.bank_selection("S1", 1, "DEV", banks_npz=synthetic.banks_npz,
                            identity_sidecar=synthetic.sidecar,
                            bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)
    args = run_args(synthetic)
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    inputs, arrays, _r1, _b = rd.build_inputs(args, config, di.get_distortion("dev"), sel,
                                              historical_mods, historical_mods["cd"].ClosureInputs)
    assert np.array_equal(arrays["pseudo_rows"], sel.pseudo_rows)
    assert np.array_equal(arrays["prior_rows"], sel.prior_rows)
    assert np.all(arrays["pseudo_pass_truth"]) and np.all(arrays["prior_pass_truth"])
    assert len(inputs.pdata["rows"]) == int(arrays["pseudo_pass_reco"].sum())


# ------------------------------------------------------------------------------------------- #
# (iii) FB / RB access
# ------------------------------------------------------------------------------------------- #
def test_committed_protocol_seals_fb_and_rb():
    assert di.refuse_bank("DEV")["sealed"] is False
    for bank in ("FB", "RB"):
        with pytest.raises(scope.ScopeViolation, match="sealed"):
            di.refuse_bank(bank)
    with pytest.raises(SystemExit):
        di.refuse_bank("R")


def _git(d, *a):
    subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)


def test_release_amendments_open_exactly_their_bank(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    proto = repo / "PROTOCOL.md"
    base = di.STUDY_PROTOCOL.read_text()
    proto.write_text(base)
    _git(repo, "add", "PROTOCOL.md")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1")
    for bank in ("FB", "RB"):
        with pytest.raises(scope.ScopeViolation):
            di.refuse_bank(bank, proto)
    # prose, a wrong heading level, or the wrong bank do not release
    for text in ("\nThe FB release amendment is planned.\n",
                 "\n## Amendment 1 (2026-10-01): FB release\n",
                 "\n#### Amendment 1 (2026-10-01): FB release\n",
                 "\n### Amendment 1 (2026-10-01): RB release\n"):
        proto.write_text(base + text)
        _git(repo, "commit", "-qam", "try")
        with pytest.raises(scope.ScopeViolation):
            di.refuse_bank("FB", proto)
    # an amendment that is not committed does not release
    proto.write_text(base + "\n### Amendment 1 (2026-10-01): FB release\n")
    with pytest.raises(scope.ScopeViolation, match="uncommitted"):
        di.refuse_bank("FB", proto)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "FB release")
    got = di.refuse_bank("FB", proto)
    assert got["released_by"].startswith("### Amendment 1") and got["git"]["git"] == "committed"
    with pytest.raises(scope.ScopeViolation):
        di.refuse_bank("RB", proto)                    # FB's release does not open RB
    proto.write_text(proto.read_text() + "\n### Amendment 2 (2026-11-01): RB release for §11\n")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "RB release")
    assert di.refuse_bank("RB", proto)["sealed"] is True


def _main_args(tmp_path, *extra):
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    return ["--config", str(DEV1_CONFIG), "--config-hash", config.content_hash(), "--repo",
            str(REPO), "--out", str(tmp_path / "out"), "--inputs-npz", str(tmp_path / "G2.npz"),
            "--identity-sidecar", str(tmp_path / "id.npz"), "--populations",
            str(tmp_path / "pop.npz"), *extra]


def test_runner_refuses_sealed_banks_and_pool_r_before_reading(tmp_path):
    for extra in (["--bank-draw", "S4:0", "--pseudo-bank", "FB", "--banks-npz", "x.npz"],
                  ["--bank-draw", "S4:0", "--pseudo-bank", "RB", "--banks-npz", "x.npz"],
                  ["--pool", "R", "--replicate", "0", "--pools-npz", "p", "--manifest", "m"],
                  ["--pool", "S", "--replicate", "4", "--pools-npz", "p", "--manifest", "m"]):
        with pytest.raises(scope.ScopeViolation):
            rd.main(_main_args(tmp_path, *extra))
        assert not (tmp_path / "out").exists()
    with pytest.raises(SystemExit):     # --pseudo-bank without --bank-draw
        rd.parse_args(_main_args(tmp_path, "--historical-halves", "--pseudo-bank", "DEV"))
    with pytest.raises(SystemExit):     # bank draw without banks
        rd.parse_args(_main_args(tmp_path, "--bank-draw", "S1:0", "--pseudo-bank", "DEV"))
    with pytest.raises(SystemExit):     # malformed
        rd.parse_args(_main_args(tmp_path, "--bank-draw", "S1", "--pseudo-bank", "DEV",
                                 "--banks-npz", "x"))
    with pytest.raises(SystemExit):     # member without seed
        rd.parse_args(_main_args(tmp_path, "--bank-draw", "S1:0", "--pseudo-bank", "DEV",
                                 "--banks-npz", "x", "--bootstrap-member", "1"))
    a = rd.parse_args(_main_args(tmp_path, "--bank-draw", "S1:7", "--pseudo-bank", "DEV",
                                 "--banks-npz", "x"))
    assert (a.bank_stage, a.bank_replicate) == ("S1", 7)


# ------------------------------------------------------------------------------------------- #
# (iv) bootstrap members
# ------------------------------------------------------------------------------------------- #
def test_poisson_counts_reproducible_mean_one_and_order_free():
    rng = np.random.default_rng(1)
    ident = np.stack([rng.integers(1, 10**6, 200_000), rng.integers(0, 10**4, 200_000),
                      np.arange(200_000)], 1).astype(np.int64)
    k = di.bootstrap_counts(ident, 11, 3, "pseudo")
    assert k.tobytes() == di.bootstrap_counts(ident, 11, 3, "pseudo").tobytes()
    assert abs(k.mean() - 1) < 0.01 and abs(k.var() - 1) < 0.02
    assert abs((k == 0).mean() - np.exp(-1)) < 0.005 and abs((k == 2).mean() - np.exp(-1) / 2) < 0.005
    perm = rng.permutation(ident.shape[0])
    assert np.array_equal(di.bootstrap_counts(ident[perm], 11, 3, "pseudo"), k[perm])
    for other in (di.bootstrap_counts(ident, 11, 4, "pseudo"),
                  di.bootstrap_counts(ident, 12, 3, "pseudo"),
                  di.bootstrap_counts(ident, 11, 3, "prior")):
        assert abs(np.corrcoef(k, other)[0, 1]) < 0.01
    u = np.array([0.0, np.exp(-1) - 1e-12, np.exp(-1) + 1e-12, 1 - 1e-16])
    assert di.poisson1_quantile(u).tolist()[:3] == [0.0, 0.0, 1.0]


def test_member_config_changes_only_the_seeds():
    import freeze_runs as fr
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    m1, rec = di.bootstrap_config(config, 1)
    m1b, _ = di.bootstrap_config(config, 1)
    m2, _ = di.bootstrap_config(config, 2)
    assert m1.content_hash() == m1b.content_hash() != m2.content_hash() != config.content_hash()
    seeds = {m1.step1.seed, m1.step1.validation.seed, m1.step2.seed, m1.step2.validation.seed}
    assert len(seeds) == 4 and config.step1.seed not in seeds
    # nothing but the seeds differs: reseeding both back gives the original config
    back = m1.replace(step1=fr.reseed(m1, config.step1.seed, m1.name, m1.note).step1,
                      step2=fr.reseed(m1, config.step2.seed, m1.name, m1.note).step2)
    assert back.content_hash() == config.content_hash()
    assert rec["member_config_hash"] == m1.content_hash()


def test_bootstrap_resamples_weights_and_keeps_the_target(synthetic, historical_mods,
                                                          stub_regions):
    sel = di.bank_selection("S1", 2, "DEV", banks_npz=synthetic.banks_npz,
                            identity_sidecar=synthetic.sidecar,
                            bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    dist = di.get_distortion("dev")
    cls = historical_mods["cd"].ClosureInputs
    base_in, base_ar, _, _ = rd.build_inputs(run_args(synthetic), config, dist, sel,
                                             historical_mods, cls)
    args = run_args(synthetic, bootstrap_member=2, bootstrap_seed=99)
    b_in, b_ar, _, rec = rd.build_inputs(args, config, dist, sel, historical_mods, cls)
    b_in2, b_ar2, _, _ = rd.build_inputs(args, config, dist, sel, historical_mods, cls)
    # reproducible
    for k in b_ar:
        assert np.asarray(b_ar[k]).tobytes() == np.asarray(b_ar2[k]).tobytes(), k
    assert b_in.pdata["weight"].tobytes() == b_in2.pdata["weight"].tobytes()
    # the score target is unchanged: pseudodata truth, weights, distortion
    for k in ("pseudo_truth", "pseudo_w_truth", "pseudo_w_reco", "pseudo_distortion",
              "pseudo_pass_truth", "pseudo_rows", "prior_oracle"):
        assert np.asarray(b_ar[k]).tobytes() == np.asarray(base_ar[k]).tobytes(), k
    kp, kq = b_ar["pseudo_bootstrap_weight"], b_ar["prior_bootstrap_weight"]
    idp = synthetic.ident[sel.pseudo_rows]
    assert np.array_equal(kp, di.bootstrap_counts(idp, 99, 2, "pseudo"))
    np.testing.assert_array_equal(b_ar["prior_w_truth"], base_ar["prior_w_truth"] * kq)
    np.testing.assert_array_equal(b_ar["prior_w_truth_unresampled"], base_ar["prior_w_truth"])
    # engine weights = Poisson x original, before normalization (float32 of the float64 product)
    pos = np.searchsorted(base_ar["pseudo_rows"], base_in.pdata["rows"])
    np.testing.assert_array_equal(
        b_in.pdata["weight"],
        (base_in.pdata["weight"].astype(np.float64) * kp[pos]).astype(np.float32))
    np.testing.assert_array_equal(
        b_in.mc["weight"], (base_in.mc["weight"].astype(np.float64) * kq).astype(np.float32))
    np.testing.assert_array_equal(
        b_in.mc["weight_reco"],
        (base_in.mc["weight_reco"].astype(np.float64) * kq).astype(np.float32))
    # the event arrays the networks see are untouched
    assert b_in.digests(np) == base_in.digests(np)
    assert rec["weight_digests_after"]["pdata.weight"] == di.sha256_bytes(b_in.pdata["weight"])
    assert 0.8 < rec["counts_prior"]["mean"] < 1.2 and rec["counts_prior"]["n"] == 900


# ------------------------------------------------------------------------------------------- #
# (v) null distortion
# ------------------------------------------------------------------------------------------- #
def test_null_distortion_target_is_the_undistorted_truth(synthetic, historical_mods,
                                                         stub_regions):
    sel = di.bank_selection("S1", 0, "DEV", banks_npz=synthetic.banks_npz,
                            identity_sidecar=synthetic.sidecar,
                            bank_manifest=synthetic.bank_manifest, n_prior=900, n_pseudo=700)
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    null = di.get_distortion("null")
    assert null.name == "null" and null.reco_energy_scale is None and not null.needs_species
    inputs, arrays, _, _ = rd.build_inputs(run_args(synthetic), config, null, sel,
                                           historical_mods, historical_mods["cd"].ClosureInputs)
    assert np.all(arrays["pseudo_distortion"] == 1.0) and np.all(arrays["prior_oracle"] == 1.0)
    s1 = arrays["pseudo_pass_reco"] & arrays["pseudo_pass_truth"]
    np.testing.assert_array_equal(inputs.pdata["weight"],
                                  arrays["pseudo_w_reco"][s1].astype(np.float32))
    assert inputs.meta["tilt_spec"]["pre_normalization_mean"] == 1.0
    combo = di.get_distortion("R1_x1.05+null")
    assert combo.reco_energy_scale == 1.05 and combo.record["truth"]["name"] == "null"
    assert "null" not in ri.dist.registry()             # a study-only name, not a phase_e id


# ------------------------------------------------------------------------------------------- #
# The counts arm, the miss rule
# ------------------------------------------------------------------------------------------- #
def test_counts_arm_appends_standardized_truncated_cloud_counts(synthetic, historical_mods):
    import b2_driver as b2d
    import distortions as dist
    ffd = historical_mods["ffd"]
    rows = np.flatnonzero(synthetic.pass_truth)[:3000]
    loaded = ri.load_signal_rows(ffd, historical_mods["DataLoader"], synthetic.npz, rows)
    gen = np.asarray(loaded.mc.gen)
    counts = da.species_counts(np, gen)
    ref = dist.count_species(loaded.pdg)
    for mine, theirs in (("n_proton", "p"), ("n_neutron", "n"), ("n_charged_pion", "pipm"),
                         ("n_neutral_pion", "pi0")):
        np.testing.assert_array_equal(counts[mine], ref[theirs].astype(np.float64))
    real = (np.asarray(loaded.pdg) != 0).sum(1)
    np.testing.assert_array_equal(counts["n_valid"], real)
    known = sum(counts[k] for k in ("n_proton", "n_neutron", "n_charged_pion", "n_neutral_pion"))
    np.testing.assert_array_equal(counts["n_other"], real - known)
    assert counts["n_other"].sum() > 0                  # photons land in `other`

    def make_inputs():
        pg = np.asarray(loaded.mc.pass_gen, bool)
        return SimpleNamespace(
            pdata={"reco": np.asarray(loaded.mc.reco)[:100],
                   "reco_evt": np.asarray(loaded.mc.reco_evt)[:100], "rows": rows[:100]},
            mc={"reco": np.asarray(loaded.mc.reco), "reco_evt": np.asarray(loaded.mc.reco_evt),
                "gen": gen.copy(), "gen_evt": np.asarray(loaded.mc.gen_evt).copy(),
                "pass_reco": np.asarray(loaded.mc.pass_reco, bool), "pass_gen": pg,
                "rows": rows},
            meta={"coord_gen": tuple(loaded.coord_gen)})
    arm = da.get("pdg_onehot_counts")
    a, b = make_inputs(), make_inputs()
    rec = da.apply_arm(np, arm, a, lambda *x: None, None, b2d)
    rec_base = da.apply_arm(np, da.get("pdg_onehot"), b, lambda *x: None, None, b2d)
    assert rec_base["arm"] == "pdg_onehot"              # predecessor arm, predecessor path
    assert a.mc["gen"].tobytes() == b.mc["gen"].tobytes()          # the same one-hot cloud
    assert a.meta["coord_gen"] == b.meta["coord_gen"]
    n0 = b.mc["gen_evt"].shape[1]
    assert a.mc["gen_evt"].shape[1] == n0 + 6
    assert a.mc["gen_evt"][:, :n0].tobytes() == b.mc["gen_evt"].tobytes()
    pg = a.mc["pass_gen"]
    z = a.mc["gen_evt"][:, n0:].astype(np.float64)
    np.testing.assert_allclose(z[pg].mean(0), 0, atol=1e-5)
    np.testing.assert_allclose(z[pg].std(0), 1, atol=1e-4)
    assert np.all(z[~pg] == 0)
    assert rec["step2"] == [f"truth_cloud_counts:{n}" for n in da.COUNT_NAMES]
    assert arm.content_hash() != da.get("pdg_onehot").content_hash()
    with pytest.raises(KeyError):
        da.get("no_such_arm")


def test_miss_rule_from_config_else_cli():
    config = RunConfig.from_json(DEV1_CONFIG.read_text())
    assert rd.resolve_miss_mode(config, None) == ("carry", "default")
    assert rd.resolve_miss_mode(config, "efficiency_corrected") == ("efficiency_corrected", "cli")

    class WithField(SimpleNamespace):
        pass
    c = WithField(step2_miss_mode="efficiency_corrected")
    assert rd.resolve_miss_mode(c, None) == ("efficiency_corrected", "config")
    assert rd.resolve_miss_mode(c, "efficiency_corrected") == ("efficiency_corrected", "config")
    with pytest.raises(SystemExit, match="contradicts"):
        rd.resolve_miss_mode(c, "carry")
    with pytest.raises(SystemExit):
        rd.resolve_miss_mode(WithField(step2_miss_mode="drop"), None)


# ------------------------------------------------------------------------------------------- #
# The launcher library (bash >= 4: Perlmutter; skipped on macOS's bash 3.2)
# ------------------------------------------------------------------------------------------- #
def _bash4() -> str | None:
    for b in (shutil.which("bash"), "/opt/homebrew/bin/bash", "/usr/local/bin/bash"):
        if b and os.path.exists(b):
            v = subprocess.run([b, "-c", "echo ${BASH_VERSINFO[0]}"], capture_output=True,
                               text=True).stdout.strip()
            if v.isdigit() and int(v) >= 4:
                return b
    return None


def test_design_lib_run_row_builds_the_study_command(tmp_path):
    # probed inside the test, not at import: a module-level subprocess made collection fail under
    # mnv_guarded_run.py (Perlmutter job 58886821); run this test outside the guard
    bash = _bash4()
    if bash is None:
        pytest.skip("needs bash >= 4 (the launcher's shell)")
    lib = STUDY / "jobs" / "design_lib.sh"
    rows = {
        "bank": "r1\tcfg.json\tH\tBANK:DEV:S1:3\tnull\t-\t--step2-miss-mode efficiency_corrected",
        "pool": "r2\tcfg.json\tH\tT:1\tdev\t-\t-",
        "boot": "r3\tcfg.json\tH\tBANK:FB:S5:0\tdev\t-\t--bootstrap-member 2 --bootstrap-seed 7",
    }
    out = {}
    for key, row in rows.items():
        script = (f'set -eo pipefail; MINE="{REPO}"; OUT="{tmp_path}"; SLURM_JOB_ID=1; '
                  f'source "{CONFIRM}/jobs/confirm_lib.sh"; source "{lib}"; '
                  f'DESIGN_DRY_RUN=1 run_row "$1" 0 123')
        r = subprocess.run([bash, "-c", script, "x", row], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        out[key] = r.stdout.split("\n")
    bank = " ".join(out["bank"])
    assert "final_design/runner/run_design.py" in bank
    assert "--bank-draw S1:3 --pseudo-bank DEV --banks-npz" in bank and "--distortion null" in bank
    assert "--pool" not in bank and "run_replicate.py" not in bank
    pool = " ".join(out["pool"])
    assert "--pool T --replicate 1 --pools-npz" in pool and "--banks-npz" in pool
    assert "--bank-draw S5:0 --pseudo-bank FB" in " ".join(out["boot"])
    assert "--bootstrap-member 2 --bootstrap-seed 7" in " ".join(out["boot"])


# ------------------------------------------------------------------------------------------- #
# The committed bank manifest (and, on Perlmutter, the built banks.npz)
# ------------------------------------------------------------------------------------------- #
CLUSTER_BANKS = Path("/pscratch/sd/j/josephrb/pet-final-design-20260925/impl-runner/banks/"
                     "banks.npz")


def test_committed_bank_manifest_is_consistent():
    m = json.loads(di.BANK_MANIFEST.read_text())
    assert {k: v["count"] for k, v in m["banks"].items()} == {
        "DEV": 45_089_191, "FB": 2_646_891, "RB": 1_414_846}
    assert m["digest_check"]["summary"]["ok"] and m["digest_check"]["summary"]["n_mismatch"] == 0
    assert m["expected_counts_check"]["equal"] and m["code"]["clean"]
    assert all(v["bank"] == "DEV" for v in m["known_historical_rows_in_pools"].values())


@pytest.mark.skipif(not CLUSTER_BANKS.exists(), reason="perlmutter: the built banks.npz")
def test_cluster_banks_match_the_committed_manifest():
    codes, rec = di.load_bank_codes(CLUSTER_BANKS)
    assert rec["counts"]["FB"] == 2_646_891 and codes.size == 49_152_885
