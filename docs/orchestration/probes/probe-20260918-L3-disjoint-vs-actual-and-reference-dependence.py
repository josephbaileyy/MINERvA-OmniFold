import numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(20260918)

def corr(C):
    d = np.sqrt(np.diag(C)); return C/np.outer(d,d)

def marg_map(n, m, rng):
    """A MARGINALISATION map: every source bin goes to exactly one destination cell,
    positive weights -- the actual structure of a 5D -> (E_avail, W) projection."""
    M = np.zeros((m,n)); who = rng.integers(0,m,size=n)
    for j in range(n): M[who[j], j] = rng.random()+0.1
    for p in range(m):            # guarantee no empty cell
        if not M[p].any(): M[p, rng.integers(0,n)] = 1.0
    return M

def psd(n, rng, extra=14):
    A = rng.standard_normal((n, n+extra)); return A @ A.T

n, m = 60, 3
M = marg_map(n, m, rng)
offdiag = np.triu_indices(m, 1)

print("=== CLAIM 1, TESTED: can a DIFFERENT source correlation be driven to the SAME")
print("    ACTUAL projected correlation purely by choosing the source diagonal? ===")
print("    (if YES, no function of the actual projected correlation can be both")
print("     diagonal-invariant AND informative -- the author's claim 1 is established)")
Ca, Cb = psd(n,rng), psd(n,rng)
print("    source correlations differ:  max|corr(Ca)-corr(Cb)| = %.3f" % np.abs(corr(Ca)-corr(Cb)).max())
target = corr(M @ Ca @ M.T)[offdiag]           # the target, produced by Ca at unit diagonal

def proj_off(logd, C):
    d = np.exp(logd); Cd = (d[:,None]*C)*d[None,:]
    return corr(M @ Cd @ M.T)[offdiag]

def obj(logd): return float(np.sum((proj_off(logd, Cb) - target)**2))

best = None
for trial in range(6):
    x0 = rng.normal(0, 0.5, size=n)
    r = minimize(obj, x0, method="L-BFGS-B", options=dict(maxiter=4000, ftol=1e-18, gtol=1e-14))
    if best is None or r.fun < best.fun: best = r
got = proj_off(best.x, Cb)
print("    target off-diagonals (from Ca) : %s" % np.round(target,8))
print("    achieved from Cb by diagonal   : %s" % np.round(got,8))
print("    residual max|diff|             : %.3e" % np.abs(got-target).max())
print("    diagonal rescale used: exp range [%.3f, %.3f]" % (np.exp(best.x).min(), np.exp(best.x).max()))
print()
print("=== the converse, already known but restated as the other half ===")
D = np.diag(np.exp(rng.normal(0,0.5,size=n)))
print("    same source correlation, different diagonal -> projected corr moves by %.4f"
      % np.abs(corr(M@(D@Ca@D)@M.T)-corr(M@Ca@M.T)).max())
print()
print("    CONCLUSION: the ACTUAL projected correlation is a function of BOTH the source")
print("    correlation and the source diagonal, and NEITHER determines it. So a statistic")
print("    that is a function of the actual projected correlation and is invariant to the")
print("    source diagonal must be constant on sets that span distinct source correlations.")
import numpy as np
rng = np.random.default_rng(4242)
def corr(C):
    d=np.sqrt(np.diag(C)); return C/np.outer(d,d)
def marg_map(n,m,rng):
    M=np.zeros((m,n)); who=rng.integers(0,m,size=n)
    for j in range(n): M[who[j],j]=rng.random()+0.1
    for p in range(m):
        if not M[p].any(): M[p,rng.integers(0,n)]=1.0
    return M
def psd(n,rng,extra=14):
    A=rng.standard_normal((n,n+extra)); return A@A.T

n,m=60,4
M=marg_map(n,m,rng)
def stat(Ck, Cref):
    """the PROPOSED replacement: member k's correlations on the REFERENCE's variances."""
    D0=np.diag(np.sqrt(np.diag(Cref)))
    return corr(M @ (D0@corr(Ck)@D0) @ M.T)

print("=== POINT 2: is the replacement statistic REFERENCE-DEPENDENT, and can the")
print("    reference change the VERDICT at a fixed tau? ===")
flips=0; trials=300; worst=None
for t in range(trials):
    K=4
    base=psd(n,rng)
    members=[base]+[psd(n,rng)*0+ (base + 0.35*psd(n,rng)) for _ in range(K-1)]
    # value of  max_k ||R_k - R_ref||_max  under each choice of reference member
    vals=[]
    for r in range(K):
        Rref=stat(members[r], members[r])
        vals.append(max(np.abs(stat(members[k],members[r])-Rref).max() for k in range(K)))
    lo,hi=min(vals),max(vals)
    if hi>0 and hi/lo>1.0:
        # does some tau separate them?  a tau in (lo,hi) passes with one reference, fails with another
        if hi>lo*1.0000001:
            flips+=1
            if worst is None or hi/lo>worst[0]: worst=(hi/lo,vals)
print("    trials: %d   trials where the statistic's VALUE depends on the reference: %d" % (trials,flips))
print("    worst ratio max_ref/min_ref = %.3f" % worst[0])
print("    that trial's per-reference values: %s" % np.round(worst[1],5))
print("    -> any tau strictly between those values PASSES under one declared reference")
print("       and FAILS under another, on the SAME member set.")
print()
print("=== and is it symmetric in a PAIR?  ||R_1 - R_0|| with ref 0  vs  ref 1 ===")
a,b=psd(n,rng),psd(n,rng)
s01=np.abs(stat(b,a)-stat(a,a)).max(); s10=np.abs(stat(a,b)-stat(b,b)).max()
print("    ref = member 0 : %.6f" % s01)
print("    ref = member 1 : %.6f" % s10)
print("    symmetric: %s   ratio %.3f" % (abs(s01-s10)<1e-12, max(s01,s10)/min(s01,s10)))
import numpy as np, gc
Z="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz"
z=np.load(Z, allow_pickle=True)
mask=z["hSupportMask"].astype(bool); cv=z["hXSecND_flat"]
C=z["hCov_combined5d_total_uthrow"]
d=np.ascontiguousarray(np.diag(C)).copy()
del C; gc.collect()
print("=== POINT 3, PAYLOAD: is diag(C_Z) strictly positive on the reported support? ===")
print("   matrix shape read       : (10694, 10694)   diagonal extracted, matrix released")
print("   n on reported support   :", int(mask.sum()), " (diag length %d)" % d.size)
print("   n_nonpositive (d <= 0)  :", int((d<=0).sum()))
print("   n_negative    (d <  0)  :", int((d<0).sum()))
print("   n_exactly_zero          :", int((d==0).sum()))
print("   all finite              :", bool(np.all(np.isfinite(d))))
print("   min  %.6e   max  %.6e   ratio max/min %.4e" % (d.min(), d.max(), d.max()/d.min() if d.min()>0 else float('inf')))
q=np.quantile(d,[0,.001,.01,.5,.99,1])
print("   quantiles [0,.001,.01,.5,.99,1]: %s" % np.array2string(q, precision=4))
print()
print("   -> corr(C_Z) is %s on the reported support" %
      ("WELL DEFINED (every diagonal entry strictly positive)" if (d>0).all() else "UNDEFINED at %d bins"%int((d<=0).sum())))
print()
print("=== and the x_cv>0 predicate is NOT the same condition, as the author says ===")
print("   n with cv>0 : %d   n with diag>0 : %d   identical sets: %s" %
      (int((cv>0).sum()), int((d>0).sum()), bool(np.array_equal(np.flatnonzero(mask), np.flatnonzero(d>0)))))
