#!/usr/bin/env python3
"""The M1 runner's preconditions are REFUSALS, and these make them fire.

`run_m1_projection.sh` cannot run today by design: the trunk is not adopted. A runner whose
preconditions merely warned would be one careless invocation away from producing an unauthorized
product, so each is an exit with its own code. **A guard never made to fire is untested, not
proven** -- the specification says so in terms about the cause-4 guard -- so every refusal here has
a control that trips it and the positive control proves none of them trips on good input.

⚠ TWO METHOD NOTES, both from mistakes made writing this.
1. `bash -n` is NECESSARY AND NOT SUFFICIENT. A balanced pair of apostrophes parses cleanly and
   still merges the assignments between them, voiding the guards in the gap. So the operand controls
   below unset each mandatory variable IN TURN and require the refusal to NAME that variable. An
   11-of-12 presence test once missed exactly the variable that was broken.
2. MY FIRST HARNESS WAS INVALID and looked fine: every refusal control returned nonzero, but all
   four died at an UNSET OPERAND before reaching the guard under test -- zsh does not word-split an
   unquoted `$BASE`. That is the mutation-refused-before-reaching-the-guard shape, and it is why
   each refusal has a DISTINCT exit code (3 adoption, 4 instrumentation, 5 mask, 6 receipt) and why
   these tests assert on the code and the message, never merely on nonzero.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SH = REPO / "nd-unfolding" / "run_m1_projection.sh"
MANDATORY = ["MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_ADOPTION_RECORD", "MNV_SRC_COV",
             "MNV_SRC_HIST", "MNV_SRC_CV", "MNV_DST_MASK", "MNV_OUT"]


class M1RunnerRefusals(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "code" / "nd-unfolding").mkdir(parents=True)
        shutil.copy(REPO / "nd-unfolding" / "project_cov_nd.py",
                    self.t / "code" / "nd-unfolding" / "project_cov_nd.py")
        (self.t / "cov.root").touch()
        (self.t / "cv.root").touch()
        # THE ADOPTION RECORD MUST NAME THE COVARIANCE BY DIGEST (rc 1b), so the fixture computes
        # it rather than hardcoding a string. A keyword-only record is kept as a control.
        import hashlib
        _cov_sha = hashlib.sha256((self.t / "cov.root").read_bytes()).hexdigest()
        self.cov_sha = _cov_sha
        (self.t / "adopt.md").write_text(
            "This record ADOPTS the scalar-5D trunk.\n"
            f"src_cov sha256: {_cov_sha}\n")
        (self.t / "adopt_nodigest.md").write_text(
            "This record ADOPTS the scalar-5D trunk.\n")          # keyword only, no digest
        (self.t / "notadopt.md").write_text("no decision here\n")
        self.env = {
            "MNV_CODE_ROOT": str(self.t / "code"), "MNV_DATA_ROOT": str(self.t),
            "MNV_ADOPTION_RECORD": str(self.t / "adopt.md"),
            "MNV_SRC_COV": str(self.t / "cov.root"), "MNV_SRC_HIST": "hCov",
            "MNV_SRC_CV": str(self.t / "cv.root"), "MNV_DST_MASK": "receiving-cells",
            "MNV_OUT": str(self.t / "out.root"),
        }

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def _run(self, **over):
        env = {**os.environ, **self.env, **over}
        for k, v in over.items():
            if v is None:
                env.pop(k, None)
        return subprocess.run(["bash", str(SH)], env=env, capture_output=True, text=True)

    def test_syntax_parses_under_bash(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SH)]).returncode, 0)

    def test_no_apostrophe_inside_any_mandatory_operand_message(self):
        """The failure that voided guards twice in this campaign."""
        import re
        for m in re.finditer(r"\$\{[A-Za-z_][A-Za-z_0-9]*:\?([^}]*)\}", SH.read_text()):
            self.assertNotIn("'", m.group(1), f"apostrophe in operand message: {m.group(1)[:50]}")

    def test_every_mandatory_operand_refuses_BY_NAME_when_unset(self):
        for v in MANDATORY:
            r = self._run(**{v: None})
            self.assertNotEqual(r.returncode, 0, f"{v} unset did not refuse")
            self.assertIn(v, r.stderr, f"{v} unset refused without NAMING {v}")

    def test_missing_adoption_record_refuses_with_code_3(self):
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "nosuch.md"))
        self.assertEqual(r.returncode, 3)
        self.assertIn("no adoption record", r.stderr)

    def test_record_that_does_not_adopt_refuses_with_code_3(self):
        """A file existing is not a decision; it has to say it adopts."""
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "notadopt.md"))
        self.assertEqual(r.returncode, 3)
        self.assertIn("does not state an adoption", r.stderr)

    def test_uninstrumented_projector_refuses_with_code_4(self):
        """OI-129: a digest retrofitted after the product exists records only non-change since."""
        p = self.t / "code" / "nd-unfolding" / "project_cov_nd.py"
        p.write_text(p.read_text().replace("proj_sha256", "REMOVED_XX"))
        r = self._run()
        self.assertEqual(r.returncode, 4)
        self.assertIn("OI-129", r.stderr)

    def test_undeclared_destination_mask_refuses_with_code_5(self):
        r = self._run(MNV_DST_MASK="whatever")
        self.assertEqual(r.returncode, 5)
        self.assertIn("declared-dst-cv or receiving-cells", r.stderr)

    def test_declared_dst_cv_requires_its_operand(self):
        r = self._run(MNV_DST_MASK="declared-dst-cv")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("MNV_DST_CV", r.stderr)

    def test_POSITIVE_CONTROL_good_operands_trip_no_refusal(self):
        """Without this, a script that refused everything would pass every test above."""
        r = self._run()
        self.assertNotIn("REFUSED", r.stderr,
                         "a guard fired on valid input -- it would refuse a correct run")


class TheAdoptionRecordMustNameTheProduct(unittest.TestCase):
    """rc 1b: a keyword search is not identity.

    `grep -i adopt` is satisfied by ANY file containing the word, for ANY source -- so on its own it
    authorizes every candidate at once, which is the opposite of an adoption decision. The record
    must contain the MEASURED digest of the covariance being projected.

    ⚠ Adding this guard broke four existing tests in this file, because the old fixture's record
    carried no digest and the new refusal fired before the guard each of them targets. That is the
    refused-before-reaching-the-guard shape appearing in a fixture rather than a mutation, and the
    fix was to make the fixture compute the digest -- not to weaken the guard.
    """

    setUp = M1RunnerRefusals.setUp
    tearDown = M1RunnerRefusals.tearDown
    _run = M1RunnerRefusals._run

    def test_keyword_only_record_is_refused(self):
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "adopt_nodigest.md"))
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("does not name the measured digest", r.stderr)
        self.assertIn("A keyword match is not identity", r.stderr)

    def test_the_refusal_reports_the_measured_digest(self):
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "adopt_nodigest.md"))
        self.assertIn(self.cov_sha, r.stderr, "it must print what it measured")

    def test_a_record_naming_a_DIFFERENT_digest_is_refused(self):
        p = self.t / "adopt_wrong.md"
        p.write_text("This record ADOPTS the trunk.\nsrc_cov sha256: " + ("a" * 64) + "\n")
        r = self._run(MNV_ADOPTION_RECORD=str(p))
        self.assertEqual(r.returncode, 3, r.stderr)

    def test_the_matching_record_passes_this_guard(self):
        """Positive control: the digest guard must not fire on the record that does name it."""
        r = self._run()
        self.assertNotIn("does not name the measured digest", r.stderr)
        self.assertIn("record names the measured source digest", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
