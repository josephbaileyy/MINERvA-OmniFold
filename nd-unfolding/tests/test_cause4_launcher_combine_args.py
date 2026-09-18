#!/usr/bin/env python3
"""The C4 launcher must pass every argument the combine path REQUIRES.

58531919 failed after 593 s with `[FAIL] --expected-throws LO-HI is required for combine`. The
check lives at `unified_throw_cov.py:902`, which runs only AFTER the LightGBM fits and after all
40 throw slabs are loaded and validated -- so a missing argument costs ten minutes of compute to
report. Joseph ruled the check stays where it is: moving it above the fits would save future
burns and is not on the required path.

⚠ SCOPE IS DELIBERATE. Ten other launchers in `nd-unfolding/` invoke `--combine` without
`--expected-throws`. They are NOT covered here and NOT repaired: that is the gated
post-publication cleanup. A test written over all of them would fail on work nobody has
authorized, which is how a guard becomes something people disable.
"""
import re
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
LAUNCHER = ND / "run_cause4_jitter_print.sh"
PRODUCTION = ND / "sbatch_uthrow_combine_5d.sh"


def _combine_invocation(path):
    """The invocation with line continuations joined, so a flag on any line is visible."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\\\n\s*", " ", text)
    return [ln for ln in text.splitlines()
            if "--combine" in ln and not ln.lstrip().startswith("#")]


class Cause4LauncherCombineArgs(unittest.TestCase):
    def test_the_launcher_has_exactly_one_combine_invocation(self):
        """If this ever finds two, the assertions below stop covering the whole launcher."""
        self.assertEqual(len(_combine_invocation(LAUNCHER)), 1)

    def test_it_passes_expected_throws(self):
        self.assertIn("--expected-throws", _combine_invocation(LAUNCHER)[0])

    def test_the_value_is_the_PRODUCTION_one_and_not_a_fresh_choice(self):
        """A relaunch must not quietly redefine the throw inventory it claims."""
        got = re.search(r"--expected-throws\s+(\S+)", _combine_invocation(LAUNCHER)[0]).group(1)
        want = re.search(r"--expected-throws\s+(\S+)",
                         _combine_invocation(PRODUCTION)[0]).group(1)
        self.assertEqual(got, want)

    def test_that_value_is_the_N_that_sets_C2s_sampling_floor(self):
        """Corroboration, not decoration: C2's floor is sqrt_tr/sqrt(N) with N = 160 read from the
        precursor product, and the production combine independently declares ids 0-159. Two
        records of one fact that are required to agree."""
        got = re.search(r"--expected-throws\s+(\d+)-(\d+)",
                        _combine_invocation(LAUNCHER)[0])
        lo, hi = int(got.group(1)), int(got.group(2))
        self.assertEqual(hi - lo + 1, 160)


if __name__ == "__main__":
    unittest.main()
