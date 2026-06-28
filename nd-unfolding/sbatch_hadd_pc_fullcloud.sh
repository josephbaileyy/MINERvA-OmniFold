#!/bin/bash
#SBATCH --job-name=hadd_pc_fc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=16G --time=03:00:00
#SBATCH --output=hadd_pc_fc_%j.out --error=hadd_pc_fc_%j.err
# Stage 2 of the truth-cloud-fix re-dump: merge the 12 per-playlist CV-only PC
# files (regenerated with the cloud-coverage fix) into a fullcloud MEFHC file.
# CV-only PC files total ~49 GB -> well under ROOT's 100 GB TTree limit, so plain
# hadd is safe (unlike the universes_full monster). Baseline PC_MEFHC.root is left
# untouched (new -fullcloud name).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
INPUTS=()
for pl in "${PLAYLISTS[@]}"; do
  f="runEventLoopOmniFold_PC_${pl}.root"
  [ -s "$f" ] || { echo "[hadd] MISSING per-playlist input: $f"; exit 1; }
  INPUTS+=("$f")
done
OUT="runEventLoopOmniFold_PC_MEFHC_fullcloud.root"
echo "[hadd] merging ${#INPUTS[@]} files -> ${OUT}  $(date -u '+%F %T UTC')"
hadd -f "${OUT}" "${INPUTS[@]}"
echo "[hadd] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
