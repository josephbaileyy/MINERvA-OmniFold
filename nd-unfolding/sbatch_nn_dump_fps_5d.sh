#!/bin/bash
#SBATCH --job-name=nndumpfps5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=04:00:00
#SBATCH --output=nndumpfps5d_%j.out --error=nndumpfps5d_%j.err
# FPS GBDT 5D scalar inputs (of_inputs_5d_fps_full.npz) for the 3-prior envelope's
# CHEAP re-unfolding leg (LightGBM re-unfolds from each prior -> correct data-
# reconvergence structure, transferred onto the PET headline). Standard edges (matches
# the 65856 PET grid); FPS-ness is in the omnifile (denom includes the reco-inefficient
# extrapolation region). NO --full-phase-space (keep the theta gate, matching the PET
# pc dump).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
[[ -s of_inputs_5d_fps_full.npz ]] && { echo "skip (exists)"; exit 0; }
python3 nn_dump_inputs.py \
  --omnifile "${REPO}/nd-unfolding/runEventLoopOmniFold_PC_FPS_MEFHC.root" \
  --axes eavail,q3,W --out of_inputs_5d_fps_full.npz
