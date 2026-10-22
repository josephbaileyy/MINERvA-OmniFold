#!/usr/bin/env python3
"""Does `build_all.sh` refuse a build it did not perform?

WHAT THIS TESTS AND WHY IT EXISTS
---------------------------------
On 2026-08-19 `build_all.sh` exited 0, printed all three "building" lines and passed the
containment check while `latexmk` reported "Nothing to do" for every target and nothing
recompiled -- the validated PDFs were from 2026-08-11 and 2026-08-15. The procedure was
fixed by hand the same day; the SCRIPT could still not tell "built and passed" from
"skipped and passed". These tests pin the difference.

The failing run is reproduced directly: a fake `latexmk` that prints "Nothing to do" and
touches nothing, over pre-existing PDFs backdated a week. That is the ACTUAL 2026-08-19
transcript, not an analogue of it, and the test asserts the script now exits non-zero and
never reaches the containment stage.

WHAT IS FAKED AND WHAT IS NOT
-----------------------------
`latexmk` is faked -- there is no TeX toolchain assumption here, and the point under test is
the script's decision, not LaTeX's output. The SCRIPT is the real one, copied into a sandbox
and run unmodified. `check_dead_containment.py` is replaced by a stub that records whether
it was reached: its own contract (every skip is fatal, `--source-only` must never be passed
from the build) is deliberate and correct, and nothing here changes or re-tests it -- only
whether the build lets it see a stale PDF.
"""

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "build_all.sh"
# main_records (2026-10-21) is the internal records document; it is last because it reads main_note.aux.
TARGETS = ("main_note", "main_primer", "main_paper", "pet_note", "main_records")
SHARED = ("preamble.tex", "values.tex", "technote.bib")

# A fake latexmk. Its behaviour comes from BUILD_TEST_MODE so one shim covers every scenario.
FAKE_LATEXMK = r"""#!/usr/bin/env bash
# args: -g -pdf -interaction=nonstopmode -halt-on-error <target>.tex
tex="${!#}"
t="${tex%.tex}"
echo "latexmk: fake invoked for $tex with args: $*" >> "$BUILD_TEST_LOG"
# Every real latexmk run leaves a .log. The clean one carries the T1/cmtt font-shape warning
# every real build prints, so the happy path also proves that "undefined" alone is NOT flagged.
clean_log() { printf "LaTeX Font Warning: Font shape \`T1/cmtt/m/it' undefined\n" > "${t}.log"; }
unresolved_log() {
  printf "LaTeX Warning: Reference \`sec:fake' on page 1 undefined on input line 3.\n" > "${t}.log"
  printf "LaTeX Warning: There were undefined references.\n" >> "${t}.log"
}
case "$BUILD_TEST_MODE" in
  nothing-to-do)
    # The 2026-08-19 transcript, verbatim in shape: exit 0, touch nothing.
    echo "Latexmk: Nothing to do for '$tex'."
    ;;
  build)
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"; clean_log
    ;;
  build-no-log)
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"; rm -f "${t}.log"
    ;;
  multiply-defined)
    # LaTeX's own duplicate-label warnings, in the records build only; the other targets are clean.
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"; clean_log
    if [ "$t" = "main_records" ]; then
      printf "LaTeX Warning: Label \`app:history' multiply defined.\n" >> "${t}.log"
      printf "LaTeX Warning: There were multiply-defined labels.\n" >> "${t}.log"
    fi
    ;;
  unresolved-persist)
    # The KNOWN_ISSUES-50 cold tree, when one more invocation does NOT resolve it.
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"; unresolved_log
    ;;
  unresolved-citation-persist)
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"
    printf "LaTeX Warning: Citation 'fake2026' on page 1 undefined on input line 3.\n" > "${t}.log"
    ;;
  unresolved-first-invocation-only)
    # The KNOWN_ISSUES-50 cold tree as measured: unresolved after one invocation, clean after two.
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"
    if [ -f "${t}.invoked" ]; then clean_log; else unresolved_log; touch "${t}.invoked"; fi
    ;;
  build-note-only)
    if [ "$t" = "main_note" ]; then printf '%%PDF-1.5 fake\n' > "${t}.pdf"; clean_log
    else echo "Latexmk: Nothing to do for '$tex'."; fi
    ;;
  latexmk-semantics)
    # Models latexmk's OWN rule rather than a scenario I chose: -g forces processing, and
    # without it an up-to-date PDF produces "Nothing to do". This is the fixture that makes
    # the -g flag BEHAVIOURALLY load-bearing instead of only textually present.
    forced=no
    for a in "$@"; do if [ "$a" = "-g" ]; then forced=yes; fi; done
    if [ "$forced" = "no" ] && [ -f "${t}.pdf" ]; then
      stale=no
      for s in preamble.tex values.tex technote.bib "$tex"; do
        if [ -e "$s" ] && [ "$s" -nt "${t}.pdf" ]; then stale=yes; fi
      done
      if [ "$stale" = "no" ]; then
        echo "Latexmk: Nothing to do for '$tex'."
        exit 0
      fi
    fi
    printf '%%PDF-1.5 fake\n' > "${t}.pdf"; clean_log
    ;;
  build-then-edit-source)
    printf '%%PDF-1.5 fake\n' > "${t}.pdf"; clean_log
    sleep 1
    printf 'edited during the build\n' >> values.tex
    ;;
  fail)
    echo "! LaTeX Error: fake failure" >&2
    exit 12
    ;;
  *)
    echo "fake latexmk: unknown BUILD_TEST_MODE '$BUILD_TEST_MODE'" >&2
    exit 99
    ;;
esac
"""

FAKE_CHECKER = r"""#!/usr/bin/env python3
import os, sys
with open(os.environ["BUILD_TEST_LOG"], "a") as fh:
    fh.write("containment: reached with args %r\n" % (sys.argv[1:],))
sys.exit(int(os.environ.get("BUILD_TEST_CONTAINMENT_RC", "0")))
"""


# The Sec. IV receipt check (check_sec4_receipts.py, G11) reads receipts that the sandbox does not have; it is
# stubbed like the containment checker and its own behaviour is tested in test_check_sec4_receipts.py.
FAKE_SEC4 = r"""#!/usr/bin/env python3
import os, sys
with open(os.environ["BUILD_TEST_LOG"], "a") as fh:
    fh.write("sec4: reached with args %r\n" % (sys.argv[1:],))
mode = "self" if "--self-test" in sys.argv[1:] else "check"
sys.exit(1 if os.environ.get("BUILD_TEST_SEC4_FAIL") == mode else 0)
"""

# The body-pointer lint (check_body_pointers.py) reads the note sources the sandbox does not have; it is stubbed like
# the other checkers, and its own fixtures run in its --self-test.
FAKE_BODY_LINT = r"""#!/usr/bin/env python3
import os, sys
with open(os.environ["BUILD_TEST_LOG"], "a") as fh:
    fh.write("bodylint: reached with args %r\n" % (sys.argv[1:],))
mode = "self" if "--self-test" in sys.argv[1:] else "check"
sys.exit(1 if os.environ.get("BUILD_TEST_BODYLINT_FAIL") == mode else 0)
"""

# The records-pin check (check_note_records.py pin, plan commit 3) reads git and the note sources the sandbox does not
# have; it is stubbed like the others, and its own behaviour is tested in PinCheckTest and its --self-test-pin.
FAKE_PIN = r"""#!/usr/bin/env python3
import os, sys
with open(os.environ["BUILD_TEST_LOG"], "a") as fh:
    fh.write("pin: reached with args %r\n" % (sys.argv[1:],))
mode = "self" if "--self-test-pin" in sys.argv[1:] else "check"
sys.exit(1 if os.environ.get("BUILD_TEST_PIN_FAIL") == mode else 0)
"""


class BuildAllHarness(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.sandbox = Path(tempfile.mkdtemp(prefix="build-all-test-"))
        self.addCleanup(shutil.rmtree, self.sandbox, True)
        self.bin = self.sandbox / "bin"
        self.bin.mkdir()
        self.log = self.sandbox / "calls.log"
        self.log.write_text("")

        # The REAL script, unmodified. It cds to its own directory, so a copy is enough.
        shutil.copyfile(str(SCRIPT), str(self.sandbox / "build_all.sh"))

        for name in SHARED:
            (self.sandbox / name).write_text("%% fake source %s\n" % name)
        for t in TARGETS:
            (self.sandbox / (t + ".tex")).write_text("%% fake driver %s\n" % t)

        self._install(self.bin / "latexmk", FAKE_LATEXMK)
        self._install(self.sandbox / "check_dead_containment.py", FAKE_CHECKER)
        self._install(self.sandbox / "check_sec4_receipts.py", FAKE_SEC4)
        self._install(self.sandbox / "check_body_pointers.py", FAKE_BODY_LINT)
        self._install(self.sandbox / "check_note_records.py", FAKE_PIN)

    def _install(self, path, body):
        path.write_text(body)
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def stale_pdfs(self, days=8):
        """Pre-existing PDFs from a previous week -- the 08-11/08-15 artifacts."""
        old = time.time() - days * 86400
        for t in TARGETS:
            p = self.sandbox / (t + ".pdf")
            p.write_text("%PDF-1.5 stale\n")
            os.utime(str(p), (old, old))
            # The stale tree's clean logs came with it, so a "Nothing to do" run is refused by
            # the marker check itself and not, incidentally, by the missing-log check.
            lg = self.sandbox / (t + ".log")
            lg.write_text("stale clean log\n")
            os.utime(str(lg), (old, old))

    def run_build(self, mode, containment_rc="0", drop_latexmk=False, sec4_fail="", bodylint_fail="", pin_fail=""):
        env = dict(os.environ)
        # NERSC exports `module` as a Bash function and recreates it through
        # BASH_ENV.  If either reaches the fixture shell, build_all.sh loads the
        # real TeX module and its prepended PATH bypasses FAKE_LATEXMK.  Remove
        # only that shell initialization from the harness; production builds
        # still exercise the module load normally.
        env.pop("BASH_ENV", None)
        env.pop("BASH_FUNC_module%%", None)
        env.pop("BASH_FUNC_ml%%", None)
        env["BUILD_TEST_MODE"] = mode
        env["BUILD_TEST_LOG"] = str(self.log)
        env["BUILD_TEST_CONTAINMENT_RC"] = containment_rc
        env["BUILD_TEST_SEC4_FAIL"] = sec4_fail   # "check" or "self": that sec4 invocation exits 1
        env["BUILD_TEST_BODYLINT_FAIL"] = bodylint_fail   # likewise for the body-pointer lint
        env["BUILD_TEST_PIN_FAIL"] = pin_fail             # likewise for the records-pin check
        # A minimal PATH plus the shim dir, so the fake latexmk is the only one reachable.
        base = "/usr/bin:/bin:/usr/sbin:/sbin"
        env["PATH"] = base if drop_latexmk else "%s:%s" % (self.bin, base)
        proc = subprocess.run(
            ["bash", "build_all.sh"], cwd=str(self.sandbox), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.calls = self.log.read_text()
        return proc

    def assert_containment_not_reached(self, proc):
        self.assertNotIn("containment: reached", self.calls,
                         "the containment check was handed artifacts this run did not build; "
                         "it would report a PASS nobody earned.\n%s" % proc.stdout)


class TestTheObservedFailure(BuildAllHarness):
    def test_nothing_to_do_over_stale_pdfs_now_FAILS(self):
        """THE 2026-08-19 RUN. Before the fix this exited 0 with a green containment line."""
        self.stale_pdfs()
        proc = self.run_build("nothing-to-do")
        self.assertNotEqual(0, proc.returncode,
                            "a run that recompiled nothing still reports success:\n" + proc.stdout)
        self.assertIn("was NOT written by this run", proc.stdout)
        self.assert_containment_not_reached(proc)

    def test_it_names_the_target_that_was_not_built(self):
        self.stale_pdfs()
        proc = self.run_build("nothing-to-do")
        self.assertIn("main_note.pdf", proc.stdout)

    def test_the_stale_pdf_is_newer_than_its_sources_which_is_why_that_check_is_not_enough(self):
        """The reason the marker exists. The 08-11 PDFs WERE newer than sources nobody had
        touched since, so a sources-only comparison passes precisely the run that failed."""
        self.stale_pdfs(days=8)
        old = time.time() - 30 * 86400
        for name in SHARED + tuple(t + ".tex" for t in TARGETS):
            os.utime(str(self.sandbox / name), (old, old))
        for t in TARGETS:
            pdf = self.sandbox / (t + ".pdf")
            for name in SHARED:
                self.assertGreater(pdf.stat().st_mtime, (self.sandbox / name).stat().st_mtime)
        proc = self.run_build("nothing-to-do")
        self.assertNotEqual(0, proc.returncode,
                            "the sources-only invariant held and the run still had to fail")
        self.assertIn("was NOT written by this run", proc.stdout)

    def test_a_partial_build_fails_on_the_target_that_was_skipped(self):
        """One target rebuilding does not license the other two."""
        self.stale_pdfs()
        proc = self.run_build("build-note-only")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("main_primer.pdf", proc.stdout)
        self.assertIn("was NOT written by this run", proc.stdout)
        self.assert_containment_not_reached(proc)


class TestTheHappyPath(BuildAllHarness):
    def test_a_real_build_passes_and_reaches_containment(self):
        proc = self.run_build("build")
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("containment: reached", self.calls)
        for t in TARGETS:
            self.assertIn("OK   %s.pdf written by this run" % t, proc.stdout)

    def test_the_build_is_forced_so_nothing_to_do_cannot_arise(self):
        self.stale_pdfs()
        self.run_build("build")
        for t in TARGETS:
            self.assertIn("-g", self.calls)
            self.assertIn("%s.tex" % t, self.calls)
        self.assertEqual(len(TARGETS), self.calls.count("latexmk: fake invoked"),
                         "expected exactly one forced latexmk run per target")

    def test_the_force_flag_is_what_makes_an_up_to_date_pdf_rebuild(self):
        """Against a fake that follows latexmk's own up-to-date rule: with `-g` the build
        happens and passes; without it the shim would say "Nothing to do" and the marker
        check would refuse. This is why `-g` is not decoration."""
        self.stale_pdfs(days=8)
        old = time.time() - 30 * 86400
        for name in SHARED + tuple(t + ".tex" for t in TARGETS):
            os.utime(str(self.sandbox / name), (old, old))
        proc = self.run_build("latexmk-semantics")
        self.assertEqual(0, proc.returncode, proc.stdout)
        # The shim's line, not the bare phrase: the script's own banner says "Nothing to do"
        # while explaining why it cannot pass, and asserting on the phrase matched that.
        self.assertNotIn("Latexmk: Nothing to do", proc.stdout)
        for t in TARGETS:
            self.assertIn("OK   %s.pdf written by this run" % t, proc.stdout)

    def test_containment_still_gates_the_build(self):
        """The new proof stage must not have become a substitute for the old check."""
        proc = self.run_build("build", containment_rc="1")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("containment: reached", self.calls)

    def test_a_failing_sec4_check_fails_the_build_before_page_counts(self):
        """G11: a printed Sec. IV value that disagrees with its receipt must stop the build."""
        for which in ("check", "self"):
            with self.subTest(sec4_fails=which):
                self.log.write_text("")
                proc = self.run_build("build", sec4_fail=which)
                self.assertNotEqual(0, proc.returncode, proc.stdout)
                self.assertIn("sec4: reached", self.calls)
                self.assertNotIn("page counts", proc.stdout)

    def test_a_failing_body_pointer_lint_fails_the_build_before_any_latexmk(self):
        """An internal pointer printed in the note body must stop the build, and cheaply: before any LaTeX run."""
        for which in ("check", "self"):
            with self.subTest(bodylint_fails=which):
                self.log.write_text("")
                proc = self.run_build("build", bodylint_fail=which)
                self.assertNotEqual(0, proc.returncode, proc.stdout)
                self.assertIn("bodylint: reached", self.calls)
                self.assertNotIn("latexmk: fake invoked", self.calls)

    def test_a_failing_records_pin_fails_the_build_before_any_latexmk(self):
        """Plan commit 3: a NoteRecords2026 pin that is not a merged ancestor holding every cited tag stops the build."""
        for which in ("check", "self"):
            with self.subTest(pin_fails=which):
                self.log.write_text("")
                proc = self.run_build("build", pin_fail=which)
                self.assertNotEqual(0, proc.returncode, proc.stdout)
                self.assertIn("pin: reached", self.calls)
                self.assertNotIn("latexmk: fake invoked", self.calls)

    def test_the_records_pin_runs_and_its_self_test_runs_first(self):
        self.run_build("build")
        self.assertIn("pin: reached with args ['pin']", self.calls)
        self.assertLess(self.calls.index("pin: reached with args ['--self-test-pin']"),
                        self.calls.index("pin: reached with args ['pin']"))

    def test_the_body_pointer_self_test_runs_before_its_verdict(self):
        self.run_build("build")
        self.assertLess(self.calls.index("bodylint: reached with args ['--self-test']"),
                        self.calls.index("bodylint: reached with args []"))

    def test_the_sec4_self_test_runs_before_its_verdict(self):
        self.run_build("build")
        self.assertLess(self.calls.index("sec4: reached with args ['--self-test']"),
                        self.calls.index("sec4: reached with args []"))

    def test_the_self_test_runs_before_the_verdict(self):
        self.run_build("build")
        self.assertIn("containment: reached with args ['--self-test']", self.calls)
        self.assertIn("containment: reached with args []", self.calls)
        self.assertLess(self.calls.index("['--self-test']"), self.calls.index("with args []"),
                        "the regex power test must precede the verdict it licenses")

    def test_page_counts_cannot_fail_a_build_that_passed(self):
        """`set -o pipefail` plus a missing or unhappy pdfinfo used to abort the script AFTER
        the builds and containment had passed, turning an informational stage into a gate."""
        proc = self.run_build("build")
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("page counts", proc.stdout)
        self.assertIn("main_note.pdf", proc.stdout)


class TestOtherRefusals(BuildAllHarness):
    def test_a_failing_latexmk_fails_the_build_and_stops_before_containment(self):
        self.stale_pdfs()
        proc = self.run_build("fail")
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("latexmk failed for main_note.tex", proc.stdout)
        self.assert_containment_not_reached(proc)

    def test_a_missing_latexmk_is_named_rather_than_inferred(self):
        proc = self.run_build("build", drop_latexmk=True)
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("latexmk not found", proc.stdout)
        self.assert_containment_not_reached(proc)

    def test_a_source_edited_during_the_build_fails(self):
        """The other direction: the PDF was written by this run but is already out of date."""
        proc = self.run_build("build-then-edit-source")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("is NEWER than", proc.stdout)
        self.assert_containment_not_reached(proc)


class TestUnresolvedReferences(BuildAllHarness):
    """KNOWN_ISSUES row 50: a cold tree exited 0 with `??` in all three PDFs."""

    def test_unresolved_after_the_extra_invocation_FAILS_before_containment(self):
        proc = self.run_build("unresolved-persist")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("main_note.pdf has unresolved references after 2 latexmk", proc.stdout)
        self.assertIn("Reference `sec:fake'", proc.stdout)
        self.assertEqual(2, self.calls.count("fake invoked for main_note.tex"),
                         "the extra cold-tree invocation must be tried exactly once")
        self.assert_containment_not_reached(proc)

    def test_an_unresolved_citation_alone_also_FAILS(self):
        proc = self.run_build("unresolved-citation-persist")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("has unresolved references", proc.stdout)
        self.assert_containment_not_reached(proc)

    def test_the_cold_tree_as_measured_converges_on_the_extra_invocation_and_passes(self):
        proc = self.run_build("unresolved-first-invocation-only")
        self.assertEqual(0, proc.returncode, proc.stdout)
        for t in TARGETS:
            self.assertEqual(2, self.calls.count("fake invoked for %s.tex" % t), self.calls)
            self.assertIn("OK   %s.pdf written by this run" % t, proc.stdout)
        self.assertIn("containment: reached", self.calls)

    def test_a_clean_log_takes_one_invocation_and_font_shape_undefined_is_not_flagged(self):
        proc = self.run_build("build")
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertNotIn("has unresolved references after latexmk invocation", proc.stdout)
        self.assertEqual(len(TARGETS), self.calls.count("latexmk: fake invoked"), self.calls)
        self.assertIn("Font shape", (self.sandbox / "main_note.log").read_text())

    def test_a_missing_log_FAILS_rather_than_passing_unread(self):
        proc = self.run_build("build-no-log")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("main_note.log does not exist", proc.stdout)
        self.assert_containment_not_reached(proc)


class TestMultiplyDefinedLabels(BuildAllHarness):
    """Item 7 (2026-10-21): a duplicate label prints a wrong number with no `??`, so the log check must catch it."""

    def test_a_multiply_defined_label_FAILS_before_containment(self):
        proc = self.run_build("multiply-defined")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertIn("main_records.pdf has multiply-defined labels", proc.stdout)
        self.assertIn("Label `app:history' multiply defined", proc.stdout)
        self.assert_containment_not_reached(proc)

    def test_a_duplicate_label_is_not_retried(self):
        """It does not converge, so it must fail at once rather than spend the cold-tree invocation."""
        self.run_build("multiply-defined")
        self.assertEqual(1, self.calls.count("fake invoked for main_records.tex"), self.calls)

    def test_the_clean_targets_before_it_still_report_ok(self):
        proc = self.run_build("multiply-defined")
        for t in ("main_note", "main_primer", "main_paper", "pet_note"):
            self.assertIn("OK   %s.pdf written by this run; no unresolved references and no multiply-defined" % t,
                          proc.stdout)


class TestRecordsBuildOrder(BuildAllHarness):
    """main_records reads main_note.aux through xr-hyper, so it must be built after main_note -- and last, so the
    order of the earlier targets and their messages is unchanged."""

    def test_records_are_built_last_and_after_the_note(self):
        self.run_build("build")
        order = [line.split("fake invoked for ")[1].split(" ")[0] for line in self.calls.splitlines()
                 if "fake invoked for " in line]
        self.assertEqual([t + ".tex" for t in TARGETS], order, self.calls)
        self.assertEqual("main_records.tex", order[-1])


class TestContractsThatMustNotDrift(unittest.TestCase):
    """Static properties of the real script. The containment contract is not mine to change."""

    def setUp(self):
        self.text = SCRIPT.read_text()

    def test_source_only_is_never_passed_from_the_build(self):
        for line in self.text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            self.assertNotIn("--source-only", line,
                             "passing --source-only from the build restores the exact defect "
                             "the 2026-08-12 contract change removed, and would look like a fix")

    def test_the_containment_stage_still_runs_both_halves_and_its_self_test(self):
        self.assertIn("python3 check_dead_containment.py --self-test", self.text)
        self.assertIn("\npython3 check_dead_containment.py\n", self.text)

    def test_a_missing_python3_is_still_fatal(self):
        self.assertIn("FAIL python3 not found", self.text)

    def test_the_build_is_forced_and_the_marker_is_stamped_before_any_build(self):
        self.assertIn("latexmk -g -pdf", self.text)
        body = self.text
        marker_at = body.index('marker="$(mktemp')
        build_at = body.index("latexmk -g -pdf")
        self.assertLess(marker_at, build_at,
                        "the marker must be stamped BEFORE the first build, or a PDF written "
                        "by this run cannot be told from one that predates it")

    def test_it_parses_under_bash(self):
        proc = subprocess.run(["bash", "-n", str(SCRIPT)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout)


MUTANTS = [
    ("m1-drop-the-force-flag", "latexmk -g -pdf", "latexmk -pdf"),
    ("m2-drop-the-marker-check",
     'if [ ! "${t}.pdf" -nt "$marker" ]; then', "if false; then"),
    ("m3-drop-the-source-freshness-check",
     'if [ -e "$s" ] && [ "$s" -nt "${t}.pdf" ]; then', "if false; then"),
    ("m4-warn-instead-of-failing",
     '    echo "       Delete ${t}.pdf and its .aux/.fls/.fdb_latexmk, then re-run."\n    exit 1',
     '    echo "       Delete ${t}.pdf and its .aux/.fls/.fdb_latexmk, then re-run."'),
    ("m5-let-a-failed-latexmk-through", "if ! latexmk -g -pdf", "if ! : latexmk -g -pdf"),
    ("m6-drop-the-final-reference-check",
     'if grep -Eq "$unresolved_re" "${t}.log"; then', "if false; then"),
    ("m7-no-extra-invocation", "max_invocations=2", "max_invocations=1"),
    ("m8-accept-a-missing-log", 'if [ ! -f "${t}.log" ]; then', "if false; then"),
    ("m9-drop-the-multiply-defined-check", 'if grep -Eq "$multidef_re" "${t}.log"; then', "if false; then"),
    ("m10-build-the-records-before-the-note", "targets=(main_note main_primer main_paper pet_note main_records)",
     "targets=(main_records main_note main_primer main_paper pet_note)"),
    ("m11-drop-the-records-pin", "python3 check_note_records.py pin\n", "true\n"),
    ("m12-drop-the-records-pin-self-test", "python3 check_note_records.py --self-test-pin", "true"),
]


def run_mutations():
    src = SCRIPT.read_text()
    tmp = Path(tempfile.mkdtemp(prefix="build-all-mutants-"))
    print("=== mutation run: %d mutants against %s" % (len(MUTANTS), SCRIPT.name), flush=True)
    caught = 0
    for name, old, new in MUTANTS:
        if old not in src:
            print("%-40s UNAPPLIED (anchor text not found -- stale mutant)" % name, flush=True)
            continue
        target = tmp / "build_all.sh"
        target.write_text(src.replace(old, new, 1))
        env = dict(os.environ, BUILD_ALL_SCRIPT=str(target))
        proc = subprocess.run([sys.executable, "-m", "unittest", "-q", Path(__file__).stem],
                              cwd=str(HERE), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        killed = proc.returncode != 0
        caught += 1 if killed else 0
        first = ""
        for line in proc.stdout.splitlines():
            if line.startswith("FAIL:") or line.startswith("ERROR:"):
                first = " <- " + line.split(" (")[0]
                break
        print("%-40s %s%s" % (name, "CAUGHT" if killed else "SURVIVED (test is decorative)",
                              first), flush=True)
    print("=== %d/%d mutants caught" % (caught, len(MUTANTS)), flush=True)
    shutil.rmtree(tmp, True)
    return 0 if caught == len(MUTANTS) else 1


class GatedMacroDetectorTest(unittest.TestCase):
    r"""Keep `gated_macro_usages` proven while `GATED_NW_MACROS` is EMPTY.

    The negweight durability step ungated all twelve production `\nw*` macros, which left the
    declared gated set empty. With nothing declared the detector iterates over nothing and its
    caller reports success by looking at nothing -- a check that cannot fail, which is the defect
    shape `check_dead_containment.py`'s own header exists to argue against. The production set
    being empty is correct; the detector going unexercised is not.

    So the mechanism is tested against a SYNTHETIC note directory with the gated set injected,
    in BOTH directions -- a filter needs a test that it fires and a test that it does not. If a
    later lane re-gates a macro, these tests already cover the machinery it will rely on.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gatedmacro-"))
        # `values.tex` is skipped by the detector by design (definitions are not usages), so a
        # definition here must NOT be reported even though it names a gated macro.
        (self.tmp / "values.tex").write_text(r"\newcommand{\nwFake}{0.986}" + "\n")
        self.mod = self._load()

    def tearDown(self):
        shutil.rmtree(self.tmp, True)

    def _load(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cdc_under_test", str(HERE / "check_dead_containment.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.GATED_NW_MACROS = ("nwFake",)
        return mod

    def _run(self, body):
        (self.tmp / "body.tex").write_text(body + "\n")
        return self.mod.gated_macro_usages(self.tmp)

    def test_live_gated_usage_is_reported(self):
        """The direction that matters: an un-struck gated macro must be FOUND."""
        live, struck = self._run(r"agreement of $\nwFake$ across the plane")
        self.assertEqual(len(live), 1, f"detector missed a live gated usage: {live} {struck}")
        self.assertIn("body.tex:1", live[0])
        self.assertEqual(struck, [])

    def test_struck_gated_usage_is_not_reported(self):
        """The opposite direction: a properly struck usage must NOT be flagged."""
        live, struck = self._run(r"agreement of $\dead{\nwFake}$ across the plane")
        self.assertEqual(live, [], f"detector flagged a struck usage: {live}")
        self.assertEqual(len(struck), 1)

    def test_struck_inside_SI_wrapper_is_not_reported(self):
        r"""`\dead{\SI{\nwFake}{\percent}}` is the real idiom and must read as struck.

        This is the shape the note actually uses. `\SI{\dead{x}}{\percent}` is invalid siunitx and
        broke the note build for four hours on 2026-08-21, so the wrapper is always outside.
        """
        live, struck = self._run(r"to \dead{\SI{\nwFake}{\percent}} of the total")
        self.assertEqual(live, [], f"detector flagged a struck \\SI usage: {live}")
        self.assertEqual(len(struck), 1)

    def test_macro_named_as_prose_is_not_a_usage(self):
        r"""`\texttt{\textbackslash nwFake}` prints the NAME; a gate notice must be able to say
        which macros it gates without tripping itself."""
        live, struck = self._run(r"the gated set is \texttt{\textbackslash nwFake} and no other")
        self.assertEqual((live, struck), ([], []))

    def test_definition_in_values_tex_is_not_a_usage(self):
        """setUp put a gated definition in values.tex; the detector must skip that file."""
        live, struck = self._run("no macros here at all")
        self.assertEqual((live, struck), ([], []))

    def test_longer_macro_name_is_not_a_prefix_match(self):
        r"""`\nwFakeExtra` is a different macro. A prefix match would gate it by accident."""
        live, struck = self._run(r"value $\nwFakeExtra$ is unrelated")
        self.assertEqual((live, struck), ([], []))

    def test_production_set_is_empty_and_that_is_deliberate(self):
        """Pin the current state so a silent re-gating cannot slip in unexplained.

        Not a value judgement: if a lane re-gates something it should edit this assertion in the
        same commit, which is the same discipline `GATED_NW_MACROS` exists to impose on the tex.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cdc_pristine", str(HERE / "check_dead_containment.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(
            mod.GATED_NW_MACROS, (),
            "GATED_NW_MACROS changed. If you re-gated a macro, update this test in the same "
            "commit and say which macro and on whose authority.")


class ResultLineNamesItsObjectTest(unittest.TestCase):
    """KNOWN_ISSUES row 64: the checker's verdict must name the object it was computed on.

    A synthetic note directory (outside any git tree) with fake PDFs that are plain text, read
    through a `pdftotext` shim that copies them -- so the PDF stage really runs, over bytes this
    test controls. latexmk's `.fdb_latexmk` is written by hand with the real md5s, then one source
    is edited to make one PDF stale. Both directions: fresh passes, stale fails in strict mode.
    """

    # Since 2026-10-21 the struck values live in the records document, whose app_history.tex the checker requires;
    # the posted note (main_note) is an outward build with a clean body, like the paper and the primer.
    # Each strike-carrying body also strikes the literal of one production CONTEXT_EXEMPT entry, and the directory
    # carries each entry's source text, because the checker refuses a stale exemption (review F8).
    BODIES = {"main_records": r"struck $\dead{1.234}$ here and $\dead{1.014}$",
              "pet_note": r"struck $\dead{5.678}$ here and $\dead{0.912}$",
              "main_note": "clean posted note", "main_paper": "clean paper", "main_primer": "clean primer"}
    EXEMPT_SOURCES = {"sec_validation.tex": "the injected bump (mean weight 1.014)\n",
                      "values.tex": "\\newcommand{\\covTwoDCTwo}{0.912}\n"}
    BODY_FILES = {"main_records": "app_history", "pet_note": "app_history_pet", "main_note": "body_main_note",
                  "main_paper": "body_main_paper", "main_primer": "body_main_primer"}
    # What each fake PDF "renders": each strike-carrying build shows its own struck literal (its positive control).
    PDF_TEXT = {"main_records": "1.234 rendered\n", "pet_note": "5.678 rendered\n"}

    def setUp(self):
        import hashlib
        self.tmp = Path(tempfile.mkdtemp(prefix="cdc-object-"))
        self.note = self.tmp / "note"
        self.note.mkdir()
        shim = self.tmp / "bin"
        shim.mkdir()
        (shim / "pdftotext").write_text('#!/bin/sh\ncat "$2" > "$3"\n')
        (shim / "pdftotext").chmod(0o755)
        self.env = dict(os.environ, PATH=f"{shim}{os.pathsep}{os.environ.get('PATH', '')}")
        for name, text in ResultLineNamesItsObjectTest.EXEMPT_SOURCES.items():
            (self.note / name).write_text(text)
        for driver, body in self.BODIES.items():
            stem = self.BODY_FILES[driver]
            (self.note / f"{driver}.tex").write_text(
                "\\documentclass{article}\n\\input{%s}\n" % stem)
            (self.note / f"{stem}.tex").write_text(body + "\n")
            (self.note / f"{driver}.pdf").write_text(self.PDF_TEXT.get(driver, "nothing struck\n"))
            rows = "".join(
                '  "%s" 1790000000 %d %s ""\n' % (
                    name, (self.note / name).stat().st_size,
                    hashlib.md5((self.note / name).read_bytes()).hexdigest())
                for name in (f"{driver}.tex", f"{stem}.tex"))
            (self.note / f"{driver}.fdb_latexmk").write_text(
                '# Fdb version 4\n["pdflatex"] 1790000000 "%s.tex" "%s.pdf" "%s" 1790000001 0\n'
                '%s  (generated)\n  "%s.pdf"\n' % (driver, driver, driver, rows, driver))

    def tearDown(self):
        shutil.rmtree(self.tmp, True)

    def _run(self, *extra):
        r = subprocess.run([sys.executable, str(HERE / "check_dead_containment.py"),
                            "--dir", str(self.note), "--tmp", str(self.tmp / "txt"), *extra],
                           capture_output=True, text=True, env=self.env)
        result = [line for line in r.stdout.splitlines() if line.startswith("RESULT ::")]
        self.assertEqual(len(result), 1, r.stdout + r.stderr)
        return r.returncode, result[0], r.stdout

    def test_fresh_products_pass_and_the_line_names_every_field(self):
        import hashlib
        code, line, out = self._run()
        self.assertEqual(code, 0, out)
        self.assertTrue(line.startswith("RESULT :: PASS :: "), line)
        helper = any(p.is_file() for p in (HERE / "tree_state.py",
                                           HERE.parents[1] / "lib" / "tree_state.py"))
        # outside git there is no sha to claim; a checkout without the helper must SAY so
        self.assertIn("head=none tree=no-git" if helper else "helper not found", line)
        self.assertIn("mode=strict", line)
        digest = hashlib.sha256((self.note / "main_note.pdf").read_bytes()).hexdigest()
        self.assertIn(f"main_note.pdf@sha256:{digest}(fresh)", line)
        self.assertEqual(line.count("(fresh)"), 5, line)

    def test_a_stale_product_fails_strict_mode(self):
        (self.note / "body_main_paper.tex").write_text("clean paper, edited after the build\n")
        code, line, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertTrue(line.startswith("RESULT :: FAIL :: "), line)
        self.assertIn("main_paper.pdf is STALE", out)
        self.assertIn("body_main_paper.tex", out)
        self.assertIn("main_paper.pdf@sha256:", line)
        self.assertIn("(stale)", line)

    def test_source_only_reports_the_stale_product_without_failing(self):
        (self.note / "body_main_paper.tex").write_text("clean paper, edited after the build\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 0, out)
        self.assertIn("mode=source-only", line)
        self.assertIn("(stale)", line)

    def test_a_missing_database_is_unknown_not_fresh(self):
        (self.note / "main_primer.fdb_latexmk").unlink()
        code, line, out = self._run()
        self.assertEqual(code, 0, out)
        self.assertIn("main_primer.pdf freshness UNKNOWN", out)
        self.assertIn("(unknown)", line)
        self.assertEqual(line.count("(fresh)"), 4, line)

    def test_absent_pdfs_are_named_absent(self):
        for driver in self.BODIES:
            (self.note / f"{driver}.pdf").unlink()
        code, line, out = self._run()
        self.assertEqual(code, 1, out)
        # The first PDF read is the first strike-carrying build's positive control.
        self.assertIn("products=main_records.pdf=absent", line)


class StruckOnlyInHistoryTest(unittest.TestCase):
    r"""Inside the records document, `\dead{}` may occur only in app_history.tex.

    Same synthetic directory as ResultLineNamesItsObjectTest, whose records document keeps its only strike in
    app_history.tex and passes. Here a body file joins the records' closure: clean, it must still
    pass; carrying a `\dead{}` -- in any of the forms DEAD_RE reads -- it must FAIL and name the
    file. Adding the file changes main_records.tex after its .fdb_latexmk was written, so these runs
    use --source-only and the PDF stage's staleness cannot be what fails or passes them.
    (Until 2026-10-21 this was main_note's invariant; the posted note now may strike nothing: PostedNoteIsOutwardTest.)
    """

    BODIES = ResultLineNamesItsObjectTest.BODIES
    BODY_FILES = ResultLineNamesItsObjectTest.BODY_FILES
    PDF_TEXT = ResultLineNamesItsObjectTest.PDF_TEXT
    setUp = ResultLineNamesItsObjectTest.setUp
    tearDown = ResultLineNamesItsObjectTest.tearDown
    _run = ResultLineNamesItsObjectTest._run

    def _add_body(self, text):
        (self.note / "main_records.tex").write_text(
            "\\documentclass{article}\n\\input{app_history}\n\\input{sec_body}\n")
        (self.note / "sec_body.tex").write_text(text + "\n")
        return self._run("--source-only")

    def test_a_clean_body_file_passes(self):
        code, line, out = self._add_body("current value $4.993$ only")
        self.assertEqual(code, 0, out)
        self.assertTrue(line.startswith("RESULT :: PASS :: "), line)

    def test_a_struck_value_in_a_body_file_FAILS(self):
        for form in (r"was $\dead{1.008}$ before", r"was $\dead {1.008}$ before",
                     "was $\\dead%c\n{1.008}$ before"):
            with self.subTest(form=form):
                code, line, out = self._add_body(form)
                self.assertEqual(code, 1, out)
                self.assertTrue(line.startswith("RESULT :: FAIL :: "), line)
                self.assertIn("in sec_body.tex", out)
                self.assertIn("belongs only in app_history.tex", out)

    def test_a_struck_value_only_in_a_body_file_FAILS(self):
        """Moving the strike out of app_history.tex, not just adding one, is caught too."""
        (self.note / "app_history.tex").write_text("no struck values here\n")
        code, line, out = self._add_body(r"was $\dead{1.008}$ before")
        self.assertEqual(code, 1, out)
        self.assertIn("in sec_body.tex", out)

    def test_the_pet_note_has_its_own_history_file(self):
        """pet_note (2026-10-12) may strike only in app_history_pet.tex, not in main_note's file."""
        (self.note / "pet_note.tex").write_text(
            "\\documentclass{article}\n\\input{app_history_pet}\n\\input{sec_pet_body}\n")
        (self.note / "sec_pet_body.tex").write_text(r"was $\dead{2.468}$ before" + "\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("pet_note: 1 \\dead{} use(s) in sec_pet_body.tex", out)
        self.assertIn("belongs only in app_history_pet.tex", out)

    def test_each_note_runs_its_own_positive_control(self):
        """main_records rendering its strikes must not vouch for a pet_note PDF that drops its own."""
        (self.note / "pet_note.pdf").write_text("nothing struck\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("appear in pet_note.pdf", out)
        self.assertIn("records.pdf carries 1/2 struck literals (positive control OK)", out)

    def test_a_pet_note_strike_in_the_paper_FAILS(self):
        """The outward builds are checked against the PET note's struck literals too."""
        (self.note / "main_paper.pdf").write_text("the paper prints 5.678\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("main_paper.pdf contains struck literal(s) ['5.678']", out)


class PostedNoteIsOutwardTest(unittest.TestCase):
    r"""Since 2026-10-21 (DECISION-20261021-joseph-da-and-note-records.md item 2) the posted note strikes nothing.

    Its struck values moved, with app_history.tex, to the internal records document main_records.tex. Both
    directions of the outward check now apply to main_note: a `\dead{}` reaching its closure FAILS at the source
    stage, and a struck literal some strike-carrying PDF renders FAILS when main_note.pdf prints it.
    """

    BODIES = ResultLineNamesItsObjectTest.BODIES
    BODY_FILES = ResultLineNamesItsObjectTest.BODY_FILES
    PDF_TEXT = ResultLineNamesItsObjectTest.PDF_TEXT
    setUp = ResultLineNamesItsObjectTest.setUp
    tearDown = ResultLineNamesItsObjectTest.tearDown
    _run = ResultLineNamesItsObjectTest._run

    def test_the_clean_posted_note_passes(self):
        code, line, out = self._run()
        self.assertEqual(code, 0, out)
        self.assertIn("note.pdf: 0 of 2 struck literals", out)

    def test_a_dead_in_the_posted_note_FAILS(self):
        for form in (r"was $\dead{4.321}$ before", r"was $\dead {4.321}$ before", "was $\\dead%c\n{4.321}$ before"):
            with self.subTest(form=form):
                (self.note / "body_main_note.tex").write_text(form + "\n")
                code, line, out = self._run("--source-only")
                self.assertEqual(code, 1, out)
                self.assertIn("main_note (note build) reaches 1 \\dead{} use(s) via body_main_note.tex", out)

    def test_app_history_back_in_the_posted_note_FAILS(self):
        """Re-inputting the history appendix is the likeliest regression, so it is tested by name."""
        (self.note / "main_note.tex").write_text(
            "\\documentclass{article}\n\\input{body_main_note}\n\\input{app_history}\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("main_note (note build) reaches 2 \\dead{} use(s) via app_history.tex", out)

    def test_a_struck_literal_in_the_posted_note_pdf_FAILS(self):
        for value in ("1.234", "5.678"):   # the records' strike, and the PET note's
            for end in ("\n", ".\n"):    # also at the end of a sentence (review F7)
                with self.subTest(value=value, end=end):
                    (self.note / "main_note.pdf").write_text("the posted note prints %s%s" % (value, end))
                    code, line, out = self._run("--source-only")
                    self.assertEqual(code, 1, out)
                    self.assertIn("main_note.pdf contains struck literal(s) ['%s']" % value, out)

    def test_the_production_maps_name_the_records_and_not_the_note(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("cdc_maps", str(HERE / "check_dead_containment.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.STRUCK_ALLOWED, {"main_records": "app_history.tex", "pet_note": "app_history_pet.tex"})
        self.assertEqual(mod.BUILDS["main_records"], "records")
        self.assertEqual(mod.BUILDS["main_note"], "note")
        note = (HERE / "main_note.tex").read_text()
        self.assertNotIn("\\input{app_history}", note)
        self.assertNotIn("\\input{app_provenance}", note)
        records = (HERE / "main_records.tex").read_text()
        for name in ("app_provenance", "app_release_records", "app_codebase_records", "app_history"):
            self.assertIn("\\input{%s}" % name, records)


class UnitRequiredLiteralTest(unittest.TestCase):
    r"""check_dead_containment.UNIT_REQUIRED narrows the outward PDF test for listed literals only.

    Added 2026-10-11 with the narrowing: the live pull RMS 0.564 (\pullRMS) printed bare in the paper
    must not count as a leak of the struck `0.564\%`, while the struck percentage itself still must.
    """

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cdc_unit_under_test", str(HERE / "check_dead_containment.py"))
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_bare_live_number_is_not_a_hit(self):
        self.assertFalse(self.mod.outward_hit("0.564", "mean = 0.074, RMS = 0.564 (205 bins)"))

    def test_struck_percentage_is_still_a_hit(self):
        for text in ("median spread 0.564% per bin", "median spread 0.564 % per bin",
                     "median spread 0.564\u2009% per bin"):
            with self.subTest(text=text):
                self.assertTrue(self.mod.outward_hit("0.564", text))

    def test_a_struck_literal_at_sentence_end_is_a_hit(self):
        """Review F7: the old boundary `(?![\\d.])` refused any following full stop."""
        for value, text in (("1.014", "a ratio of 1.014."), ("0.406", "rms 0.406."), ("0.912", "ratio of 0.912.\nNext")):
            with self.subTest(text=text):
                self.assertTrue(self.mod.token_hit(value, text))
                self.assertTrue(self.mod.outward_hit(value, text))

    def test_a_point_that_continues_the_number_still_blocks_the_match(self):
        for value, text in (("1.014", "version 1.014.5"), ("1.014", "1.0140"), ("0.406", "0.4061.")):
            with self.subTest(text=text):
                self.assertFalse(self.mod.token_hit(value, text))

    def test_unlisted_literal_keeps_the_bare_token_test(self):
        self.assertTrue(self.mod.outward_hit("6.865", "a median of 6.865 in the table"))
        self.assertFalse(self.mod.outward_hit("6.865", "a median of 6.8650"))

    def test_every_key_is_struck_with_its_unit_in_app_history(self):
        hist = (HERE / "app_history.tex").read_text(encoding="utf-8")
        for value, unit in self.mod.UNIT_REQUIRED.items():
            with self.subTest(value=value):
                self.assertEqual(unit, "%")
                self.assertIn("\\dead{" + value + "\\%}", hist)

    def test_the_2026_10_21_keys_bare_in_the_posted_note_are_not_hits_but_their_percentages_are(self):
        """1.008, 0.563 and 2.26 print bare as live quantities in the posted note (measured 2026-10-21)."""
        for value, live in (("1.008", "The median per-bin ratio is 1.008; 82.9% of bins"),
                            ("0.563", "0.56 0.564 0.563 0.565 (i) Iterations"),
                            ("2.26", "of the central value from it, or 0.08-2.26 of the band's sigma")):
            with self.subTest(value=value):
                self.assertFalse(self.mod.outward_hit(value, live))
                self.assertTrue(self.mod.outward_hit(value, "struck median %s%% per bin" % value))


class ExemptionGuardTest(unittest.TestCase):
    r"""Review F8: check_dead_containment.py's own main() refuses a stale CONTEXT_EXEMPT entry, so the build gate
    enforces it, not only this suite. Same synthetic directory as ResultLineNamesItsObjectTest."""

    BODIES = ResultLineNamesItsObjectTest.BODIES
    BODY_FILES = ResultLineNamesItsObjectTest.BODY_FILES
    PDF_TEXT = ResultLineNamesItsObjectTest.PDF_TEXT
    setUp = ResultLineNamesItsObjectTest.setUp
    tearDown = ResultLineNamesItsObjectTest.tearDown
    _run = ResultLineNamesItsObjectTest._run

    def test_live_exemptions_hold_and_say_so(self):
        code, line, out = self._run()
        self.assertEqual(code, 0, out)
        self.assertIn("CONTEXT_EXEMPT[('main_note', '1.014')] holds", out)
        self.assertIn("CONTEXT_EXEMPT[('main_note', '0.912')] holds", out)

    def test_a_context_that_no_longer_prints_FAILS(self):
        (self.note / "sec_validation.tex").write_text("the injected bump, reworded\n")
        code, line, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertIn("CONTEXT_EXEMPT[('main_note', '1.014')] is STALE: sec_validation.tex no longer contains", out)

    def test_a_missing_source_file_FAILS(self):
        (self.note / "values.tex").unlink()
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("CONTEXT_EXEMPT[('main_note', '0.912')] is STALE: values.tex no longer contains", out)

    def test_a_literal_that_is_no_longer_struck_FAILS(self):
        (self.note / "app_history.tex").write_text(r"struck $\dead{1.234}$ here" + "\n")
        code, line, out = self._run("--source-only")
        self.assertEqual(code, 1, out)
        self.assertIn("CONTEXT_EXEMPT[('main_note', '1.014')] is STALE: 1.014 is no longer struck", out)


class PinCheckTest(unittest.TestCase):
    """check_note_records.py pin (plan commit 3) on synthetic git repositories, in both directions."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("cnr_pin", str(HERE / "check_note_records.py"))
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = Path(tempfile.mkdtemp(prefix="pin-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        self.note = self.repo / "docs" / "analysis-note"
        self.note.mkdir(parents=True)
        self.git("init", "-q")
        (self.note / "app_provenance.tex").write_text("\\section{Provenance}\n\\texttt{joint-5d} & see below \\\\\n")
        (self.note / "app_history.tex").write_text("\\section{Superseded values and withdrawn results}\n"
                                                    "\\subsubsection{The VL175 construction: retired material}\n")
        (self.note / "main_note.tex").write_text("\\documentclass{article}\n\\input{sec_joint}\n")
        self.cite(r"\texttt{joint-5d}")
        self.records = self.commit(None)
        self.bib(self.records)
        self.head = self.commit(self.records)
        self.git("update-ref", "HEAD", self.head)

    def git(self, *args, cwd=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t.invalid", *args],
                              cwd=str(cwd or self.repo), env=env, capture_output=True, text=True)

    def commit(self, parent):
        self.git("add", "-A")
        tree = self.git("write-tree").stdout.strip()
        return self.git("commit-tree", tree, "-m", "t", *(["-p", parent] if parent else [])).stdout.strip()

    def bib(self, ref):
        (self.note / "technote.bib").write_text(
            "@misc{NoteRecords2026,\n  howpublished = {\\url{https://github.com/josephbaileyy/MINERvA-OmniFold/tree/"
            + ref + "/docs/analysis-note}}\n}\n")

    def cite(self, what):
        (self.note / "sec_joint.tex").write_text("No uncertainty (Ref.~\\cite{NoteRecords2026}, %s).\n" % what)

    def test_a_good_pin_passes(self):
        status, msgs = self.mod.pin_check(self.note)
        self.assertEqual(status, "PASS", msgs)

    def test_a_pin_lacking_a_cited_tag_FAILS(self):
        self.cite(r"\texttt{joint-6d}")
        status, msgs = self.mod.pin_check(self.note)
        self.assertEqual(status, "FAIL", msgs)
        self.assertTrue(any("cites tag joint-6d" in m for m in msgs), msgs)

    def test_a_pin_lacking_a_cited_heading_FAILS(self):
        self.cite("superseded values: the retired 2D construction")
        status, msgs = self.mod.pin_check(self.note)
        self.assertEqual(status, "FAIL", msgs)
        self.assertTrue(any("'the retired 2d construction'" in m for m in msgs), msgs)
        self.cite("superseded values: retired material")
        self.assertEqual(self.mod.pin_check(self.note)[0], "PASS")

    def test_a_non_ancestor_sha_FAILS(self):
        side = self.commit(None)        # the same tree with no parent: a commit HEAD does not contain
        self.bib(side)
        status, msgs = self.mod.pin_check(self.note)
        self.assertEqual(status, "FAIL", msgs)
        self.assertTrue(any("is not an ancestor of HEAD" in m for m in msgs), msgs)

    def test_a_branch_name_FAILS(self):
        self.bib("main")
        status, msgs = self.mod.pin_check(self.note)
        self.assertEqual(status, "FAIL", msgs)
        self.assertIn("not a full 40-hex commit sha", msgs[0])

    def test_the_standalone_layout_skips(self):
        standalone = self.tmp / "standalone"
        shutil.copytree(self.note, standalone)
        self.git("init", "-q", cwd=standalone)
        self.assertEqual(self.mod.pin_check(standalone)[0], "SKIP")

    def test_a_copy_outside_git_skips(self):
        copy = self.tmp / "export" / "docs" / "analysis-note"
        shutil.copytree(self.note, copy)
        self.assertEqual(self.mod.pin_check(copy)[0], "SKIP")

    def test_an_inherited_GIT_DIR_cannot_redirect_the_check(self):
        """The check drops every GIT_* variable, so a hook's GIT_DIR cannot make another repository answer."""
        old = os.environ.get("GIT_DIR")
        os.environ["GIT_DIR"] = str(self.tmp / "nowhere.git")
        try:
            self.assertEqual(self.mod.pin_check(self.note)[0], "PASS")
        finally:
            if old is None:
                os.environ.pop("GIT_DIR", None)
            else:
                os.environ["GIT_DIR"] = old

    def test_the_self_test_passes(self):
        self.assertEqual(self.mod.pin_self_test(), 0)

    def test_the_production_bib_names_a_full_sha(self):
        ref, entry = self.mod.bib_pin(HERE)
        self.assertIsNotNone(ref, entry)
        self.assertRegex(ref, r"^[0-9a-f]{40}$")


class ContextExemptLiteralTest(unittest.TestCase):
    r"""check_dead_containment.CONTEXT_EXEMPT removes one declared context, in one build, before the outward search.

    Added 2026-10-21 when the posted note became outward-facing. Both directions: the declared context is not a hit
    in its build, and the same literal anywhere else -- or in the context in another build -- still is. Each entry's
    source text must still occur in its source file and its literal must still be struck, so a stale exemption fails.
    """

    setUp = UnitRequiredLiteralTest.setUp

    def test_the_declared_context_is_not_a_hit_in_its_build(self):
        for text in ("Same Gaussian form in truth q3 (mean weight 1.014) 4D",
                     "Same Gaussian form in truth q3 (mean\nweight 1.014) 4D",
                     "the bump had mean weight 1.014.",
                     "Fixed-truth C2 = 0.912.",
                     "the fraction within 2 sigma, C2 = 0.912, vs. 0.954",
                     "Fixed-truth C2 = 0.912 (nominal 0.954)"):
            with self.subTest(text=text):
                searched = self.mod.exempt_text("main_note", text)
                self.assertFalse(any(self.mod.outward_hit(v, searched) for v in ("1.014", "0.912")), searched)

    def test_the_literal_elsewhere_in_that_build_is_still_a_hit(self):
        for value, text in (("1.014", "(mean weight 1.014); the struck chi2/ndf 1.014 would leak"),
                            ("0.912", "C2 = 0.912, and a PET/GBDT ratio of 0.912")):
            with self.subTest(value=value):
                self.assertTrue(self.mod.outward_hit(value, self.mod.exempt_text("main_note", text)))

    def test_the_context_in_another_build_is_still_a_hit(self):
        for build in ("main_paper", "main_primer", "main_records", "pet_note"):
            with self.subTest(build=build):
                self.assertTrue(self.mod.outward_hit("1.014", self.mod.exempt_text(build, "(mean weight 1.014)")))
                self.assertTrue(self.mod.outward_hit("0.912", self.mod.exempt_text(build, "C2 = 0.912")))

    def test_each_source_text_still_prints_and_each_literal_is_still_struck(self):
        macros = self.mod.macro_table(HERE)
        struck = set()
        for name in ("app_history.tex", "app_history_pet.tex"):
            for body in self.mod.dead_bodies(HERE / name):
                struck |= self.mod.literals_from(body, macros)[0]
        for (build, value), (pattern, source, printed) in self.mod.CONTEXT_EXEMPT.items():
            with self.subTest(value=value):
                self.assertEqual(build, "main_note")
                self.assertIn(printed, (HERE / source).read_text(encoding="utf-8"))
                self.assertIn(value, struck)
                self.assertIsNotNone(re.search(pattern, printed.replace("\\newcommand{\\covTwoDCTwo}{0.912}",
                                                                        "C2 = 0.912")))


# The mutation runner points the whole suite at a mutated copy without editing anything.
if os.environ.get("BUILD_ALL_SCRIPT"):
    SCRIPT = Path(os.environ["BUILD_ALL_SCRIPT"])

if __name__ == "__main__":
    if "--mutate" in sys.argv:
        sys.exit(run_mutations())
    unittest.main()
