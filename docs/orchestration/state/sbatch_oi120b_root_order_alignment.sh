#!/bin/bash
#SBATCH --job-name=laned_legb
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=04:00:00
#SBATCH --nice=1000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/lane-d-oi120/legb_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/lane-d-oi120/legb_%j.err
# OI-120(b) / OI-22 leg (b): event-by-event ORDER proof, G2 NPZ vs source ROOT.
#
# CPU-ONLY AND NICED ON PURPOSE. The Gate-5 extraction family (56936015) is GPU-bound
# under Priority contention and is the critical path; this job takes no GPU slot and
# carries nice=1000 so it cannot outrank anything. Verified, not assumed: the G2 dump
# that produced this NPZ ran on the same --constraint=cpu --qos=shared pool.
#
# READ-ONLY with respect to the campaign: opens the merged ROOT and the NPZ, writes
# only its own log and receipt under a path lane D owns.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
OUT="/pscratch/sd/j/josephrb/lane-d-oi120"
mkdir -p "$OUT"
cd "$REPO"
source ./setup_salloc_env.sh
export PYTHONUNBUFFERED=1
# Never pipe a diagnostic run through tail/head -- BEN-026. Whole stream to a file.
python3 "$OUT/legb_align.py" > "$OUT/legb_full_${SLURM_JOB_ID}.txt" 2>&1
echo "[legb] rc=$? wrote $OUT/legb_full_${SLURM_JOB_ID}.txt"
