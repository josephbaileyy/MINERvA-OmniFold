#!/bin/bash
#SBATCH --job-name=unfold_MEHFC_seed
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --array=1-10
#SBATCH --output=unfold_MEHFC_seed%a_%A.out
#SBATCH --error=unfold_MEHFC_seed%a_%A.err

# 2D OmniFold MEHFC 5-iter ML-stochasticity seed scan (Phase-18.2 pipeline,
# HistGBT estimator).
#
# Motivated by advisor's 2026-05-19 request: chi^2-vs-paper uses the paper's
# covariance, so any uncertainty that differs between the two methods is
# excluded. The next step is to characterize uncertainties that ARE method-
# dependent; the most distinct is the stochastic nature of ML training.
#
# Each trial reruns the production 5-iter MEHFC unfold with HistGBT
# (--estimator hist) and a different seed, so the random_state on the
# step1 classifier, step2 classifier, and step1 miss regressor are
# independent and reproducible. Measured per-trial walltime on the
# validation run: 17m33s at 32 CPUs. 1h walltime budget gives 3x margin.
# Array tasks queue independently under regular QOS so all 10 may dispatch
# in parallel.
#
# Output: seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed${SLURM_ARRAY_TASK_ID}.root
# Spread analysis: 2d-unfolding/seedscan/analyze_seedscan.py.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEHFC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEHFC.root"
SEED=${SLURM_ARRAY_TASK_ID}
XSEC_OUT="${DOCS}/seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed${SEED}.root"

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/seedscan"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] seed:  ${SEED}"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator hist \
  --seed      "${SEED}" \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
