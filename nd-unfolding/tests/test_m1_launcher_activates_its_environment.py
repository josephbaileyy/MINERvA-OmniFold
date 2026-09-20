#!/usr/bin/env python3
"""`run_m1_projection.sh` must activate the campaign environment -- and only AFTER its refusals.

MEASURED 2026-09-20, job `58653845`. The launcher exists so that *"the eventual authorization is a
SUBMISSION rather than new code written under time pressure"*. When the authorization arrived it
passed every refusal -- the adoption record was matched by digest -- and then died in 8 s on
`ModuleNotFoundError: No module named 'ROOT'`. It never sourced the environment. Its own header
names ROOT I/O as *"the UNMEASURED leg"*, and that is the leg that failed.

The guard-set control could not have caught it: that control shadows ROOT for the refusal legs on
purpose, and its one positive control sources the environment in the CONTROL script rather than
through this launcher. So the launcher's own activation was never on the path any test took --
this campaign's catalogued shape, one more time.

TWO PROPERTIES, and the second is why this is more than an `assertIn`:
  1. the environment IS activated, through the shared chain rather than a second copy of it;
  2. it is activated **after** the refusals, so a refusal still fires in a degraded environment.
"""
import re
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
LAUNCHER = ND / "run_m1_projection.sh"


class TheLauncherActivatesItsEnvironment(unittest.TestCase):
    def setUp(self):
        self.text = LAUNCHER.read_text(encoding="utf-8")

    def test_it_sources_the_activator(self):
        self.assertRegex(self.text, r'source\s+"\$\{ENV_ROOT\}/setup_salloc_env\.sh"')

    def test_it_uses_the_SHARED_preflight_chain_not_a_second_copy(self):
        for lib in ("lib_mnv_env_preflight.sh", "lib_mnv_env_pathcheck.sh"):
            self.assertIn(lib, self.text, f"{lib} is how every production arm does this")
        self.assertIn("mnv_env_preflight ", self.text)
        self.assertIn("mnv_env_pathcheck ", self.text)

    def test_MNV_ENV_ROOT_is_mandatory_with_no_default(self):
        self.assertRegex(self.text, r'ENV_ROOT="\$\{MNV_ENV_ROOT:\?')
        self.assertNotRegex(self.text, r'ENV_ROOT="\$\{MNV_ENV_ROOT:-')

    def test_it_reports_a_missing_ROOT_as_an_ENVIRONMENT_fault(self):
        """An environment fault reported as a science failure routes to the wrong action."""
        self.assertIn("import ROOT", self.text)
        self.assertIn("ENVIRONMENT fault", self.text)

    def test_the_activation_comes_AFTER_every_refusal(self):
        """The load-bearing one. The guard-set control proved these refusals need no ROOT; if the
        activation moved above them, a degraded environment would silence them instead."""
        act = self.text.index('source "${ENV_ROOT}/setup_salloc_env.sh"')
        refusals = [m.start() for m in re.finditer(r"^# ---- REFUSAL \d", self.text, re.M)]
        self.assertGreaterEqual(len(refusals), 4, "refusal banners missing; this test is blind")
        self.assertTrue(all(r < act for r in refusals),
                        "the environment is activated before a refusal, so that refusal now "
                        "depends on an environment it does not need")

    def test_the_projector_invocation_comes_after_the_activation(self):
        act = self.text.index('source "${ENV_ROOT}/setup_salloc_env.sh"')
        self.assertLess(act, self.text.index("python3 project_cov_nd.py"))

    def test_no_set_u_is_introduced(self):
        """`set -u` plus this activator aborts the shell with 0-byte logs -- twice, on record."""
        for line in self.text.splitlines():
            if line.startswith("set -") and "u" in line.split()[1]:
                self.fail(f"`set -u` reintroduced: {line!r}")


if __name__ == "__main__":
    unittest.main()
