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
TARGETS = ("main_note", "main_primer", "main_paper")
SHARED = ("preamble.tex", "values.tex", "technote.bib")

# A fake latexmk. Its behaviour comes from BUILD_TEST_MODE so one shim covers every scenario.
FAKE_LATEXMK = r"""#!/usr/bin/env bash
# args: -g -pdf -interaction=nonstopmode -halt-on-error <target>.tex
tex="${!#}"
t="${tex%.tex}"
echo "latexmk: fake invoked for $tex with args: $*" >> "$BUILD_TEST_LOG"
case "$BUILD_TEST_MODE" in
  nothing-to-do)
    # The 2026-08-19 transcript, verbatim in shape: exit 0, touch nothing.
    echo "Latexmk: Nothing to do for '$tex'."
    ;;
  build)
    printf '%%PDF-1.5 fake %s\n' "$t" > "${t}.pdf"
    ;;
  build-note-only)
    if [ "$t" = "main_note" ]; then printf '%%PDF-1.5 fake\n' > "${t}.pdf"
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
    printf '%%PDF-1.5 fake\n' > "${t}.pdf"
    ;;
  build-then-edit-source)
    printf '%%PDF-1.5 fake\n' > "${t}.pdf"
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

    def run_build(self, mode, containment_rc="0", drop_latexmk=False):
        env = dict(os.environ)
        env["BUILD_TEST_MODE"] = mode
        env["BUILD_TEST_LOG"] = str(self.log)
        env["BUILD_TEST_CONTAINMENT_RC"] = containment_rc
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
        self.assertEqual(3, self.calls.count("latexmk: fake invoked"),
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


# The mutation runner points the whole suite at a mutated copy without editing anything.
if os.environ.get("BUILD_ALL_SCRIPT"):
    SCRIPT = Path(os.environ["BUILD_ALL_SCRIPT"])

if __name__ == "__main__":
    if "--mutate" in sys.argv:
        sys.exit(run_mutations())
    unittest.main()
