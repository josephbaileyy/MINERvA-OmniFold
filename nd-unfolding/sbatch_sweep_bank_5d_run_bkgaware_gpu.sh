#!/bin/bash
#SBATCH --job-name=sweep5dBKGrun
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --array=1-169%48
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/sweep5dBKGrun_%a_%A.out --error=uq_4d/sweep5dBKGrun_%a_%A.err
# KNOWN_ISSUES #13 closing step (run), GPU-allocation variant (2026-07-14).
# Stage-2 5D re-unfold of each VERTICAL universe from bank_sweep_5d_bkgaware, now
# rebinning the CV background with that universe's w_bkg to recompute the measured
# purity down-weight (per-universe background). FAIL-CLOSED: no --allow-cv-background,
# so any universe whose bank lacks bkgw aborts (guards against a silent CV fallback).
# NON-DESTRUCTIVE outdir uq_5d/universe_sweep_bkgaware. ~15 min, ~15GB -> 1-GPU slot.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
# GEANT bands are owned by the detector direct-driver leg (matches validated
# methodology); this vertical bank-sweep leg runs the other 169 (GEANT filtered).
U=$(sed -n "${SLURM_ARRAY_TASK_ID}p" uq_4d/vertical_run_bkgaware.txt)
[[ -z "$U" ]] && exit 0
echo "[sweep-run-bkg] node=$(hostname) task=${SLURM_ARRAY_TASK_ID} universe=${U} start $(date -u '+%F %T UTC')"
python3 sweep_bank_5d.py --run --universe "$U" \
  --bankdir "${REPO}/nd-unfolding/bank_sweep_5d_bkgaware" \
  --outdir "${REPO}/nd-unfolding/uq_5d/universe_sweep_bkgaware" --iters 5
echo "[sweep-run-bkg] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
