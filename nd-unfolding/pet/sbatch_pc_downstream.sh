#!/bin/bash
#SBATCH --job-name=pc_down
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=96G --time=04:00:00
#SBATCH --output=pc_down_%j.out --error=pc_down_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
OUT="runEventLoopOmniFold_PC_MEFHC.root"; INP=""
FORCE_PC_REBUILD="${FORCE_PC_REBUILD:-0}"
archive_if_forcing() {
  local path="$1"
  if [[ "${FORCE_PC_REBUILD}" == "1" && -e "${path}" ]]; then
    local stamp
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    mv -v "${path}" "${path}.stale_${stamp}"
  fi
}
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  F="runEventLoopOmniFold_PC_${PL}.root"; [[ -s "$F" ]] || { echo "missing $F" >&2; exit 2; }
  INP="${INP} ${F}"
done
archive_if_forcing "${OUT}"
archive_if_forcing "of_inputs_pc.npz"
if [[ -s "${OUT}" ]]; then
  echo "[pc] merged omnifile ${OUT} already present ($(date -u +%T)); skip hadd"
else
  echo "[pc] hadd $(date -u +%T)"; hadd -f "${OUT}" ${INP}
fi
if [[ -s of_inputs_pc.npz ]]; then
  echo "[pc] of_inputs_pc.npz already present; skip dump"; ls -lh of_inputs_pc.npz; exit 0
fi
echo "[pc] dump pointcloud inputs $(date -u +%T)"
python3 dump_pointcloud_inputs.py --omnifile "${OUT}" --num-part 12 --out of_inputs_pc.npz
echo "[pc] done $(date -u +%T)"; ls -lh of_inputs_pc.npz
