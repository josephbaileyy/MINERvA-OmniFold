#!/usr/bin/env python3
"""EVERY launcher that declares a reservation is priced in the governing unit. Discovered, not listed.

THE DEFECT THIS EXISTS FOR. The M1 request was priced `8 cpus x 0.25 h = 2.0 CPU task-h`. That is
CORE-HOURS wearing the task-hour label. `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-
hours.md` settles the unit -- its positive clause is "the sum of `ElapsedRaw` over the arm tasks",
and its exclusion clause names `AllocCPUS`-weighting -- so the figure was 8x high, and it was
written AFTER that ruling landed. The ruling exists because a ceiling whose unit is undefined is
not a ceiling.

WHY DISCOVERY AND NOT A LIST. A test over a hardcoded list of launchers is a universal claim
implemented as the current diff: it passes forever while the next launcher goes unchecked. These
tests find their own population by grepping for the declaration, so a new launcher that declares a
cap is covered the moment it exists, and one that declares none is reported by name rather than
silently skipped.

⚠ THE DIRECTION THAT MATTERS. Overstating a reservation misreports the ledger; UNDERSTATING it
admits an item against headroom it may exceed. Both are refused, and the `cpus-per-task` check is
asserted as a NON-match so the specific historical error cannot return.
"""
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ND = REPO / "nd-unfolding"
LIB = ND / "lib_r5_admission.sh"

# The population: every shell script in nd-unfolding that declares an enforced reservation.
DECLARING = sorted(p for p in ND.glob("*.sh")
                   if re.search(r"^ENFORCED_TASK_HOURS=", p.read_text(), re.M))


class PopulationIsNotEmpty(unittest.TestCase):
    def test_discovery_found_something(self):
        """An empty population would make every test below vacuously pass. This campaign has been
        caught by a criterion whose declared population was empty."""
        self.assertGreaterEqual(len(DECLARING), 2,
                                f"discovery found {[p.name for p in DECLARING]}")


class PricedInTaskHours(unittest.TestCase):
    def _constants(self, text):
        return {
            "ntasks": int(re.search(r"^ENFORCED_NTASKS=(\d+)", text, re.M).group(1)),
            "wall": float(re.search(r"^ENFORCED_WALL_HOURS=([0-9.]+)", text, re.M).group(1)),
            "task_h": float(re.search(r"^ENFORCED_TASK_HOURS=([0-9.]+)", text, re.M).group(1)),
        }

    def _sbatch(self, text):
        t = re.search(r"^#SBATCH .*--time=(\d+):(\d+):(\d+)", text, re.M)
        n = re.search(r"^#SBATCH .*--ntasks=(\d+)", text, re.M)
        c = re.search(r"^#SBATCH .*--cpus-per-task=(\d+)", text, re.M)
        self.assertIsNotNone(t, "no #SBATCH --time")
        self.assertIsNotNone(n, "no #SBATCH --ntasks")
        h, m, s = (int(g) for g in t.groups())
        return {"wall": h + m / 60.0 + s / 3600.0,
                "ntasks": int(n.group(1)),
                "cpus": int(c.group(1)) if c else 1}

    def test_every_declaration_matches_its_own_sbatch_directives(self):
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                text = p.read_text()
                dec, sb = self._constants(text), self._sbatch(text)
                self.assertEqual(dec["ntasks"], sb["ntasks"], "ntasks disagrees with #SBATCH")
                self.assertAlmostEqual(dec["wall"], sb["wall"], places=6,
                                       msg="wall hours disagree with #SBATCH --time")

    def test_every_reservation_is_ntasks_times_wall(self):
        """task-hours = ntasks x wall. The governing definition, not a convention chosen here."""
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                dec = self._constants(p.read_text())
                self.assertAlmostEqual(dec["task_h"], dec["ntasks"] * dec["wall"], places=6)

    def test_no_reservation_is_priced_in_core_hours(self):
        """The specific historical error: `cpus-per-task x wall`. Asserted as a NON-match."""
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                text = p.read_text()
                dec, sb = self._constants(text), self._sbatch(text)
                if sb["cpus"] > 1:
                    self.assertNotAlmostEqual(
                        dec["task_h"], sb["cpus"] * sb["wall"], places=6,
                        msg=f"{p.name} is priced in core-hours, not task-hours")

    def test_the_declared_string_is_typable(self):
        """The cap check is a STRING comparison, so a declaration a human cannot type exactly
        would make the guard fire on every correct invocation."""
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                raw = re.search(r"^ENFORCED_TASK_HOURS=([0-9.]+)", p.read_text(), re.M).group(1)
                self.assertLessEqual(len(raw.split(".")[-1]), 4,
                                     f"{p.name} declares {raw}, which no operator will type exactly")


class AdmissionIsCalledNotRetyped(unittest.TestCase):
    def test_every_declaring_launcher_sources_the_shared_library(self):
        """A copy of the admission block is a second implementation that does not change when the
        first is corrected. This campaign has that shape on record."""
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                self.assertIn("lib_r5_admission.sh", p.read_text())

    def test_every_declaring_launcher_verifies_admission(self):
        for p in DECLARING:
            with self.subTest(launcher=p.name):
                text = p.read_text()
                self.assertIn("r5_admission_check", text)
                self.assertIn("r5_require_declared_cap", text)

    def test_the_library_calls_the_meter_rather_than_reimplementing_it(self):
        text = LIB.read_text()
        self.assertIn("r5_meter.py", text)
        self.assertIn("check", text)
        # A local reimplementation of the ceiling would be the retyped-rule defect.
        self.assertNotIn("500", text.replace("500.", ""),
                         "the ceiling must come from the meter, not be hardcoded here")

    def test_the_library_and_every_caller_parse(self):
        for p in [LIB] + DECLARING:
            with self.subTest(f=p.name):
                self.assertEqual(subprocess.run(["bash", "-n", str(p)]).returncode, 0)

    def test_no_apostrophe_in_any_operand_message_anywhere(self):
        """The failure that voided guards twice: a balanced apostrophe pair inside ${VAR:?...}
        parses cleanly and merges the assignments between."""
        for p in [LIB] + DECLARING:
            with self.subTest(f=p.name):
                for m in re.finditer(r"\$\{[A-Za-z_][A-Za-z_0-9]*:\?([^}]*)\}", p.read_text()):
                    self.assertNotIn("'", m.group(1), f"{p.name}: {m.group(1)[:50]}")


if __name__ == "__main__":
    unittest.main()
