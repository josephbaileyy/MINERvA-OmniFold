#!/bin/bash
#SBATCH --job-name=ev5d_active
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=05:00:00
#SBATCH --array=0-119%12
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=nd-unfolding/logs_active/ev5d_active_%A_%a.out
#SBATCH --error=nd-unfolding/logs_active/ev5d_active_%A_%a.err

# P3S/P3F selection-complete active-universe event loops:
# 5 kinematic bands x 2 endpoints x 12 playlists = 120 per-playlist ROOTs.
# Each requested universe becomes the ORDINARY event-loop universe, rebuilding
# truth/reco selection, backgrounds, truth-authoritative IDs, native misses
# (migration census vs CV written as TParameters). MNV101_DUMP_POINTCLOUD=1 so
# signal/data/background trees carry point-cloud branches for PET P5.
# Do NOT set MNV101_DUMP_UNIVERSES (its shadow branches retain CV-selected support).
#
# ONE playlist per array task (index t -> band=t/24, endpoint=(t/12)%2, playlist=t%12).
# Outputs are ~6-7 GB each (point clouds); the %12 array throttle keeps concurrent
# read+write well below the Lustre thrash point observed at ~40-wide. Non-preemptible
# batch (CPU acct restored); skip-if-exists makes cancel/relaunch safe & resumable.
# Set FPS=1 at submission for the P3F full-phase-space campaign.

set -o pipefail   # NOT set -u: setup_MAT.sh references unset vars under nounset
export HOME=/global/homes/j/josephrb

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)

TASK=${SLURM_ARRAY_TASK_ID}
PL_INDEX=$((TASK % 12))
ENDPOINT=$(((TASK / 12) % 2))
BAND_INDEX=$((TASK / 24))
PL=${PLAYLISTS[$PL_INDEX]}
BAND=${BANDS[$BAND_INDEX]}
MODE=standard

source "${REPO}/setup_salloc_env.sh"
export MNV101_ACTIVE_UNIVERSE="${BAND}:${ENDPOINT}"
export MNV101_DUMP_POINTCLOUD=1
export PYTHONUNBUFFERED=1
unset MNV101_DUMP_UNIVERSES
if [[ "${FPS:-0}" == "1" ]]; then export MNV101_FULL_PHASE_SPACE=1; MODE=fps; else unset MNV101_FULL_PHASE_SPACE; fi

OUTDIR="${REPO}/nd-unfolding/active_universe_5d/${MODE}/${BAND}_${ENDPOINT}"
FINAL="${OUTDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${ENDPOINT}.root"
mkdir -p "${OUTDIR}"
if [[ -s "${FINAL}" ]]; then
  echo "[active] SKIP task=${TASK} ${BAND}:${ENDPOINT} ${PL} exists ($(stat -c '%s' "${FINAL}") bytes)"; exit 0
fi

# unique workdir per batch task so a concurrent interactive orchestrator (which
# uses the un-suffixed name) can never collide on rm -rf / cwd for the same unit.
WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_active_${MODE}_${BAND}_${ENDPOINT}_${PL}_b${SLURM_JOB_ID}"
rm -rf "${WORKDIR}"; mkdir -p "${WORKDIR}"; cd "${WORKDIR}"
DATA="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
echo "[active] task=${TASK} ${BAND}:${ENDPOINT} ${PL} pointcloud=1 md5=$(md5sum "${BIN}"|cut -d' ' -f1)"
"${BIN}" "${DATA}" "${MC}"
mv -v runEventLoopOmniFold.root "${FINAL}"
echo "[active] wrote ${FINAL} ($(stat -c '%s' "${FINAL}") bytes)"
cd "${REPO}" && rm -rf "${WORKDIR}"
