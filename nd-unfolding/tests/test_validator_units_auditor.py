#!/usr/bin/env python3
"""The mixed-units auditor must keep its classifier honest and its live control findable.

`docs/orchestration/audit_validator_tolerance_units.py` mechanises the review heuristic behind BEN-070
and BEN-071: read a validator's checks against each other before reading any against the physics. Three
times in two days a guard was written in different units from its neighbours, twice with the correct
scale two lines away.

The auditor's power control is REAL rather than synthetic -- `p4_validate_active_lateral_fps.mat_gates`
mixes units in the current tree -- so these tests pin both directions:
  * the control must be found (a silent classifier reports a clean repo, which is the defect class the
    tool exists to find);
  * and the classifier must get ABSOLUTE / RELATIVE / FLOOR right on constructed cases, because the
    whole table's value rests on that call being defensible rather than plausible.

See docs/orchestration/VALIDATOR-TOLERANCE-UNITS-20260808.md for the table and its verdicts.
"""
import ast
import os
import subprocess
import sys
import unittest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ND)
AUD = os.path.join(REPO, "docs", "orchestration", "audit_validator_tolerance_units.py")


@unittest.skipUnless(os.path.exists(AUD), "auditor not present")
class MixedUnitsAuditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.dirname(AUD))
        import audit_validator_tolerance_units as m
        cls.m = m

    def _classify(self, src):
        """Run the classifier over a one-function source and return {line: kind}."""
        tree = ast.parse(src)
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[id(child)] = node
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        rows = self.m.classify_function(fn, src.split("\n"), parents)
        return {r["line"]: r["kind"] for r in rows}

    def test_relative_when_tolerance_is_scaled(self):
        got = self._classify("def f(ev):\n    return ev[0] >= -1e-12 * abs(ev[-1])\n")
        self.assertEqual(set(got.values()), {"RELATIVE"}, got)

    def test_relative_when_compared_quantity_is_a_quotient(self):
        got = self._classify("def f(a, b, d):\n    return abs(a - b) / d < 1e-9\n")
        self.assertEqual(set(got.values()), {"RELATIVE"}, got)

    def test_absolute_when_bare_literal_against_raw_quantity(self):
        got = self._classify("def f(d):\n    return d >= -1e-30\n")
        self.assertEqual(set(got.values()), {"ABSOLUTE"}, got)

    def test_floor_inside_max_is_not_a_tolerance(self):
        """`max(1e-300, max|C|)` is a div-by-zero guard and must count as neither."""
        got = self._classify("def f(C, x):\n    return x / max(1e-300, abs(C).max()) < 1e-9\n")
        self.assertNotIn("ABSOLUTE", got.values(), got)
        self.assertIn("RELATIVE", got.values(), got)

    def test_physics_bars_are_excluded_by_the_tolerance_cut(self):
        """recovery >= 0.80 is absolute BY SPECIFICATION and must not be flagged."""
        got = self._classify("def f(recovery, gap):\n    return recovery >= 0.80\n")
        self.assertEqual(got, {}, got)

    def test_mixing_is_what_gets_reported(self):
        src = ("def f(ev, d):\n"
               "    a = ev[0] >= -1e-12 * abs(ev[-1])\n"
               "    b = d >= -1e-30\n"
               "    return a and b\n")
        got = self._classify(src)
        self.assertEqual(set(got.values()), {"RELATIVE", "ABSOLUTE"}, got)

    def test_live_positive_control_is_found_and_sweep_fails_closed_without_it(self):
        r = subprocess.run([sys.executable, AUD], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("FOUND", r.stdout)
        self.assertNotIn("NOT FOUND", r.stdout)

    def test_sweep_refuses_a_root_with_no_code(self):
        r = subprocess.run([sys.executable, AUD, "--root", os.path.dirname(AUD)],
                           capture_output=True, text=True, cwd=REPO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("visited only", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
