#!/usr/bin/env python3
"""`run_m1_diagnostic.sh` is the path Joseph's 2026-09-18 grant opened, and its grant is
CONDITIONAL. These make every condition fire.

The grant: "I explicitly authorize provisional projections and counterfactuals from the preserved
candidate covariance when needed to resolve acceptance questions. Keep them labeled diagnostic and
non-adopted, with separate outputs and receipts. Preserve the adoption requirement for publication
products; add a distinct diagnostic execution path where needed." Plus: "Before every submission,
account for all lanes charged usage and outstanding reservations, record the scientific question,
inputs, expected decision value, and enforced resource limits, and verify admission."

A condition that is only documented is not a condition, so each clause is a refusal with its own
exit code: 3 question/decision-value, 4 instrumentation, 5 mask, 6 output separation, 7 overwrite,
8 declared-versus-enforced reservation, 9 R5 admission, 10 missing receipt.

THREE TESTS CARRY THE WEIGHT AND ARE NOT ABOUT THIS FILE.
* `test_enforced_constants_equal_the_sbatch_directives` is the pricing guard. The reservation was
  once priced as `cpus-per-task x wall` -- core-hours wearing the task-hour label, against a
  standing decision record that task-hours are the sum of ElapsedRaw and are NOT AllocCPUS
  weighted. This makes the drift unlandable rather than merely documented. It reads the file
  STATICALLY, because sbatch executes a COPY and `$0`/`BASH_SOURCE` both name the spool path.
* `test_publication_runner_still_refuses_without_adoption` is the ratchet. Adding a diagnostic path
  is exactly how a publication guard gets waived in practice, so the neighbouring script is
  re-measured here rather than assumed intact.
* `test_positive_control_reaches_past_every_refusal` proves the refusals are not vacuous. It
  asserts the run got PAST them -- the pre-submission record printed and the exit code is not a
  refusal code -- rather than asserting success, which is unreachable without ROOT.

METHOD NOTE, carried over because it cost a whole harness once: `bash -n` is necessary and NOT
sufficient -- it passed a stray `$tooshort` in this very script's refusal message -- and a control
that returns nonzero may have died at an unset operand BEFORE reaching the guard under test. So
every assertion below is on the exit CODE and the message, never on nonzero alone.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SH = REPO / "nd-unfolding" / "run_m1_diagnostic.sh"
PUB_SH = REPO / "nd-unfolding" / "run_m1_projection.sh"
METER = REPO / "docs" / "orchestration" / "r5_meter.py"

MANDATORY = ["MNV_CODE_ROOT", "MNV_ACCEPTANCE_QUESTION", "MNV_DECISION_VALUE", "MNV_SRC_COV",
             "MNV_SRC_HIST", "MNV_SRC_CV", "MNV_DST_MASK", "MNV_OUT", "MNV_R5_RECEIPT",
             "MNV_DECLARED_TASK_HOURS"]

GOOD_Q = "tau: how far may the projected (E_avail,W) correlation move before the corner claim flips"
GOOD_V = "whether tau can be computed at all, which is what blocks the adoption decision"


def _write_receipt(path: Path, elapsed_seconds: int) -> None:
    """Build the R5 receipt with the PRODUCER, never by hand.

    A fixture hand-written to the schema agrees with my reading of the schema rather than with the
    meter, and the meter is what the runner calls. `measure` also stamps `measured_at_utc` to now,
    which is what makes the receipt fresh -- a hand-built fixture would have to fake that field and
    would then be testing the faking.
    """
    sacct = path.parent / f"sacct_{elapsed_seconds}.txt"
    sacct.write_text(
        f"9000001|m1diag|COMPLETED|{elapsed_seconds}|cpu_ss11|"
        f"2026-09-10T00:00:00|2026-09-10T00:00:01|billing=1,cpu=8,mem=16G,node=1\n")
    out = subprocess.run(["python3", str(METER), "measure", "--from-file", str(sacct)],
                         capture_output=True, text=True, check=True)
    path.write_text(out.stdout)


class M1DiagnosticRefusals(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "code" / "nd-unfolding").mkdir(parents=True)
        (self.t / "code" / "docs" / "orchestration").mkdir(parents=True)
        shutil.copy(REPO / "nd-unfolding" / "project_cov_nd.py",
                    self.t / "code" / "nd-unfolding" / "project_cov_nd.py")
        shutil.copy(METER, self.t / "code" / "docs" / "orchestration" / "r5_meter.py")
        (self.t / "cov.root").touch()
        (self.t / "cv.root").touch()
        self.receipt = self.t / "r5.json"
        _write_receipt(self.receipt, 600)          # 0.1667 CPU task-h spent, far inside
        (self.t / "DIAGNOSTIC").mkdir()
        self.env = {
            "MNV_CODE_ROOT": str(self.t / "code"),
            "MNV_ACCEPTANCE_QUESTION": GOOD_Q,
            "MNV_DECISION_VALUE": GOOD_V,
            "MNV_SRC_COV": str(self.t / "cov.root"), "MNV_SRC_HIST": "hCov",
            "MNV_SRC_CV": str(self.t / "cv.root"), "MNV_DST_MASK": "receiving-cells",
            "MNV_OUT": str(self.t / "DIAGNOSTIC" / "m1_diag.root"),
            "MNV_R5_RECEIPT": str(self.receipt),
            "MNV_DECLARED_TASK_HOURS": "0.25",
        }

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def _run(self, **over):
        env = {**os.environ, **self.env, **over}
        for k, v in over.items():
            if v is None:
                env.pop(k, None)
        return subprocess.run(["bash", str(SH)], env=env, capture_output=True, text=True)

    # ---- the two static checks -------------------------------------------------------------
    def test_syntax_parses_under_bash(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SH)]).returncode, 0)

    def test_no_apostrophe_inside_any_mandatory_operand_message(self):
        for m in re.finditer(r"\$\{[A-Za-z_][A-Za-z_0-9]*:\?([^}]*)\}", SH.read_text()):
            self.assertNotIn("'", m.group(1), f"apostrophe in operand message: {m.group(1)[:50]}")

    def test_no_undefined_variable_in_any_refusal_message(self):
        """`bash -n` accepted a stray `$tooshort` here, which would have printed nothing and read
        as a truncated message. Every `$NAME` in an echo must be assigned somewhere in the file."""
        text = SH.read_text()
        assigned = set(re.findall(r"^([A-Za-z_][A-Za-z_0-9]*)=", text, re.M))
        assigned |= set(re.findall(r'"\$\{([A-Za-z_][A-Za-z_0-9]*):[?-]', text))
        assigned |= {"rc", "_rc", "_need", "_v", "PATH", "HOME"}
        for m in re.finditer(r"^\s*echo\s+\"([^\"]*)\"", text, re.M):
            for name in re.findall(r"\$\{?([A-Za-z_][A-Za-z_0-9]*)", m.group(1)):
                if name.startswith("#"):
                    continue
                self.assertIn(name, assigned, f"unassigned ${name} in: {m.group(1)[:60]}")

    def test_enforced_constants_equal_the_sbatch_directives(self):
        """THE PRICING GUARD. A declared reservation that disagrees with the enforced cap admits
        an item against headroom it may exceed, and the wrong unit is what made that possible."""
        text = SH.read_text()
        sbatch = re.search(r"^#SBATCH .*--time=(\d+):(\d+):(\d+)", text, re.M)
        self.assertIsNotNone(sbatch, "no #SBATCH --time directive found")
        h, m, s = (int(g) for g in sbatch.groups())
        wall_hours = h + m / 60.0 + s / 3600.0
        ntasks = int(re.search(r"^#SBATCH .*--ntasks=(\d+)", text, re.M).group(1))
        declared_wall = float(re.search(r"^ENFORCED_WALL_HOURS=([0-9.]+)", text, re.M).group(1))
        declared_ntasks = int(re.search(r"^ENFORCED_NTASKS=(\d+)", text, re.M).group(1))
        declared_th = float(re.search(r"^ENFORCED_TASK_HOURS=([0-9.]+)", text, re.M).group(1))
        self.assertAlmostEqual(declared_wall, wall_hours, places=9)
        self.assertEqual(declared_ntasks, ntasks)
        # task-hours = ntasks x wall. NOT cpus-per-task x wall, which is core-hours.
        self.assertAlmostEqual(declared_th, ntasks * wall_hours, places=9)
        cpus = int(re.search(r"^#SBATCH .*--cpus-per-task=(\d+)", text, re.M).group(1))
        self.assertNotAlmostEqual(declared_th, cpus * wall_hours, places=6,
                                  msg="the reservation is priced in core-hours, not task-hours")

    def test_it_is_not_the_publication_path_wearing_another_name(self):
        """A diagnostic runner that read an adoption record would be the publication path with its
        guard relocated. It must not consult one at all."""
        self.assertNotIn("MNV_ADOPTION_RECORD", SH.read_text())

    # ---- every mandatory operand refuses BY NAME -------------------------------------------
    def test_every_mandatory_operand_refuses_by_name(self):
        for var in MANDATORY:
            with self.subTest(var=var):
                r = self._run(**{var: None})
                self.assertNotEqual(r.returncode, 0, f"{var} unset did not refuse")
                self.assertIn(var, r.stderr, f"refusal did not name {var}: {r.stderr[:200]}")

    # ---- rc 3: the grant is scoped to a NAMED acceptance question -------------------------
    def test_short_question_refuses_rc3(self):
        r = self._run(MNV_ACCEPTANCE_QUESTION="tau")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("MNV_ACCEPTANCE_QUESTION", r.stderr)

    def test_short_decision_value_refuses_rc3(self):
        r = self._run(MNV_DECISION_VALUE="useful")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("MNV_DECISION_VALUE", r.stderr)

    # ---- rc 4: instrumentation, including the class label ---------------------------------
    def test_projector_without_run_class_refuses_rc4(self):
        proj = self.t / "code" / "nd-unfolding" / "project_cov_nd.py"
        proj.write_text(proj.read_text().replace("runClass", "xxxClass"))
        r = self._run()
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn("runClass", r.stderr)

    def test_projector_without_readback_refuses_rc4(self):
        proj = self.t / "code" / "nd-unfolding" / "project_cov_nd.py"
        proj.write_text(proj.read_text().replace("row_index_sha256_readback", "gone"))
        r = self._run()
        self.assertEqual(r.returncode, 4, r.stderr)

    # ---- rc 5: the destination mask is declared --------------------------------------------
    def test_undeclared_mask_refuses_rc5(self):
        r = self._run(MNV_DST_MASK="whatever")
        self.assertEqual(r.returncode, 5, r.stderr)

    # ---- rc 6: separate outputs, enforced on the path --------------------------------------
    def test_output_without_the_marker_refuses_rc6(self):
        r = self._run(MNV_OUT=str(self.t / "m1.root"))
        self.assertEqual(r.returncode, 6, r.stderr)
        self.assertIn("DIAGNOSTIC", r.stderr)

    def test_output_into_a_product_tree_refuses_rc6(self):
        (self.t / "products" / "5d").mkdir(parents=True)
        r = self._run(MNV_OUT=str(self.t / "products" / "5d" / "DIAGNOSTIC_m1.root"))
        self.assertEqual(r.returncode, 6, r.stderr)

    def test_output_into_the_candidate_projection_tree_refuses_rc6(self):
        d = self.t / "projections_candidate"
        d.mkdir()
        r = self._run(MNV_OUT=str(d / "DIAGNOSTIC_m1.root"))
        self.assertEqual(r.returncode, 6, r.stderr)

    # ---- rc 7: no silent overwrite ---------------------------------------------------------
    def test_existing_output_refuses_rc7(self):
        out = Path(self.env["MNV_OUT"])
        out.write_text("a prior diagnostic")
        r = self._run()
        self.assertEqual(r.returncode, 7, r.stderr)

    # ---- rc 8: the declared reservation IS the enforced cap --------------------------------
    def test_understated_reservation_refuses_rc8(self):
        """The direction that matters: it admits against headroom the run may exceed."""
        r = self._run(MNV_DECLARED_TASK_HOURS="0.01")
        self.assertEqual(r.returncode, 8, r.stderr)
        self.assertIn("0.25", r.stderr)

    def test_core_hour_priced_reservation_refuses_rc8(self):
        """2.0 is `cpus-per-task x wall` -- the exact figure this campaign committed once."""
        r = self._run(MNV_DECLARED_TASK_HOURS="2.0")
        self.assertEqual(r.returncode, 8, r.stderr)

    # ---- rc 9: R5 admission ----------------------------------------------------------------
    def test_missing_r5_receipt_refuses_rc9(self):
        r = self._run(MNV_R5_RECEIPT=str(self.t / "nope.json"))
        self.assertEqual(r.returncode, 9, r.stderr)

    def test_exhausted_headroom_refuses_rc9(self):
        """Producer-built receipt at 499.9 CPU task-h: spend + 0.25 crosses 500, so admission
        fails. This is the clause that makes the ceiling bind rather than be quoted."""
        near = self.t / "r5_near.json"
        _write_receipt(near, int(499.9 * 3600))
        r = self._run(MNV_R5_RECEIPT=str(near))
        self.assertEqual(r.returncode, 9, r.stderr)

    def test_stale_receipt_refuses_rc9(self):
        """The meter fails closed on staleness, and the runner must not survive that."""
        stale = json.loads(self.receipt.read_text())
        stale["measured_at_utc"] = "2026-09-01T00:00:00.000000Z"
        p = self.t / "r5_stale.json"
        p.write_text(json.dumps(stale))
        r = self._run(MNV_R5_RECEIPT=str(p))
        self.assertEqual(r.returncode, 9, r.stderr)

    # ---- the positive control, and the neighbouring ratchet -------------------------------
    def test_positive_control_reaches_past_every_refusal(self):
        """Asserts the refusals are not vacuous. Success is unreachable without ROOT, so the
        assertion is that the pre-submission record printed and the exit code is not a refusal."""
        r = self._run()
        self.assertIn("the five things the authorization requires be recorded", r.stdout)
        self.assertIn("scientific question", r.stdout)
        self.assertIn("enforced limits", r.stdout)
        self.assertNotIn(r.returncode, (3, 4, 5, 6, 7, 8, 9),
                         f"a refusal fired on valid input: rc={r.returncode} {r.stderr[:300]}")

    def test_publication_runner_still_refuses_without_adoption(self):
        """THE RATCHET. Adding a diagnostic path is how a publication guard gets waived, so this
        re-measures the neighbouring script rather than assuming it is intact."""
        env = {**os.environ,
               "MNV_CODE_ROOT": str(self.t / "code"), "MNV_DATA_ROOT": str(self.t),
               "MNV_ADOPTION_RECORD": str(self.t / "no_such_adoption.md"),
               "MNV_SRC_COV": str(self.t / "cov.root"), "MNV_SRC_HIST": "hCov",
               "MNV_SRC_CV": str(self.t / "cv.root"), "MNV_DST_MASK": "receiving-cells",
               "MNV_OUT": str(self.t / "out.root")}
        r = subprocess.run(["bash", str(PUB_SH)], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("no adoption record", r.stderr)

    def test_publication_runner_does_not_accept_a_diagnostic_class(self):
        """The publication path must not be able to emit a diagnostic-labelled product, or the two
        classes stop being separate in the other direction."""
        self.assertNotIn("--run-class diagnostic", PUB_SH.read_text())


if __name__ == "__main__":
    unittest.main()
