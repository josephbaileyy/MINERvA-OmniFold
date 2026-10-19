"""Read-only reduction of committed D-ID tables: CR-width floor per reporting map at nominal truth."""
import sys, json, hashlib
import numpy as np
p = sys.argv[1]
h = hashlib.sha256(open(p,'rb').read()).hexdigest()
t = np.load(p, allow_pickle=False)
g = t['groups183']; rep = t['reported183']; names = t['names']
out = {'tables_npz': p, 'sha256': h, 'groups': {str(k): int(v) for k, v in zip(*np.unique(g, return_counts=True))}}
for grid in ('T1', 'T2'):
    for wt in ('widths_nom', 'widths_dep'):
        for truth in ('nominal', 'gibuu', 'w3'):
            key = f'{grid}/{truth}/{wt}/sigma_rel'
            s = t[key]; hole = t[f'{grid}/{truth}/{wt}/acceptance_hole']
            for grp in np.unique(g):
                m = (g == grp) & rep
                v = s[m]; fin = np.isfinite(v)
                out[f'{key}|{grp}'] = dict(n=int(m.sum()), n_finite=int(fin.sum()), holes=int(hole[m].sum()),
                    median_all=float(np.median(np.where(fin, v, np.inf))),
                    median_finite=float(np.median(v[fin])) if fin.any() else None,
                    frac_le_0p086=float(np.mean(v <= 0.086)), frac_le_0p10=float(np.mean(v <= 0.10)),
                    frac_le_0p025=float(np.mean(v <= 0.025)))
print(json.dumps(out, indent=1))
