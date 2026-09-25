import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(H + "/r6_refine_reco.json")); names = d["names"]; idx = {n: i for i, n in enumerate(names)}
a = np.load(H + "/r1_arrays.npz"); rel = a["rel_nom"]; r8 = a["r8"]; rdat = (a["fn"] - a["fp"]) / a["fp"]
bias = rel.mean(0); se = rel.std(0, ddof=1) / np.sqrt(rel.shape[0]); t = bias / se
b8 = r8.mean(0)
A = lambda k: np.mean([np.array(d[s][k]) for s in ("300000", "300001")], 0)
S, Sg, R, T, Bc = A("S"), A("Sg"), A("R"), A("T"), A("Bc")
refine_err = (R - Sg) / S          # refinement's local departure from the signed sum (deterministic smoothing)
tot_err = (R - S) / S              # refined minus the pseudo-data's true signal counts
bfrac = T / S
dd = d["data"]; D, B, Rd, P = map(np.array, (dd["D"], dd["B"], dd["R"], dd["P"]))
refine_err_data = (Rd - (D - B)) / (D - B); purity_err_data = (P - (D - B)) / (D - B)
claimed = ["J80", "J85", "J88", "J89", "J94", "J97", "J98", "J106", "J107", "J161", "J162", "J175"]
print("name   C3bias%  t   C8bias%  bkg/sig  refine(R-Sg)/S%  (R-S)/S%  | data: refine(R-(D-B))%  purity%  C7 rd%")
top = list(np.argsort(-np.abs(t))[:20]) + [idx[n] for n in ("EW41", "EW36", "J242", "J26", "EW37", "total_integrated")]
for i in top:
    print(f"{names[i]:<16s} {100*bias[i]:6.2f} {t[i]:6.1f} {100*b8[i]:6.2f}  {bfrac[i]:.3f}  {100*refine_err[i]:7.3f}  {100*tot_err[i]:7.3f}  | {100*refine_err_data[i]:7.3f} {100*purity_err_data[i]:7.3f} {100*rdat[i]:7.3f}")
from scipy.stats import spearmanr, pearsonr
ex = bias - b8
o = {"spearman(C3bias - C8bias, bkg/sig)": float(spearmanr(ex, bfrac).correlation),
     "spearman(C3bias - C8bias, reco refine err)": float(spearmanr(ex, refine_err).correlation),
     "pearson(C3bias - C8bias, reco refine err)": float(pearsonr(ex, refine_err)[0]),
     "spearman(C3 bias, reco (R-S)/S)": float(spearmanr(bias, tot_err).correlation),
     "reco refine err: median|.|%, max|.|%": [100*float(np.median(np.abs(refine_err))), 100*float(np.max(np.abs(refine_err)))],
     "reco refine err claimed J %": {j: round(100*float(refine_err[idx[j]]), 3) for j in claimed},
     "data refine err claimed J %": {j: round(100*float(refine_err_data[idx[j]]), 3) for j in claimed},
     "spearman(data refine err, C7 rd)": float(spearmanr(refine_err_data, rdat).correlation),
     "spearman(data refine err - purity err, C7 rd)": float(spearmanr(refine_err_data - purity_err_data, rdat).correlation),
     "spearman(reco refine err pseudo, reco refine err data)": float(spearmanr(refine_err, refine_err_data).correlation)}
print(json.dumps(o, indent=1)); json.dump(o, open(H + "/r7_cells.json", "w"), indent=1)
