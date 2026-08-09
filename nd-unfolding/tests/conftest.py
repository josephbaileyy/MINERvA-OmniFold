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
"""
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


def pytest_collection_modifyitems(config, items):
    """Auto-skip anything that needs a temp dir when none is available.

    Detection is by marker OR by the test's own source mentioning TemporaryDirectory, so a new
    test that forgets the marker still skips cleanly instead of erroring. That is deliberate:
    relying on every author to remember a marker is the same 'depends on someone remembering'
    weakness this lane has been removing."""
    if TMPDIR_WRITABLE:
        return
    skip = pytest.mark.skip(reason=SKIP_REASON)
    for item in items:
        needs = item.get_closest_marker("needs_tmpdir") is not None
        if not needs:
            try:
                src = item.function.__code__.co_consts
                needs = any(isinstance(c, str) and "TemporaryDirectory" in c for c in src)
            except Exception:
                needs = False
            if not needs:
                try:
                    import inspect
                    needs = "TemporaryDirectory" in inspect.getsource(item.function)
                except Exception:
                    needs = False
        if needs:
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
