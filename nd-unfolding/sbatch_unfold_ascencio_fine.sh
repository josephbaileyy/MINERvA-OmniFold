#!/bin/bash
#SBATCH --job-name=asc_fine
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=08:00:00
#SBATCH --output=asc_fine_%j.out --error=asc_fine_%j.err

# Ascencio fine-binned comparison, stage 1 (OPEN_ITEMS item 2 residual):
# CV re-unfold on the UNION of the Ascencio 2110.13372 44-cell edges
# (their per-q3-column E_avail binnings tile this rectangular union grid, so
# their cells are exact merges of ours). q3/E_avail catch bins keep the
# Jacobian identity. Stage 2 (a 187-universe sweep on this binning, for the
# full-covariance chi^2) is a separate decision -- this run gives the
# bin-identical CV comparison with their published covariance.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"

EA="0,0.04,0.08,0.12,0.16,0.24,0.32,0.34,0.4,0.6,0.8,1.0,1.2,100"
Q3="0,0.2,0.3,0.4,0.6,0.9,1.2,100"
OUT="products/4d/xsec_4d_MEFHC_ascencio_fine.root"
[[ -s "${OUT}" ]] && { echo "skip (exists)"; exit 0; }

python3 unfold_nd_omnifold_unbinned.py \
  --omnifile runEventLoopOmniFold_5D_MEFHC_universes_full.root \
  --mcfile "${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root" \
  --axes "eavail,q3" \
  --edges "eavail:${EA};q3:${Q3}" \
  --iters 5 --use-weights --estimator lgbm --seed 42 \
  --out "${OUT}"
