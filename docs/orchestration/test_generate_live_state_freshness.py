"""`--check-freshness` must not depend on how long either host abbreviates a sha.

Hermetic: a throwaway repository with three commits. The recorded `Git:` value is written at
several abbreviation lengths, because the rendering host and the checking host each choose their
own `rev-parse --short` length (2026-10-28: 8 digits on a fresh cluster clone, 9 in this checkout).
"""
import contextlib
import io
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from generate_live_state import check_freshness


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t",
                           "-c", "user.email=t@t", *args], cwd=cwd, env=env,
                          capture_output=True, text=True, check=True).stdout.strip()


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp(prefix="freshness-"))
        git(self.repo, "init", "-q")
        self.live = self.repo / "docs/orchestration/LIVE-STATE.md"
        self.live.parent.mkdir(parents=True)
        self.shas = []
        for n in range(3):
            (self.repo / f"f{n}").write_text(f"{n}\n")
            git(self.repo, "add", f"f{n}")
            git(self.repo, "commit", "-q", "-m", f"c{n}")
            self.shas.append(git(self.repo, "rev-parse", "HEAD"))

    def tearDown(self):
        shutil.rmtree(self.repo, True)

    def check(self, recorded):
        self.live.write_text(f"- Git: `{recorded}`; 0 local worktree entries\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_freshness(self.repo)
        return code, out.getvalue()

    def test_head_is_fresh_at_every_abbreviation_length(self):
        head = self.shas[-1]
        for length in (7, 8, 9, 12, 40):
            code, out = self.check(head[:length])
            self.assertEqual(code, 0, (length, out))
            self.assertIn("== HEAD", out)

    def test_parent_is_fresh_at_every_abbreviation_length(self):
        parent = self.shas[-2]
        for length in (7, 8, 9, 40):
            code, out = self.check(parent[:length])
            self.assertEqual(code, 0, (length, out))
            self.assertIn("HEAD's parent", out)

    def test_grandparent_is_stale(self):
        code, out = self.check(self.shas[0][:8])
        self.assertEqual(code, 1, out)
        self.assertIn("STALE", out)

    def test_an_unknown_sha_is_stale_and_a_too_short_one_cannot_be_checked(self):
        self.assertEqual(self.check("0123456789abcdef")[0], 1)
        self.assertEqual(self.check(self.shas[-1][:6])[0], 2)


if __name__ == "__main__":
    unittest.main()
