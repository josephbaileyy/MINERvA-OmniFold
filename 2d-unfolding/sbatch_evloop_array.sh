#!/bin/bash
#SBATCH --job-name=evloop
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-11
#SBATCH --output=evloop_%a_%A.out
#SBATCH --error=evloop_%a_%A.err

# Per-playlist full-stats event loop for all ME FHC playlists except 1A
# (1A already has runEventLoopOmniFold_1A.root from the initial 2D pass).
#
# The C++ binary writes to a hardcoded filename "runEventLoopOmniFold.root"
# in its CWD. Each array task runs in its own work directory to avoid the
# 11 tasks stomping on each other's output, then moves the result to a
# uniquely-named file in Documents/ once complete.
#
# util::GetPlaylist infers the playlist from the first event's run number
# and applies playlist-specific flux/calibration globally. Running per
# playlist (rather than a combined manifest) ensures each dataset gets the
# correct corrections; the 12 outputs are later hadd-merged for OmniFold.
#
# Runtime: 1A on 41 MC files took ~1-2h. Largest playlists (1D, 1M) are
# 3-4x that. 12h walltime is generous.
# Memory: event loop is single-pass over TTrees; 1A peaked well under 4 GB.
# 8 GB gives headroom for larger playlists.

set -eo pipefail

PLAYLISTS=(1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
# SLURM_ARRAY_TASK_ID is 1-indexed; bash arrays are 0-indexed
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/2d-unfolding/evloop_work_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest  : ${MC_MANIFEST}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/2d-unfolding/runEventLoopOmniFold_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
