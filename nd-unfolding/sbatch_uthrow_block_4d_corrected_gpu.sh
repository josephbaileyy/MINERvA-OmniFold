#!/bin/bash
#SBATCH --job-name=blk4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=0-25%6
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/blk4dC_%a_%A.out --error=uq_4d/corrected/logs/blk4dC_%a_%A.err
# P6-4D corrected block-sum producer (MAT biased-1/N mean-centered comparator).
# 124 block units = 12 knob bands x2 endpoints (24) + 100 flux, spread over 26
# small tasks so each stays well inside the 3h wall (<=5 units/task):
#   tasks 0-5  : one knob PAIR each (4 unfolds)  [no flux]
#   tasks 6-25 : one 5-flux chunk each (5 unfolds) -> flux 0..99 exactly once
# do_blockunits atomic-saves each unit; a wall-kill loses <=1 unit. uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/uthrow_slabs_4d
T=${SLURM_ARRAY_TASK_ID}
OUT="uq_4d/corrected/uthrow_slabs_4d/block4d_${T}.npz"
COMMON=(--blockunits --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --seed 1000 --invalid-ratio neutral --out "$OUT")
if [ "$T" -lt 6 ]; then
  KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
  echo "[blk4dC] task=$T knobs=${KNOBS[$T]} $(date -u '+%F %T')"
  python3 unified_throw_cov.py "${COMMON[@]}" --block-knobs "${KNOBS[$T]}"
else
  lo=$(( (T-6)*5 )); hi=$(( lo+4 ))
  echo "[blk4dC] task=$T flux=${lo}-${hi} $(date -u '+%F %T')"
  python3 unified_throw_cov.py "${COMMON[@]}" --block-knobs none --block-flux "${lo}-${hi}"
fi
echo "[blk4dC] task=$T done $(date -u '+%F %T')"
