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
#
# 2026-08-07 (G-1): --bkg-mode is passed EXPLICITLY (from P4Config, not hardcoded) and
# stamped into every receipt. The value is `purity` per the 2026-08-07 footing decision,
# which is also the driver default -- so this changes provenance, not physics, and the
# produced ROOTs must hash identically to the 2026-07-18 ones. If a re-unfold after this
# change yields a different ROOT, STOP and find out why; do not adjust the manifest.
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
# G-1 (2026-08-07): the background footing is passed EXPLICITLY, never inherited from the
# driver default. Read from P4Config (validated above) rather than hardcoded here, so the
# launcher and the manifest cannot drift apart. `purity` is also the driver default, so this
# is a provenance change and a physics NO-OP: it must not move any output ROOT hash.
BKG_MODE=$(python3 -c "import p4_lib; c=p4_lib.P4Config(); c.validate(); print(c.bkg_mode)") || { echo "[p4-unfold] ABORT bkg_mode"; exit 2; }
CODE_REV=$(git rev-parse HEAD 2>/dev/null)
# repair-5 (D2): stamp the PRODUCING driver's committed blob into every receipt, so the resume
# gate can COMPARE source identity instead of merely observing that code_rev is non-empty.
UNFOLD_BLOB=$(git rev-parse "HEAD:nd-unfolding/unfold_nd_omnifold_unbinned.py" 2>/dev/null)
[[ -n "${CODE_REV}" && -n "${UNFOLD_BLOB}" ]] || { echo "[p4-unfold] ABORT cannot resolve code_rev/unfold blob"; exit 2; }
echo "[p4-unfold] start $(date -u +%T) CONC=${CONC} config_hash=${CFG_HASH} bkg_mode=${BKG_MODE}"

valid_root(){ python3 -c "import ROOT,sys; f=ROOT.TFile.Open('$1'); sys.exit(0 if (f and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered) and f.Get('hXSecND_flat') and f.Get('hXSecND_flat').GetNbinsX()==65856) else 1)" >/dev/null 2>&1; }
attest(){ python3 -c "import json,hashlib,sys;m=json.load(open('$MANIFEST'));import p4_lib as P;sys.exit(0 if P.sha256_file('$1')==m['endpoint_sha256'].get('$2','') else 1)" >/dev/null 2>&1; }
sha(){ python3 -c "import p4_lib;print(p4_lib.sha256_file('$1'))" 2>/dev/null; }

unfold_one(){
  local BAND="$1" EP="$2" tag="${1}_${2}"
  local MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${tag}.root"
  local OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${tag}.root"
  local REC="${OUT}.done"
  # D2a: the skip is now CONTENT-validating. A ROOT plus any nonempty .done used to be enough;
  # p4_check_receipt.py re-derives root/central/config/bkg_mode identities live and compares the
  # merged sha against the orchestrator receipt. A reject falls through and re-runs the endpoint.
  if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then
    if RCHK=$(python3 p4_check_receipt.py --receipt "${REC}" --tag "${tag}" \
                --root "${OUT}" --merged "${MERGED}" 2>&1); then
      echo "[unfold] SKIP ${tag} (receipt validated)"; return 0
    fi
    echo "[unfold] STALE ${tag} -> re-running: ${RCHK}"
    rm -f "${REC}"                       # D2: never leave a stale ROOT/receipt pair behind
  fi
  if [[ -s "${OUT}" && ! -s "${REC}" ]] && valid_root "${OUT}" && [[ -f "${MANIFEST}" ]] && attest "${OUT}" "${tag}"; then
    # D2b: the legacy receipt used to omit merged/central provenance, so an attested endpoint
    # was permanently less provable than a produced one. It now carries the same fields.
    local AMH ACH
    AMH=$(python3 -c "import p4_check_receipt as C;print(C.committed_merged_sha('${MERGED}'))") || {
      echo "[unfold] ABORT ${tag} cannot resolve committed merged sha"; return 6; }
    ACH=$(sha "products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    if ! { printf '{"tag":"%s","mode":"legacy-attested","root_sha256":"%s","merged_sha256":"%s","central5d_sha256":"%s","config_hash":"%s","bkg_mode":"%s","bkg_mode_basis":"log-branch-evidence (attestation certifies identity, not footing)","code_rev":"%s","unfold_blob":"%s","t":"%s"}\n' \
      "${tag}" "$(sha "${OUT}")" "${AMH}" "${ACH}" "${CFG_HASH}" "${BKG_MODE}" "${CODE_REV}" "${UNFOLD_BLOB}" "$(date -u +%FT%TZ)" > "${REC}.tmp" && mv -f "${REC}.tmp" "${REC}"; }; then
      echo "[unfold] FAIL ${tag} attest receipt publication failed"; rm -f "${REC}.tmp"; return 7
    fi
    echo "[unfold] ATTEST ${tag} (legacy ROOT sha256 == manifest)"; return 0
  fi
  [[ ! -s "${MERGED}" ]] && { echo "[unfold] ABORT ${tag} merged missing"; return 3; }
  local TMP="${OUT}.$$.${RANDOM}.tmp.root"
  rm -f "${TMP}"
  if python3 unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3,W \
       --iters 5 --use-weights --estimator lgbm --seed 42 --bkg-mode "${BKG_MODE}" \
       --out "${TMP}" --verbose \
       > "${OUTDIR}/unfold_${tag}.log" 2>&1 && valid_root "${TMP}"; then
    local MH CH RH; MH=$(sha "${MERGED}"); CH=$(sha "products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    mv -f "${TMP}" "${OUT}"; RH=$(sha "${OUT}")                       # atomic ROOT publish
    # D2c: this used to be an unchecked `printf … && mv`, so a failed receipt write still fell
    # through to `echo DONE` and returned 0 -- a published ROOT with no receipt, reported as
    # success. The write is now the function's success condition.
    if ! { printf '{"tag":"%s","mode":"produced","root_sha256":"%s","merged_sha256":"%s","central5d_sha256":"%s","config_hash":"%s","bkg_mode":"%s","bkg_mode_basis":"passed explicitly to the driver by this launcher","code_rev":"%s","unfold_blob":"%s","t":"%s"}\n' \
      "${tag}" "${RH}" "${MH}" "${CH}" "${CFG_HASH}" "${BKG_MODE}" "${CODE_REV}" "${UNFOLD_BLOB}" "$(date -u +%FT%TZ)" > "${REC}.tmp" && mv -f "${REC}.tmp" "${REC}"; }; then
      echo "[unfold] FAIL ${tag} receipt publication failed after ROOT publish"; rm -f "${REC}.tmp"; return 8
    fi
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
# D2d: the loop above only asks whether the ten EXPECTED tags exist, so an eleventh product in
# the directory was invisible to it. Reject extras as well as missing -- an unexplained endpoint
# in a publication namespace is exactly the state this lane spent three weeks in.
extras=0
LIVE_TAGS=$(ls "${OUTDIR}"/5d_xsec_MEFHC_5iter_lgbm_uni_full_*.root 2>/dev/null \
  | sed -e 's#.*uni_full_##' -e 's#\.root$##' | sort)
python3 -c "
import sys; sys.path.insert(0,'.')
import p4_lib as P
tags=[t for t in sys.stdin.read().split() if t]
P.require_exact_endpoint_tags(tags)
" <<< "${LIVE_TAGS}" || { echo "[p4-unfold] EXTRA/UNEXPECTED endpoint products present"; extras=1; }
if [[ "${fail}" -ne 0 || "${missing}" -ne 0 || "${extras}" -ne 0 ]]; then echo "[p4-unfold] FAIL-CLOSED (worker fail, incomplete inventory, or extra products)"; exit 5; fi
echo "[p4-unfold] COMPLETE 10/10 published+receipted $(date -u +%T)"
