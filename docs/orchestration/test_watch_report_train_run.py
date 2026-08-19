#!/usr/bin/env python3
"""Tests for watch_report_train_run.py, built on REAL producer-emitted logs.

BEN-476 is the governing constraint: a fixture derived from the rule cannot disagree with the rule. So
no fixture here was written from the five-signature list. Every byte comes from a log that a real Slurm
job on Perlmutter actually wrote (see test_fixtures_watch_report/PROVENANCE.tsv for source paths and
source-file sha256s).

The five signatures were written AFTER the three historical runs failed, so which signature each run
matches is MEASURED here, not assumed. The measurement is:

    57235710  (target stage) -> UNKNOWN   <- matches none of the five; a real producer-emitted UNKNOWN
    57253127_0               -> FAIL-2
    57256638_0               -> FAIL-3

Coverage shape required of every branch: a test that it FIRES on real input, and tests that it does NOT
fire on the other real inputs. A classifier that returned UNKNOWN for everything, or FAIL-3 for
everything, is caught by `test_no_verdict_is_constant` plus the per-run negative assertions. The
mutation run (`python3 test_watch_report_train_run.py --mutation`) demonstrates that by neutering the
matchers and showing these tests go red.

No test sends mail. The mail runner is always injected.
"""

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watch_report_train_run as W  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_fixtures_watch_report")

# (label, log-prefix, job-id, task, expected verdict) -- the measured truth table.
REAL_RUNS = (
    ("57235710 target-stage set -u death", "target", "57235710", "0", "UNKNOWN"),
    ("57253127_0 F2 family-root off-by-one", "train", "57253127", "0", "FAIL-2"),
    ("57256638_0 died at the receipt write", "train", "57256638", "0", "FAIL-3"),
)


class FakeProc(object):
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class MailSpy(object):
    """Injected in place of the mail runner. Records; never executes anything."""

    def __init__(self, returncode=0):
        self.calls = []
        self.returncode = returncode

    def __call__(self, argv, body):
        self.calls.append((list(argv), body))
        return FakeProc(self.returncode, "", "" if self.returncode == 0 else "simulated MTA failure")

    @property
    def subject(self):
        argv = self.calls[-1][0]
        return argv[argv.index("-s") + 1]

    @property
    def body(self):
        return self.calls[-1][1]


SACCT_ROWS = (
    "       JobID      State ExitCode    Elapsed \n"
    "------------ ---------- -------- ---------- \n"
    "    57256638     FAILED      1:0   02:58:44 \n"
)


def sacct_ok(argv):
    return FakeProc(0, SACCT_ROWS, "")


def sacct_down(argv):
    return FakeProc(1, "", "sacct: error: slurm_load_jobs: Unable to contact slurm controller")


def fixture_path(prefix, job, task, ext):
    """Fixtures are stored with a trailing .txt: .gitignore excludes *.out/*.err repo-wide.

    See test_fixtures_watch_report/README.md. The bytes are the excerpt bytes; only the stored name
    differs from the producer's name, and PROVENANCE.tsv records the full source path either way.
    """
    return os.path.join(FIXTURES, "%s_%s_%s%s.txt" % (prefix, job, task, ext))


def load_readable(prefix, job, task):
    """The (label, path, text) triples `classify` consumes, straight from the fixtures."""
    readable = []
    for label, ext in (("stdout", ".out"), ("stderr", ".err")):
        path = fixture_path(prefix, job, task, ext)
        with open(path, "r", errors="replace") as handle:
            readable.append((label, path, handle.read()))
    return readable


def verdict_of(prefix, job, task, index=0, seed=50000):
    return W.classify(load_readable(prefix, job, task), index, seed)[0]


# =====================================================================================================
# 1. Every branch fires on real input, and does not fire on the others.
# =====================================================================================================

class TestRealRunClassification(unittest.TestCase):

    def test_each_real_run_gets_its_measured_verdict(self):
        for label, prefix, job, task, expected in REAL_RUNS:
            with self.subTest(run=label):
                self.assertEqual(verdict_of(prefix, job, task), expected,
                                 "%s should classify as %s" % (label, expected))

    def test_each_verdict_fires_for_exactly_one_real_run(self):
        """The does-not-fire direction. A matcher that fires on two real runs is over-broad."""
        seen = {}
        for label, prefix, job, task, _expected in REAL_RUNS:
            seen[label] = verdict_of(prefix, job, task)
        for label, prefix, job, task, expected in REAL_RUNS:
            for other, got in seen.items():
                if other == label:
                    continue
                self.assertNotEqual(got, expected,
                                    "%r and %r both classified as %s; the matcher does not "
                                    "discriminate" % (label, other, expected))

    def test_no_verdict_is_constant(self):
        """Catches 'returns UNKNOWN for everything' and 'returns FAIL-3 for everything'."""
        verdicts = [verdict_of(p, j, t) for _l, p, j, t, _e in REAL_RUNS]
        self.assertEqual(len(set(verdicts)), len(verdicts),
                         "all three real runs produced verdicts %r -- a constant or near-constant "
                         "classifier" % (verdicts,))

    def test_57235710_matches_none_of_the_five(self):
        """The load-bearing UNKNOWN evidence: a real run the closed set does not cover.

        This is the one the five signatures were NOT written for. Its stdout is empty and its stderr is
        a single line about ADDR2LINE being unbound -- a conda activate shim killed by a `set -u`, which
        is upstream of anything the five describe.
        """
        readable = load_readable("target", "57235710", "0")
        verdict, matches, done, receipt, cfg = W.classify(readable, 0, 50000)
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(matches, [], "expected zero signature matches, got %r" % (matches,))
        self.assertFalse(done)
        self.assertFalse(receipt)
        self.assertFalse(cfg)

    def test_57235710_stdout_is_empty_but_that_is_not_NO_LOGS(self):
        """An empty-but-readable stream is UNKNOWN, not NO-LOGS. Distinct outcomes, distinct causes."""
        readable = load_readable("target", "57235710", "0")
        self.assertEqual(readable[0][2], "", "fixture drift: 57235710 stdout should be 0 bytes")
        self.assertEqual(len(readable), 2, "both streams were readable, so NO-LOGS must not apply")
        self.assertEqual(W.classify(readable, 0, 50000)[0], "UNKNOWN")

    def test_fail2_and_fail3_matched_lines_are_the_real_producer_lines(self):
        _v, m2, _d, _r, _c = W.classify(load_readable("train", "57253127", "0"), 0, 50000)
        self.assertEqual(m2[0][0], "FAIL-2")
        self.assertIn("replicas/replicas", m2[0][4])
        self.assertIn("[gate5-dataonly] F2 the loader opened", m2[0][4])

        _v, m3, _d, _r, _c = W.classify(load_readable("train", "57256638", "0"), 0, 50000)
        self.assertEqual(m3[0][0], "FAIL-3")
        self.assertIn("withheld key(s) present: ['bootstrap_seed']", m3[0][4])

    def test_synthesised_signature_branches_fire(self):
        """FAIL-1, FAIL-4 and FAIL-5 have no historical run, so they are exercised on producer TEXT.

        Each needle below was read out of the emitting source, not out of the handoff table:
          FAIL-1  fullevent_fps_dataloader.py:742
          FAIL-4  cstat_data_only.py:286-291 rendered with DATA_ONLY_BOOTSTRAP_SEED_VALUE = -1 (:124)
          FAIL-5  sbatch_gate5_data_only_train_array.sh:69 (in-job form) and
                  submit_gate5_data_only_n50.sh:223 (submitter form, which cannot reach these logs)
        This is weaker evidence than a real log and is labelled as such; it is not a fixture.
        """
        cases = (
            ("FAIL-1", "[negweight] refined target has bootstrap_seed=None (NOMINAL) — cannot be used"),
            ("FAIL-4", "[gate5-dataonly] write-time: bootstrap_seed is 7, not -1 -- in a data-only "
                       "build the loader draws NO MC factors, so the pinned base driver stamps -1;"),
            ("FAIL-5", "[gate5-do-train][FAIL] collision/no-clobber guard: "
                       "/pscratch/.../GATE5_REPLICA_TRAINING_RECEIPT.json"),
        )
        for expected, line in cases:
            with self.subTest(sig=expected):
                readable = [("stdout", "/x.out", ""), ("stderr", "/x.err", line + "\n")]
                self.assertEqual(W.classify(readable, 0, 50000)[0], expected)

    def test_fail5_matches_both_emitter_variants(self):
        for line in ("[gate5-do-train][FAIL] collision/no-clobber guard: /p/OUT.npz",
                     "collision/no-clobber guard (checkpoints): 14 file(s) already under /p/w_nominal"):
            with self.subTest(line=line[:40]):
                readable = [("stdout", "/x.out", ""), ("stderr", "/x.err", line + "\n")]
                self.assertEqual(W.classify(readable, 0, 50000)[0], "FAIL-5")


# =====================================================================================================
# 2. The substring trap: one signature's text must not satisfy another's.
# =====================================================================================================

class TestSubstringTrap(unittest.TestCase):

    def test_no_needle_is_a_substring_of_another(self):
        needles = [n for _c, n, _m in W.SIGNATURES]
        for i, a in enumerate(needles):
            for j, b in enumerate(needles):
                if i != j:
                    self.assertNotIn(a, b, "needle %r is contained in needle %r; the closed set "
                                           "collapses" % (a, b))

    def test_fail3_line_does_not_trigger_fail1(self):
        """The real trap, from a real log.

        train_57256638_0.err contains the literal text `bootstrap_seed`. FAIL-1's signature is
        `bootstrap_seed=None (NOMINAL)`. A FAIL-1 matcher keyed on `bootstrap_seed` alone would fire on
        the FAIL-3 run -- and FAIL-1 has precedence, so the verdict would be silently wrong.
        """
        readable = load_readable("train", "57256638", "0")
        blob = "".join(t for _l, _p, t in readable)
        self.assertIn("bootstrap_seed", blob, "fixture drift: the trap material is gone")
        self.assertNotIn("bootstrap_seed=None (NOMINAL)", blob)
        self.assertEqual(W.classify(readable, 0, 50000)[0], "FAIL-3")

    def test_config_gate_pass_never_implies_success(self):
        """Measured, not assumed: `"config_gate": "PASS"` is in the stdout of BOTH real train runs.

        A SUCCESS check keyed on a bare "PASS" would fire on every failed run. The receipt token is
        `"status": "PASS"`, which none of the three real runs ever emitted -- 57256638_0 died AT the
        receipt write, which is the whole reason the receipt-write step has never been observed.
        """
        for prefix, job in (("train", "57253127"), ("train", "57256638")):
            with self.subTest(job=job):
                readable = load_readable(prefix, job, "0")
                _v, _m, _d, receipt, cfg = W.classify(readable, 0, 50000)
                self.assertTrue(cfg, "fixture drift: config_gate PASS should be present in %s" % job)
                self.assertFalse(receipt, "%s never wrote a receipt; receipt_pass must be False" % job)

    def test_start_line_does_not_satisfy_the_done_line(self):
        """Both real train runs print `index=0 seed=50000` in a START line and never a DONE line.

        Producer: `[gate5-do-train] index=$INDEX seed=$SEED job=... ` at
        sbatch_gate5_data_only_train_array.sh:114, versus `... DONE index=$INDEX seed=$SEED <ts>` at :124.
        A DONE matcher that only looks for `index=0 seed=50000` reports completion for a run that died
        seconds after startup.
        """
        for job in ("57253127", "57256638"):
            with self.subTest(job=job):
                readable = load_readable("train", job, "0")
                blob = "".join(t for _l, _p, t in readable)
                self.assertIn("index=0 seed=50000", blob, "fixture drift: start line missing")
                self.assertFalse(W.classify(readable, 0, 50000)[2],
                                 "%s has no DONE line; done_seen must be False" % job)

    def test_done_fields_are_anchored_on_the_right(self):
        """A whole-field comparison written as a bare substring is not one.

        `seed=50000` is a prefix of `seed=500001`, and `index=0` of `index=01`. Both must be rejected.
        """
        good = "[gate5-do-train] DONE index=0 seed=50000 2026-08-19T07:00:00Z\n"
        self.assertTrue(W.done_pattern(0, 50000).search(good))
        for bad in ("[gate5-do-train] DONE index=0 seed=500001 2026-08-19T07:00:00Z\n",
                    "[gate5-do-train] DONE index=01 seed=50000 2026-08-19T07:00:00Z\n",
                    "[gate5-do-train] DONE index=0 seed=5000 2026-08-19T07:00:00Z\n"):
            with self.subTest(bad=bad.strip()):
                self.assertIsNone(W.done_pattern(0, 50000).search(bad))

    def test_done_matcher_tolerates_the_trailing_timestamp(self):
        """Anchoring to end-of-line would be wrong: the producer appends `$(date -u ...)`."""
        self.assertTrue(W.done_pattern(0, 50000).search(
            "[gate5-do-train] DONE index=0 seed=50000 2026-08-19T07:00:00Z"))

    def test_success_requires_both_receipt_and_done(self):
        done = "[gate5-do-train] DONE index=0 seed=50000 2026-08-19T07:00:00Z\n"
        receipt = '  "status": "PASS",\n'
        self.assertEqual(W.classify([("stdout", "/x.out", done + receipt)], 0, 50000)[0], "SUCCESS")
        self.assertEqual(W.classify([("stdout", "/x.out", done)], 0, 50000)[0], "UNKNOWN")
        self.assertEqual(W.classify([("stdout", "/x.out", receipt)], 0, 50000)[0], "UNKNOWN")

    def test_a_failure_signature_beats_a_success_marker(self):
        """57256638_0's real shape: it trained fully AND emitted a failure signature."""
        text = ('  "status": "PASS",\n'
                "[gate5-do-train] DONE index=0 seed=50000 2026-08-19T07:00:00Z\n"
                "[gate5-dataonly] write-time: withheld key(s) present: ['bootstrap_seed']\n")
        self.assertEqual(W.classify([("stdout", "/x.out", text)], 0, 50000)[0], "FAIL-3")


# =====================================================================================================
# 3. NO-LOGS, and the exit-code contract (instrument status, never run outcome).
# =====================================================================================================

class TestNoLogsAndExitCodes(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wrtr-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out = StringSink()

    def _copy_fixture(self, prefix, job, task, dest_job="57266000", dest_task="0"):
        for ext in (".out", ".err"):
            shutil.copyfile(
                fixture_path(prefix, job, task, ext),
                os.path.join(self.tmp, "train_%s_%s%s" % (dest_job, dest_task, ext)))

    def _run(self, extra=(), mail=None, sacct=sacct_ok):
        mail = mail or MailSpy()
        argv = ["--job-id", "57266000", "--task-id", "0", "--log-dir", self.tmp] + list(extra)
        rc = W.run(argv, slurm_runner=sacct, mail_runner=mail, stdout=self.out)
        return rc, mail

    def test_missing_logs_but_live_slurm_is_NO_LOGS_and_exits_zero(self):
        rc, mail = self._run()
        self.assertEqual(rc, 0, "NO-LOGS is a successful classification; rc must be 0")
        self.assertIn("NO-LOGS", mail.subject)
        self.assertIn(self.tmp, mail.body, "the body must name the paths that were tried")

    def test_no_logs_and_no_slurm_is_an_instrument_failure(self):
        rc, mail = self._run(sacct=sacct_down)
        self.assertNotEqual(rc, 0, "nothing was observable, so this IS an instrument failure")
        self.assertEqual(mail.calls, [], "must not mail a verdict it does not have")

    def test_every_failing_run_still_exits_zero(self):
        """The distinction this campaign keeps getting wrong: rc reports the SCRIPT, not the RUN.

        A non-zero rc makes wakerctl retry. Retrying a failed training run re-mails and changes nothing.
        """
        for label, prefix, job, task, expected in REAL_RUNS:
            with self.subTest(run=label):
                shutil.rmtree(self.tmp, True)
                os.makedirs(self.tmp)
                self._copy_fixture(prefix, job, task)
                rc, mail = self._run()
                self.assertEqual(rc, 0, "%s classified as %s; that is a SUCCESSFUL classification"
                                        % (label, expected))
                self.assertIn(expected, mail.subject)

    def test_mail_failure_is_the_one_thing_that_exits_non_zero(self):
        self._copy_fixture("train", "57256638", "0")
        rc, mail = self._run(mail=MailSpy(returncode=1))
        self.assertNotEqual(rc, 0, "a failed mail is worth retrying, so rc must be non-zero")
        self.assertIn("FAIL-3", self.out.text, "the undelivered body must reach the event log")

    def test_dry_run_sends_nothing(self):
        self._copy_fixture("train", "57253127", "0")
        rc, mail = self._run(extra=["--dry-run"])
        self.assertEqual(rc, 0)
        self.assertEqual(mail.calls, [])
        self.assertIn("DRY RUN", self.out.text)

    def test_slurm_and_log_verdicts_are_both_reported_when_they_disagree(self):
        """Slurm COMPLETED 0:0 while the log says FAIL-3 must show BOTH, with neither overwritten."""
        self._copy_fixture("train", "57256638", "0")
        completed = ("       JobID      State ExitCode    Elapsed \n"
                     "    57266000  COMPLETED      0:0   02:58:44 \n")
        rc, mail = self._run(sacct=lambda argv: FakeProc(0, completed, ""))
        self.assertEqual(rc, 0)
        self.assertIn("FAIL-3", mail.subject)
        self.assertIn("COMPLETED", mail.body)
        self.assertIn("0:0", mail.body)
        self.assertIn("DISAGREEMENT", mail.body)

    def test_unreadable_slurm_does_not_change_a_log_verdict(self):
        self._copy_fixture("train", "57253127", "0")
        rc, mail = self._run(sacct=sacct_down)
        self.assertEqual(rc, 0)
        self.assertIn("FAIL-2", mail.subject)
        self.assertIn("SLURM STATE UNAVAILABLE", mail.body)


# =====================================================================================================
# 4. The mail itself.
# =====================================================================================================

class TestMailContents(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wrtr-mail-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out = StringSink()

    def _mail_for(self, prefix, job, task):
        for ext in (".out", ".err"):
            shutil.copyfile(fixture_path(prefix, job, task, ext),
                            os.path.join(self.tmp, "train_57266000_0" + ext))
        mail = MailSpy()
        rc = W.run(["--job-id", "57266000", "--task-id", "0", "--log-dir", self.tmp],
                   slurm_runner=sacct_ok, mail_runner=mail, stdout=self.out)
        self.assertEqual(rc, 0)
        return mail

    def test_recipient_and_mail_command_defaults(self):
        mail = self._mail_for("train", "57256638", "0")
        argv = mail.calls[-1][0]
        self.assertEqual(argv[0], "/usr/bin/mail")
        self.assertEqual(argv[-1], "josephrb@nersc.gov")
        self.assertEqual(argv[1], "-s")

    def test_subject_carries_the_verdict_for_a_phone_notification(self):
        self.assertTrue(self._mail_for("train", "57253127", "0").subject.startswith(
            "[MNV] 57266000_0 FAIL-2 -- "))

    def test_standing_constraints_appear_verbatim(self):
        for prefix, job in (("train", "57253127"), ("train", "57256638"), ("target", "57235710")):
            with self.subTest(job=job):
                self.assertIn(W.STANDING_CONSTRAINTS, self._mail_for(prefix, job, "0").body)
                self.assertIn("A PASS IS NOT AUTHORISATION",
                              self._mail_for(prefix, job, "0").body)

    def test_body_reports_slurm_state_exit_code_and_elapsed(self):
        body = self._mail_for("train", "57256638", "0").body
        for token in ("FAILED", "1:0", "02:58:44", "JobID"):
            self.assertIn(token, body)

    def test_unknown_is_rendered_loudly_with_generous_tails(self):
        mail = self._mail_for("target", "57235710", "0")
        self.assertIn("UNKNOWN", mail.subject)
        self.assertIn("UNKNOWN IS NOT AN ERROR", mail.body)
        self.assertIn("FOURTH THING", mail.body)
        self.assertIn("GENEROUS TAILS", mail.body)
        self.assertIn("ADDR2LINE: unbound variable", mail.body,
                      "the reader must be able to see the ACTUAL failure")
        self.assertIn("EMPTY", mail.body, "an empty stream must be reported as empty, not omitted")

    def test_matched_signature_is_quoted_with_context(self):
        body = self._mail_for("train", "57256638", "0").body
        self.assertIn("MATCHED FAIL-3", body)
        self.assertIn("withheld key(s) present", body)
        self.assertIn("degenerate event-feature columns", body,
                      "surrounding context lines should be included")

    def test_body_names_both_log_paths(self):
        body = self._mail_for("train", "57253127", "0").body
        self.assertIn("train_57266000_0.out", body)
        self.assertIn("train_57266000_0.err", body)


# =====================================================================================================
# 5. Self-containment: no repo imports, stdlib only.
# =====================================================================================================

class TestSelfContainment(unittest.TestCase):

    def test_imports_are_stdlib_only_and_no_syspath_edits(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "watch_report_train_run.py")
        with open(path) as handle:
            source = handle.read()
        allowed = {"argparse", "os", "re", "subprocess", "sys", "datetime"}
        found = set()
        for line in source.splitlines():
            s = line.strip()
            if s.startswith("import "):
                found.add(s[len("import "):].split()[0].split(".")[0])
            elif s.startswith("from ") and " import " in s:
                found.add(s[len("from "):].split()[0].split(".")[0])
        self.assertTrue(found <= allowed,
                        "non-stdlib or repo import(s) present: %r" % (sorted(found - allowed),))

    def test_no_executable_sys_path_manipulation(self):
        """Positional, via the AST -- a substring check cannot express 'in executable code'.

        The first version of this test was `assertNotIn("sys.path", source)` and it failed on the
        module docstring's own sentence promising not to edit sys.path. An over-broad check that fires
        on prose about the rule is not a check on the rule; parsing makes the requirement positional.
        """
        import ast
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "watch_report_train_run.py")
        with open(path) as handle:
            tree = ast.parse(handle.read())
        hits = [node.lineno for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and node.attr == "path"
                and isinstance(node.value, ast.Name) and node.value.id == "sys"]
        self.assertEqual(hits, [], "executable sys.path reference(s) at line(s) %r" % (hits,))

    def test_no_repo_module_is_importable_from_the_scripts_own_imports(self):
        """Belt-and-braces on the import allowlist: none of the named modules is a repo file."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for name in ("argparse", "os", "re", "subprocess", "sys", "datetime"):
            mod = __import__(name)
            f = getattr(mod, "__file__", None)
            if f:
                self.assertFalse(os.path.abspath(f).startswith(repo_root + os.sep),
                                 "%s resolves inside the repo at %s" % (name, f))

    def test_script_does_not_require_the_fixture_directory(self):
        source_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(source_dir, "watch_report_train_run.py")) as handle:
            source = handle.read()
        self.assertNotIn("test_fixtures_watch_report", source)


class StringSink(object):
    def __init__(self):
        self.text = ""

    def write(self, s):
        self.text += s


# =====================================================================================================
# Mutation / power run.
# =====================================================================================================

MUTATIONS = (
    ("neuter every signature (closed set becomes empty -> everything UNKNOWN)",
     lambda: setattr(W, "SIGNATURES", ())),
    ("collapse the classifier to a constant FAIL-3",
     lambda: setattr(W, "classify",
                     lambda readable, i, s: ("FAIL-3", [("FAIL-3", "stub", "/x", 1, "x")],
                                             False, False, False))),
    ("un-anchor the DONE matcher (bare substring, no right-hand boundary)",
     lambda: setattr(W, "done_pattern",
                     lambda i, s: __import__("re").compile(r"index=%d\s+seed=%d" % (i, s)))),
    ("weaken the receipt token to a bare PASS",
     lambda: setattr(W, "RECEIPT_PASS_TOKEN", "PASS")),
    ("make FAIL-1 match on bare bootstrap_seed (the real substring trap)",
     lambda: setattr(W, "SIGNATURES",
                     (("FAIL-1", "bootstrap_seed", "over-broad"),) + W.SIGNATURES[1:])),
)


def mutation_run():
    """Show the tests have power: break a matcher, watch the suite go red.

    A test that cannot fail measures nothing. Each mutation below is a plausible implementation of the
    same intent, and each must be caught.
    """
    import copy
    originals = {name: getattr(W, name) for name in
                 ("SIGNATURES", "classify", "done_pattern", "RECEIPT_PASS_TOKEN")}
    loader = unittest.TestLoader()
    all_ok = True
    for description, mutate in MUTATIONS:
        for name, value in originals.items():
            setattr(W, name, copy.copy(value))
        mutate()
        suite = unittest.TestSuite([
            loader.loadTestsFromTestCase(TestRealRunClassification),
            loader.loadTestsFromTestCase(TestSubstringTrap),
        ])
        result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w")).run(suite)
        broke = len(result.failures) + len(result.errors)
        verdict = "CAUGHT" if broke else "*** NOT CAUGHT ***"
        print("MUTATION: %s\n    -> %d test(s) failed  %s" % (description, broke, verdict))
        if not broke:
            all_ok = False
    for name, value in originals.items():
        setattr(W, name, value)
    print("\nmutation run: %s" % ("all mutations caught" if all_ok
                                  else "AT LEAST ONE MUTATION SURVIVED -- the suite lacks power"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    if "--mutation" in sys.argv:
        sys.exit(mutation_run())
    unittest.main(verbosity=2)
