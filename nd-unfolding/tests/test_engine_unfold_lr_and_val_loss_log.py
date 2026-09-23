"""The REAL `omnifold.py` Unfold/RunModel/CompileModel path, run with TensorFlow stubbed out.

KNOWN_ISSUES #38. `Unfold()` used to call `CompileModels(fixed=True)` after every iteration. It was
dead: it compiled the untrained templates `model1`/`model2` (and, only at `n_ensemble > 1`, the
clones), and `RunModel` recompiles each clone at full `self.LR` immediately before `fit()`. The call
was removed. These tests pin what that removal must NOT change -- the learning rate every `fit()`
actually runs at, for the bare engine and for the adopted `annealed_estimator` subclass, at
`n_ensemble` 1 and 2, and the subclass's `records` channel -- and that the call stays gone.

KNOWN_ISSUES #28. The `Last val loss` line printed `val_loss[0]`, i.e. epoch 1. It now prints the
last epoch and the best epoch (1-based).

Only TensorFlow is faked (optimizer, `clone_model`, callbacks, `fit` returning a history). The engine
code under test is the committed file, loaded from disk; `cache()` is overridden to skip building
`tf.data` pipelines, which is plumbing this does not exercise.
"""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENGINE = os.path.join(REPO, "omnifold_nn", "omnifold", "omnifold.py")
sys.path.insert(0, os.path.join(REPO, "nd-unfolding", "pet"))
from annealed_estimator import make_annealed_multifold  # noqa: E402

BASE_LR, ANNEALED_LR = 1e-4, 1e-5   # the engine's `lr` default and get_optimizer's min_learning_rate
VAL_LOSS = [0.50, 0.30, 0.40]       # last != best != first, so each label is distinguishable


class _Opt:
    def __init__(self, learning_rate):
        self.learning_rate = learning_rate


class _Hist:
    def __init__(self, val_loss):
        self.history = {"val_loss": list(val_loss), "loss": list(val_loss)}


class _Model:
    """Records every compile and the LR each fit ran at."""
    _n = 0

    def __init__(self, role):
        _Model._n += 1
        self.role, self.uid = role, _Model._n
        self.optimizer = None
        self.compiles = []

    def compile(self, opt, loss=None, weighted_metrics=None):
        self.optimizer = opt
        self.compiles.append(opt.learning_rate)

    def fit(self, *a, **kw):
        _FIT_LOG.append((self.role, self.uid, self.optimizer.learning_rate))
        return _Hist(VAL_LOSS)

    def predict(self, events, batch_size=None, verbose=0):
        n = len(events[0]) if isinstance(events, (tuple, list)) else len(events)
        return np.zeros((n, 1), dtype=np.float32)


_FIT_LOG = []


def _clone_model(m):
    return _Model("clone-of-" + m.role)


def _fake_tf():
    tf = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    callbacks = types.ModuleType("tensorflow.keras.callbacks")
    for name in ("EarlyStopping", "ModelCheckpoint", "ReduceLROnPlateau"):
        setattr(callbacks, name, lambda *a, **kw: None)
    keras.callbacks = callbacks
    keras.optimizers = types.SimpleNamespace(Adam=_Opt)
    keras.models = types.SimpleNamespace(clone_model=_clone_model)
    keras.backend = types.SimpleNamespace(get_value=lambda v: v)
    tf.keras = keras
    tf.config = types.SimpleNamespace(experimental=types.SimpleNamespace(
        list_physical_devices=lambda *_: []))
    pkg = types.ModuleType("omnifold")
    net = types.ModuleType("omnifold.net")
    net.weighted_binary_crossentropy = object()
    pkg.net = net
    return {"tensorflow": tf, "tensorflow.keras": keras, "tensorflow.keras.callbacks": callbacks,
            "omnifold": pkg, "omnifold.net": net, "horovod": None}, tf


def _load_engine():
    mods, tf = _fake_tf()
    with mock.patch.dict(sys.modules, mods):
        spec = importlib.util.spec_from_file_location("_engine_under_test", ENGINE)
        mod = importlib.util.module_from_spec(spec)
        with mock.patch("builtins.print"):
            spec.loader.exec_module(mod)
    return mod, tf


ENGINE_MOD, FAKE_TF = _load_engine()


def _make(cls, n_ensemble, niter, tmp):
    """An instance without __init__ (which needs real DataLoaders); attributes as __init__ sets them."""
    n = 8
    self = cls.__new__(cls)
    mc = types.SimpleNamespace(weight=np.ones(n, np.float32), pass_reco=np.ones(n, bool),
                               pass_gen=np.ones(n, bool), reco=np.zeros((n, 2), np.float32),
                               gen=np.zeros((n, 2), np.float32), nmax=n)
    data = types.SimpleNamespace(weight=np.ones(n, np.float32), pass_reco=np.ones(n, bool),
                                 reco=np.zeros((n, 2), np.float32), nmax=n)
    self.name, self.niter, self.n_ensemble = "t", niter, n_ensemble
    self.data, self.mc, self.strap_id, self.start = data, mc, 0, 0
    self.train_frac, self.size, self.rank, self.verbose = 0.8, 1, 0, False
    self.log_file = open(os.path.join(tmp, "log.txt"), "w")
    self.model1, self.model2 = _Model("model1"), _Model("model2")
    self.BATCH_SIZE, self.EPOCHS, self.LR, self.patience = 2, 3, BASE_LR, 10
    self.num_steps_reco = self.num_steps_gen = 4
    self.weights_folder = tmp
    self.PrepareInputs()
    return self


def _subclass_without_data_pipeline(base):
    class _NoCache(base):
        def cache(self, label, weights, stepn, cached, NTRAIN):
            return None, None
    return _NoCache


def _run(annealed, n_ensemble, niter=3):
    _FIT_LOG.clear()
    records = []
    base = ENGINE_MOD.MultiFold
    if annealed:
        base = make_annealed_multifold(base, FAKE_TF, records)
    cls = _subclass_without_data_pipeline(base)
    with tempfile.TemporaryDirectory() as tmp, mock.patch("builtins.print"):
        inst = _make(cls, n_ensemble, niter, tmp)
        if annealed:
            inst._ann_iter, inst._inside_fit_compile = 0, False   # what the subclass __init__ sets
        inst.Unfold()
        inst.log_file.close()
        with open(os.path.join(tmp, "log.txt")) as fh:
            log = fh.read()
    return inst, list(_FIT_LOG), records, log


class FitTimeLearningRate(unittest.TestCase):
    """What every fit() runs at -- the only LR that reaches the numbers."""

    def test_bare_engine_trains_every_fit_at_full_lr(self):
        for ens in (1, 2):
            _, fits, _, _ = _run(annealed=False, n_ensemble=ens)
            self.assertEqual(len(fits), 3 * 2 * ens)
            self.assertEqual({lr for _, _, lr in fits}, {BASE_LR}, f"n_ensemble={ens}")

    def test_annealed_subclass_base_at_iteration_0_then_annealed(self):
        for ens in (1, 2):
            _, fits, records, _ = _run(annealed=True, n_ensemble=ens)
            per_iter = 2 * ens
            self.assertEqual([lr for _, _, lr in fits],
                             [BASE_LR] * per_iter + [ANNEALED_LR] * (2 * per_iter),
                             f"n_ensemble={ens}")
            # The receipt channel: one record per fit-time compile, nothing else. The removed
            # between-iteration compile ran outside RunModel, so it never appended here.
            self.assertEqual(len(records), len(fits))
            self.assertEqual([r["learning_rate"] for r in records], [lr for _, _, lr in fits])
            self.assertEqual([r["iteration"] for r in records],
                             [0] * per_iter + [1] * per_iter + [2] * per_iter)

    def test_templates_are_compiled_once_and_never_trained(self):
        """The only compile Unfold makes outside RunModel is the initial CompileModels()."""
        for ens in (1, 2):
            inst, fits, _, _ = _run(annealed=False, n_ensemble=ens)
            self.assertEqual(inst.model1.compiles, [BASE_LR])
            self.assertEqual(inst.model2.compiles, [BASE_LR])
            trained = {uid for _, uid, _ in fits}
            self.assertNotIn(inst.model1.uid, trained)
            self.assertNotIn(inst.model2.uid, trained)
            # Each clone is compiled exactly once per fit (the fit-time compile), never between.
            for m in inst.step1_models + inst.step2_models:
                self.assertEqual(len(m.compiles), 3, f"n_ensemble={ens}")


class ValLossLog(unittest.TestCase):

    def test_logs_last_and_best_epoch_not_the_first(self):
        _, _, _, log = _run(annealed=False, n_ensemble=1, niter=1)
        lines = [ln for ln in log.splitlines() if ln.startswith("Last val loss")]
        self.assertEqual(len(lines), 2)
        for ln in lines:
            self.assertEqual(ln, "Last val loss 0.4 (epoch 3); best val loss 0.3 (epoch 2)")
            self.assertNotIn("0.5", ln, "val_loss[0] (epoch 1) is being reported")


if __name__ == "__main__":
    unittest.main(verbosity=2)
