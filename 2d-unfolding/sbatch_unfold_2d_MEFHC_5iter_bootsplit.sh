#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_bootsplit
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-200%30
#SBATCH --output=unfold_MEFHC_bootsplit_%a_%A.out
#SBATCH --error=unfold_MEFHC_bootsplit_%a_%A.err

# Split-stream bootstrap (2026-05-31): re-run the Poisson bootstrap fluctuating
# ONLY the data weights (STREAM=data) or ONLY the MC weights (STREAM=mc), to
# report the data-statistical and MC-statistical covariances separately
# (--bootstrap-streams). Streams are independent, so Cov(data)+Cov(mc) should
# reconstruct the joint 'both' covariance (uq/bootstrap_MEFHC_300) -- a
# decomposition AND a closure check. Motivates the open question in
# technote App B sec:rank (why our stat block is 2.5x smaller than the
# paper's StatOnlyCov: OmniFold efficiency vs the paper's stat definition).
#
# ML seed pinned to 1 (matches the 300-set 'both' campaign) so the variance is
# pure Poisson. Submit twice:
#   sbatch --export=ALL,STREAM=data sbatch_unfold_2d_MEFHC_5iter_bootsplit.sh
#   sbatch --export=ALL,STREAM=mc   sbatch_unfold_2d_MEFHC_5iter_bootsplit.sh
# Output: uq/boot_${STREAM}/2d_xsec_MEFHC_5iter_lgbm_boot${SEED}.root
# Rollup: uq/analyze_uq.py --glob 'boot_${STREAM}/2d_xsec_*_boot*.root' \
#           --outdir boot_${STREAM} --out-root uq_covariance_boot${STREAM}200.root

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

STREAM=${STREAM:?must set STREAM=data or STREAM=mc via --export=ALL,STREAM=...}
case "${STREAM}" in data|mc) ;; *) echo "bad STREAM=${STREAM}"; exit 1;; esac

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
SEED=${SLURM_ARRAY_TASK_ID}
OUTDIR="${DOCS}/uq/boot_${STREAM}"
XSEC_OUT="${OUTDIR}/2d_xsec_MEFHC_5iter_lgbm_boot${SEED}.root"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk (seed=${SEED})"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} task=${SLURM_ARRAY_TASK_ID} stream=${STREAM}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')  seed=${SEED}  out=${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile          "${OMNIFILE}" \
  --mcfile            "${FLUX_MC}" \
  --iters             5 \
  --use-weights \
  --estimator         lgbm \
  --bootstrap-seed    "${SEED}" \
  --bootstrap-streams "${STREAM}" \
  --seed              1 \
  --out               "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
