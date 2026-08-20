#!/usr/bin/env python3
"""OI-136: run the fail-open probe, and make its inventory a RATCHET rather than a note.

WHY THIS EXISTS, AND WHY IT IS NOT THE 59-FILE FIX. `mnv_guarded_run.py` changed the
DIRECTION of failure for the two launchers wired to it. It did not remove a single
hardcoded `sys.path.insert(0, <cluster root>)`, and nothing stops file number 60 from
joining the set tomorrow. `OI-74`'s surviving residual is stated exactly this way --
"the real residual is a MECHANISM, not an inventory" -- and `OI-64`'s is "an unwired
check is a check nobody runs". The probe was the inventory; this is the mechanism.

IDENTITY, NOT A FLOOR, and the choice is copied from `verify_hash_bindings.py`'s
`RECEIPT_BINDING_SHA256` with its reason: a floor catches collapse but permits erosion.
Either direction requires an explicit, reviewed update here --
  * a NEW hijack site  -> red, which is the regression this exists to catch;
  * a site REPAIRED    -> also red, because a 59-file inventory inside frozen provenance
                          must not shrink silently either. Update the two constants in
                          the same commit as the repair and say which site moved.

THE INVENTORY IS OVER THE WORKING TREE, INCLUDING UNTRACKED FILES, ON PURPOSE. OI-136's
whole lesson is that the path checked and the module imported are two different facts; an
untracked `.py` that inserts the cluster root at position 0 hijacks exactly as well as a
committed one, so restricting this to `git ls-files` would reintroduce the blind spot in
the guard against it.

NON-VACUITY IS ASSERTED, NOT ASSUMED. A ratchet over an empty set passes forever, so the
probe's own positive controls are re-asserted here independently of the probe's exit code.

NO LITERAL CLUSTER ROOT APPEARS IN THIS FILE. The probe counts `.py` files containing that
literal and excludes only itself; a test that spelled the root out would add itself to the
quantity it is guarding. Same reason the probe assembles it from parts.
"""
import hashlib
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROBE = os.path.join("docs", "orchestration", "state",
                     "probe-oi136-sys-path-hijack-20260820.py")

# Measured at fa123ec9 by running the probe; see the module docstring for the update rule.
FAILOPEN_COUNT = 59
FAILOPEN_SHA256 = "605310c881a38671e2dbfc003955715be6ff2ef0db930827c1f6dfcd61c07940"

# The probe's own positive controls, restated here so this file does not inherit its blind
# spots. Relative to the repo root, as the probe prints them.
POSITIVE_CONTROLS = ("./nd-unfolding/adopt_unified_5d.py",
                     "./nd-unfolding/unfold_nd_omnifold_unbinned.py")

GUARD_REL = os.path.join("nd-unfolding", "mnv_guarded_run.py")
GUARDED_LAUNCHERS = (os.path.join("nd-unfolding", "pet",
                                  "sbatch_gate5_data_only_train_array.sh"),
                     os.path.join("nd-unfolding", "pet",
                                  "sbatch_gate5_data_only_target_array.sh"))


def run_probe():
    if sys.version_info < (3, 10):
        raise unittest.SkipTest(
            "the probe's annotations need >= 3.10; run this suite under "
            "/usr/bin/python3.11 or the root_6_28 env")
    return subprocess.run([sys.executable, PROBE], cwd=REPO,
                          capture_output=True, text=True)


def failopen_set(stdout):
    block = stdout.split("FAIL-OPEN SET:", 1)
    if len(block) != 2:
        raise AssertionError("the probe printed no FAIL-OPEN SET block; parse this, never "
                             "treat a missing block as an empty inventory")
    return sorted(l.strip() for l in block[1].strip().splitlines() if l.strip())


class TheProbeStillMeasures(unittest.TestCase):
    def test_it_exits_0_which_means_BOTH_its_controls_held(self):
        """Exit 2 is 'cannot check'. Reading that as a clean tree is the failure mode."""
        p = run_probe()
        self.assertEqual(p.returncode, 0,
                         f"probe did not report a measurement.\nstdout:\n{p.stdout}\n"
                         f"stderr:\n{p.stderr}")
        self.assertIn("positive controls IN the set", p.stdout)
        self.assertIn("negative control -- rejected", p.stdout)

    def test_its_negative_control_still_rejects_something(self):
        """A classifier that rejects nothing has not been shown to discriminate."""
        p = run_probe()
        m = re.search(r"negative control -- rejected (\d+)", p.stdout)
        self.assertIsNotNone(m, p.stdout)
        self.assertGreater(int(m.group(1)), 0)


class TheInventoryIsARatchet(unittest.TestCase):
    def test_the_fail_open_set_is_EXACTLY_the_recorded_one(self):
        p = run_probe()
        rels = failopen_set(p.stdout)
        digest = hashlib.sha256("".join(r + "\n" for r in rels).encode()).hexdigest()
        self.assertEqual(
            (len(rels), digest), (FAILOPEN_COUNT, FAILOPEN_SHA256),
            "The OI-136 fail-open inventory MOVED.\n"
            f"  recorded: {FAILOPEN_COUNT} files / {FAILOPEN_SHA256}\n"
            f"  measured: {len(rels)} files / {digest}\n"
            "A NEW site is a regression: an absolute insert(0, <cluster root>) executes that "
            "tree's modules whichever checkout launched the entrypoint, PYTHONPATH cannot "
            "outrank position 0, and a re-deploy does not fix it. A REPAIRED site is welcome "
            "and still red: update both constants above in the same commit, naming the site.\n"
            f"  measured set:\n    " + "\n    ".join(rels))

    def test_this_ratchet_cannot_pass_over_an_empty_set(self):
        """Non-vacuity, asserted here rather than inherited from the probe's exit code."""
        p = run_probe()
        rels = failopen_set(p.stdout)
        self.assertGreater(len(rels), 0)
        for c in POSITIVE_CONTROLS:
            self.assertIn(c, rels,
                          f"{c} is a known hijacker by inspection; if it is missing the "
                          f"classifier under-counts and the smaller number is not the answer")


class TheMitigationIsStillDeployed(unittest.TestCase):
    """A guard that exists and is not invoked is the OI-64 shape, not a mitigation."""

    def test_the_guard_file_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(REPO, GUARD_REL)), GUARD_REL)

    def test_both_data_only_launchers_still_invoke_it_with_the_mandatory_split(self):
        for rel in GUARDED_LAUNCHERS:
            with self.subTest(launcher=rel):
                with open(os.path.join(REPO, rel)) as fh:
                    text = fh.read()
                self.assertIn("mnv_guarded_run.py", text)
                self.assertRegex(
                    text, r'"\$GUARD"\s+--expect-root\s+"\$CODE_ROOT"\s+--',
                    "the `--` split is mandatory; without it a child flag can be eaten "
                    "by the wrapper")

    def test_the_guard_is_itself_parity_checked_by_those_launchers(self):
        """A guard imported from the tree it polices is theatre; the launchers say so."""
        for rel in GUARDED_LAUNCHERS:
            with self.subTest(launcher=rel):
                with open(os.path.join(REPO, rel)) as fh:
                    text = fh.read()
                self.assertIn('--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"', text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
