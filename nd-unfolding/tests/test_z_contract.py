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
from unittest import mock

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


class TheInvariantHoldsOnEveryConstructionPath(unittest.TestCase):
    """Review finding 1. The classmethods were the polite path; the dataclass ctor was the door."""

    def test_the_raw_constructor_cannot_mint_a_value_without_provenance(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary("null_epsilon", 1.0, None, None)

    def test_the_raw_constructor_cannot_mint_a_withheld_boundary_without_a_reason(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary("null_epsilon", None, None, None)

    def test_a_boundary_cannot_be_both_declared_and_withheld(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary("t", 1.0, "REC", "and also withheld")

    def test_a_withheld_boundary_cannot_carry_provenance(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary("t", None, "REC", "reason")

    def test_dataclasses_replace_also_goes_through_the_invariant(self):
        import dataclasses
        good = zc.Boundary.declared("t", 0.5, "REC")
        with self.assertRaises(zc.ZContractError):
            dataclasses.replace(good, provenance=None)

    def test_declared_with_no_value_is_refused_clearly(self):
        with self.assertRaises(zc.ZContractError):
            zc.Boundary.declared("t", None, "REC")

    def test_ordinary_unpickling_does_NOT_call_post_init_so_setstate_does(self):
        """⚠ ROUND-3 NONBLOCKING 1. The docstring claimed `__post_init__` covered unpickling.

        Measured: it does not. `pickle` restores state directly and never calls `__init__`, and a
        payload whose provenance had been blanked came back with `.value` usable. Rather than
        withdraw the claim and leave the gap, `__setstate__` re-runs the invariant -- so the test
        for the claim is the counterexample that disproved it.
        """
        import pickle
        good = zc.Boundary.declared("t", 0.5, "REC")
        self.assertEqual(pickle.loads(pickle.dumps(good)).value, 0.5)
        tampered = pickle.dumps(good).replace(b"REC", b"   ")
        with self.assertRaises(zc.ZContractError):
            pickle.loads(tampered)

    def test_a_withheld_boundary_survives_a_pickle_round_trip_and_stays_withheld(self):
        import pickle
        w = pickle.loads(pickle.dumps(zc.Z_BOUNDARIES["null_epsilon"]))
        self.assertFalse(w.is_declared)
        with self.assertRaises(zc.BoundaryWithheld):
            w.value

    def test_copy_and_deepcopy_still_work(self):
        """`__setstate__` must not break the ordinary paths it sits on."""
        import copy
        good = zc.Boundary.declared("t", 0.5, "REC")
        self.assertEqual(copy.deepcopy(good), good)
        self.assertEqual(copy.copy(good), good)


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
        self.INV = self.V + self.R + self.A

    def test_the_real_partition_passes(self):
        out = zc.check_band_partition(self.V, self.R, self.A, self.INV)
        self.assertEqual(out["n_total"], 45)
        self.assertEqual(out["n_vert"], 13)
        self.assertEqual(out["n_residual"], 27)
        self.assertEqual(out["n_lateral"], 5)

    def test_an_overlap_between_V_and_R_is_caught(self):
        R = list(self.R[:-1]) + [self.V[0]]
        with self.assertRaises(zc.ZContractError) as cm:
            zc.check_band_partition(self.V, R, self.A, self.INV)
        self.assertIn("overlap", str(cm.exception))

    def test_a_missing_vertical_band_is_caught(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V[:-1], self.R + ["extra"], self.A, self.INV)

    def test_a_short_residual_set_is_caught_even_with_V_and_A_correct(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V, self.R[:-1], self.A, self.INV)

    def test_a_duplicate_inside_one_set_is_caught(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V, self.R[:-1] + [self.R[0]], self.A, self.INV)

    def test_INVENTED_residual_names_no_longer_pass(self):
        """Review finding 6, verbatim: correct V and A plus 27 invented names used to pass."""
        invented = [f"invented_{i}" for i in range(zc.N_RESIDUAL)]
        with self.assertRaises(zc.ZContractError) as cm:
            zc.check_band_partition(self.V, invented, self.A, self.INV)
        self.assertIn("exhaustive", str(cm.exception))

    def test_a_band_in_the_partition_but_absent_from_the_inventory_is_caught(self):
        inv = self.V + self.R[:-1] + self.A          # inventory is missing one residual band
        with self.assertRaises(zc.ZContractError) as cm:
            zc.check_band_partition(self.V, self.R, self.A, inv)
        self.assertIn("absent from the support-family", str(cm.exception))

    def test_an_empty_inventory_is_refused_rather_than_vacuously_satisfied(self):
        with self.assertRaises(zc.ZContractError):
            zc.check_band_partition(self.V, self.R, self.A, [])

    def test_the_inventory_is_a_required_argument(self):
        with self.assertRaises(TypeError):
            zc.check_band_partition(self.V, self.R, self.A)


class LGBM45Table:
    """Shaped like LightGBM 4.5.0's PYTHON accessor: the canonical name is PREPENDED to its aliases.

    ⚠ TWO ROUNDS OF FIXTURE DEFECTS, both of the same kind -- a fixture agreeing with my code
    rather than with the world, so the control it feeds could not fail.

      * round 2's invented an alias for EVERY parameter, so nothing was alias-free and finding 2
        was invisible.
      * round 3's gave alias-free parameters `[]`. That is the C++ JSON dump's shape, but the
        Python accessor prepends the canonical name, so upstream returns `[name]`. Measured
        against a source-shaped table with three alias-free parameters, the control reported
        UNAVAILABLE and silently did not run.

    `deterministic` and `force_row_wise` are alias-free upstream and are alias-free here;
    `is_unbalance` is an alias-free parameter that is NOT one of Z's knobs, so the control has an
    independent name to choose.
    """

    _dump = {
        "num_leaves": ["num_leaves", "num_leaf", "max_leaves", "max_leaf", "max_leaf_nodes"],
        "num_threads": ["num_threads", "num_thread", "nthread", "nthreads", "n_jobs"],
        "learning_rate": ["learning_rate", "shrinkage_rate", "eta"],
        "deterministic": ["deterministic"],
        "force_row_wise": ["force_row_wise"],
        "is_unbalance": ["is_unbalance"],
    }

    @classmethod
    def _get_all_param_aliases(cls):
        return {k: list(v) for k, v in cls._dump.items()}

    @classmethod
    def get(cls, name):
        return {name} | set(cls._dump.get(name, []))


class RawDumpTable(LGBM45Table):
    """The other shape: the C++ `LGBM_DumpParamAliases` JSON, where alias-free means `[]`.

    Both shapes are in play and this module cannot verify from here which accessor answers on the
    campaign build, so the control must give the same verdict on either.
    """

    @classmethod
    def _get_all_param_aliases(cls):
        return {k: [a for a in v if a != k] for k, v in cls._dump.items()}


def probe_against(table, version="4.5.0"):
    """Run the real `probe_backend` against a stand-in backend exposing `table`."""
    import types
    fake = types.ModuleType("lightgbm")
    fake.__version__ = version
    fake.basic = types.SimpleNamespace(_ConfigAliases=table)
    with mock.patch.dict(sys.modules, {"lightgbm": fake}):
        return zr.probe_backend()


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

    def test_an_EMPTY_recognition_map_refuses(self):
        """Review finding 5: iterating the probe's own dict meant an empty one had no dissent."""
        empty = zr.BackendProbe(available=True, version="4.5.0", recognised_knobs={})
        with self.assertRaises(zc.ZContractError) as cm:
            zr.z_lgbm_overlay(empty)
        for knob in zr.Z_REPRO_KNOBS:
            self.assertIn(knob, str(cm.exception))

    def test_a_backend_reporting_no_version_refuses(self):
        anon = zr.BackendProbe(available=True, version=None,
                               recognised_knobs={k: True for k in zr.Z_REPRO_KNOBS})
        with self.assertRaises(zc.ZContractError) as cm:
            zr.z_lgbm_overlay(anon)
        self.assertIn("version", str(cm.exception))

    def test_a_build_with_no_READABLE_table_is_unverified_rather_than_certified(self):
        """An echoing `get()` and no table is the shape both broken methods were built on."""
        class Echo:
            @staticmethod
            def get(name):
                return {name}

        p = probe_against(Echo)
        self.assertTrue(p.available)
        self.assertIn("no readable parameter table", p.error or "")
        self.assertTrue(all(v is None for v in p.recognised_knobs.values()))
        with self.assertRaises(zc.ZContractError):
            zr.z_lgbm_overlay(p)

    def test_ALIAS_FREE_parameters_are_recognised(self):
        """⚠ ROUND-3 FINDING 2, verbatim, and the reason the previous method was wrong.

        LightGBM 4.5.0 defines `deterministic` and `force_row_wise` with EMPTY alias lists, so
        `_ConfigAliases.get(name)` returns `{name}` for them -- byte-identical to what it returns
        for a name that does not exist. The `get(name) != {name}` method therefore marked two of
        Z's three knobs unrecognised and the overlay refused a perfectly valid configuration.

        This fixture is shaped like the real table, alias-free entries and all.
        """
        p = probe_against(LGBM45Table)
        self.assertIsNone(p.error)
        self.assertEqual(p.recognised_knobs,
                         {"deterministic": True, "force_row_wise": True, "num_threads": True})
        self.assertEqual(zr.z_lgbm_overlay(p)["backend"]["version"], "4.5.0")

    def test_the_alias_free_CONTROL_is_run_and_is_chosen_from_the_table(self):
        """The control that would have caught finding 2, and it is not a name hard-coded here.

        Naming an alias-free parameter in this file would only be true of the version I guessed;
        deriving it from the table keeps the control honest across versions. It also prefers a
        parameter that is NOT one of Z's knobs, so it asks an independent question.
        """
        p = probe_against(LGBM45Table)
        af = p.controls["alias_free"]
        self.assertTrue(af["got"])
        self.assertTrue(af["independent_of_Z_knobs"])
        self.assertNotIn(af["name"], zr.Z_REPRO_KNOBS)
        self.assertEqual(p.controls["table_source"],
                         "_ConfigAliases._get_all_param_aliases()")

    def test_the_control_RUNS_on_the_source_shape_where_alias_free_means_name_alone(self):
        """⚠ ROUND-4 FINDING 2, verbatim. The control silently stopped running.

        The Python accessor prepends the canonical name, so an alias-free parameter is `[name]`
        and never `[]`. Round 3 tested `not aliases`, which is only the JSON dump's shape.
        Measured on this fixture before the fix: recognition and the overlay both SUCCEEDED and
        the control reported UNAVAILABLE -- the single control written to catch this defect class
        did not run, and nothing said so. A green result reachable without the work being done.
        """
        af = probe_against(LGBM45Table).controls["alias_free"]
        self.assertIsNotNone(af["name"], "the control did not run on the source shape")
        self.assertNotIn("status", af)
        self.assertEqual(af["n_alias_free_in_table"], 3)

    def test_both_accessor_shapes_give_the_same_control_verdict(self):
        """Which accessor answers is not knowable from here, so it must not change the verdict."""
        a = probe_against(LGBM45Table)
        b = probe_against(RawDumpTable)
        self.assertEqual(a.controls["alias_free"], b.controls["alias_free"])
        self.assertEqual(a.recognised_knobs, b.recognised_knobs)
        self.assertIsNone(a.error)
        self.assertIsNone(b.error)

    def test_extra_aliases_subtracts_the_canonical_name_under_either_shape(self):
        self.assertEqual(zr._extra_aliases("deterministic", ["deterministic"]), set())
        self.assertEqual(zr._extra_aliases("deterministic", []), set())
        self.assertEqual(zr._extra_aliases("num_threads", ["num_threads", "n_jobs"]), {"n_jobs"})
        self.assertIsNone(zr._extra_aliases("num_threads", None))

    def test_the_alias_free_control_reports_UNAVAILABLE_rather_than_passing(self):
        """A table with no alias-free entry cannot run the control. Absence is not a pass."""
        class NoAliasFree:
            @staticmethod
            def _get_all_param_aliases():
                # Every parameter has a REAL alias beyond its own name, under either shape.
                return {k: [k, f"{k}_alias"] for k in
                        list(zr.Z_REPRO_KNOBS) + [zr._POSITIVE_CONTROL]}

        p = probe_against(NoAliasFree)
        self.assertIsNone(p.error)                       # not a failure ...
        self.assertIsNone(p.controls["alias_free"]["name"])
        self.assertIn("UNAVAILABLE", p.controls["alias_free"]["status"])   # ... but recorded

    def test_a_table_missing_the_POSITIVE_control_is_unverified(self):
        """Catches a table that is present but truncated, empty-ish or differently shaped."""
        class Truncated:
            @staticmethod
            def _get_all_param_aliases():
                return {"learning_rate": ["eta"]}

        p = probe_against(Truncated)
        self.assertIn("not discriminating", p.error or "")
        self.assertIn("positive", p.error or "")
        self.assertTrue(all(v is None for v in p.recognised_knobs.values()))

    def test_a_table_admitting_the_NEGATIVE_control_is_unverified(self):
        """The echo detector, moved to where the method now reads."""
        class Permissive:
            @staticmethod
            def _get_all_param_aliases():
                return {zr._NEGATIVE_CONTROL: [], zr._POSITIVE_CONTROL: ["num_leaf"],
                        **{k: [] for k in zr.Z_REPRO_KNOBS}}

        p = probe_against(Permissive)
        self.assertIn("negative", p.error or "")
        with self.assertRaises(zc.ZContractError):
            zr.z_lgbm_overlay(p)

    def test_a_knob_genuinely_ABSENT_from_the_table_is_refused(self):
        """The direction that must survive the fix: a real refusal is still a refusal."""
        class MissingKnob:
            @staticmethod
            def _get_all_param_aliases():
                d = {k: [] for k in zr.Z_REPRO_KNOBS if k != "force_row_wise"}
                d[zr._POSITIVE_CONTROL] = ["num_leaf"]
                d["is_unbalance"] = []
                return d

        p = probe_against(MissingKnob)
        self.assertIs(p.recognised_knobs["force_row_wise"], False)
        with self.assertRaises(zc.ZContractError) as cm:
            zr.z_lgbm_overlay(p)
        self.assertIn("force_row_wise", str(cm.exception))

    def test_an_alias_is_admitted_as_well_as_the_canonical_name(self):
        universe = zr._parameter_universe(LGBM45Table._get_all_param_aliases())
        self.assertIn("num_threads", universe)
        self.assertIn("n_jobs", universe)                # an alias of it
        self.assertNotIn(zr._NEGATIVE_CONTROL, universe)

    def test_the_second_accessor_is_used_when_the_first_is_absent(self):
        class OldStyle:
            aliases = {"num_leaves": {"num_leaf"}, "is_unbalance": set(),
                       **{k: set() for k in zr.Z_REPRO_KNOBS}}

        p = probe_against(OldStyle)
        self.assertIsNone(p.error)
        self.assertEqual(p.controls["table_source"], "_ConfigAliases.aliases")

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
