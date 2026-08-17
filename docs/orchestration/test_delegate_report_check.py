"""Tests for delegate_report_check (BEN-390).

Every failure string below is a VERBATIM capture from a real dispatch on 2026-08-17, not a
paraphrase — a signature table tested against invented text tests the table's spelling, not the
delegate's. Provenance for each is in
FINDING-20260817-a-delegate-failure-has-no-reliable-signal.md.

Per the repo rule that a filter is tested in the direction it acts, this covers both directions:
each signature FIRES on the text it was written for, and a genuine report does NOT trip any of
them.
"""

import tempfile
import unittest
from pathlib import Path

import delegate_report_check as drc

# --- verbatim captures, 2026-08-17 ---------------------------------------------------------
CODEX_PERSONAL_LIMIT = (
    "ERROR: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), "
    "visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at "
    "Aug 20th, 2026 12:43 AM.\n"
)
CODEX_SCHOOL_CREDITS = (
    "ERROR: Your workspace is out of credits. Ask your workspace owner to refill in order to "
    "continue.\n"
)
AGY_HEADLESS_DENIAL = (
    'jetski: no output produced — a tool required the "command" permission that headless mode '
    "cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in "
    "settings.json (e.g. command(<target>)). Alternatively, re-run with "
    "--dangerously-skip-permissions to auto-approve all tools.\n"
)
CODEX_UNTRUSTED_DIR = (
    "Reading additional input from stdin...\n"
    "Not inside a trusted directory and --skip-git-repo-check was not specified.\n"
)
GENUINE_REPORT = (
    "VERDICT: ABSENT-FROM-CODE\n"
    "Searched nd-unfolding/*.py at HEAD and across --all; unrestricted control returned 72 "
    "commits, so the corpus is non-empty.\n"
)


class Tmp:
    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        self.dir = Path(self._d.name)
        return self

    def __exit__(self, *exc):
        self._d.cleanup()

    def write(self, name: str, text: str) -> Path:
        p = self.dir / name
        p.write_text(text)
        return p


class TestSignaturesFire(unittest.TestCase):
    """The guard direction: each observed failure must be caught."""

    def _fails(self, text, **kw):
        with Tmp() as t:
            ok, reasons = drc.evaluate(t.write("report.txt", text), **kw)
        self.assertFalse(ok, f"should have failed on: {text[:60]!r}")
        return reasons

    def test_codex_personal_usage_limit(self):
        reasons = self._fails(CODEX_PERSONAL_LIMIT)
        self.assertTrue(any("personal-account usage limit" in r for r in reasons), reasons)

    def test_codex_school_out_of_credits(self):
        """The wording that broke a failover predicate keyed to 'usage limit'."""
        reasons = self._fails(CODEX_SCHOOL_CREDITS)
        self.assertTrue(any("out of credits" in r for r in reasons), reasons)

    def test_agy_headless_denial_is_caught_despite_being_non_empty(self):
        """303 B of fluent prose: 'non-empty' alone would have passed this."""
        self.assertGreater(len(AGY_HEADLESS_DENIAL), 300)
        reasons = self._fails(AGY_HEADLESS_DENIAL)
        self.assertTrue(any("headless permission auto-denial" in r for r in reasons), reasons)

    def test_untrusted_directory(self):
        reasons = self._fails(CODEX_UNTRUSTED_DIR)
        self.assertTrue(any("trusted directory" in r for r in reasons), reasons)

    def test_stdin_block_fires_when_it_is_the_whole_output(self):
        """The hang case: 39 bytes and nothing else, after 300 s. Captured verbatim."""
        reasons = self._fails("Reading additional input from stdin...\n")
        self.assertTrue(any("blocked on stdin" in r for r in reasons), reasons)

    def test_missing_report(self):
        with Tmp() as t:
            ok, reasons = drc.evaluate(t.dir / "never-written.txt")
        self.assertFalse(ok)
        self.assertTrue(any(r.startswith("MISSING") for r in reasons), reasons)

    def test_empty_report(self):
        reasons = self._fails("   \n\n")
        self.assertTrue(any(r.startswith("EMPTY") for r in reasons), reasons)

    def test_prompt_echo(self):
        prompt = "Report whether the jitter scalar exists in code. Answer PRESENT or ABSENT."
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", prompt), prompt_file=t.write("prompt.txt", prompt)
            )
        self.assertFalse(ok)
        self.assertTrue(any(r.startswith("PROMPT ECHO") for r in reasons), reasons)

    def test_format_mismatch_is_the_primary_test(self):
        """A plausible report that does not answer in the required form still fails."""
        reasons = self._fails(
            "I looked into this and it seems fine overall.\n", require_regex=r"^VERDICT: \w+"
        )
        self.assertTrue(any(r.startswith("FORMAT") for r in reasons), reasons)

    def test_log_scan_catches_a_failure_a_clean_report_would_hide(self):
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", GENUINE_REPORT),
                require_regex=r"^VERDICT: \w+",
                log=t.write("full.log", CODEX_PERSONAL_LIMIT),
            )
        self.assertFalse(ok)
        self.assertTrue(any("in log" in r for r in reasons), reasons)


class TestNoFalsePositives(unittest.TestCase):
    """The other direction: a real report must pass, or the check gets switched off."""

    def test_genuine_report_passes(self):
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", GENUINE_REPORT), require_regex=r"^VERDICT: \w+"
            )
        self.assertTrue(ok, reasons)

    def test_report_discussing_limits_in_prose_is_not_a_quota_failure(self):
        """'usage limit' inside a sentence about the finding is the obvious false positive."""
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", "VERDICT: OK\nThe run stayed well under the wall limit.\n"),
                require_regex=r"^VERDICT: \w+",
            )
        self.assertTrue(ok, reasons)

    def test_stdin_line_in_a_healthy_log_is_not_a_failure(self):
        """`codex exec` prints this line on every run, including with `< /dev/null`. A substring
        match here would fire on every codex log ever captured (BEN-381's shape)."""
        healthy_log = (
            "Reading additional input from stdin...\n"
            "OpenAI Codex v0.147.0\n--------\nworkdir: /repo\nmodel: gpt-5.6-sol\n--------\n"
            "user\nAnswer PRESENT or ABSENT.\ncodex\nVERDICT: PRESENT\n"
        )
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", GENUINE_REPORT),
                require_regex=r"^VERDICT: \w+",
                log=t.write("full.log", healthy_log),
            )
        self.assertTrue(ok, reasons)

    def test_longer_report_quoting_its_prompt_is_not_an_echo(self):
        prompt = "Answer PRESENT or ABSENT."
        report = (
            "Dispatch was: Answer PRESENT or ABSENT.\n"
            "VERDICT: PRESENT\n"
            "a0cdc019 nd-unfolding/unified_throw_cov.py:224 carries the block with its derivation, "
            "and 07c18aee removed it by editing the file rather than deleting it.\n"
        )
        with Tmp() as t:
            ok, reasons = drc.evaluate(
                t.write("report.txt", report),
                require_regex=r"^VERDICT: \w+",
                prompt_file=t.write("prompt.txt", prompt),
            )
        self.assertTrue(ok, reasons)


class TestExitCodes(unittest.TestCase):
    def test_main_returns_2_on_failure_and_0_on_success(self):
        with Tmp() as t:
            bad = t.write("bad.txt", CODEX_SCHOOL_CREDITS)
            good = t.write("good.txt", GENUINE_REPORT)
            self.assertEqual(drc.main([str(bad)]), 2)
            self.assertEqual(drc.main([str(good), "--require-regex", r"^VERDICT: \w+"]), 0)


if __name__ == "__main__":
    unittest.main()
