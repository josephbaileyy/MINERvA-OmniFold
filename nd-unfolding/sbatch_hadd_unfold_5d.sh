#!/bin/bash
#SBATCH --job-name=hadd_unfold_5d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=hadd_unfold_5d_%A.out
#SBATCH --error=hadd_unfold_5d_%A.err

# After the 12-playlist 5D event-loop array (sbatch_evloop_array_5d.sh): hadd the
# per-playlist 5D CV omnifiles (plain hadd is safe -- CV-only, ~34 GB total, under
# ROOT's 100 GB tree limit) and run the CV 5D unfold
# d^5 sigma/(dpt dpz dEavail dq3 dW), then the W-marginal anchor + W closure.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

MERGED="runEventLoopOmniFold_5D_MEFHC.root"
PARTS=()
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  PARTS+=("runEventLoopOmniFold_5D_${PL}.root")
done

echo "[hadd] start $(date -u +%H:%M:%S)"
hadd -f "${MERGED}" "${PARTS[@]}"
echo "[hadd] merged -> ${MERGED} ($(du -h ${MERGED} | cut -f1))"

echo "[unfold] 5D CV unfold start $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${MERGED}" --axes eavail,q3,W \
    --iters 5 --use-weights --estimator lgbm \
    --out products/5d/xsec_5d_MEFHC_5iter_lgbm.root --verbose

echo "[anchor] W-marginal -> frozen 4D check $(date -u +%H:%M:%S)"
python3 check_5d_anchors.py --xsec5d products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
    --xsec4d products/4d/xsec_4d_MEFHC_5iter_lgbm.root || true

echo "[closure] injected-W-shape closure $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${MERGED}" --axes eavail,q3,W \
    --iters 5 --use-weights --estimator lgbm \
    --closure --closure-reweight-axis W \
    --out products/5d/closure_5d_Wbump.root --verbose

echo "[done] $(date -u +%H:%M:%S)"
