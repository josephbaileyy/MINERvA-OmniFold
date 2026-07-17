#!/bin/bash
#SBATCH --job-name=ev5d_active_fps
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=12:00:00
#SBATCH --array=0-119%16
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=active_universe_5d/fps/logs/ev5d_active_fps_%A_%a.out
#SBATCH --error=active_universe_5d/fps/logs/ev5d_active_fps_%A_%a.err
# =====================================================================================
# P3F FPS active-universe event loops (Agent C). DO NOT LAUNCH until Agent A commits P2
# (interface validation) and records the validated installed-binary fingerprint. This is
# a PREPARED launcher (a distinct FPS-owned file; Agent A's shared
# sbatch_evloop_array_5d_active_laterals.sh is left untouched).
#
# 5 kinematic bands x 2 endpoints x 12 playlists = 120 selection-complete FPS event loops.
# Each promoted universe rebuilds truth/reco selection, backgrounds, truth-authoritative
# IDs, and native misses. Adds the two P3F-mandatory flags over the standard active run:
#   MNV101_DUMP_POINTCLOUD=1   (point-cloud branches for the PET-FPS descendant)
#   MNV101_FULL_PHASE_SPACE=1  (FPS truth-gate lift)
# Runs the C++ event loop on GPU HOST CORES (CPU acct m3246 exhausted; buying cores with
# GPU-hours, GPU idle). High --nice yields to critical-path PET(B)/4D(D)/standard(A) work.
# Output namespace is DISJOINT from standard: active_universe_5d/fps/ only.
#
# Binary fingerprint (Agent A's committed P2 receipt, active_universe_5d/INTERFACE_VALIDATION.md):
#   md5 e63c74961d699313ef155065fc790ff1 (default below; override via MNV101_ACTIVE_BIN_MD5).
# The task fails closed if the installed binary does not match A's validated build.
# =====================================================================================
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)

TASK=${SLURM_ARRAY_TASK_ID}
PL_INDEX=$((TASK % 12))
ENDPOINT=$(((TASK / 12) % 2))
BAND_INDEX=$((TASK / 24))
PL=${PLAYLISTS[$PL_INDEX]}
BAND=${BANDS[$BAND_INDEX]}
MODE=fps

source "${REPO}/setup_salloc_env.sh"
export MNV101_ACTIVE_UNIVERSE="${BAND}:${ENDPOINT}"
export MNV101_FULL_PHASE_SPACE=1
export MNV101_DUMP_POINTCLOUD=1
export PYTHONUNBUFFERED=1
unset MNV101_DUMP_UNIVERSES   # its shadow branches would retain CV-selected support

OUTDIR="${REPO}/nd-unfolding/active_universe_5d/${MODE}/${BAND}_${ENDPOINT}"
WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_active_${MODE}_${BAND}_${ENDPOINT}_${PL}"
mkdir -p "${OUTDIR}" "${REPO}/nd-unfolding/active_universe_5d/${MODE}/logs" "${WORKDIR}"
FINAL="${OUTDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${ENDPOINT}.root"
[[ -s "${FINAL}" ]] && { echo "[active-fps] skip (exists) ${FINAL}"; exit 0; }

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
[[ -x "${EVLOOP_BIN}" ]] || { echo "[FAIL] no installed binary ${EVLOOP_BIN}" >&2; exit 2; }
[[ -s "${DATA_MANIFEST}" && -s "${MC_MANIFEST}" ]] || { echo "[FAIL] missing manifest for ${PL}" >&2; exit 2; }

# Fail-closed on the Agent-A-validated binary fingerprint (never run an unvalidated build).
EXPECT_MD5="${MNV101_ACTIVE_BIN_MD5:-e63c74961d699313ef155065fc790ff1}"
GOT=$(md5sum "${EVLOOP_BIN}" | awk '{print $1}')
[[ "${GOT}" == "${EXPECT_MD5}" ]] || { echo "[FAIL] binary md5 ${GOT} != A-validated ${EXPECT_MD5}" >&2; exit 3; }
echo "[active-fps] binary fingerprint OK (md5 ${GOT})"

cd "${WORKDIR}"
echo "[active-fps] task=${TASK} playlist=${PL} universe=${MNV101_ACTIVE_UNIVERSE} mode=${MODE} pointcloud=1"
echo "[active-fps] binary=${EVLOOP_BIN} ($(stat -c '%y' "${EVLOOP_BIN}"))"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
mv -v runEventLoopOmniFold.root "${FINAL}"
echo "[active-fps] wrote ${FINAL}"
