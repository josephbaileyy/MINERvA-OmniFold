#!/bin/bash
# STANDARD P4 stage-1: 10 endpoint hadd-merges (CONC-capped for Lustre) + acceptance
# audit. Runs inside a held interactive CPU alloc (via alloc_run srun --overlap; the
# whole node is ours, so bare-background hadds are fine). skip-if-exists.
set -o pipefail
export HOME=/global/homes/j/josephrb
# DE-ROOTED 2026-08-12 (OI-43, increment 2) -- see run_p4_standard.sh for the idiom and why
# BASH_SOURCE is safe for these three drivers but would not be for an sbatch-submitted script.
ND="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "${ND}/.." && pwd)"
[[ -f "${ND}/p4_lib.py" ]] || { echo "[p4-merge-audit] ABORT: derived ND=${ND} contains no p4_lib.py; refusing to run against an unresolved root"; exit 3; }
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MERGEDIR="${ND}/active_universe_5d/standard/merged"; mkdir -p "${MERGEDIR}"
CONC="${CONC:-4}"
echo "[p4-merge] start $(date -u +%T) CONC=${CONC}"
valid_merged () {  # a complete merged ROOT opens with the 4 trees
  python3 -c "import ROOT,sys; f=ROOT.TFile.Open('$1'); sys.exit(0 if (f and not f.IsZombie() and f.Get('mc_truth_denom') and f.Get('mc_signal_reco') and f.Get('mc_background') and f.Get('data')) else 1)" >/dev/null 2>&1
}
merge_one () {
  local BAND="$1" EP="$2"
  local MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
  if [[ -s "${MERGED}" ]] && valid_merged "${MERGED}"; then echo "[merge] SKIP ${BAND}:${EP} valid ($(stat -c '%s' "${MERGED}")B)"; return 0; fi
  [[ -s "${MERGED}" ]] && echo "[merge] REDO ${BAND}:${EP} (existing invalid/partial)" && rm -f "${MERGED}"
  local INPUTS=(); for PL in "${PLAYLISTS[@]}"; do local f="${ND}/active_universe_5d/standard/${BAND}_${EP}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${EP}.root"; [[ -s "$f" ]] && INPUTS+=("$f"); done
  [[ ${#INPUTS[@]} -ne 12 ]] && { echo "[merge] ABORT ${BAND}:${EP} ${#INPUTS[@]}/12"; return 3; }
  python "${REPO}/2d-unfolding/uq/hadd_universes_full.py" "${MERGED}" "${INPUTS[@]}" > "${MERGEDIR}/merge_${BAND}_${EP}.log" 2>&1 \
    && echo "[merge] DONE ${BAND}:${EP} ($(stat -c '%s' "${MERGED}")B)" || { echo "[merge] FAIL ${BAND}:${EP}"; rm -f "${MERGED}"; return 4; }
}
# J31 (AUDIT-FINDINGS-20260731): merge failures used to be converted into success, twice over.
# `merge_one`'s last command on the failure path was `rm -f`, which returns 0 whether or not the
# file exists, so the function exited 0; and a bare `wait` discards every child status anyway,
# including the `return 3` abort the author did write. NMERGED was computed, printed, and never
# compared to EXPECTED, and there is no `set -e`. Fixing only the `rm` would have changed nothing.
# So: collect the PIDs, wait on each one individually, and fail closed on the count.
EXPECTED=$(( ${#BANDS[@]} * 2 ))
PIDS=(); LABELS=()
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  merge_one "$BAND" "$EP" &
  PIDS+=($!); LABELS+=("${BAND}:${EP}")
done; done
NFAILED=0
for i in "${!PIDS[@]}"; do
  if ! wait "${PIDS[$i]}"; then
    echo "[merge] child ${LABELS[$i]} exited non-zero (rc=$?)" >&2
    NFAILED=$(( NFAILED + 1 ))
  fi
done
NMERGED=$(find "${MERGEDIR}" -name 'runEventLoopOmniFold_5D_MEFHC_active_*.root' -size +0c 2>/dev/null | wc -l)
echo "[p4-merge] merges done $(date -u +%T); merged=${NMERGED}/${EXPECTED}; failed_children=${NFAILED}"
if [[ "${NFAILED}" -ne 0 || "${NMERGED}" -ne "${EXPECTED}" ]]; then
  echo "[p4-merge][FAIL] ${NMERGED}/${EXPECTED} merged, ${NFAILED} child failure(s) -- refusing to" >&2
  echo "  run the acceptance audit on an incomplete merge set. Re-run; merge_one is idempotent" >&2
  echo "  (it SKIPs a valid merged file and REDOes an invalid one)." >&2
  exit 5
fi
echo "[p4-audit] running acceptance audit..."
cd "${ND}" && python3 p3s_manifest_summary.py --mode standard
echo "[p4-merge-audit] complete $(date -u +%T)"
