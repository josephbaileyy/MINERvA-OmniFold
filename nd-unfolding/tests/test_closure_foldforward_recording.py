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
import tempfile
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


class CorrectedArmTest(unittest.TestCase):
    """Arm 1: the SCALE-ONLY fold-forward correction (proposal 4b).

    Predeclared scale-only, and these tests are what makes that checkable rather than aspirational.
    A per-cell variant is refused because a per-cell field built from `push` is the unfolding's own
    output, so dividing it out is a de-unfolding (BEN-310). `test_correction_is_a_pure_scalar`
    is the guard that would catch a later "improvement" to per-cell.
    """

    def legs(self, n=6):
        w_reco = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], np.float32)[:n]
        w_truth = w_reco * np.array([1.0, 5.0, 2.0, 9.0, 3.0, 7.0], np.float32)[:n]
        pr = np.array([True, True, False, True, False, True], bool)[:n]
        mc = _Leg(w_truth, pr, w_reco)
        data = _Leg([2.0] * n, [True] * n)      # R = sum(data)/sum(w_reco[pr]) != 1
        return mc, data, w_reco, pr

    def build(self, correct, push=None):
        mc, data, leg, pr = self.legs()
        if push is None:
            push = np.array([0.5, 2.0, 9.0, 1.0, 9.0, 3.0], np.float32)
        cls, records = CPT.install_fold_forward_recorder(_FakeBase, correct=correct)
        obj = cls(mc, push, leg, data=data)
        return obj, records, leg, pr

    def test_correction_is_off_by_default(self):
        cls, _ = CPT.install_fold_forward_recorder(_FakeBase)
        mc, data, leg, pr = self.legs()
        push = np.array([0.5, 2.0, 9.0, 1.0, 9.0, 3.0], np.float32)
        obj = cls(mc, push, leg, data=data)
        before = np.array(obj.weights_push, np.float64, copy=True)
        obj.RunStep1(0)
        np.testing.assert_allclose(obj.weights_push, before, rtol=0, atol=0)

    def test_corrected_arm_makes_the_fold_forward_equal_R(self):
        obj, records, leg, pr = self.build(correct=True)
        obj.RunStep1(0)
        w = np.asarray(leg, np.float64)
        push = np.asarray(obj.weights_push, np.float64)
        after = float((w[pr] * push[pr]).sum() / w[pr].sum())
        # TOLERANCE IS SET BY THE REPRESENTATION, NOT BY WHAT PASSES. weights_push is
        # float32 by the engine's contract (omnifold.py:164), so the corrected ratio can
        # only be exact to float32 epsilon (1.19e-07); measured deviation here is 1.4e-08.
        # A per-cell or mis-ordered correction deviates by O(0.1-1), so 1e-6 keeps all the
        # power -- re-verified by re-running both mutations after this change.
        self.assertLess(abs(after - records[0]["step1_class_ratio"]), 1e-6)
        self.assertLess(abs(records[0]["reco_weighted_mean_push_after_correction"] - after), 1e-6)

    def test_recorded_ratio_is_the_PRE_correction_measurement(self):
        """The measurement must survive the correction, or arm 1 records only its own fixed point."""
        obj, records, leg, pr = self.build(correct=True)
        push_before = np.array(obj.weights_push, np.float64, copy=True)
        w = np.asarray(leg, np.float64)
        expect = float((w[pr] * push_before[pr]).sum() / w[pr].sum())
        obj.RunStep1(0)
        self.assertAlmostEqual(records[0]["reco_weighted_mean_push"], expect, places=12)
        self.assertNotAlmostEqual(records[0]["reco_weighted_mean_push"],
                                  records[0]["step1_class_ratio"], places=6,
                                  msg="fixture is degenerate; pre-correction ratio already equals R")

    def test_recorded_factor_is_R_over_the_measured_ratio(self):
        obj, records, leg, pr = self.build(correct=True)
        obj.RunStep1(0)
        r = records[0]
        self.assertAlmostEqual(r["applied_correction_factor"],
                               r["step1_class_ratio"] / r["reco_weighted_mean_push"], places=12)

    def test_correction_is_a_pure_scalar(self):
        """Every row scaled by ONE factor: the SHAPE of push is untouched. Guards per-cell drift."""
        obj, records, leg, pr = self.build(correct=True)
        before = np.array(obj.weights_push, np.float64, copy=True)
        obj.RunStep1(0)
        after = np.asarray(obj.weights_push, np.float64)
        ratios = after / before
        # float32 storage again: identical scaling still differs in the last bit. A per-cell factor
        # spreads the ratios by O(0.01) or more, which 1e-5 catches with room to spare.
        self.assertLess(float(ratios.max() - ratios.min()), 1e-5,
                        "the correction varied across rows; predeclared SCALE-ONLY")
        self.assertLess(abs(float(ratios[0]) - records[0]["applied_correction_factor"]), 1e-6)

    def test_correction_is_applied_BEFORE_step1_consumes_it(self):
        """Order matters: a correction applied after delegation would not change training at all."""
        seen = {}

        class Watcher(_FakeBase):
            def RunStep1(self, i):
                seen["push_at_step1"] = np.array(self.weights_push, np.float64, copy=True)
                return super().RunStep1(i)

        mc, data, leg, pr = self.legs()
        push = np.array([0.5, 2.0, 9.0, 1.0, 9.0, 3.0], np.float32)
        cls, records = CPT.install_fold_forward_recorder(Watcher, correct=True)
        obj = cls(mc, push, leg, data=data)
        obj.RunStep1(0)
        w = np.asarray(leg, np.float64)
        p = seen["push_at_step1"]
        consumed = float((w[pr] * p[pr]).sum() / w[pr].sum())
        # If the correction ran AFTER delegation, `consumed` is the PRE-correction ratio, which
        # differs from R by O(0.1) here -- so 1e-6 is nowhere near the discriminating scale.
        self.assertLess(abs(consumed - records[0]["step1_class_ratio"]), 1e-6,
                        "step 1 consumed the UNcorrected push; the correction is a no-op")


class EngineInterfaceContractTest(unittest.TestCase):
    """The guard that 18 passing tests did not have, and job 57012031_3 paid for.

    WHAT THE OTHER TESTS COULD NOT SEE. They exercise the correction's ARITHMETIC against fixtures --
    scalar not per-cell, applied before delegation, ratio equals R afterwards -- and all of that was
    correct. The defect was in the INTERFACE: the dtype of the object handed back to the engine.
    `weights_push` is float32 (omnifold.py:164,168); a Python-float scalar promotes it to float64;
    the engine packs it into column 1 of y_true (omnifold.py:360) and
    net.weighted_binary_crossentropy:13 multiplies it against float32 logits, dying inside a
    tf.function. A fixture-only suite cannot fail on a contract with a collaborator it never calls.

    So one test asserts the contract directly (runs anywhere), and one pushes the corrected array
    through the ENGINE'S OWN LOSS (skipped only if TF is unavailable, so it is real on the cluster).
    """

    def corrected_push(self):
        w_reco = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], np.float32)
        w_truth = w_reco * np.array([1.0, 5.0, 2.0, 9.0, 3.0, 7.0], np.float32)
        pr = np.array([True, True, False, True, False, True], bool)
        mc = _Leg(w_truth, pr, w_reco)
        data = _Leg([2.0] * 6, [True] * 6)
        cls, records = CPT.install_fold_forward_recorder(_FakeBase, correct=True)
        obj = cls(mc, np.array([0.5, 2.0, 9.0, 1.0, 9.0, 3.0], np.float32), w_reco, data=data)
        obj.RunStep1(0)
        return obj, records

    def test_correction_preserves_the_engine_weight_dtype(self):
        obj, _ = self.corrected_push()
        self.assertEqual(np.asarray(obj.weights_push).dtype, np.float32,
                         "weights_push must stay float32; the engine's loss multiplies it against "
                         "float32 logits (net.py:13) and float64 dies inside a tf.function")

    def test_correction_preserves_whatever_dtype_it_was_given(self):
        """Not hardcoded to float32: the contract is 'do not change it', which is the general rule."""
        for dt in (np.float32, np.float64):
            w_reco = np.array([1.0, 2.0, 4.0], dt)
            mc = _Leg(np.array([1.0, 2.0, 4.0], dt), np.array([True, True, True]), w_reco)
            data = _Leg([2.0, 2.0, 2.0], [True, True, True])
            cls, _ = CPT.install_fold_forward_recorder(_FakeBase, correct=True)
            obj = cls(mc, np.array([0.5, 2.0, 3.0], dt), w_reco, data=data)
            obj.weights_push = np.asarray(obj.weights_push, dt)
            obj.RunStep1(0)
            self.assertEqual(np.asarray(obj.weights_push).dtype, np.dtype(dt),
                             f"dtype {dt} was not preserved through the correction")

    def test_corrected_weights_survive_the_ENGINES_OWN_loss(self):
        """The real thing: pack as omnifold.py:360 does and call net.weighted_binary_crossentropy.

        This is the test that would have caught 57012031_3. It is not a fixture -- it calls the
        engine function whose Mul raised, with the array this module actually produces.
        """
        try:
            import tensorflow as tf
        except Exception as exc:                                     # pragma: no cover
            self.skipTest(f"tensorflow unavailable: {exc}")
        engine_dir = os.path.join(os.path.dirname(ROOT), "omnifold_nn", "omnifold")
        net_path = os.path.join(engine_dir, "net.py")
        if not os.path.exists(net_path):                             # pragma: no cover
            self.skipTest(f"engine net.py not found at {net_path}")
        spec = importlib.util.spec_from_file_location("omnifold_net_for_test", net_path)
        net = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(net)
        except Exception as exc:                                     # pragma: no cover
            self.skipTest(f"engine net.py not importable in this environment: {exc}")

        obj, _ = self.corrected_push()
        weights = np.asarray(obj.weights_push)
        labels = np.ones(weights.shape[0], np.float32)
        # EXACTLY the engine's packing, omnifold.py:360.
        y_true = np.stack((labels, weights), axis=1)
        y_pred = tf.zeros((weights.shape[0], 1), tf.float32)
        loss = net.weighted_binary_crossentropy(tf.convert_to_tensor(y_true), y_pred)
        self.assertTrue(np.isfinite(float(loss)), "the engine's loss did not return a finite value")

    def test_the_loss_really_does_reject_float64_so_the_test_above_has_power(self):
        """Without this, the test above could pass because the loss accepts anything."""
        try:
            import tensorflow as tf
        except Exception as exc:                                     # pragma: no cover
            self.skipTest(f"tensorflow unavailable: {exc}")
        engine_dir = os.path.join(os.path.dirname(ROOT), "omnifold_nn", "omnifold")
        net_path = os.path.join(engine_dir, "net.py")
        if not os.path.exists(net_path):                             # pragma: no cover
            self.skipTest("engine net.py not found")
        spec = importlib.util.spec_from_file_location("omnifold_net_for_test_power", net_path)
        net = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(net)
        except Exception as exc:                                     # pragma: no cover
            self.skipTest(f"engine net.py not importable: {exc}")
        n = 4
        y_true64 = np.stack((np.ones(n), np.full(n, 1.7)), axis=1).astype(np.float64)
        y_pred = tf.zeros((n, 1), tf.float32)
        with self.assertRaises(Exception):
            float(net.weighted_binary_crossentropy(tf.convert_to_tensor(y_true64), y_pred))


class ReportAnnotationTest(unittest.TestCase):
    """The two things a JSON-ONLY consumer of one of these reports has to be able to see.

    Both were absent from the six products of 2026-08-15 and both are the same shape of defect: a
    fact carried somewhere a `json.load` does not reach. Non-quotability lived in the FILENAME and
    in `artifact.path`; the retired-0.80-bar self-report lived under a name (`recovery_criteria_met`)
    that reads as the verdict. Those six receipts are the record and were not rewritten.
    """

    def _report(self, **extra):
        rep = {"metrics": {"recovery": 0.5118916141218095}, "recovery_criteria_met": False,
               "verdict": "FAIL"}
        rep.update(extra)
        return rep

    def test_nonquotability_is_a_field_not_only_a_filename(self):
        rep = CPT.annotate_nonquotability(
            self._report(), "/x/NONQUOTABLE-DIAGNOSTIC.FOLDFORWARD_ARM0_DRAW0.slurm-1_0.json",
            artifact_path="/x/NONQUOTABLE-DIAGNOSTIC.FOLDFORWARD_ARM0_DRAW0.slurm-1_0.npz")
        self.assertTrue(rep["nonquotable"])
        self.assertEqual(rep["label"], "nonquotable-diagnostic")
        self.assertTrue(rep["nonquotability"]["marker_in_report_filename"])
        self.assertTrue(rep["nonquotability"]["marker_in_artifact_path"])

    def test_the_label_is_the_one_the_quarantine_gate_actually_refuses_on(self):
        """Not a new boolean nobody reads: `require_quotable` keys off exactly this value.

        The artifact below is built to CLEAR ground 1 (the physics, `dev = 0`), because that ground
        is sufficient on its own and would otherwise reject for a reason that says nothing about the
        label. Reaching ground 3 is the whole point: with the label the run is refused, and with the
        label removed the same call returns True -- so the assertion is about this field and not
        about the gate rejecting everything handed to it.
        """
        pdq_path = os.path.join(PET, "pet_diagnostic_quarantine.py")
        spec = importlib.util.spec_from_file_location("pdq_for_test", pdq_path)
        pdq = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pdq)
        rep = CPT.annotate_nonquotability(self._report(), "/x/r.json")
        self.assertEqual(rep["label"], pdq.DIAGNOSTIC_LABEL)

        with tempfile.TemporaryDirectory() as tmp:
            npz = os.path.join(tmp, "w.npz")
            np.savez(npz, fold_forward_sum_w_push_reco=np.array([2.0]),
                     fold_forward_sum_w_reco=np.array([2.0]),
                     target=np.array({"step1_class_ratio": 1.0}, dtype=object))
            with self.assertRaises(pdq.NonQuotableError) as ctx:
                pdq.require_quotable(rep, npz)
            self.assertIn(pdq.DIAGNOSTIC_LABEL, str(ctx.exception))
            cleared = {k: v for k, v in rep.items() if k != "label"}
            self.assertTrue(pdq.require_quotable(cleared, npz),
                            "the label is what the refusal turned on")

    def test_a_missing_filename_marker_is_reported_false_not_hidden(self):
        """The measured half must be able to read false, or it is decoration (BEN-070 rule 3)."""
        rep = CPT.annotate_nonquotability(self._report(), "/x/plain_name.json",
                                          artifact_path="/x/plain_name.npz")
        self.assertFalse(rep["nonquotability"]["marker_in_report_filename"])
        self.assertFalse(rep["nonquotability"]["marker_in_artifact_path"])
        self.assertTrue(rep["nonquotable"], "the module-level fact does not depend on the filename")

    def test_retired_080_bar_field_is_renamed_away_from_the_verdict(self):
        rep = CPT.rename_retired_recovery_bar_field(self._report())
        self.assertNotIn("recovery_criteria_met", rep)
        self.assertIs(rep["recovery_criteria_met_AGAINST_RETIRED_0p80_BAR_NOT_THE_VERDICT"], False)
        self.assertIn("CLM-012", rep["recovery_criteria_met_field_note"])

    def test_the_rename_is_idempotent_and_preserves_the_value(self):
        """It composes with closure_powered_annealed_lr's rename; applying twice must not lose it."""
        once = CPT.rename_retired_recovery_bar_field(self._report(recovery_criteria_met=True))
        twice = CPT.rename_retired_recovery_bar_field(dict(once))
        self.assertIs(twice["recovery_criteria_met_AGAINST_RETIRED_0p80_BAR_NOT_THE_VERDICT"], True)
        self.assertNotIn("recovery_criteria_met", twice)

    def test_the_rename_does_not_touch_the_measurements(self):
        rep = CPT.rename_retired_recovery_bar_field(
            CPT.annotate_nonquotability(self._report(), "/x/r.json"))
        self.assertEqual(rep["metrics"]["recovery"], 0.5118916141218095)
        self.assertEqual(rep["verdict"], "FAIL", "`verdict` is the pinned driver's; not rewritten")


class LauncherWrapperPinTest(unittest.TestCase):
    """G0's fourth pin must name the wrapper AS IT IS NOW, or the launcher refuses every run.

    `test_foldforward_launcher_guards.sh` case 1 asserts the same thing end-to-end, but it needs
    bash >= 4 and SKIPS on macOS -- where this repo's local development happens. A pin that only
    a skipped test checks is a pin that goes stale silently.
    """

    def test_wrapper_pin_matches_the_wrapper(self):
        launcher = os.path.join(PET, "sbatch_foldforward_instrumented_closure.sh")
        with open(launcher) as fh:
            src = fh.read()
        h = hashlib.sha256()
        with open(PATH, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        self.assertIn(
            f'["$WRAPPER"]="{h.hexdigest()}"', src,
            "closure_foldforward_instrumented.py changed without updating G0's WRAPPER pin in "
            "sbatch_foldforward_instrumented_closure.sh. Update the literal in the SAME commit "
            "(the launcher's own maintenance note says so); do NOT delete the pin, and do not "
            "repin the DRIVER, which is receipt-bound (BEN-270).")


class _FakeEngine:
    """Mirrors omnifold.MultiFold's Unfold LOOP, because that ordering is what the hooks depend on.

    `omnifold.py:172-177` is `for i in range(start, niter): RunStep1(i); RunStep2(i);
    CompileModels(fixed=True)`, and `RunStep2` assigns `self.weights_push` (`:220`). The trailing
    `CompileModels` is reproduced deliberately -- the claim under test is that it does NOT touch
    `weights_push`, so a fixture that omitted it would assume what it is meant to demonstrate.
    """

    def __init__(self, mc, weight_reco_leg, niter=3, n=4):
        self.mc = mc
        self.data = _Leg([1.0] * n, [True] * n)
        self.mc_weight_reco = weight_reco_leg
        self.weights_push = np.ones(n, dtype=np.float32)
        self.niter, self.start = niter, 0
        self.LR = 1e-4
        self.compile_calls = []
        self.step2_calls = []

    def Unfold(self):
        for i in range(self.start, self.niter):
            self.RunStep1(i)
            self.RunStep2(i)
            self.CompileModels(fixed=True)

    def RunStep1(self, i):
        return "step1"

    def RunStep2(self, i):
        # A DIFFERENT push each iteration, so a hook reading at the wrong moment gets a wrong number
        # rather than an accidentally-equal one.
        self.step2_calls.append(i)
        self.weights_push = np.full(self.weights_push.shape[0], 1.0 + 0.1 * (i + 1), dtype=np.float32)
        return "step2"

    def CompileModels(self, fixed=False):
        self.compile_calls.append(fixed)          # must not touch weights_push


class EndOfRunPushHookTest(unittest.TestCase):
    """The RunStep2 hook exists to capture the ONE push no RunStep1 row can see (BEN-360, VL134).

    `RunStep2(niter-1)` leaves a push that nothing consumes, and that is the value
    `closure_powered_truth_reweight.py:332-333` persists and `OI-125` is about. Substituting the last
    RunStep1 row gives 0.981165 against a predicted 1.011418 -- a ~105-draw-sd 'disagreement' with the
    sign of ratio-1 flipped. Predeclared in
    PREDECLARATION-20260816-endofrun-push-recording.md before any run carries it.
    """

    def _run(self):
        n = 4
        mc = _Leg([1.0] * n, [True, True, True, False], weight_reco=[1.0, 2.0, 3.0, 4.0])
        rec_cls, ff = CPT.install_fold_forward_recorder(_FakeEngine)
        inst = rec_cls(mc, mc.weight_reco, niter=3, n=n)
        inst.Unfold()
        return inst, ff, list(rec_cls.FOLD_FORWARD_STEP2_RECORDS)

    def test_one_post_step2_record_per_iteration_in_order(self):
        inst, ff, s2 = self._run()
        self.assertEqual([r["iteration"] for r in s2], [0, 1, 2])
        self.assertEqual(len(ff), 3)
        self.assertEqual(inst.step2_calls, [0, 1, 2])

    def test_exactly_one_record_is_flagged_end_of_run(self):
        _, _, s2 = self._run()
        flagged = [r for r in s2 if r["is_end_of_run_push"]]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["iteration"], 2)
        self.assertEqual(flagged[0]["push_recorded_here_was_left_by"], "RunStep2(2)")

    def test_the_final_capture_is_BIT_IDENTICAL_to_what_the_driver_persists(self):
        """The load-bearing claim: what the hook records is what `of.weights_push` holds afterwards.

        The driver reads `of.weights_push` AFTER `Unfold()` returns
        (closure_powered_truth_reweight.py:332-333). Only `CompileModels(fixed=True)` runs between the
        last RunStep2 and that read, so the arrays must agree bit-for-bit.
        """
        inst, ff, s2 = self._run()
        persisted = np.asarray(inst.weights_push, np.float64)          # exactly the driver's read
        leg = np.asarray(inst.mc_weight_reco, np.float64)
        pr = np.asarray(inst.mc.pass_reco).astype(bool)
        driver_ratio = float((leg[pr] * persisted[pr]).sum()) / float(leg[pr].sum())
        end = [r for r in s2 if r["is_end_of_run_push"]][0]
        self.assertEqual(end["reco_weighted_mean_push"], driver_ratio,
                         "the hook's end-of-run capture is not the array the driver persists")
        self.assertTrue(inst.compile_calls and all(inst.compile_calls),
                        "the fixture must exercise the trailing CompileModels(fixed=True)")

    def test_THE_ASSERTION_ABOVE_HAS_POWER_a_pre_delegation_capture_FAILS_it(self):
        """A hook recording BEFORE super().RunStep2 would capture the previous iteration's push.

        Without this, `test_the_final_capture_is_BIT_IDENTICAL...` could pass on a fixture where every
        push happened to be equal, and would then be asserting nothing -- BEN-314.
        """
        n = 4
        mc = _Leg([1.0] * n, [True, True, True, False], weight_reco=[1.0, 2.0, 3.0, 4.0])
        captured = []

        class WrongMoment(_FakeEngine):
            def RunStep2(self, i):
                captured.append(np.asarray(self.weights_push, np.float64).copy())   # BEFORE
                return super().RunStep2(i)

        inst = WrongMoment(mc, mc.weight_reco, niter=3, n=n)
        inst.Unfold()
        persisted = np.asarray(inst.weights_push, np.float64)
        self.assertFalse(np.array_equal(captured[-1], persisted),
                         "the fixture's pushes are indistinguishable, so the bit-identity test above "
                         "would pass vacuously")

    def test_the_overlapping_rows_agree_EXACTLY_between_the_two_hooks(self):
        """`RunStep2(i)` leaves the push `RunStep1(i+1)` consumes, so those rows are the same number."""
        _, ff, s2 = self._run()
        by_iter = {r["iteration"]: r for r in ff}
        pairs = 0
        for r in s2:
            nxt = by_iter.get(r["iteration"] + 1)
            if nxt is None:
                continue
            self.assertEqual(r["reco_weighted_mean_push"], nxt["reco_weighted_mean_push"])
            pairs += 1
        self.assertEqual(pairs, 2, "niter=3 must produce 2 overlapping pairs")

    def test_the_overlap_gate_REFUSES_a_disagreement(self):
        """Demonstrated on the gate itself, not just on a passing case."""
        ff = [{"iteration": 1, "reco_weighted_mean_push": 1.5}]
        s2 = [{"iteration": 0, "reco_weighted_mean_push": 1.4, "is_end_of_run_push": False}]
        by_iter = {int(r["iteration"]): r for r in ff}
        mismatches = [r for r in s2
                      if by_iter.get(int(r["iteration"]) + 1) is not None
                      and r["reco_weighted_mean_push"]
                      != by_iter[int(r["iteration"]) + 1]["reco_weighted_mean_push"]]
        self.assertEqual(len(mismatches), 1,
                         "the gate's comparison must flag a differing overlapping pair")

    def test_both_hooks_share_ONE_reduction(self):
        """Two copies of 'the same' arithmetic is how the overlap check would start comparing
        implementations instead of moments."""
        with open(PATH) as fh:
            src = fh.read()
        self.assertEqual(src.count("def _ff_reduce"), 1)
        self.assertIn("rec = self._ff_reduce(int(i))", src)

    def test_the_corrected_arm_still_overlaps_because_RunStep1_records_PRE_correction(self):
        """Arm 1 rescales push inside RunStep1, but AFTER appending its row -- so equality survives."""
        n = 4
        mc = _Leg([1.0] * n, [True, True, True, False], weight_reco=[1.0, 2.0, 3.0, 4.0])
        rec_cls, ff = CPT.install_fold_forward_recorder(_FakeEngine, correct=True)
        inst = rec_cls(mc, mc.weight_reco, niter=3, n=n)
        inst.Unfold()
        s2 = list(rec_cls.FOLD_FORWARD_STEP2_RECORDS)
        by_iter = {r["iteration"]: r for r in ff}
        for r in s2:
            nxt = by_iter.get(r["iteration"] + 1)
            if nxt is not None:
                self.assertEqual(r["reco_weighted_mean_push"], nxt["reco_weighted_mean_push"])
        self.assertTrue(all(r["applied_correction_factor"] is not None for r in ff))


class AnnealAttestationTest(unittest.TestCase):
    """`attest_anneal_took_effect` must REFUSE an un-annealed run, not describe one (BEN-317).

    A guard that passes on the thing it exists to catch is worse than no guard, because it converts
    an open question into a recorded assurance -- `BEN-314`'s lesson, and the reason every case here
    is a failure demonstrated rather than a success asserted.

    The six products of 2026-08-15 carry `fold_forward_composed_with_annealed_arm: True` and nothing
    else, and that boolean is True even when the LR record list is EMPTY. These tests are what makes
    the replacement falsifiable.
    """

    @classmethod
    def setUpClass(cls):
        import sys
        if PET not in sys.path:                     # the sibling is imported by name at runtime
            sys.path.insert(0, PET)
        import closure_powered_annealed_lr as cpa
        cls.cpa = cpa

    @staticmethod
    def _records(pattern):
        """pattern: list of (iteration, learning_rate); two fits per iteration, as the engine does."""
        out = []
        for it, lr in pattern:
            for step in (1, 2):
                out.append({"iteration": it, "step": step, "learning_rate": lr,
                            "requested_fixed": False, "effective_fixed": it > 0})
        return out

    def _good(self):
        return self._records([(0, 1e-4), (1, self.cpa.ANNEALED_LR), (2, self.cpa.ANNEALED_LR)])

    def test_empty_records_are_REFUSED_not_reported(self):
        """The exact state the old boolean left as an unbacked True."""
        with self.assertRaises(SystemExit) as ctx:
            CPT.attest_anneal_took_effect([], declared_lr=1e-4, start=0, niter=3)
        self.assertIn("NO fit-time LR records", str(ctx.exception))

    def test_None_records_are_refused(self):
        with self.assertRaises(SystemExit):
            CPT.attest_anneal_took_effect(None, declared_lr=1e-4, start=0, niter=3)

    def test_a_correct_pattern_passes_and_counts_both_legs(self):
        proof = CPT.attest_anneal_took_effect(self._good(), declared_lr=1e-4, start=0, niter=3)
        self.assertTrue(proof["pass"])
        self.assertEqual(proof["n_fits_at_base_lr"], 2)
        self.assertEqual(proof["n_fits_at_annealed_lr"], 4)
        self.assertEqual(proof["n_records"], 6)
        self.assertTrue(proof["n_records_matches_two_per_iteration"])
        self.assertEqual(proof["engine_declared_LR"], 1e-4)

    def test_the_reference_pattern_matches_run_56552326s_proof(self):
        """The landed proof for the band-setting run: 2 fits at 1e-4, 4 at 1e-5, 6 records."""
        proof = CPT.attest_anneal_took_effect(self._good(), declared_lr=1e-4, start=0, niter=3)
        self.assertEqual(
            (proof["n_fits_at_base_lr"], proof["n_fits_at_annealed_lr"], proof["n_records"]),
            (2, 4, 6))

    def test_an_UNANNEALED_run_is_refused(self):
        """Every fit at the base rate -- the interception silently not firing."""
        bad = self._records([(0, 1e-4), (1, 1e-4), (2, 1e-4)])
        with self.assertRaises(SystemExit) as ctx:
            CPT.attest_anneal_took_effect(bad, declared_lr=1e-4, start=0, niter=3)
        self.assertIn("DID NOT TAKE EFFECT", str(ctx.exception))

    def test_annealing_the_wrong_iteration_is_refused(self):
        """Iteration 0 must run at the base rate; annealing it is a different configuration."""
        bad = self._records([(0, self.cpa.ANNEALED_LR), (1, self.cpa.ANNEALED_LR),
                             (2, self.cpa.ANNEALED_LR)])
        with self.assertRaises(SystemExit):
            CPT.attest_anneal_took_effect(bad, declared_lr=1e-4, start=0, niter=3)

    def test_A_GLOBALLY_WRONG_BASE_RATE_IS_CAUGHT_HERE_AND_NOT_BY_THE_SIBLING(self):
        """THE DISCRIMINATING CASE, and the whole reason this is a second implementation.

        Base fits at 1e-3 instead of the engine's declared 1e-4, annealed fits correct at 1e-5. The
        record set is internally self-consistent, so a check that derives its reference from
        `max(records)` judges the wrong rate against itself and passes.
        """
        bad = self._records([(0, 1e-3), (1, self.cpa.ANNEALED_LR), (2, self.cpa.ANNEALED_LR)])

        # The sibling PASSES it -- demonstrated, not asserted from reading its source.
        sibling_base_lr = max(r["learning_rate"] for r in bad)      # exactly cpa's own :177
        self.assertEqual(sibling_base_lr, 1e-3)
        self.cpa.assert_anneal_took_effect(bad, sibling_base_lr, start=0)   # does NOT raise

        # This one refuses it, because its reference is DECLARED rather than inferred.
        with self.assertRaises(SystemExit) as ctx:
            CPT.attest_anneal_took_effect(bad, declared_lr=1e-4, start=0, niter=3)
        self.assertIn("DID NOT TAKE EFFECT", str(ctx.exception))
        self.assertIn("DECLARED", str(ctx.exception))

    def test_a_missing_declared_rate_is_refused_rather_than_derived(self):
        """Falling back to max(records) would silently reintroduce the hole above."""
        for bad_lr in (None, float("nan"), 0.0, -1e-4):
            with self.assertRaises(SystemExit) as ctx:
                CPT.attest_anneal_took_effect(self._good(), declared_lr=bad_lr, start=0, niter=3)
            self.assertIn("declared base learning rate", str(ctx.exception))

    def test_start_boundary_is_honoured(self):
        """With start=1, iterations 0 AND 1 run at the base rate."""
        recs = self._records([(0, 1e-4), (1, 1e-4), (2, self.cpa.ANNEALED_LR)])
        proof = CPT.attest_anneal_took_effect(recs, declared_lr=1e-4, start=1, niter=3)
        self.assertEqual((proof["n_fits_at_base_lr"], proof["n_fits_at_annealed_lr"]), (4, 2))

    def test_a_wrong_record_COUNT_is_reported_but_not_fatal(self):
        """Deliberate: this runs after a multi-hour GPU run, and the rates are the predeclared thing.

        A false refusal over a count whose invariance across future engine paths is unestablished
        would discard a good run's annotation. The rates fail closed; the count is surfaced.
        """
        recs = self._records([(0, 1e-4), (1, self.cpa.ANNEALED_LR)])          # 4 records, niter=3
        proof = CPT.attest_anneal_took_effect(recs, declared_lr=1e-4, start=0, niter=3)
        self.assertTrue(proof["pass"])
        self.assertEqual(proof["n_records"], 4)
        self.assertEqual(proof["expected_n_records_at_two_fits_per_iteration"], 6)
        self.assertFalse(proof["n_records_matches_two_per_iteration"])

    def test_the_recorder_captures_the_engines_declared_LR_and_start(self):
        """The attestation is only non-self-referential if the recorder actually reads the instance."""
        mc = _Leg([1.0, 2.0], [True, True], weight_reco=[1.0, 3.0])
        base = _FakeBase(mc, [1.0, 1.0], mc.weight_reco)
        base.LR = 1e-4
        base.start = 0
        rec_cls, records = CPT.install_fold_forward_recorder(type(base))
        inst = rec_cls(mc, [1.0, 1.0], mc.weight_reco)
        inst.LR, inst.start = 1e-4, 0
        inst.RunStep1(0)
        self.assertEqual(records[0]["engine_declared_LR"], 1e-4)
        self.assertEqual(records[0]["anneal_start"], 0)

    def test_the_proof_does_not_claim_to_cover_the_six_existing_products(self):
        """Scope guard: the fix must not read as retro-attestation of 2026-08-15's receipts."""
        with open(PATH) as fh:
            src = fh.read()
        self.assertIn("BOUNDED, NOT ATTESTED", src)
        self.assertIn("nothing here retro-attests them", src)


if __name__ == "__main__":
    unittest.main()
