#!/bin/bash
#SBATCH --job-name=pcproj_fc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=02:00:00
#SBATCH --output=pcproj_fc_%j.out --error=pcproj_fc_%j.err
# Stage 5: re-run the truth-cloud projection on the FULL spectrum -- new npz
# (filled miss clouds) + retrained weights. OMNI points at the fullcloud MEFHC
# file (row-aligned with the new npz for the MC_W assert). Products go to a
# separate fullcloud/ dir so the baseline products are preserved for comparison.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
mkdir -p products/pet/fullcloud
export PCPROJ_PC="${REPO}/nd-unfolding/of_inputs_pc_fullcloud.npz"
export PCPROJ_WEIGHTS="${REPO}/nd-unfolding/products/pet/pet_weights_fullcloud.npz"
export PCPROJ_OMNI="${REPO}/nd-unfolding/runEventLoopOmniFold_PC_MEFHC_fullcloud.root"
export PCPROJ_OUTDIR="${REPO}/nd-unfolding/products/pet/fullcloud"
for f in "$PCPROJ_PC" "$PCPROJ_WEIGHTS" "$PCPROJ_OMNI"; do
  [ -s "$f" ] || { echo "[proj] MISSING $f"; exit 1; }
done
echo "[proj] full-spectrum projection $(date -u +%T)"
python3 pet/pointcloud_projection.py
echo "[proj] done $(date -u +%T); products in products/pet/fullcloud/"
