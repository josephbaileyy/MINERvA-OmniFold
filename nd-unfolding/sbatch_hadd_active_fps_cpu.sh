#!/bin/bash
#SBATCH --job-name=haddActFpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=16G --time=03:00:00
#SBATCH --array=0-9%5
#SBATCH --nice=0
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=active_universe_5d/fps/logs/haddActFpsC_%A_%a.out
#SBATCH --error=active_universe_5d/fps/logs/haddActFpsC_%A_%a.err
# P3F FPS endpoint merges (Agent C). GATED: run only after the P3F event-loop array
# (sbatch_evloop_array_5d_active_laterals_fps.sh) has produced all 120 ROOTs.
# 5 bands x 2 endpoints = 10 merges; each combines the 12 per-playlist active ROOTs for
# one (band,endpoint) into ONE endpoint omnifile under fps/merged/, with the active
# band/idx in the filename. Uses the large-tree-safe merger (SetMaxTreeSize 300GB) -- NEVER
# bare hadd (KNOWN_ISSUES #6). Runs on GPU host cores (CPU exhausted). High --nice yields.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
T=${SLURM_ARRAY_TASK_ID}
ENDPOINT=$(( T % 2 ))
BAND=${BANDS[$(( T / 2 ))]}
SRCDIR="active_universe_5d/fps/${BAND}_${ENDPOINT}"
MERGEDIR="active_universe_5d/fps/merged"; mkdir -p "${MERGEDIR}"
OUT="${MERGEDIR}/runEventLoopOmniFold_5D_FPS_active_${BAND}_${ENDPOINT}_universes_full.root"
[[ -s "${OUT}" ]] && { echo "[haddActFpsC] skip (exists) ${OUT}"; exit 0; }
INPUTS=(); for PL in "${PLAYLISTS[@]}"; do
  f="${SRCDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${ENDPOINT}.root"
  [[ -s "${f}" ]] || { echo "[FAIL] missing endpoint input ${f}" >&2; exit 2; }
  INPUTS+=("${f}")
done
(( ${#INPUTS[@]} == 12 )) || { echo "[FAIL] expected 12 playlist ROOTs, found ${#INPUTS[@]}" >&2; exit 2; }
echo "[haddActFpsC] band=${BAND} endpoint=${ENDPOINT} -> ${OUT}"
python3 ../2d-unfolding/uq/hadd_universes_full.py "${OUT}" "${INPUTS[@]}"
echo "[haddActFpsC] done ${OUT}"
