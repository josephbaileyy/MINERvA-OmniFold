#!/bin/bash
#SBATCH --job-name=fps_mefhc
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --output=fps_mefhc_%A.out
#SBATCH --error=fps_mefhc_%A.err

# FPS campaign step 2 (chained after sbatch_evloop_array_5d_fps.sh): merge the
# 12 FPS CV omnifiles and run the full-statistics MEFHC honesty battery:
#   [1] hadd (plain hadd safe: CV-only, ~7 GB total)
#   [2] acceptance study at MEFHC scale
#   [3] FPS unfold, MnvTune prior (extended grid)     -> the FPS cross section
#   [4] FPS unfold, bare-GENIE prior                  -> prior swap
#   [5] control unfold (standard 5D MEFHC omnifile)   -> anchor reference
#   [6] plain closure in FPS mode (MC reco as pseudo-data, extended grid)
#   [7] compare: anchor + prior swap maps/numbers
# Decision memo: FPS_PILOT.md. Gate for step-3 (universes_full UQ campaign):
# the [7] anchor must PASS at MEFHC scale.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

MERGED="runEventLoopOmniFold_5D_FPS_MEFHC.root"
CTRL_OMNI="runEventLoopOmniFold_5D_MEFHC.root"
PARTS=()
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  F="runEventLoopOmniFold_5D_FPS_${PL}.root"
  [[ -s "$F" ]] || { echo "[fps] FAIL: missing $F" >&2; exit 2; }
  PARTS+=("$F")
done

# keep in sync with fps_acceptance.py / sbatch_fps_pilot.sh
PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

echo "===== [1/7] hadd $(date -u +%H:%M:%S) ====="
hadd -f "${MERGED}" "${PARTS[@]}"
echo "[hadd] merged -> ${MERGED} ($(du -h ${MERGED} | cut -f1))"

echo "===== [2/7] acceptance study (MEFHC) ====="
python3 fps_acceptance.py --omnifile "${MERGED}" \
  --out-png products/5d/fps_acceptance_MEFHC.png

echo "===== [3/7] FPS unfold, MnvTune prior ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --use-weights --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_MEFHC_tune.root

echo "===== [4/7] FPS unfold, bare-GENIE prior ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_FPS_MEFHC_genie.root

echo "===== [5/7] control unfold (standard MEFHC omnifile, paper grid) ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "${CTRL_OMNI}" --axes "" \
  --use-weights --seed 1 --iters 5 --estimator lgbm \
  --out products/5d/xsec_2d_CTRL_MEFHC.root

echo "===== [6/7] FPS plain closure (extended grid) ====="
python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes "" \
  --full-phase-space --pt-edges "$PT_EXT" --pz-edges "$PZ_EXT" \
  --use-weights --seed 1 --iters 5 --estimator lgbm --closure \
  --out products/5d/closure_2d_FPS_MEFHC.root

echo "===== [7/7] honesty battery (anchor + prior swap, MEFHC) ====="
python3 fps_pilot_compare.py \
  --fps-tune products/5d/xsec_2d_FPS_MEFHC_tune.root \
  --fps-genie products/5d/xsec_2d_FPS_MEFHC_genie.root \
  --ctrl products/5d/xsec_2d_CTRL_MEFHC.root \
  --omnifile "${MERGED}" \
  --out-png products/5d/fps_pilot_compare_MEFHC.png

echo "[fps] MEFHC stage done $(date -u '+%F %T UTC')"
