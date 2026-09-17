import numpy as np
rng = np.random.default_rng(20260918)
def corr(C):
    d = np.sqrt(np.diag(C)); return C / np.outer(d, d)

print("=== TEST 1: is corr(M C M') invariant under SOURCE-basis rescaling C -> D C D? ===")
print("    (the packet's 4.1 test is stated over C -> D C D; its PROOF is about corr(C), not corr(M C M'))")
n, m = 40, 6
worstC, worstP = 0.0, 0.0
for t in range(400):
    A = rng.standard_normal((n, n+12)); C = A @ A.T                      # PSD source covariance
    M = np.zeros((m, n))                                                  # non-negative aggregation map
    who = rng.integers(0, m, size=n)
    for j in range(n): M[who[j], j] = rng.random() + 0.1
    D = np.diag(np.exp(rng.normal(0, 0.7, size=n)))                       # positive diagonal rescale
    Cd = D @ C @ D
    # unprojected correlation: invariant?
    worstC = max(worstC, np.abs(corr(Cd) - corr(C)).max())
    # projected correlation: invariant?
    Rp, Rpd = corr(M @ C @ M.T), corr(M @ Cd @ M.T)
    worstP = max(worstP, np.abs(Rpd - Rp).max())
print("    worst |corr(DCD) - corr(C)|              = %.3e   <- invariant, as the packet proves" % worstC)
print("    worst |corr(M DCD M') - corr(M C M')|    = %.3e   <- NOT invariant" % worstP)
print()
print("=== TEST 2: can a PURE DIAGONAL change move the proposed statistic? ===")
A = rng.standard_normal((n, n+12)); C0 = A @ A.T
M = np.zeros((m, n)); who = rng.integers(0, m, size=n)
for j in range(n): M[who[j], j] = rng.random() + 0.1
for s in (0.05, 0.2, 0.7):
    D = np.diag(np.exp(rng.normal(0, s, size=n)))
    Ck = D @ C0 @ D                        # member k differs from k=0 by a PURE diagonal rescale
    dR = np.abs(corr(M @ Ck @ M.T) - corr(M @ C0 @ M.T)).max()
    print("    rescale sd=%.2f :  ||R_p^(k) - R_p^(0)||_max = %.4f   (source correlations IDENTICAL)" % (s, dR))
print("    -> a member differing ONLY in its diagonal produces a non-zero, and large, statistic.")
print("       So the statistic is NOT blind to the diagonal in the source basis.")
print()
print("=== TEST 3: what IS corr(M C M') invariant under? ===")
E = np.diag(np.exp(rng.normal(0, 0.7, size=m)))     # rescale in the PROJECTED basis
R1 = corr(M @ C0 @ M.T); R2 = corr(E @ (M @ C0 @ M.T) @ E)
print("    worst |corr(E (MCM') E) - corr(MCM')|   = %.3e   <- invariant (trivially: it IS a corr matrix)" % np.abs(R2-R1).max())
print()
print("=== TEST 4: do a trace ratio and a per-bin sigma ratio fail the source-basis test? ===")
D = np.diag(np.exp(rng.normal(0, 0.5, size=n))); Cd = D @ C0 @ D
print("    Tr(DCD)/Tr(C) = %.4f            -> trace ratio FAILS invariance (packet correct)" % (np.trace(Cd)/np.trace(C0)))
s0, sd = np.sqrt(np.diag(C0)), np.sqrt(np.diag(Cd))
print("    max_i |sd_i-s0_i|/s0_i = %.4f   -> per-bin sigma ratio FAILS invariance (packet correct)" % np.abs((sd-s0)/s0).max())
