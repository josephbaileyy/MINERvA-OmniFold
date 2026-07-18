#!/bin/bash
# P4 stage 2: unfold the 10 merged active endpoint ROOTs -> flat 5D xsec vectors.
# Runs INSIDE a gpu_interactive salloc; concurrent `srun --overlap --gres=none` steps.
# Each merged endpoint is a nominal 5D unfold (NO --universe: the ROOT already IS the
# promoted universe, selection-complete). FIXED --seed 42 on BOTH endpoints of a band
# so the MAT +/- pair cancels the CV but preserves the detector shift. skip-if-exists.
# Set FPS=1 to unfold the P3F merges instead (Agent C's namespace — not run here).
set -o pipefail
export HOME=/global/homes/j/josephrb

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
CONC="${CONC:-6}"; CPT="${CPT:-20}"
if [[ "${FPS:-0}" == "1" ]]; then MODE=fps; else MODE=standard; fi
# RETIRED for STANDARD publication (repair 2026-07-18): superseded by the atomic,
# resumable, fail-closed run_p4_unfold_std.sh, orchestrated by run_p4_standard.sh.
# FPS path untouched (Agent C).
if [[ "${MODE}" == "standard" && "${ALLOW_RETIRED:-0}" != "1" ]]; then
  echo "[RETIRED] run_active_lateral_unfolds_interactive.sh is forbidden for standard publication work."
  echo "          Use: bash run_p4_standard.sh  (canonical driver)."; exit 9
fi
MERGEDIR="${ND}/active_universe_5d/${MODE}/merged"
OUTDIR="${ND}/active_universe_5d/${MODE}/unfolds"   # packet P4 namespace; UNI_RE-compatible names
mkdir -p "${OUTDIR}"

echo "[p4-unfold] mode=${MODE} CONC=${CONC} start $(date -u +%T)"
for BAND in "${BANDS[@]}"; do
  for EP in 0 1; do
    MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
    OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${BAND}_${EP}.root"
    if [[ -s "${OUT}" ]]; then echo "[p4-unfold] SKIP ${BAND}:${EP} (exists)"; continue; fi
    if [[ ! -s "${MERGED}" ]]; then echo "[p4-unfold] WAIT ${BAND}:${EP} merged ROOT absent"; continue; fi
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
    srun --overlap --exact --gres=none -n1 -c"${CPT}" bash -lc "
      export HOME=/global/homes/j/josephrb OMP_NUM_THREADS=${CPT}
      source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1
      cd '${ND}'
      python3 unfold_nd_omnifold_unbinned.py --omnifile '${MERGED}' \
        --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 \
        --out '${OUT}' --verbose > '${OUTDIR}/unfold_${BAND}_${EP}.log' 2>&1 \
        && echo '[done] ${BAND}:${EP} '\$(date -u +%T) \
        || echo '[FAIL] ${BAND}:${EP} rc='\$? '(see ${OUTDIR}/unfold_${BAND}_${EP}.log)'" &
    sleep 2
  done
done
wait
N=$(find "${OUTDIR}" -name '5d_xsec_MEFHC_5iter_lgbm_uni_full_*_?.root' -size +0c 2>/dev/null | wc -l)
echo "[p4-unfold] window done $(date -u +%T); endpoint unfolds present=${N}/10"
