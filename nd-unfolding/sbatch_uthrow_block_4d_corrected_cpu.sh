#!/bin/bash
#SBATCH --job-name=blk4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=03:00:00
#SBATCH --array=0-25%24
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/blk4dCc_%a_%A.out --error=uq_4d/corrected/logs/blk4dCc_%a_%A.err
# P6-4D corrected block-sum producer on CPU (MAT biased-1/N mean-centered comparator):
# tasks 0-5 = one knob PAIR each (24 endpoints); tasks 6-25 = one 5-flux chunk each
# (flux 0..99). skip-if-exists. uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/uthrow_slabs_4d
T=${SLURM_ARRAY_TASK_ID}
OUT="uq_4d/corrected/uthrow_slabs_4d/block4d_${T}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
COMMON=(--blockunits --bank uq_4d/corrected/bank_uthrow_4d --iters 5 --seed 1000 --invalid-ratio neutral --out "$OUT")
if [ "$T" -lt 6 ]; then
  KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
  echo "[blk4dCc] task=$T knobs=${KNOBS[$T]} $(date -u '+%F %T')"
  python3 unified_throw_cov.py "${COMMON[@]}" --block-knobs "${KNOBS[$T]}"
else
  lo=$(( (T-6)*5 )); hi=$(( lo+4 ))
  echo "[blk4dCc] task=$T flux=${lo}-${hi} $(date -u '+%F %T')"
  python3 unified_throw_cov.py "${COMMON[@]}" --block-knobs none --block-flux "${lo}-${hi}"
fi
echo "[blk4dCc] task=$T done $(date -u '+%F %T')"
