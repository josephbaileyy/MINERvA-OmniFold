#!/bin/bash
#SBATCH --job-name=evloop3d_uni_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --array=1-12
#SBATCH --output=evloop3d_uni_full_%a_%A.out
#SBATCH --error=evloop3d_uni_full_%a_%A.err

# Gap 2 of the 3D systematic-UQ campaign (3D_SYSTEMATIC_UQ_PLAN.md): re-run the
# per-playlist event loop in DUMP-ALL mode (MNV101_DUMP_UNIVERSES=1) so the 3D
# omnifile carries, per (band, idx) over all 188 standard universes:
#   - w_truth_<band>_<idx> / w_reco_<band>_<idx>  (vertical + lateral weights)
#   - shifted (pT, pz) for the 5 lateral bands (BeamAngleX/Y, MuonResolution,
#     Muon_Energy_MINERvA/MINOS) as MC_/sim_/pT_truth_ branches
#   - the CV E_avail branches (MC_eavail / sim_eavail / sim_background_eavail /
#     measured_eavail) the binary writes unconditionally.
# E_avail is invariant under every lateral band (Gap 1 finding 2026-05-31), so
# no per-universe E_avail branch exists or is needed; the 3D driver's --universe
# path swaps (pT, pz) only and keeps CV E_avail.
#
# Resources mirror the successful 2D dump-all (sbatch_evloop_array_universes_full.sh):
# 8 cpu / 48 G / 24 h. Per-playlist output ~10 GB; full campaign ~120 GB (the
# eavail CV branches are negligible vs the 188 universe branches, so this is a
# touch larger than the 119 GB 2D dump-all, not the conservative 170 GB).
#
# NON-DESTRUCTIVE: writes runEventLoopOmniFold_3D_${PL}_universes_full.root under
# 3d-unfolding/, leaving the CV per-playlist files (runEventLoopOmniFold_3D_${PL}.root)
# and the 2D dump-all (../2d-unfolding/...) untouched. hadd afterwards with
# sbatch_hadd_3d_universes_full.sh.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

export MNV101_DUMP_UNIVERSES="1"
export PYTHONUNBUFFERED=1

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/3d-unfolding/evloop_work_3d_uni_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES} (dump-all, 188 universes)"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/3d-unfolding/runEventLoopOmniFold_3D_${PL}_universes_full.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
ls -lh "${FINAL}"
