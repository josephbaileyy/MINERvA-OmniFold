#!/bin/bash
# STANDARD P4 stage-1: 10 endpoint hadd-merges (CONC-capped for Lustre) + acceptance
# audit. Runs inside a held interactive CPU alloc (via alloc_run srun --overlap; the
# whole node is ours, so bare-background hadds are fine). skip-if-exists.
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
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
    && echo "[merge] DONE ${BAND}:${EP} ($(stat -c '%s' "${MERGED}")B)" || { echo "[merge] FAIL ${BAND}:${EP}"; rm -f "${MERGED}"; }
}
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  merge_one "$BAND" "$EP" &
done; done
wait
NMERGED=$(find "${MERGEDIR}" -name 'runEventLoopOmniFold_5D_MEFHC_active_*.root' -size +0c 2>/dev/null | wc -l)
echo "[p4-merge] merges done $(date -u +%T); merged=${NMERGED}/10"
echo "[p4-audit] running acceptance audit..."
cd "${ND}" && python3 p3s_manifest_summary.py --mode standard
echo "[p4-merge-audit] complete $(date -u +%T)"
