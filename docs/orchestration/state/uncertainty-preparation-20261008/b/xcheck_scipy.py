# Lane B self-check of assurance.json with scipy 1.15.2 / numpy 1.26.4 (not the independent E recomputation).
# Run from the repository root: python3 docs/orchestration/state/uncertainty-preparation-20261008/b/xcheck_scipy.py

import json, numpy as np
from scipy import stats, integrate
d=json.load(open('docs/orchestration/state/uncertainty-preparation-20261008/b/assurance.json'))
z95=stats.norm.ppf(0.975); nom={'I68':stats.norm.cdf(1)*2-1,'I95':0.95}; z={'I68':1.0,'I95':z95}
def cov(zz,k,B=300):
    # P(|N(0,k^2)| <= zz*s), s^2 ~ chi2_{B-1}/(B-1)  <=> P(|t_{B-1}| <= zz/k)
    return 2*stats.t.cdf(zz/k,B-1)-1
edges={q:(cov(z[q],1.25),cov(z[q],0.8)) for q in z}
print('edges',edges, {q:d['coverage_edges_b300'][q] for q in z})
at=0.04/412
def region(n,p0):
    ks=np.arange(n+1); cdf=stats.binom.cdf(ks,n,p0); sf=stats.binom.sf(ks-1,n,p0)
    a=int(np.max(np.where(cdf<=at/2)[0]))+1 if np.any(cdf<=at/2) else 0
    b=int(np.min(np.where(sf<=at/2)[0]))-1
    return a,b
def ok(n):
    for q in z:
        a,b=region(n,nom[q])
        for p in edges[q]:
            if stats.binom.cdf(b,n,p)-stats.binom.cdf(a-1,n,p)>0.10: return False
    return True
good=[ok(n) for n in range(400,1300)]
# first n where ok holds for n..n+100
for i in range(len(good)-100):
    if all(good[i:i+101]): print('N_required xcheck', 400+i); break
for n in (719,1116): print(n,{q:region(n,nom[q]) for q in z}, d['at_N_required'] if n==719 else d['at_N_design'])
# bias
za=stats.norm.ppf(1-0.01/412); zb=stats.norm.ppf(0.9)
print('bias N', int(np.ceil(((za+zb)/0.2)**2)), int(np.ceil(((za+zb)*1.25/0.2)**2)))
# offset average check: rho .5 s .5
tau=d['finite_reference_offset_N1'][4]['tau_ref_pull_units']; n=719
tot=0
for q in z:
    a,b=region(n,nom[q])
    f=lambda dl: (1-(stats.binom.cdf(b,n,stats.norm.cdf(z[q]-dl)-stats.norm.cdf(-z[q]-dl))-stats.binom.cdf(a-1,n,stats.norm.cdf(z[q]-dl)-stats.norm.cdf(-z[q]-dl))))*stats.norm.pdf(dl,0,tau)
    tot+=integrate.quad(f,-8*tau,8*tau,limit=200)[0]
print('expected cov failures rho.5 s.5', 206*tot, d['finite_reference_offset_N1'][4]['expected_coverage_failures_at_exact_calibration'])
