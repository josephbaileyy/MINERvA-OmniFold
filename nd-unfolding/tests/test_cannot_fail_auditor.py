#!/usr/bin/env python3
"""The gates-that-cannot-fail auditor must keep its own power, or it becomes the thing it hunts.

`docs/orchestration/audit_gates_that_cannot_fail.py` is the repo-wide sweep for the defect class filed
independently by two lanes on 2026-08-07 (BEN-043, BEN-044, BEN-046; earlier BEN-023/032/039/040/042).
Every real instance is now fixed, so a sweep of the current tree cannot show the detectors work -- the
auditor's own `--power` mode fires each detector at a reconstruction of the pre-fix source instead.

These tests exist because the auditor already failed its own power test twice during development: two
detectors were silent on their own known instances (`\\btol\\b` does not match inside `psd_tol`, because
`_` is a word character), and one sweep reported "0 hits" from a `--root` that had resolved to a
directory containing none of the audited code. An auditor whose detectors have gone silent reports a
clean repo, which is exactly the failure it is built to catch -- so the power test is load-bearing and
needs a guard of its own. See BEN-070.
"""
import os
import subprocess
import sys
import unittest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ND)
AUDITOR = os.path.join(REPO, "docs", "orchestration", "audit_gates_that_cannot_fail.py")


@unittest.skipUnless(os.path.exists(AUDITOR), "auditor not present")
class AuditorKeepsItsPower(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run([sys.executable, AUDITOR, *args],
                              capture_output=True, text=True, cwd=REPO)

    def test_every_detector_fires_on_its_own_pre_fix_source(self):
        r = self._run("--power-only")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("power test PASSED for all detectors", r.stdout)
        self.assertNotIn("SILENT", r.stdout, "a detector went silent on its own known instance")

    def test_power_test_names_every_registered_detector(self):
        """A detector added without a power case would otherwise be silently unproven."""
        sys.path.insert(0, os.path.dirname(AUDITOR))
        import audit_gates_that_cannot_fail as aud
        registered = {name for name, _ in aud.DETECTORS}
        powered = set(aud.POWER)
        self.assertEqual(registered, powered,
                         f"detectors without a power case: {registered - powered}; "
                         f"power cases without a detector: {powered - registered}")

    def test_sweep_refuses_to_report_from_a_root_with_no_code(self):
        """The '0 hits' bug: a clean bill of health from a check that examined nothing."""
        r = self._run("--root", os.path.join(REPO, "docs", "orchestration"))
        self.assertNotEqual(r.returncode, 0,
                            "sweeping a near-empty root must FAIL CLOSED, not report 0 hits")
        self.assertIn("visited only", r.stdout + r.stderr)

    def test_sweep_visits_the_real_tree(self):
        r = self._run("--severity", "DEFECT")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"=== SWEEP of .* \(\d{3,} files\) ===",
                         "the default root must reach the code, not a docs subdirectory")


if __name__ == "__main__":
    unittest.main(verbosity=2)
