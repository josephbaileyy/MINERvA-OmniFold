#!/bin/bash
# Slim the MasterAnaDev tuples to the R4 manifest, one array task per
# (playlist, stream). CPU only, read-only on the tuples, writes slim ROOTs.
#
# This is the extraction R4 authorized. It applies NO selection and computes
# nothing: same rows, same order, fewer columns, so it cannot change which
# events exist. Selection, the identity join and his token construction happen
# downstream against the inventory.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=03:00:00
#SBATCH --job-name=pet-r4-extract
#SBATCH --array=1-24
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT=/pscratch/sd/j/josephrb/r4slim
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
INDEX=$((SLURM_ARRAY_TASK_ID - 1))
if (( INDEX < 12 )); then
  PL="${PLAYLISTS[$INDEX]}"; STREAM=MC
else
  PL="${PLAYLISTS[$((INDEX - 12))]}"; STREAM=Data
fi
MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_${STREAM}.txt"
[[ -f "$MANIFEST" ]]
mkdir -p "${OUT}/${PL}_${STREAM}" "${OUT}/reports"

source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1 || true

python3 /pscratch/sd/j/josephrb/extract_r4_slim.py \
  --manifest "$MANIFEST" \
  --outdir "${OUT}/${PL}_${STREAM}" \
  --threads 16 \
  --report "${OUT}/reports/report_${PL}_${STREAM}.json"

echo "COMPLETE ${PL}_${STREAM}" > "${OUT}/reports/${PL}_${STREAM}.done"
