#!/bin/bash
#SBATCH --job-name=fps_envelope
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=06:00:00
#SBATCH --output=fps_envelope_%A.out
#SBATCH --error=fps_envelope_%A.err

# FPS campaign step 3 (chained after sbatch_fps_mefhc.sh): the NuWro-shaped
# third prior + the 3-prior envelope.
#   [1] rebuild the NuWro/MnvTune prior ratio from the MERGED MEFHC truth
#   [2] FPS unfold with the NuWro-shaped prior (--prior-reweight)
#   [3] 3-prior envelope (tune / bare-GENIE / NuWro-shaped) zone summary
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

MERGED="runEventLoopOmniFold_5D_FPS_MEFHC.root"
[[ -s "$MERGED" ]] || { echo "[env] FAIL: missing $MERGED" >&2; exit 2; }

PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

echo "===== [1/3] prior ratio from merged MEFHC truth ====="
python3 build_fps_prior_nuwro.py --omnifile "${MERGED}" \
  --out products/5d/fps_prior_nuwro_ratio.root

echo "===== [2/3] FPS unfold, NuWro-shaped prior ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --use-weights --prior-reweight products/5d/fps_prior_nuwro_ratio.root \
  --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_MEFHC_nuwroprior.root

echo "===== [3/3] 3-prior envelope ====="
python3 fps_prior_envelope.py

echo "[env] done $(date -u '+%F %T UTC')"
