#!/usr/bin/env python3
"""B-4 is GATED, not merely recorded.

Before 2026-07-31 `gate2_target_runtime.py` computed the w_reco-vs-w_truth telemetry, wrote its
own verdict string -- "B-4 ACTIVE ... resolve B-4 before freezing R" -- into the receipt as
`step1_class_ratio.b4_note`, and then emitted `status: PASS`. Every consumer reads `status`, not a
note, so the gate contradicted its own telemetry. Found by adversarial review.

WHY THE PREDICATE IS TESTED, NOT THE ASSERTION SITE. `b4_blocking_reason` was extracted from
`run_validate` for the same reason `step1_target_sum_matches` was: exercising it end-to-end needs
the frozen 9.9 GB dump, and a test that re-types the three conditions against a hand-built dict
proves only that the test agrees with itself -- the tautology pattern
AUDIT-FINDINGS-20260729-B.md §4 found across all 49 provenance tests. So the telemetry these cases
feed the predicate is built by the REAL producer, `fullevent_fps_dataloader
.step1_class_ratio_from_dump`, not typed out here.

NOT COVERED HERE: the matching `require`s added to `validate_gate2_target_receipt.py`. Those check
what a receipt DECLARES, and the only post-B1 receipt that could exercise them does not exist yet
-- the one on disk at g2_fullevent/gate2/final/ is pre-B1 and already fails closed at :131. They
get their end-to-end run with the Step 2 re-issue.
"""
import os
import sys
import unittest

import numpy as np

PET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)

import fullevent_fps_dataloader as fed          # noqa: E402
import gate2_target_runtime as gtr              # noqa: E402


class FakeDump(dict):
    """Minimal stand-in for an open npz: mapping access plus `.files`."""

    @property
    def files(self):
        return list(self.keys())


def dump(*, n_sig=80, n_bkg=20, n_data=60, w_reco_delta=None, drop_w_reco=False, seed=3):
    """A tiny g2-fullevent-shaped mapping carrying only what R and its telemetry read.

    `w_reco_delta`, when given, is added to w_reco so it differs from w_truth -- which is the only
    thing that makes B-4 ACTIVE.
    """
    rng = np.random.default_rng(seed)
    w_truth = (rng.random(n_sig) + 0.5).astype(np.float64)
    pass_reco = rng.random(n_sig) < 0.7
    d = FakeDump({
        "w_truth": w_truth,
        "pass_reco": pass_reco,
        "w_bkg": (rng.random(n_bkg) + 0.5).astype(np.float64),
        "pot_scale": np.asarray(0.25),
        "measured_scalars": rng.random((n_data, 4)).astype(np.float32),
    })
    if not drop_w_reco:
        d["w_reco"] = w_truth if w_reco_delta is None else w_truth + w_reco_delta
    return d, pass_reco


class B4BlocksCertification(unittest.TestCase):

    def test_inactive_does_not_block(self):
        """w_reco bit-identical to w_truth over pass_reco: R's denominator is the right one."""
        d, _ = dump()
        _, telem = fed.step1_class_ratio_from_dump(d)
        self.assertTrue(telem["b4_w_reco_vs_w_truth"]["bit_identical_over_pass_reco"])
        self.assertIsNone(gtr.b4_blocking_reason(telem))

    def test_differing_legs_no_longer_block(self):
        """POST-D1 INVERSION (2026-08-04). Differing legs used to block -- that was B-4 ACTIVE, and
        it is what stopped job 56320955. B-4 is now resolved in favour of the reco leg, so the reco
        leg carrying the reco-only MINOS efficiency correction is the CORRECT state and must pass.

        Kept as its own test rather than deleted: if someone restores the old condition, this goes
        red and names why, instead of the change looking like a silent weakening of a gate."""
        d, pass_reco = dump(w_reco_delta=None)
        delta = np.zeros(d["w_truth"].shape)
        delta[np.flatnonzero(pass_reco)[:5]] = 0.25      # 5 differing pass_reco rows
        d, _ = dump(w_reco_delta=delta)
        _, telem = fed.step1_class_ratio_from_dump(d)
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertFalse(b4["bit_identical_over_pass_reco"])
        self.assertEqual(b4["n_pass_reco_differing"], 5)
        self.assertEqual(telem["reco_leg_weight_used"], "w_reco")
        self.assertIsNone(gtr.b4_blocking_reason(telem),
                          "post-D1 a differing reco leg is the correct configuration, not a block")

    def test_truth_leg_denominator_blocks(self):
        """The INVERTED gate. What must fail closed now is a denominator built from the truth leg --
        i.e. exactly the pre-D1 behaviour. Without this the D1 change has no gate at all: the old
        condition was removed, so something has to hold the new invariant."""
        d, _ = dump()
        _, telem = fed.step1_class_ratio_from_dump(d)
        self.assertIsNone(gtr.b4_blocking_reason(telem))
        telem["reco_leg_weight_used"] = "w_truth"          # the pre-D1 configuration
        reason = gtr.b4_blocking_reason(telem)
        self.assertIsNotNone(reason, "a truth-leg denominator must not certify post-D1")
        self.assertIn("w_reco", reason)
        for bogus in (None, "", "w_bkg"):
            telem["reco_leg_weight_used"] = bogus
            self.assertIsNotNone(gtr.b4_blocking_reason(telem))

    def test_difference_outside_pass_reco_does_not_block(self):
        """The contract question is over pass_reco only, so the gate must not be over-eager.

        Without this, any dump whose w_reco differs on rejected rows would be blocked, and the
        cheapest way to make that green again is to weaken the gate.
        """
        d, pass_reco = dump()
        delta = np.zeros(d["w_truth"].shape)
        delta[np.flatnonzero(~pass_reco)] = 3.0
        d, _ = dump(w_reco_delta=delta)
        _, telem = fed.step1_class_ratio_from_dump(d)
        self.assertTrue(telem["b4_w_reco_vs_w_truth"]["bit_identical_over_pass_reco"])
        self.assertIsNone(gtr.b4_blocking_reason(telem))

    def test_absent_w_reco_now_raises_rather_than_reporting(self):
        """Post-D1 this fails EARLIER and harder. w_reco is no longer diagnostic -- it IS R's
        denominator -- so its absence cannot be recorded and passed downstream; there is nothing to
        build R from. dump_pointcloud_inputs.py:299 requires the array."""
        d, _ = dump(drop_w_reco=True)
        with self.assertRaises(ValueError) as cm:
            fed.step1_class_ratio_from_dump(d)
        self.assertIn("w_reco", str(cm.exception))

    def test_gate_still_blocks_a_present_in_dump_false_telemetry(self):
        """The predicate keeps its own defence. The loader can no longer emit `present_in_dump:
        False`, but receipts written before D1 can, and re-validating one of those must not pass on
        a denominator that was never corroborated."""
        stale = {"reco_leg_weight_used": "w_reco",
                 "b4_w_reco_vs_w_truth": {"present_in_dump": False,
                                          "verdict": "w_reco absent -- contract violation"}}
        reason = gtr.b4_blocking_reason(stale)
        self.assertIsNotNone(reason)
        self.assertIn("unanswerable", reason.lower())

    def test_unasked_question_blocks(self):
        """check_w_reco=False omits the block entirely; the gate must not read that as a pass."""
        d, _ = dump()
        _, telem = fed.step1_class_ratio_from_dump(d, check_w_reco=False)
        self.assertNotIn("b4_w_reco_vs_w_truth", telem)
        self.assertIsNotNone(gtr.b4_blocking_reason(telem))
        self.assertIsNotNone(gtr.b4_blocking_reason({}))
        self.assertIsNotNone(gtr.b4_blocking_reason(None))


class TheGateActuallyCallsThePredicate(unittest.TestCase):
    """A predicate nothing calls is the defect one level up. run_validate needs the frozen dump, so
    what is checked is that the assertion site delegates rather than carrying an inline copy that
    could drift away from the tested one."""

    def test_run_validate_delegates_to_b4_blocking_reason(self):
        import inspect
        src = inspect.getsource(gtr.run_validate)
        self.assertIn("b4_blocking_reason(", src)
        self.assertNotIn("bit_identical_over_pass_reco", src,
                         "run_validate re-inlined the B-4 conditions; the tested predicate and "
                         "the executed one have diverged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
