#!/bin/bash
# Negweight-vs-purity COVARIANCE comparison (run AFTER the Phase-D campaign lands).
# Builds the negweight statistical (bootstrap) + systematic (universe) covariances
# and compares to the purity references. Dispatch via:
#   ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28 \
#     ./alloc_run.sh 'bash 2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh'
#
# Prereqs (job IDs in tmp/regen_jids.txt; check squeue first):
#   - Bootstrap: uq/negweight_boot/2d_xsec_*_nw_boot*.root (job 55668087, array 1-50)
#     vs the 300 adopted purity replicas uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root
#   - Universe : uq/negweight_uni/ + uq/purity_newomni/ (both-mode rebuild on the
#     freshly regenerated 150 GB omnifile; jobs 55668380/82 + CV 55668400/01),
#     which also lets purity_newomni vs the May adopted covariance quantify the
#     Jul-04 event-loop binary drift.
set -uo pipefail
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
PY=python

echo "############ STATISTICAL (bootstrap) covariance ############"
n_nw=$(ls uq/negweight_boot/2d_xsec_*_nw_boot*.root 2>/dev/null | wc -l)
echo "negweight bootstrap replicas on disk: ${n_nw}"
if (( n_nw >= 2 )); then
  $PY uq/analyze_uq.py --glob "uq/negweight_boot/2d_xsec_*_nw_boot*.root" \
      --outdir uq/negweight_boot --out-root uq_cov_negweight_boot.root
fi
echo "--- purity bootstrap reference (matched seeds 1-50 of the 300 on disk) ---"
$PY uq/analyze_uq.py --glob "uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root" \
    --outdir uq/boot_purity_ref --out-root uq_cov_purity_boot.root || true

echo "############ SYSTEMATIC (universe) covariance ############"
NWCV=uq/negweight_uni/2d_xsec_MEFHC_5iter_lgbm_nw_uni_CV.root
PNCV=uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root
n_nwu=$(ls uq/negweight_uni/2d_xsec_*_nw_uni_*.root 2>/dev/null | grep -v _CV | wc -l)
n_pnu=$(ls uq/purity_newomni/2d_xsec_*_pn_uni_*.root 2>/dev/null | grep -v _CV | wc -l)
echo "negweight universe unfolds: ${n_nwu} ; purity-new universe unfolds: ${n_pnu}"
if [[ -s "$NWCV" && $n_nwu -ge 2 ]]; then
  $PY uq/analyze_universes.py --cv "$NWCV" \
      --glob "uq/negweight_uni/2d_xsec_*_nw_uni_*.root" \
      --outdir uq/negweight_uni/rollup
fi
if [[ -s "$PNCV" && $n_pnu -ge 2 ]]; then
  $PY uq/analyze_universes.py --cv "$PNCV" \
      --glob "uq/purity_newomni/2d_xsec_*_pn_uni_*.root" \
      --outdir uq/purity_newomni/rollup
fi

echo "############ COMPARE (trace, sqrt-trace, per-bin diag) ############"
$PY - <<'PYEOF'
import ROOT, math, os
ROOT.gROOT.SetBatch(True)
def load_cov(path, hname):
    if not os.path.exists(path): return None
    f=ROOT.TFile.Open(path); h=f.Get(hname)
    if not h: f.Close(); return None
    n=h.GetNbinsX(); import numpy as np
    C=np.array([[h.GetBinContent(i+1,j+1) for j in range(n)] for i in range(n)])
    f.Close(); return C
import numpy as np
pairs=[
 ("STAT bootstrap", "uq/negweight_boot/uq_cov_negweight_boot.root",
  "uq/boot_purity_ref/uq_cov_purity_boot.root", "hCov2D_reported"),
 ("SYST universe", "uq/negweight_uni/rollup/uq_universe_covariance.root",
  "uq/purity_newomni/rollup/uq_universe_covariance.root", "hCov_universe_total"),
]
for label,pnw,ppu,hn in pairs:
    Cn=load_cov(pnw,hn); Cp=load_cov(ppu,hn)
    if Cn is None or Cp is None:
        print(f"[{label}] missing ({'nw ok' if Cn is not None else 'nw MISSING'}, "
              f"{'pu ok' if Cp is not None else 'pu MISSING'})"); continue
    tn,tp=np.trace(Cn),np.trace(Cp)
    print(f"[{label}] sqrt(trace): negweight={math.sqrt(abs(tn)):.4e} "
          f"purity={math.sqrt(abs(tp)):.4e} ratio={math.sqrt(abs(tn)/abs(tp)):.4f}")
print("COV_COMPARE_DONE")
PYEOF
echo "ANALYSIS_DONE"
