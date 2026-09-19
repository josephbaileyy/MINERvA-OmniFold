#!/bin/bash
# Build Gregor's complete-arm inputs from the slim tuples, one task per
# (playlist, stream). CPU only.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --job-name=pet-build-inputs
#SBATCH --array=1-24
set -eo pipefail
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
SLIM=/pscratch/sd/j/josephrb/r4slim
OUT=/pscratch/sd/j/josephrb/theirs_inputs
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
INDEX=$((SLURM_ARRAY_TASK_ID - 1))
if (( INDEX < 12 )); then PL="${PLAYLISTS[$INDEX]}"; STREAM=MC
else PL="${PLAYLISTS[$((INDEX - 12))]}"; STREAM=Data; fi
mkdir -p "${OUT}/${PL}_${STREAM}" "${OUT}/reports"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1 || true
python3 /pscratch/sd/j/josephrb/run_build_inputs.py \
  --slimdir "${SLIM}/${PL}_${STREAM}" \
  --outdir "${OUT}/${PL}_${STREAM}" \
  --stream "$STREAM" \
  --report "${OUT}/reports/build_${PL}_${STREAM}.json"
echo COMPLETE > "${OUT}/reports/${PL}_${STREAM}.done"
