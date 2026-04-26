#!/bin/bash
#SBATCH --job-name=unfold2d_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=36:00:00
#SBATCH --output=unfold2d_full_%j.out
#SBATCH --error=unfold2d_full_%j.err

# Full-statistics 2D OmniFold run on combined ME FHC dataset.
#
# Input: 2d-unfolding/runEventLoopOmniFold_MEHFC.root (hadd of 12 playlists,
#   2.17 GB, 32.8M truth / 28.3M signal-reco / 5.7M data entries).
# Iters: 5 (convergence confirmed on playlist 1A: 5-iter within 0.07% of
#   10-iter total xsec, 2.9% per-bin RMS shape deviation).
# Output: 2d-unfolding/2d_crossSection_omnifold_MEHFC_5iter.root
#
# Resource sizing, relative to playlist 1A 5-iter baseline (1h45m,
# 8 GB on shared QOS):
#   - Data scale-up: ~80x more events per training set.
#   - GBT training is ~O(n log n); scaling factor ~107x per classifier.
#   - Conservative runtime estimate: ~10-24h; 36h walltime gives margin.
#   - Memory: peak arrays ~2 GB; sklearn overhead can push to ~8-12 GB.
#     32 GB chosen for headroom.
#   - CPUs: sklearn GBT is single-threaded per tree; 4 cores is a
#     modest boost in case any stage of the pipeline parallelizes,
#     with minimal extra billing.

set -eo pipefail

export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

OMNIFILE="runEventLoopOmniFold_MEHFC.root"
MCFILE="baseline_flux/runEventLoopMC_MEHFC.root"
OUT="2d_crossSection_omnifold_MEHFC_5iter.root"
ITERS=5

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] input:   ${OMNIFILE}"
echo "[sbatch] mcfile:  ${MCFILE}  (POT(data)-weighted 12-playlist flux)"
echo "[sbatch] iters:   ${ITERS}"
echo "[sbatch] out:     ${OUT}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# srun omitted — --ntasks=1 doesn't need it, and it triggers NERSC's
# SLURM_CPUS_PER_TASK / SLURM_TRES_PER_TASK conflict on shared QOS.
python unfold_2d_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" \
    --mcfile "${MCFILE}" \
    --iters "${ITERS}" \
    --use-weights \
    --out "${OUT}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final: ${REPO}/2d-unfolding/${OUT}"
