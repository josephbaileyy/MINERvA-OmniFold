#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_boot
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-300%30
#SBATCH --output=unfold_MEFHC_boot%a_%A.out
#SBATCH --error=unfold_MEFHC_boot%a_%A.err

# Stage-2 bootstrap, fixed ML seed (2026-05-27 reissue): 300 Poisson-
# weight replicas. ML classifier random_state pinned to 1 (matches
# seedscan trial 1) so variance across replicas is pure Poisson —
# stat and ML-noise components are now independently estimated and
# non-overlapping. Previous run (sbatch 53327775) varied --seed
# together with --bootstrap-seed and double-counted ML stochasticity
# into the bootstrap cov; those ROOTs are sidelined under
# uq/bootstrap_MEFHC_300_contaminated_seedvarying/ for forensics.
#
# Per-task wall ~ 13 min at 128 CPU (lgbm). 30 concurrent cap; total
# wall ~10 waves * 15 min = ~2.5 h.
#
# Output: uq/2d_xsec_MEFHC_5iter_lgbm_boot${SLURM_ARRAY_TASK_ID}.root
# Rollup: uq/analyze_uq.py (existing analyzer auto-detects all
# 2d_xsec_MEFHC_5iter_lgbm_boot*.root files).

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
SEED=${SLURM_ARRAY_TASK_ID}
XSEC_OUT="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_boot${SEED}.root"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk (seed=${SEED})"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] seed:  ${SEED}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile        "${OMNIFILE}" \
  --mcfile          "${FLUX_MC}" \
  --iters           5 \
  --use-weights \
  --estimator       lgbm \
  --bootstrap-seed  "${SEED}" \
  --seed            1 \
  --out             "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
