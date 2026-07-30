"""Make the 503 G2 guard checks actually run under the suite (audit finding B-8).

WHAT B-8 GOT RIGHT, AND WHAT IT GOT WRONG
-----------------------------------------
`AUDIT-FINDINGS-20260729-B.md` B-8 is CONFIRMED on the substance: `nd-unfolding/pet/test_g2_*.py`
hold 503 guard checks -- including the C++ truth<->reco leakage guard -- and the suite has never
run one of them, because the baseline command is `pytest nd-unfolding/tests` and they live under
`pet/`. So the 333-passed baseline carried no evidence about any of them.

Its proposed remedy does not work, and its stated risk is wrong. Both verified 2026-07-29:

  * "Adding a `pytest.ini` / `conftest.py` collection path is unbound" -- but pointing pytest
    straight at those two files collects **zero** tests (`no tests ran in 0.03s`). They are
    `main()`-driven scripts: no `test_`-prefixed functions, no `unittest.TestCase`, only
    `if __name__ == "__main__"`. A collection path would have collected the files and found
    nothing, and the finding would have read as closed while nothing ran.
  * "these guards may require ROOT and therefore may not be login-safe off Perlmutter -- confirm
    before wiring them into the default baseline, or the 7-failure baseline becomes a moving
    target". Neither imports ROOT, needs `/pscratch`, or reads the dump. Run as scripts on this
    host both exit 0: 29 domain-classification checks + 474 static dump-contract checks = the
    503 lane D reported, now executed rather than relayed.

So the fix is a wrapper that invokes them as subprocesses and gates on their exit code and their
own reported check counts. A wrapper, not an edit, for a specific reason:
`test_g2_domain_validator.py` is named by a receipt (1 match under
`docs/orchestration/state` / `nd-unfolding/g2_fullevent`), so renaming its functions to suit
pytest's collection rules would void a binding for a cosmetic reason -- the mistake
`nd-unfolding/tests/conftest.py` exists to stop us repeating. Wrapping also keeps them usable
standalone, which is how the C++ guard is invoked on Perlmutter.

THE COUNTS ARE ASSERTED, NOT JUST THE EXIT CODE. A guard script that silently stopped checking
things would still exit 0. Pinning the totals means a check that disappears is a test failure.
Update the constants deliberately when guards are added, and say so in the commit.
"""
import os
import re
import subprocess
import sys
import unittest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ND, "pet")

# Guard script -> (expected check count, the regex that reports it). Counts observed 2026-07-29.
GUARDS = {
    "test_g2_domain_validator.py": (29, r"PASS:\s*(\d+)\s+domain-classification"),
    "test_g2_fullevent_dump_schema.py": (474, r"PASS:\s*(\d+)\s+static full-event-dump"),
}
TOTAL_CHECKS = 503          # B-8's number, now executed on this host rather than relayed


def _run(script):
    return subprocess.run([sys.executable, script], cwd=PET, capture_output=True, text=True,
                          env=dict(os.environ, CUDA_VISIBLE_DEVICES="-1",
                                   TF_CPP_MIN_LOG_LEVEL="3"))


class G2GuardsRun(unittest.TestCase):
    """Each guard script must exist, exit 0, and report its full complement of checks."""

    def test_guards_exist_where_the_finding_says_they_do(self):
        for name in GUARDS:
            self.assertTrue(os.path.exists(os.path.join(PET, name)),
                            f"{name} moved; update this wrapper (and B-8's evidence)")

    def test_guards_are_not_pytest_collectable_on_their_own(self):
        """Pin the REASON this wrapper exists. If someone later converts these to real pytest
        tests, this test fails and the wrapper should be deleted rather than left duplicating
        them -- which is the outcome we want to be told about."""
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--collect-only"]
                           + [os.path.join(PET, n) for n in GUARDS],
                           cwd=ND, capture_output=True, text=True)
        out = (r.stdout + r.stderr).lower()
        self.assertTrue("no tests ran" in out or "no tests collected" in out,
                        f"guards are now pytest-collectable; retire this wrapper:\n{out[-500:]}")

    def test_each_guard_passes_and_reports_its_expected_check_count(self):
        for name, (expected, pattern) in GUARDS.items():
            with self.subTest(guard=name):
                r = _run(os.path.join(PET, name))
                self.assertEqual(r.returncode, 0,
                                 f"{name} failed:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
                m = re.search(pattern, r.stdout)
                self.assertIsNotNone(m, f"{name} did not report a check count:\n{r.stdout[-2000:]}")
                self.assertEqual(int(m.group(1)), expected,
                                 f"{name} ran {m.group(1)} checks, expected {expected}. If guards "
                                 "were added or removed, update GUARDS deliberately.")

    def test_total_matches_the_finding(self):
        self.assertEqual(sum(c for c, _ in GUARDS.values()), TOTAL_CHECKS)

    def test_guards_are_login_safe(self):
        """B-8 warned these might need ROOT and so might make the baseline a moving target. They
        do not. Pin that, because it is the reason wiring them in is safe at all."""
        for name in GUARDS:
            src = open(os.path.join(PET, name)).read()
            self.assertNotIn("import ROOT", src, f"{name} now imports ROOT; revisit B-8")
            self.assertNotIn("/pscratch", src, f"{name} now hardcodes /pscratch; revisit B-8")


class LeakageGuardIsAmongThem(unittest.TestCase):
    """The specific claim that made B-8 a BLOCKER: the truth<->reco leakage guard the campaign
    believes the suite enforces. Confirm it is genuinely inside the wrapped set, so this file
    cannot pass while the guard that motivated it has been removed."""

    def test_leakage_guard_present(self):
        src = open(os.path.join(PET, "test_g2_fullevent_dump_schema.py")).read()
        self.assertRegex(src, r"(?i)leak", "no leakage guard found in the wrapped dump-schema guards")


if __name__ == "__main__":
    unittest.main(verbosity=2)
