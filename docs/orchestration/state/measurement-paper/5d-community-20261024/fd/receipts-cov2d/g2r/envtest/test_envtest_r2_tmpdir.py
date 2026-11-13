"""Run one unittest module with the open audit's guarded trees = cov2d_blocks.GUARDED plus G2R_GUARD (a local
stand-in for /pscratch). Used by test_envtest_r2_tmpdir.sh only.
    python test_envtest_r2_tmpdir.py <checkout>/2d-unfolding/cov2d/g2r/tests <module>"""
import os
import sys
import unittest
G = os.path.realpath(os.environ["G2R_GUARD"])
T = os.path.realpath(sys.argv[1])
sys.path[:0] = [T, os.path.dirname(os.path.dirname(T))]
import cov2d_blocks as cb  # noqa: E402
guarded = tuple(cb.GUARDED) + (G,)
cb.OpenAudit.__init__.__defaults__ = (guarded,)
print("guarded", cb.OpenAudit().guarded, "TMPDIR", os.environ.get("TMPDIR"), flush=True)
os.chdir(T)
r = unittest.main(module=sys.argv[2], argv=["x"], exit=False).result
sys.exit(0 if r.wasSuccessful() else 1)
