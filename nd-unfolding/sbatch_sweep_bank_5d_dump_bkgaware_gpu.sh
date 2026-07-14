#!/bin/bash
#SBATCH --job-name=sweep5dBKGdump
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=0-15
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/sweep5dBKGdump_%a_%A.out --error=uq_4d/sweep5dBKGdump_%a_%A.err
# KNOWN_ISSUES #13 closing step (dump), GPU-allocation variant (2026-07-14).
# Re-bank the 175 VERTICAL universes from the BKG-AWARE omnifile, now capturing the
# per-universe w_bkg_<band>_<idx> weight columns (-> {tag}_bkgw.npy) + CV bkg_cols in
# cv.npz. NON-DESTRUCTIVE: distinct bankdir bank_sweep_5d_bkgaware (the old CV-frozen
# bank_sweep_5d is empty anyway). Peak MaxRSS was 72GB at 8 groups (dominated by
# python-list per-universe weight accumulation, scales with universes/group); 16
# groups halves that to ~36GB -> fits a 1-GPU shared slot (~64GB), which schedules
# FAR better under fairshare than 2-GPU slots. Bank output identical (ngroups only
# repartitions; cv.npz stays group-0-only). ~25-30 min/group.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
OMNI="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
BANKDIR="${REPO}/nd-unfolding/bank_sweep_5d_bkgaware"; mkdir -p "${BANKDIR}"
echo "[sweep-dump-bkg] node=$(hostname) group=${SLURM_ARRAY_TASK_ID} start $(date -u '+%F %T UTC')"
python3 sweep_bank_5d.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 16 \
  --omnifile "${OMNI}" --bankdir "${BANKDIR}"
echo "[sweep-dump-bkg] group=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
