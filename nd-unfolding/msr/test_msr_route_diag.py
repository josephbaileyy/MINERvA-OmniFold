#!/usr/bin/env python3
"""Tests of msr_route_diag.py: it writes only the director's seven fields and never a value a reading uses.

    python3 -m unittest nd-unfolding/msr/test_msr_route_diag.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_route_diag as D  # noqa: E402
import msr_project as P  # noqa: E402
from test_msr import make_fixture, FIXTURE_COMMON  # noqa: E402

GOOD = dict(stat="Z_well", vector_id="5d#001", build="full/numpy", rel_diff=1e-9, passes_current_bar=True,
            kappa2=1e6, ten_kappa_eps=2e-9)


class Writer(unittest.TestCase):
    def test_exact_fields_accepted(self):
        r = D.Record()
        r.add(**GOOD)
        self.assertEqual(set(r.rows[0]), set(D.FIELDS))

    def test_any_other_field_is_refused(self):
        for extra in ({"a": 1.0}, {"b": 0.3}, {"value": 2.0}, {"label": "below"}, {"band": "mixed"}):
            with self.assertRaises(ValueError):
                D.Record().add(**GOOD, **extra)

    def test_a_missing_field_is_refused(self):
        row = dict(GOOD)
        row.pop("kappa2")
        with self.assertRaises(ValueError):
            D.Record().add(**row)

    def test_wrong_types_are_refused(self):
        for k, v in (("passes_current_bar", 1), ("rel_diff", "0.1"), ("kappa2", 3), ("stat", 5)):
            with self.assertRaises(ValueError):
                D.Record().add(**dict(GOOD, **{k: v}))

    def test_rel_and_bar_helpers(self):
        self.assertEqual(D.rel(2.0, 2.0), 0.0)
        self.assertAlmostEqual(D.rel(1.0, 1.1), 0.1 / 1.1)
        self.assertEqual(D.rel(None, 1.0), float("inf"))
        self.assertEqual(D.rel(None, None), 0.0)
        self.assertTrue(D.passes(1.0, 1.0 + 5e-9))
        self.assertFalse(D.passes(1.0, 1.0 + 5e-8))
        self.assertFalse(D.passes(None, 1.0))
        self.assertTrue(D.passes(None, None))


class EndToEnd(unittest.TestCase):
    def test_the_output_holds_only_the_fields_and_no_reading_value(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON), \
                    mock.patch.object(D, "MSR_PROJECT_SHA", P.sha256(Path(P.__file__))):
                real_route, real_r = P.route_independent, P.r_independent
                try:
                    rc = D.run(prod, Path(d) / "diag.json")
                finally:
                    P.route_independent, P.r_independent = real_route, real_r
                out = json.loads((Path(d) / "diag.json").read_text())
                with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON):
                    P.run(prod, Path(d) / "ref")
                ref = json.loads((Path(d) / "ref/readout.json").read_text())
        self.assertEqual(rc, 0)
        self.assertEqual(set(out), {"schema", "fields", "rows"})
        self.assertTrue(out["rows"])
        for row in out["rows"]:
            self.assertEqual(set(row), set(D.FIELDS))
            self.assertIn(row["stat"], ("S_poor", "Z_well", "r_poor", "r_well"))
        # no S_poor or Z_well value of the fixture's readings appears anywhere in the diagnostic's output
        values = []
        for block in ref["M1"].values():
            for v in block.values():
                values += [v["S_poor"]] + ([v["Z_well"]] if v["Z_well"] is not None else [])
        text = json.dumps(out)
        nontrivial = [float(x) for x in values if abs(float(x)) > 1e-6 and float(x) not in (0.0, 1.0)]
        self.assertTrue(nontrivial)   # the check is not vacuous
        for x in nontrivial:          # 0 and 1 carry no information and also occur as relative differences
            self.assertNotIn(repr(x), text)
            self.assertNotIn(json.dumps(x), text)
        stats = {r["stat"] for r in out["rows"]}
        self.assertEqual(stats, {"S_poor", "Z_well", "r_poor", "r_well"})

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
    unittest.main()
