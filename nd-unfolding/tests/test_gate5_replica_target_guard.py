"""Gate 5, BLOCKED: the replica path needs a loader change that breaks two live Gate-2 bindings.

This file is a SPECIFICATION plus the measurement that blocks it. The behavioural tests are skipped
on purpose, with the blocker named, so the requirement is recorded and the suite stays honest rather
than green-by-omission.

WHAT THE REPLICA PATH NEEDS. The adopted architecture (PREDECLARATION-20260813-gate5-coherent-
replicas-n50.md) is two jobs per replica: a negweight-refined target built PER REPLICA under ROOT,
then that replica's TF training job consuming it, because no Perlmutter interpreter carries both.

WHY IT CANNOT BE BUILT AS SPECIFIED. `build_fullevent_loaders` refuses EVERY precomputed target when
`bootstrap_seed` is set (`fullevent_fps_dataloader.py:1461`):

    "a precomputed target is the NOMINAL target; a bootstrap replica draws its own data/background
     factors, so consuming the nominal array here would silently give every replica the nominal's
     measured weights and collapse the measured-side variance (fail closed)."

That refusal is CORRECT for the nominal array and it also refuses a replica's own target, so a
replica has no way to consume one. Fixing it means distinguishing the two cases inside that
function -- i.e. editing `fullevent_fps_dataloader.py`.

THE BLOCKER, MEASURED 2026-08-13 with `docs/orchestration/verify_hash_bindings.py`. The
predeclaration states the loader is "NOT pinned", which is true of the Gate-4 code gate's 19 pins and
FALSE overall. Editing it broke TWO live bindings:

    MISMATCH nd-unfolding/pet/fullevent_fps_dataloader.py
      want 57f33f87b07e0c6b9bd27a8c56f8013acf9863c72f80f1c01de556ad09f97117
      from nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
    MISMATCH nd-unfolding/pet/fullevent_fps_dataloader.py
      want 57f33f87b07e0c6b9bd27a8c56f8013acf9863c72f80f1c01de556ad09f97117
      from nd-unfolding/pet/run_gate2_target_validator.sh

THE SECOND ONE IS THE CIRCULAR PART AND IT IS THE REASON THIS IS NOT A ONE-LINE EDIT.
`run_gate2_target_validator.sh` carries an `EXPECTED_*_SHA` guard on the loader, so it REFUSES TO RUN
against a modified loader. The per-replica target build has to go through that validator path. So the
loader edit that enables replicas simultaneously disables the tool that must build their targets.
Sequencing cannot dodge it: whichever order you choose, one of the two is broken while the other runs.

The edit was written, tested green (7 tests, both directions), and REVERTED on this measurement. The
loader is back at `57f33f87...` and `verify_hash_bindings.py` reports no loader mismatch. The design
below is what should be built once the binding question is decided by the gate's owner.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pet"))
import fullevent_fps_dataloader as fed          # noqa: E402  (login-safe: numpy only)

BLOCKER = ("Gate 5 loader change reverted: it breaks G2_GATE2_TARGET_RUNTIME_RECEIPT.json and the "
           "EXPECTED_*_SHA guard in run_gate2_target_validator.sh, which is the tool that must build "
           "each replica's target. Needs a Gate-2 binding decision from the gate's owner.")


class ReplicaTargetProvenance(unittest.TestCase):
    """This half needs NO loader change and is live now: the provenance function itself."""

    def test_assert_refined_target_is_replica_is_two_sided(self):
        """The function with ZERO production callers. Gate 5 is the path that must call it, and the
        replica DRIVER is where it belongs -- provenance is the driver's job, structure the
        loader's, per fullevent_fps_dataloader.py:1457-1460."""
        self.assertTrue(fed.assert_refined_target_is_replica({"bootstrap_seed": 7},
                                                             bootstrap_seed=7))
        with self.assertRaises(ValueError):                      # the NOMINAL target
            fed.assert_refined_target_is_replica({"bootstrap_seed": None}, bootstrap_seed=7)
        with self.assertRaises(ValueError):                      # ANOTHER replica's target
            fed.assert_refined_target_is_replica({"bootstrap_seed": 3}, bootstrap_seed=7)
        with self.assertRaises(ValueError):                      # no metadata at all
            fed.assert_refined_target_is_replica({}, bootstrap_seed=7)

    def test_that_battery_is_not_vacuous(self):
        """A stub returning True unconditionally must fail the battery above, so its three raises
        are load-bearing rather than incidental."""
        raised = 0
        for meta in ({"bootstrap_seed": None}, {"bootstrap_seed": 3}, {}):
            try:
                (lambda m, *, bootstrap_seed: True)(meta, bootstrap_seed=7)
            except ValueError:
                raised += 1
        self.assertEqual(raised, 0)

    def test_the_current_refusal_is_present_and_absolute(self):
        """Documents the state being blocked ON, so a future edit that relaxes it silently is
        visible here. The loader today refuses a precomputed target under ANY bootstrap seed."""
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pet",
                               "fullevent_fps_dataloader.py"), encoding="utf-8").read()
        i = src.index("if precomputed_target is not None:")
        window = src[i:i + 1400]
        self.assertIn("if bootstrap_seed is not None:", window)
        self.assertIn("collapse the measured-side variance (fail closed)", window)
        self.assertNotIn("precomputed_target_replica_seed", window,
                         "if this fires, the Gate-5 loader change has landed -- unskip the tests "
                         "below and re-run verify_hash_bindings.py")


@unittest.skip(BLOCKER)
class ReplicaTargetGuardSpecification(unittest.TestCase):
    """The design, recorded so it is not re-derived. Unskip when the binding question is settled.

    `build_fullevent_loaders` gains `precomputed_target_replica_seed=None`, and the refusal splits:
      * seed not named            -> the ORIGINAL refusal, verbatim (fails closed by default)
      * named but != bootstrap_seed -> refuse: one replica's measured weights with another's MC draw
      * named and == bootstrap_seed -> PERMIT, and record both seeds in meta['target']
    The caller may only name it after binding the array to its receipt with
    `assert_refined_target_is_replica`, keeping provenance in the driver and structure in the loader.
    """

    def test_default_still_refuses(self):
        self.fail(BLOCKER)

    def test_mismatched_seed_refuses(self):
        self.fail(BLOCKER)

    def test_matching_seed_permits_and_records_both_seeds(self):
        self.fail(BLOCKER)


if __name__ == "__main__":
    unittest.main(verbosity=2)
