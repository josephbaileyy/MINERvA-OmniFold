#!/usr/bin/env python3
"""regenA amendment A5: the eigenmode numbers of appC_supplementary.tex:7 and records_r03_twod.tex:18, on one input.
Reads; draws nothing.

  a5_readout.py --module-dir <W>/2d-unfolding --anc <anc dir> --xsec <xsec.root> --report <tension_report.txt> --out <json>

The decomposition is diagnose_tension.py:110-171's: eigh of the published TotalCovariance on the 205 reported cells;
c = U^T (ours - published); contribution c_k^2 / lam_k for lam_k > 1e-15 lam_max; modes ranked by contribution;
lam_rank 0 = smallest eigenvalue. The standardized component of a mode is |c_k| / sqrt(lam_k) (diagnose_tension's
eigpull; per_period_benchmark.py:415-420's abs_z is the same quantity). Share = the fraction of sum u^2 in the two
highest p_par bins (p_par >= 20 GeV/c).
C5-REP: every value diagnose_tension printed in --report (the committed regenA P4 tension_report.txt of this input) is
reproduced at its printed precision.
"""
import argparse, json, re, sys
import numpy as np

ap = argparse.ArgumentParser()
for k in ("module-dir", "anc", "xsec", "report", "out"):
    ap.add_argument("--" + k, required=True)
a = ap.parse_args()
sys.path[:0] = [a.module_dir, a.module_dir + "/uq"]
import ROOT
import compare_to_paper_fullcov as cpf

N_PT, N_PZ = 14, 16
fp = ROOT.TFile.Open(f"{a.anc}/cov_ptpl_minerva_inclusive_6GeV.root")
pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section"))
cov_t = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance")); cov_s = cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
fp.Close()
fo = ROOT.TFile.Open(a.xsec); ours = cpf.flatten_ours(fo.Get("hXSec2D")); fo.Close()
mask = np.diag(cov_s) > 0; n = int(mask.sum()); idx = np.where(mask)[0]
d = (ours - pub)[mask]; V = cov_t[np.ix_(mask, mask)]
lam, U = np.linalg.eigh(V); lam_max = lam.max()
c = U.T @ d
keep = lam > 1e-15 * lam_max
contrib = np.where(keep, c ** 2 / np.where(keep, lam, 1.0), 0.0); chi2 = float(contrib.sum())
order = np.argsort(contrib)[::-1]; lam_rank = np.argsort(np.argsort(lam))
def share(k):
    g = np.zeros((N_PT, N_PZ)); g[idx // N_PZ, idx % N_PZ] = U[:, k] ** 2
    return float(g[:, 14:].sum() / g.sum())
modes = [{"rank": j, "lam_rel": float(lam[k] / lam_max), "lam_rank": int(lam_rank[k]), "abs_z": float(abs(c[k]) / np.sqrt(lam[k])),
          "eigpull": float(c[k] / np.sqrt(lam[k])), "chi2_contrib": float(contrib[k]), "share_pz_ge_20": share(k)} for j, k in enumerate(order[:15])]
top5 = order[:5]
out = {"xsec": a.xsec, "n_reported": n, "chi2_modes": chi2, "modes": modes,
       "share10_smallest": float(contrib[lam_rank < 10].sum() / chi2),
       "top5_in_smallest_tenth": int(np.sum(lam_rank[top5] < n * 0.1)),
       "largest_abs_z": modes[0]["abs_z"], "next_nine_abs_z": [m["abs_z"] for m in modes[1:10]]}
six = modes[:6]; hi = [m for m in six if m["share_pz_ge_20"] > 0.5]; lo = [m for m in six if m["share_pz_ge_20"] <= 0.5]
out["six_split"] = {"high_pz": [m["rank"] for m in hi], "lower_pz": [m["rank"] for m in lo],
                    "high_pz_lam_rel": [m["lam_rel"] for m in hi], "lower_pz_lam_rel": [m["lam_rel"] for m in lo]}
# C5-REP against the producer's printed report
rep = open(a.report).read(); bad = []
rows = re.findall(r"^\s+(\d+)\s+([0-9.e+-]+)\s+(\d+)/(\d+)\s+([+-][0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$", rep, re.M)
for (r, lr, lk, nn, ep, cc, cum) in rows[:15]:
    m = modes[int(r)]
    ok = f"{m['lam_rel']:.3e}" == lr and m["lam_rank"] == int(lk) and f"{m['eigpull']:+.2f}" == ep and f"{m['chi2_contrib']:.2f}" == cc
    if not ok: bad.append((r, lr, lk, ep, cc, m))
fs = re.search(r"smallest-10%+ lambda band:\s+([0-9.]+)", rep); s10 = re.search(r"10 smallest-lambda modes:\s+([0-9.]+)", rep)
ok_fs = fs and f"{out['top5_in_smallest_tenth'] / 5:.2f}" == fs.group(1); ok_s10 = s10 and f"{out['share10_smallest']:.3f}" == s10.group(1)
out["C5-REP"] = {"rows_compared": len(rows[:15]), "row_mismatches": [b[:5] for b in bad], "top5_fraction": bool(ok_fs),
                 "share10": bool(ok_s10), "pass": len(rows) >= 15 and not bad and bool(ok_fs) and bool(ok_s10)}
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps({"C5-REP": out["C5-REP"]["pass"], "share10": out["share10_smallest"], "top5_small": out["top5_in_smallest_tenth"],
                  "z": [round(out["largest_abs_z"], 4), round(min(out["next_nine_abs_z"]), 4), round(max(out["next_nine_abs_z"]), 4)],
                  "split": out["six_split"]}))
