#!/bin/bash
#SBATCH --job-name=nndumpfps5dxps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=04:00:00
#SBATCH --output=nndumpfps5dxps_%j.out --error=nndumpfps5dxps_%j.err
# FPS Stage 1 (extended phase space): GBDT 5D scalar inputs WITH the theta_mu<20deg
# truth gate LIFTED (--full-phase-space), matching the extended PET pc dump
# (of_inputs_pc_fps_xps.npz). Independent of the PET pc dump (reads the omnifile
# directly) so this can run in parallel with sbatch_npz_pc_fps_xps.sh. Same standard
# 65856-bin grid (theta lives inside the existing pt/pz rectangle -- no grid change).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
[[ -s of_inputs_5d_fps_xps.npz ]] && { echo "skip (exists)"; exit 0; }
python3 nn_dump_inputs.py \
  --omnifile "${REPO}/nd-unfolding/runEventLoopOmniFold_PC_FPS_MEFHC.root" \
  --axes eavail,q3,W --full-phase-space --out of_inputs_5d_fps_xps.npz
