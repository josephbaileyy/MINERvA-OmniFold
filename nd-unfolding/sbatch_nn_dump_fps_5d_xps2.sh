#!/bin/bash
#SBATCH --job-name=nndumpfps5dxps2
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=04:00:00
#SBATCH --output=nndumpfps5dxps2_%j.out --error=nndumpfps5dxps2_%j.err
# FPS Stage 2: GBDT 5D scalar inputs with the theta_mu gate lifted (Stage 1) AND the
# PT_EXT/PZ_EXT extended reporting grid (Stage 2). Independent of the PET pc dump
# (reads the omnifile directly) so this can run in parallel with
# sbatch_npz_pc_fps_xps2.sh. Expect "[INFO] flux remapped to 15 pT bins".
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
[[ -s of_inputs_5d_fps_xps2.npz ]] && { echo "skip (exists)"; exit 0; }
PT_EXT="0,0.07,0.15,0.25,0.33,0.4,0.47,0.55,0.7,0.85,1.0,1.25,1.5,2.5,4.5,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"
python3 nn_dump_inputs.py \
  --omnifile "${REPO}/nd-unfolding/runEventLoopOmniFold_PC_FPS_MEFHC.root" \
  --axes eavail,q3,W --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
  --out of_inputs_5d_fps_xps2.npz
