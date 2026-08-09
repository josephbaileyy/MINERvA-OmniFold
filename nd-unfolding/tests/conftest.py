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
