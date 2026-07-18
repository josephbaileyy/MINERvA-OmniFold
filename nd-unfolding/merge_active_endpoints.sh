#!/bin/bash
# P3S/P3F endpoint merge: for each (band,endpoint) with all 12 per-playlist active
# ROOTs present, merge into one MEFHC endpoint ROOT under {mode}/merged/ using the
# large-tree-safe merger (SetMaxTreeSize 300GB), NOT bare hadd (KNOWN_ISSUES #6).
# skip-if-exists on the merged output; skip endpoints that are not yet 12/12.
# Runs on a compute node (login can't run ROOT). Set FPS=1 for the P3F namespace.
# NO set -u (conda activate); HOME fix inline.
set -o pipefail
export HOME=/global/homes/j/josephrb/

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
if [[ "${FPS:-0}" == "1" ]]; then MODE=fps; else MODE=standard; fi
# RETIRED for STANDARD publication (repair 2026-07-18): superseded by the canonical
# manifest-bound, PID-aggregating merge in sbatch_merge_active_array.sh /
# run_p4_merge_audit_std.sh, orchestrated by run_p4_standard.sh. FPS path untouched.
if [[ "${MODE}" == "standard" && "${ALLOW_RETIRED:-0}" != "1" ]]; then
  echo "[RETIRED] merge_active_endpoints.sh is forbidden for standard publication work."
  echo "          Use: bash run_p4_standard.sh  (canonical driver)."; exit 9
fi
MERGEDIR="${ND}/active_universe_5d/${MODE}/merged"
mkdir -p "${MERGEDIR}"

echo "[merge] mode=${MODE} start $(date -u +%T)"
for BAND in "${BANDS[@]}"; do
  for EP in 0 1; do
    OUTDIR="${ND}/active_universe_5d/${MODE}/${BAND}_${EP}"
    MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
    if [[ -s "${MERGED}" ]]; then
      echo "[merge] SKIP ${BAND}:${EP} merged exists ($(stat -c '%s' "${MERGED}") bytes)"; continue
    fi
    INPUTS=(); MISS=0
    for PL in "${PLAYLISTS[@]}"; do
      f="${OUTDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${EP}.root"
      if [[ -s "${f}" ]]; then INPUTS+=("${f}"); else MISS=$((MISS+1)); fi
    done
    if (( MISS > 0 )); then
      echo "[merge] WAIT ${BAND}:${EP} only $((12-MISS))/12 playlists present; skipping"; continue
    fi
    echo "[merge] ${BAND}:${EP} -> ${MERGED} (12 inputs)"
    if python "${REPO}/2d-unfolding/uq/hadd_universes_full.py" "${MERGED}" "${INPUTS[@]}" > "${MERGEDIR}/merge_${BAND}_${EP}.log" 2>&1; then
      echo "[merge] DONE ${BAND}:${EP} ($(stat -c '%s' "${MERGED}") bytes)"
    else
      echo "[merge] FAIL ${BAND}:${EP} (see ${MERGEDIR}/merge_${BAND}_${EP}.log)"; rm -f "${MERGED}"
    fi
  done
done
NMERGED=$(find "${MERGEDIR}" -name 'runEventLoopOmniFold_5D_MEFHC_active_*.root' -size +0c 2>/dev/null | wc -l)
echo "[merge] done $(date -u +%T); merged endpoints present=${NMERGED}/10"
