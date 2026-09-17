"""Regression tests for the A1 launcher's shell contract.

Job 58470007 died in four seconds because the launcher ran ``set -u`` while conda's
``activate-binutils_linux-64.sh`` reads ``$ADDR2LINE`` unbound. The login-node smoke
test had exercised the payload but not the launcher's shell options, so it passed.
These tests read the launcher's real lines rather than restating them, so a future
edit that reintroduces the fault fails here instead of on the cluster.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest

LAUNCHER = Path(__file__).resolve().parent / "sbatch_source_characterization.sh"


class LauncherShellContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = LAUNCHER.read_text()
        self.lines = self.text.splitlines()

    def test_strict_mode_is_on(self) -> None:
        self.assertIn("set -euo pipefail", self.text)

    def test_conda_activation_is_bracketed_by_set_plus_u(self) -> None:
        activate = [
            index for index, line in enumerate(self.lines) if "conda activate" in line
        ]
        self.assertTrue(activate, "launcher no longer activates an environment")
        for index in activate:
            before = "\n".join(self.lines[max(0, index - 6) : index])
            after = "\n".join(self.lines[index : index + 4])
            self.assertIn(
                "set +u", before, "activation must be preceded by `set +u`"
            )
            self.assertIsNotNone(
                re.search(r"^\s*set -u\s*$", after, flags=re.MULTILINE),
                "`-u` must be restored on its own line after activation",
            )

    def test_the_hook_eval_is_inside_the_same_relaxed_window(self) -> None:
        # The hook eval sources the same activate.d scripts, so it must be inside
        # the window too, not only the `conda activate` line.
        relaxed = re.search(
            r"set \+u\n(.*?)\nset -u", self.text, flags=re.DOTALL
        )
        self.assertIsNotNone(relaxed, "no relaxed window found")
        window = relaxed.group(1)
        self.assertIn("shell.bash hook", window)
        self.assertIn("conda activate", window)

    def test_it_never_resubmits_itself(self) -> None:
        self.assertNotIn("sbatch", self.text)

    def test_it_pins_the_commit_and_requires_a_clean_tree(self) -> None:
        self.assertIn('[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]', self.text)
        self.assertIn('[[ -z "$(git status --porcelain)" ]]', self.text)

    def test_it_refuses_to_overwrite_an_existing_output(self) -> None:
        self.assertIn('[[ ! -e "$output" ]]', self.text)

    def test_it_requires_a_production_crosscheck_to_have_run(self) -> None:
        self.assertIn("production_crosschecks_passed", self.text)

    def test_it_is_cpu_only(self) -> None:
        self.assertIn("--constraint=cpu", self.text)
        self.assertNotIn("--gpus", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
