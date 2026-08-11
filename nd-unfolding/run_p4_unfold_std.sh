#!/bin/bash
# STANDARD P4 stage-3: TRANSACTIONAL, resumable endpoint unfolds (repair round 3).
# Bare-background (no nested srun) under one outer `srun --overlap --jobid=<holder>`.
# Per endpoint: unique temp path -> content/config validation -> ATOMIC rename of the
# ROOT -> write the receipt LAST (so a receipt implies a fully-published ROOT). Nominal
# unfold (NO --universe), FIXED --seed 42 (MAT +/- cancels CV). Resume rules:
#   * .done receipt present + ROOT valid + receipt CONTENT-validated (identities AND the whole
#     producing closure, via p4_check_receipt.py)                    -> skip
#   * otherwise                                                      -> (re)run transactionally
# Never a key-only/size-only skip. Aggregates every worker exit; requires the EXACT
# 10-tag inventory, rejecting extras as well as omissions; fail-closed.
#
# 2026-08-07 (G-1): --bkg-mode is passed EXPLICITLY (from P4Config, not hardcoded) and stamped
# into every receipt. The value is `purity` per the 2026-08-07 footing decision, which is also
# the driver default -- so this changes provenance, not physics.
#
# REPAIR-6 corrects a claim this header used to make. It said the produced ROOTs "must hash
# identically to the 2026-07-18 ones", and that is FALSE: these ROOTs are not bit-reproducible
# (KNOWN_ISSUES #24 -- measured 0/10 sha256 match on a clean re-unfold, contents agreeing to
# 1.9e-11 per bin and 2.6e-14 on the integral, from LightGBM/OpenMP reduction order). Sameness
# of a re-run is a CONTENT question at a declared tolerance (p4_lib.check_reproducibility,
# REPRO_RTOL_PER_BIN / REPRO_RTOL_INTEGRAL), never a hash question. The legacy-attest resume
# rule that depended on the false assumption is deleted; see the comment in unfold_one().
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MERGEDIR="${ND}/active_universe_5d/standard/merged"
OUTDIR="${ND}/active_universe_5d/standard/unfolds"; mkdir -p "${OUTDIR}"
# (no MANIFEST variable: its only consumer was the deleted legacy-attest path)
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
# PB2 (2026-08-11): stamp the WHOLE PRODUCING CLOSURE, not just the driver. `unfold_blob` binds
# one of the six modules that can execute while an endpoint ROOT is produced; a change to any of
# the other five (omnifold.py, omnifold_nn_core.py, xsec_nd.py, ...) used to leave the endpoint
# resumable. The map is DERIVED from p4_lib.producing_closure_blobs -- deliberately not a path
# list written out here, because a second copy of the closure is a second thing to keep in sync,
# and p4_check_receipt.py re-derives it from the same helper to compare against.
SURFACE_JSON=$(python3 -c "
import json, p4_lib as P
_c, b = P.producing_closure_blobs(P.REPO_ROOT, P.UNFOLD_DRIVER_REL)
print(json.dumps(b, sort_keys=True, separators=(',', ':')))") \
  || { echo "[p4-unfold] ABORT cannot derive the producing-closure blob map"; exit 2; }
RECEIPT_SCHEMA=$(python3 -c "import p4_lib; print(p4_lib.RECEIPT_SCHEMA_CURRENT)") \
  || { echo "[p4-unfold] ABORT cannot resolve receipt schema version"; exit 2; }
N_SURFACE=$(python3 -c "import json,sys; print(len(json.loads(sys.argv[1])))" "${SURFACE_JSON}" 2>/dev/null)
[[ -n "${SURFACE_JSON}" && "${SURFACE_JSON}" != "{}" && "${N_SURFACE:-0}" -ge 2 ]] \
  || { echo "[p4-unfold] ABORT producing-closure map is empty/degenerate (${N_SURFACE:-0} paths)"; exit 2; }
echo "[p4-unfold] start $(date -u +%T) CONC=${CONC} config_hash=${CFG_HASH} bkg_mode=${BKG_MODE} closure=${N_SURFACE} schema=${RECEIPT_SCHEMA}"

valid_root(){ python3 -c "import ROOT,sys; f=ROOT.TFile.Open('$1'); sys.exit(0 if (f and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered) and f.Get('hXSecND_flat') and f.Get('hXSecND_flat').GetNbinsX()==65856) else 1)" >/dev/null 2>&1; }
sha(){ python3 -c "import p4_lib;print(p4_lib.sha256_file('$1'))" 2>/dev/null; }

unfold_one(){
  local BAND="$1" EP="$2" tag="${1}_${2}"
  local MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_MEFHC_active_${tag}.root"
  local OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${tag}.root"
  local REC="${OUT}.done"
  # D2a: the skip is now CONTENT-validating. A ROOT plus any nonempty .done used to be enough;
  # the gate below re-derives root/central/config/bkg_mode identities live, compares the merged
  # sha against the orchestrator receipt, and (PB2) re-derives the producing closure and compares
  # every member's blob. A reject falls through and re-runs the endpoint.
  if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then
    if RCHK=$(python3 p4_check_receipt.py --receipt "${REC}" --tag "${tag}" \
                --root "${OUT}" --merged "${MERGED}" 2>&1); then
      echo "[unfold] SKIP ${tag} (receipt validated)"; return 0
    fi
    echo "[unfold] STALE ${tag} -> re-running: ${RCHK}"
    rm -f "${REC}"                       # D2: never leave a stale ROOT/receipt pair behind
  fi
  # REPAIR-6: the LEGACY-ATTEST path is DELETED, not repaired.
  #
  # It matched a legacy ROOT's sha256 against the committed manifest and then wrote a receipt
  # stamped with the CURRENT code_rev and unfold_blob -- asserting that today's driver produced
  # a file made on 2026-07-18 by an older one. That is a provenance lie, and guarding it would
  # only have made the lie harder to see (repair-5 verifier finding 1, and the same class as
  # KNOWN_ISSUES #23 and BEN-043's "a checkpoint is not provenance unless something asserts it
  # reproduces the product").
  #
  # A second, independent reason it had to go: attestation-by-hash rested on the endpoint ROOTs
  # being bit-reproducible, and they are NOT (KNOWN_ISSUES #24, measured 2026-08-07 -- 0/10
  # sha256 match on a clean re-unfold while contents agreed to 1.9e-11 per bin and 2.6e-14 on
  # the integral). So "re-unfold and compare hashes" could never have succeeded; the path could
  # only ever certify that a file had not changed on disk, which is storage integrity, not
  # provenance.
  #
  # The replacement is not a better guard -- it is removing the need for one. Every endpoint is
  # PRODUCED by this launcher, so the receipt's producer claim is true by construction. The ten
  # 2026-07-18 ROOTs are preserved under unfolds__SUPERSEDED_20260718/ and are never read here.
  [[ ! -s "${MERGED}" ]] && { echo "[unfold] ABORT ${tag} merged missing"; return 3; }
  local TMP="${OUT}.$$.${RANDOM}.tmp.root"
  rm -f "${TMP}"
  # `-u`: unbuffered. On this Lustre filesystem st_blksize is 4 MiB, so a buffered redirect
  # shows ZERO progress for the whole run and liveness has to be inferred from sstat
  # instead (BEN-028). Cost me an hour of blind watching on the 2026-08-07 probe run.
  if python3 -u unfold_nd_omnifold_unbinned.py --omnifile "${MERGED}" --axes eavail,q3,W \
       --iters 5 --use-weights --estimator lgbm --seed 42 --bkg-mode "${BKG_MODE}" \
       --out "${TMP}" --verbose \
       > "${OUTDIR}/unfold_${tag}.log" 2>&1 && valid_root "${TMP}"; then
    local MH CH RH; MH=$(sha "${MERGED}"); CH=$(sha "products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    mv -f "${TMP}" "${OUT}"; RH=$(sha "${OUT}")                       # atomic ROOT publish
    # D2c: this used to be an unchecked `printf … && mv`, so a failed receipt write still fell
    # through to `echo DONE` and returned 0 -- a published ROOT with no receipt, reported as
    # success. The write is now the function's success condition.
    if ! { printf '{"tag":"%s","mode":"produced","receipt_schema":%s,"root_sha256":"%s","merged_sha256":"%s","central5d_sha256":"%s","config_hash":"%s","bkg_mode":"%s","bkg_mode_basis":"passed explicitly to the driver by this launcher","code_rev":"%s","unfold_blob":"%s","surface_blobs":%s,"t":"%s"}\n' \
      "${tag}" "${RECEIPT_SCHEMA}" "${RH}" "${MH}" "${CH}" "${CFG_HASH}" "${BKG_MODE}" "${CODE_REV}" "${UNFOLD_BLOB}" "${SURFACE_JSON}" "$(date -u +%FT%TZ)" > "${REC}.tmp" && mv -f "${REC}.tmp" "${REC}"; }; then
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
