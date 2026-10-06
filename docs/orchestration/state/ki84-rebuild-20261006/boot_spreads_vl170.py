"""KNOWN_ISSUES 84 / VL170 adoption: boot_spreads.py of state/note-boot-20261003/ (VL162) with only the replica
set, the stored rollup and OUTDIR changed, to the 300 rebuilt replicas and uq/bootstrap_MEFHC_300_vl170/.
Original docstring follows.
Read-only: re-measure the 2D statistical-bootstrap spreads quoted in App. A on the pure-Poisson
(pinned --seed 1) N=300 MEFHC lgbm replicas, with analyze_uq.py's own definitions (imported unchanged),
and check the replicas against the stored rollup uq/bootstrap_MEFHC_300/uq_covariance_boot300.root.
Writes only to OUTDIR."""
import glob, json, os, re, sys
sys.dont_write_bytecode = True
import numpy as np
UQ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
OUTDIR = "/pscratch/sd/j/josephrb/ki84-rebuild-20261006/adoption_controls/boot_spreads"
REPL = "/pscratch/sd/j/josephrb/ki84-rebuild-20261006/replicas"
sys.path.insert(0, UQ)
import analyze_uq as au
import ROOT
ROOT.gROOT.SetBatch(True)

files = glob.glob(os.path.join(REPL, "2d_xsec_MEFHC_5iter_lgbm_boot*.root"))
idx = lambda p: int(re.search(r"_boot(\d+)\.root$", p).group(1))
files = sorted(files, key=idx)
assert [idx(p) for p in files] == list(range(1, 301)), "expected boot1..boot300"
X = []
for p in files:
    f = ROOT.TFile.Open(p); X.append(au.th2_to_array(f.Get("hXSec2D"))); f.Close()
X = np.stack(X)                                  # (300, 14, 16)
dA = np.diff(au.PT_EDGES)[:, None] * np.diff(au.PZ_EDGES)[None, :]

def stats(Xs):
    N = Xs.shape[0]
    mean = Xs.mean(0); std = Xs.std(0, ddof=1)
    rel = np.where(mean > 0, std / np.where(mean > 0, mean, 1), np.nan)
    rep = (mean > 0).ravel(order="C")
    rr = rel.ravel(order="C")[rep]
    stot = (Xs * dA[None]).sum(axis=(1, 2))
    C = np.cov(Xs.reshape(N, -1, order="C")[:, rep], rowvar=False, ddof=1)
    return {"N": N, "n_reported": int(rep.sum()),
            "sigma_tot_mean": float(stot.mean()), "sigma_tot_rel_std_pct": float(100 * stot.std(ddof=1) / stot.mean()),
            "median_rel_pct": float(100 * np.median(rr)), "p16_rel_pct": float(100 * np.percentile(rr, 16)),
            "p84_rel_pct": float(100 * np.percentile(rr, 84)), "max_rel_pct": float(100 * rr.max()),
            "sqrt_trace": float(np.sqrt(np.trace(C)))}, C, rep

out = {"files": len(files), "mtime_first": min(os.path.getmtime(p) for p in files),
       "mtime_last": max(os.path.getmtime(p) for p in files)}
s300, C300, rep300 = stats(X)
s50, _, _ = stats(X[:50])
out["N300"], out["N50_first50"] = s300, s50

f = ROOT.TFile.Open(os.path.join(UQ, "bootstrap_MEFHC_300_vl170", "uq_covariance_boot300.root"))
Cst = au.th2_to_array(f.Get("hCov2D_reported"))
mst = au.th2_to_array(f.Get("hMean2D")); relst = au.th2_to_array(f.Get("hRel2D")); f.Close()
rep_st = (mst > 0).ravel(order="C")
rr_st = relst.ravel(order="C")[rep_st]
w = dA.ravel(order="C")[rep_st]
out["stored"] = {"n_reported": int(rep_st.sum()), "sqrt_trace": float(np.sqrt(np.trace(Cst))),
                 "median_rel_pct": float(100 * np.median(rr_st)), "p84_rel_pct": float(100 * np.percentile(rr_st, 84)),
                 "sigma_tot_rel_std_pct": float(100 * np.sqrt(w @ Cst @ w) / (mst.ravel(order="C")[rep_st] @ w))}
out["controls"] = {"same_reported_set": bool(np.array_equal(rep_st, rep300)),
                   "cov_max_abs_diff_over_max": float(np.max(np.abs(C300 - Cst)) / np.max(np.abs(Cst))),
                   "mean_max_rel_diff": float(np.nanmax(np.abs(X.mean(0) - mst)[mst > 0] / mst[mst > 0]))}
os.makedirs(OUTDIR, exist_ok=True)
json.dump(out, open(os.path.join(OUTDIR, "boot_spreads.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
