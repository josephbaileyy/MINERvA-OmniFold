#!/bin/bash
#SBATCH --job-name=blkfpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=04:00:00
#SBATCH --array=0-25%16
#SBATCH --nice=0
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/blkfpsC_%a_%A.out --error=uq_fps/corrected/logs/blkfpsC_%a_%A.err
# CORRECTED FPS block-sum units (Agent C / P6-FPS): the apples-to-apples comparator for
# the unified throw, from the SAME bank at the SAME fixed estimator seed.
#   tasks 0-5   -> 12 knobs x 2 endpoints = 24 knob units (2 knobs/task)
#   tasks 6-25  -> 100 flux universes (5 flux/task) -- the corrected combine requires ALL
#                  100 flux block units (the June launcher produced only 12; incompatible
#                  with the current do_combine flux-inventory gate).
# => 24 knob + 100 flux = 124 block units (matches the corrected 5D build's 124-unit block).
# High --nice yields to PET(B)/4D(D). Non-destructive: uq_fps/corrected/uthrow_slabs_fps_neutral/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/corrected/uthrow_slabs_fps_neutral
T=${SLURM_ARRAY_TASK_ID}
KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
OUT="uq_fps/corrected/uthrow_slabs_fps_neutral/blockfps_${T}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
if (( T <= 5 )); then
  echo "[blkfpsC] task=$T knobs=${KNOBS[$T]} $(date -u '+%F %T UTC')"
  python3 unified_throw_cov.py --blockunits --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --seed 1000 \
      --block-knobs "${KNOBS[$T]}" --out "${OUT}"
else
  LO=$(( (T-6)*5 )); HI=$(( LO+4 ))
  echo "[blkfpsC] task=$T flux=${LO}-${HI} $(date -u '+%F %T UTC')"
  python3 unified_throw_cov.py --blockunits --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --seed 1000 \
      --block-knobs "" --block-flux "${LO}-${HI}" --out "${OUT}"
fi
echo "[blkfpsC] task=$T done $(date -u '+%F %T UTC')"
