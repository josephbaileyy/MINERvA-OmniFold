#!/bin/bash
#SBATCH --job-name=uthfps_dump
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=64G --time=04:00:00
#SBATCH --array=0-7
#SBATCH --output=uq_fps/uthfps_dump_%a_%A.out --error=uq_fps/uthfps_dump_%a_%A.err

# FPS unified-throw ratio bank (mandatory per FPS_PILOT.md): per-event universe/CV
# ratios from the merged FPS _universes_full file, on the 2D extended grid with the
# FPS truth gate. Miss-row ratios are pinned to 1.0 (KNOWN_ISSUES #12: the merged
# FPS file is pre-fix; pinning equals the post-fix event-loop CV proxies).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"

PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

python3 unified_throw.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 \
    --omnifile runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root \
    --bankdir bank_uthrow_fps --axes "" --full-phase-space \
    --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}"
