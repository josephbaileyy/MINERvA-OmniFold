#!/bin/bash
#SBATCH --job-name=evloop_pc
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop_pc_%a_%A.out
#SBATCH --error=evloop_pc_%a_%A.err

# Phase 3 point-cloud track: per-playlist event loop with MNV101_DUMP_POINTCLOUD=1
# so the omnifile carries per-event variable-length truth FS-hadron + reco-cluster
# vectors (part_gen_{E,px,py,pz,pdg}, part_reco_{E,x,y,z}) on top of the scalar
# pt/pz/eavail/q3 schema. CV-only (no universes) -> cheap (~few GB/playlist), unlike
# the 120 GB universe dump. Feeds nn_dump_inputs.py --pointcloud -> the vendored PET.
set -eo pipefail
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export MNV101_DUMP_POINTCLOUD=1
export PYTHONUNBUFFERED=1
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
WORKDIR="${REPO}/nd-unfolding/evloop_work_pc_${PL}"
mkdir -p "${WORKDIR}"; cd "${WORKDIR}"
DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
echo "[pc] playlist=${PL} jobid=${SLURM_JOB_ID} start $(date -u '+%F %T UTC')"
echo "[pc] MNV101_DUMP_POINTCLOUD=${MNV101_DUMP_POINTCLOUD}"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
mv -v runEventLoopOmniFold.root "${REPO}/nd-unfolding/runEventLoopOmniFold_PC_${PL}.root"
echo "[pc] done ${PL} $(date -u '+%F %T UTC')"
