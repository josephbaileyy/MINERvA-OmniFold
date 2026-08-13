"""Equivalence test for the extracted annealed estimator.

WHAT IT PROVES: the LR interception and the records channel behave as they did when the class lived
inside `train_fullevent_nominal.py:423` -- 2 fits at base_lr for iteration 0, 4 at annealed_lr for
iterations 1-2, matching what job 56563761's receipt reports.

WHAT IT DOES NOT PROVE: that a full training run reproduces 56563761 bit-for-bit. That needs the
6 GPU-hours. Stated because a check trusted further than it goes is worse than none.

WHY THE EXISTING SUITE WAS NOT EVIDENCE: it never exercises `_fit_lr_records` at all, so it would
pass on a drifted copy that never anneals. "The tests pass" was never going to establish this.

No TensorFlow, no GPU, no omnifold: the base class and `tf` are injected, which is the whole point
of the factory.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pet"))
from annealed_estimator import make_annealed_multifold  # noqa: E402

BASE_LR, ANNEALED_LR = 1e-4, 1e-5


class _FakeOptimizer:
    def __init__(self, lr): self.learning_rate = lr


class _FakeModel:
    def __init__(self, lr=BASE_LR): self.optimizer = _FakeOptimizer(lr)


class _FakeBackend:
    @staticmethod
    def get_value(x): return x


class _FakeKeras:
    backend = _FakeBackend()


class _FakeTF:
    keras = _FakeKeras()


class _FakeMultiFold:
    """Stands in for omnifold.MultiFold. `start` is the iteration after which the anneal applies.

    CompileModel sets the model's LR the way the real engine does: full base_lr unless `fixed`,
    in which case it keeps the annealed value. That is the behaviour the subclass must flip.
    """
    def __init__(self, start=0):
        self.start = start
        self.compile_calls = []

    def CompileModel(self, model, num_steps, fixed=False):
        model.optimizer.learning_rate = ANNEALED_LR if fixed else BASE_LR
        self.compile_calls.append(bool(fixed))
        return model

    def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
        # The real engine recompiles the clone immediately before fit(); that is the intercept point.
        self.CompileModel(model, num_steps=1, fixed=False)
        return model


def _drive(cls, niter=3, steps_per_iter=2):
    """Run the engine's call pattern: one RunModel per (iteration, step)."""
    inst = cls(start=0)
    for it in range(niter):
        for stepn in range(1, steps_per_iter + 1):
            inst.RunModel(None, None, it, _FakeModel(), stepn)
    return inst


class TestAnnealedEstimator(unittest.TestCase):

    def test_records_two_base_then_four_annealed(self):
        """The 2 + 4 split 56563761's receipt reports. Fails if the interception stops firing."""
        rec = []
        cls = make_annealed_multifold(_FakeMultiFold, _FakeTF, rec)
        _drive(cls)
        self.assertEqual(len(rec), 6, f"expected 6 fit records, got {len(rec)}: {rec}")
        base = [r for r in rec if r["iteration"] == 0]
        ann = [r for r in rec if r["iteration"] > 0]
        self.assertEqual(len(base), 2, "iteration 0 must contribute 2 fits at base_lr")
        self.assertEqual(len(ann), 4, "iterations 1-2 must contribute 4 fits at annealed_lr")
        self.assertTrue(all(r["learning_rate"] == BASE_LR for r in base), base)
        self.assertTrue(all(r["learning_rate"] == ANNEALED_LR for r in ann), ann)

    def test_two_factory_calls_do_not_share_a_records_list(self):
        """THE REBINDING HAZARD, and the one a single-call test cannot see.

        A module-scope or defaulted accumulator passes the test above on the first call and then
        silently accumulates -- which is exactly what a 50-replica campaign does. Raised by the
        mediator; it is the failure mode that only appears at the scale Gate 5 will use this.
        """
        r1, r2 = [], []
        c1 = make_annealed_multifold(_FakeMultiFold, _FakeTF, r1)
        c2 = make_annealed_multifold(_FakeMultiFold, _FakeTF, r2)
        _drive(c1)
        self.assertEqual(len(r1), 6)
        self.assertEqual(len(r2), 0, "second factory call's records must be untouched by the first")
        _drive(c2)
        self.assertEqual(len(r1), 6, "first call's records must not grow when the second runs")
        self.assertEqual(len(r2), 6)
        self.assertIsNot(r1, r2)

    def test_records_is_mandatory(self):
        """No default accumulator exists, and asking for one fails loudly rather than sharing."""
        with self.assertRaises(ValueError):
            make_annealed_multifold(_FakeMultiFold, _FakeTF, None)
        with self.assertRaises(TypeError):
            make_annealed_multifold(_FakeMultiFold, _FakeTF)   # no default: this is the guarantee

    def test_anneal_actually_changes_something(self):
        """NEGATIVE CONTROL. With start above every iteration the anneal must never fire, so all
        records sit at base_lr. Without this, a subclass that forced `fixed=True` unconditionally --
        or never -- would pass the counting test by producing 6 records either way."""
        rec = []
        cls = make_annealed_multifold(_FakeMultiFold, _FakeTF, rec)
        inst = cls(start=99)
        for it in range(3):
            for stepn in (1, 2):
                inst.RunModel(None, None, it, _FakeModel(), stepn)
        self.assertEqual(len(rec), 6)
        self.assertTrue(all(r["learning_rate"] == BASE_LR for r in rec),
                        f"with start=99 nothing may anneal, got {rec}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
