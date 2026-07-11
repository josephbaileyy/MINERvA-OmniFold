#!/bin/bash
#SBATCH --job-name=fpsreunf5dxps2
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=06:00:00
#SBATCH --output=fpsreunf5dxps2_%j.out --error=fpsreunf5dxps2_%j.err
# Step 3 (Stage 2: extended reporting grid / pilot catch bins): PET-headline GBDT-prior
# envelope re-run on the theta-lifted + PT_EXT/PZ_EXT full-stats PET weights, using the
# xps2-aligned GBDT/PET-pc/W-source inputs. Writes products/pet/fps_envelope_5d_xps2/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps2.npz \
    --pet-pc of_inputs_pc_fps_xps2.npz --pet-weights products/pet/pet_weights_fps_xps2.npz \
    --pet-wsource of_inputs_5d_fps_xps2_wsource.npz --full-phase-space \
    --outdir products/pet/fps_envelope_5d_xps2 --iters 5 --seed 1000
