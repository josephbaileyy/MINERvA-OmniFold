#!/bin/bash
#SBATCH --job-name=evloop_fps1A
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --output=evloop_fps1A_%j.out
#SBATCH --error=evloop_fps1A_%j.err

# FULL-PHASE-SPACE pilot (1A only): same 5D dump as sbatch_evloop_array_5d.sh
# but with MNV101_FULL_PHASE_SPACE=1, which drops the truth muon kinematic
# cuts (theta<20deg, 1.5<p_||<60, p_T<4.5) from the signal definition while
# keeping the tracker-fiducial ZRange/Apothem. Reco selection unchanged.
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_5D_FPS_1A.root.

set -eo pipefail

PL="1A"
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

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} playlist=${PL} FPS=1"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_FPS_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
