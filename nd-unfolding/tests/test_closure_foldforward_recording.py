"""The closure's per-iteration fold-forward recording (OI-125 / BEN-312).

WHY THIS TEST EXISTS. `closure_powered_truth_reweight.py` had NO fold-forward computation at all --
`git grep 'fold_forward'` over it and over `closure_powered_annealed_lr.py` returned zero hits. That
is why the quarantine manifest for closure 56552326 had to reach for ANOTHER RUN'S weights
(`fullevent_nominal/…weights.npz`, the pre-anneal arm) to state a fold-forward rejection, and why
three parties then agreed on a deviation measured on the wrong file (`BEN-312`).

WHAT IS GUARDED, and every case here is a defect that was possible before the patch:

  1. the recorder is built from the base class HANDED TO IT, not from a hardcoded `MultiFold`. This is
     the load-bearing one. `closure_powered_annealed_lr.py` installs an `AnnealedMultiFold` subclass
     by rebinding `omnifold.MultiFold` before calling `cpt.main`, so a recorder that derived from the
     engine class directly would SILENTLY DROP THE ANNEAL -- the exact silent no-op that driver's own
     docstring was written to prevent, reintroduced one layer down.
  2. `RunStep1` still runs. A recorder that forgot to delegate would train nothing and report cleanly.
  3. the recorded quantity is the one step 1 CONSUMES: sum over `pass_reco` of
     `weight_reco * weights_push`, over sum of `weight_reco`. Reco leg, per D1 -- the truth leg would
     be a different number that looks equally plausible.
  4. one record per iteration, in order, capturing the push that ENTERED that iteration. A single
     end-of-run scalar cannot say which iteration drifted, and the fold-forward acts in 2 and 3 of 3.
  5. single-leg loaders (no `weight_reco`) fall back to `mc.weight`, matching the engine's own
     `Unfold`.
  6. `step1_class_ratio` is computed FROM THE CLOSURE'S OWN LOADERS, never read from the loader meta.
     The meta's value describes the NOMINAL target; this closure has an A/B split with an injected
     tilt on half A, so inheriting it would restate another configuration's R -- which is the same
     class of error as the manifest's, one field over.
"""
import hashlib
import importlib.util
import os
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ROOT, "pet")
PATH = os.path.join(PET, "closure_foldforward_instrumented.py")
SPEC = importlib.util.spec_from_file_location("closure_foldforward_instrumented", PATH)
CPT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CPT)

PINNED_DRIVER = os.path.join(PET, "closure_powered_truth_reweight.py")
PINNED_DRIVER_SHA256 = "a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48"


class _Leg:
    """The slice of a DataLoader the fold-forward reads."""

    def __init__(self, weight, pass_reco, weight_reco=None):
        self.weight = np.asarray(weight, np.float32)
        self.pass_reco = np.asarray(pass_reco, bool)
        if weight_reco is not None:
            self.weight_reco = np.asarray(weight_reco, np.float32)


class _FakeBase:
    """Stands in for MultiFold. Records that RunStep1 was reached, so delegation is observable."""

    def __init__(self, mc, weights_push, weight_reco_leg, data=None):
        self.mc = mc
        self.data = data if data is not None else _Leg([1.0] * len(mc.weight),
                                                       [True] * len(mc.weight))
        self.weights_push = np.asarray(weights_push, np.float32)
        self.mc_weight_reco = weight_reco_leg
        self.step1_calls = []

    def RunStep1(self, i):
        self.step1_calls.append(i)
        return "base-ran"


class FoldForwardRecorderTest(unittest.TestCase):
    def build(self, base=_FakeBase, **kw):
        cls, records = CPT.install_fold_forward_recorder(base)
        return cls, records

    def instance(self, n=6, push=None, dual_leg=True):
        w_reco = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], np.float32)[:n]
        # NOT proportional to w_reco, deliberately. A pure global scale makes the weighted mean of
        # push identical on both legs, so a truth-leg implementation would pass -- the first version
        # of this fixture used `w_reco * 10.0` and `test_uses_the_reco_leg_not_the_truth_leg` failed
        # on its own degeneracy guard rather than on the code. Per-row factors discriminate.
        w_truth = w_reco * np.array([1.0, 5.0, 2.0, 9.0, 3.0, 7.0], np.float32)[:n]
        pr = np.array([True, True, False, True, False, True], bool)[:n]
        mc = _Leg(w_truth, pr, w_reco if dual_leg else None)
        leg = w_reco if dual_leg else w_truth
        if push is None:
            push = np.ones(n, np.float32)
        cls, records = self.build()
        return cls(mc, push, leg), records, leg, pr

    # ---- 1: composition, the load-bearing guard --------------------------------------------------
    def test_recorder_subclasses_the_base_it_is_handed(self):
        class OtherBase(_FakeBase):
            pass

        cls, _ = CPT.install_fold_forward_recorder(OtherBase)
        self.assertTrue(issubclass(cls, OtherBase),
                        "the recorder must derive from the class handed to it; deriving from a "
                        "hardcoded MultiFold would silently drop the annealed subclass")

    def test_delegation_reaches_the_base_run_step1(self):
        obj, records, _, _ = self.instance()
        self.assertEqual(obj.RunStep1(0), "base-ran")
        self.assertEqual(obj.step1_calls, [0], "RunStep1 must still run; recording is additive")
        self.assertEqual(len(records), 1)

    # ---- 3: the recorded quantity ----------------------------------------------------------------
    def test_records_the_reco_leg_sum_over_pass_reco(self):
        push = np.array([0.5, 2.0, 9.0, 1.0, 9.0, 3.0], np.float32)
        obj, records, leg, pr = self.instance(push=push)
        obj.RunStep1(0)
        r = records[0]
        want_num = float((leg[pr].astype(np.float64) * push[pr].astype(np.float64)).sum())
        want_den = float(leg[pr].astype(np.float64).sum())
        self.assertAlmostEqual(r["sum_w_push_reco"], want_num, places=9)
        self.assertAlmostEqual(r["sum_w_reco"], want_den, places=9)
        self.assertAlmostEqual(r["reco_weighted_mean_push"], want_num / want_den, places=12)
        self.assertEqual(r["n_pass_reco"], int(pr.sum()))

    def test_excluded_rows_do_not_enter_either_sum(self):
        """A row with pass_reco False carries a huge push; it must not move the ratio."""
        push = np.array([1.0, 1.0, 1e6, 1.0, 1e6, 1.0], np.float32)
        obj, records, _, _ = self.instance(push=push)
        obj.RunStep1(0)
        self.assertAlmostEqual(records[0]["reco_weighted_mean_push"], 1.0, places=9)

    def test_uses_the_reco_leg_not_the_truth_leg(self):
        """The legs differ per row, so a truth-leg implementation gives a different ratio."""
        push = np.array([1.0, 2.0, 1.0, 4.0, 1.0, 6.0], np.float32)
        obj, records, leg, pr = self.instance(push=push)
        obj.RunStep1(0)
        truth_leg = np.asarray(obj.mc.weight, np.float64)
        truth_ratio = float((truth_leg[pr] * push[pr]).sum() / truth_leg[pr].sum())
        reco_ratio = float((leg[pr].astype(np.float64) * push[pr].astype(np.float64)).sum()
                           / leg[pr].astype(np.float64).sum())
        self.assertNotAlmostEqual(truth_ratio, reco_ratio, places=6,
                                  msg="fixture is degenerate; it cannot discriminate the legs")
        self.assertAlmostEqual(records[0]["reco_weighted_mean_push"], reco_ratio, places=12)

    # ---- 4: per iteration, in order, capturing the ENTERING push ---------------------------------
    def test_one_record_per_iteration_in_order_with_the_entering_push(self):
        obj, records, leg, pr = self.instance()
        obj.RunStep1(0)
        obj.weights_push = np.full(6, 0.5, np.float32)   # as RunStep2 would leave it
        obj.RunStep1(1)
        obj.weights_push = np.full(6, 0.25, np.float32)
        obj.RunStep1(2)
        self.assertEqual([r["iteration"] for r in records], [0, 1, 2])
        self.assertAlmostEqual(records[0]["reco_weighted_mean_push"], 1.0, places=9)
        self.assertAlmostEqual(records[1]["reco_weighted_mean_push"], 0.5, places=9)
        self.assertAlmostEqual(records[2]["reco_weighted_mean_push"], 0.25, places=9)

    # ---- 5: single-leg fallback ------------------------------------------------------------------
    def test_single_leg_loader_falls_back_to_mc_weight(self):
        obj, records, leg, pr = self.instance(dual_leg=False)
        obj.RunStep1(0)
        w = np.asarray(obj.mc.weight, np.float64)
        self.assertAlmostEqual(records[0]["sum_w_reco"], float(w[pr].sum()), places=6)

    # ---- 6: R from the loaders, never from meta ---------------------------------------------------
    def test_step1_class_ratio_is_computed_from_the_two_loaders(self):
        data = _Leg([3.0, 4.0, 100.0], [True, True, False])
        mc = _Leg([10.0, 20.0, 30.0], [True, False, True], weight_reco=[1.0, 2.0, 4.0])
        r = CPT.step1_class_ratio(data, mc)
        self.assertAlmostEqual(r, (3.0 + 4.0) / (1.0 + 4.0), places=12)

    def test_step1_class_ratio_ignores_any_meta_value(self):
        """Guards the manifest's own error one field over: R must not be inherited."""
        data = _Leg([1.0, 1.0], [True, True])
        mc = _Leg([5.0, 5.0], [True, True], weight_reco=[1.0, 1.0])
        mc.meta = {"target": {"step1_class_ratio": 999.0}}
        self.assertAlmostEqual(CPT.step1_class_ratio(data, mc), 1.0, places=12)

    def test_step1_class_ratio_fails_closed_on_an_empty_denominator(self):
        data = _Leg([1.0], [True])
        mc = _Leg([1.0], [False], weight_reco=[1.0])
        with self.assertRaises(SystemExit):
            CPT.step1_class_ratio(data, mc)


class PinnedDriverUntouchedTest(unittest.TestCase):
    """The instrumentation must stay OUT of the pinned driver.

    `closure_powered_truth_reweight.py` is pinned by four launchers and bound by run receipts --
    including `NONQUOTABLE-DIAGNOSTIC.INDEPENDENT_VALIDATION.slurm-56562169.json`'s
    `hash:source-driver`. The first version of this work edited it in place and turned
    `test_hash_bindings::test_no_new_broken_hash_bindings` and
    `test_powered_closure_preflight::…code_pins_are_discoverable…` red ("pin is stale"). Repinning to
    make that pass is prohibited while receipts bind it (BEN-270). This test states the constraint
    where the next person to reach for the driver will trip over it.
    """

    def test_driver_still_matches_its_pinned_digest(self):
        h = hashlib.sha256()
        with open(PINNED_DRIVER, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        self.assertEqual(h.hexdigest(), PINNED_DRIVER_SHA256,
                         "closure_powered_truth_reweight.py has changed. It is pinned by four "
                         "launchers and by the 47/47 validation receipt; add instrumentation in "
                         "closure_foldforward_instrumented.py instead, and do NOT repin.")

    def test_instrumentation_does_not_live_in_the_driver(self):
        with open(PINNED_DRIVER) as fh:
            src = fh.read()
        for name in ("install_fold_forward_recorder", "fold_forward_per_iteration"):
            self.assertNotIn(name, src,
                             f"{name} must live in closure_foldforward_instrumented.py, not in the "
                             f"pinned driver")


if __name__ == "__main__":
    unittest.main()
