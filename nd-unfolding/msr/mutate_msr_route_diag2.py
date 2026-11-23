#!/usr/bin/env python3
"""Hand mutants of msr_route_diag2.py, each run in its own process against test_msr_route_diag2 (the source on disk is
never modified). Exit 0 only if every mutant is killed.

    python3 nd-unfolding/msr/mutate_msr_route_diag2.py
"""
import concurrent.futures as cf
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE / "msr_route_diag2.py"
M = [
 ("tol boundary", "return x <= RULE_TOL", "return x < RULE_TOL"),
 ("indep branch any", "if all(eig_ok) and not all(ind_ok):", "if all(eig_ok):"),
 ("c-form any->all", "if any(not e and not i for e, i in zip(eig_ok, ind_ok)):", "if all(not e and not i for e, i in zip(eig_ok, ind_ok)):"),
 ("partition ignored", '    if not all(r["ref_partition_equal"] is True for r in two):\n        return "director"', "    pass"),
 ("rows check off", '    if sorted(r["vector_id"] for r in two) != sorted(TARGETS_2D):\n        return "director"', "    pass"),
 ("fisher mu skip off", "        if mu <= 0:\n            continue", "        if False:\n            continue"),
 ("range cut off", "if lam[i] > mp.mpf(repr(float(P.EIG_RTOL))) * lmax]", "if lam[i] > 0]"),
 ("null tol", "> mp.mpf(repr(float(P.NULL_TOL)))]", "> mp.mpf(1)]"),
 ("well cut", "if s[k] <= mp.mpf(repr(float(WELL_CUT)))]", "if s[k] < mp.mpf(0)]"),
 ("z no s", "tot += proj ** 2 / ref[\"s\"][k] ** 2", "tot += proj ** 2"),
 ("no BQ", "    CQ = BQ.T * C * BQ\n", "    CQ = C\n    BQ = mp.eye(m)\n"),
 ("fisher no 1/mu", "F[ca, cb] += a * bb / mu", "F[ca, cb] += a * bb"),
 ("5d ref nan off", 'if dim == "2d" else None', 'if True else None'),
 ("partition none ok off", 'row["ref_partition_equal"] is None or isinstance', 'isinstance'),
 ("missing check off", "    if missing:\n", "    if False:\n"),
]
RUN = r'''
import sys, types, unittest
from pathlib import Path
here, target, old, new = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
src = target.read_text(); assert src.count(old) == 1, "site"
sys.path.insert(0, str(here))
mod = types.ModuleType("msr_route_diag2"); mod.__file__ = str(target); sys.modules["msr_route_diag2"] = mod
exec(compile(src.replace(old, new), str(target), "exec"), mod.__dict__)
import test_msr_route_diag2 as t
r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null","w")).run(unittest.defaultTestLoader.loadTestsFromModule(t))
sys.exit(0 if r.wasSuccessful() else 1)
'''
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
def one(m):
    p = subprocess.run([sys.executable, "-c", RUN, str(HERE), str(T), m[1], m[2]], capture_output=True, text=True, env=env, cwd=str(HERE))
    return m[0], ("SURVIVED" if p.returncode == 0 else "ERROR" if "site" in p.stderr and "AssertionError" in p.stderr else "killed")
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, M))
for n, s in res: print(f"{s:9s} {n}")
bad = sum(s != "killed" for _, s in res)
print(f"mutants {len(res)}; not killed {bad}")
sys.exit(1 if bad else 0)
