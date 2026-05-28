#!/bin/bash
#SBATCH --job-name=unfold_MEFHC
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=24:00:00
#SBATCH --output=unfold_MEFHC_%j.out
#SBATCH --error=unfold_MEFHC_%j.err

# 2D OmniFold unfold on the merged 12-playlist MEFHC ROOT.
# Designed to run as afterok dependency of sbatch_hadd_MEFHC.sh.
# Observed ~3h50m per iter on 128 CPUs (job 53012901 reached only iter 2
# in 9h31m before being scancelled). 24h wallclock gives ~5h/iter headroom
# for the full 5-iter run.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
XSEC_OUT="${DOCS}/2d_crossSection_omnifold_MEFHC_5iter.root"

source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE}" \
  --mcfile   "${FLUX_MC}" \
  --iters 5 \
  --use-weights \
  --out      "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
