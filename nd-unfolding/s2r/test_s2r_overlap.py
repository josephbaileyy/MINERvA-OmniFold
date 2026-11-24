"""Tests of s2r_overlap.py: CLEAR on the bound set; a write under IBUB's root, a read of IBUB's staging, a write on a
cov2d path, and an acked read on a non-cov2d entry each STOP. Run: python3 -B -m unittest nd-unfolding/s2r/test_s2r_overlap.py"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s2r_overlap as O  # noqa: E402


class Overlap(unittest.TestCase):
    def setUp(self):
        self.saved = O.ours

    def tearDown(self):
        O.ours = self.saved

    def with_extra(self, *extra):
        base = self.saved
        O.ours = lambda clone: base(clone) + list(extra)
        return O.check(O.REPO)

    def test_the_bound_set_is_clear(self):
        rc, lines = O.check(O.REPO)
        self.assertEqual(rc, 0, "\n".join(lines))
        self.assertIn("hits 0", lines[-1])
        self.assertEqual(sum(1 for x in lines if x.startswith("OVERLAP ALLOWED") and "cov2d-acked" in x), 3)

    def test_each_kind_of_hit_stops(self):
        cases = [("write", "/pscratch/sd/j/josephrb/ibub-20261124/x"),
                 ("read", "/pscratch/sd/j/josephrb/ibub-20261124/stage/runEventLoopMC_MEFHC.root"),
                 ("write", "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"),
                 ("read (cov2d-acked)", "/pscratch/sd/j/josephrb/ibub-20261124"),
                 ("write", "/dev/shm/ibub-connect/y"),
                 ("write", "/pscratch/sd/j/josephrb/msr-p-20261122/z"),
                 ("write", "/dev/shm/ibubc.123.sh"),
                 ("write", "/dev/shm/ibubc.")]
        for c in cases:
            rc, lines = self.with_extra(c)
            self.assertEqual(rc, 3, c)
            self.assertTrue(any(x.startswith("OVERLAP HIT") for x in lines), c)


if __name__ == "__main__":
    unittest.main()
