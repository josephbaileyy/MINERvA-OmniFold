#!/bin/bash
#SBATCH --job-name=evloop3d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop3d_%a_%A.out
#SBATCH --error=evloop3d_%a_%A.err

# Workstream C re-run: per-playlist event loop for ALL 12 MEFHC playlists
# with the Eavail branches (MC_eavail / sim_eavail / sim_background_eavail /
# measured_eavail) added to runEventLoopOmniFold.cpp.
#
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_3D_${PL}.root under 3d-unfolding/
# so the frozen 2D per-playlist ROOTs in 2d-unfolding/ are untouched. The new
# files are a superset of the 2D schema (pt/pz + eavail), so the 2D driver
# still reads them unchanged if ever pointed at one.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/3d-unfolding/evloop_work_3d_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/3d-unfolding/runEventLoopOmniFold_3D_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
