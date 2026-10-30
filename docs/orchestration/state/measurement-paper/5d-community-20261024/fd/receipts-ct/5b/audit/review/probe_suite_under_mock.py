"""Run the whole test_fd_ct_5b_audit suite with one mutation applied by mock (the source file is not edited).
argv: <worktree> <mutant>; mutants: guard_empty | no_floor_check | no_sigmaM_check | ref_bound_wrong | no_a4"""
import sys, unittest
from pathlib import Path
from unittest import mock
W = Path(sys.argv[1]); sys.path.insert(0, str(W / "nd-unfolding")); sys.path.insert(0, str(W / "nd-unfolding/tests"))
import numpy as np
import test_fd_ct_5b_audit as T
au, cp = T.au, T.cp
which = sys.argv[2]
patches = []
if which == "guard_empty":
    g = cp.guarded
    patches.append(mock.patch.object(cp, "guarded", lambda f, i: g(f, [])))
elif which in ("no_floor_check", "no_sigmaM_check"):
    real = au.f0.report
    key = "the noise floor rebuilt" if which == "no_floor_check" else "sigma_M equals"
    patches.append(mock.patch.object(au.f0, "report", lambda c, n, ok, *a, **k: real(c, n, True if key in n else ok, *a, **k)))
elif which == "ref_bound_wrong":
    real4 = au.item4
    def bad(*a, **k):
        o = real4(*a, **k)
        for X in o["reference_bound"]:
            o["reference_bound"][X]["value"] *= 7.0
            o["reference_bound"][X]["first_order_bound"] = -1.0
        o["whitened_eigenvalues"] = [0.0, 0.0]
        o["largest_chi2_fall_fraction"] = 0.99
        return o
    patches.append(mock.patch.object(au, "item4", bad))
elif which == "no_a4":
    patches.append(mock.patch.object(au, "basis", lambda C: np.linalg.qr(np.random.default_rng(0).normal(size=(16, 2)))[0]))
for p in patches:
    p.start()
suite = unittest.defaultTestLoader.loadTestsFromModule(T)
r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
print(f"{which}: ran {r.testsRun}, failures {len(r.failures)}, errors {len(r.errors)}, skipped {len(r.skipped)} ->",
      "KILLED" if not r.wasSuccessful() else "SURVIVED")
