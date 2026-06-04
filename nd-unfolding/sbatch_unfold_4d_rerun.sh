#!/bin/bash
#SBATCH --job-name=unfold_4d_rerun
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=06:00:00
#SBATCH --output=unfold_4d_rerun_%A.out
#SBATCH --error=unfold_4d_rerun_%A.err

# Re-run the 4D CV unfold + anchors + injected-q3 closure after the THnSparse
# segfault fix (the merged omnifile already exists; skip hadd).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
MERGED="runEventLoopOmniFold_4D_MEFHC.root"

echo "[unfold] 4D CV unfold $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3 \
    --iters 5 --use-weights --estimator lgbm \
    --out xsec_4d_MEFHC_5iter_lgbm.root --verbose

echo "[anchor] $(date -u +%H:%M:%S)"
python3 check_4d_anchors.py --xsec4d xsec_4d_MEFHC_5iter_lgbm.root \
    --xsec3d ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root

echo "[closure] injected-q3-shape $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3 \
    --iters 5 --use-weights --estimator lgbm \
    --closure --closure-reweight-axis q3 --out closure_4d_q3bump.root --verbose
echo "[done] $(date -u +%H:%M:%S)"
