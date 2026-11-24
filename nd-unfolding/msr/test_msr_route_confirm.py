#!/usr/bin/env python3
"""Tests of msr_route_confirm.py: diagnostic 2's fields and rows only, no reading value, and the pre-committed verdict.

    python3 -m unittest nd-unfolding/msr/test_msr_route_confirm.py
"""
from __future__ import annotations

import json
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
import msr_route_confirm as C  # noqa: E402
import msr_route_diag2 as D  # noqa: E402
import msr_project as P  # noqa: E402
from test_msr import make_fixture, FIXTURE_COMMON  # noqa: E402

GOOD = dict(stat="Z_well", vector_id="2d#013", build="full/numpy", kappa2_C=1e20, kappa2_CQ=5e6, rel_diff_drivers=1e-12,
            rel_diff_eigen_vs_ref=1e-11, rel_diff_indep_vs_ref=1e-11, ref_partition_equal=True)


def rows(eig=None, ind=None, part=None):
    ids = list(D.TARGETS_2D) + list(D.TARGETS_5D)
    eig = eig or [1e-11] * len(ids)
    ind = ind or [1e-11] * len(ids)
    part = part or [True] * len(ids)
    return [dict(GOOD, vector_id=v, rel_diff_eigen_vs_ref=e, rel_diff_indep_vs_ref=i, ref_partition_equal=q)
            for v, e, i, q in zip(ids, eig, ind, part)]


class Verdict(unittest.TestCase):
    def test_pass_needs_every_row(self):
        self.assertEqual(C.confirm(rows()), ("PASS", 24, 24))
        self.assertEqual(C.confirm(rows(eig=[1e-8] * 24, ind=[1e-8] * 24)), ("PASS", 24, 24))   # the bar is inclusive

    def test_one_route_missing_on_one_row_fails(self):
        self.assertEqual(C.confirm(rows(eig=[2e-8] + [0.0] * 23)), ("FAIL", 23, 24))
        self.assertEqual(C.confirm(rows(ind=[0.0] * 23 + [2e-8])), ("FAIL", 23, 24))   # a 5D control row counts too

    def test_nan_inf_and_partition_fail(self):
        self.assertEqual(C.confirm(rows(eig=[float("nan")] + [0.0] * 23))[0], "FAIL")
        self.assertEqual(C.confirm(rows(ind=[float("inf")] + [0.0] * 23))[0], "FAIL")
        self.assertEqual(C.confirm(rows(part=[False] + [True] * 23)), ("FAIL", 23, 24))
        self.assertEqual(C.confirm(rows(part=[None] + [True] * 23)), ("FAIL", 23, 24))
        self.assertEqual(C.confirm(rows(eig=[float("-inf")] + [0.0] * 23)), ("FAIL", 23, 24))

    def test_missing_or_extra_rows_fail(self):
        self.assertEqual(C.confirm(rows()[1:]), ("FAIL", 0, 24))
        self.assertEqual(C.confirm(rows() + [dict(GOOD, vector_id="2d#999")]), ("FAIL", 0, 24))


class Pins(unittest.TestCase):
    def test_the_pins_match_the_files(self):   # a stale pin would refuse the real run (rc 9)
        self.assertEqual(C.MSR_PROJECT_SHA, P.sha256(Path(P.__file__)))
        self.assertEqual(C.DIAG2_SHA, P.sha256(Path(D.__file__)))


class Kappa(unittest.TestCase):
    def test_kappa_from_singular_values(self):
        d = {"G": np.diag([10.0, 1.0]), "s": np.array([0.1, 2.0])}
        self.assertAlmostEqual(C.kappa_g(d), 100.0)
        self.assertAlmostEqual(C.kappa_q(d), 400.0)

    def test_rank_deficient_is_infinite(self):
        self.assertEqual(C.kappa_g({"G": np.array([[1.0], [1.0]])}), float("inf"))
        self.assertEqual(C.kappa_g({"G": np.ones((2, 2))}), float("inf"))   # numerically singular (codex's case)
        self.assertEqual(C.kappa_q({"s": np.array([0.0, 1.0])}), float("inf"))
        self.assertEqual(C.kappa_q({"s": np.zeros(0)}), float("inf"))


def float64_reference(F, J_np):
    dec = P.decompose(np.asarray(F, float), J_np, "numpy", D.WELL_CUT)
    return {"w": mp.matrix(dec["w"].tolist()), "s": [mp.mpf(float(x)) for x in dec["s"]],
            "well": [int(k) for k in np.flatnonzero(dec["well"])], "n_well": dec["n_well"], "dim_inf": dec["dim_inf"]}


class EndToEnd(unittest.TestCase):
    def test_output_fields_rows_and_no_reading_value(self):
        import did
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            seen, real_route = [], P.route_independent

            def spy(dec, beta):
                seen.append("5d" if beta.size == 16 else "2d")
                return real_route(dec, beta)
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(P, "route_independent", spy):
                P.run(prod, Path(d) / "ref")
            ref = json.loads((Path(d) / "ref/readout.json").read_text())
            ids2 = tuple(f"2d#{i + 1:03d}" for i, k in enumerate(seen) if k == "2d")[:3]
            ids5 = tuple(f"5d#{i + 1:03d}" for i, k in enumerate(seen) if k == "5d")[:3]
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(C, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(D, "TARGETS_2D", ids2), mock.patch.object(D, "TARGETS_5D", ids5), \
                    mock.patch.object(D, "mp_fisher", lambda R, t0, b: did.fisher(sparse.csr_matrix(R), t0, b)), \
                    mock.patch.object(D, "mp_decompose", float64_reference):
                try:
                    rc = C.run(prod, Path(d) / "c.json")
                finally:
                    P.route_independent = real_route
                out = json.loads((Path(d) / "c.json").read_text())
                verdict = C.confirm(out["rows"])
        self.assertEqual(rc, 0)
        self.assertEqual(set(out), {"schema", "fields", "rows"})
        self.assertEqual(out["fields"], list(D.FIELDS))
        self.assertEqual([r["vector_id"] for r in out["rows"]], list(ids2) + list(ids5))
        for row in out["rows"]:
            self.assertEqual(set(row), set(D.FIELDS))
            self.assertIsInstance(row["ref_partition_equal"], bool)   # 5D rows have a reference here
        self.assertEqual(verdict, ("PASS", 6, 6))   # the float64 stand-in reference agrees with the amended code
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

    def test_refuses_a_changed_msr_project_or_diag2(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(C, "MSR_PROJECT_SHA", "0" * 64):
                self.assertEqual(C.run(Path(d), Path(d) / "x.json"), 9)
            with mock.patch.object(C, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(C, "DIAG2_SHA", "0" * 64):
                self.assertEqual(C.run(Path(d), Path(d) / "x.json"), 9)

    def test_refuses_when_a_control_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(C, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(P, "controls", lambda prod: ({"C-OPS": {"pass": False}}, {})):
                self.assertEqual(C.run(Path(d), Path(d) / "x.json"), 3)

    def test_refuses_when_a_target_row_is_not_reached(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            real_route = P.route_independent
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(C, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))), \
                    mock.patch.object(D, "TARGETS_2D", ("2d#999",)):
                try:
                    rc = C.run(prod, Path(d) / "c.json")
                finally:
                    P.route_independent = real_route
            self.assertEqual(rc, 4)
            self.assertFalse((Path(d) / "c.json").exists())

    def test_refuses_an_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text("{}")
            self.assertEqual(C.main(["--products", d, "--out", str(p)]), 9)


if __name__ == "__main__":
    unittest.main()
