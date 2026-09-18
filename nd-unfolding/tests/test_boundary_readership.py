#!/usr/bin/env python3
"""The operative sheet's `read by production` column must MATCH a live measurement.

Joseph, 2026-09-18: *"every declared boundary carries `read by production: yes/no`, measured, not
asserted ... That converts this from a recurring finding into a schema property."*

A hand-typed column would become the fifth asserted-but-inert artifact in this campaign, after the
keyword adoption search, the routing document that satisfied rc 1, `variant` in a docstring, and
`--run-class` never passed. So the column is bound to `boundary_readership.measure()` here, and
this test fails if they diverge -- whether because a boundary became live and the sheet still says
`no`, or because a reader was deleted and the sheet still says `yes`.

⚠ THE MEASURER NEEDS ITS OWN POWER TEST. A measurer that returned `no` unconditionally would make
the binding test pass forever while measuring nothing -- exactly the shape of the defects it
exists to catch. `test_the_measurer_reports_yes_...` builds a module that genuinely reads a value
from a reachable entry point and requires `yes`, and its sibling removes only the reachability and
requires `no`.
"""
import re
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
SHEET = ND.parent / "docs" / "orchestration" / "OPERATIVE-SHEET-scalar5d.md"
sys.path.insert(0, str(ND))
import boundary_readership as br          # noqa: E402
import z_contract as zc                   # noqa: E402


def sheet_rows():
    """`{boundary: bool}` from the sheet's table, read rather than assumed."""
    rows = {}
    for ln in SHEET.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*`([a-z0-9_]+)`\s*\|.*?\|\s*\*\*(yes|no)\*\*", ln)
        if m:
            rows[m.group(1)] = (m.group(2) == "yes")
    return rows


class SheetMatchesTheMeasurement(unittest.TestCase):
    def test_the_sheet_lists_every_declared_boundary(self):
        self.assertEqual(set(sheet_rows()), set(zc.Z_BOUNDARIES),
                         "the sheet's boundary table and Z_BOUNDARIES have diverged")

    def test_each_recorded_value_equals_the_measured_value(self):
        measured = br.measure(sorted(zc.Z_BOUNDARIES))
        for key, recorded in sheet_rows().items():
            with self.subTest(key):
                self.assertEqual(
                    recorded, measured[key]["read_by_production"],
                    f"{key}: sheet says {'yes' if recorded else 'no'}, measurement says "
                    f"{'yes' if measured[key]['read_by_production'] else 'no'}. Re-run "
                    f"`python3 nd-unfolding/boundary_readership.py` and correct the sheet.")


class TheMeasurerHasPower(unittest.TestCase):
    """Both directions, because a one-directional check waves the other through."""

    def _with_module(self, name, body):
        p = ND / name
        p.write_text(body, encoding="utf-8")
        self.addCleanup(lambda: p.unlink(missing_ok=True))
        return p

    BODY_READS = ('from z_contract import boundary\n'
                  'def go():\n    return boundary("cause3_agg").value\n')

    def test_it_reports_yes_for_a_reachable_value_read(self):
        self._with_module("_tmp_probe_reachable.py",
                          self.BODY_READS + 'if __name__ == "__main__":\n    go()\n')
        self.assertTrue(br.measure(["cause3_agg"])["cause3_agg"]["read_by_production"],
                        "the measurer missed a genuine reachable value read")

    def test_it_reports_no_when_only_reachability_is_removed(self):
        """Same read, no entry point. Isolates reachability as the discriminating property."""
        self._with_module("_tmp_probe_unreachable.py", self.BODY_READS)
        self.assertFalse(br.measure(["cause3_agg"])["cause3_agg"]["read_by_production"],
                         "the measurer counted an unreachable module as production")

    def test_a_boundary_key_STRING_is_not_counted_as_a_read(self):
        """The distinction the whole column rests on."""
        self._with_module("_tmp_probe_named.py",
                          'KEY = "cause3_agg"\nif __name__ == "__main__":\n    print(KEY)\n')
        r = br.measure(["cause3_agg"])["cause3_agg"]
        self.assertFalse(r["read_by_production"])
        self.assertIn("_tmp_probe_named.py", r["named_only_in"])


if __name__ == "__main__":
    unittest.main()
