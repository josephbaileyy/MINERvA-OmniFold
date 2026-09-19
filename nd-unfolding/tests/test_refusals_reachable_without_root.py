#!/usr/bin/env python3
"""Every refusal in `project_cov_nd.py` must be reachable WITHOUT the production environment.

WHY. `import ROOT` sat at the top of `main()`, before argparse. An independent assessor ran the
eight guard cases and got rc=1 on ALL EIGHT -- including the positive control, which should have
succeeded. That reads exactly like "all seven guards fire" and was nothing of the kind: every case
died at `import ROOT`. Its second attempt segfaulted on all eight. **Uniform failure was
indistinguishable from uniform success, twice, and only the positive control separated them.**

A refusal a reviewer cannot exercise without the full stack is a refusal nobody will exercise --
and the reviewer is exactly the person who will try them on a bare interpreter.

⚠ THE FIXTURE MANUFACTURES THE CONDITION rather than relying on it. This Mac has no ROOT, so the
test would pass here for the wrong reason and rot silently on the cluster, where ROOT imports
fine. So it shadows `ROOT` with a module that raises on import and puts it FIRST on PYTHONPATH.
The condition is then a property of the test, not of the machine.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
PROJ = ND / "project_cov_nd.py"


class RefusalsReachableWithoutRoot(unittest.TestCase):
    def setUp(self):
        self.shim = Path(tempfile.mkdtemp())
        (self.shim / "ROOT.py").write_text(
            'raise ImportError("ROOT deliberately unavailable: this fixture manufactures the '
            'bare-interpreter condition a reviewer exercises refusals in")\n', encoding="utf-8")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.shim, ignore_errors=True))
        self.env = {**os.environ, "PYTHONPATH": str(self.shim)}

    def _run(self, *args):
        return subprocess.run([sys.executable, str(PROJ), *args],
                              env=self.env, capture_output=True, text=True)

    def test_the_shim_actually_blocks_ROOT(self):
        """Power control. Without this the tests below could pass because ROOT imports fine."""
        r = subprocess.run([sys.executable, "-c", "import ROOT"], env=self.env,
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("deliberately unavailable", r.stderr)

    def test_help_does_not_require_the_production_environment(self):
        r = self._run("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--expect-variant", r.stdout)

    def test_a_MISSING_REQUIRED_ARG_reports_argparse_not_ImportError(self):
        r = self._run("--src-cov", "/tmp/x.npz")
        self.assertIn("required", (r.stderr + r.stdout).lower())
        self.assertNotIn("No module named", r.stderr)

    def test_a_GUARD_refusal_is_reachable_and_says_what_it_refused(self):
        r = self._run("--src-cov", "/tmp/x.npz", "--src-hist", "h", "--src-cv", "/tmp/x.npz",
                      "--src-axes", "pt,pz,eavail,q3,W", "--keep-axes", "eavail,W",
                      "--out", "/tmp/o.root", "--run-class", "diagnostic",
                      "--expect-variant", "cv")
        self.assertIn("[FAIL] --run-class diagnostic requires --acceptance-question", r.stderr)
        self.assertNotIn("No module named", r.stderr)

    def test_the_failure_modes_are_DISTINGUISHABLE_from_each_other(self):
        """The assessor's actual problem was not that things failed -- it was that eight different
        cases failed identically, so the suite could not tell a firing guard from a dead import."""
        outs = {
            "help": self._run("--help"),
            "argparse": self._run("--src-cov", "/tmp/x.npz"),
            "guard": self._run("--src-cov", "/tmp/x.npz", "--src-hist", "h",
                               "--src-cv", "/tmp/x.npz", "--src-axes", "pt,pz,eavail,q3,W",
                               "--keep-axes", "eavail,W", "--out", "/tmp/o.root",
                               "--run-class", "diagnostic", "--expect-variant", "cv"),
        }
        codes = {k: v.returncode for k, v in outs.items()}
        self.assertEqual(len(set(codes.values())), len(codes),
                         f"failure modes are not distinguishable by exit code: {codes}")


if __name__ == "__main__":
    unittest.main()
