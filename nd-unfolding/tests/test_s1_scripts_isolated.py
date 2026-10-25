"""S1's two scripts run as S1-DECLARATION.md section 3 invokes them: ``env -u PYTHONPATH <python> -I -B <script>``,
from a cwd outside nd-unfolding. Under -I the script's directory is not on sys.path (Python >= 3.4; 3.11 reports it as
sys.flags.safe_path), so a script that imports a sibling module must put its own directory there. The 2026-10-25 S1 assembly
stopped on exactly this (ModuleNotFoundError: s5p_stage1_inspect); the other tests import the module after their own
sys.path.insert and could not see it."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]


def run_isolated(script: str, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    with tempfile.TemporaryDirectory(prefix="s1-isolated-") as cwd:
        return subprocess.run([sys.executable, "-I", "-B", str(ND / script), *args], cwd=cwd, env=env,
                              capture_output=True, text=True, timeout=120)


class IsolatedInvocation(unittest.TestCase):
    def check_help(self, script: str) -> None:
        r = run_isolated(script, "--help")
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("usage:", r.stdout)

    def test_s1_assemble_imports_under_isolation(self):
        self.check_help("s1_assemble.py")

    def test_s1_controls_imports_under_isolation(self):
        self.check_help("s1_controls.py")

    def test_s1_controls_argparse_error_is_not_an_import_error(self):
        r = run_isolated("s1_controls.py", "no-such-gate")
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 2, r.stderr)  # argparse's usage error, reached only after the imports

    def test_s1_assemble_argparse_error_is_not_an_import_error(self):
        r = run_isolated("s1_assemble.py")
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == "__main__":
    unittest.main()
