#!/bin/bash
#SBATCH --job-name=hadd_unfold_4d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=hadd_unfold_4d_%A.out
#SBATCH --error=hadd_unfold_4d_%A.err

# After the 12-playlist q3 event-loop array: hadd the per-playlist 4D omnifiles
# (plain hadd is safe -- CV-only files, ~34 GB total, well under ROOT's 100 GB
# tree limit; hadd sums the dataPOTUsed/mcPOTUsed TParameters) and run the CV 4D
# unfold d^4 sigma/(dpt dpz dEavail dq3), then the validation anchors.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

MERGED="runEventLoopOmniFold_4D_MEFHC.root"
PARTS=()
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  PARTS+=("runEventLoopOmniFold_4D_${PL}.root")
done

echo "[hadd] start $(date -u +%H:%M:%S)"
hadd -f "${MERGED}" "${PARTS[@]}"
echo "[hadd] merged -> ${MERGED} ($(du -h ${MERGED} | cut -f1))"

echo "[unfold] 4D CV unfold start $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${MERGED}" --axes eavail,q3 \
    --iters 5 --use-weights --estimator lgbm \
    --out xsec_4d_MEFHC_5iter_lgbm.root --verbose

echo "[anchor] q3->3D and ->2D marginal checks $(date -u +%H:%M:%S)"
python3 check_4d_anchors.py --xsec4d xsec_4d_MEFHC_5iter_lgbm.root \
    --xsec3d ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root || true

echo "[closure] injected-q3-shape closure $(date -u +%H:%M:%S)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${MERGED}" --axes eavail,q3 \
    --iters 5 --use-weights --estimator lgbm \
    --closure --closure-reweight-axis q3 \
    --out closure_4d_q3bump.root --verbose

echo "[done] $(date -u +%H:%M:%S)"
