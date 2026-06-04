#!/bin/bash
#SBATCH --job-name=evloop4d_uni_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop4d_uni_full_%a_%A.out
#SBATCH --error=evloop4d_uni_full_%a_%A.err

# Workstream D, q3 systematic campaign: re-run the per-playlist event loop in
# DUMP-ALL mode (MNV101_DUMP_UNIVERSES=1) so the 4D omnifile carries, per
# (band, idx) over all 188 standard universes:
#   - w_truth_<band>_<idx> / w_reco_<band>_<idx>  (vertical + lateral weights)
#   - shifted (pT, pz) for the 5 lateral bands (BeamAngleX/Y, MuonResolution,
#     Muon_Energy_MINERvA/MINOS) as MC_/sim_/pT_truth_ branches
#   - shifted q3 for the same 5 lateral bands as MC_q3_/sim_q3_/q3_truth_
#     branches  <-- NEW vs the 3D dump-all. q3 is NOT lateral-invariant (it
#     depends on the muon kinematics + recoil), UNLIKE E_avail, so the 4D
#     driver must swap per-universe q3 and cannot reuse CV q3. (Verified
#     2026-06-04: reco q3 shifts for 100% of passing events; truth q3 is
#     invariant under beam-angle bands, matching truth pT/pz behaviour.)
#   - the CV E_avail + CV q3 branches the binary writes unconditionally.
#
# Resources mirror the successful 3D dump-all
# (../3d-unfolding/sbatch_evloop_array_3d_universes_full.sh): 8 cpu / 48 G /
# 24 h. Per-playlist output ~10 GB; full campaign ~120 GB (the extra q3 lateral
# branches are 5 bands x a few universes, negligible vs the 188 weight columns).
#
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_4D_${PL}_universes_full.root
# under nd-unfolding/, leaving the CV 4D per-playlist files
# (runEventLoopOmniFold_4D_${PL}.root) untouched. hadd afterwards with
# sbatch_hadd_4d_universes_full.sh (SetMaxTreeSize merger -- the combined trees
# exceed ROOT's 100 GB rollover, same as the 3D/2D dump-all).

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

export MNV101_DUMP_UNIVERSES="1"
export PYTHONUNBUFFERED=1

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/nd-unfolding/evloop_work_4d_uni_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES} (dump-all, 188 universes, +q3 lateral)"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_4D_${PL}_universes_full.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
