#!/usr/bin/env python3
"""Amendment E's fixture against the PRE-amendment formation: runs test_msr.AmendmentE's reference tests with msr_project
at ffb88e7b (merged at 88994c9a; C = J F+ J^T formed in float64). The only shim is a `decompose` that accepts and ignores
`A`, and the new `fisher_root` (which those tests use only to build A). Exit 0 only if every fixture test FAILS there.

    python3 nd-unfolding/msr/old_formation_check.py
"""
import hashlib
import subprocess
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_COMMIT, OLD_SHA = "88994c9a", "ffb88e7b32d8cf1f5df03be96e9506b82c00f81f4f12123d6de0c134d7af994e"
TESTS = ("test_both_routes_meet_the_50_digit_reference_on_the_ill_conditioned_fixture",
         "test_the_eigen_route_widths_meet_the_reference")


def main() -> int:
    src = subprocess.run(["git", "show", f"{OLD_COMMIT}:nd-unfolding/msr/msr_project.py"], cwd=HERE, check=True,
                         capture_output=True).stdout
    assert hashlib.sha256(src).hexdigest() == OLD_SHA, "not the pre-amendment msr_project.py"
    sys.path.insert(0, str(HERE))
    import msr_project as new   # the amended module, for fisher_root only
    fisher_root = new.fisher_root
    old = types.ModuleType("msr_project")
    old.__file__ = str(HERE / "msr_project.py")
    exec(compile(src.decode(), old.__file__, "exec"), old.__dict__)
    real = old.decompose
    old.decompose = lambda F, J, driver="numpy", cut=old.CUT, A=None: real(F, J, driver, cut)
    old.fisher_root = fisher_root
    sys.modules["msr_project"] = old
    for k in [k for k in sys.modules if k in ("test_msr", "msr_route_diag2")]:
        del sys.modules[k]
    import test_msr
    assert test_msr.P is old
    bad = 0
    for t in TESTS:
        suite = unittest.defaultTestLoader.loadTestsFromName(f"AmendmentE.{t}", test_msr)   # runs setUpClass
        r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
        failed = bool(r.failures) and not r.errors     # an assertion against the reference, never a crash
        last = (r.failures or r.errors)[0][1].strip().splitlines() if (r.failures or r.errors) else [""]
        why = next((ln for ln in reversed(last) if ln.startswith("AssertionError")), last[-1])
        print(f"{'FAILS (as required)' if failed else 'DOES NOT FAIL BY ASSERTION'}  {t}  {why[:220]}")
        bad += not failed
    # and the defect itself, per seed: BOTH old routes miss the reference by more than 1e-8 (toy vectors, no reading)
    import numpy as np
    import did
    import mpmath as mp
    import msr_route_diag2 as D
    mp.mp.dps = 50
    for seed in test_msr.ILL_SEEDS:
        R, t0, b, J = test_msr.ill_conditioned(seed)
        ref = D.mp_decompose(D.mp_fisher(R, t0, b), J)
        d = real(did.fisher(R, t0, b), J, "numpy")
        worst_e = worst_i = 0.0
        for k in range(4):
            beta = np.random.default_rng(100 + k).normal(size=J.shape[0])
            z_ref = D.mp_z(ref, beta)
            e, i = D.rel(old.z_well(d, beta), z_ref), D.rel(old.route_independent(d, beta)[1], z_ref)
            worst_e = max(worst_e, e) if e == e else float("inf")
            worst_i = max(worst_i, i) if i == i else float("inf")
        both = worst_e > 1e-8 and worst_i > 1e-8
        print(f"seed {seed}: old eigen route worst rel {worst_e:.2e}, old independent route worst rel {worst_i:.2e}: "
              f"{'both miss (defect reproduced)' if both else 'NOT both'}")
        bad += not both
    print(f"old formation at {OLD_COMMIT} (msr_project {OLD_SHA[:8]}): {len(TESTS) - min(bad, len(TESTS))}/{len(TESTS)} "
          f"fixture tests fail; not reproduced: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
