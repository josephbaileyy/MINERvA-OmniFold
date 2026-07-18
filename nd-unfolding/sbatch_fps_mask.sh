#!/bin/bash
#SBATCH --job-name=cfpsmask
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=2 --mem=8G --time=00:15:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=active_universe_5d/fps/covariance/cfpsmask_%A.out
#SBATCH --error=active_universe_5d/fps/covariance/cfpsmask_%A.err
# Tiny owner-correct job: compute + commit the 266/285 FPS reported mask from the 26KB CV and lock
# its fingerprint construction to the verifier-canonical 23b2a2f4... value. Read-only wrt data.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
mkdir -p active_universe_5d/fps/covariance
python3 fps_reported_mask.py \
    --cv uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root \
    --out active_universe_5d/fps/covariance/fps_reported_mask.json
