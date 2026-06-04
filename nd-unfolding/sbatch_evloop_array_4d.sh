#!/bin/bash
#SBATCH --job-name=evloop4d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop4d_%a_%A.out
#SBATCH --error=evloop4d_%a_%A.err

# Workstream D re-run: per-playlist event loop for ALL 12 MEFHC playlists with
# the q3 branches (MC_q3 / sim_q3 / sim_background_q3 / measured_q3) added to
# runEventLoopOmniFold.cpp on top of the existing pt/pz/eavail schema.
#   reco  q3 = CVUniverse::RecoQ3()  (calorimetric, LowRecoilFunctions GetLowRecoilQ3)
#   truth q3 = CVUniverse::Getq3True() (MAT TruthFunctions, mc_Q2 + true muon)
#
# CV-only (no MNV101_DUMP_UNIVERSES): produces the central-value 4D omnifile for
# the unfold + validation anchors. The 187-universe systematic campaign is a
# separate, much larger run.
#
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_4D_${PL}.root under nd-unfolding/.
# These are a strict superset of the 3D schema (pt/pz/eavail + q3), so the 3D
# driver still reads them unchanged.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/nd-unfolding/evloop_work_4d_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_4D_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
