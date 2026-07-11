#!/bin/bash
#SBATCH --job-name=bkgnw
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=08:00:00
#SBATCH --output=HANDOFF_bkg_negweight/runs/bkgnw_%x_%j.out
#SBATCH --error=HANDOFF_bkg_negweight/runs/bkgnw_%x_%j.err

# 2D purity-vs-negweight background-subtraction comparison on the merged MEFHC
# omnifile, FAST hist estimator. Method comparison only (estimator cancels in
# the mode-to-mode ratio); NOT byte-comparable to the exact-estimator headline
# (frozen benchmark sigma_tot = 3.073e-38). Parameterized by:
#   MODE : purity | negweight        (--bkg-mode)
#   SEED : integer                   (--seed, matched across modes so GBDT
#                                      stochasticity is identical and the
#                                      mode-to-mode difference isolates the
#                                      background treatment)
# Submit via: sbatch --export=ALL,MODE=...,SEED=... sbatch_bkg_negweight_hist.sh
set -eo pipefail
export PYTHONUNBUFFERED=1
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
: "${MODE:?set MODE=purity|negweight}"
: "${SEED:?set SEED=<int>}"
EST="${ESTIMATOR:-hist}"   # hist (fast, default) | exact (headline backend)
XSEC_OUT="${DOCS}/HANDOFF_bkg_negweight/runs/2d_xsec_${MODE}_seed${SEED}_${EST}5.root"

source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} mode=${MODE} seed=${SEED} est=${EST}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] xsec out: ${XSEC_OUT}"
python --version

python -u unfold_2d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE}" \
  --mcfile   "${FLUX_MC}" \
  --iters 5 \
  --use-weights \
  --estimator "${EST}" \
  --bkg-mode "${MODE}" \
  --seed "${SEED}" \
  --out      "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
