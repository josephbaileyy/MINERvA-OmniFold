#!/bin/bash
#SBATCH --job-name=evloop5d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop5d_%a_%A.out
#SBATCH --error=evloop5d_%a_%A.err

# Workstream F re-run: per-playlist event loop for ALL 12 MEFHC playlists, now
# with the W branches (MC_W / sim_W / sim_background_W / measured_W) + the truth
# diagnostics (MC_nproton / MC_npip / MC_hadangle) the rebuilt binary dumps on
# top of the pt/pz/eavail/q3 schema.
#   reco  W = CVUniverse::RecoW()  (calorimetric, same q0/Q^2 lineage as RecoQ3)
#   truth W = CVUniverse::GetTrueExperimentersW() (MAT DIS-weighting convention)
#
# CV-only (no MNV101_DUMP_UNIVERSES): produces the central-value 5D omnifile for
# the unfold + validation anchors. The 187-universe systematic campaign for W is
# a separate, much larger run (the binary already dumps shifted W under
# MNV101_DUMP_UNIVERSES, so that re-run needs no new code).
#
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_5D_${PL}.root, leaving the frozen
# 4D CV omnifiles (runEventLoopOmniFold_4D_${PL}.root) untouched. The 5D files
# are a strict superset of the 4D schema (+W +diagnostics), so the 4D/3D drivers
# still read them unchanged.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
