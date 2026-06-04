#!/bin/bash
#SBATCH --job-name=unfold4d_val
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=96G --time=01:30:00
#SBATCH --output=unfold4d_val_%j.out --error=unfold4d_val_%j.err
# Validate the nd --universe q3-swap path on ONE lateral band (MuonResolution:0)
# before committing the full 187-universe sweep. Lateral => exercises the pt/pz+q3
# swap; a finite total xsec near CV with q3 actually shifted = the path is correct.
set -eo pipefail
export PYTHONUNBUFFERED=1; export OMP_NUM_THREADS=32
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
ND="${REPO}/nd-unfolding"; cd "${ND}"; mkdir -p uq_4d/universe_sweep
python3 unfold_nd_omnifold_unbinned.py \
  --omnifile runEventLoopOmniFold_4D_MEFHC_universes_full.root \
  --mcfile ${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root \
  --axes eavail,q3 --iters 5 --use-weights --estimator lgbm --seed 42 --verbose \
  --universe MuonResolution:0 \
  --out uq_4d/universe_sweep/4d_xsec_MEFHC_5iter_lgbm_uni_full_MuonResolution_0.root
echo "[validate] MuonResolution:0 unfold complete"
