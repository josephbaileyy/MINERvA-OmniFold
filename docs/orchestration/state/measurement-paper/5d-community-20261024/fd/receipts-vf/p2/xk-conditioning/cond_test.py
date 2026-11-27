# The director's conditioning test (2026-11-26): K's OLD replay with seeded relative noise on (A) the cross-covariances
# as they leave fd_xcov.cross_cov, or (B) the own blocks as they enter fd_xcov.bound_matrix; the producer's functions
# otherwise unchanged. Records condition numbers of the bounded blocks and of V_d at r = 1.
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/Users/josephbailey/s2r-wt/nd-unfolding")
import fd_vf_p2 as V
import fd_gencmp as GC, fd_xcov_steps as XS, fd_xcov as X
variant, seed, eps, work = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
rng = np.random.default_rng(seed)
conds = {"bound_S16": [], "bound_S2": [], "Vd_r1": []}
orig_cc, orig_bm, orig_ra = X.cross_cov, X.bound_matrix, X.route_a
def noisy(A):
    A = np.asarray(A, float)
    return A * (1 + eps * rng.standard_normal(A.shape))
def sym_noisy(A):
    A = np.asarray(A, float); N = rng.standard_normal(A.shape); N = (N + N.T) / 2
    return A * (1 + eps * N)
def cc(*a, **k):
    out = orig_cc(*a, **k)
    return noisy(out) if variant == "A" else out
def bm(S16, S2):
    for key, S in (("bound_S16", S16), ("bound_S2", S2)):
        ev = np.linalg.eigvalsh(np.asarray(S, float)); pos = ev[ev > 0]
        conds[key].append(float(pos.max() / pos.min()) if pos.size else float("inf"))
    if variant == "B":
        S16, S2 = sym_noisy(S16), sym_noisy(S2)
    return orig_bm(S16, S2)
def ra(d, C16q, C2q, K_rest, M, *a, **k):
    Vd1 = X.Vd_of(C16q, C2q, K_rest + M)
    conds["Vd_r1"].append(float(np.linalg.cond(Vd1)))
    return orig_ra(d, C16q, C2q, K_rest, M, *a, **k)
X.cross_cov, X.bound_matrix, X.route_a = cc, bm, ra
fetch = Path("/Users/josephbailey/vf-p2-fetch-20261126")
V.xk_run_dir(fetch, work)
rc = V.xk_replay(XS, GC, fetch, work, {}, [], [])
summ = {k: (min(v), max(v)) if v else None for k, v in conds.items()}
json.dump({"rc": rc, "variant": variant, "seed": seed, "eps": eps, "conds": summ}, open(work / "cond.json", "w"))
print("rc", rc, variant, seed, eps, summ)
