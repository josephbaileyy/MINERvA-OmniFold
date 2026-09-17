import numpy as np
th = 7.11e-2                      # theta_A as recommended
print("=== 0. theta_A reproduces from the launcher N's ===")
for N,lab in ((100,'C_stat'),(24,'C_ML')):
    v = np.sqrt(2.0/(N-1)); print(f"  {lab:7s} N={N:3d}  on variance {v:.6f}  on sigma {v/2:.6f}")
print()

print("=== 1. is  dsigma/sigma = f * u  EXACT for finite u?  (sigma^2 = f-share scaled) ===")
def exact_dsig(f,u): return np.sqrt(1.0 + f*((1.0+u)**2 - 1.0)) - 1.0
for u in (1e-6, 1e-3, 1e-2, 7.11e-2, 0.3556):
    f = 0.2
    e, lin = exact_dsig(f,u), f*u
    print(f"  f=0.2  u={u:<9.4g}  exact {e:.8e}   linear f*u {lin:.8e}   rel gap {abs(lin/e-1):.3e}")
print("  -> at 1e-6 the two agree to 4e-7; at the theta scale the linear form is 12% off.")
print()

print("=== 2. INVERSION: what |u| does a per-bin sigma tolerance theta actually permit? ===")
def u_exact(f,th): return np.sqrt(1.0 + ((1.0+th)**2 - 1.0)/f) - 1.0
print(f"  {'f':>6} {'linear th/f':>12} {'EXACT u_max':>12} {'linear/exact':>13}")
for f in (1.0,0.5,0.2,0.1,0.01):
    print(f"  {f:6.2f} {th/f:12.6f} {u_exact(f,th):12.6f} {(th/f)/u_exact(f,th):13.4f}")
print("  -> the linear inversion PERMITS MORE than the exact relation allows: as a GATE it is unsafe;")
print("     as an input to a worst-case DeltaC bound it is conservative.")
print()

print("=== 3. the DeltaC bound, two compositions ===")
print(f"  {'min f':>6} {'linear (1+th/f)^2-1':>21} {'EXACT ((1+th)^2-1)/f':>22}")
for f in (1.0,0.5,0.2,0.1,0.01):
    lin = (1.0+th/f)**2 - 1.0
    ex  = ((1.0+th)**2 - 1.0)/f
    print(f"  {f:6.2f} {100*lin:20.1f}% {100*ex:21.1f}%")
# where does each cross 100%?
f_lin = th/(np.sqrt(2.0)-1.0)
f_ex  = ((1.0+th)**2 - 1.0)
print(f"  crosses 100% at  min f = {f_lin:.6f} (linear)   vs {f_ex:.6f} (exact)")
print("  -> the published table is the LINEAR one; the exact composition is tighter and moves the")
print("     'settles nothing' threshold DOWN from ~0.172 to ~0.147.")
print()

print("=== 4. the inversion is ONE-SIDED: downward g movement ===")
lo = 1.0 - (1.0-th)**2
print(f"  a two-sided sigma tolerance constrains DOWNWARD g movement only while f > 1-(1-th)^2 = {lo:.6f}")
for f in (0.20,0.1365,0.10,0.01):
    lim = 1.0 - (1.0-th)**2
    if f > lim:
        u = 1.0 - np.sqrt(1.0 - lim/f); print(f"  f={f:6.4f}  max downward |u| = {u:.6f}")
    else:
        print(f"  f={f:6.4f}  max downward |u| = UNBOUNDED (g may go to 0 with sigma_i moving < theta)")
print()

print("=== 5. the deadband partition reproduces from the relayed counts ===")
print(f"  n_gt_one 6528 + n_saturated 4166 = {6528+4166}  (n_support 10694)")
print(f"  deadband share = {4166/10694:.4%}   <- bins with g_i == 1, where du/u == 0 for non-crossing moves")
print()

print("=== 6. does 'the same factor bounds every projection' hold? ===")
g = 0.30
for name, C, w in (
    ("entrywise-NONNEG C, w>=0", np.array([[1.0,0.8],[0.8,1.0]]), np.array([1.0,1.0])),
    ("NEAR-ANNIHILATING w",      np.array([[1.0,-1.0],[-1.0,1.0]]), np.array([1.0,1.0])),
    ("near-annihilating, eps",   np.array([[1.0,-0.999],[-0.999,1.0]]), np.array([1.0,1.0])),
):
    D = np.diag([1.0+g, 1.0-g])
    num = float(w @ (D@C@D - C) @ w); den = float(w @ C @ w)
    lim = (1.0+g)**2 - 1.0
    r = abs(num)/den if den > 0 else float('inf')
    print(f"  {name:26s} |dPCP|/|PCP| = {r:>10.4g}   limit {lim:.4f}   holds={r <= lim + 1e-12}")
print("  -> the failure at a near-annihilating projection is UNBOUNDED, not a gradual degradation.")
print("     PSD is preserved in all three C's:", [bool(np.all(np.linalg.eigvalsh(C) >= -1e-12)) for C in
      (np.array([[1.0,0.8],[0.8,1.0]]), np.array([[1.0,-1.0],[-1.0,1.0]]), np.array([[1.0,-0.999],[-0.999,1.0]]))])
