#!/bin/bash
# STANDARD P4 stage-3: TRANSACTIONAL, resumable endpoint unfolds (repair round 3).
# Bare-background (no nested srun) under one outer `srun --overlap --jobid=<holder>`.
# Per endpoint: unique temp path -> content/config validation -> ATOMIC rename of the
# ROOT -> write the receipt LAST (so a receipt implies a fully-published ROOT). Nominal
# unfold (NO --universe), FIXED --seed 42 (MAT +/- cancels CV). Resume rules:
#   * .done receipt present + ROOT valid           -> skip
#   * legacy ROOT (no receipt) + sha256 == committed manifest attestation -> attest, write receipt
#   * otherwise                                     -> (re)run transactionally
# Never a key-only/size-only skip. Aggregates every worker exit; requires the EXACT
# 10-tag inventory; fail-closed.
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MERGEDIR="${ND}/active_universe_5d/standard/merged"
OUTDIR="${ND}/active_universe_5d/standard/unfolds"; mkdir -p "${OUTDIR}"
MANIFEST="${ND}/active_universe_5d/standard/evidence/p4_standard_manifest.json"
CONC="${CONC:-4}"
cd "${ND}"
CFG_HASH=$(python3 -c "import p4_lib; c=p4_lib.P4Config(); c.validate(); print(c.hash())") || { echo "[p4-unfold] ABORT config"; exit 2; }
CODE_REV=$(git rev-parse HEAD 2>/dev/null)
echo "[p4-unfold] start $(date -u +%T) CONC=${CONC} config_hash=${CFG_HASH}"

valid_root(){ python3 -c "import ROOT,sys; f=ROOT.TFile.Open('$1'); sys.exit(0 if (f and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered) and f.Get('hXSecND_flat') and f.Get('hXSecND_flat').GetNbinsX()==65856) else 1)" >/dev/null 2>&1; }
attest(){ python3 -c "import json,hashlib,sys;m=json.load(open('$MANIFEST'));import p4_lib as P;sys.exit(0 if P.sha256_file('$1')==m['endpoint_sha256'].get('$2','') else 1)" >/dev/null 2>&1; }
sha(){ python3 -c "import p4_lib;print(p4_lib.sha256_file('$1'))" 2>/dev/null; }

unfold_one(){
  local BAND="$1" EP="$2" tag="${1}_${2}"
  local MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${tag}.root"
  local OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${tag}.root"
  local REC="${OUT}.done"
  if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then echo "[unfold] SKIP ${tag} (receipt+valid)"; return 0; fi
  if [[ -s "${OUT}" && ! -s "${REC}" ]] && valid_root "${OUT}" && [[ -f "${MANIFEST}" ]] && attest "${OUT}" "${tag}"; then
    printf '{"tag":"%s","mode":"legacy-attested","root_sha256":"%s","config_hash":"%s","code_rev":"%s","t":"%s"}\n' \
      "${tag}" "$(sha "${OUT}")" "${CFG_HASH}" "${CODE_REV}" "$(date -u +%FT%TZ)" > "${REC}.tmp" && mv -f "${REC}.tmp" "${REC}"
    echo "[unfold] ATTEST ${tag} (legacy ROOT sha256 == manifest)"; return 0
  fi
  [[ ! -s "${MERGED}" ]] && { echo "[unfold] ABORT ${tag} merged missing"; return 3; }
  local TMP="${OUT}.$$.${RANDOM}.tmp.root"
  rm -f "${TMP}"
  if python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3,W \
       --iters 5 --use-weights --estimator lgbm --seed 42 --out "${TMP}" --verbose \
       > "${OUTDIR}/unfold_${tag}.log" 2>&1 && valid_root "${TMP}"; then
    local MH CH RH; MH=$(sha "${MERGED}"); CH=$(sha "products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    mv -f "${TMP}" "${OUT}"; RH=$(sha "${OUT}")                       # atomic ROOT publish
    printf '{"tag":"%s","mode":"produced","root_sha256":"%s","merged_sha256":"%s","central5d_sha256":"%s","config_hash":"%s","code_rev":"%s","t":"%s"}\n' \
      "${tag}" "${RH}" "${MH}" "${CH}" "${CFG_HASH}" "${CODE_REV}" "$(date -u +%FT%TZ)" > "${REC}.tmp" && mv -f "${REC}.tmp" "${REC}"  # receipt LAST
    echo "[unfold] DONE ${tag}"
  else
    echo "[unfold] FAIL ${tag} (see unfold_${tag}.log)"; rm -f "${TMP}"; return 4
  fi
}

declare -A RC
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
  ( unfold_one "${BAND}" "${EP}" ) & RC["${BAND}_${EP}"]=$!
done; done
fail=0
for tag in "${!RC[@]}"; do wait "${RC[$tag]}" || { echo "[p4-unfold] worker FAILED: ${tag}"; fail=1; }; done

# exact 10-tag inventory of published (ROOT + receipt) endpoints
missing=0
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  t="${BAND}_${EP}"; [[ -s "${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${t}.root" && -s "${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${t}.root.done" ]] || { echo "[p4-unfold] MISSING published ${t}"; missing=1; }
done; done
if [[ "${fail}" -ne 0 || "${missing}" -ne 0 ]]; then echo "[p4-unfold] FAIL-CLOSED (worker fail or incomplete inventory)"; exit 5; fi
echo "[p4-unfold] COMPLETE 10/10 published+receipted $(date -u +%T)"
