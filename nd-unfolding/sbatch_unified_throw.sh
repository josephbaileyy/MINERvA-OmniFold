#!/bin/bash
#SBATCH --job-name=unithrow
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=unithrow_%j.out
#SBATCH --error=unithrow_%j.err

# prepub #1: unified-throw vs block-sum cross-check via the superposition test.
# Phase 1 (dump): one pass over the 120 GB 3D universes omnifile to extract CV
# inputs + the vertical-band universe weight columns. Phase 2 (analyze): CV +
# single-band(+1s) + joint unfolds -> cross-term residual Delta_AB-(Delta_A+Delta_B).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

OMNI="${REPO}/3d-unfolding/runEventLoopOmniFold_MEFHC_3D_universes_full.root"
BANDS="MaCCQE,2p2h,MaRES"

echo "[unithrow] dump start $(date -u '+%F %T UTC')"
python3 compare_unified_throw.py --dump --omnifile "${OMNI}" --bands "${BANDS}" \
    --out combo_inputs_3d.npz
echo "[unithrow] analyze start $(date -u '+%F %T UTC')"
python3 compare_unified_throw.py --analyze --npz combo_inputs_3d.npz --iters 5 \
    --cv "${REPO}/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root"
echo "[unithrow] done $(date -u '+%F %T UTC')"
