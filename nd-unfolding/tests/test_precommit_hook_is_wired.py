#!/usr/bin/env python3
"""The pre-commit hook is WIRED — asserted from the test suite, because it cannot be asserted from the hook.

**Why this is not in the hook.** On 2026-08-17 a lane ran `git config core.hooksPath <throwaway>/.githooks`
inside a linked worktree and then deleted that worktree. `extensions.worktreeConfig` is unset here, so
linked worktrees share `.git/config`; the write landed in the MAIN repo's config and pointed
`core.hooksPath` at a directory that no longer existed. **Git skips a missing `hooksPath` silently — no
warning, no error, exit 0.** Two commits were made in the ~30-minute window with all nine checks not run,
and nothing said so.

**The bootstrap constraint is real: a check that `core.hooksPath` resolves cannot live in the hook, because
a disabled hook cannot run it.** The escape is to put the assertion somewhere lanes already execute code
that is not the hook. That is this suite, which every lane runs constantly and which runs regardless of
hook state.

**What this catches that the existing instruments do not.**
`CONVENTION-verifying-a-check-is-deployed.md` already prescribes the deployment PROBE (commit something
only the check can reject) and already records that reading the `N checks passed` count verifies a hook
*line* and cannot see a stale *payload* (`BEN-224`). But **every instrument in that convention assumes the
hook EXECUTED.** Its "four reasons a check runs and tells you nothing" table is about checks that run; the
nearest row, `BEN-185`, is a check correctly SKIPPED inside a passing suite. **A hook that never runs at
all produces no output, and absence of output does not look like failure** — `BEN-344` applied to the hook
itself: a green run and a run that never happened are indistinguishable unless you look for the POSITIVE
signal.

**Deliberately NOT the remedy: `extensions.worktreeConfig = true`.** Measured in a throwaway repo before
recommending anything — with the extension enabled, a PLAIN `git config demo.two x` inside a linked
worktree **still lands in the shared config** (`config.worktree` stays empty). Only an explicit
`git config --worktree` write goes local, which requires the author to already know. The extension is
false comfort for this failure. **What does work, measured: `git -c key=value <cmd>` writes nothing at
all** — that is the operational rule, and it needs no repo configuration.
"""
import os
import subprocess
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent


def _git(*args, cwd=None):
    p = subprocess.run(("git",) + args, cwd=str(cwd or REPO),
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return p.returncode, p.stdout.decode().strip()


def hook_resolution(configured, toplevel):
    """PURE: given the configured `core.hooksPath` and a top-level, return the pre-commit path.

    Factored out so both directions are testable without writing any git config — writing config in a
    worktree is the very act that caused the incident, so this file does not do it, not even in a
    temporary repo.
    """
    if not configured:
        return Path(toplevel) / ".git" / "hooks" / "pre-commit", "git default"
    p = Path(configured)
    if not p.is_absolute():
        p = Path(toplevel) / p
    return p / "pre-commit", "core.hooksPath"


def is_wired(pre_commit: Path):
    return pre_commit.is_file() and os.access(pre_commit, os.X_OK)


class PreCommitHookIsWired(unittest.TestCase):

    def setUp(self):
        rc, self.configured = _git("config", "--get", "core.hooksPath")
        self.configured = self.configured if rc == 0 else ""
        rc, self.toplevel = _git("rev-parse", "--show-toplevel")
        self.assertEqual(rc, 0, "not inside a git work tree")

    def test_the_hook_git_would_run_EXISTS_and_is_executable(self):
        """The whole point. If this fails, commits are being made unchecked and silently."""
        pre_commit, via = hook_resolution(self.configured, self.toplevel)
        self.assertTrue(
            is_wired(pre_commit),
            f"core.hooksPath resolves to {pre_commit}, which is not an executable file (via {via}; "
            f"configured value {self.configured!r}). GIT SKIPS A MISSING hooksPath SILENTLY -- no "
            f"warning, exit 0 -- so every commit made in this state runs ZERO checks and says nothing. "
            f"Repair: `git config --unset core.hooksPath` then `git config core.hooksPath .githooks`, "
            f"from the MAIN checkout. Do not diagnose this by re-reading terminal output: the evidence "
            f"is the ABSENCE of the 'N checks passed' line.")

    def test_it_is_the_TRACKED_hook_and_not_some_other_file(self):
        """Absence is one failure; pointing at a different existing directory is the other (`BEN-224`
        -- the hook file and the payload coming from different trees). Compares bytes against the
        tracked `.githooks/pre-commit` rather than trusting the path."""
        pre_commit, _ = hook_resolution(self.configured, self.toplevel)
        if not is_wired(pre_commit):
            self.skipTest("not wired at all; the test above owns that failure")
        rc, tracked = _git("show", "HEAD:.githooks/pre-commit")
        self.assertEqual(rc, 0, "no .githooks/pre-commit at HEAD to compare against")
        self.assertEqual(
            pre_commit.read_text().strip(), tracked.strip(),
            f"the hook git would run ({pre_commit}) differs from the tracked .githooks/pre-commit at "
            f"HEAD. A hook that exists but is not the committed one passes silently while enforcing "
            f"something else (BEN-224).")

    def test_the_resolver_DETECTS_a_broken_path_and_so_this_check_can_fail(self):
        """Power, in the direction that matters, with no config written anywhere.

        Without this, `is_wired` returning True unconditionally would satisfy the assertions above and
        the check would be a green that cannot fail -- which is the exact class it exists to catch.
        """
        top = self.toplevel
        broken, via = hook_resolution("/nonexistent-hooks-dir-for-this-test", top)
        self.assertEqual(via, "core.hooksPath")
        self.assertFalse(is_wired(broken), "a nonexistent hooksPath was reported as wired")

        deleted_worktree = hook_resolution(
            "/tmp/some-deleted-throwaway-worktree/.githooks", top)[0]
        self.assertFalse(is_wired(deleted_worktree),
                         "the incident's exact shape -- hooksPath into a deleted worktree -- was "
                         "reported as wired")

        # and the relative form must resolve against the top-level, which is how this repo sets it
        rel, _ = hook_resolution(".githooks", top)
        self.assertEqual(rel, Path(top) / ".githooks" / "pre-commit")

        # a directory that exists but holds no pre-commit is also not wired
        self.assertFalse(is_wired(Path(top) / "pre-commit"),
                         "a path with no pre-commit file was reported as wired")


if __name__ == "__main__":
    unittest.main(verbosity=2)
