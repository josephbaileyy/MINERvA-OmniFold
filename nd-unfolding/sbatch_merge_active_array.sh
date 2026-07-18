#!/bin/bash
#SBATCH --job-name=mrg_std
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=03:00:00
#SBATCH --array=0-9%4
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=nd-unfolding/logs_active/mrg_%A_%a.out
#SBATCH --error=nd-unfolding/logs_active/mrg_%A_%a.err

# P4 stage-1 (STANDARD only): merge 12 per-playlist active ROOTs into one MEFHC
# endpoint ROOT, one (band,endpoint) per array task. Uses the large-tree-safe
# merger (SetMaxTreeSize 300GB), NOT bare hadd. skip-if-exists. %4 throttle keeps
# concurrent merge I/O below the Lustre thrash point. STANDARD namespace only
# (FPS post-processing is Agent C's).
set -o pipefail
export HOME=/global/homes/j/josephrb

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MODE=standard

TASK=${SLURM_ARRAY_TASK_ID}
BAND=${BANDS[$((TASK/2))]}
EP=$((TASK%2))
OUTDIR="${ND}/active_universe_5d/${MODE}/${BAND}_${EP}"
MERGEDIR="${ND}/active_universe_5d/${MODE}/merged"
MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
mkdir -p "${MERGEDIR}"

if [[ -s "${MERGED}" ]]; then
  echo "[merge] SKIP ${BAND}:${EP} exists ($(stat -c '%s' "${MERGED}") bytes)"; exit 0
fi
INPUTS=(); MISS=0
for PL in "${PLAYLISTS[@]}"; do
  f="${OUTDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${EP}.root"
  if [[ -s "${f}" ]]; then INPUTS+=("${f}"); else MISS=$((MISS+1)); echo "[merge] MISSING ${BAND}:${EP} ${PL}"; fi
done
if (( MISS > 0 )); then echo "[merge] ABORT ${BAND}:${EP} incomplete ($((12-MISS))/12)"; exit 3; fi

echo "[merge] ${BAND}:${EP} -> ${MERGED} (12 inputs)"
python "${REPO}/2d-unfolding/uq/hadd_universes_full.py" "${MERGED}" "${INPUTS[@]}"
rc=$?
if [[ $rc -eq 0 && -s "${MERGED}" ]]; then
  echo "[merge] DONE ${BAND}:${EP} ($(stat -c '%s' "${MERGED}") bytes)"
else
  echo "[merge] FAIL ${BAND}:${EP} rc=$rc"; rm -f "${MERGED}"; exit 4
fi
