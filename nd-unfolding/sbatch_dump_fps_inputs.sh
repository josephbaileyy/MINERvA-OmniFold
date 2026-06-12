#!/bin/bash
#SBATCH --job-name=dumpfps_in
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=04:00:00
#SBATCH --output=uq_fps/dumpfps_in_%A.out --error=uq_fps/dumpfps_in_%A.err

# of_inputs npz for the FPS bootstrap (C_stat) + split-seedscan (C_ML) stages:
# the ROOT-free input dump on the FPS extended grid (same flags as the sweep CV).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"

PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

[[ -s of_inputs_fps.npz ]] && { echo "[sbatch] SKIP: of_inputs_fps.npz exists"; exit 0; }
python3 nn_dump_inputs.py \
    --omnifile runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root \
    --axes "" --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
    --out of_inputs_fps.npz
