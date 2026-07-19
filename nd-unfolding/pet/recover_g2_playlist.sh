#!/bin/bash
# Additive no-clobber, hash-bound recovery for a preserved G2 work ROOT whose
# launcher validation failed on UPSTREAM-corrupt but OUT-OF-DOMAIN rows (e.g.
# playlists 1D and 1E). It re-validates the EXISTING work ROOT with the exhaustive
# domain validator (validate_g2_fullevent_domain.py) and, ONLY with --publish,
# publishes it WITHOUT recomputing the event loop, via the same no-clobber atomic
# hardlink discipline as the production launcher. It NEVER modifies the hash-bound
# active files (binary / base validator / production launcher) and never touches a
# running array task.
#
# Usage:
#   recover_g2_playlist.sh <PLAYLIST>            # VALIDATE-ONLY (default; no publish)
#   recover_g2_playlist.sh <PLAYLIST> --publish  # validate THEN no-clobber publish
#
# This turn the recovery is authored but NOT executed with --publish.
#
# set -u omitted (root_6_28 conda deactivate hook aborts under nounset; AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
EXPECTED_BIN_SHA="61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
EXPECTED_BASE_VAL_SHA="3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8"
EXPECTED_LAUNCHER_SHA="dfcfa5c612e2067b12c879f183533de2678de78c8f6acba816ac2db86e94a715"
BUILT_SOURCE_COMMIT="486e53e677eb64eb9d622ff6e5daecb3e62aab22"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
DOMAIN_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_domain.py"
BASE_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_smoke.py"
PRODUCTION_LAUNCHER="${REPO}/nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh"
MANIFEST_DIR="${REPO}/2d-unfolding/playlist_manifests"
WORK_ROOT_DIR="${REPO}/nd-unfolding/g2_fullevent/work"
FINAL_DIR="${REPO}/nd-unfolding/g2_fullevent/final"
VALID_PLAYLISTS=" 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P "

die() { echo "[recover][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
path_occupied() { [[ -e "$1" || -L "$1" ]]; }
dev_ino() { stat -c '%d:%i' "$1"; }

PL="${1:-}"; PUBLISH=0
[[ "${2:-}" == "--publish" ]] && PUBLISH=1
[[ -n "$PL" ]] || die "usage: recover_g2_playlist.sh <PLAYLIST> [--publish]"
[[ "$VALID_PLAYLISTS" == *" $PL "* ]] || die "unknown playlist '$PL'"

WORK_ROOT="${WORK_ROOT_DIR}/${PL}/runEventLoopOmniFold.root"
FINAL_ROOT="${FINAL_DIR}/runEventLoopOmniFold_G2_FPS_${PL}.root"
RECEIPT="${FINAL_DIR}/G2_receipt_${PL}.json"
DOMAIN_RCPT="${WORK_ROOT_DIR}/${PL}/g2_domain_${PL}.json"
DATA_MANIFEST="${MANIFEST_DIR}/${PL}_Data.txt"
MC_MANIFEST="${MANIFEST_DIR}/${PL}_MC.txt"

# ---- preconditions ----
[[ -s "$WORK_ROOT" ]] || die "preserved work ROOT missing/empty: $WORK_ROOT"
[[ -f "$DOMAIN_VALIDATOR" ]] || die "domain validator missing: $DOMAIN_VALIDATOR"
[[ -f "$BASE_VALIDATOR" ]] || die "base validator missing: $BASE_VALIDATOR"
[[ -f "$PRODUCTION_LAUNCHER" ]] || die "production launcher missing: $PRODUCTION_LAUNCHER"
[[ -x "$BIN" ]] || die "canonical binary missing: $BIN"
[[ -s "$DATA_MANIFEST" && -s "$MC_MANIFEST" ]] || die "canonical manifests missing for $PL"
GBIN="$(sha_of "$BIN")"; [[ "$GBIN" == "$EXPECTED_BIN_SHA" ]] || die "binary drift: $GBIN != $EXPECTED_BIN_SHA"
GBASE="$(sha_of "$BASE_VALIDATOR")"; [[ "$GBASE" == "$EXPECTED_BASE_VAL_SHA" ]] || die "base-validator drift: $GBASE != $EXPECTED_BASE_VAL_SHA"
GLAUNCH="$(sha_of "$PRODUCTION_LAUNCHER")"; [[ "$GLAUNCH" == "$EXPECTED_LAUNCHER_SHA" ]] || die "production-launcher drift: $GLAUNCH != $EXPECTED_LAUNCHER_SHA"
# Read the manifest hashes from the exact committed production launcher rather
# than maintaining a second independent table.
BOUND_DSHA="$(bash -c 'G2FE_SELFTEST=1; source "$1"; printf "%s" "${MANIFEST_SHA[${2}_Data.txt]}"' _ "$PRODUCTION_LAUNCHER" "$PL")"
BOUND_MSHA="$(bash -c 'G2FE_SELFTEST=1; source "$1"; printf "%s" "${MANIFEST_SHA[${2}_MC.txt]}"' _ "$PRODUCTION_LAUNCHER" "$PL")"
DSHA="$(sha_of "$DATA_MANIFEST")"; [[ "$DSHA" == "$BOUND_DSHA" ]] || die "data-manifest drift for $PL"
MSHA="$(sha_of "$MC_MANIFEST")"; [[ "$MSHA" == "$BOUND_MSHA" ]] || die "MC-manifest drift for $PL"
# no-clobber: refuse if either published path already exists (dangling symlink counts)
path_occupied "$FINAL_ROOT" && die "refuse: final ROOT already exists: $FINAL_ROOT"
path_occupied "$RECEIPT"   && die "refuse: receipt already exists: $RECEIPT"

# Same playlist lock as the production launcher: never validate/publish while a
# writer or another recovery owns this namespace.
exec 200>"${WORK_ROOT_DIR}/${PL}/.g2fe.lock"
flock -n 200 || die "another writer/recovery holds the playlist lock for $PL"

# ---- environment (PyROOT for the domain validator) ----
source "${REPO}/setup_salloc_env.sh"

# ---- exhaustive domain validation (read-only; writes only its own receipt) ----
echo "[recover] exhaustive domain validation of preserved ${PL} work ROOT ..."
python3 "$DOMAIN_VALIDATOR" "$WORK_ROOT" "$DOMAIN_RCPT" || die "domain validation FAILED for ${PL} (see ${DOMAIN_RCPT}); NOT recoverable — fatal corruption could enter the FPS domain."
python3 - "$DOMAIN_RCPT" <<'PY' || die "domain validation not PASS for ${PL}"
import json,sys
d=json.load(open(sys.argv[1]))
assert d.get("status")=="PASS" and not d.get("fatal"), d.get("status")
PY
DVAL_SHA="$(sha_of "$DOMAIN_VALIDATOR")"
DRCPT_SHA="$(sha_of "$DOMAIN_RCPT")"
echo "[recover] domain validation PASS. censused out-of-domain rows bound in ${DOMAIN_RCPT}"

if [[ "$PUBLISH" -ne 1 ]]; then
  echo "[recover] VALIDATE-ONLY (no --publish). ${PL} is recovery-eligible."
  echo "[recover] to publish (after independent recheck): $0 ${PL} --publish"
  exit 0
fi

# ---- no-clobber atomic publication (hardlink -> prove identity -> unlink source) ----
path_occupied "$FINAL_ROOT" && die "race: final ROOT appeared: $FINAL_ROOT"
path_occupied "$RECEIPT"   && die "race: receipt appeared: $RECEIPT"
SRC_SHA="$(sha_of "$WORK_ROOT")"; SRC_DI="$(dev_ino "$WORK_ROOT")"
ln "$WORK_ROOT" "$FINAL_ROOT" || die "atomic hardlink publish failed: $FINAL_ROOT"
path_occupied "$FINAL_ROOT" || die "post-publish: final ROOT absent"
DST_SHA="$(sha_of "$FINAL_ROOT")"; DST_DI="$(dev_ino "$FINAL_ROOT")"
[[ "$DST_DI" == "$SRC_DI" ]] || die "post-publish: not a hardlink of source ($DST_DI != $SRC_DI)"
[[ "$DST_SHA" == "$SRC_SHA" ]] || die "post-publish: content hash mismatch"
rm "$WORK_ROOT" || die "failed to unlink work ROOT after publish"
! path_occupied "$WORK_ROOT" || die "post-publish: work ROOT source still present"
ROOT_SIZE="$(stat -c '%s' "$FINAL_ROOT")"

# ---- hash-bound recovery receipt (atomic no-clobber) ----
TMP="$(mktemp "${FINAL_DIR}/.g2rec_${PL}.XXXXXX")"
python3 - "$TMP" "$PL" "$FINAL_ROOT" "$DST_SHA" "$ROOT_SIZE" "$EXPECTED_BIN_SHA" "$BUILT_SOURCE_COMMIT" \
         "$DATA_MANIFEST" "$MC_MANIFEST" "$DSHA" "$MSHA" "$DOMAIN_VALIDATOR" "$DVAL_SHA" \
         "$DOMAIN_RCPT" "$DRCPT_SHA" "$BASE_VALIDATOR" "$GBASE" "$PRODUCTION_LAUNCHER" "$GLAUNCH" "$REPO" <<'PY'
import json,sys,os,datetime,subprocess
(tmp,pl,root,rsha,rsize,binexp,built,dman,mman,dsha,msha,dvp,dvsha,drcpt,drsha,
 basev,basevsha,launcher,launchersha,repo)=sys.argv[1:21]
try: head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"]).decode().strip()
except Exception: head="UNKNOWN"
dom=json.load(open(drcpt))
r={"receipt_schema":"g2-recovery-receipt-v1","playlist":pl,"status":"PASS","recovery":True,
   "recovery_reason":"launcher base-validator failed on upstream-corrupt OUT-OF-DOMAIN rows; "
                     "the exhaustive domain validator confirmed they are finite and outside "
                     "the declared retained domain, and censused/bound every excluded row. "
                     "Republished without recomputing.",
   "conditional_use":"This Gate-1 ROOT is valid only for a downstream input builder that "
                     "enforces the receipt's retained-domain bounds before training; Gate-1 "
                     "publication alone does not prove that downstream exclusion.",
   "binary_sha256":binexp,"binary_sha256_expected":binexp,
   "built_source_commit":built,"runtime_head":head,
   "base_validator":{"path":basev,"sha256":basevsha},
   "production_launcher":{"path":launcher,"sha256":launchersha},
   "env":{"MNV101_DUMP_POINTCLOUD":"1","MNV101_FULL_PHASE_SPACE":"1"},
   "manifest_data":{"path":dman,"sha256":dsha},"manifest_mc":{"path":mman,"sha256":msha},
   "final_root":{"path":root,"sha256":rsha,"size_bytes":int(rsize)},
   "domain_validation":{"validator":dvp,"validator_sha256":dvsha,"receipt":drcpt,
                        "receipt_sha256":drsha,"status":dom.get("status"),
                        "out_of_domain_censused_and_bound":dom.get("out_of_domain_censused_and_bound"),
                        "census":dom.get("census")},
   "produced_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
with open(tmp,"w") as f:
    f.write(json.dumps(r,indent=2)+"\n"); f.flush(); os.fsync(f.fileno())
PY
path_occupied "$RECEIPT" && { rm -f "$TMP"; die "race: receipt appeared: $RECEIPT"; }
ln "$TMP" "$RECEIPT" || { rm -f "$TMP"; die "atomic hardlink receipt publish failed: $RECEIPT"; }
rm "$TMP" || die "failed to unlink receipt temp"
echo "[recover] PUBLISHED ${PL}: root=${FINAL_ROOT} sha=${DST_SHA} receipt=${RECEIPT}"
