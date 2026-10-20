import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import norm
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import s5c_coverage as cov
S = WT / "docs/orchestration/state/s5c"
contract = json.loads((S / "contract.json").read_text())
U, names = cov.reported_functionals(contract)
D = json.loads(Path("diag_out.json").read_text())["rows"]
rec = json.loads((S / "tier_s/interim_400.json").read_text())
g = {x["truth"]: x for x in rec["grid"]}
fut_t = [i for i, u in enumerate(g["eavail_tilt"]["ucb68"]) if u < 0.66]
fut_t95 = [i for i, u in enumerate(g["eavail_tilt"]["ucb95"]) if u < 0.94]
print("futile tilt 68:", len(fut_t), " 95:", len(fut_t95), " union:", len(set(fut_t) | set(fut_t95)))
# W>=2.2 share of each functional's truth (nominal p3 truth)
z = np.load(S / "p3/products/p3_nominal_s1.npz"); xt = z["xtrue_flat"]
shape = tuple(z["shape"]); idx = np.unravel_index(np.arange(xt.size), shape)
Wb = idx[4]; Eb = idx[2]
hiW = (Wb >= 4)
fW = (U * (xt * hiW)) .sum(1) / (U * xt).sum(1)
fW3 = (U * (xt * (Wb == 5))).sum(1) / (U * xt).sum(1)
ft = U @ xt; tot = ft[names.index("total_integrated")]
for lab, S_ in (("futile68", set(fut_t)), ("futile95-only", set(fut_t95) - set(fut_t)), ("not futile", set(range(len(names))) - set(fut_t) - set(fut_t95))):
    ii = sorted(S_)
    print(f"{lab:14s} n={len(ii):3d}  median W>=2.2 share {np.median(fW[ii]):.2f}  min {np.min(fW[ii]):.2f}  "
          f"n with W>=2.2 share>0.5: {(fW[ii]>0.5).sum()}  median beta {np.median([D[i]['beta_pct'] for i in ii]):+.2f}%")
print("non-futile functionals with W>=2.2 share > 0.5:", [names[i] for i in range(len(names)) if fW[i] > 0.5 and i not in fut_t and i not in fut_t95])
print("futile functionals with W>=2.2 share < 0.5:", [(names[i], round(fW[i],2)) for i in sorted(set(fut_t)|set(fut_t95)) if fW[i] < 0.5])
# EW table by W bin: shift = p3 tilt raw - beta ; validation-inferred |d| in sigma
print("EW cells: name Ebin Wbin inj beta p3raw p3cor cov68t |d|t")
for k in range(42):
    r = D[k]; e, w = divmod(k, 6)
    print(f"EW{k:<3d} E{e} W{w} inj {r['inj_pct']:+6.2f} beta {r['beta_pct']:+6.2f} p3raw {r['p3tilt_raw_pct']:+6.2f} p3cor {r['p3tilt_cor_pct']:+6.2f} pull {r['p3tilt_cor_pull']:+5.1f} c68 {r['eavail_tilt']['cov68']:.3f}/{r['nominal']['cov68']:.3f} |d| {r['eavail_tilt']['inferred_absbias_over_sigma']:.2f}")
# per-W mean of p3 corrected pull over EW cells
for w in range(6):
    ks = [6*e+w for e in range(7)]
    print("Wbin", w, "mean p3 cor pct", np.mean([D[k]['p3tilt_cor_pct'] for k in ks]).round(2), "mean pull", np.mean([D[k]['p3tilt_cor_pull'] for k in ks]).round(2), "median tilt c68", np.median([D[k]['eavail_tilt']['cov68'] for k in ks]))
# correlation across all 153: p3 corrected pull vs W>=2.2 share
p = np.array([r['p3tilt_cor_pull'] for r in D]); print("corr(p3 tilt corrected pull, W>=2.2 share) =", np.corrcoef(p, fW)[0,1].round(3))
print("J224 share of total truth", ft[names.index('J224')]/1, "relative to total (unit-mismatch, vol-weighted):")
# coverage decomposition with inferred (d, s)
print("decomposition: actual | bias only (sd=hw) | width only (d=0)")
for nm in ("J224","EW17","J233","EW23","EW11","EW29","EW16","EW10","J116"):
    r = D[names.index(nm)]["eavail_tilt"]; d, s, h = r["inferred_absbias_over_sigma"], r["inferred_sd_over_sigma"], r["hw_over_sigma"]
    c = lambda d, s, k: norm.cdf((k*h - d)/s) - norm.cdf((-k*h - d)/s)
    print(f"{nm:5s} d {d:.2f} sd {s:.2f} hw {h:.2f} | 68 {c(d,s,1):.3f} 95 {c(d,s,1.96):.3f} | bias-only 68 {c(d,h,1):.3f} | no-bias 68 {c(0,s,1):.3f} 95 {c(0,s,1.96):.3f}")
