import numpy as np
rng = np.random.default_rng(20260918)

print("=== (a) N-scaling: my claim was 1/N; the formula is 1/sqrt(N-1) ===")
th = lambda N: 0.5*np.sqrt(2.0/(N-1))
print(f"  N=100 -> {th(100):.6f}   N=200 -> {th(200):.6f}   ratio {th(200)/th(100):.4f}")
print(f"  sqrt(99/199) = {np.sqrt(99/199):.4f}   <- agrees, so 'doubling halves theta' is WRONG")
Nhalf = 1 + 4*99
print(f"  halving needs N-1 = 4*99 -> N = {Nhalf}  (theta {th(Nhalf):.6f} = {th(Nhalf)/th(100):.4f} x)")
print()

print("=== (b1) corr of per-bin VARIANCE estimation errors, from first principles ===")
print("  Gaussian theory: Cov(s_i^2,s_j^2) = 2 sig_i^2 sig_j^2 rho_ij^2/(N-1)  =>  corr = rho_ij^2")
for rho in (0.9, 0.5, 0.1):
    N = 100; T = 40000
    L = np.linalg.cholesky(np.array([[1.0,rho],[rho,1.0]]))
    # T independent realisations of an N-member ensemble; per-realisation per-bin sample variance
    z = rng.standard_normal((T, N, 2)) @ L.T
    s2 = z.var(axis=1, ddof=1)
    c = np.corrcoef(s2[:,0], s2[:,1])[0,1]
    sig = np.sqrt(s2)
    c_sig = np.corrcoef(sig[:,0], sig[:,1])[0,1]
    print(f"  rho={rho:<4} corr(s^2) measured {c:+.4f}  vs rho^2 {rho**2:+.4f}   |  corr(sigma) {c_sig:+.4f}")
print("  -> my claim that sigma's estimation error is INDEPENDENT across bins is WRONG whenever")
print("     the bins are correlated; the correlation is rho_ij^2 and it is NOT small at rho=0.9.")
print()

print("=== (b2) THE LOAD-BEARING QUANTITY NEITHER DOCUMENT COMPUTED ===")
print("  Aggregate V_P = w' C w; sigma_i -> sigma_i(1+e_i) gives dV_P/V_P = 2 a'e/(1'a), a_i = w_i (Cw)_i.")
print("  coherent e = s*1  -> 2s.   random e = s*z, corr(z)=R -> sd 2s sqrt(a'Ra)/(1'a).")
print("  With R = (1-c)I + cJ and near-uniform a over n bins:  suppression = sqrt(c + (1-c)/n).")
n = 10694
print(f"  {'c_bar':>8} {'suppression':>12} {'coherent/random':>17}")
for c in (0.0, 1e-4, 1e-3, 1e-2, 0.1, 0.5, 0.815, 1.0):
    sup = np.sqrt(c + (1.0-c)/n)
    print(f"  {c:8.4g} {sup:12.4f} {1.0/sup:17.1f}")
# numerical confirmation of the closed form at one point
c = 0.815
R = (1-c)*np.eye(400) + c*np.ones((400,400))
a = np.ones(400)
print(f"  check n=400,c=0.815: closed form {np.sqrt(c+(1-c)/400):.6f}  direct {np.sqrt(a@R@a)/a.sum():.6f}")
print()
print("  => at c_bar = 0.815 the aggregate suppresses the estimation error by only 10%, NOT by")
print(f"     sqrt(10694) = {np.sqrt(n):.0f}. My T2 magnitude claim is DEFEATED at that c_bar.")
print("     But c_bar is the MEAN OFF-DIAGONAL rho^2 over all pairs, which is UNMEASURED; 0.815 was")
print("     measured for ONE pair at rho=0.9. Distant bins contribute small rho^2, so c_bar may be")
print("     far below 0.815 and the suppression far larger. THAT is what decides T2.")
print()

print("=== (d) is downward g movement unbounded? ===")
g_max, g_med = 17.653141714565614, 1.0473565738188244
print("  g = sqrt(max(v_uni,v_blk))/sqrt(v_blk) >= 1 BY CONSTRUCTION, and g' uses the same max,")
print("  so u = g'/g - 1 >= 1/g - 1 for every bin:")
for g,lab in ((g_max,'g_max'),(g_med,'g_median'),(1.0,'deadband (g=1)')):
    print(f"    {lab:16s} g={g:.6f}  worst downward u = {1.0/g - 1.0:+.6f}")
print("  -> my T5c inference 'g may fall to zero' is IMPOSSIBLE; gamma is finite from construction")
print("     alone, with no tolerance required. The f <= 1-(1-theta)^2 threshold is unaffected:")
th0 = 7.11e-2
print(f"     1-(1-theta)^2 = {1-(1-th0)**2:.6f}  (arithmetic stands; only the inference was wrong)")
