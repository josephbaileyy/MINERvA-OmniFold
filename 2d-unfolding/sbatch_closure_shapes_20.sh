#!/bin/bash
#SBATCH --job-name=closure_shapes_20
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=00:45:00
#SBATCH --array=1-20%10
#SBATCH --output=closure_shapes_20_%a_%A.out
#SBATCH --error=closure_shapes_20_%a_%A.err

# Stage-2 closure-shape scan: 20 reweight shapes total (Stage-1 used 2).
# Combines gauss_pt and tilt_pz shapes over a parameter grid covering
# amplitude, pt0 / pz_ref, and sigma / alpha. Each task drives
# uq/closure/closure_truth_reweight.py and asserts the per-bin median
# residual stays under the configured threshold (default 1.5 %).
#
# Output: uq/closure/2d_xsec_1A_5iter_lgbm_closure_shape<N>.root + .log

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"

# 20 shape configurations: 16 gauss_pt (4 amplitudes x 4 pt0 centers,
# sigma fixed at 0.08 GeV/c) + 4 tilt_pz (4 alphas, pz_ref fixed at
# 5.0 GeV/c). Each entry: shape|amplitude|sigma|pt0|alpha|pz_ref
SHAPES=(
  "gauss_pt|0.05|0.08|0.2|0.0|5.0"
  "gauss_pt|0.05|0.08|0.4|0.0|5.0"
  "gauss_pt|0.05|0.08|0.6|0.0|5.0"
  "gauss_pt|0.05|0.08|0.8|0.0|5.0"
  "gauss_pt|0.10|0.08|0.2|0.0|5.0"
  "gauss_pt|0.10|0.08|0.4|0.0|5.0"
  "gauss_pt|0.10|0.08|0.6|0.0|5.0"
  "gauss_pt|0.10|0.08|0.8|0.0|5.0"
  "gauss_pt|0.20|0.08|0.2|0.0|5.0"
  "gauss_pt|0.20|0.08|0.4|0.0|5.0"
  "gauss_pt|0.20|0.08|0.6|0.0|5.0"
  "gauss_pt|0.20|0.08|0.8|0.0|5.0"
  "gauss_pt|0.30|0.08|0.2|0.0|5.0"
  "gauss_pt|0.30|0.08|0.4|0.0|5.0"
  "gauss_pt|0.30|0.08|0.6|0.0|5.0"
  "gauss_pt|0.30|0.08|0.8|0.0|5.0"
  "tilt_pz|0.0|0.0|0.0|0.05|5.0"
  "tilt_pz|0.0|0.0|0.0|0.10|5.0"
  "tilt_pz|0.0|0.0|0.0|0.20|5.0"
  "tilt_pz|0.0|0.0|0.0|0.30|5.0"
)

IDX=$((SLURM_ARRAY_TASK_ID - 1))
SPEC="${SHAPES[$IDX]}"
IFS='|' read -r SHAPE AMPL SIGMA PT0 ALPHA PZREF <<< "${SPEC}"

XSEC_OUT="${DOCS}/uq/closure/2d_xsec_1A_5iter_lgbm_closure_shape${SLURM_ARRAY_TASK_ID}.root"
LOG_OUT="${DOCS}/uq/closure/closure_shape${SLURM_ARRAY_TASK_ID}_$(date +%Y%m%d_%H%M%S).log"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq/closure"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] shape=${SHAPE} amplitude=${AMPL} sigma=${SIGMA} pt0=${PT0} alpha=${ALPHA} pz_ref=${PZREF}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python uq/closure/closure_truth_reweight.py \
  --shape       "${SHAPE}" \
  --amplitude   "${AMPL}" \
  --sigma       "${SIGMA}" \
  --pt0         "${PT0}" \
  --alpha       "${ALPHA}" \
  --pz-ref      "${PZREF}" \
  --out         "${XSEC_OUT}" \
  2>&1 | tee "${LOG_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
