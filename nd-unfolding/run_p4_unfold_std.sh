#!/bin/bash
# STANDARD P4 stage-2: unfold the 10 merged endpoints -> flat 5D xsec vectors.
# Bare-background (NO nested srun) so it runs under a single outer
# `srun --overlap --jobid=<holder>` step. Nominal unfold per merged endpoint
# (NO --universe; the ROOT already IS the promoted universe), FIXED --seed 42 on
# both endpoints so the MAT +/- pair cancels the CV. valid-skip so it resumes
# after a wall on a fresh holder. Writes active_universe_5d/standard/unfolds/.
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MERGEDIR="${ND}/active_universe_5d/standard/merged"
OUTDIR="${ND}/active_universe_5d/standard/unfolds"; mkdir -p "${OUTDIR}"
CONC="${CONC:-4}"
echo "[p4-unfold] start $(date -u +%T) CONC=${CONC}"
# Fail-closed config/source validation: pin seed/iters/estimator/no-universe.
cd "${ND}"
CFG_HASH=$(python3 -c "import p4_lib; c=p4_lib.P4Config(); c.validate(); print(c.hash())") || {
  echo "[p4-unfold] ABORT: config validation failed"; exit 2; }
echo "[p4-unfold] config_hash=${CFG_HASH}"

valid_unfold () {  # a complete unfold ROOT has hXSecND_flat
  python3 -c "import ROOT,sys; f=ROOT.TFile.Open('$1'); sys.exit(0 if (f and not f.IsZombie() and f.Get('hXSecND_flat')) else 1)" >/dev/null 2>&1
}
unfold_one () {
  local BAND="$1" EP="$2"
  local MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
  local OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${BAND}_${EP}.root"
  if [[ -s "${OUT}" ]] && valid_unfold "${OUT}"; then echo "[unfold] SKIP ${BAND}:${EP} valid"; return 0; fi
  [[ -s "${OUT}" ]] && echo "[unfold] REDO ${BAND}:${EP} (partial)" && rm -f "${OUT}"
  [[ ! -s "${MERGED}" ]] && { echo "[unfold] ABORT ${BAND}:${EP} merged missing"; return 3; }
  cd "${ND}"
  local t0=$(date +%s)
  if python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3,W \
       --iters 5 --use-weights --estimator lgbm --seed 42 --out "${OUT}" --verbose \
       > "${OUTDIR}/unfold_${BAND}_${EP}.log" 2>&1 && [[ -s "${OUT}" ]] && valid_unfold "${OUT}"; then
    printf '{"config_hash":"%s","band":"%s","endpoint":%s,"seed":42,"t":"%s"}\n' \
      "${CFG_HASH}" "${BAND}" "${EP}" "$(date -u +%FT%TZ)" > "${OUT}.done.tmp" && mv -f "${OUT}.done.tmp" "${OUT}.done"
    echo "[unfold] DONE ${BAND}:${EP} $(( $(date +%s)-t0 ))s"
  else
    echo "[unfold] FAIL ${BAND}:${EP} rc=$? (see unfold_${BAND}_${EP}.log)"; rm -f "${OUT}"
  fi
}
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
  unfold_one "${BAND}" "${EP}" &
done; done
wait
N=$(find "${OUTDIR}" -name '5d_xsec_MEFHC_5iter_lgbm_uni_full_*_?.root' -size +0c 2>/dev/null | wc -l)
echo "[p4-unfold] done $(date -u +%T); unfolds present=${N}/10"
# Fail-closed: the driver only returns success on a complete 10/10 set.
if [[ "${N}" -ne 10 ]]; then echo "[p4-unfold] FAIL-CLOSED: ${N}/10 (incomplete — resume on a fresh holder)"; exit 5; fi
echo "[p4-unfold] COMPLETE 10/10"
