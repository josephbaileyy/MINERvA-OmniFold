#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_boot_nw
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-50
#SBATCH --output=unfold_MEFHC_boot%a_%A.out
#SBATCH --error=unfold_MEFHC_boot%a_%A.err

# 2D OmniFold MEFHC 5-iter Poisson-weight bootstrap (Stage-1 UQ #1, MEFHC).
#
# Per-trial: full MEFHC 5-iter unfold with --bootstrap-seed N, ML
# random_state pinned via --seed 1 (matches seedscan trial 1). Pure
# Poisson variance across replicas; ML-noise component is measured
# independently by the seedscan and added in the final block-sum.
# Data and MC sub-RNGs inside the Python driver are independent
# (--bootstrap-seed vs --bootstrap-seed+1e7). LEGACY: kept for the
# original seeds 1-50 reference; production resubmission uses
# sbatch_unfold_2d_MEFHC_5iter_bootstrap_scaleup.sh (1-300 array).
#
# Validated baseline: lgbm 5-iter MEFHC @ 128 CPU = 13m24s (2026-05-21
# bench). 1 h walltime gives ~4x margin. Array tasks queue independently
# under regular QOS so several may dispatch in parallel; total wallclock
# = max(per-task elapsed) when the queue can accommodate all 50 in
# parallel, otherwise serialized in waves.
#
# Output: uq/2d_xsec_MEFHC_5iter_lgbm_boot${SLURM_ARRAY_TASK_ID}.root
# Covariance analysis: uq/analyze_uq.py.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
SEED=${SLURM_ARRAY_TASK_ID}
XSEC_OUT="${DOCS}/uq/negweight_boot/2d_xsec_MEFHC_5iter_lgbm_nw_boot${SEED}.root"

# Pin the root_6_28 env prefix explicitly: this array may be submitted from a
# sandboxed HOME (e.g. a background agent whose $HOME is not the real home), in
# which case setup_salloc_env.sh's $HOME-relative default misses the env and
# falls to the legacy by-name `conda activate root_6_28`, which no longer
# resolves under the 2026-07-02 base -> EnvironmentNameNotFound. Hardcode the
# canonical prefix so env sourcing is submit-env-independent.
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] seed:  ${SEED}"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile        "${OMNIFILE}" \
  --mcfile          "${FLUX_MC}" \
  --iters           5 \
  --use-weights \
  --estimator       lgbm \
  --bootstrap-seed  "${SEED}" \
  --seed            1 \
  --bkg-mode        negweight \
  --out             "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
