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
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SH = REPO / "nd-unfolding" / "run_m1_projection.sh"
MANDATORY = ["MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_ADOPTION_RECORD", "MNV_SRC_COV",
             "MNV_SRC_HIST", "MNV_SRC_CV", "MNV_DST_MASK", "MNV_OUT",
             "MNV_EXPECT_VARIANT"]


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
            "This record adopts the scalar-5D trunk.\n"
            f"ADOPTS-SHA256: {_cov_sha}\n")
        (self.t / "adopt_nodigest.md").write_text(
            "This record ADOPTS the scalar-5D trunk.\n")          # keyword only, no sentinel
        # A receipt or routing document naturally carries the digest AND the word, in prose.
        # That is the measured defect: it must be refused.
        (self.t / "prose_receipt.md").write_text(
            "Adoption route notes for the pilot outcome.\n"
            f"{_cov_sha}  z-cv.npz    890,500,272 B\n")
        # A sentinel that negates or defers itself is not a decision.
        (self.t / "adopt_negated.md").write_text(
            f"ADOPTS-SHA256: {_cov_sha} -- PROPOSED, held as drafted and not executed.\n")
        (self.t / "adopt_nothing.md").write_text(
            f"ADOPTS-SHA256: nothing. The digest {_cov_sha} is recorded for reference only.\n")
        (self.t / "notadopt.md").write_text("no decision here\n")
        self.env = {
            "MNV_CODE_ROOT": str(self.t / "code"), "MNV_DATA_ROOT": str(self.t),
            "MNV_ADOPTION_RECORD": str(self.t / "adopt.md"),
            "MNV_SRC_COV": str(self.t / "cov.root"), "MNV_SRC_HIST": "hCov",
            "MNV_SRC_CV": str(self.t / "cv.root"), "MNV_DST_MASK": "receiving-cells",
            "MNV_EXPECT_VARIANT": "none",
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
        self.assertIn("carries no ADOPTS-SHA256", r.stderr)
        self.assertIn("A keyword match is not identity", r.stderr)

    def test_the_refusal_reports_the_measured_digest(self):
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "adopt_nodigest.md"))
        self.assertIn(self.cov_sha, r.stderr, "it must print what it measured")

    def test_a_record_naming_a_DIFFERENT_digest_is_refused(self):
        p = self.t / "adopt_wrong.md"
        p.write_text("This record adopts the trunk.\nADOPTS-SHA256: " + ("a" * 64) + "\n")
        r = self._run(MNV_ADOPTION_RECORD=str(p))
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("does not name the measured digest", r.stderr)
        self.assertIn("declared:", r.stderr)

    def test_a_PROSE_document_carrying_the_word_and_the_digest_is_refused(self):
        """THE MEASURED DEFECT, end to end. A receipt or routing document naturally contains both
        the digest and the word, in prose. Three real repo documents did. It must be refused."""
        r = self._run(MNV_ADOPTION_RECORD=str(self.t / "prose_receipt.md"))
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("carries no ADOPTS-SHA256", r.stderr)

    def test_a_NEGATED_or_HELD_sentinel_is_refused(self):
        """The repo idiom for refusing is literally *adopts nothing*, and the 6.4 exception is held
        *as drafted, not executed*. Neither shape may read as a decision."""
        for name in ("adopt_negated.md", "adopt_nothing.md"):
            with self.subTest(name):
                r = self._run(MNV_ADOPTION_RECORD=str(self.t / name))
                self.assertEqual(r.returncode, 3, r.stderr)
                self.assertIn("negated, provisional or held", r.stderr)

    def test_the_matching_record_passes_this_guard(self):
        """Positive control: the digest guard must not fire on the record that does name it."""
        r = self._run()
        self.assertNotIn("does not name the measured digest", r.stderr)
        self.assertIn("record names the measured source digest", r.stdout)




class AdoptionSentinelIsNotAKeywordSearch(unittest.TestCase):
    """MEASURED DEFECT, 2026-09-18: the old guard passed three non-authorizing repo documents.

    Joseph named this failure directly -- *"the launcher's keyword search does not enforce digest
    identity"* -- and the first repair only added the digest half. The conjunction of
    `grep -i adopt` and a loose `grep -F <sha>` is still not a decision, for a structural reason:
    a RECEIPT naturally contains the digest and any document DISCUSSING adoption naturally
    contains the word. Measured against the repo, `PLAN-20260918`, `NAVIGATION-20260917` (a pure
    routing document) and `DECISION-PACKET-20260918` all passed BOTH checks for the `z-cv` digest.

    These tests are the both-directions pair: the OLD predicate admitted those documents, the NEW
    one refuses them, and the new one still ACCEPTS a properly formed record. A repair that only
    tightened would be indistinguishable from one that broke the launcher outright.
    """
    Z_CV_SHA = "3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5"
    SUSPECTS = ("docs/orchestration/PLAN-20260918-scalar5d-publication-completion.md",
                "docs/orchestration/NAVIGATION-20260917-z-pilot-outcome-route.md",
                "docs/orchestration/DECISION-PACKET-20260918-scalar5d-publication-blockers.md")

    @staticmethod
    def _old_predicate(text, sha):
        return bool(re.search(r"adopt(ed|s|ion)", text, re.I)) and sha in text

    @staticmethod
    def _new_predicate(text, sha):
        lines = [ln for ln in text.splitlines()
                 if re.match(r"^[\s*`>_ -]*ADOPTS-SHA256[*`_]*\s*:", ln)]
        if not lines:
            return False
        if any(re.search(r"nothing|never|withheld|\snot\s|pending|proposed|draft|held", ln, re.I)
               for ln in lines):
            return False
        return any(sha in re.findall(r"[0-9a-f]{64}", ln) for ln in lines)

    def test_the_old_predicate_DID_admit_non_authorizing_documents(self):
        """Proves the repair is real and not decorative. If this ever fails, the defect is gone
        for some other reason and the regression below is no longer measuring anything."""
        admitted = [s for s in self.SUSPECTS
                    if self._old_predicate((REPO / s).read_text(encoding="utf-8"), self.Z_CV_SHA)]
        self.assertEqual(len(admitted), 3, f"expected all three admitted, got {admitted}")

    def test_the_new_predicate_refuses_every_one_of_them(self):
        for rel in self.SUSPECTS:
            with self.subTest(rel):
                self.assertFalse(
                    self._new_predicate((REPO / rel).read_text(encoding="utf-8"), self.Z_CV_SHA),
                    f"{rel} adopts nothing and must not satisfy the adoption gate")

    SENTINEL_RE = r"^[\s*`>_ -]*ADOPTS-SHA256[*`_]*\s*:[^\n]*?\b[0-9a-f]{64}\b"

    ADOPTION_RECORD = ("docs/orchestration/"
                       "DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md")

    def test_EXACTLY_ONE_document_adopts_and_it_is_the_expected_one(self):
        """⚠ THIS TEST USED TO ASSERT **ZERO**, AND THAT WAS RIGHT UNTIL 2026-09-20.

        It read: *"Nothing is adopted yet, so the gate must be unsatisfiable by anything now
        committed."* Joseph adopted `3d7465f6...` on 2026-09-20, so that assertion is obsolete and
        keeping it would have meant deleting a live guard to make a commit pass.

        **The replacement is STRICTER than the original in the world that now exists.** "Zero" only
        says nothing adopts; this says exactly WHICH document adopts and exactly WHAT it adopts, so
        a second adoption record anywhere under `docs/` -- or the same one silently repointed at
        other bytes -- fails here. The predicate is the launcher's own, not a restatement: a
        negated sentinel does not count, which is why the still-refusing draft is absent from the
        expected list.

        ⚠ THE PATTERN REQUIRES A REAL 64-HEX ON THE SENTINEL LINE, deliberately -- a template
        carrying a `<placeholder>` DECLARES NOTHING and must not count. The companion test below
        is the other direction."""
        adopting = sorted(
            str(q.relative_to(REPO)) for q in (REPO / "docs").rglob("*.md")
            if self._new_predicate(q.read_text(encoding="utf-8", errors="ignore"), self.Z_CV_SHA))
        self.assertEqual(adopting, [self.ADOPTION_RECORD],
                         f"expected exactly one adopting document; got {adopting}")

    def test_the_still_refusing_draft_does_NOT_count_as_an_adoption(self):
        """Its sentinel is negated, so the launcher refuses it -- and so must this scan."""
        draft = REPO / "docs/orchestration/DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md"
        self.assertTrue(draft.is_file())
        self.assertFalse(self._new_predicate(draft.read_text(encoding="utf-8"), self.Z_CV_SHA))

    def test_no_document_adopts_any_OTHER_digest(self):
        """The exception attaches to bytes. A sentinel naming different bytes is a second adoption
        nobody authorized -- including either product of the 2026-09-20 campaign."""
        offenders = []
        for q in (REPO / "docs").rglob("*.md"):
            text = q.read_text(encoding="utf-8", errors="ignore")
            for ln in text.splitlines():
                if not re.search(self.SENTINEL_RE, ln, re.I):
                    continue
                if re.search(r"nothing|never|withheld|\snot\s|pending|proposed|draft|held",
                             ln, re.I):
                    continue
                for sha in re.findall(r"[0-9a-f]{64}", ln):
                    if sha != self.Z_CV_SHA:
                        offenders.append((str(q.relative_to(REPO)), sha))
        self.assertEqual(offenders, [], f"documents adopting other bytes: {offenders}")

    def test_that_scan_WOULD_catch_a_real_declaration_and_skips_a_template(self):
        """Without this, the scan above could pass by matching nothing at all."""
        real = f"ADOPTS-SHA256: {'b' * 64}\n"
        self.assertRegex(real, self.SENTINEL_RE)
        for template in ("ADOPTS-SHA256: <64 hex of the covariance being projected>\n",
                         "ADOPTS-SHA256: <measured sha256 of the trunk>\n"):
            with self.subTest(template.strip()):
                self.assertNotRegex(template, self.SENTINEL_RE)

    def test_the_new_predicate_ACCEPTS_a_properly_formed_record(self):
        sha = "a" * 64
        for body in (f"ADOPTS-SHA256: {sha}\n",
                     f"**ADOPTS-SHA256**: {sha}\n",
                     f"- ADOPTS-SHA256: `{sha}`\n"):
            with self.subTest(body.strip()):
                self.assertTrue(self._new_predicate(body, sha))


class TheLauncherCanActuallyHandOverTheExceptionRecord(unittest.TestCase):
    """PROJ would have refused the moment Joseph adopted, and nothing would have caught it.

    ADOPTION DOES NOT EDIT THE SOURCE -- by design, the candidate keeps `adoptable: false` and its
    historical rejection. So after ADOPT the projector STILL refuses `--run-class publication`
    unless handed the digest-bound exception record (`project_cov_nd.py:361`). This launcher passed
    `--adoption-exception` ZERO times.

    That is the fifth instance of one shape in this campaign: `grep -i adopt` authorising every
    candidate, rc 1 admitting a routing document, `variant` in a docstring nothing read,
    `--run-class` never passed so its refusal could not fire, and now an exception route the
    publication launcher could not reach. Every one was a protection or a path that existed and did
    nothing, and every one was found by exercising the real thing rather than the predicate.
    """
    def setUp(self):
        self.src = SH.read_text(encoding="utf-8")

    def test_the_array_is_BUILT(self):
        self.assertIn("EXC_ARG=(", self.src)

    def test_the_array_is_actually_PASSED_to_the_projector(self):
        """Building an array and forgetting to pass it is exactly the --run-class defect. The
        assertion is on the invocation line, not on the array's existence."""
        inv = re.sub(r"\\\n\s*", " ", self.src)
        line = [l for l in inv.splitlines()
                if "project_cov_nd.py" in l and l.lstrip().startswith("python3")]
        self.assertEqual(len(line), 1, "expected exactly one projector invocation")
        self.assertIn('"${EXC_ARG[@]}"', line[0])
        self.assertIn("--run-class publication", line[0])

    def test_it_is_OPTIONAL_so_an_adoptable_source_needs_no_exception(self):
        """A guard that fires on every correct run is not a guard: an adoptable trunk must not be
        forced to carry an exception record it does not need.

        ⚠ THIS TEST WAS VACUOUS WHEN FIRST WRITTEN -- its helper ran `bash -n`, a syntax check,
        while the name claimed it exercised the unset path. It now RUNS the launcher with the
        variable unset and requires that the exception branch stays silent."""
        self.assertIn('ADOPTION_EXCEPTION="${MNV_ADOPTION_EXCEPTION:-}"', self.src)
        env = {k: v for k, v in self._good_env().items()}
        env.pop("MNV_ADOPTION_EXCEPTION", None)
        r = subprocess.run(["bash", str(SH)], env=env, capture_output=True, text=True)
        self.assertNotIn("MNV_ADOPTION_EXCEPTION set but no record", r.stderr)
        self.assertNotEqual(r.returncode, 3,
                            f"unset exception must not trip a refusal: {r.stderr}")

    def _good_env(self):
        t = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, t, True)
        (t / "code" / "nd-unfolding").mkdir(parents=True)
        shutil.copy(REPO / "nd-unfolding" / "project_cov_nd.py",
                    t / "code" / "nd-unfolding" / "project_cov_nd.py")
        (t / "cov.root").touch(); (t / "cv.root").touch()
        import hashlib
        sha = hashlib.sha256((t / "cov.root").read_bytes()).hexdigest()
        (t / "adopt.md").write_text(f"adopts it\nADOPTS-SHA256: {sha}\n")
        return {**os.environ,
                "MNV_CODE_ROOT": str(t / "code"), "MNV_DATA_ROOT": str(t),
                "MNV_ADOPTION_RECORD": str(t / "adopt.md"),
                "MNV_SRC_COV": str(t / "cov.root"), "MNV_SRC_HIST": "hCov",
                "MNV_SRC_CV": str(t / "cv.root"), "MNV_DST_MASK": "receiving-cells",
                "MNV_OUT": str(t / "out.root"), "MNV_EXPECT_VARIANT": "none"}

    def test_a_MISSING_exception_file_refuses_rather_than_passing_a_bad_path(self):
        env = self._good_env()
        env["MNV_ADOPTION_EXCEPTION"] = str(Path(env["MNV_DATA_ROOT"]) / "nope.md")
        r = subprocess.run(["bash", str(SH)], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("MNV_ADOPTION_EXCEPTION set but no record", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
