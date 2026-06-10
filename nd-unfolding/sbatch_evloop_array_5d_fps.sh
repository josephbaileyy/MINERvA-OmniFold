#!/bin/bash
#SBATCH --job-name=evloop5d_fps
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=2-12
#SBATCH --output=evloop5d_fps_%a_%A.out
#SBATCH --error=evloop5d_fps_%a_%A.err

# FULL-PHASE-SPACE campaign step 1: per-playlist CV event loop for the
# remaining 11 MEFHC playlists (1A done by job 54232780). Same 5D dump as
# sbatch_evloop_array_5d.sh but with MNV101_FULL_PHASE_SPACE=1 (truth muon
# kinematic cuts off, fiducial kept; reco selection unchanged).
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_5D_FPS_${PL}.root.
# Decision memo: FPS_PILOT.md (GO, two-tier reporting).

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export MNV101_FULL_PHASE_SPACE=1

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_fps_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL} FPS=1"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_FPS_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
