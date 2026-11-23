#!/usr/bin/env python3
"""Tests of msr_route_diag2.py: it writes only the director's fields, never a value a reading uses, and its 50-digit
reference reproduces section 3.3 where float64 is accurate.

    python3 -m unittest nd-unfolding/msr/test_msr_route_diag2.py
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import mpmath as mp
import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_route_diag2 as D  # noqa: E402
import msr_project as P  # noqa: E402
from test_msr import make_fixture, FIXTURE_COMMON  # noqa: E402

GOOD = dict(stat="Z_well", vector_id="2d#013", build="full/numpy", kappa2_C=1e6, kappa2_CQ=5e2, rel_diff_drivers=1e-12,
            rel_diff_eigen_vs_ref=1e-9, rel_diff_indep_vs_ref=1e-3, ref_partition_equal=True)


class Writer(unittest.TestCase):
    def test_exact_fields_accepted(self):
        r = D.Record()
        r.add(**GOOD)
        r.add(**dict(GOOD, ref_partition_equal=None, rel_diff_eigen_vs_ref=float("nan")))
        self.assertEqual(set(r.rows[0]), set(D.FIELDS))

    def test_any_other_field_is_refused(self):
        for extra in ({"a": 1.0}, {"b": 0.3}, {"value": 2.0}, {"label": "below"}, {"band": "mixed"},
                      {"z_ref": 1.0}):
            with self.assertRaises(ValueError):
                D.Record().add(**GOOD, **extra)

    def test_a_missing_field_is_refused(self):
        for k in D.FIELDS:
            row = dict(GOOD)
            row.pop(k)
            with self.assertRaises(ValueError):
                D.Record().add(**row)

    def test_wrong_types_are_refused(self):
        for k, v in (("ref_partition_equal", 1), ("rel_diff_eigen_vs_ref", "0.1"), ("kappa2_C", 3), ("stat", 5),
                     ("rel_diff_drivers", None)):
            with self.assertRaises(ValueError):
                D.Record().add(**dict(GOOD, **{k: v}))

    def test_targets_are_diagnostic_1s_failing_rows(self):
        self.assertEqual(len(D.TARGETS_2D), 21)
        self.assertEqual(len(set(D.TARGETS_2D)), 21)
        self.assertEqual(D.TARGETS_5D, ("5d#001", "5d#002", "5d#003"))
        diag1 = HERE.parents[1] / "docs/orchestration/state/measurability-20261122/route-diag/diag.json"
        rows = json.loads(diag1.read_text())["rows"]
        failing = sorted(r["vector_id"] for r in rows if r["stat"] == "Z_well" and not r["passes_current_bar"])
        passing = {r["vector_id"] for r in rows if r["stat"] == "Z_well" and r["passes_current_bar"]}
        self.assertEqual(failing, sorted(D.TARGETS_2D))
        self.assertTrue(set(D.TARGETS_5D) <= passing)


def rows_for(eig, ind, part=True):
    return [dict(GOOD, vector_id=v, rel_diff_eigen_vs_ref=e, rel_diff_indep_vs_ref=i, ref_partition_equal=part)
            for v, e, i in zip(D.TARGETS_2D, eig, ind)] + \
           [dict(GOOD, vector_id=v, rel_diff_eigen_vs_ref=float("nan"), rel_diff_indep_vs_ref=float("nan"),
                 ref_partition_equal=None) for v in D.TARGETS_5D]


class Rule(unittest.TestCase):
    def test_independent_route_branch(self):
        self.assertEqual(D.branch(rows_for([1e-8] * 21, [1e-12] * 20 + [2e-8])), "independent-route")

    def test_c_formation_branch(self):
        self.assertEqual(D.branch(rows_for([1e-12] * 20 + [2e-8], [1e-12] * 20 + [3e-3])), "c-formation")
        self.assertEqual(D.branch(rows_for([float("nan")] + [0.0] * 20, [float("inf")] + [0.0] * 20)), "c-formation")

    def test_anything_else_goes_to_the_director(self):
        self.assertEqual(D.branch(rows_for([0.0] * 21, [0.0] * 21)), "director")             # both agree
        self.assertEqual(D.branch(rows_for([2e-8] + [0.0] * 20, [0.0] * 21)), "director")    # only eigen misses
        self.assertEqual(D.branch(rows_for([2e-8, 0.0] + [0.0] * 19, [0.0, 2e-8] + [0.0] * 19)), "director")
        self.assertEqual(D.branch(rows_for([0.0] * 21, [1.0] * 21, part=False)), "director")  # partition differs
        self.assertEqual(D.branch(rows_for([0.0] * 21, [1.0] * 21)[1:]), "director")          # a row missing

    def test_nan_eigen_is_not_within_tolerance(self):
        self.assertEqual(D.branch(rows_for([float("nan")] + [0.0] * 20, [0.0] * 21)), "director")


def small_problem(seed: int, n_reco: int = 14, n_true: int = 9, m: int = 4, null_col=True):
    """A small, well-conditioned problem with one unseen truth column (a null direction of F); null_col="tiny" makes
    that column 1e-9 of the rest, so F's eigenvalue there is nonzero but below the 1e-12 range cut."""
    rng = np.random.default_rng(seed)
    R = rng.uniform(0.0, 1.0, (n_reco, n_true)) * (rng.uniform(size=(n_reco, n_true)) < 0.6)
    R += np.eye(n_reco, n_true) * 0.8
    if null_col:
        R[:, -1] = R[:, -1] * 1e-9 if null_col == "tiny" else 0.0
    t0 = rng.uniform(50.0, 200.0, n_true)
    b = rng.uniform(1.0, 5.0, n_reco)
    J = np.zeros((m, n_true))
    cols = [n_true - 1] + list(rng.choice(n_true - 1, m - 1, replace=False))   # J reads the unseen column
    for r, c in enumerate(cols):
        J[r, c] = 1.0 / t0[c]
    return sparse.csr_matrix(R), t0, b, J


class Reference(unittest.TestCase):
    def setUp(self):
        self.dps = mp.mp.dps
        mp.mp.dps = D.DPS

    def tearDown(self):
        mp.mp.dps = self.dps

    def test_fisher_matches_did(self):
        import did
        R, t0, b, _ = small_problem(1)
        b[3] = -1e9   # one reco cell with mu <= 0 is excluded, as did.fisher excludes it
        R = R.tolil()
        R[5, :] = 0.0   # and an empty reco row contributes nothing
        R = R.tocsr()
        R.eliminate_zeros()
        F64 = did.fisher(R, t0, b)
        Fmp = D.mp_fisher(R, t0, b)
        self.assertLess(float(mp.mnorm(Fmp - mp.matrix(F64.tolist()), 1)), 1e-12 * float(np.abs(F64).sum()))

    def test_reference_reproduces_float64_where_it_is_accurate(self):
        import did
        for seed, null_col in ((2, True), (3, False), (4, True), (6, "tiny")):
            R, t0, b, J = small_problem(seed, null_col=null_col)
            F = did.fisher(R, t0, b)
            for cut in (P.CUT,):
                dec = P.decompose(F, J, "numpy", cut)
                # widen the cut so the well block is non-empty on this toy, the same for both sides
                cut2 = float(np.sort(dec["s"])[len(dec["s"]) // 2]) * 1.0001 if dec["s"].size else cut
                dec = P.decompose(F, J, "numpy", cut2)
                ref = mp_decompose_cut(D.mp_fisher(R, t0, b), J, cut2)
                self.assertEqual((ref["n_well"], ref["dim_inf"]), (dec["n_well"], dec["dim_inf"]))
                self.assertEqual(dec["dim_inf"], 1 if null_col else 0)
                if null_col == "tiny":   # the cut is exercised: an eigenvalue in (0, 1e-12 lam_max)
                    lam = mp.eigsy(D.mp_fisher(R, t0, b))[0]
                    lo, hi = min(lam), max(lam)
                    self.assertTrue(0 < lo < mp.mpf("1e-12") * hi)
                beta = np.random.default_rng(seed).normal(size=J.shape[0])
                z64, zref = P.z_well(dec, beta), D.mp_z(ref, beta)
                self.assertIsNotNone(z64)
                self.assertLess(D.rel(z64, zref), 1e-10)

    def test_reference_sees_an_error_a_perturbed_float64_c_would_make(self):
        """The reference is independent of the float64 C: corrupting C by 1e-6 relative moves the float64 Z, not it."""
        import did
        R, t0, b, J = small_problem(5)
        F = did.fisher(R, t0, b)
        dec = P.decompose(F, J, "numpy", 10.0)
        ref = mp_decompose_cut(D.mp_fisher(R, t0, b), J, 10.0)
        beta = np.ones(J.shape[0])
        self.assertLess(D.rel(P.z_well(dec, beta), D.mp_z(ref, beta)), 1e-10)
        real = P.decompose

        def corrupt(F_, J_, driver="numpy", cut=P.CUT):
            return real(F_ * (1 + 1e-6 * np.random.default_rng(0).normal(size=F_.shape)), J_, driver, cut)
        bad = corrupt(0.5 * (F + F.T), J, "numpy", 10.0)
        self.assertGreater(D.rel(P.z_well(bad, beta), D.mp_z(ref, beta)), 1e-9)

    def test_rel(self):
        self.assertEqual(D.rel(2.0, 2.0), 0.0)
        self.assertEqual(D.rel(None, 1.0), float("inf"))
        self.assertEqual(D.rel(None, None), 0.0)
        self.assertAlmostEqual(D.rel(1.0, mp.mpf("1.1")), 0.1 / 1.1)


def mp_decompose_cut(F, J, cut):
    with mock.patch.object(D, "WELL_CUT", cut):
        return D.mp_decompose(F, J)


def float64_reference(F, J_np):
    """A fast stand-in for mp_decompose in the end-to-end test (the Reference tests check the real one)."""
    dec = P.decompose(np.asarray(F, float), J_np, "numpy", D.WELL_CUT)
    return {"w": mp.matrix(dec["w"].tolist()), "s": [mp.mpf(float(x)) for x in dec["s"]],
            "well": [int(k) for k in np.flatnonzero(dec["well"])], "n_well": dec["n_well"], "dim_inf": dec["dim_inf"]}


class EndToEnd(unittest.TestCase):
    SLOW = False   # True runs the 50-digit reference on the fixture's 224-cell 2D problem (several minutes)

    def test_the_output_holds_only_the_fields_and_no_reading_value(self):
        if self.SLOW:
            self._run()
        else:
            import did
            with mock.patch.object(D, "mp_fisher", lambda R, t0, b: did.fisher(sparse.csr_matrix(R), t0, b)), \
                    mock.patch.object(D, "mp_decompose", float64_reference):
                self._run()

    def _run(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            # the fixture's vectors: which call numbers are 5D and 2D (the real targets do not exist on it)
            seen = []
            real_route = P.route_independent

            def spy(dec, beta):
                seen.append("5d" if beta.size == 16 else "2d")
                return real_route(dec, beta)
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(P, "route_independent", spy):
                P.run(prod, Path(d) / "ref")
            ref = json.loads((Path(d) / "ref/readout.json").read_text())
            ids2 = tuple(f"2d#{i + 1:03d}" for i, k in enumerate(seen) if k == "2d")[:3]
            ids5 = tuple(f"5d#{i + 1:03d}" for i, k in enumerate(seen) if k == "5d")[:3]
            self.assertTrue(ids2 and ids5)
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(D, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(D, "TARGETS_2D", ids2), mock.patch.object(D, "TARGETS_5D", ids5):
                try:
                    rc = D.run(prod, Path(d) / "diag.json")
                finally:
                    P.route_independent = real_route
            out = json.loads((Path(d) / "diag.json").read_text())
        self.assertEqual(rc, 0)
        self.assertEqual(set(out), {"schema", "fields", "rows"})
        self.assertEqual([r["vector_id"] for r in out["rows"]], list(ids2) + list(ids5))
        for row in out["rows"]:
            self.assertEqual(set(row), set(D.FIELDS))
            self.assertEqual(row["stat"], "Z_well")
        for row in out["rows"][len(ids2):]:
            self.assertIsNone(row["ref_partition_equal"])
            self.assertTrue(math.isnan(row["rel_diff_eigen_vs_ref"]) and math.isnan(row["rel_diff_indep_vs_ref"]))
        for row in out["rows"][:len(ids2)]:
            self.assertIsInstance(row["ref_partition_equal"], bool)
        values = []
        for block in ref["M1"].values():
            for v in block.values():
                values += [v["S_poor"]] + ([v["Z_well"]] if v["Z_well"] is not None else [])
        text = json.dumps(out)
        nontrivial = [float(x) for x in values if abs(float(x)) > 1e-6 and float(x) not in (0.0, 1.0)]
        self.assertTrue(nontrivial)
        for x in nontrivial:
            self.assertNotIn(repr(x), text)
            self.assertNotIn(json.dumps(x), text)

    def test_refuses_when_a_control_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(D, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(P, "controls", lambda prod: ({"C-OPS": {"pass": False}}, {})):
                self.assertEqual(D.run(Path(d), Path(d) / "x.json"), 3)
            self.assertFalse((Path(d) / "x.json").exists())

    def test_refuses_when_a_target_row_is_not_reached(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            real_route = P.route_independent
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(D, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(D, "TARGETS_2D", ("2d#999",)):
                try:
                    rc = D.run(prod, Path(d) / "diag.json")
                finally:
                    P.route_independent = real_route
            self.assertEqual(rc, 4)
            self.assertFalse((Path(d) / "diag.json").exists())

    def test_refuses_a_changed_msr_project(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(D, "MSR_PROJECT_SHA", "0" * 64):
                self.assertEqual(D.run(Path(d), Path(d) / "x.json"), 9)

    def test_refuses_an_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text("{}")
            self.assertEqual(D.main(["--products", d, "--out", str(p)]), 9)


if __name__ == "__main__":
    if "--slow" in sys.argv:
        sys.argv.remove("--slow")
        EndToEnd.SLOW = True
    unittest.main()
