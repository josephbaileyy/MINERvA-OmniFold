#!/usr/bin/env python3
"""Z's contract constants, the boundary registry's refusal semantics, and the LightGBM probe.

THE TRIPWIRE. `AllScientificBoundariesAreWithheld` fails the day anybody declares one of Z's
acceptance boundaries. That is deliberate and it is the point: Joseph accepted the baseline at
`10c24678` "with unresolved scientific acceptance criteria expressly withheld", so a declaration is
a change of scientific state and it must not be able to arrive as a quiet constant. If you are here
because this test failed, the question is not how to fix the test -- it is which record approved
the number.

Every guard below is tested in BOTH directions: it fires on the defect AND stays silent on the
clean case. A one-directional check waves the other through, which this repository has paid for.
"""
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

import z_contract as zc                 # noqa: E402
import z_reproducibility as zr          # noqa: E402
import p4_lib                           # noqa: E402
import adopt_unified_5d as _adopt       # noqa: E402


def _probe_lightgbm() -> bool:
    import importlib.util
    return importlib.util.find_spec("lightgbm") is not None


# Evaluated once at import so it can gate a decorator. Its VALUE is the finding: absent here.
LIGHTGBM_AVAILABLE = _probe_lightgbm()


class AllScientificBoundariesAreWithheld(unittest.TestCase):
    """The state Joseph's authorization fixed. Any change here is a scientific change."""

    def test_no_boundary_is_declared_at_this_baseline(self):
        declared = zc.declared_boundaries()
        self.assertEqual(
            declared, {},
            "A Z acceptance boundary has been DECLARED. That is a scientific change, not a code "
            "change: name the record that approved it and update this test deliberately.")

    def test_the_four_named_boundaries_all_exist_and_are_withheld(self):
        for key in ("null_epsilon", "cause3_agg", "cause3_med", "cause3_corr"):
            with self.subTest(boundary=key):
                b = zc.boundary(key)
                self.assertFalse(b.is_declared)
                self.assertTrue(b.reason and b.reason.strip())

    def test_using_a_withheld_boundary_raises_rather_than_defaulting(self):
        b = zc.boundary("null_epsilon")
        with self.assertRaises(zc.BoundaryWithheld):
            _ = b.value

    def test_describe_is_safe_on_a_withheld_boundary(self):
        # A receipt must be able to record a withheld boundary without tripping over it.
        d = zc.boundary("cause3_agg").describe()
        self.assertEqual(d["status"], "WITHHELD")
        self.assertIsNone(d["value"])

    def test_an_unknown_boundary_name_fails_rather_than_returning_a_default(self):
        with self.assertRaises(zc.ZContractError):
            zc.boundary("cause3_whatever")


class DeclaringABoundaryRequiresItsApproval(unittest.TestCase):
    """The positive direction: declaration works, but only with provenance and a finite value."""

    def test_a_declared_boundary_yields_its_value(self):
        b = zc.Boundary.declared("t", 0.01, "TEST-RECORD §1")
        self.assertTrue(b.is_declared)
        self.assertEqual(b.value, 0.01)
        self.assertEqual(b.describe()["status"], "DECLARED")

    def test_declaration_without_provenance_is_refused(self):
        for bad in ("", "   ", None):
            with self.subTest(provenance=bad):
                with self.assertRaises(zc.ZContractError):
                    zc.Boundary.declared("t", 0.01, bad)

    def test_declaration_of_a_non_finite_value_is_refused(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=bad):
                with self.assertRaises(zc.ZContractError):
                    zc.Boundary.declared("t", bad, "TEST-RECORD §1")

    def test_withholding_without_a_reason_is_refused(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary.withheld("t", "")


class ConstantsAreImportedNotRetyped(unittest.TestCase):
    """§1.2. A retyped band list is a second implementation of a predicate."""

    def test_the_band_sets_are_the_owning_modules_objects(self):
        self.assertEqual(tuple(zc.VERT_BANDS), tuple(_adopt.VERT_BANDS))
        self.assertEqual(tuple(zc.LATERAL_BANDS), tuple(p4_lib.BANDS))

    def test_the_measured_cardinalities(self):
        self.assertEqual(zc.N_VERT, 13)
        self.assertEqual(zc.N_LATERAL, 5)
        self.assertEqual(zc.N_BANDS_TOTAL, 45)

    def test_the_residual_count_is_derived_not_listed(self):
        # If someone retypes R as a literal list, this stops agreeing with the subtraction.
        self.assertEqual(zc.N_RESIDUAL, 45 - len(_adopt.VERT_BANDS) - len(p4_lib.BANDS))
        self.assertEqual(zc.N_RESIDUAL, 27)

    def test_the_validated_p4_reproduction_path_is_imported_unchanged(self):
        self.assertEqual(zc.P4_REPRO_RTOL_PER_BIN, p4_lib.REPRO_RTOL_PER_BIN)
        self.assertEqual(zc.P4_REPRO_RTOL_INTEGRAL, p4_lib.REPRO_RTOL_INTEGRAL)


class TheBandPartitionGateFiresInBothDirections(unittest.TestCase):
    def setUp(self):
        self.V = list(zc.VERT_BANDS)
        self.A = list(zc.LATERAL_BANDS)
        self.R = [f"residual_{i}" for i in range(zc.N_RESIDUAL)]

    def test_the_real_partition_passes(self):
        out = zc.check_band_partition(self.V, self.R, self.A)
        self.assertEqual(out["n_total"], 45)
        self.assertEqual(out["n_vert"], 13)
        self.assertEqual(out["n_residual"], 27)
        self.assertEqual(out["n_lateral"], 5)

    def test_an_overlap_between_V_and_R_is_caught(self):
        R = list(self.R[:-1]) + [self.V[0]]
        with self.assertRaises(zc.ZContractError) as cm:
            zc.check_band_partition(self.V, R, self.A)
        self.assertIn("overlap", str(cm.exception))

    def test_a_missing_vertical_band_is_caught(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V[:-1], self.R + ["extra"], self.A)

    def test_a_short_residual_set_is_caught_even_with_V_and_A_correct(self):
        # The count leg has to bite on its own: V and A are exactly right here.
        with self.assertRaises(zc.ZContractError) as cm:
            zc.check_band_partition(self.V, self.R[:-1], self.A)
        self.assertIn("45", str(cm.exception))

    def test_a_duplicate_inside_one_set_is_caught(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V, self.R[:-1] + [self.R[0]], self.A)


class TheLightGBMProbeRefusesWhatItCannotVerify(unittest.TestCase):
    """Joseph asked for the config 'after checking the actual LightGBM backend and version'.

    Checked: absent from this interpreter, and unpinned anywhere in the repository. So the overlay
    refuses. The positive direction is exercised with a synthetic probe, because a real one is not
    available here and a test that skipped would leave the accepting path unexercised.
    """

    def test_the_probe_reports_the_backend_honestly(self):
        p = zr.probe_backend()
        self.assertIsInstance(p, zr.BackendProbe)
        if not p.available:
            self.assertIsNotNone(p.error)
            self.assertTrue(all(v is None for v in p.recognised_knobs.values()))

    def test_an_absent_backend_refuses_the_overlay(self):
        absent = zr.BackendProbe(available=False, error="ImportError: no module named lightgbm",
                                 recognised_knobs={k: None for k in zr.Z_REPRO_KNOBS})
        with self.assertRaises(zc.ZContractError) as cm:
            zr.z_lgbm_overlay(absent)
        self.assertIn("REFUSED", str(cm.exception))

    def test_an_unverified_knob_refuses_even_when_the_backend_imports(self):
        # The dangerous middle case: LightGBM is there, but we cannot confirm a parameter name.
        # An unrecognised LightGBM parameter is SILENTLY IGNORED, so accepting here would produce
        # a run that reports itself pinned while its reduction order still varies.
        knobs = {k: True for k in zr.Z_REPRO_KNOBS}
        knobs["deterministic"] = None
        partial = zr.BackendProbe(available=True, version="4.5.0", recognised_knobs=knobs)
        with self.assertRaises(zc.ZContractError) as cm:
            zr.z_lgbm_overlay(partial)
        self.assertIn("deterministic", str(cm.exception))

    def test_a_fully_verified_backend_yields_the_overlay(self):
        good = zr.BackendProbe(available=True, version="4.5.0",
                               recognised_knobs={k: True for k in zr.Z_REPRO_KNOBS})
        out = zr.z_lgbm_overlay(good)
        self.assertEqual(set(out["params"]), set(zr.Z_REPRO_KNOBS))
        self.assertEqual(out["params"]["num_threads"], 1)
        self.assertTrue(out["declares_divergence_from_historical_chain"])
        self.assertTrue(out["rationale"]["num_threads"])

    def test_the_overlay_does_not_touch_the_production_estimator(self):
        """Joseph: 'Preserve all existing non-Z defaults and validated reproduction paths.'

        Checked STRUCTURALLY, by parsing the module, rather than by scanning its text. The first
        version of this test searched the source for `core.make_estimators` and failed on the
        docstring's own citation of `omnifold_nn_core.make_estimators:143-148` -- a substring
        search matching prose, which is this repository's catalogued both-ways failure. An AST
        walk asks the question in the language the property lives in.
        """
        import ast
        with open(zr.__file__, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())

        imported, mutations = set(), []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Attribute) and tgt.attr == "make_estimators":
                        mutations.append("assignment to .make_estimators")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "setattr":
                mutations.append("setattr(...)")

        self.assertNotIn("omnifold_nn_core", imported,
                         "the Z overlay must not import the production estimator module")
        self.assertEqual(mutations, [],
                         f"the Z overlay must not rebind production attributes: {mutations}")

    def test_importing_the_overlay_does_not_pull_in_the_production_estimator(self):
        """The runtime half: a monkeypatch needs the module loaded, so absence is evidence."""
        import subprocess
        code = ("import sys; sys.path.insert(0, %r); import z_reproducibility; "
                "print('omnifold_nn_core' in sys.modules)" % os.path.dirname(zr.__file__))
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "False", out.stdout)

    @unittest.skipUnless(LIGHTGBM_AVAILABLE,
                         "lightgbm absent from this interpreter -- which is itself the finding "
                         "recorded in z_reproducibility's docstring")
    def test_the_production_defaults_are_what_they_always_were(self):
        import omnifold_nn_core as core
        clf1, _, _ = core.make_estimators("lgbm", 3, seed=42)
        params = clf1.get_params()
        self.assertEqual(params["n_estimators"], 100)
        self.assertEqual(params["num_leaves"], 8)
        self.assertEqual(params["random_state"], 42)

    def test_the_transferred_evidence_is_labelled_and_is_not_a_boundary(self):
        ev = zr.transferred_repro_evidence()
        self.assertEqual(ev["class"], "TRANSFERRED")
        self.assertIn("NOT Z", ev["subject"])
        self.assertNotIn("epsilon", ev)
        # It must not be reachable through the boundary registry.
        self.assertNotIn("transferred", zc.Z_BOUNDARIES)


# Entry point at the END of the file, so running this file collects EVERY class above. A
# `unittest.main()` placed mid-file leaves later classes undefined and still exits zero.
if __name__ == "__main__":
    unittest.main(verbosity=2)
