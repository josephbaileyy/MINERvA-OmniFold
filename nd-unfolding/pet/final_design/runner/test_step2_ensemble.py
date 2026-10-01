"""Tests of the step-2 ensemble (`step2_ensemble.py`, `recipe.StepRecipe.ensemble`); no training.

The driver logic runs on a fake B2 (`FakeB2`, the B2MultiFold contract the ensemble relies on:
per-step seeds from `step_recipe(stepn).seed`, one model per step in `step{1,2}_models`, the
engine's multi-model weight average, B2's persistence) with fake models and a fake
`tf.keras.utils.set_random_seed`; `test_parent_contract_*` pin that contract on the real
predecessor source, and the across-member average is compared with the real engine's
`MultiFold.reweight`. Config tests: the field round-trips, enters the hash only when != 1, and
leaves every committed config's content hash and bytes unchanged.
"""

from __future__ import annotations

import dataclasses
import inspect
import json
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PET = STUDY.parent
REPO = PET.parents[1]
CAMPAIGN = PET / "improvement_campaign"
for _p in reversed((HERE, STUDY / "dev", CAMPAIGN / "confirm", CAMPAIGN,
                    CAMPAIGN / "phase_b" / "pet")):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import b2_driver as b2d  # noqa: E402
import design_inputs as di  # noqa: E402
import freeze_runs as fr  # noqa: E402
import make_dev_configs as mdc  # noqa: E402
import run_unfold as ru  # noqa: E402
import step2_ensemble as s2e  # noqa: E402
from recipe import RecipeError, RunConfig  # noqa: E402

DEV1_CONFIG = STUDY / "configs" / "dev1" / "dev1-H1-T0-D1_p0.350.json"
CAP = 30.0


def with_ensemble(config: RunConfig, m: int) -> RunConfig:
    return config.replace(step2=dataclasses.replace(config.step2, ensemble=m))


def dev1() -> RunConfig:
    return RunConfig.from_json(DEV1_CONFIG.read_text())


# ------------------------------------------------------------------------------------------- #
# Config field
# ------------------------------------------------------------------------------------------- #
def test_field_round_trips_and_enters_the_hash_only_when_not_one():
    base = dev1()
    assert base.step2.ensemble == 1 and base.step1.ensemble == 1
    assert "ensemble" not in base.to_json()
    assert with_ensemble(base, 1).content_hash() == base.content_hash()
    x4 = with_ensemble(base, 4)
    d = json.loads(x4.to_json())
    assert d["step2"]["ensemble"] == 4 and "ensemble" not in d["step1"]
    assert x4.content_hash() != base.content_hash()
    back = RunConfig.from_json(x4.to_json(indent=1))
    assert back == x4 and back.content_hash() == x4.content_hash()
    # an explicit default in a file is the same config
    d1 = json.loads(base.to_json())
    d1["step2"]["ensemble"] = 1
    assert RunConfig.from_dict(d1).content_hash() == base.content_hash()


@pytest.mark.parametrize("bad", [0, -1, 2.0, True])
def test_field_validation_refuses_non_positive_and_non_integer(bad):
    with pytest.raises(RecipeError, match="ensemble"):
        with_ensemble(dev1(), bad).validate()


def test_step1_ensemble_is_refused():
    base = dev1()
    c = base.replace(step1=dataclasses.replace(base.step1, ensemble=2))
    with pytest.raises(RecipeError, match="step 2"):
        c.validate()


def test_reseed_and_bootstrap_members_keep_the_ensemble():
    x4 = with_ensemble(dev1(), 4)
    assert fr.reseed(x4, 11, "n", "note").step2.ensemble == 4
    member, rec = di.bootstrap_config(x4, 2)
    assert member.step2.ensemble == 4 and rec["member_config_hash"] == member.content_hash()
    # the member's step-2 seed (the ensemble's s) differs, so every s_m differs
    a = s2e.member_seeds(x4.step2.seed, 4, ru.derive_seed)
    b = s2e.member_seeds(member.step2.seed, 4, ru.derive_seed)
    assert not set(a) & set(b)


def _manifest_hashes() -> dict[str, set[str]]:
    """config file name -> config_hash recorded in the committed run manifests."""
    out: dict[str, set[str]] = {}
    for tsv in sorted((STUDY / "runs").glob("*.tsv")):
        for line in tsv.read_text().splitlines():
            f = line.split("\t")
            if line.startswith("#") or len(f) < 3:
                continue
            if f[1].endswith(".json") and re.fullmatch(r"[0-9a-f]{64}", f[2]):
                out.setdefault(Path(f[1]).name, set()).add(f[2])
    return out


def test_existing_config_hashes_and_bytes_are_unchanged():
    """Every committed study config predates the field: it re-serializes byte for byte and its
    content hash equals the hash its run manifest recorded when it was generated."""
    files = sorted((STUDY / "configs").rglob("*.json"))
    assert len(files) >= 500
    recorded = _manifest_hashes()
    assert len(recorded) >= 500
    checked = 0
    for path in files:
        text = path.read_text()
        assert "ensemble" not in text, path
        config = RunConfig.from_json(text)
        assert config.step2.ensemble == 1
        assert text in (config.to_json(indent=1) + "\n", config.to_json(indent=1)), path
        if path.name in recorded:
            assert recorded[path.name] == {config.content_hash()}, path
            checked += 1
    assert checked >= 500
    # spot values, typed from the committed manifests (runs/dev3N.tsv)
    for rel, want in (("dev3N/dev3N-H2S1T24-F0.json",
                       "989969ac0b47cbfebea276e1a3386f6547bc45d50f3f2cb6d6da74855de1ba6e"),
                      ("dev3N/dev3N-L128S1T24-F0.json",
                       "390e4b7236aa7789fc203ec004c6357658c0ed71627b1a070eacc10919803b5e")):
        assert RunConfig.from_json((STUDY / "configs" / rel).read_text()).content_hash() == want


def test_predecessor_base_config_hash_is_unchanged():
    _, path, _sha = mdc.BASE
    assert mdc.base_config().to_json(indent=1) + "\n" == path.read_text() or \
        mdc.base_config().to_json(indent=1) == path.read_text()


def test_prepared_candidates_are_defined_but_not_in_the_table():
    assert "H2S1X4" not in mdc.CANDIDATES and "L128S1X4" not in mdc.CANDIDATES
    src = inspect.getsource(mdc)
    assert '# "H2S1X4"' in src and '# "L128S1X4"' in src
    base = mdc.base_config()
    for name in ("H2S1", "L128S1"):
        ref = mdc.CANDIDATES[name][1](base)
        x4 = mdc._ensemble2(4)(ref)
        assert x4.step2.ensemble == 4
        assert x4.replace(step2=dataclasses.replace(x4.step2, ensemble=1)) == ref
        assert RunConfig.from_json(x4.to_json()).content_hash() == x4.content_hash()
        assert x4.content_hash() != ref.content_hash()


# ------------------------------------------------------------------------------------------- #
# Seeds and the average
# ------------------------------------------------------------------------------------------- #
def test_member_seed_rule():
    s = 123456
    seeds = s2e.member_seeds(s, 4, ru.derive_seed)
    assert seeds[0] == s
    assert seeds[1:] == [ru.derive_seed(s, "step2_ensemble", m) for m in (1, 2, 3)]
    assert s2e.member_seeds(s, 4, ru.derive_seed) == seeds          # deterministic
    assert s2e.member_seeds(s, 2, ru.derive_seed) == seeds[:2]      # prefix-stable in M
    assert len(set(seeds)) == 4
    with pytest.raises(SystemExit, match="collide"):
        s2e.member_seeds(s, 3, lambda *parts: s)


def test_average_is_the_mean_weight_and_m1_is_the_identity():
    rng = np.random.default_rng(3)
    logits = rng.normal(0, 1.5, (4, 1000))
    w = np.exp(np.clip(logits, -CAP, CAP))
    one = s2e.average_member_weights(np, [w[0]])
    assert one.dtype == np.float64 and one.tobytes() == w[0].tobytes()
    avg = s2e.average_member_weights(np, list(w))
    np.testing.assert_allclose(avg, w.mean(axis=0), rtol=1e-14)
    # weight space, not logit space: mean exp >= exp mean, strictly here
    assert np.all(avg >= np.exp(logits.mean(axis=0)) * (1 - 1e-12))
    assert np.mean(avg - np.exp(logits.mean(axis=0))) > 0.1
    with pytest.raises(ValueError):
        s2e.average_member_weights(np, [])


class _Predictor:
    def __init__(self, logit: np.ndarray) -> None:
        self.logit = logit

    def predict(self, events, batch_size=None, verbose=0):  # noqa: D102
        return self.logit[:, None]


def test_average_matches_the_engine_multi_model_reweight():
    """The engine's own `MultiFold.reweight` over M models == the ensemble's per-member engine
    weights averaged by `average_member_weights`, bit for bit (and M = 1 is the engine's)."""
    if str(REPO / "omnifold_nn") not in sys.path:
        sys.path.insert(0, str(REPO / "omnifold_nn"))
    try:
        import omnifold.omnifold as engine
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"engine not importable here: {exc}")
    rng = np.random.default_rng(5)
    logits = rng.normal(0, 2, (3, 500))
    logits[0, :3] = [40.0, -40.0, 30.0]                   # the cap is the engine's
    models = [_Predictor(x) for x in logits]
    events = np.zeros((500, 2))

    def engine_reweight(ms):
        fake = SimpleNamespace(BATCH_SIZE=64, n_ensemble=1, step1_models=[], step2_models=ms,
                               model1=object(), verbose=False, log_string=lambda s: None)
        return engine.MultiFold.reweight(fake, events, object(), batch_size=64)

    per_member = [engine_reweight([m]) for m in models]
    assert engine_reweight(models).tobytes() == \
        s2e.average_member_weights(np, per_member).tobytes()
    assert engine_reweight(models[:1]).tobytes() == \
        s2e.average_member_weights(np, per_member[:1]).tobytes()
    assert per_member[0][0] == np.exp(CAP) and per_member[0][1] == np.exp(-CAP)


def test_spread_record():
    w = [np.array([1.0, 2.0, 3.0]), np.array([1.0, 4.0, 3.0])]
    rec = s2e.spread_record(np, w, np.array([True, True, False]))
    assert rec["rows"] == 2 and rec["member_mean_weight"] == [1.5, 2.5]
    np.testing.assert_allclose(rec["relative_sd_mean"], (0 + np.sqrt(2) / 3) / 2)
    with pytest.raises(ValueError):
        s2e.spread_record(np, w[:1], np.ones(3, bool))


# ------------------------------------------------------------------------------------------- #
# A fake B2 (the contract) and fake models
# ------------------------------------------------------------------------------------------- #
class FakeTF:
    """`tf.keras.utils.set_random_seed`: resets the one global generator the fake models use."""

    def __init__(self) -> None:
        self.log: list[int] = []
        self.rng = np.random.default_rng(0)
        self.keras = SimpleNamespace(utils=SimpleNamespace(set_random_seed=self.set_random_seed))

    def set_random_seed(self, seed: int) -> None:
        self.log.append(int(seed))
        self.rng = np.random.default_rng(int(seed))


class FakeModel:
    """Weights from the global generator at construction; a fit moves them by a data term plus
    noise from the global generator (so a fit depends on its seeds, inputs and warm start)."""

    def __init__(self, tf: FakeTF, d: int) -> None:
        self.tf = tf
        self.w = tf.rng.normal(0, 0.3, d)

    def fit(self, x, labels, weights) -> None:
        g = (x * ((labels - 0.5) * weights)[:, None]).mean(axis=0)
        self.w = self.w + 0.5 * g + 0.05 * self.tf.rng.normal(size=self.w.shape)

    def predict(self, x, batch_size=None, verbose=0):
        return (x @ self.w)[:, None]

    def get_weights(self):
        return [self.w.copy(), np.arange(3, dtype=np.float32)]

    def set_weights(self, ws) -> None:
        self.w = np.asarray(ws[0]).copy()


def make_fake_b2(tf: FakeTF, ru_: SimpleNamespace) -> type:
    """What the ensemble relies on in B2MultiFold / RecipeMultiFold / the engine (pinned on the
    real source by `test_parent_contract_*`)."""

    class FakeB2:
        def __init__(self, config, out_dir, factories, mc, niter) -> None:
            self.config, self.factories, self.mc, self.niter = config, factories, mc, niter
            self.out_dir = Path(out_dir)
            self.model1, self.model2 = object(), object()
            self.state_dir = self.out_dir / "iterations"
            self.state_dir.mkdir(parents=True, exist_ok=True)
            (self.out_dir / "weights").mkdir(exist_ok=True)
            self.fits_sink = self.out_dir / "fits.jsonl"
            self.fit_records: list = []
            self._fits_written = 0
            self.recorded_contexts: list = []

        def step_recipe(self, stepn):
            return self.config.step1 if stepn == 1 else self.config.step2

        def seed_step(self, stepn, iteration):
            tf.keras.utils.set_random_seed(
                ru_.derive_seed(self.step_recipe(stepn).seed, stepn, iteration, "pre_step"))

        def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=None, cached=False):
            step = self.step_recipe(stepn)
            models = self.step1_models if stepn == 1 else self.step2_models
            fresh = iteration == 0 or not models
            if fresh:
                tf.keras.utils.set_random_seed(ru_.derive_seed(step.seed, stepn, "init", 0))
                model_e = self.factories[stepn]()
                models[:] = [model_e]
            else:
                model_e = models[0]
            context = {"iteration": int(iteration), "step": int(stepn)}
            recorder = ru_.rec.make_epoch_recorder(tf, np, context=context, sink=None)
            self.recorded_contexts.append(recorder["context"])
            tf.keras.utils.set_random_seed(ru_.derive_seed(step.seed, stepn, iteration, "fit"))
            t0 = time.perf_counter()
            model_e.fit(np.concatenate([self.mc.gen, self.mc.gen]), labels, weights)
            seconds = time.perf_counter() - t0
            path = self.out_dir / "weights" / f"iter{iteration}_step{stepn}.weights.h5"
            path.write_bytes(model_e.w.tobytes())
            self.fit_records.append({**context, "fresh_model": fresh, "fit_seconds": seconds,
                                     "recorder": recorder, "weights_path": str(path)})

        def reweight(self, events, model, batch_size=None):      # the engine's accumulation
            models = self.step1_models if model is self.model1 else self.step2_models
            avg = np.zeros(len(events))
            for m in models:
                logit = np.asarray(m.predict(events))[:, 0]
                if not np.all(np.isfinite(logit)):
                    raise ValueError("non-finite logits")
                avg += np.exp(np.clip(logit, -CAP, CAP)) / len(models)
            return avg

        def RunStep1(self, i):
            n = len(self.mc.weight)
            self.RunModel(np.concatenate([np.zeros(n), np.ones(n)]),
                          np.concatenate([self.weights_push * self.mc.weight,
                                          self.mc.weight * 1.1]), i, self.model1, stepn=1)
            new = np.ones_like(self.weights_pull)
            new[self.mc.pass_reco] = self.reweight(self.mc.gen, self.model1)[self.mc.pass_reco]
            self.weights_pull = self.weights_push * new

        def RunStep2(self, i):
            n, pg = len(self.mc.weight), self.mc.pass_gen
            self.RunModel(np.concatenate([np.zeros(n), np.ones(n)]),
                          np.concatenate([self.mc.weight * pg,
                                          self.mc.weight * self.weights_pull * pg]),
                          i, self.model2, stepn=2)
            new = np.ones_like(self.weights_push)
            new[pg] = self.reweight(self.mc.gen, self.model2)[pg]
            self.weights_push = new

        def _save_iteration(self, i, seconds):
            np.savez(self.state_dir / f"iter{i:02d}.npz", pull=self.weights_pull,
                     push=self.weights_push)
            blobs = {}
            for stepn, models in ((1, self.step1_models), (2, self.step2_models)):
                for j, w in enumerate(models[0].get_weights()):
                    blobs[f"s{stepn}_{j:04d}"] = w
            np.savez(self.state_dir / f"models{i:02d}.npz", **blobs)
            with self.fits_sink.open("a") as handle:
                for record in self.fit_records[self._fits_written:]:
                    handle.write(json.dumps(record, default=repr) + "\n")
            self._fits_written = len(self.fit_records)
            self.iteration_records[-1]["seconds"] = seconds
            (self.out_dir / "state.json").write_text(json.dumps({
                "completed_iteration": i, "config_hash": self.config.content_hash(),
                "iteration_records": self.iteration_records}))

        def _restore(self):
            state_path = self.out_dir / "state.json"
            if not state_path.exists():
                return 0
            state = json.loads(state_path.read_text())
            assert state["config_hash"] == self.config.content_hash()
            k = int(state["completed_iteration"])
            with np.load(self.state_dir / f"iter{k:02d}.npz") as blob:
                self.weights_push = np.asarray(blob["push"], np.float32)
                self.weights_pull = np.asarray(blob["pull"], np.float32)
            with np.load(self.state_dir / f"models{k:02d}.npz") as blob:
                for stepn, models in ((1, self.step1_models), (2, self.step2_models)):
                    step = self.step_recipe(stepn)
                    tf.keras.utils.set_random_seed(ru_.derive_seed(step.seed, stepn, "init", 0))
                    model = self.factories[stepn]()
                    names = sorted(n for n in blob.files if n.startswith(f"s{stepn}_"))
                    model.set_weights([blob[n] for n in names])
                    models[:] = [model]
            self.iteration_records = list(state["iteration_records"])
            self.fit_records = [json.loads(x) for x in self.fits_sink.read_text().splitlines()]
            self._fits_written = len(self.fit_records)
            return k + 1

        def Unfold(self, stop_after=None):
            self.step1_models, self.step2_models = [], []
            n = len(self.mc.weight)
            self.weights_pull = np.ones(n, np.float32)
            self.weights_push = np.ones(n, np.float32)
            self.iteration_records = []
            start = self._restore()
            for i in range(start, self.niter):
                self.seed_step(1, i)
                self.RunStep1(i)
                self.seed_step(2, i)
                self.RunStep2(i)
                self.iteration_records.append({"iteration": i})
                self._save_iteration(i, 0.0)
                if stop_after is not None and i >= stop_after:
                    return False
            return True

    return FakeB2


@pytest.fixture
def world():
    tf = FakeTF()
    original = lambda tf_, np_, *, context, sink: {"context": context}  # noqa: E731
    ru_ = SimpleNamespace(derive_seed=ru.derive_seed,
                          rec=SimpleNamespace(make_epoch_recorder=original))
    rng = np.random.default_rng(11)
    n, d = 400, 5
    mc = SimpleNamespace(gen=rng.normal(size=(n, d)), weight=rng.uniform(0.5, 1.5, n),
                         pass_gen=rng.random(n) < 0.8, pass_reco=rng.random(n) < 0.6)
    factories = {1: lambda: FakeModel(tf, d), 2: lambda: FakeModel(tf, d)}
    return SimpleNamespace(tf=tf, ru=ru_, mc=mc, factories=factories, original=original,
                           B2=make_fake_b2(tf, ru_))


def run(world, config, out, niter=3, stop_after=None):
    cls = s2e.driver_class(world.B2, config, world.tf, np, world.ru)
    u = cls(config, out, world.factories, world.mc, niter)
    complete = u.Unfold(stop_after=stop_after)
    return u, complete


def member_weights(u, events):
    return [np.exp(np.clip(m.predict(events)[:, 0], -CAP, CAP)) for m in u.step2_models]


# ------------------------------------------------------------------------------------------- #
# The driver
# ------------------------------------------------------------------------------------------- #
def test_m1_runs_the_predecessor_class_itself(world, tmp_path):
    base = dev1()
    assert s2e.driver_class(world.B2, base, world.tf, np, world.ru) is world.B2
    B2 = b2d.make_b2_multifold(type("MultiFold", (), {}), None, np)
    assert s2e.driver_class(B2, base, None, np, ru) is B2
    assert s2e.driver_class(B2, with_ensemble(base, 2), None, np, ru) is not B2
    # and the M = 1 run through driver_class is the fake B2's own run, bit for bit
    a, _ = run(world, base, tmp_path / "a")
    b = world.B2(base, tmp_path / "b", world.factories, world.mc, 3)
    b.Unfold()
    assert a.weights_push.tobytes() == b.weights_push.tobytes()


def test_ensemble_push_is_the_member_average_with_the_declared_seeds(world, tmp_path):
    config = with_ensemble(dev1(), 3)
    seeds = s2e.member_seeds(config.step2.seed, 3, ru.derive_seed)
    u, complete = run(world, config, tmp_path / "x3")
    assert complete and len(u.step2_models) == 3 and len(u.step1_models) == 1
    assert len({id(m) for m in u.step2_models}) == 3
    # the push = the mean of the final members' engine weights, on truth-passing rows
    pg = world.mc.pass_gen
    want = np.ones(len(pg), np.float32)
    want[pg] = s2e.average_member_weights(np, member_weights(u, world.mc.gen))[pg]
    assert u.weights_push.tobytes() == want.tobytes()
    # per-member fit records: member, seed, fit seconds, own checkpoint; warm start per member
    s2 = [r for r in u.fit_records if r["step"] == 2]
    assert [(r["iteration"], r["step2_ensemble"]["member"]) for r in s2] == \
        [(i, m) for i in range(3) for m in range(3)]
    assert all(r["step2_ensemble"]["step_seed"] == seeds[r["step2_ensemble"]["member"]]
               and r["step2_ensemble"]["members"] == 3 and r["fit_seconds"] >= 0 for r in s2)
    assert [r["fresh_model"] for r in s2] == [True] * 3 + [False] * 6
    for r in s2:
        p = Path(r["weights_path"])
        assert p.name == f"iter{r['iteration']}_step2_member{r['step2_ensemble']['member']:02d}" \
                         ".weights.h5" and p.exists()
    assert not list((tmp_path / "x3" / "weights").glob("iter*_step2.weights.h5"))
    # every member seed reached the fits by the predecessor's rules
    for i in range(3):
        for m, s in enumerate(seeds):
            assert ru.derive_seed(s, 2, i, "fit") in world.tf.log
            assert ru.derive_seed(s, 2, i, "pre_step") in world.tf.log
        assert ru.derive_seed(config.step1.seed, 1, i, "fit") in world.tf.log
    for s in seeds:
        assert ru.derive_seed(s, 2, "init", 0) in world.tf.log
    # epoch contexts tagged per member (step 2 only); the recorder patch is undone
    ctx2 = [c for c in u.recorded_contexts if c["step"] == 2]
    assert [c["step2_ensemble_member"] for c in ctx2] == [0, 1, 2] * 3
    assert all("step2_ensemble_member" not in c for c in u.recorded_contexts if c["step"] == 1)
    assert world.ru.rec.make_epoch_recorder is world.original
    # iteration records: seeds, per-member timing, spread
    for i, it in enumerate(u.iteration_records):
        e = it["step2_ensemble"]
        assert e["iteration"] == i and e["member_seeds"] == seeds
        assert len(e["fit_seconds"]) == len(e["run_model_seconds"]) == \
            len(e["predict_seconds"]) == 3
        assert e["spread_on_pass_gen"]["rows"] == int(pg.sum())
        assert e["spread_on_pass_gen"]["relative_sd_mean"] > 0


def test_member0_first_fit_is_the_single_fit(world, tmp_path):
    base = dev1()
    one, _ = run(world, base, tmp_path / "m1", niter=1)
    ens, _ = run(world, with_ensemble(base, 3), tmp_path / "m3", niter=1)
    assert ens.step2_models[0].w.tobytes() == one.step2_models[0].w.tobytes()
    assert ens.step1_models[0].w.tobytes() == one.step1_models[0].w.tobytes()
    assert ens.step2_models[1].w.tobytes() != one.step2_models[0].w.tobytes()


def test_members_do_not_depend_on_each_other(world, tmp_path):
    """Member m's first fit is the same in an M = 2 and an M = 4 ensemble (it is reseeded)."""
    base = dev1()
    e2, _ = run(world, with_ensemble(base, 2), tmp_path / "e2", niter=1)
    e4, _ = run(world, with_ensemble(base, 4), tmp_path / "e4", niter=1)
    for m in range(2):
        assert e2.step2_models[m].w.tobytes() == e4.step2_models[m].w.tobytes()


def test_resume_is_bit_identical_and_refuses_missing_members(world, tmp_path):
    config = with_ensemble(dev1(), 3)
    cont, _ = run(world, config, tmp_path / "cont", niter=3)
    part, complete = run(world, config, tmp_path / "res", niter=3, stop_after=0)
    assert not complete and (tmp_path / "res" / "iterations" / "s2members00.npz").exists()
    resumed, complete = run(world, config, tmp_path / "res", niter=3)
    assert complete
    assert resumed.weights_push.tobytes() == cont.weights_push.tobytes()
    for a, b in zip(resumed.step2_models, cont.step2_models):
        assert a.w.tobytes() == b.w.tobytes()
    assert [it["iteration"] for it in resumed.iteration_records] == [0, 1, 2]
    # a missing or incomplete members file refuses the resume
    part, _ = run(world, config, tmp_path / "miss", niter=3, stop_after=0)
    (tmp_path / "miss" / "iterations" / "s2members00.npz").unlink()
    with pytest.raises(SystemExit, match="missing"):
        run(world, config, tmp_path / "miss", niter=3)
    part, _ = run(world, config, tmp_path / "short", niter=3, stop_after=0)
    with np.load(tmp_path / "short" / "iterations" / "s2members00.npz") as blob:
        kept = {n: blob[n] for n in blob.files if n.startswith("m01_")}
    np.savez(tmp_path / "short" / "iterations" / "s2members00.npz", **kept)
    with pytest.raises(SystemExit, match="expected"):
        run(world, config, tmp_path / "short", niter=3)


def test_reweight_refuses_a_wrong_member_count(world, tmp_path):
    config = with_ensemble(dev1(), 3)
    u, _ = run(world, config, tmp_path / "w", niter=1)
    u.step2_models = u.step2_models[:2]
    with pytest.raises(SystemExit, match="expected 3"):
        u.reweight(world.mc.gen, u.model2)


# ------------------------------------------------------------------------------------------- #
# The real predecessor: the guard and the contract the ensemble relies on
# ------------------------------------------------------------------------------------------- #
class _Reached(Exception):
    pass


class _FakeEngine:
    def __init__(self, *a, **k):
        raise _Reached


def test_recipe_driver_refuses_an_ensemble_it_does_not_execute(tmp_path):
    Recipe = ru.make_recipe_multifold(_FakeEngine, None, np)
    kw = dict(factories={}, data=None, mc=None, out_dir=tmp_path / "o")
    with pytest.raises(SystemExit, match="step-2 ensemble"):
        Recipe("x", config=with_ensemble(dev1(), 4), **kw)
    with pytest.raises(_Reached):                                   # M = 1 passes the guard
        Recipe("x", config=dev1(), **kw)
    B2 = b2d.make_b2_multifold(_FakeEngine, None, np)
    with pytest.raises(SystemExit, match="B2MultiFold does not execute"):
        B2("x", config=with_ensemble(dev1(), 4), **kw)
    Ens = s2e.make_step2_ensemble(B2, None, np, ru)
    with pytest.raises(_Reached):                                   # the ensemble class passes
        Ens("x", config=with_ensemble(dev1(), 4), **kw)


def _source(cls, name):
    return inspect.getsource(vars(cls)[name])


def test_parent_contract_recipe_run_model():
    Recipe = ru.make_recipe_multifold(_FakeEngine, None, np)
    src = _source(Recipe, "RunModel")
    assert "step = self.step_recipe(stepn)" in src
    assert "models = self.step1_models if stepn == 1 else self.step2_models" in src
    assert "models[:] = [model_e]" in src and "model_e = models[0]" in src
    seeds = re.findall(r"derive_seed\(([^,]+),", src)
    assert seeds and set(seeds) == {"step.seed"}, seeds
    assert "rec.make_epoch_recorder(" in src and "context=context" in src
    assert '"fit_seconds": seconds' in src and '"weights_path": str(weights_path)' in src
    assert 'f"iter{iteration}_step{stepn}.weights.h5"' in src
    assert "spec = self.step_recipe(stepn).validation" in _source(Recipe, "_split")
    assert "step = self.step_recipe(1 if model is self.model1 else 2)" in \
        _source(Recipe, "reweight")


def test_parent_contract_b2():
    B2 = b2d.make_b2_multifold(_FakeEngine, None, np)
    assert "self.step_recipe(stepn).seed, stepn, iteration, \"pre_step\"" in \
        _source(B2, "seed_step")
    save = _source(B2, "_save_iteration")
    assert "models[0].get_weights()" in save
    assert save.index('f"models{i:02d}.npz"') < save.index('"state.json"')
    restore = _source(B2, "_restore")
    assert "step = self.step_recipe(stepn)" in restore and "models[:] = [model]" in restore
    unfold = _source(B2, "Unfold")
    assert unfold.index("self.seed_step(2, i)") < unfold.index("self.RunStep2(i)")
    assert "self.step1_models, self.step2_models = [], []" in unfold
    step2 = _source(B2, "RunStep2")
    assert "self.reweight(" in step2 and "self.model2" in step2


def test_parent_contract_engine_reweight():
    src = (REPO / "omnifold_nn" / "omnifold" / "omnifold.py").read_text()
    body = src[src.index("    def reweight(self,events,model,batch_size=None):"):]
    body = body[: body.index("    def log_string")]
    assert "models = self.step1_models if model == self.model1 else self.step2_models" in body
    assert "avg_weights = np.zeros((nrows))" in body
    assert "w = np.exp(np.clip(logit, -REWEIGHT_LOGIT_CAP, REWEIGHT_LOGIT_CAP))" in body
    assert "avg_weights += w / len(models)" in body
    step2 = src[src.index("    def RunStep2(self,i):"): src.index("    def RunModel(self,")]
    assert "self.reweight(self._pack_gen(self.mc.gen),self.model2)" in step2


def test_run_design_routes_through_driver_class_with_the_run_config():
    import run_design as rd
    src = inspect.getsource(rd.main)
    assert "B2 = s2e.driver_class(B2, run_config, tf, np, ru)" in src
    assert src.index("s2e.driver_class(") < src.index("unfolder = B2(")
    assert 'study["step2_ensemble"] = s2e.receipt_record(run_config, ru.derive_seed)' in src


def test_receipt_record():
    x4 = with_ensemble(dev1(), 4)
    rec = s2e.receipt_record(x4, ru.derive_seed)
    assert rec["members"] == 4
    assert rec["member_seeds"] == s2e.member_seeds(x4.step2.seed, 4, ru.derive_seed)
    assert "weight" in rec["weight_space"] and "derive_seed" in rec["seed_rule"]
