#!/bin/bash
#SBATCH --job-name=fps_pilot
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=fps_pilot_%j.out
#SBATCH --error=fps_pilot_%j.err

# FPS pilot chain (1A): acceptance study + three 2D unfolds + honesty battery.
#   unfold 1: FPS omnifile, MnvTune prior, extended grid
#   unfold 2: FPS omnifile, bare-GENIE prior (no --use-weights)  -> prior swap
#   unfold 3: standard 1A omnifile, paper grid, MnvTune prior    -> anchor ref
# Chained after sbatch_evloop_1A_fps.sh.

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

FPS_OMNI="runEventLoopOmniFold_5D_FPS_1A.root"
CTRL_OMNI="runEventLoopOmniFold_5D_1A.root"
[[ -s "$FPS_OMNI" ]] || { echo "[fps] FAIL: missing $FPS_OMNI" >&2; exit 2; }

# extended edges: exact paper edges + catch bins (keep in sync with fps_acceptance.py)
PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

echo "===== [1/5] acceptance study ====="
python3 fps_acceptance.py --omnifile "$FPS_OMNI"

echo "===== [2/5] FPS unfold, MnvTune prior ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "$FPS_OMNI" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --use-weights --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_1A_tune.root

echo "===== [3/5] FPS unfold, bare-GENIE prior ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "$FPS_OMNI" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_1A_genie.root

echo "===== [4/5] control unfold (standard omnifile, paper grid) ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "$CTRL_OMNI" --axes "" \
  --use-weights --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_CTRL_1A.root

echo "===== [5/5] honesty battery (anchor + prior swap) ====="
python3 fps_pilot_compare.py

echo "[fps] pilot chain done $(date -u '+%F %T UTC')"
