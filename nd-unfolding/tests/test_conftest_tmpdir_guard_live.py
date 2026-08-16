#!/usr/bin/env python3
"""REPAIR-10 N6: run the tmpdir guard for real, in the state it was written for.

**Why this file exists and why the existing tests were not enough.** `TmpdirGuardItself` in
`test_p4_repair.py` monkeypatches `tempfile` and calls `conftest.pytest_collection_modifyitems`
directly with hand-built fake items. That tests the hook's BODY. It does not test the hook being
invoked by pytest, and it cannot: its fake items have no class, no fixture closure, and a
`get_closest_marker` that returns `None` unconditionally -- so the marker route, the fixture route
and the setUp route were all unreachable from it. N6 was carried "open structurally" through
repair-8, -9 and -10 with the same sentence each round: *the guard is inert wherever a writable
tmpdir exists, which is the condition every round had to create in order to run the suite at all.*

**What breaks the deadlock.** The environment is manufactured for a subprocess instead of for this
run: a `sitecustomize.py` on `PYTHONPATH` replaces `tempfile.TemporaryDirectory`, `mkdtemp` and
`NamedTemporaryFile` with raising stand-ins at interpreter start -- before pytest, before conftest --
and a real `pytest` runs a throwaway suite that imports the REAL conftest by path. So the guard runs
live, under pytest, in a process where no temp directory can be made.

**`TMPDIR` cannot do this, and that is measured, not assumed.** Pointing `TMPDIR` at a nonexistent
or read-only directory does NOT reproduce the sandbox: `tempfile._candidate_tempdir_list` falls
through to `/tmp`, `/var/tmp` and the cwd, so `gettempdir()` returns `/tmp` and the probe reports
writable. A preflight that exported `TMPDIR`, saw green and concluded the guard was exercised would
have been wrong -- which is exactly what conftest.py's own docstring records happening
(*"Exporting TMPDIR from outside did not reach the sandbox"*). `test_TMPDIR_alone_cannot_simulate...`
keeps that fact from being rediscovered.

**Every assertion here is paired with a negative control** in which the guard is neutralized by one
line (`_real.TMPDIR_WRITABLE = True`) and NOTHING else changes. Without that pairing a green run
proves only that the subprocess started: the guard's whole output is skips, and a suite that skips
everything for an unrelated reason looks identical. So each case asserts both that the guarded run
skips and that the controlled run does not -- and the controlled run is where the historical damage
is visible, since that is the run that produces the errors and failures this guard exists to
suppress. That the guard CAN fail is therefore observed in the same invocation, per the standing
requirement that a null result show it could have been otherwise (BEN-344).
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_CONFTEST = HERE / "conftest.py"

# The stand-ins raise the error the read-only audit sandbox raises. Installed at interpreter start
# via sitecustomize so that the REAL conftest's module-level probe sees them; a monkeypatch applied
# from inside the test process would be too late for the subprocess and would not exercise the
# import-time path at all.
SITECUSTOMIZE = '''
import os
import tempfile

_REAL_TMP = os.path.realpath(tempfile.gettempdir())
_real_mkdir, _real_makedirs = os.mkdir, os.makedirs


def _boom(*a, **k):
    raise OSError("read-only file system (simulated read-only audit sandbox)")


class _BoomCtx:
    def __init__(self, *a, **k):
        _boom()


tempfile.TemporaryDirectory = _BoomCtx
tempfile.mkdtemp = _boom


def _under_tmp(path):
    try:
        return os.path.realpath(os.fspath(path)).startswith(_REAL_TMP + os.sep)
    except Exception:
        return False


def mkdir(path, *a, **k):
    if _under_tmp(path):
        _boom()
    return _real_mkdir(path, *a, **k)


def makedirs(path, *a, **k):
    if _under_tmp(path):
        _boom()
    return _real_makedirs(path, *a, **k)


os.mkdir, os.makedirs = mkdir, makedirs
'''

# WHY THE SIMULATED CONDITION IS EXACTLY "DIRECTORY CREATION FAILS, FILE CREATION WORKS", and why
# getting this wrong is itself the N6 finding.
#
# The first attempt patched `tempfile.gettempdir` to raise -- the textbook signature of a machine
# with no usable temp directory -- and pytest never started: `_pytest.capture` builds its FDCapture
# from `tempfile.TemporaryFile`, which calls `gettempdir()` during
# `pytest_load_initial_conftests`, so the process died before ANY conftest was loaded.
#
# That is a load-bearing fact about this guard's reach. **If nothing under the temp root can be
# created, the guard cannot run at all, because pytest cannot run at all** -- so the guard's value
# is bounded to sandboxes where pytest itself survives.
#
# It also identifies what the historical sandbox actually was, which conftest.py describes only as
# "provides no writable temporary directory". That description cannot be literally true: pytest
# started and reported 23 ERRORS, so it made its capture temp file successfully. The condition
# consistent with the observed history is the narrower one simulated here -- `mkdir` under the temp
# root is refused while a temp FILE is fine. `tempfile.NamedTemporaryFile`, `mkstemp` and
# `TemporaryFile` are therefore deliberately left working.
#
# `tmp_path` is reached through `os.mkdir`, not `mkdtemp` (pytest's `make_numbered_dir`), which is
# why the patch has to sit at the `os` layer to exercise the 171-item fixture stratum at all.

# Loaded by path under a private module name. `import conftest` would collide with the throwaway
# directory's own conftest in sys.modules and raise a partially-initialized-module AttributeError --
# measured, not guessed. Rebinding the three hooks by name is deliberate: if a hook is renamed in
# the real conftest, this goes red instead of silently testing nothing.
SHIM = '''
import importlib.util
_spec = importlib.util.spec_from_file_location("p4_real_conftest_under_test", {real!r})
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
pytest_configure = _real.pytest_configure
pytest_collection_modifyitems = _real.pytest_collection_modifyitems
pytest_report_header = _real.pytest_report_header
'''

# Four shapes, one per detection route, plus the control that must NOT be skipped. Each is written
# the way the real suite writes it, because the point is the route and not the string.
PROBE_HELPERS = '''
import tempfile


class ImportedRepo:
    """Owns a tmpdir, and lives in a DIFFERENT module from the test that builds it."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="probe-imported-")
'''

PROBE_SUITE = '''
import tempfile
import unittest

import pytest

from probe_helpers import ImportedRepo


@pytest.mark.needs_tmpdir
def test_route1_marker():
    with tempfile.TemporaryDirectory() as d:
        assert d


def test_route2_pytest_fixture(tmp_path):
    assert tmp_path.exists()


def test_route3_body_calls_mkdtemp():
    d = tempfile.mkdtemp()
    assert d


class Route4aSetupCallsTheApiDirectly(unittest.TestCase):
    """The 113-item stratum: setUp owns the tmpdir, the test body never names one."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="probe-direct-")

    def test_direct_setup_body_names_nothing(self):
        assert self.d


class _HelperOwningTheTmpdir:
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="probe-")


class Route4bSetupThroughAHelper(unittest.TestCase):
    """The 12-item stratum: one indirection further out. Kept SEPARATE from 4a deliberately -- when
    only the indirection shape was probed, deleting the direct setUp-source check was a surviving
    mutant, because the depth-1 helper walk covered the probe and the direct check was never the
    thing under test (the BEN-342 shape: a fixture degenerate on the axis it was meant to vary)."""

    def setUp(self):
        self.h = _HelperOwningTheTmpdir()

    def test_body_never_names_a_tmpdir_api(self):
        assert self.h.dir


class Route4cSetupThroughAnIMPORTEDHelper(unittest.TestCase):
    """The known residual: the depth-1 walk follows only helpers defined in the test module."""

    def setUp(self):
        self.h = ImportedRepo()

    def test_imported_helper_is_NOT_detected(self):
        assert self.h.dir


@pytest.mark.needs_tmpdir
class Route4dTheSameThingWithTheMarker(unittest.TestCase):
    """...and the remedy for it. Same shape as 4c plus the marker an author is expected to add."""

    def setUp(self):
        self.h = ImportedRepo()

    def test_the_marker_covers_what_inference_cannot(self):
        assert self.h.dir


class OverFireControl(unittest.TestCase):
    """A sibling method uses a tmpdir; setUp does not. The other test MUST still run: skipping it
    would be the guard hiding real coverage, which is the mirror image of the bug it fixes."""

    def test_sibling_that_does_use_one(self):
        with tempfile.TemporaryDirectory() as d:
            assert d

    def test_this_one_needs_NOTHING_and_must_not_be_skipped(self):
        assert 1 + 1 == 2


def test_needs_nothing_at_all():
    assert 1 + 1 == 2
'''

GUARDED_MUST_SKIP = ("test_route1_marker",
                     "test_route2_pytest_fixture",
                     "test_route3_body_calls_mkdtemp",
                     "test_direct_setup_body_names_nothing",
                     "test_body_never_names_a_tmpdir_api",
                     "test_the_marker_covers_what_inference_cannot")
# Detected by NOTHING, on purpose, and asserted so a future widening is a visible red rather than a
# silent behaviour change. See `_is_local_helper` in conftest.py for why following imports is worse.
KNOWN_RESIDUAL = "test_imported_helper_is_NOT_detected"
MUST_ALWAYS_RUN = ("test_this_one_needs_NOTHING_and_must_not_be_skipped",
                   "test_needs_nothing_at_all")


def _report(root, neutralize):
    """Run a real pytest over the probe suite with tempfile broken; return per-test outcomes.

    Outcomes come from a `pytest_report_teststatus`-free route on purpose: a tiny reporting plugin
    writes `nodeid -> outcome` as JSON, so the assertions below read structured data instead of
    grepping terminal text whose format is a pytest implementation detail.
    """
    site = root / "site"
    suite = root / "suite"
    site.mkdir()
    suite.mkdir()
    (site / "sitecustomize.py").write_text(SITECUSTOMIZE)
    shim = SHIM.format(real=str(REAL_CONFTEST))
    if neutralize:
        shim += "_real.TMPDIR_WRITABLE = True   # NEGATIVE CONTROL: guard off, nothing else changed\n"
    (suite / "conftest.py").write_text(shim)
    (suite / "probe_helpers.py").write_text(PROBE_HELPERS)
    (suite / "test_probe.py").write_text(PROBE_SUITE)
    out = root / "outcomes.json"
    (site / "collect_outcomes.py").write_text(textwrap.dedent(f'''
        import json
        _seen = {{}}

        def pytest_runtest_logreport(report):
            # first non-passed wins per test, else the call-phase pass
            prev = _seen.get(report.nodeid)
            if report.outcome != "passed" and prev in (None, "passed"):
                _seen[report.nodeid] = report.outcome
                _seen[report.nodeid + "::phase"] = report.when
            elif prev is None and report.when == "call":
                _seen[report.nodeid] = report.outcome

        def pytest_sessionfinish(session, exitstatus):
            open({str(out)!r}, "w").write(json.dumps(_seen))
    '''))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(site) + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("PYTEST_ADDOPTS", None)
    # the throwaway suite lives under the temp root, and __pycache__ creation there would hit the
    # patched os.mkdir. CPython swallows that, but silently -- better to not create the ambiguity.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        # NOT -q: the guard's `pytest_report_header` line is what proves the subprocess really had
        # no tmpdir, and -q suppresses the header.
        [sys.executable, "-m", "pytest", str(suite), "-p", "collect_outcomes",
         "-p", "no:cacheprovider"],
        env=env, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    text = proc.stdout.decode()
    assert out.exists(), f"the probe run never reached sessionfinish; pytest said:\n{text}"
    raw = json.loads(out.read_text())
    outcomes, phases = {}, {}
    for k, v in raw.items():
        if k.endswith("::phase"):
            phases[k[: -len("::phase")].rsplit("::", 1)[-1]] = v
        else:
            outcomes[k.rsplit("::", 1)[-1]] = v
    return outcomes, phases, text


class TmpdirGuardLive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        root = Path(cls._tmp.name)
        (root / "g").mkdir()
        (root / "c").mkdir()
        cls.guarded, cls.guarded_phase, cls.guarded_text = _report(root / "g", neutralize=False)
        cls.control, cls.control_phase, cls.control_text = _report(root / "c", neutralize=True)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_the_subprocess_really_had_no_usable_tmpdir(self):
        """If this fails, every other assertion in the file is vacuous -- the guard would be inert
        for the ordinary reason and the skips would have to come from somewhere else."""
        self.assertIn("writable tmpdir = False", self.guarded_text,
                      "the guarded run reported a WRITABLE tmpdir, so the guard was inert and this "
                      "file proved nothing:\n" + self.guarded_text)
        self.assertIn("will SKIP, not error", self.guarded_text)

    def test_every_detection_route_SKIPS_under_a_live_pytest(self):
        for name in GUARDED_MUST_SKIP:
            with self.subTest(route=name):
                self.assertEqual(self.guarded.get(name), "skipped",
                                 f"{name} was {self.guarded.get(name)!r}, not skipped, in a real "
                                 f"pytest run with no writable tmpdir. In the audit sandbox this "
                                 f"reads as a defect, which is the whole failure conftest.py "
                                 f"exists to prevent.\n" + self.guarded_text)

    def test_AND_THE_SAME_TESTS_DO_NOT_SKIP_WITH_THE_GUARD_NEUTRALIZED(self):
        """The power test. One line differs between the two runs. If the control also skipped
        everything, the skips above would be evidence about the subprocess and not about the guard.
        """
        for name in GUARDED_MUST_SKIP:
            with self.subTest(route=name):
                self.assertNotEqual(
                    self.control.get(name), "skipped",
                    f"{name} skipped even with TMPDIR_WRITABLE forced True, so the guarded skip is "
                    f"not attributable to the guard:\n" + self.control_text)
                self.assertIn(self.control.get(name), ("failed", "error"),
                              f"{name} came out {self.control.get(name)!r} with the guard off; it "
                              f"was expected to break, since no temp directory can be created")

    def test_WHICH_shape_errors_and_which_merely_fails(self):
        """conftest.py justifies itself specifically by ERRORS ('23 of 165 ... to ERRORS, not
        failures') because an error reads as a defect. Which shape errors is therefore the question
        that ranks the detection routes -- and measuring it here reversed the answer I assumed.

        Measured, guard off, from the report phase rather than from the terminal text:

          * the pytest FIXTURE route breaks in the SETUP phase -> rendered as an ERROR;
          * the unittest `setUp` route breaks in the CALL phase -> rendered as a FAILURE, because
            pytest's unittest integration runs `setUp` inside `runtest` and not in its own setup
            phase;
          * a tmpdir call in the test body likewise fails in CALL.

        So the only stratum that produces the ERRORS this file was written about is the fixture one,
        which is also the largest (171 items) and the one the old function-source detection could
        not see at all -- it never looked at fixtures. The `setUp` stratum is real and worth
        skipping, but it was never an error.

        The phase is the assertion and not the outcome string, which is a third thing measured here
        rather than assumed: `TestReport.outcome` is `"failed"` for a setup break as well as a call
        break. "ERROR" is not a stored outcome -- the terminal derives the label from
        `when != "call"`. So a test asserting `outcome == "error"` would be red no matter how the
        code behaved.
        """
        self.assertEqual(self.control_phase.get("test_route2_pytest_fixture"), "setup",
                         "the pytest tmpdir fixture no longer breaks in the setup phase, so the "
                         "error-vs-failure account in conftest.py and here needs re-deriving")
        self.assertRegex(self.control_text, r"(?m)^ERROR ",
                         "the control run rendered no ERROR line, so the claim that the fixture "
                         "stratum is the erroring one is not supported by this run:\n"
                         + self.control_text)
        for name in ("test_body_never_names_a_tmpdir_api", "test_route3_body_calls_mkdtemp"):
            with self.subTest(shape=name):
                self.assertEqual(self.control_phase.get(name), "call",
                                 f"{name} broke in phase {self.control_phase.get(name)!r}, not "
                                 f"call; the error/failure asymmetry recorded here would then be "
                                 f"wrong")
                self.assertEqual(self.control.get(name), "failed")

    def test_the_guard_does_NOT_over_fire_on_a_tmpdir_free_sibling(self):
        """The boundary. Whole-class source scanning was the obvious fix and would have skipped 154
        real tests in this suite; this is the shape that would have caught it."""
        for name in MUST_ALWAYS_RUN:
            with self.subTest(control=name):
                self.assertEqual(self.guarded.get(name, "passed"), "passed",
                                 f"{name} needs no temp directory and was not run; the guard "
                                 f"over-fires and is hiding coverage behind phantom skips.\n"
                                 + self.guarded_text)
                self.assertEqual(self.control.get(name, "passed"), "passed")

    def test_an_IMPORTED_helper_is_the_known_residual(self):
        """The other boundary, pinned in the direction it actually acts.

        `_is_local_helper` follows only definitions owned by the test module, so a setUp building an
        IMPORTED helper is not detected. Asserting that -- rather than leaving it undocumented -- is
        what makes the narrowing falsifiable: widen the walk to follow imports and this goes red and
        says why, instead of the change looking free. The marker remains the remedy, and the
        4d/4c pair shows it working on the identical shape.
        """
        self.assertNotEqual(self.guarded.get(KNOWN_RESIDUAL), "skipped",
                            "the guard now detects an imported setUp helper. That is a widening, "
                            "not a bug fix: it means the depth-1 walk is following definitions "
                            "outside the test module, which reintroduces the over-fire risk "
                            "documented in conftest.py._is_local_helper. If it is intended, delete "
                            "this test and say so; do not leave both.")
        self.assertEqual(self.guarded.get("test_the_marker_covers_what_inference_cannot"),
                         "skipped",
                         "the marker no longer covers the shape inference cannot reach, which "
                         "leaves the residual with no remedy at all")

    def test_TMPDIR_alone_cannot_simulate_the_sandbox(self):
        """Kept as an executable fact because it invalidates the cheap version of this whole file.
        A read-only or absent TMPDIR falls through to /tmp, so the guard reports WRITABLE and any
        test built on `TMPDIR=...` would pass while exercising nothing."""
        env = dict(os.environ)
        env["TMPDIR"] = "/nonexistent-path-for-the-n6-probe"
        env.pop("PYTHONPATH", None)
        probe = subprocess.run(
            [sys.executable, "-c",
             "import tempfile;"
             "d=tempfile.TemporaryDirectory();"
             "print(tempfile.gettempdir(), d.name);"
             "d.cleanup()"],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        text = probe.stdout.decode()
        self.assertEqual(probe.returncode, 0,
                         "a bogus TMPDIR now DOES break tempfile on this platform; if so the "
                         "reasoning in conftest.py and here needs revisiting, not this assertion "
                         f"relaxing:\n{text}")
        self.assertNotIn("/nonexistent-path-for-the-n6-probe", text,
                         "tempfile honoured the bogus TMPDIR instead of falling through")


if __name__ == "__main__":
    unittest.main(verbosity=2)
