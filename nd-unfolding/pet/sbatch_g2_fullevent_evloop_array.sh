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
# ONE playlist per array task. Fail-closed: binary-hash-bound, manifest-checked,
# duplicate-writer-guarded, full G2 validation BEFORE atomic publication, hash-bound
# per-playlist receipt written LAST, content-validated resume. DO NOT edit the output
# paths to any recoil/purity namespace -- the script refuses.
#
# NOTE: NOT auto-submitted by Agent E. The orchestrator submits after inspecting the
# pushed G2-gate commit. Produces per-playlist G2 ROOTs; it does NOT hadd/merge, build
# NPZ, or train PET (those are downstream, separately gated).
#
# set -u is intentionally OMITTED: the conda deactivate hook in the root_6_28 env
# aborts under nounset (AGENTS.md). Keep -e -o pipefail only.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# ---- Bound footing (must match the validated G2 build) -----------------------
EXPECTED_BIN_SHA="61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_smoke.py"
MANIFEST_DIR="${REPO}/2d-unfolding/playlist_manifests"

# ---- Isolated G2 namespaces (NEVER a canonical recoil-only / purity path) ----
WORK_ROOT="${REPO}/nd-unfolding/g2_fullevent/work"
FINAL_DIR="${REPO}/nd-unfolding/g2_fullevent/final"

# 12 canonical MEFHC playlists, one per array task.
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)

die() { echo "[g2fe][FAIL] $*" >&2; exit 1; }

# ---- Guard: forbidden (old recoil/purity) namespace in output paths ----------
case "${WORK_ROOT}${FINAL_DIR}" in
  *recoil*|*purity*|*of_inputs_pc*|*bkgsub*|*_PC_*)
    die "output namespace resolves to a forbidden recoil/purity path: ${WORK_ROOT} ${FINAL_DIR}" ;;
esac
[[ "${FINAL_DIR}" == *"/nd-unfolding/g2_fullevent/final" ]] || \
  die "FINAL_DIR is not the isolated G2 namespace: ${FINAL_DIR}"

# ---- Resolve this task's playlist --------------------------------------------
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

echo "[g2fe] node=$(hostname) jobid=${SLURM_JOB_ID:-NA} task=${SLURM_ARRAY_TASK_ID} playlist=${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# ---- Guard: manifests exist and are non-empty --------------------------------
[[ -s "${DATA_MANIFEST}" ]] || die "missing/empty data manifest ${DATA_MANIFEST}"
[[ -s "${MC_MANIFEST}"   ]] || die "missing/empty mc manifest ${MC_MANIFEST}"
[[ -x "${BIN}"       ]] || die "canonical binary not found/executable: ${BIN}"
[[ -f "${VALIDATOR}" ]] || die "validator not found: ${VALIDATOR}"

# ---- Guard: canonical binary hash (reject drift) -----------------------------
GOT_BIN_SHA="$(sha256sum "${BIN}" | awk '{print $1}')"
[[ "${GOT_BIN_SHA}" == "${EXPECTED_BIN_SHA}" ]] || \
  die "binary drift: ${BIN} sha256 ${GOT_BIN_SHA} != expected ${EXPECTED_BIN_SHA}"

mkdir -p "${WORK}" "${FINAL_DIR}"

# ---- Duplicate-writer guard (per playlist) -----------------------------------
exec 200>"${WORK}/.g2fe.lock"
flock -n 200 || die "another writer holds the lock for playlist ${PL} (${WORK}/.g2fe.lock)"

# ---- Content-validated resume ------------------------------------------------
# Skip only if BOTH final ROOT and receipt exist AND the receipt is internally
# consistent: expected binary hash, PASS/0-failed validation, and the recorded
# ROOT sha256 equals the actual final ROOT content hash.
if [[ -s "${FINAL_ROOT}" && -s "${RECEIPT}" ]]; then
  if python3 - "$RECEIPT" "$FINAL_ROOT" "$EXPECTED_BIN_SHA" <<'PYRES'
import json,sys,hashlib
rc,root,expbin=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(rc))
if d.get("status")!="PASS" or d.get("validation",{}).get("n_failed")!=0: sys.exit(1)
if d.get("binary_sha256")!=expbin: sys.exit(1)
h=hashlib.sha256()
with open(root,"rb") as f:
    for b in iter(lambda:f.read(1<<20),b""): h.update(b)
sys.exit(0 if d.get("final_root",{}).get("sha256")==h.hexdigest() else 1)
PYRES
  then
    echo "[g2fe] RESUME-SKIP: ${PL} already published+validated (content-matched receipt)."
    exit 0
  else
    die "existing final ROOT/receipt for ${PL} is inconsistent (stale/partial); refusing to overwrite a published product. Inspect ${FINAL_ROOT} / ${RECEIPT}."
  fi
fi

# ---- Quarantine any stale partial (work ROOT with no valid published pair) ----
if [[ -e "${WORK_ROOT_FILE}" ]]; then
  QDIR="${WORK}/partial_$(date -u '+%Y%m%dT%H%M%SZ')_${SLURM_JOB_ID:-NA}"
  mkdir -p "${QDIR}"
  mv -v "${WORK_ROOT_FILE}" "${QDIR}/" || true
  echo "[g2fe] quarantined stale partial to ${QDIR}"
fi

# ---- Environment (real HOME under sbatch; conda root_6_28 activates cleanly) --
source "${REPO}/setup_salloc_env.sh"

# ---- Event loop (bare binary; NO nested srun) --------------------------------
cd "${WORK}"
echo "[g2fe] START loop ${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1 "${BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
[[ -s "${WORK_ROOT_FILE}" ]] || die "event loop produced no/empty ROOT for ${PL}"
echo "[g2fe] END loop ${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# ---- Full G2 validation BEFORE publication -----------------------------------
python3 "${VALIDATOR}" "${WORK_ROOT_FILE}" "${VAL_JSON}" || die "G2 validation FAILED for ${PL} (see ${VAL_JSON})"
python3 - "$VAL_JSON" <<'PYCHK' || die "G2 validation not PASS/50 for ${PL}"
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"]=="PASS" and d["n_failed"]==0 and d["n_checks"]>=50, d.get("status")
PYCHK

# ---- Atomic publication (same-fs rename of the validated work ROOT) ----------
# work/ and final/ are the same filesystem, so mv is an atomic rename. Hash the
# validated work ROOT first, then rename, then re-hash the final path and require
# equality (rename must preserve content).
SRC_SHA="$(sha256sum "${WORK_ROOT_FILE}" | awk '{print $1}')"
mv -f "${WORK_ROOT_FILE}" "${FINAL_ROOT}"
PUB_SHA="$(sha256sum "${FINAL_ROOT}" | awk '{print $1}')"
[[ "${SRC_SHA}" == "${PUB_SHA}" ]] || die "post-move hash mismatch for ${PL} (${SRC_SHA} != ${PUB_SHA})"
ROOT_SIZE="$(stat -c '%s' "${FINAL_ROOT}")"

# ---- Hash-bound per-playlist receipt, written LAST ---------------------------
python3 - "$RECEIPT" "$FINAL_ROOT" "$PUB_SHA" "$ROOT_SIZE" "$GOT_BIN_SHA" "$BIN" \
         "$DATA_MANIFEST" "$MC_MANIFEST" "$VAL_JSON" "$PL" "${SLURM_JOB_ID:-NA}" \
         "${SLURM_ARRAY_TASK_ID}" "$REPO" <<'PYRCPT'
import json,sys,hashlib,subprocess,datetime,os
(rc_path,root,root_sha,root_size,bin_sha,binp,dman,mman,valjson,pl,jid,tid,repo)=sys.argv[1:14]
def sh(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
try:
    commit=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"]).decode().strip()
except Exception:
    commit="UNKNOWN"
val=json.load(open(valjson))
receipt={
 "receipt_schema":"g2-production-playlist-receipt-v1",
 "playlist":pl,"status":"PASS",
 "binary_sha256":bin_sha,
 "binary_sha256_expected":"61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b",
 "source_commit":commit,
 "env":{"MNV101_DUMP_POINTCLOUD":"1","MNV101_FULL_PHASE_SPACE":"1"},
 "manifest_data":{"path":dman,"sha256":sh(dman)},
 "manifest_mc":{"path":mman,"sha256":sh(mman)},
 "final_root":{"path":root,"sha256":root_sha,"size_bytes":int(root_size)},
 "validation":{"n_checks":val["n_checks"],"n_failed":val["n_failed"],
               "counts":val["counts"],"validation_json":valjson},
 "slurm":{"jobid":jid,"array_task_id":int(tid),"node":os.uname().nodename},
 "produced_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
# write to a temp then atomic-rename so the receipt (the completion marker) is never partial
tmp=rc_path+".tmp"
open(tmp,"w").write(json.dumps(receipt,indent=2)+"\n")
os.replace(tmp,rc_path)
print("[g2fe] receipt written:",rc_path)
PYRCPT

echo "[g2fe] DONE playlist=${PL} root=${FINAL_ROOT} sha=${PUB_SHA} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
