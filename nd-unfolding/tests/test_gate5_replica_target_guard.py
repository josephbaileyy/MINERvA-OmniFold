"""Gate 5: the precomputed-target guard must tell a replica's OWN target from the nominal's.

WHY THE GUARD CHANGED. Before 2026-08-13 `build_fullevent_loaders` refused EVERY precomputed target
whenever `bootstrap_seed` was set. Correct for the nominal array, and it made Gate 5's adopted
architecture impossible: the predeclaration requires a negweight-refined target built PER REPLICA
under ROOT, then consumed by that replica's TF training job, because no Perlmutter interpreter carries
both. Refusing every precomputed target left a replica no way to consume its own.

RELAXING A FAIL-CLOSED GUARD IS THE CHANGE MOST ABLE TO SILENTLY STOP PROTECTING, so every case here
is asserted in BOTH directions -- the paths that must still REFUSE and the one that must now be
PERMITTED -- and the behavioural cases run against a real synthetic dump rather than reading source.

These are the tests that were committed SKIPPED at `c06f2b4` as a specification, when the change was
blocked. Joseph decided the blocker on 2026-08-13 (~02:25 EDT): re-run Gate 2 and gate on the new
weights being BIT-IDENTICAL to the archived ones, rather than re-digesting the pin and arguing the
branch is inert. So they are live now. The bit-identity run is what actually establishes inertness on
the nominal path; these tests establish the guard's behaviour on the replica path.
"""
import os
import sys
import tempfile
import unittest

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "pet"))
sys.path.insert(0, os.path.join(_HERE, ".."))                 # pet_bootstrap
sys.path.insert(0, os.path.join(_HERE, "..", "..", "omnifold_nn"))  # vendored engine


def _engine_importable():
    """`build_fullevent_loaders` constructs a DataLoader at :1336, BEFORE the target guard at :1461,
    and `omnifold/__init__.py` imports MultiFold and PET -- so reaching the guard needs TensorFlow.
    Off-cluster that fails (Mac TF 2.16 / Keras 3 against the vendored Keras-2 net), so the
    behavioural cases below are CLUSTER-ONLY, exactly like test_fullevent_gate2.py and
    test_gate2_target_runtime.py. They SKIP with a reason here rather than passing vacuously."""
    try:
        import omnifold.dataloader  # noqa: F401
        import pet_bootstrap        # noqa: F401
        return True
    except Exception:
        return False


ENGINE = _engine_importable()
import fullevent_fps_dataloader as fed          # noqa: E402  (login-safe: numpy only)
import make_synthetic_g2_fullevent as syn       # noqa: E402
import fullevent_dump_contract as fdc           # noqa: E402


def synthetic(td, name="G2.npz", **over):
    """A contract-valid g2-fullevent-v1 fixture, written through the same gates a real dump is.
    Mirrors test_fullevent_schema.synthetic rather than reinventing it."""
    kw = dict(n_sig=600, n_data=200, n_bkg=80, tokens=6, seed=4,
              fingerprint="pet-fullevent-fps-v1")
    kw.update(over)
    arrays = syn.build(**kw)
    path = os.path.join(td, name)
    fdc.write_fullevent_npz_atomic(path, arrays)
    return path, arrays


def _target_npy(td, n_rows, name="target.npy"):
    """A structurally valid refined target: non-negative, finite, positive sum, right row count."""
    p = os.path.join(td, name)
    np.save(p, np.full(n_rows, 0.5, dtype=np.float64))
    return p


class ReplicaTargetProvenance(unittest.TestCase):
    """The provenance half, which needs no loader change: `assert_refined_target_is_replica`.

    This is the function that had ZERO production callers until Gate 5 -- specified, implemented,
    tested, and enforced by nothing. Provenance belongs to the DRIVER and structure to the loader,
    per the division stated at fullevent_fps_dataloader.py:1457-1460."""

    def test_it_is_two_sided(self):
        self.assertTrue(fed.assert_refined_target_is_replica({"bootstrap_seed": 7},
                                                             bootstrap_seed=7))
        with self.assertRaises(ValueError):                      # the NOMINAL target
            fed.assert_refined_target_is_replica({"bootstrap_seed": None}, bootstrap_seed=7)
        with self.assertRaises(ValueError):                      # ANOTHER replica's target
            fed.assert_refined_target_is_replica({"bootstrap_seed": 3}, bootstrap_seed=7)
        with self.assertRaises(ValueError):                      # no metadata at all
            fed.assert_refined_target_is_replica({}, bootstrap_seed=7)

    def test_that_battery_is_not_vacuous(self):
        """An always-True stub must raise nothing, so the three raises above are load-bearing."""
        raised = 0
        for meta in ({"bootstrap_seed": None}, {"bootstrap_seed": 3}, {}):
            try:
                (lambda m, *, bootstrap_seed: True)(meta, bootstrap_seed=7)
            except ValueError:
                raised += 1
        self.assertEqual(raised, 0)


@unittest.skipUnless(ENGINE, "cluster-only: reaching the target guard needs the vendored omnifold "
                             "engine (TensorFlow) and pet_bootstrap; run under tensorflow/2.15.0")
class ReplicaTargetGuardBehaviour(unittest.TestCase):
    """The three cases, exercised through `build_fullevent_loaders` against a real dump."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.path, cls.arrays = synthetic(cls._td.name)
        cls.n_rows = int(np.asarray(cls.arrays["measured_pc"]).shape[0]) + \
            int(np.asarray(cls.arrays["w_bkg"]).shape[0])
        cls.target = _target_npy(cls._td.name, cls.n_rows)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def _build(self, **kw):
        return fed.build_fullevent_loaders(self.path, enforce_fps_edges=False,
                                           precomputed_target=self.target, **kw)

    def test_default_still_refuses_a_precomputed_target_under_a_bootstrap_seed(self):
        """The ORIGINAL protection. A caller that names no seed must get the original refusal, so the
        nominal array can never reach a replica by omission."""
        with self.assertRaises(ValueError) as cm:
            self._build(bootstrap_seed=11)
        self.assertIn("collapse the measured-side variance", str(cm.exception))

    def test_mismatched_seed_is_refused(self):
        """Pairing replica A's measured weights with replica B's MC draw must be fatal, not noted."""
        with self.assertRaises(ValueError) as cm:
            self._build(bootstrap_seed=11, precomputed_target_replica_seed=12)
        msg = str(cm.exception)
        self.assertIn("another's MC draw", msg)
        self.assertIn("11", msg)
        self.assertIn("12", msg)

    def test_matching_seed_is_permitted_and_records_both_seeds(self):
        """The path Gate 5 needs. It must be allowed AND the receipt must be able to say which
        target was consumed -- a run that cannot attest that is the defect this campaign keeps
        finding."""
        data, mc, imc, cr, cg, meta = self._build(bootstrap_seed=11,
                                                 precomputed_target_replica_seed=11)
        tgt = meta["target"]
        self.assertEqual(tgt["precomputed_target_replica_seed"], 11)
        self.assertEqual(tgt["bootstrap_seed"], 11)
        self.assertFalse(tgt["refinement_invoked"],
                         "a consumed precomputed target must not also re-derive the refinement")

    def test_the_nominal_path_is_untouched(self):
        """The change must be invisible with no bootstrap seed -- which is the claim the Gate-2
        bit-identity re-run exists to establish on real data. Here: it still loads, and the receipt
        records None rather than omitting the fields."""
        data, mc, imc, cr, cg, meta = self._build()
        tgt = meta["target"]
        self.assertIsNone(tgt["precomputed_target_replica_seed"])
        self.assertIsNone(tgt["bootstrap_seed"])


class GuardShapeRegression(unittest.TestCase):
    """Source-level assertions on the SHAPE of the guard, because a behavioural test can pass
    against a guard that has been weakened from equality to mere presence."""

    @classmethod
    def setUpClass(cls):
        cls.src = open(os.path.join(_HERE, "..", "pet", "fullevent_fps_dataloader.py"),
                       encoding="utf-8").read()

    def test_permission_is_conditional_on_equality_not_presence(self):
        self.assertIn("if int(precomputed_target_replica_seed) != int(bootstrap_seed):", self.src,
                      "a presence-only check would let any named seed through")

    def test_the_original_refusal_text_survives(self):
        self.assertIn("collapse the measured-side variance (fail closed)", self.src,
                      "that sentence names the physics failure; losing it loses the reason")

    def test_the_default_is_none_so_omission_refuses(self):
        import inspect
        sig = inspect.signature(fed.build_fullevent_loaders)
        self.assertIn("precomputed_target_replica_seed", sig.parameters)
        self.assertIsNone(sig.parameters["precomputed_target_replica_seed"].default)


if __name__ == "__main__":
    unittest.main(verbosity=2)
