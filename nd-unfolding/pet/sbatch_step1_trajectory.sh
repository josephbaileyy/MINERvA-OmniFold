#!/bin/bash
#SBATCH --job-name=fe_step1_traj
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal/logs/fe_traj_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal/logs/fe_traj_%j.err
#
# Per-iteration trajectory of the step-1 classifier ratio. Answers the question Joseph put at the top
# of the queue on 2026-08-09: step 1's final increment is wrong-signed (0.648331 where ~1.16 is
# required), an increment moving AGAINST its target is a different failure from under-application,
# and it probably has a findable cause.
#
# The discriminator is iteration 0, where weights_push == 1 and the ideal step-1 ratio's
# reco-weighted mean is EXACTLY R = 1.1240802949941018:
#   ~1.124 -> step 1 starts correct, the defect is in the iteration dynamics
#   ~0.65  -> step 1 is broken before any feedback exists, defect is its own normalization/training
# Those point at disjoint code, which is why this is worth a job rather than more reading.
#
# GATED: reproduces the three committed STEP1_DECOMPOSITION numbers before printing any trajectory.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
JOB="${SLURM_JOB_ID:-nojob}"
OUT="${PET}/fullevent_nominal/STEP1_TRAJECTORY.slurm-${JOB}.json"
RUNLOG="${PET}/fullevent_nominal/logs/step1_traj_${JOB}.log"

mkdir -p "${PET}/fullevent_nominal/logs"
module load tensorflow/2.15.0
export MNV_REPO="$REPO"
cd "$PET"

# Whole stream to a file, then filter READS of it. Never piped through tail at write time (BEN-026).
python3 -u step1_increment_trajectory.py \
  --weights "${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz" \
  --decomposition-receipt "${PET}/fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json" \
  --json "$OUT" \
  >>"$RUNLOG" 2>&1

echo "[traj] rc=0  json=${OUT}  log=${RUNLOG}"
grep -E "VERDICT|GATE|^  [0-9]" "$RUNLOG" | tail -20 || true
