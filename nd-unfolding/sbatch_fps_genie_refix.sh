#!/bin/bash
#SBATCH --job-name=fps_genie_refix
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=08:00:00
#SBATCH --output=fps_genie_refix_%A.out
#SBATCH --error=fps_genie_refix_%A.err

# Verification of the 2026-06-10 driver fix for KNOWN_ISSUES #1 (no
# --use-weights mode was globally low by pot_scale). Re-runs the two
# bare-GENIE-prior unfolds with the fixed driver (overwrites the pre-fix
# artifacts) and re-runs the honesty battery + 3-prior envelope, whose
# 1/pot_scale corrections have been removed.
# PASS criteria: tune/genie total ratios and the envelope medians reproduce
# the ledger values that previously required the exact global correction.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

echo "===== [1/4] 1A bare-GENIE unfold (fixed driver) ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile runEventLoopOmniFold_5D_FPS_1A.root \
  --axes "" --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_1A_genie.root

echo "===== [2/4] 1A honesty battery (no correction) ====="
python3 fps_pilot_compare.py

echo "===== [3/4] MEFHC bare-GENIE unfold (fixed driver) ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root \
  --axes "" --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_MEFHC_genie.root

echo "===== [4/4] MEFHC battery + 3-prior envelope (no correction) ====="
python3 fps_pilot_compare.py \
  --fps-tune products/5d/xsec_2d_FPS_MEFHC_tune.root \
  --fps-genie products/5d/xsec_2d_FPS_MEFHC_genie.root \
  --ctrl products/5d/xsec_2d_CTRL_MEFHC.root \
  --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root \
  --out-png products/5d/fps_pilot_compare_MEFHC.png
python3 fps_prior_envelope.py

echo "[refix] done $(date -u '+%F %T UTC')"
