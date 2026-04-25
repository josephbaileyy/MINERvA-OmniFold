#!/bin/bash
#SBATCH --job-name=baseline_flux
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=baseline_flux_%a_%A.out
#SBATCH --error=baseline_flux_%a_%A.err

# Per-playlist baseline event loop used only to regenerate the histogram-based
# MC outputs that carry pTmu_reweightedflux_integrated.
#
# Why separate from runEventLoopOmniFold:
#   runEventLoopOmniFold writes only TTrees + metadata for OmniFold and does
#   not write the standard ExtractCrossSection histogram suite. The baseline
#   runEventLoop path is the one that writes pTmu_reweightedflux_integrated.
#
# Why per-playlist:
#   the normalization audit now shows the full-MEHFC result is currently using
#   a legacy 1A-derived flux histogram. To test playlist dependence, each
#   playlist needs its own runEventLoopMC_<PL>.root so the per-playlist flux
#   integrals can be compared and POT-weighted afterward.
#
# Outputs:
#   Documents/baseline_flux/runEventLoopMC_<PL>.root
#   Documents/baseline_flux/runEventLoopData_<PL>.root
#
# Runtime/memory:
#   Same code family and dataset scale as the prior OmniFold event-loop array.
#   2 CPU / 8 GB / 12 h is conservative for the largest playlists.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

cd /pscratch/sd/j/josephrb/MINERvA101
module load python
conda activate root_6_28
source OmniFold/unbinned_unfolding/build/setup.sh
source opt/bin/setup.sh

OUTDIR="/pscratch/sd/j/josephrb/MINERvA101/Documents/baseline_flux"
WORKDIR="${OUTDIR}/work_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="/pscratch/sd/j/josephrb/MINERvA101/Doc_tmp/${PL}_Data.txt"
MC_MANIFEST="/pscratch/sd/j/josephrb/MINERvA101/Doc_tmp/${PL}_MC.txt"

export PYTHONUNBUFFERED=1

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] outdir:  ${OUTDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest  : ${MC_MANIFEST}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

runEventLoop "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL_MC="${OUTDIR}/runEventLoopMC_${PL}.root"
FINAL_DATA="${OUTDIR}/runEventLoopData_${PL}.root"

mv -v runEventLoopMC.root "${FINAL_MC}"
mv -v runEventLoopData.root "${FINAL_DATA}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final MC:   ${FINAL_MC}"
echo "[sbatch] final Data: ${FINAL_DATA}"
