#!/bin/bash
#SBATCH --job-name=fpsreunf5dxps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=06:00:00
#SBATCH --output=fpsreunf5dxps_%j.out --error=fpsreunf5dxps_%j.err
# Step 3 (extended phase space): PET-headline GBDT-prior envelope re-run on the
# theta-lifted (--full-phase-space) full-stats PET weights, using the xps-aligned
# GBDT/PET-pc/W-source inputs. Writes products/pet/fps_envelope_5d_xps/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps.npz \
    --pet-pc of_inputs_pc_fps_xps.npz --pet-weights products/pet/pet_weights_fps_xps.npz \
    --pet-wsource of_inputs_5d_fps_xps_wsource.npz --full-phase-space \
    --outdir products/pet/fps_envelope_5d_xps --iters 5 --seed 1000
