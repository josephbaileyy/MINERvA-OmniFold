"""Published-side flux component of arXiv:2106.16210 data release (own code)."""
import sys, csv, hashlib
import numpy as np
D = sys.argv[1]
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
m = {}
with open(f"{D}/bin_mapping.txt") as f:
    for r in csv.DictReader(f):
        m[(int(r['P||bin']), int(r['Ptbin']))] = (int(r['GlobalID']),
            (float(r['P||bin_highedge'])-float(r['P||bin_lowedge']))*(float(r['Ptbin_highedge'])-float(r['Ptbin_lowedge'])))
n = 224
xs = np.zeros(n); area = np.zeros(n); tot = np.zeros(n); st = np.zeros(n)
with open(f"{D}/data_result_ptpl_2D_minerva_inclusive_6GeV.txt") as f:
    for r in csv.DictReader(f):
        g, a = m[(int(r['P||bin']), int(r['Ptbin']))]
        xs[g] = float(r['cross_section']); area[g] = a
        st[g] = float(r['statistical_uncertainty']); tot[g] = float(r['total_uncertainty'])
def cov(name):
    C = np.zeros((n, n)); p = f"{D}/cov_ptpl_minerva_inclusive_6GeV_{name}.txt"
    with open(p) as f:
        next(f)
        for line in f:
            i, j, v = line.strip().split(',')
            C[int(i), int(j)] = float(v)
    return C, sha(p)
rep = xs > 0
print("reported cells", rep.sum())
for name in ["flux", "energyscale", "stat", "total"]:
    C, h = cov(name)
    s = np.sqrt(np.clip(np.diag(C), 0, None))[rep] / xs[rep]
    a = area[rep]; Cr = C[np.ix_(rep, rep)]
    integ = np.sqrt(a @ Cr @ a) / (a @ xs[rep])
    print(f"{name:12s} sha256={h[:16]}  per-cell median={100*np.median(s):.3f}%  p16={100*np.percentile(s,16):.3f}% "
          f"min={100*s.min():.3f}%  max={100*s.max():.3f}%  integral sigma={100*integ:.3f}%")
# correlation structure of flux: leading eigenvalue fraction
C, _ = cov("flux"); Cr = C[np.ix_(rep, rep)]
w = np.linalg.eigvalsh(Cr); print("flux leading-eig fraction of trace", w[-1]/w.sum())
print("csv total-unc median rel", 100*np.median(tot[rep]/xs[rep]))
