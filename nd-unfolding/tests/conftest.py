"""Shared pytest configuration for the standard-P4 suites.

**Why this exists.** Three consecutive `standard-p4-verifier` passes lost ~14% of the suite --
23 of 165 tests on the last one -- to ERRORS, not failures, because the read-only audit sandbox
provides no writable temporary directory and every `tempfile.TemporaryDirectory()` test blew up
before reaching an assertion. Exporting TMPDIR from outside did not reach the sandbox.

Errored tests are worse than skipped ones here for a specific reason: an error looks like a
defect. Each pass cost effort untangling phantom failures from real ones, and a genuine failure
hiding among 23 phantoms is exactly the kind of thing this lane keeps finding. So:

  * if a writable temp directory exists, nothing changes;
  * if none does, tests that need one are SKIPPED with an explicit reason, so the report says
    "skipped: no writable tmpdir" instead of 23 tracebacks.

`needs_tmpdir` is the marker. Registered in-code rather than in a config file so the suites stay
self-contained and a reader of the test file can see why a test skipped.

**2026-08-16, repair-10 N6.** N6 was carried three rounds as "open structurally": the guard is inert
wherever a writable tmpdir exists, which is the condition every round had to create in order to run
the suite at all, so no round could observe it working. It is now observed -- `tests/
test_conftest_tmpdir_guard_live.py` runs a real `pytest` in a subprocess with `tempfile` broken at
interpreter start, and asserts SKIP against a negative control in which the guard is neutralized and
the same tests fail. Two things fell out of finally running it, and both were real:

  1. **Fixtures were not looked at at all, and that is the stratum that ERRORS.** `171` items
     request pytest's own `tmp_path`/`tmpdir`/`tmp_path_factory`. Detection read only the test
     function's source, so every one of them was invisible -- and a fixture that raises breaks in
     the SETUP phase, which pytest reports as an ERROR. This is therefore the *only* stratum that
     produces the failure mode named at the top of this file, and it was completely unguarded.
     (Measured from report phases, not assumed: `test_WHICH_shape_errors_and_which_merely_fails`.)
  2. **`TemporaryDirectory` was the only term searched, and only in the test's own body.** Three
     further strata, all of which break as FAILURES rather than errors -- still worth skipping,
     since a phantom failure costs the same triage as a phantom error: **119** items build the
     tmpdir in `setUp`/`setup_method` (whose exception pytest reports in the CALL phase, because its
     unittest integration runs `setUp` inside `runtest`), **26** call `mkdtemp`/`NamedTemporaryFile`
     directly in the test body, and **12** reach it one indirection past setUp (`setUp` builds
     `_Repo()`; `_Repo.__init__` calls `mkdtemp`).

Measured on one tree -- this one -- with the guard forced on over 1465 collected items, the before
side taken from `git show HEAD:nd-unfolding/tests/conftest.py` rather than reconstructed: **157
skipped before, 485 after**; the 328 added are exactly those four strata, and each is now 0. **Six of
the 119 and one of the 157 are this change's own probe tests**, so the pre-existing exposure was
`113` and `156`; the figures are quoted on the current tree so that both sides come from the same
collection. **Deliberately NOT widened to whole-class source**,
which was the obvious fix and is wrong: 154 further items sit in classes where a *sibling* method
uses a tmpdir while the test itself needs none, and skipping those would hide real coverage behind
phantom skips -- the failure mode symmetric to the one this file was written for. The over-fire test
in `test_conftest_tmpdir_guard_live.py` pins that boundary, and the whole fix is mutation-tested 6/6
against deletion of each route and widening of each filter (`BEN-345`).

One item is left deliberately unskipped and is not a gap: `test_fps_provenance.py::
test_path_alias_ok` is declared `def test_path_alias_ok(tmp_path=None)` and never uses it. Measured,
not assumed -- it does not appear in that item's `fixturenames`, because pytest excludes parameters
carrying defaults from fixture resolution, so no tmpdir is requested and none is needed.
"""
import inspect
import os
import tempfile

import pytest


def _tmpdir_is_writable():
    """Probe by actually writing, not by checking a path or an env var -- the sandbox failure
    mode was that TMPDIR was set and the directory was not usable."""
    try:
        with tempfile.TemporaryDirectory() as td:
            probe = os.path.join(td, ".probe")
            with open(probe, "w") as fh:
                fh.write("x")
            return True
    except Exception:
        return False


TMPDIR_WRITABLE = _tmpdir_is_writable()

SKIP_REASON = (
    "no writable temporary directory in this environment (read-only audit sandbox). "
    "Skipped rather than errored so it does not read as a defect -- see tests/conftest.py."
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "needs_tmpdir: requires a writable temp directory; skipped (not errored) without one",
    )


TMPDIR_APIS = ("TemporaryDirectory", "NamedTemporaryFile", "mkdtemp", "mkstemp")
TMPDIR_FIXTURES = frozenset({"tmp_path", "tmpdir", "tmp_path_factory"})
# The names pytest gives a class's per-test setup. `setUp` is unittest, `setup_method` is pytest's
# own class style, `setUpClass` runs once but its failure errors every test in the class.
SETUP_ATTRS = ("setUp", "setup_method", "setUpClass", "setup_class")


def _source_of(obj):
    try:
        return inspect.getsource(obj)
    except Exception:
        return ""


def _is_local_helper(obj, module):
    """Is `obj` a class/function DEFINED IN this test module, and so safe to read the source of?

    The name filter matters more than it looks. The depth-1 walk below reads the source of things
    `setUp` mentions, and the very first name `setUp` mentions is usually `tempfile` -- whose source
    contains every string in TMPDIR_APIS, so following modules made the walk fire on any setUp that
    merely referenced the module. That was caught by a surviving mutant: deleting the direct
    setUp-source check changed nothing, because the walk was matching the stdlib and not the helper.
    Restricting to definitions owned by the test module keeps `_Repo` and drops `tempfile`.

    Both conditions are load-bearing and each is pinned by a test, in the direction it acts:
    `isclass or isfunction` excludes modules (an explicit `types.ModuleType` check was removed as
    dead code -- it never fired, which a surviving mutant showed), and the `__module__` equality
    excludes helpers imported from elsewhere. The second is a deliberate NARROWING and it leaves a
    residual: a setUp that builds an IMPORTED helper owning a tmpdir is not detected. Following
    imports would fix that and reintroduce the over-fire this whole design avoids -- an imported
    class merely mentioning a tmpdir API anywhere in its body would skip every test in the class --
    so the marker is the remedy, and `test_an_IMPORTED_helper_is_the_known_residual` states the
    boundary as an executable fact rather than leaving it to be rediscovered.
    """
    if not (inspect.isclass(obj) or inspect.isfunction(obj)):
        return False
    return getattr(obj, "__module__", None) == getattr(module, "__name__", None)


def _item_needs_tmpdir(item):
    """Does this item require a writable temp directory? Four routes, in order of reliability.

    Route 1 (marker) is authoritative. Routes 2-4 are the safety net for a test that forgets it,
    and each exists because it was measured missing -- see the N6 note in the module docstring for
    the per-route counts over the real suite. Every route is wrapped so a probe that cannot run
    degrades to "not detected" rather than breaking collection: this hook runs before every suite
    in the directory, and a guard that can abort collection is worse than no guard.
    """
    # 1. the marker, which an author states explicitly
    if item.get_closest_marker("needs_tmpdir") is not None:
        return True

    # 2. a pytest tmpdir fixture in the item's resolved fixture closure. This is the largest
    #    stratum (171) and the guard used to look at fixtures not at all -- and a fixture that
    #    raises is reported as an ERROR, the mode this file exists to suppress.
    if set(getattr(item, "fixturenames", ()) or ()) & TMPDIR_FIXTURES:
        return True

    fn = getattr(item, "function", None)

    # 3. the test function's own body. co_consts first (cheap, and survives a missing source file),
    #    then the source text, which catches attribute-style uses that leave no string constant.
    try:
        if any(isinstance(c, str) and any(a in c for a in TMPDIR_APIS)
               for c in fn.__code__.co_consts):
            return True
    except Exception:
        pass
    if any(a in _source_of(fn) for a in TMPDIR_APIS):
        return True

    # 4. the class's SETUP methods only -- NOT the whole class. A tmpdir built in setUp errors
    #    every test in the class while none of their bodies name it (113 items); scanning the whole
    #    class body instead would also skip 154 items whose sibling methods use a tmpdir but which
    #    need none themselves, which is over-firing and hides real coverage.
    #
    #    One level of indirection is followed, because the common idiom is that setUp constructs a
    #    helper which owns the tmpdir -- `RevisionGateTest.setUp` does `self.r = _Repo()` and it is
    #    `_Repo.__init__` that calls `mkdtemp` (12 items). Following it cannot over-fire: whatever
    #    setUp builds is built for every test in the class. Depth is capped at 1 deliberately --
    #    deeper is an unbounded call-graph walk during collection, and the marker is the remedy for
    #    anything this misses.
    cls = getattr(item, "cls", None)
    if cls is None:
        return False
    module = getattr(item, "module", None)
    for name in SETUP_ATTRS:
        attr = getattr(cls, name, None)
        if attr is None:
            continue
        if any(a in _source_of(attr) for a in TMPDIR_APIS):
            return True
        if module is None:
            continue
        for ref in getattr(getattr(attr, "__code__", None), "co_names", ()) or ():
            helper = getattr(module, ref, None)
            if not _is_local_helper(helper, module):
                continue
            if any(a in _source_of(helper) for a in TMPDIR_APIS):
                return True
    return False


def pytest_collection_modifyitems(config, items):
    """Auto-skip anything that needs a temp dir when none is available.

    Detection is by marker OR by inference, so a new test that forgets the marker still skips
    cleanly instead of erroring. That is deliberate: relying on every author to remember a marker
    is the same 'depends on someone remembering' weakness this lane has been removing -- and until
    2026-08-16 the inference covered only one of the four routes in `_item_needs_tmpdir`, missing
    both shapes that produce an ERROR rather than a failure."""
    if TMPDIR_WRITABLE:
        return
    skip = pytest.mark.skip(reason=SKIP_REASON)
    for item in items:
        if _item_needs_tmpdir(item):
            item.add_marker(skip)


def pytest_report_header(config):
    return (f"standard-P4 suites: writable tmpdir = {TMPDIR_WRITABLE}"
            + ("" if TMPDIR_WRITABLE else "  -> tmpdir-dependent tests will SKIP, not error"))


# ---------------------------------------------------------------------------
# Import-time-unsafe modules in OTHER lanes (2026-08-09).
#
# tests/test_p3f_pet_fullevent_launcher.py does `TEXT = open(LAUNCHER).read()` at module scope
# against a hardcoded /pscratch path, so off the cluster it raises FileNotFoundError during
# COLLECTION and pytest aborts the entire tests/ directory -- every off-cluster run of every
# suite, not just theirs.
#
# The obvious fix -- guard inside that module -- is the WRONG one, and I made it first and had to
# undo it: that file's sha256 is frozen into
# docs/orchestration/state/p3f-pet-gate3-launch-code-gate-20260720.json as `launcher_test`, so a
# one-line guard silently voided a PET gate binding, and tests/test_hash_bindings.py went red on
# a receipt this lane does not own. Editing another lane's file to fix MY collection problem was
# the error; the repo rule is that a drifted binding is re-issued by re-running the owning gate,
# never by editing the file or the hash. Skipping collection from here is equivalent for the
# purpose and leaves the frozen file byte-identical.
_PET_LAUNCHER = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh"
collect_ignore = []
if not os.path.exists(_PET_LAUNCHER):
    collect_ignore.append("test_p3f_pet_fullevent_launcher.py")
