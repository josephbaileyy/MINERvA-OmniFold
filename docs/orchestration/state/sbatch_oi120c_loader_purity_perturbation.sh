#!/bin/bash
#SBATCH --job-name=laned_legc
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=06:00:00
#SBATCH --nice=1000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/lane-d-oi120/legc_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/lane-d-oi120/legc_%j.err
# OI-120(c): purity of event_reco through the PRODUCTION loader, by perturbation.
#
# A WHOLE CPU NODE, FOR MEASURED REASONS. The NPZ is 29.0 GB decompressed (part_gen
# 11.8 GB, part_reco 7.1 GB, reco_view/reco_time 2.4 GB each -- measured from the .npy
# headers, not estimated), and the loader's own comment warns a full 49.2M cloud pass
# "would spike tens of GB". Six sequential loader passes with gc between, so the peak is
# one pass; a shared-QOS fraction would risk an OOM two hours in.
#
# CPU-ONLY AND NICED. The Gate-5 extraction family (56936015) is GPU-bound under Priority
# contention and is the critical path. This job takes no GPU and carries nice=1000.
#
# READ-ONLY w.r.t. the campaign: reads the NPZ, writes only its own log under a lane-D path.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
OUT="/pscratch/sd/j/josephrb/lane-d-oi120"
mkdir -p "$OUT"
cd "$REPO"
source ./setup_salloc_env.sh
export PYTHONUNBUFFERED=1
# BEN-026: whole stream to a file; never truncate at write time.
python3 "$OUT/legc_purity.py" > "$OUT/legc_full_${SLURM_JOB_ID}.txt" 2>&1
echo "[legc] rc=$? wrote $OUT/legc_full_${SLURM_JOB_ID}.txt"
