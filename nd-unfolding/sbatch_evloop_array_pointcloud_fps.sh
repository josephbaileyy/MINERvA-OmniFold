#!/bin/bash
#SBATCH --job-name=evloop_pc_fps
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop_pc_fps_%a_%A.out
#SBATCH --error=evloop_pc_fps_%a_%A.err

# Capstone sub-campaign 2, step 1: FULL-PHASE-SPACE point-cloud re-dump.
# Combines the two flags that already exist separately:
#   MNV101_DUMP_POINTCLOUD=1     (per-event truth FS-hadron + reco-cluster vectors,
#                                 as in sbatch_evloop_array_pointcloud.sh)
#   MNV101_FULL_PHASE_SPACE=1    (truth muon kinematic cuts off, fiducial kept,
#                                 reco selection unchanged, as in sbatch_evloop_array_5d_fps.sh)
# so the matured PET (pet_weights_cal20m.npz) can be unfolded onto the full-phase-space
# truth definition from raw reconstructed clusters -- the headline capstone.
# CV-only (no universes). NON-DESTRUCTIVE: writes runEventLoopOmniFold_PC_FPS_${PL}.root.
set -eo pipefail
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export MNV101_DUMP_POINTCLOUD=1
export MNV101_FULL_PHASE_SPACE=1
export PYTHONUNBUFFERED=1
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
WORKDIR="${REPO}/nd-unfolding/evloop_work_pc_fps_${PL}"
mkdir -p "${WORKDIR}"; cd "${WORKDIR}"
DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
echo "[pc-fps] playlist=${PL} jobid=${SLURM_JOB_ID} start $(date -u '+%F %T UTC')"
echo "[pc-fps] DUMP_POINTCLOUD=${MNV101_DUMP_POINTCLOUD} FULL_PHASE_SPACE=${MNV101_FULL_PHASE_SPACE}"
echo "[pc-fps] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
mv -v runEventLoopOmniFold.root "${REPO}/nd-unfolding/runEventLoopOmniFold_PC_FPS_${PL}.root"
echo "[pc-fps] done ${PL} $(date -u '+%F %T UTC')"
