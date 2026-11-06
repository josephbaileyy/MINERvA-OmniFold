#!/usr/bin/env python3
"""Run a unittest suite and record each test's outcome from unittest's own result object, not from its text.

    run_suite.py run   TESTFILE OUT.json      run every test in TESTFILE (verbose output as usual; nothing printed by
                                              the code under test is suppressed), write per-test outcomes to OUT.json
    run_suite.py check OUT.json EXPECT TEST   exit 0 only if EXPECT tests ran, none skipped, failed or errored, and the
                                              test TEST (Class.method) has outcome "ok"; print one RUN PASS/FAIL line

Why: a test whose code prints to stdout between unittest's "test name ..." and its "ok" (RooUnfoldBayes does) defeats
any one-line grep of the verbose output; the REF-C2C1 cluster run of 2026-11-05 read RUN FAIL that way with every test
passing. Outcomes recorded here are the ones unittest itself decided.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


class Recording(unittest.TextTestResult):
    """TextTestResult that also keeps each test's outcome by name."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.outcomes: dict[str, str] = {}

    @staticmethod
    def name(test) -> str:
        return f"{type(test).__name__}.{test._testMethodName}" if hasattr(test, "_testMethodName") else str(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[self.name(test)] = "ok"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[self.name(test)] = "fail"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[self.name(test)] = "error"  # a class-level error is recorded under its setUpClass name

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[self.name(test)] = "skip"

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcomes[self.name(test)] = "expected failure"

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcomes[self.name(test)] = "unexpected success"


def run(testfile: Path, out: Path) -> int:
    sys.path.insert(0, str(testfile.resolve().parent))
    spec = importlib.util.spec_from_file_location(testfile.stem, testfile)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    runner = unittest.TextTestRunner(verbosity=2, resultclass=Recording)
    result = runner.run(suite)
    rec = {"schema": "ref-c2c1-suite-run/1", "testfile": str(testfile), "ran": result.testsRun,
           "outcomes": dict(sorted(result.outcomes.items())), "was_successful": result.wasSuccessful()}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    return 0 if result.wasSuccessful() else 1


def verdict(rec: dict, expect: int, must_ok: str) -> tuple[bool, str]:
    """The run passes only if it ran EXPECT tests, none skipped, failed or errored, and MUST_OK is "ok"."""
    o = rec["outcomes"]
    bad = {k: v for k, v in o.items() if v != "ok"}
    if rec["ran"] != expect:
        return False, f"ran {rec['ran']} of {expect} tests"
    if bad:
        return False, f"not ok: {bad}"
    if o.get(must_ok) != "ok":
        return False, f"{must_ok} outcome {o.get(must_ok)!r}"
    return True, f"{expect} tests, none skipped, failed or errored; {must_ok} ok"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["run"] and len(argv) == 3:
        return run(Path(argv[1]), Path(argv[2]))
    if argv[:1] == ["check"] and len(argv) == 4:
        ok, why = verdict(json.loads(Path(argv[1]).read_text()), int(argv[2]), argv[3])
        print(("RUN PASS: " if ok else "RUN FAIL: ") + why)
        return 0 if ok else 1
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
