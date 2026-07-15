#!/bin/bash
#SBATCH --job-name=pet_clat_bkgsub
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=2
#SBATCH --cpus-per-task=64
#SBATCH --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=pet/pet_clat_%x_%j.out --error=pet/pet_clat_%x_%j.err
# PET-native 5D lateral (detector) block on the CORRECTED bkgsub target.
# Frozen-cloud transfer (reco-weight ratios) via the event-aligned 5D join
# (pet_lateral_band_5d.py); CORRECTION vs the old 2026-06-29 product = the
# corrected bkgsub weights + bkgsub point cloud (+ bkgaware omnifile, per user).
# ROOT+numpy (no GPU compute); gpu_shared is used only for the CPU+RAM (CPU
# allocation exhausted). 2 GPUs -> ~114G RAM (docstring estimate ~120G).
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
cd "$REPO/nd-unfolding"
source "$REPO/setup_salloc_env.sh"
ROOTPY="${ROOT628_PREFIX}/bin/python3"

PC="${PET_PC:-of_inputs_pc_fullcloud_bkgsub_5d.npz}"
WSOURCE="${PET_W_SOURCE:-of_inputs_5d.npz}"
WEIGHTS="${PET_NOM_WEIGHTS:-products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz}"
OMNI="${PET_OMNI:-runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root}"
OUTNPZ="${PET_CLAT_OUT:-products/pet/bkgsub/pet_clateral_bkgsub_5d.npz}"

for f in "$PC" "$WEIGHTS" "$OMNI" "$WSOURCE"; do
  [[ -s "$f" ]] || { echo "[FAIL] missing input: $f" >&2; exit 2; }
done

echo "[clat] start $(date -u +%FT%TZ) on $(hostname)"
echo "[clat] pc=$PC weights=$WEIGHTS omni=$OMNI -> $OUTNPZ"
"$ROOTPY" pet_lateral_band_5d.py \
  --pc "$PC" --w-source "$WSOURCE" --weights "$WEIGHTS" \
  --omnifile "$OMNI" --combined "" --out-npz "$OUTNPZ"
echo "[clat] done $(date -u +%FT%TZ)"
ls -lh "$OUTNPZ" 2>/dev/null || true
