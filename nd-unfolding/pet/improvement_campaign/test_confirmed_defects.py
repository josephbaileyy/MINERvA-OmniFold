"""Regression tests for the CONFIRMED defects of `phase_a/INTENDED_VS_EXECUTED-20260922.md`.

Every test runs a tiny OmniFold unfold twice: through the HISTORICAL path (the engine's
`MultiFold` wrapped by `make_annealed_multifold`, constructed exactly as
`run_arm_evaluation.evaluate` does -- one batch size, one learning rate) and through the REPAIRED
path (`run_unfold.make_recipe_multifold`). It asserts on EXECUTED objects captured while `fit`
runs -- the `model.optimizer` Keras trains with, the rows of the first batch actually drawn, the
weights at train begin and after the fit, the validation rows the engine held out -- never on a
declared configuration. The historical parameter is `xfail(strict=True)`: the test must FAIL on
the historical behaviour (a pass there is an error), and pass on the repaired one.

Needs TensorFlow; skipped where it is not importable.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for extra in (REPO / "nd-unfolding" / "pet", REPO / "omnifold_nn",
              REPO / "nd-unfolding" / "pet" / "configuration_comparison", HERE):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

_spec = importlib.util.spec_from_file_location("numpy_probe", HERE / "phase_a" / "numpy_probe.py")
_probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_probe)
_probe.disable_numpy_sve_probe()

from keras_backend import select_keras_backend  # noqa: E402

select_keras_backend()
tf = pytest.importorskip("tensorflow")
tf.config.experimental.enable_op_determinism()


def _seeded_layers_build() -> str | None:
    """Some Keras-2 builds (tf_keras 2.16 on Python 3.12) cannot build a layer after
    `set_random_seed`: `random.randint(1, 1e9)` is a TypeError there. Detect it and skip, so an
    unusable environment reports SKIPPED rather than failures unrelated to the defects."""
    try:
        tf.keras.utils.set_random_seed(0)
        tf.keras.layers.Dense(1)(np.zeros((1, 1), np.float32))
    except TypeError as exc:
        return f"this TensorFlow/Keras cannot build seeded layers: {exc}"
    return None


_UNUSABLE = _seeded_layers_build()
if _UNUSABLE:
    pytest.skip(_UNUSABLE, allow_module_level=True)

from annealed_estimator import make_annealed_multifold  # noqa: E402
from omnifold.dataloader import DataLoader  # noqa: E402
from omnifold.net import PET  # noqa: E402
from omnifold.omnifold import MultiFold  # noqa: E402
import recorder as rec  # noqa: E402
import run_unfold as ru  # noqa: E402
import torch_adamw  # noqa: E402
import training_recipe  # noqa: E402
from recipe import (ClippingSpec, EndpointSpec, EventSplitSpec, IterationLRSpec,  # noqa: E402
                    ModelSpec, OptimizerSpec, RunConfig, ScheduleSpec, StepRecipe,
                    StoppingSpec)

rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                              if "_clip_gradients" in vars(k)))

# `raises=AssertionError`: the historical run must COMPLETE and then fail the assertion; any other
# exception is a real failure of the test, not evidence of the defect.
HISTORICAL = pytest.param("historical", marks=pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="confirmed defect of the historical path"))
IMPLS = [HISTORICAL, "repaired"]


# ---------------------------------------------------------------------------------------------- #
# Tiny synthetic closure and models
# ---------------------------------------------------------------------------------------------- #
def synthetic(n_mc: int = 320, n_data: int = 160, parts: int = 4, feats: int = 3):
    rng = np.random.default_rng(11)

    def cloud(n):
        c = rng.normal(size=(n, parts, feats)).astype(np.float32)
        c[..., 0] = np.abs(c[..., 0]) + 0.1          # column 0 non-zero: every token is real
        return c

    def evt(n):
        return rng.normal(size=(n, 2)).astype(np.float32)

    mc = DataLoader(reco=cloud(n_mc), gen=cloud(n_mc), pass_reco=rng.random(n_mc) < 0.8,
                    pass_gen=np.ones(n_mc, bool), weight=np.ones(n_mc, np.float32),
                    weight_reco=np.ones(n_mc, np.float32), normalize=True,
                    reco_evt=evt(n_mc), gen_evt=evt(n_mc))
    data = DataLoader(reco=cloud(n_data), weight=np.ones(n_data, np.float32), normalize=True,
                      reco_evt=evt(n_data))
    return data, mc


def pet(depth: int = 1):
    return lambda: PET(3, num_evt=2, num_part=4, num_heads=1, num_transformer=depth,
                       projection_dim=8, local=True, K=2, coord_idx=(1, 2))


def step(lr=1e-3, batch=32, epochs=2, **kw):
    return StepRecipe(optimizer=kw.pop("optimizer", OptimizerSpec("adam", lr)), batch_size=batch,
                      stopping=kw.pop("stopping", StoppingSpec(max_epochs=epochs)), **kw)


# ---------------------------------------------------------------------------------------------- #
# Capture of what fit() executes
# ---------------------------------------------------------------------------------------------- #
@contextlib.contextmanager
def capture():
    fits, splits = [], []
    fit0, cache0 = tf.keras.Model.fit, MultiFold.cache

    def fit(self, *args, **kwargs):
        dataset = args[0] if args else kwargs["x"]
        first = next(iter(dataset))
        record = {"optimizer": ru.executed_optimizer_facts(tf, self.optimizer),
                  "first_batch_rows": int(tf.nest.flatten(first[0])[0].shape[0]),
                  "digests": [], "val_loss": []}

        class Probe(tf.keras.callbacks.Callback):
            def on_train_begin(self_, logs=None):
                record["begin"] = rec.trainable_digest(np, self)

            def on_epoch_end(self_, epoch, logs=None):
                record["digests"].append(rec.trainable_digest(np, self))
                record["val_loss"].append(float(logs["val_loss"]))

        kwargs["callbacks"] = list(kwargs.get("callbacks") or []) + [Probe()]
        history = fit0(self, *args, **kwargs)
        record["final"] = rec.trainable_digest(np, self)
        fits.append(record)
        return history

    def cache(self, label, weights, stepn, cached, NTRAIN):
        out = cache0(self, label, weights, stepn, cached, NTRAIN)
        idx = np.asarray(self.idx_1 if stepn == 1 else self.idx_2)
        splits.append({"step": stepn, "validation_digest": hashlib.sha256(
            np.sort(idx[int(NTRAIN):]).astype(np.int64).tobytes()).hexdigest()})
        return out

    tf.keras.Model.fit, MultiFold.cache = fit, cache
    try:
        yield fits, splits
    finally:
        tf.keras.Model.fit, MultiFold.cache = fit0, cache0


def run(impl, step1, step2, tmp_path, niter=1, depths=(1, 1)):
    """Run one tiny unfold; returns per-fit records keyed (iteration, step) and the unfolder."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    data, mc = synthetic()
    tf.keras.utils.set_random_seed(7)
    with capture() as (fits, splits):
        if impl == "historical":
            Annealed = make_annealed_multifold(MultiFold, tf, [])
            unfolder = Annealed("hist", pet(depths[0])(), pet(depths[1])(), data, mc,
                                niter=niter, epochs=step1.stopping.max_epochs,
                                batch_size=step1.batch_size, lr=step1.optimizer.learning_rate,
                                weights_folder=str(tmp_path / "w"), log_folder=str(tmp_path))
        else:
            config = RunConfig(name="rep", arm="ours", step1=step1, step2=step2,
                               iterations=niter, model_step1=ModelSpec("ours_pet"),
                               model_step2=ModelSpec("ours_pet"),
                               events=EventSplitSpec("tuning", 1, 0, 0),
                               endpoint=EndpointSpec(0.35, 3.0))
            Recipe = ru.make_recipe_multifold(MultiFold, tf, np)
            unfolder = Recipe("rep", config=config, factories={1: pet(depths[0]),
                                                                 2: pet(depths[1])},
                              data=data, mc=mc, out_dir=tmp_path,
                              training_recipe=training_recipe, torch_adamw=torch_adamw,
                              probe_rows=64)
        unfolder.Unfold()
    by_key = {(i // 2, i % 2 + 1): f for i, f in enumerate(fits)}
    if impl == "historical":
        first_split = {s["step"]: s["validation_digest"] for s in splits[:2]}
    else:
        first_split = {r["step"]: r["validation_digest"] for r in unfolder.fit_records
                       if r["iteration"] == 0}
    return by_key, first_split


# ---------------------------------------------------------------------------------------------- #
# The defects
# ---------------------------------------------------------------------------------------------- #
@pytest.mark.parametrize("impl", IMPLS)
def test_step1_trains_with_the_declared_optimizer(impl, tmp_path):
    """Hypothesis A: his declared TorchAdamW + warmup/cosine + torch clip must be what trains."""
    declared = step(batch=32, optimizer=OptimizerSpec("torch_adamw", 1e-3, epsilon=1e-8,
                                                      weight_decay=0.01),
                    schedule=ScheduleSpec("warmup_cosine", 0.1),
                    clipping=ClippingSpec("global_norm_torch", 1.0))
    fits, _ = run(impl, declared, step(batch=32), tmp_path)
    opt = fits[(0, 1)]["optimizer"]
    assert opt["class"] == "ClippedTorchAdamW"
    assert opt["schedule_class"] == "WarmupCosine"
    assert opt["torch_weight_decay"] == pytest.approx(0.01)
    assert opt["torch_grad_clip"] == pytest.approx(1.0)
    assert not opt["is_horovod_wrapped"]


@pytest.mark.parametrize("impl", IMPLS)
def test_each_step_trains_at_its_own_batch(impl, tmp_path):
    """Hypothesis B: step 2's batch is step 2's, not the arm's step-1 batch."""
    fits, _ = run(impl, step(batch=64), step(batch=16), tmp_path)
    assert fits[(0, 1)]["first_batch_rows"] == 64
    assert fits[(0, 2)]["first_batch_rows"] == 16


@pytest.mark.parametrize("impl", IMPLS)
def test_step2_learning_rate_is_the_step2_recipe(impl, tmp_path):
    """Hypothesis B: the arm-specific step-1 rate must not reach step 2."""
    fits, _ = run(impl, step(lr=3e-4), step(lr=1e-3), tmp_path)
    assert fits[(0, 1)]["optimizer"]["base_learning_rate"] == pytest.approx(3e-4, rel=1e-5)
    assert fits[(0, 2)]["optimizer"]["base_learning_rate"] == pytest.approx(1e-3, rel=1e-5)


@pytest.mark.parametrize("impl", IMPLS)
def test_later_iterations_use_the_declared_rate(impl, tmp_path):
    """A constant-rate recipe must not be annealed to 1e-5 after the first iteration."""
    constant = step(lr=1e-3, iteration_lr=IterationLRSpec("constant"))
    fits, _ = run(impl, constant, constant, tmp_path, niter=2)
    for stepn in (1, 2):
        assert fits[(1, stepn)]["optimizer"]["base_learning_rate"] == pytest.approx(1e-3,
                                                                                     rel=1e-5)


@pytest.mark.parametrize("impl", IMPLS)
def test_the_declared_restore_policy_decides_which_weights_leave_the_fit(impl, tmp_path):
    """The engine's restore_best_weights is inert unless stopping fires; `best` must be honoured.

    Pseudo-data and MC are drawn from one distribution, so the classifier can only overfit and
    validation loss rises after its minimum. Fits whose minimum is the last epoch say nothing
    and are skipped.
    """
    best = step(lr=3e-3, batch=32, stopping=StoppingSpec(max_epochs=6, restore="best"))
    fits, _ = run(impl, best, best, tmp_path)
    informative = [f for f in fits.values()
                   if int(np.argmin(f["val_loss"])) != len(f["val_loss"]) - 1]
    if not informative:
        pytest.skip("validation minimum was the last epoch in every fit")
    for f in informative:
        assert f["final"] == f["digests"][int(np.argmin(f["val_loss"]))]


@pytest.mark.parametrize("impl", IMPLS)
def test_step2_validation_rows_do_not_depend_on_step1(impl, tmp_path):
    """Hypothesis B: runs differing only in the step-1 batch must hold out the same step-2 rows.
    The engine cuts at `num_steps * batch`, so the cut moved with the arm's batch."""
    shared = step(batch=16)
    _, split_a = run(impl, step(batch=32), shared, tmp_path / "a")
    _, split_b = run(impl, step(batch=48), shared, tmp_path / "b")
    assert split_a[2] == split_b[2]


@pytest.mark.parametrize("impl", IMPLS)
def test_step2_initialization_does_not_depend_on_step1(impl, tmp_path):
    """Runs differing only in the step-1 architecture must start step 2 from the same weights.
    Historically a step-1 network drawing more initializer seeds (his arm's is a different
    architecture) shifted step 2's realized initialization at the same estimator seed."""
    shared = step(batch=16)
    fits_a, _ = run(impl, step(batch=32), shared, tmp_path / "a", depths=(1, 1))
    fits_b, _ = run(impl, step(batch=32), shared, tmp_path / "b", depths=(2, 1))
    assert fits_a[(0, 2)]["begin"] == fits_b[(0, 2)]["begin"]
