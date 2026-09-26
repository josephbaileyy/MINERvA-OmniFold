"""Local tests of the PET2-hybrid path (no GPU, no real inventory).

* `theirs_rows`: the grouped one-pass gather against the historical `materialize_theirs` itself on
  synthetic signal-MC shards (byte equality, one open per shard), the per-leg split against the
  historical per-leg gathers (`prematerialize_theirs` layout), every fail-closed refusal, the keyed
  cache, and `crosscheck` against a synthetic historical cache in the historical (unsorted) order;
* `hybrid_driver`: the initialization verdicts, the step-1 substitution, the config checks;
* `make_pet2_configs`: P2pre and P2scr differ ONLY in the step-1 init; the declared PET2 recipe;
  C's step 2 and split; drawn selections only (needs TensorFlow's import for the historical
  recipe constants; skipped without it);
* `run_pet2_replicate`: the selection and distortion refusals;
* optional, `PFD_PRETRAINED_STATE`/`PFD_PRETRAINED_MANIFEST` set to local copies of the export:
  the verifier on a REAL PET2-small, loaded (must pass as pretrained) and scratch (must pass as
  scratch, and fail as pretrained).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PET = STUDY.parent
CAMPAIGN = PET / "improvement_campaign"
COMP = PET / "configuration_comparison"
for _p in reversed((HERE, STUDY / "dev", CAMPAIGN, CAMPAIGN / "phase_b" / "pet",
                    CAMPAIGN / "confirm")):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import b2_arms  # noqa: E402
import hybrid_driver as hd  # noqa: E402
import theirs_rows as tr  # noqa: E402  (appends configuration_comparison LAST on sys.path)
import materialize_theirs as mtz  # noqa: E402
from recipe import RunConfig  # noqa: E402

C_CONFIG = CAMPAIGN / "phase_b/pet/configs/b2e4-M-K10-s1.json"
PINNED = "2480f269064b4d69f323d8681acc776526cec20a89e7cea8c2338004551231b5"


# ------------------------------------------------------------------------------------------- #
# Synthetic signal-MC shards and join
# ------------------------------------------------------------------------------------------- #
def _shard_arrays(rng: np.random.Generator, n: int) -> dict[str, np.ndarray]:
    tokens = rng.normal(size=(n, 33, 5)).astype(np.float32)
    tokens[..., 3] = np.abs(tokens[..., 3]) + 0.1           # log E, never exactly 0
    tokens[..., 4] = rng.integers(0, 8, size=(n, 33))       # PID
    add = rng.normal(size=(n, 33, 5)).astype(np.float32)
    add[..., 0] = np.where(rng.random((n, 33)) < 0.2, -999.0, np.abs(add[..., 0]) * 10)
    ntok = rng.integers(1, 34, size=n)
    pad = np.arange(33)[None, :] >= ntok[:, None]
    tokens[pad] = 0.0
    add[pad] = 0.0
    return {"tokens": tokens, "add_info": add,
            "globals": rng.normal(size=(n, 16)).astype(np.float32),
            "identity": np.stack([np.full(n, 7), np.arange(n), np.arange(n)], 1).astype(np.int32)}


@pytest.fixture()
def world(tmp_path: Path) -> SimpleNamespace:
    """3 shards (two playlists), a 400-row inventory, a join with unmatched !pass_reco rows."""
    rng = np.random.default_rng(3)
    files = []
    sizes = [150, 120, 180]
    for k, (pl, n) in enumerate(zip(("1A_MC", "1A_MC", "1F_MC"), sizes)):
        d = tmp_path / "theirs_inputs" / pl
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"MasterAnaDev_mc_AnaTuple_run0011000{k}_Playlist.theirs.npz"
        np.savez_compressed(f, **_shard_arrays(rng, n))
        files.append(str(f))
    origin = np.concatenate([np.stack([np.full(n, k, np.int32), np.arange(n, dtype=np.int32)], 1)
                             for k, n in enumerate(sizes)])
    n_inv = 400
    pass_reco = rng.random(n_inv) < 0.6
    built = rng.permutation(origin.shape[0])[:n_inv]
    row_index = built.astype(np.int64)
    unmatched = (~pass_reco) & (rng.random(n_inv) < 0.5)
    row_index[unmatched] = -1
    join = tmp_path / "join"
    join.mkdir()
    np.savez_compressed(join / "join_sig.npz", row_index=row_index, origin=origin)
    report = {"reco_coverage": {"pass_reco_rows": int(pass_reco.sum()),
                                "pass_reco_matched": int(pass_reco.sum()),
                                "pass_reco_unmatched": 0},
              "stream": "sig", "identity_fields": list(tr.IDENTITY_FIELDS),
              "inventory_rows": n_inv, "built_rows": int(origin.shape[0]),
              "built_files": len(files), "positional_fallback": "never", "files": files,
              "duplicate_built_keys": 0}
    (join / "join_sig.json").write_text(json.dumps(report))
    inv = tmp_path / "G2_SYNTH_P12.npz"
    np.savez(inv, pass_reco=pass_reco, measured_scalars=np.zeros(3))
    return SimpleNamespace(files=files, origin=origin, row_index=row_index, pass_reco=pass_reco,
                           join=join, report=report, inventory=inv, n_inv=n_inv,
                           index=tr.load_index(join, inventory_rows=n_inv))


def _counting(calls: list) -> object:
    def materialize(files, row_index, origin, rows, pass_reco, **kw):
        out = mtz.materialize(files, row_index, origin, rows, pass_reco, **kw)
        calls.append((len(rows), out["shards_opened"]))
        return out
    return materialize


# ------------------------------------------------------------------------------------------- #
# theirs_rows
# ------------------------------------------------------------------------------------------- #
@pytest.mark.parametrize("group_rows", [7, 64, 100_000])
def test_gather_is_byte_identical_to_historical_materialize(world, group_rows):
    rows = np.sort(np.random.default_rng(1).choice(world.n_inv, 260, replace=False))
    calls: list = []
    got = tr.gather(world.index, rows, world.pass_reco, group_rows=group_rows,
                    materialize=_counting(calls))
    ref = mtz.materialize(world.files, world.row_index, world.origin, rows, world.pass_reco)
    assert got["packed"].tobytes() == ref["packed"].tobytes()
    assert got["globals"].tobytes() == ref["globals"].tobytes()
    assert got["packed"].dtype == ref["packed"].dtype == np.float32
    # each shard opened exactly once in total, however the rows were grouped
    needed = np.unique(world.origin[world.row_index[rows][world.row_index[rows] >= 0], 0]).size
    assert sum(o for _, o in calls) == needed == got["record"]["shards_opened"]
    if group_rows == 7:
        assert len(calls) == needed        # a group never splits a shard
    assert got["record"]["nonzero_rows_without_reco"] == 0


def test_rows_without_reco_are_zero_and_reco_rows_are_not(world):
    rows = np.arange(world.n_inv)
    got = tr.gather(world.index, rows, world.pass_reco)
    flat = got["packed"].reshape(rows.size, -1)
    assert not flat[~world.pass_reco].any() and not got["globals"][~world.pass_reco].any()
    assert flat[world.pass_reco].any(axis=1).all()
    rec = got["record"]
    assert rec["rows_without_reco"] == int((~world.pass_reco).sum())
    assert rec["unmatched_without_reco"] == int((world.row_index < 0).sum())


def test_gather_legs_equals_per_leg_historical_gathers(world):
    rng = np.random.default_rng(5)
    reco_rows = np.flatnonzero(world.pass_reco)
    pdata = np.sort(rng.choice(reco_rows, 90, replace=False))
    prior = np.sort(rng.choice(np.setdiff1d(np.arange(world.n_inv), pdata), 200, replace=False))
    got = tr.gather_legs(world.index, {"pdata": pdata, "prior": prior}, world.pass_reco,
                         group_rows=50)
    for name, rows in (("pdata", pdata), ("prior", prior)):
        ref = mtz.materialize(world.files, world.row_index, world.origin, rows, world.pass_reco)
        assert got[name]["packed"].tobytes() == ref["packed"].tobytes()
        assert got[name]["globals"].tobytes() == ref["globals"].tobytes()
        assert got["legs"][name]["rows_sha256"] == tr.rows_digest(rows)


def test_missing_reco_row_fails_closed(world):
    row_index = world.row_index.copy()
    victim = int(np.flatnonzero(world.pass_reco)[0])
    row_index[victim] = -1
    index = tr.TheirsIndex(world.files, row_index, world.origin, {})
    with pytest.raises(SystemExit, match="no built PET2 input"):
        tr.gather(index, np.array([victim]), world.pass_reco)
    with pytest.raises(SystemExit):
        tr.gather(index, np.sort(np.array([victim, victim + 1])), world.pass_reco)


@pytest.mark.parametrize("rows,match", [
    (np.array([5, 3]), "sorted"), (np.array([3, 3]), "sorted"), (np.array([-1, 2]), "outside"),
    (np.array([1, 400]), "outside"), (np.array([], dtype=np.int64), "no rows"),
    (np.array([1.0, 2.0]), "integer")])
def test_bad_row_sets_are_refused(world, rows, match):
    with pytest.raises(SystemExit, match=match):
        tr.gather(world.index, rows, world.pass_reco)


def test_nonfinite_value_is_refused_with_its_location(world):
    victim = int(np.flatnonzero(world.pass_reco & (world.row_index >= 0))[0])
    shard, local = world.origin[world.row_index[victim]]
    blob = dict(np.load(world.files[shard]))
    blob["add_info"] = blob["add_info"].copy()
    blob["add_info"][local, 0, 0] = np.nan          # a stored NaN dE/dx on the first token
    np.savez_compressed(world.files[shard], **blob)
    with pytest.raises(SystemExit, match="non-finite") as err:
        tr.gather(world.index, np.array([victim]), world.pass_reco)
    msg = str(err.value)
    assert f'"inventory_row": {victim}' in msg and '"stored_member": "add_info"' in msg
    assert '"position": [0, 0, 5]' in msg


def test_nonfinite_momentum_policy(world):
    reco = np.flatnonzero(world.pass_reco & (world.row_index >= 0))
    victim = int(reco[3])
    shard, local = world.origin[world.row_index[victim]]
    blob = dict(np.load(world.files[shard]))
    blob["tokens"] = blob["tokens"].copy()
    blob["tokens"][local, 0, 0:3] = np.nan               # the observed shape: px = py = pz = NaN
    np.savez_compressed(world.files[shard], **blob)
    rows = np.sort(np.concatenate([reco[:10], np.flatnonzero(~world.pass_reco)[:5]]))
    with pytest.raises(SystemExit, match="non-finite"):
        tr.gather(world.index, rows, world.pass_reco)
    got = tr.gather(world.index, rows, world.pass_reco, nonfinite_momentum="zero")
    ref = mtz.materialize(world.files, world.row_index, world.origin, rows, world.pass_reco)
    i = int(np.searchsorted(rows, victim))
    assert np.isfinite(got["packed"]).all()
    rep = got["record"]["nonfinite_momentum_repairs"]
    assert [r["inventory_row"] for r in rep] == [victim] and rep[0]["tokens"] == [0]
    tok = got["packed"][i, 0]
    assert tok[0] == 0.0 and tok[1] == 0.0 and tok[2] == np.float32(np.log(1e-6))
    assert tok[3:].tobytes() == ref["packed"][i, 0, 3:].tobytes()       # log E, PID, add_info
    mask = np.ones(len(rows), bool)
    mask[i] = False
    assert got["packed"][mask].tobytes() == ref["packed"][mask].tobytes()
    assert got["packed"][i, 1:].tobytes() == ref["packed"][i, 1:].tobytes()
    assert got["record"]["nonfinite_momentum_policy"] == "zero"
    # a non-finite value outside the momentum is never repaired
    blob["add_info"] = blob["add_info"].copy()
    blob["add_info"][local, 1, 2] = np.inf
    np.savez_compressed(world.files[shard], **blob)
    with pytest.raises(SystemExit, match="outside the token momentum"):
        tr.gather(world.index, rows, world.pass_reco, nonfinite_momentum="zero")
    # the policy is part of the cache key
    legs = {"prior": rows}
    k1 = tr.cache_key(world.index, "d", legs, "refuse")
    assert k1 != tr.cache_key(world.index, "d", legs, "zero")


def test_census_counts_stored_nonfinite_values(world):
    reco = np.flatnonzero(world.pass_reco & (world.row_index >= 0))
    victim = int(reco[2])
    shard, local = world.origin[world.row_index[victim]]
    blob = dict(np.load(world.files[shard]))
    blob["tokens"] = blob["tokens"].copy()
    blob["tokens"][local, 4, 0:3] = np.nan
    unused = np.setdiff1d(np.flatnonzero(world.origin[:, 0] == shard),
                          world.row_index[world.row_index >= 0])[0]
    blob["tokens"][world.origin[unused, 1], 1, 1] = np.inf      # a row no inventory row uses
    np.savez_compressed(world.files[shard], **blob)
    rep = tr.census(world.inventory, world.join, inventory_rows=world.n_inv)
    m = rep["totals"]["momentum"]
    assert (m["built_rows"], m["tokens_or_entries"], m["reco_rows"],
            m["reco_tokens_or_entries"]) == (2, 2, 1, 1)
    assert rep["listed"] == [{"class": "momentum", "inventory_row": victim,
                              "shard": world.files[shard], "row_in_shard": int(local),
                              "tokens_or_entries": [4],
                              "pid": [repr(float(blob["tokens"][local, 4, 4]))]}]
    assert rep["totals"]["globals"]["built_rows"] == 0


def test_pass_reco_length_mismatch_refused(world):
    with pytest.raises(SystemExit, match="pass_reco"):
        tr.gather(world.index, np.array([1, 2]), world.pass_reco[:-1])


@pytest.mark.parametrize("bad", ["/x/1A_Data/MasterAnaDev_data_AnaTuple_run1_Playlist.theirs.npz",
                                 "/x/1A_MC/MasterAnaDev_bkg_AnaTuple_run1_Playlist.theirs.npz",
                                 "/x/1A_MC/MasterAnaDev_mc_AnaTuple_run1_Playlist.npz"])
def test_non_signal_shard_in_join_is_refused(world, bad):
    report = dict(world.report)
    report["files"] = world.files[:-1] + [bad]
    (world.join / "join_sig.json").write_text(json.dumps(report))
    with pytest.raises(scope.ScopeViolation, match="signal-MC"):
        tr.load_index(world.join, inventory_rows=world.n_inv)


@pytest.mark.parametrize("field,value,match", [
    ("stream", "data", "stream"), ("inventory_rows", 401, "inventory"),
    ("identity_fields", ["ev_run", "ev_subrun", "ev_gate"], "identity"),
    ("positional_fallback", "allowed", "positional"),
    ("reco_coverage", {"pass_reco_unmatched": 3}, "unmatched")])
def test_unusable_join_report_is_refused(world, field, value, match):
    report = dict(world.report)
    report[field] = value
    (world.join / "join_sig.json").write_text(json.dumps(report))
    with pytest.raises(SystemExit, match=match):
        tr.load_index(world.join, inventory_rows=world.n_inv)


def test_read_pass_reco_is_signal_only(world):
    got, digest = tr.read_pass_reco(world.inventory)
    assert np.array_equal(got, world.pass_reco)
    assert digest == tr.sha256_array(world.pass_reco)


def test_cache_round_trip_and_key_refusal(world, tmp_path):
    legs = {"pdata": np.flatnonzero(world.pass_reco)[:40], "prior": np.arange(100, 180)}
    cache = tmp_path / "cache" / "theirs.npz"
    first = tr.gather_legs_cached(world.index, legs, world.pass_reco, "digest-a", cache)
    assert first["cache"]["reused"] is False and cache.exists()
    again = tr.gather_legs_cached(world.index, legs, world.pass_reco, "digest-a", cache)
    assert again["cache"]["reused"] is True
    for name in legs:
        assert again[name]["packed"].tobytes() == first[name]["packed"].tobytes()
        assert again["legs"][name] == first["legs"][name]
    with pytest.raises(SystemExit, match="another key"):
        tr.gather_legs_cached(world.index, legs, world.pass_reco, "digest-b", cache)
    other = {"pdata": legs["pdata"], "prior": np.arange(100, 181)}
    with pytest.raises(SystemExit, match="another key"):
        tr.gather_legs_cached(world.index, other, world.pass_reco, "digest-a", cache)


def test_crosscheck_against_a_historical_layout_cache(world, tmp_path):
    """A cache in `prematerialize_theirs`' layout: unsorted halves, pdata = rows_a[s1_a]."""
    rng = np.random.default_rng(11)
    perm = rng.permutation(world.n_inv)
    rows_a, rows_b = perm[:150], perm[150:320]            # historical order: NOT sorted
    s1_a = world.pass_reco[rows_a] & (rng.random(150) < 0.9)
    pd = mtz.materialize(world.files, world.row_index, world.origin, rows_a[s1_a], world.pass_reco)
    pr = mtz.materialize(world.files, world.row_index, world.origin, rows_b, world.pass_reco)
    cache = tmp_path / "theirs-synth.npz"
    np.savez(cache, pdata_packed=pd["packed"], pdata_globals=pd["globals"],
             prior_packed=pr["packed"], prior_globals=pr["globals"], rows_a=rows_a,
             rows_b=rows_b, s1_a=s1_a, key=np.array("k"))
    n = world.n_inv
    report = tr.crosscheck(cache, world.inventory, world.join, inventory_rows=n,
                           chunk_rows=17)
    assert report["all_bytes_equal"] is True
    assert report["legs"]["pdata"]["rows_compared"] == int(s1_a.sum())
    assert report["legs"]["prior"]["rows_compared"] == 170
    sub = tr.crosscheck(cache, world.inventory, world.join, max_rows=33, inventory_rows=n)
    assert sub["all_bytes_equal"] and sub["legs"]["prior"]["rows_compared"] == 33
    # the comparison has power: one flipped value in the cache is detected
    bad = dict(np.load(cache))
    bad["prior_packed"] = bad["prior_packed"].copy()
    bad["prior_packed"][3, 0, 0] += 1.0
    np.savez(cache, **bad)
    report = tr.crosscheck(cache, world.inventory, world.join, inventory_rows=n)
    assert report["all_bytes_equal"] is False
    assert report["legs"]["prior"]["packed_rows_differing"] == 1


# ------------------------------------------------------------------------------------------- #
# hybrid_driver
# ------------------------------------------------------------------------------------------- #
def _reference() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(0)
    return {"a.weight": rng.normal(size=(4, 3)).astype(np.float32),
            "a.bias": np.zeros(4, np.float32),                       # constant fill
            "b.alpha": np.full(1, 0.5, np.float32),                   # constant fill
            "c.weight": rng.normal(size=(2, 2)).astype(np.float32)}


def test_compare_init_pretrained_and_scratch_verdicts():
    ref = _reference()
    loaded = [(k, v.copy()) for k, v in ref.items()]
    ok = hd.compare_init(loaded, ref, "pretrained")
    assert ok["ok"] and ok["equal"] == 4 and ok["compared"] == 4
    assert hd.compare_init(loaded, ref, "scratch")["ok"] is False
    rng = np.random.default_rng(9)
    scratch = [(k, (rng.normal(size=v.shape).astype(np.float32) if k.endswith("weight") else v))
               for k, v in ref.items()]                 # biases/alpha at their constant init
    s = hd.compare_init(scratch, ref, "scratch")
    assert s["ok"] and s["equal"] == 2 and s["differ"] == 2
    assert set(s["equal_names"]) == {"a.bias", "b.alpha"} and not s["equal_nonconstant_names"]
    assert hd.compare_init(scratch, ref, "pretrained")["ok"] is False
    # a random-init tensor that equals the export is NOT scratch
    leaked = [(k, ref[k] if k == "c.weight" else v) for k, v in scratch]
    bad = hd.compare_init(leaked, ref, "scratch")
    assert not bad["ok"] and bad["equal_nonconstant_names"] == ["c.weight"]
    # coverage: a missing or extra tensor fails both verdicts
    for named in (loaded[:-1], loaded + [("extra", np.ones(1, np.float32))]):
        assert not hd.compare_init(named, ref, "pretrained")["ok"]
    # digests are of the bytes the model holds
    t = ok["tensors"]["a.weight"]
    assert t["model_sha256"] == hashlib.sha256(ref["a.weight"].tobytes()).hexdigest()


def test_init_verifier_refuses_wrong_reference(tmp_path):
    f = tmp_path / "state.npz"
    np.savez(f, **_reference())
    with pytest.raises(SystemExit, match="sha256"):
        hd.InitVerifier(f, "0" * 64, "scratch", lambda m: [])
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    v = hd.InitVerifier(f, sha, "pretrained", lambda m: [(k, SimpleNamespace(numpy=lambda a=a: a))
                                                         for k, a in _reference().items()])
    assert v.check(None)["ok"]


def test_substitute_theirs_checks_rows_and_touches_step1_only():
    rows_p, rows_m = np.array([2, 5, 9]), np.array([1, 2, 3, 7])
    gen = np.ones((4, 12, 8), np.float32)
    inputs = SimpleNamespace(
        pdata={"rows": rows_p, "reco": np.zeros((3, 12, 6)), "reco_evt": np.zeros((3, 9))},
        mc={"rows": rows_m, "reco": np.zeros((4, 12, 6)), "reco_evt": np.zeros((4, 9)),
            "gen": gen, "gen_evt": np.zeros((4, 3))}, meta={"coord_reco": (1, 2)})
    theirs = {"pdata": {"packed": np.full((3, 33, 10), 1, np.float32),
                        "globals": np.full((3, 16), 2, np.float32)},
              "prior": {"packed": np.full((4, 33, 10), 3, np.float32),
                        "globals": np.full((4, 16), 4, np.float32)},
              "legs": {"pdata": {"rows_sha256": tr.rows_digest(rows_p)},
                       "prior": {"rows_sha256": tr.rows_digest(rows_m)}}}
    rec = hd.substitute_theirs(inputs, theirs)
    assert inputs.pdata["reco"].shape == (3, 33, 10) and inputs.mc["reco_evt"].shape == (4, 16)
    assert inputs.mc["gen"] is gen and rec["mc"]["rows"] == 4
    theirs["legs"]["prior"]["rows_sha256"] = tr.rows_digest(rows_m + 1)
    inputs.mc["rows"] = rows_m
    with pytest.raises(SystemExit, match="other rows"):
        hd.substitute_theirs(inputs, theirs)


def _c() -> RunConfig:
    return RunConfig.from_json(C_CONFIG.read_text())


def test_check_hybrid_config_refuses_non_hybrids():
    with pytest.raises(SystemExit, match="PET2-small"):
        hd.check_hybrid_config(_c(), b2_arms.get("pdg_onehot"), PINNED)


def test_recipe_audit_flags_a_declaration_that_is_not_the_config():
    import run_unfold as ru
    c = _c()
    declared = {"family": "adam", "base_learning_rate": 4e-4, "schedule": "constant",
                "clipping": "none", "max_norm": None, "weight_decay": 0.0, "beta_1": 0.9,
                "beta_2": 0.999, "epsilon": 1e-7, "total_steps": 10}
    executed = {"class": "Adam", "is_horovod_wrapped": False, "iterations": 0,
                "base_learning_rate": 4e-4, "schedule_class": None, "warmup_steps": None,
                "max_steps": None, "keras_weight_decay": None, "torch_weight_decay": None,
                "global_clipnorm": None, "clipnorm": None, "torch_grad_clip": None,
                "beta_1": 0.9, "beta_2": 0.999, "epsilon": 1e-7}
    fit = {"step": 1, "iteration": 0, "declared_optimizer": declared,
           "executed_optimizer": executed, "batch_size": 512, "updates_per_epoch": 3,
           "recorder": {"epochs": [{"recipe_violations": []}],
                        "restore_executed_as_declared": True}}
    assert hd.recipe_audit(ru, c, [fit])["all_as_declared"] is True
    wrong = json.loads(json.dumps(fit))
    wrong["declared_optimizer"]["weight_decay"] = 0.01
    wrong["executed_optimizer"]["keras_weight_decay"] = 0.01
    audit = hd.recipe_audit(ru, c, [wrong])
    assert not audit["all_as_declared"] and "weight_decay" in audit["fits"][0]["problems"][0]


# ------------------------------------------------------------------------------------------- #
# make_pet2_configs (historical recipe constants need TensorFlow's import)
# ------------------------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pet2():
    pytest.importorskip("tensorflow")
    import make_pet2_configs as mpc
    return mpc, mpc.pet2_recipe_constants()


def test_p2_configs_differ_only_in_step1_init(pet2):
    mpc, k = pet2
    base = _c()
    pre = mpc.pet2_config(base, "pretrained", k, iterations=6)
    scr = mpc.pet2_config(base, "scratch", k, iterations=6)
    dp, ds = pre.to_dict(), scr.to_dict()
    assert dp["step1"]["init"] != ds["step1"]["init"]
    dp["step1"].pop("init"), ds["step1"].pop("init")
    assert dp == ds
    assert pre.step1.init.pretrained_state_sha256 == PINNED
    assert scr.step1.init.policy == "scratch" and scr.step1.init.pretrained_state is None


def test_p2_declared_recipe_split_and_step2(pet2):
    mpc, k = pet2
    base = _c()
    for variant in ("pretrained", "scratch"):
        c = mpc.pet2_config(base, variant, k, iterations=4)
        s1 = c.step1
        assert (s1.optimizer.family, s1.optimizer.learning_rate, s1.optimizer.weight_decay,
                s1.optimizer.epsilon) == ("torch_adamw", 1e-4, 0.01, 1e-8)
        assert (s1.clipping.kind, s1.clipping.max_norm) == ("global_norm_torch", 1.0)
        assert (s1.schedule.kind, s1.schedule.warmup_fraction) == ("warmup_cosine", 0.004)
        assert s1.batch_size == 2048 and s1.stopping.max_epochs == base.step1.stopping.max_epochs
        assert s1.iteration_lr.kind == "constant"
        assert s1.validation == base.step1.validation and s1.seed == base.step1.seed
        assert c.step2 == base.step2
        assert (c.arm, c.model_step1.kind, c.feature_arm, c.iterations) == \
            ("theirs", "theirs_pet2_small", "pdg_onehot", 4)
        assert (c.events, c.endpoint, c.model_step2) == (base.events, base.endpoint,
                                                          base.model_step2)
        info = hd.check_hybrid_config(c, b2_arms.get(c.feature_arm), PINNED)
        assert info["variant"] == variant
    smoke = mpc.pet2_config(base, "scratch", k, iterations=2, step1_epochs=2, step2_epochs=2,
                            step1_iteration_lr="anneal")
    assert smoke.step1.stopping.max_epochs == smoke.step2.stopping.max_epochs == 2
    assert smoke.step1.iteration_lr == base.step1.iteration_lr
    with pytest.raises(SystemExit, match="step-1"):
        hd.check_hybrid_config(smoke.replace(feature_arm="reco_summaries_pdg_onehot"),
                               b2_arms.get("reco_summaries_pdg_onehot"), PINNED)
    with pytest.raises(SystemExit, match="pinned"):
        hd.check_hybrid_config(mpc.pet2_config(base, "pretrained", k, iterations=2),
                               b2_arms.get("pdg_onehot"), "f" * 64)


def test_build_writes_seeded_configs_and_refuses_undrawn(pet2, tmp_path):
    mpc, _ = pet2
    import freeze_runs
    rows = mpc.build("t", ["P2pre", "P2scr"], [("F", 0, "dev"), ("T", 1, "D4c_p_up")], 3,
                     tmp_path, tmp_path / "m.tsv", step1_epochs=2)
    assert len(rows) == 4
    for row in rows:
        name, rel, h, sel, dist, ref, extra, runner = row.split("\t")
        cfg = RunConfig.from_json((tmp_path / "t" / f"{name}.json").read_text())
        assert cfg.content_hash() == h and extra == "--step2-miss-mode efficiency_corrected"
        pool, r = sel.split(":")
        seed = freeze_runs.seed_for(pool, int(r))
        assert {cfg.step1.seed, cfg.step2.seed, cfg.step1.validation.seed,
                cfg.step2.validation.seed} == {seed}
        assert runner == mpc.RUNNER
    with pytest.raises(SystemExit, match="not drawn"):
        mpc.build("t", ["P2pre"], [("F", 12, "dev")], 3, tmp_path, tmp_path / "m.tsv")
    with pytest.raises(SystemExit, match="not drawn"):
        mpc.build("t", ["P2pre"], [("R", 0, "dev")], 3, tmp_path, tmp_path / "m.tsv")


# ------------------------------------------------------------------------------------------- #
# run_pet2_replicate refusals
# ------------------------------------------------------------------------------------------- #
def test_selection_refusals():
    import run_pet2_replicate as rpr
    assert rpr.refuse_selection("F", 11, rpr.ri.FAMILY, rpr.ri.N_PRIOR, rpr.ri.N_PSEUDO)
    assert rpr.refuse_selection("T", 1, rpr.ri.FAMILY, rpr.ri.N_PRIOR, rpr.ri.N_PSEUDO)
    with pytest.raises(scope.ScopeViolation, match="reserve"):
        rpr.refuse_selection("R", 0, rpr.ri.FAMILY, rpr.ri.N_PRIOR, rpr.ri.N_PSEUDO)
    for pool, r in (("F", 12), ("S", 1), ("P", 3), ("T", 2)):
        with pytest.raises(scope.ScopeViolation, match="not drawn"):
            rpr.refuse_selection(pool, r, rpr.ri.FAMILY, rpr.ri.N_PRIOR, rpr.ri.N_PSEUDO)
    with pytest.raises(SystemExit, match="family"):
        rpr.refuse_selection("F", 0, "bank-v1", rpr.ri.N_PRIOR, rpr.ri.N_PSEUDO)
    with pytest.raises(SystemExit, match="family"):
        rpr.refuse_selection("F", 0, rpr.ri.FAMILY, 1000, rpr.ri.N_PSEUDO)


def test_preflight_refuses_r1_and_ours_configs(pet2, tmp_path, monkeypatch):
    import run_pet2_replicate as rpr
    mpc, k = pet2
    state = tmp_path / "state.npz"
    state.write_bytes(b"not the export")
    monkeypatch.setattr(rpr, "pinned_state_sha256", lambda: tr.sha256_file(state))
    cfg = mpc.pet2_config(_c(), "scratch", k, iterations=2)
    cfile = tmp_path / "c.json"
    cfile.write_text(cfg.to_json(indent=1))
    common = ["--config", str(cfile), "--config-hash", cfg.content_hash(), "--repo", "x",
              "--out", str(tmp_path / "out"), "--inputs-npz", str(tmp_path / "i.npz"),
              "--identity-sidecar", "s", "--populations", "p", "--pool", "F", "--replicate",
              "0", "--pools-npz", "q", "--manifest", "m", "--step2-miss-mode",
              "efficiency_corrected", "--pretrained-reference", str(state)]
    out, config, arm, dist, hybrid = rpr.preflight(rpr.parse_args(common))
    assert hybrid["variant"] == "scratch" and dist.name == "dev"
    with pytest.raises(SystemExit, match="reco-response"):
        rpr.preflight(rpr.parse_args(common + ["--distortion", "R1_x1.05+D1_p0.350"]))
    with pytest.raises(SystemExit, match="hash"):
        rpr.preflight(rpr.parse_args([x if x != cfg.content_hash() else "0" * 64
                                      for x in common]))
    ours = tmp_path / "ours.json"
    ours.write_text(_c().to_json(indent=1))
    swapped = [str(ours) if x == str(cfile) else (_c().content_hash()
                                                  if x == cfg.content_hash() else x)
               for x in common]
    with pytest.raises(SystemExit, match="PET2"):
        rpr.preflight(rpr.parse_args(swapped))
    with pytest.raises(SystemExit):     # the miss rule has no default
        rpr.parse_args([x for x in common if x not in ("--step2-miss-mode",
                                                       "efficiency_corrected")])


# ------------------------------------------------------------------------------------------- #
# Optional: the verifier on a real PET2-small (local copies of the export)
# ------------------------------------------------------------------------------------------- #
@pytest.mark.skipif(not os.environ.get("PFD_PRETRAINED_STATE"),
                    reason="set PFD_PRETRAINED_STATE / PFD_PRETRAINED_MANIFEST to local copies")
def test_verifier_on_real_pet2_small():
    pytest.importorskip("tensorflow")
    if str(COMP) not in sys.path:
        sys.path.append(str(COMP))
    import pet2_keras_port as port
    import theirs_omnifold_arm as toa
    state = Path(os.environ["PFD_PRETRAINED_STATE"])
    manifest = Path(os.environ["PFD_PRETRAINED_MANIFEST"])
    inv = lambda m: port.parameter_inventory(m.backbone)   # noqa: E731
    loaded = toa.TheirsCompleteArm(num_part=33, state_npz=state, manifest=manifest)
    scratch = toa.TheirsCompleteArm(num_part=33)
    pre = hd.InitVerifier(state, PINNED, "pretrained", inv).check(loaded)
    assert pre["ok"] and pre["equal"] == pre["compared"] == 176
    assert pre["parameters"] == 2_758_702
    s = hd.InitVerifier(state, PINNED, "scratch", inv).check(scratch)
    assert s["ok"] and s["compared"] == 176 and s["differ"] >= 171, s["equal_names"]
    assert not hd.InitVerifier(state, PINNED, "pretrained", inv).check(scratch)["ok"]
    assert not hd.InitVerifier(state, PINNED, "scratch", inv).check(loaded)["ok"]


# ------------------------------------------------------------------------------------------- #
# Optional: the whole hybrid loop on CPU with tiny synthetic inputs (real PET2-small at step 1,
# the vendored PET at step 2), both variants, and a stop/resume against a continuous run
# ------------------------------------------------------------------------------------------- #
def _tiny_inputs(rng: np.random.Generator, n_mc: int = 1500, n_pd: int = 900):
    def theirs_block(n: int, shift: float) -> tuple[np.ndarray, np.ndarray]:
        packed = np.zeros((n, 33, 10), np.float32)
        ntok = rng.integers(1, 20, n)
        real = np.arange(33)[None, :] < ntok[:, None]
        packed[..., 0:3] = rng.normal(size=(n, 33, 3)) + shift
        packed[..., 3] = np.abs(rng.normal(size=(n, 33))) + 0.5 + shift
        packed[..., 4] = rng.integers(0, 8, (n, 33))
        packed[..., 5:10] = rng.normal(size=(n, 33, 5)) * 0.1
        packed[~real] = 0.0
        return packed, rng.normal(size=(n, 16)).astype(np.float32) + shift

    gen = np.zeros((n_mc, 12, 8), np.float32)
    ntok = rng.integers(1, 12, n_mc)
    real = np.arange(12)[None, :] < ntok[:, None]
    gen[..., 0] = np.abs(rng.normal(size=(n_mc, 12))) + 0.1
    gen[..., 1:] = rng.normal(size=(n_mc, 12, 7))
    gen[~real] = 0.0
    reco_mc, evt_mc = theirs_block(n_mc, 0.0)
    reco_pd, evt_pd = theirs_block(n_pd, 0.2)
    pass_reco = rng.random(n_mc) < 0.7
    reco_mc[~pass_reco], evt_mc[~pass_reco] = 0.0, 0.0
    return SimpleNamespace(
        pdata={"reco": reco_pd, "reco_evt": evt_pd, "weight": np.ones(n_pd, np.float32),
               "rows": np.arange(n_pd)},
        mc={"reco": reco_mc, "reco_evt": evt_mc, "gen": gen,
            "gen_evt": rng.normal(size=(n_mc, 2)).astype(np.float32), "pass_reco": pass_reco,
            "pass_gen": rng.random(n_mc) < 0.9, "weight": np.ones(n_mc, np.float32),
            "weight_reco": np.ones(n_mc, np.float32), "rows": np.arange(n_mc)},
        meta={"coord_gen": (5, 6), "coord_reco": None})


@pytest.mark.skipif(not os.environ.get("PFD_PRETRAINED_STATE"),
                    reason="set PFD_PRETRAINED_STATE / PFD_PRETRAINED_MANIFEST to local copies")
@pytest.mark.parametrize("variant", ["pretrained", "scratch"])
def test_hybrid_loop_on_cpu_with_resume(pet2, tmp_path, variant, monkeypatch):
    import dataclasses
    import random
    tf = pytest.importorskip("tensorflow")
    repo = PET.parents[1]
    for p in (str(repo / "omnifold_nn"), str(COMP)):
        if p not in sys.path:
            sys.path.append(p)
    import omnifold.dataloader as odl
    import omnifold.net as onet
    import omnifold.omnifold as oof
    import recorder as rec
    import run_unfold as ru
    import torch_adamw
    import training_recipe
    import pet2_keras_port as port

    def set_seed(seed: int) -> None:     # tf_keras 2.16's version breaks on Python 3.12 (randint)
        random.seed(seed)
        np.random.seed(seed)
        tf.random.set_seed(seed)
    monkeypatch.setattr(tf.keras.utils, "set_random_seed", set_seed)
    rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                  if "_clip_gradients" in vars(k)))
    mpc, k = pet2
    state = Path(os.environ["PFD_PRETRAINED_STATE"])
    k = dict(k, state=str(state), manifest=os.environ["PFD_PRETRAINED_MANIFEST"])
    config = mpc.pet2_config(_c(), variant, k, iterations=2, step1_epochs=1, step2_epochs=1)
    small = lambda s, b: dataclasses.replace(s, batch_size=b, predict_batch_size=512)  # noqa
    config = config.replace(step1=small(config.step1, 256), step2=small(config.step2, 256))
    mods = {"net": onet}
    inv = lambda m: port.parameter_inventory(m.backbone)   # noqa: E731

    def run(out: Path, stop: int | None) -> tuple[bool, Any]:
        inputs = _tiny_inputs(np.random.default_rng(0))
        p, m = inputs.pdata, inputs.mc
        pdata = odl.DataLoader(reco=p["reco"], weight=p["weight"], normalize=True,
                               reco_evt=p["reco_evt"])
        mcb = odl.DataLoader(reco=m["reco"], gen=m["gen"], pass_reco=m["pass_reco"],
                             pass_gen=m["pass_gen"], weight=m["weight"],
                             weight_reco=m["weight_reco"], normalize=True,
                             normalization_factor=1e6, reco_evt=m["reco_evt"],
                             gen_evt=m["gen_evt"])
        factories, check = ru.model_factories(config, mods, inputs)
        Hybrid = hd.make_hybrid_multifold(oof.MultiFold, tf, np)
        u = Hybrid(config.name, config=config, factories=factories, data=pdata, mc=mcb,
                   out_dir=out, pretrained_check=check, training_recipe=training_recipe,
                   torch_adamw=torch_adamw, probe_rows=100, deadline_unix=None,
                   first_iteration_estimate_s=1.0, stop_after_iteration=stop,
                   step2_miss_mode="efficiency_corrected",
                   init_verifier=hd.InitVerifier(state, PINNED, variant, inv))
        return u.Unfold(), u

    done, u = run(tmp_path / "cont", None)
    assert done and len(u.init_records) == 1 and u.init_records[0]["ok"]
    assert u.init_records[0]["expect"] == variant and u.init_records[0]["compared"] == 176
    assert u.init_records[0]["optimizer_iterations"] == 0
    assert (u.init_records[0]["equal"] == 176) == (variant == "pretrained")
    audit = hd.recipe_audit(ru, config, u.fit_records)
    assert audit["all_as_declared"], audit
    s1 = [f for f in u.fit_records if f["step"] == 1]
    assert s1[0]["executed_optimizer"]["class"] == "ClippedTorchAdamW"
    assert s1[0]["step1_throughput"][0]["examples"] == s1[0]["train_rows"]
    assert (variant == "pretrained") == ("pretrained_at_first_step" in s1[0]["recorder"])
    res = [json.loads(x) for x in (tmp_path / "cont" / "resources.jsonl").read_text()
           .splitlines()]
    assert [(r["iteration"], r["step"]) for r in res] == [(0, 1), (0, 2), (1, 1), (1, 2)]
    # stop after iteration 0, resume: iteration 1 is byte-identical to the continuous run's
    done0, u0 = run(tmp_path / "split", 0)
    assert done0 is False
    done1, u1 = run(tmp_path / "split", None)
    assert done1 is True and len(u1.init_records) == 1      # no re-check of a restored model
    for name in ("iter00.npz", "iter01.npz"):
        with np.load(tmp_path / "cont" / "iterations" / name) as a, \
                np.load(tmp_path / "split" / "iterations" / name) as b:
            assert a["push"].tobytes() == b["push"].tobytes(), name
            assert a["pull"].tobytes() == b["pull"].tobytes(), name
