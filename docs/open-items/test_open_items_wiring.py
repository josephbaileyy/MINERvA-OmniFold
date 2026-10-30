#!/usr/bin/env python3
"""OI-148: the seven-column check is WIRED, and the long-line pin can only fall.

    python3 docs/open-items/test_open_items_wiring.py

Joseph's decision of 2026-10-30 (DECISION-20261030-joseph-canonical-checkout-and-table-check.md, item 2): run
`check_open_items_columns.py --check` in the commit hook and in CI, and reset the long-line pin to 147, "so it can only
go down from here".

WHAT IS TESTED, in both directions:
  * the hook's run line and the CI step exist as code, not as comments;
  * the hook's OWN `run()` and its OWN wired line, executed as a pre-commit hook in a scratch repository, let a commit
    with a well-formed table through and refuse one with a malformed row, leaving HEAD where it was;
  * the pin is read from verify_open_items_restructure.py's source and must be <= 147; a copy raised to 148 is caught.

WHAT IS NOT TESTED: the tree's own line count against the pin. The ratchet is a hand-maintained count that a blameless
committer cannot always pass, so it stays out of every gate (check_open_items_columns.py's docstring), and this file
reads the pin's VALUE only. Stdlib only. Nothing outside a TemporaryDirectory is written, except the hook's own
/tmp/.hook.<pid> scratch file, which the hook removes.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HOOK = ROOT / ".githooks" / "pre-commit"
CI = ROOT / ".github" / "workflows" / "record-checks.yml"
CHECKER = HERE / "check_open_items_columns.py"
PARSER = HERE / "verify_open_items_restructure.py"
OPEN = ROOT / "docs" / "OPEN_ITEMS.md"

COMMAND = "python3 docs/open-items/check_open_items_columns.py --check"
PIN_CEILING = 147   # the value Joseph's decision set; the pin may only fall below it
HOOK_LINE = re.compile(r'^run\s+"[^"]+"\s+' + re.escape(COMMAND) + r"\s*$", re.M)
CI_LINE = re.compile(r"^\s+run:\s+" + re.escape(COMMAND) + r"\s*$", re.M)
PIN = re.compile(r"^\s*OVER_LIMIT_PINNED\s*=\s*(\d+)\s*(#.*)?$", re.M)


def pin_value(source: str) -> int:
    """The one OVER_LIMIT_PINNED assignment in the parser's source. Zero or several is an error, not a pass."""
    found = PIN.findall(source)
    if len(found) != 1:
        raise AssertionError(f"expected exactly one OVER_LIMIT_PINNED assignment, found {len(found)}")
    return int(found[0][0])


def pin_ok(source: str) -> bool:
    return pin_value(source) <= PIN_CEILING


def hook_run_function(hook_text: str) -> str:
    """The hook's own `run() { ... }` block, verbatim, so the scratch hook executes the real dispatcher logic."""
    m = re.search(r"^run\(\) \{\n.*?^\}\n", hook_text, re.M | re.S)
    if not m:
        raise AssertionError("no `run() {` ... `}` block in .githooks/pre-commit")
    return m.group(0)


def clean_env() -> dict[str, str]:
    """No inherited GIT_* variable may point the scratch repository's git at this checkout."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t.invalid")
    return env


def malform(text: str) -> str:
    """Add one unescaped `|` inside the first data row's state cell: one extra field, the defect the check exists for."""
    lines = text.split("\n")
    rows = [i for i, line in enumerate(lines) if line.startswith("| OI-")]
    if not rows:
        raise AssertionError("no data row to malform")
    i = rows[0]
    j = lines[i].index("|", 1) + 1
    lines[i] = lines[i][:j] + " a | b " + lines[i][j:]
    return "\n".join(lines)


class TheWiringIsCode(unittest.TestCase):

    def test_the_hook_has_the_run_line(self):
        self.assertRegex(HOOK.read_text(encoding="utf-8"), HOOK_LINE)

    def test_ci_has_the_step(self):
        self.assertRegex(CI.read_text(encoding="utf-8"), CI_LINE)

    def test_ci_runs_this_test(self):
        self.assertRegex(CI.read_text(encoding="utf-8"),
                         re.compile(r"^\s+run:\s+python3 docs/open-items/test_open_items_wiring\.py\s*$", re.M))

    def test_a_commented_line_is_not_wiring(self):
        """Power for the two tests above: a commented-out line must not match."""
        self.assertNotRegex(f'# run "x" {COMMAND}\n', HOOK_LINE)
        self.assertNotRegex(f"        # run: {COMMAND}\n", CI_LINE)


class TheWiredLineActsInBothDirections(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oi148-wiring-"))
        self.repo = self.tmp / "repo"
        (self.repo / "docs" / "open-items").mkdir(parents=True)
        (self.repo / "hooks").mkdir()
        for src in (CHECKER, PARSER):
            shutil.copy2(src, self.repo / "docs" / "open-items" / src.name)
        self.good = OPEN.read_text(encoding="utf-8")
        (self.repo / "docs" / "OPEN_ITEMS.md").write_text(self.good, encoding="utf-8")
        hook_text = HOOK.read_text(encoding="utf-8")
        wired = HOOK_LINE.search(hook_text)
        self.assertIsNotNone(wired, "the hook has no wired line to execute")
        hook = self.repo / "hooks" / "pre-commit"
        hook.write_text("#!/bin/bash\nset -uo pipefail\ncd \"$(git rev-parse --show-toplevel)\" || exit 2\n"
                        "fail=0\nran=0\npassed=0\n" + hook_run_function(hook_text) + wired.group(0) + "\n"
                        "rm -f /tmp/.hook.$$\nexit \"$fail\"\n", encoding="utf-8")
        hook.chmod(0o755)
        self.env = clean_env()
        self.git("init", "-q")
        self.git("add", "docs")
        # The first commit runs without the hook, so each test starts from a committed good table.
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "base")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(("git",) + args, cwd=self.repo, env=self.env, capture_output=True, text=True)

    def commit_with_hook(self, text: str) -> subprocess.CompletedProcess:
        (self.repo / "docs" / "OPEN_ITEMS.md").write_text(text, encoding="utf-8")
        self.git("add", "docs/OPEN_ITEMS.md")
        # `-c core.hooksPath=` on the command line writes no config, here or anywhere.
        return self.git("-c", "core.hooksPath=hooks", "commit", "-q", "--allow-empty", "-m", "change")

    def test_a_well_formed_table_commits(self):
        p = self.commit_with_hook(self.good + "\n")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.head)

    def test_a_malformed_row_is_refused_and_head_does_not_move(self):
        p = self.commit_with_hook(malform(self.good))
        self.assertNotEqual(p.returncode, 0, "a malformed row was committed through the wired hook")
        self.assertIn("PRE-COMMIT FAIL: OPEN_ITEMS seven columns", p.stdout + p.stderr)
        self.assertIn("8 fields, expected 7", p.stdout + p.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.head)

    def test_the_malformation_is_the_only_difference(self):
        """Guards the refusal above against being caused by something other than the row."""
        bad = malform(self.good)
        diff = [(a, b) for a, b in zip(self.good.split("\n"), bad.split("\n")) if a != b]
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][1].replace(" a | b ", "", 1), diff[0][0])


class ThePinCanOnlyFall(unittest.TestCase):

    def setUp(self):
        self.source = PARSER.read_text(encoding="utf-8")

    def test_the_pin_is_at_or_below_the_ceiling(self):
        self.assertLessEqual(pin_value(self.source), PIN_CEILING,
                             "OVER_LIMIT_PINNED was raised above 147; raising it needs a new decision")

    def test_a_raised_pin_is_caught(self):
        raised = PIN.sub(lambda m: m.group(0).replace(m.group(1), str(PIN_CEILING + 1)), self.source)
        self.assertFalse(pin_ok(raised))

    def test_a_lowered_pin_passes(self):
        lowered = PIN.sub(lambda m: m.group(0).replace(m.group(1), str(PIN_CEILING - 7)), self.source)
        self.assertTrue(pin_ok(lowered))

    def test_a_missing_or_duplicated_pin_is_an_error_not_a_pass(self):
        with self.assertRaises(AssertionError):
            pin_value(PIN.sub("", self.source))
        with self.assertRaises(AssertionError):
            pin_value(self.source + "\n    OVER_LIMIT_PINNED = 1\n")


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if result.wasSuccessful() and result.testsRun > 0 else 1)
