#!/bin/bash
#SBATCH --job-name=g2fe_evloop
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=12:00:00
#SBATCH --array=1-12
#SBATCH --output=g2fe_evloop_%a_%A.out
#SBATCH --error=g2fe_evloop_%a_%A.err
#
# G2 full-event extended-FPS point-cloud dump — 12-playlist MEFHC production array.
# ONE playlist per array task. Fail-closed. NOT auto-submitted by Agent E; the
# orchestrator submits after inspecting the pushed corrective commit. Produces
# per-playlist G2 ROOTs only (no hadd/merge/NPZ/PET).
#
# RECOVERY / PUBLICATION CONTRACT (fail-closed):
#  * Publication state is classified by EXISTENCE, not size. Neither final ROOT
#    nor receipt -> may run. Both -> full resume validation, skip only on exact
#    match. Any one-sided / zero-length / malformed / mismatched pair -> DIE
#    BEFORE env setup / event loop. Published final/receipt paths are NEVER
#    auto-deleted, quarantined, repaired, or overwritten.
#  * All 24 canonical manifest SHA-256, the binary SHA, and the validator SHA are
#    bound here at commit time; initial execution rejects any drift before compute.
#  * ROOT and receipt publication are no-clobber atomic (hardlink + verify +
#    source unlink). A crash after ROOT publication leaves ROOT-only; the next
#    run STOPS for manual reconciliation.
#  * Built-source commit (binary provenance) is recorded separately from the
#    runtime launcher/HEAD commit.
#
# set -u is intentionally OMITTED (the root_6_28 conda deactivate hook aborts
# under nounset -- AGENTS.md). Keep -e -o pipefail only.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# ---- Immutable bound footing (matches the validated G2 build) ----------------
# Source commit the canonical binary was BUILT from (NOT the runtime/launcher HEAD).
BUILT_SOURCE_COMMIT="486e53e677eb64eb9d622ff6e5daecb3e62aab22"
EXPECTED_BIN_SHA="61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
EXPECTED_VAL_SHA="3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8"
RECEIPT_SCHEMA="g2-production-playlist-receipt-v1"

BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_smoke.py"
MANIFEST_DIR="${REPO}/2d-unfolding/playlist_manifests"
WORK_ROOT="${REPO}/nd-unfolding/g2_fullevent/work"
FINAL_DIR="${REPO}/nd-unfolding/g2_fullevent/final"

# 12 canonical MEFHC playlists, one per array task.
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)

# 24 canonical manifest SHA-256, bound at commit time (12 Data + 12 MC).
declare -A MANIFEST_SHA=(
  [1A_Data.txt]=b74d89654a4fc0400e100c3f6d30d6b87082e3fba0444b7f2dcfda8682488495
  [1A_MC.txt]=4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8
  [1B_Data.txt]=91fa4a24774bfa800cd021dd712e61c777f600a7fa0c77ef1f54dad289764b1e
  [1B_MC.txt]=89328d4fafe4d59818cbd0ea5c30427fe3221b800a057d100ed79866fb8a5bad
  [1C_Data.txt]=c9fb92bdd9e905e3ec67a85b5eb07e0e964116cb998887c50113ef59aab21464
  [1C_MC.txt]=efabcb1a5bb0db7cda0c40779fc4b50e7f0dfae8c7b0d7441886005f3b72ba60
  [1D_Data.txt]=a79b49dc2964e303e2cfb578c0ac9840684b82469d3aff57fbd56950dfc8dbd8
  [1D_MC.txt]=86b2fa7b30f483f1273d23ab36fa0b2f0c72eba0cbd9044af87b06b5c5d9ca77
  [1E_Data.txt]=ca171e580c1d4f10d21ef8fa0dc362415089bd52ce74bd72f06be14e96003422
  [1E_MC.txt]=621336248107b238dab2b9ab6d540886afd729f2175e045a67e479422202d908
  [1F_Data.txt]=96520de6b8948ded10a8780f029e9a4beb3966a8becc0c71250ae21609735e0d
  [1F_MC.txt]=88bbe5135e14bd4437d65b3ee3c2be7ab0ad2b72b4afde1821ca456f0edbac10
  [1G_Data.txt]=1972d2cba379c0cbacbacad7dc0b50100baef466b31621a7812cc8a2b31b36c6
  [1G_MC.txt]=d8e1b3751cdc72e9b515e3d911d1bf0966dc3172e12fb0b6463ed248d2498ffc
  [1L_Data.txt]=e3d5b12da14d2b846bbe59727cf5a8a619442fab53af875bf506358ce2f4e96e
  [1L_MC.txt]=0a9bc517601401bd097c5334deaf2e22f28ea8ba0352ba134ccb72155e4e9fb3
  [1M_Data.txt]=2fcf89d6d2046a52c5824eba4e55dcdf134f35236e1c85d32959bf2434849286
  [1M_MC.txt]=81ac1c7a45f6d6a287c4f0318537555921f1e88efd8060388a410587e21d0083
  [1N_Data.txt]=6d043afad8b3e699f58a8c930ce3f75b33b013c8758c3b8edb8f7de62eb9f006
  [1N_MC.txt]=c259ee39f17493e75b67fe618aa15fb67b93041ef05f7f2d4a538953ff27ce5c
  [1O_Data.txt]=14c50cdffad134a842a67a50aa00799e2c8b1268fe85b9642e4338c2900f64c3
  [1O_MC.txt]=bab6e708decd89f01ee35a76cd4d374d22e4985a8a112df3b9685fc18845f646
  [1P_Data.txt]=227387cc36f85f45f6f9c8fc180b59c15601d5379604ba73242b01927600a331
  [1P_MC.txt]=da814d6bc23340a0126e3b3870f921dd76bb6fe3cd8264ce9e5dd20e7f8d218c
)

die() { echo "[g2fe][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
# A path is OCCUPIED if it exists OR is a symlink (incl. dangling: -e is false for
# a dangling symlink, so -e alone would wrongly treat it as absent).
path_occupied() { [[ -e "$1" || -L "$1" ]]; }
# device:inode identity, for hardlink postcondition proofs.
dev_ino() { stat -c '%d:%i' "$1"; }

assert_isolated_namespace() {
  case "${WORK_ROOT}${FINAL_DIR}" in
    *recoil*|*purity*|*of_inputs_pc*|*bkgsub*|*_PC_*)
      die "output namespace resolves to a forbidden recoil/purity path" ;;
  esac
  [[ "${FINAL_DIR}" == *"/nd-unfolding/g2_fullevent/final" ]] || die "FINAL_DIR not the isolated G2 namespace: ${FINAL_DIR}"
  [[ "${WORK_ROOT}" == *"/nd-unfolding/g2_fullevent/work" ]]  || die "WORK_ROOT not the isolated G2 namespace: ${WORK_ROOT}"
}

# Existence-based classification. Prints: RUN | CHECK | DIE <reason>
classify_publication() {
  local root="$1" receipt="$2" re=0 ce=0
  path_occupied "$root" && re=1
  path_occupied "$receipt" && ce=1
  if (( re==0 && ce==0 )); then echo "RUN"; return 0; fi
  if (( re==1 && ce==0 )); then echo "DIE ROOT-only: published ROOT without receipt ($root) — manual reconciliation"; return 0; fi
  if (( re==0 && ce==1 )); then echo "DIE receipt-only: receipt without ROOT ($receipt) — manual reconciliation"; return 0; fi
  if [[ ! -s "$root" ]]; then echo "DIE zero-length final ROOT ($root)"; return 0; fi
  if [[ ! -s "$receipt" ]]; then echo "DIE zero-length receipt ($receipt)"; return 0; fi
  echo "CHECK"
}

# Deep resume validation on a both-present pair. exit 0 = resume-skip; nonzero = caller must DIE.
validate_resume() {
  local root="$1" receipt="$2" pl="$3" dman="$4" mman="$5"
  local dsha msha vsha bsha
  dsha=$(sha_of "$dman"); msha=$(sha_of "$mman"); vsha=$(sha_of "$VALIDATOR"); bsha=$(sha_of "$BIN")
  python3 - "$receipt" "$root" "$pl" "$EXPECTED_BIN_SHA" "$bsha" "$EXPECTED_VAL_SHA" "$vsha" \
           "$VALIDATOR" "$dman" "$mman" "$dsha" "$msha" \
           "${MANIFEST_SHA[${pl}_Data.txt]}" "${MANIFEST_SHA[${pl}_MC.txt]}" "$RECEIPT_SCHEMA" \
           "$BUILT_SOURCE_COMMIT" <<'PY'
import json,sys,hashlib
(rc,root,pl,expbin,curbin,expval,curval,valp,dman,mman,curd,curm,bndd,bndm,schema,builtcommit)=sys.argv[1:17]
def fail(m): print("[resume-reject]",m,file=sys.stderr); sys.exit(3)
try: d=json.load(open(rc))
except Exception as e: fail(f"receipt not valid JSON: {e}")
if d.get("receipt_schema")!=schema: fail("schema mismatch")
if d.get("playlist")!=pl: fail("playlist mismatch")
if d.get("status")!="PASS": fail("status != PASS")
v=d.get("validation",{})
if v.get("n_failed")!=0: fail("n_failed != 0")
if not isinstance(v.get("n_checks"),int) or v["n_checks"]<50: fail("n_checks < 50")
if d.get("binary_sha256")!=expbin: fail("receipt binary hash != expected bound")
if d.get("binary_sha256_expected")!=expbin: fail("receipt binary_sha256_expected != launcher bound")
if d.get("built_source_commit")!=builtcommit: fail("receipt built_source_commit != launcher bound")
if curbin!=expbin: fail("current binary drift vs expected")
fr=d.get("final_root",{})
if fr.get("path")!=root: fail("final_root.path mismatch")
h=hashlib.sha256()
try:
    with open(root,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
except Exception as e: fail(f"cannot read ROOT: {e}")
if fr.get("sha256")!=h.hexdigest(): fail("final ROOT content hash != receipt")
md=d.get("manifest_data",{}); mm=d.get("manifest_mc",{})
if md.get("path")!=dman: fail("manifest_data.path mismatch")
if mm.get("path")!=mman: fail("manifest_mc.path mismatch")
if md.get("sha256")!=curd: fail("data manifest current hash != receipt")
if mm.get("sha256")!=curm: fail("mc manifest current hash != receipt")
if curd!=bndd: fail("data manifest drift vs bound")
if curm!=bndm: fail("mc manifest drift vs bound")
val=d.get("validator",{})
if val.get("path")!=valp: fail("validator.path mismatch")
if val.get("sha256")!=curval: fail("validator current hash != receipt")
if curval!=expval: fail("validator drift vs expected bound")
env=d.get("env",{})
if env.get("MNV101_DUMP_POINTCLOUD")!="1" or env.get("MNV101_FULL_PHASE_SPACE")!="1": fail("env flags not both '1'")
print("[resume-ok]"); sys.exit(0)
PY
}

# Initial-run drift guard (before compute).
assert_input_footing() {
  local pl="$1" dman="$2" mman="$3"
  [[ -s "$dman" ]] || die "missing/empty data manifest $dman"
  [[ -s "$mman" ]] || die "missing/empty mc manifest $mman"
  [[ -x "$BIN" ]] || die "canonical binary missing/executable: $BIN"
  [[ -f "$VALIDATOR" ]] || die "validator missing: $VALIDATOR"
  local g
  g=$(sha_of "$BIN");       [[ "$g" == "$EXPECTED_BIN_SHA" ]] || die "binary drift: $g != $EXPECTED_BIN_SHA"
  g=$(sha_of "$VALIDATOR"); [[ "$g" == "$EXPECTED_VAL_SHA" ]] || die "validator drift: $g != $EXPECTED_VAL_SHA"
  g=$(sha_of "$dman");      [[ "$g" == "${MANIFEST_SHA[${pl}_Data.txt]}" ]] || die "data manifest drift for $pl ($g)"
  g=$(sha_of "$mman");      [[ "$g" == "${MANIFEST_SHA[${pl}_MC.txt]}" ]]   || die "mc manifest drift for $pl ($g)"
}

# Quarantine a stale WORK partial (work-only path; NEVER a published final/receipt).
# A failed move is FATAL and never masked, so a fixed-name stale work ROOT cannot
# fall through into the event loop. Proves the source is gone before returning.
quarantine_stale_partial() {
  local wf="$1" workdir="$2" tag="$3"
  path_occupied "$wf" || return 0
  local q="${workdir}/partial_${tag}"
  mkdir -p "$q" || die "cannot create quarantine dir ${q}"
  mv "$wf" "$q/" || die "failed to quarantine stale work partial ${wf}"
  ! path_occupied "$wf" || die "stale work partial still present after quarantine: ${wf}"
  echo "$q"
}

# No-clobber atomic ROOT publication (hardlink -> prove identity -> unlink source).
# Postconditions proven: dst is a hardlink of src (same dev:inode) with identical
# content; source is unlinked and absent. Prints published hash. Any existing dst
# is left unchanged (ln without -f fails on EEXIST).
publish_root_noclobber() {
  local src="$1" dst="$2"
  path_occupied "$dst" && die "refuse ROOT publish: destination already exists (race): $dst"
  local src_sha src_di; src_sha=$(sha_of "$src"); src_di=$(dev_ino "$src")
  ln "$src" "$dst" || die "atomic hardlink ROOT publish failed (destination may have appeared): $dst"
  path_occupied "$dst" || die "post-publish: ROOT destination absent: $dst"
  local dst_sha dst_di; dst_sha=$(sha_of "$dst"); dst_di=$(dev_ino "$dst")
  [[ "$dst_di" == "$src_di" ]] || die "post-publish ROOT not a hardlink of source (dev:ino $dst_di != $src_di)"
  [[ "$dst_sha" == "$src_sha" ]] || die "post-publish ROOT content hash mismatch: $dst_sha != $src_sha"
  rm "$src" || die "failed to unlink work ROOT after publish: $src"
  ! path_occupied "$src" || die "post-publish: work ROOT source still present: $src"
  echo "$dst_sha"
}

# No-clobber atomic receipt publication (hardlink temp -> prove identity -> unlink temp).
# Postconditions proven: dst is a hardlink of temp (same dev:inode) with identical
# content+SHA; temp is unlinked and absent. Any existing dst is left unchanged.
publish_receipt_noclobber() {
  local tmp="$1" dst="$2"
  path_occupied "$dst" && die "refuse receipt publish: destination already exists: $dst"
  local tmp_sha tmp_di; tmp_sha=$(sha_of "$tmp"); tmp_di=$(dev_ino "$tmp")
  ln "$tmp" "$dst" || die "atomic hardlink receipt publish failed: $dst"
  path_occupied "$dst" || die "post-publish: receipt destination absent: $dst"
  local dst_sha dst_di; dst_sha=$(sha_of "$dst"); dst_di=$(dev_ino "$dst")
  [[ "$dst_di" == "$tmp_di" ]] || die "post-publish receipt not a hardlink of temp (dev:ino $dst_di != $tmp_di)"
  [[ "$dst_sha" == "$tmp_sha" ]] || die "post-publish receipt content hash mismatch: $dst_sha != $tmp_sha"
  rm "$tmp" || die "failed to unlink receipt temp after publish: $tmp"
  ! path_occupied "$tmp" || die "post-publish: receipt temp still present: $tmp"
}

# ---- selftest hook: define-only (no array body). Sourced with G2FE_SELFTEST=1. ----
if [[ "${G2FE_SELFTEST:-0}" == "1" ]]; then
  assert_isolated_namespace
  return 0 2>/dev/null || exit 0
fi

# ============================ array-task body ============================
assert_isolated_namespace
[[ -n "${SLURM_ARRAY_TASK_ID:-}" ]] || die "must run as an sbatch array task (SLURM_ARRAY_TASK_ID unset)"
IDX=$(( SLURM_ARRAY_TASK_ID - 1 ))
(( IDX >= 0 && IDX < ${#PLAYLISTS[@]} )) || die "array task ${SLURM_ARRAY_TASK_ID} out of range 1-${#PLAYLISTS[@]}"
PL="${PLAYLISTS[$IDX]}"

DATA_MANIFEST="${MANIFEST_DIR}/${PL}_Data.txt"
MC_MANIFEST="${MANIFEST_DIR}/${PL}_MC.txt"
WORK="${WORK_ROOT}/${PL}"
FINAL_ROOT="${FINAL_DIR}/runEventLoopOmniFold_G2_FPS_${PL}.root"
RECEIPT="${FINAL_DIR}/G2_receipt_${PL}.json"
VAL_JSON="${WORK}/g2_validation_${PL}.json"
WORK_ROOT_FILE="${WORK}/runEventLoopOmniFold.root"

echo "[g2fe] node=$(hostname) job=${SLURM_JOB_ID:-NA} task=${SLURM_ARRAY_TASK_ID} playlist=${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 1. Classify publication state (existence-based, fail-closed).
VERDICT="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
case "$VERDICT" in
  RUN) : ;;
  CHECK)
    if validate_resume "$FINAL_ROOT" "$RECEIPT" "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"; then
      echo "[g2fe] RESUME-SKIP: ${PL} already published and fully validated (exact match)."; exit 0
    else
      die "existing ${PL} final ROOT/receipt pair FAILED resume validation (stale/mismatched); refusing to overwrite. Manual reconciliation required."
    fi ;;
  DIE*) die "${VERDICT#DIE }" ;;
  *)    die "unknown publication classification: ${VERDICT}" ;;
esac

# 2. Initial-execution drift guard BEFORE any compute.
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"

mkdir -p "$WORK" "$FINAL_DIR"

# 3. Duplicate-writer guard.
exec 200>"${WORK}/.g2fe.lock"
flock -n 200 || die "another writer holds the lock for playlist ${PL} (${WORK}/.g2fe.lock)"

# 4. Re-classify under the lock (a concurrent task may have just published).
VERDICT2="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
[[ "$VERDICT2" == "RUN" ]] || die "publication state changed after acquiring lock (${VERDICT2}); refusing to run ${PL}"

# 5. Quarantine a stale WORK partial (fatal on failure; see quarantine_stale_partial).
QDIR="$(quarantine_stale_partial "$WORK_ROOT_FILE" "$WORK" "$(date -u '+%Y%m%dT%H%M%SZ')_${SLURM_JOB_ID:-NA}")"
[[ -n "$QDIR" ]] && echo "[g2fe] quarantined stale work partial -> ${QDIR}"

# 6. Environment + event loop (bare binary; NO nested srun).
source "${REPO}/setup_salloc_env.sh"
cd "$WORK"
echo "[g2fe] START loop ${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1 "$BIN" "$DATA_MANIFEST" "$MC_MANIFEST"
[[ -s "$WORK_ROOT_FILE" ]] || die "event loop produced no/empty ROOT for ${PL}"
echo "[g2fe] END loop ${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 6b. Re-assert footing after the (multi-hour) loop, BEFORE validating: a
#     shared-worktree binary/validator/manifest drift during the run must fail
#     closed rather than validate under a drifted validator.
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"

# 7. Full G2 validation BEFORE publication.
python3 "$VALIDATOR" "$WORK_ROOT_FILE" "$VAL_JSON" || die "G2 validation FAILED for ${PL} (see ${VAL_JSON})"
python3 - "$VAL_JSON" <<'PY' || die "G2 validation not PASS/>=50 for ${PL}"
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"]=="PASS" and d["n_failed"]==0 and d["n_checks"]>=50, d.get("status")
PY

# 8. No-clobber atomic ROOT publication. Immediately before publishing, reassert
#    that BOTH final ROOT and receipt are absent (require exactly RUN from the
#    same existence classifier -- a receipt race would otherwise create an
#    inconsistent pair), and re-run footing once more (post-validation drift).
VERDICT3="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
[[ "$VERDICT3" == "RUN" ]] || die "publication state changed before publish (${VERDICT3}); refusing to publish ${PL}"
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"
PUB_SHA="$(publish_root_noclobber "$WORK_ROOT_FILE" "$FINAL_ROOT")"
ROOT_SIZE="$(stat -c '%s' "$FINAL_ROOT")"

# 9. Build receipt into a unique same-dir temp (fsync), then no-clobber atomic publish LAST.
DSHA=$(sha_of "$DATA_MANIFEST"); MSHA=$(sha_of "$MC_MANIFEST"); VSHA=$(sha_of "$VALIDATOR")
TMP_RCPT="$(mktemp "${FINAL_DIR}/.g2rcpt_${PL}.XXXXXX")"
python3 - "$TMP_RCPT" "$FINAL_ROOT" "$PUB_SHA" "$ROOT_SIZE" "$EXPECTED_BIN_SHA" "$BUILT_SOURCE_COMMIT" \
         "$DATA_MANIFEST" "$MC_MANIFEST" "$DSHA" "$MSHA" "$VALIDATOR" "$VSHA" "$VAL_JSON" "$PL" \
         "${SLURM_JOB_ID:-NA}" "${SLURM_ARRAY_TASK_ID}" "$REPO" "$RECEIPT_SCHEMA" "$EXPECTED_BIN_SHA" <<'PY'
import json,sys,os,datetime,subprocess
(tmp,root,root_sha,root_size,binsha,builtcommit,dman,mman,dsha,msha,valp,vsha,valjson,pl,jid,tid,repo,schema,binexp)=sys.argv[1:20]
try: head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"]).decode().strip()
except Exception: head="UNKNOWN"
val=json.load(open(valjson))
r={"receipt_schema":schema,"playlist":pl,"status":"PASS",
   "binary_sha256":binsha,"binary_sha256_expected":binexp,
   "built_source_commit":builtcommit,
   "runtime_launcher_head":head,
   "env":{"MNV101_DUMP_POINTCLOUD":"1","MNV101_FULL_PHASE_SPACE":"1"},
   "manifest_data":{"path":dman,"sha256":dsha},
   "manifest_mc":{"path":mman,"sha256":msha},
   "validator":{"path":valp,"sha256":vsha},
   "final_root":{"path":root,"sha256":root_sha,"size_bytes":int(root_size)},
   "validation":{"n_checks":val["n_checks"],"n_failed":val["n_failed"],"counts":val["counts"],"validation_json":valjson},
   "slurm":{"jobid":jid,"array_task_id":int(tid),"node":os.uname().nodename},
   "produced_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
with open(tmp,"w") as f:
    f.write(json.dumps(r,indent=2)+"\n"); f.flush(); os.fsync(f.fileno())
print("receipt-temp-written")
PY
publish_receipt_noclobber "$TMP_RCPT" "$RECEIPT"
echo "[g2fe] DONE playlist=${PL} root=${FINAL_ROOT} sha=${PUB_SHA} receipt=${RECEIPT} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
