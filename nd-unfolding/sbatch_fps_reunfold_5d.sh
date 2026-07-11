#!/bin/bash
#SBATCH --job-name=fpsreunf5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=06:00:00
#SBATCH --output=fpsreunf5d_%j.out --error=fpsreunf5d_%j.err
# Step 3 (correct): GBDT re-unfolds FPS from 3 priors (data reconvergence) -> per-bin
# model-dependence fraction -> fractional transfer onto the PET headline. 3 LightGBM
# nd unfolds at ~33M events; writes products/pet/fps_envelope_5d/fps_modeldep_cov_5d.root.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 fps_gbdt_prior_reunfold_5d.py --iters 5 --seed 1000
