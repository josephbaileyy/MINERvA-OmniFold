#!/bin/bash
# ONE REPRODUCIBLE SUBMISSION PROCEDURE for the reviewed deployment at fb9ec356.
#
# Every check below runs IN THIS SHELL, the same one that invokes sbatch at the end, because
# the two pilot failures of 2026-09-16 were both submission-side: a relative --output resolved
# against a read-only CWD, and five $HOME PATH entries carried in by --export=ALL. Checking in
# one shell and submitting from another is what let both through.
#
# ANY FAILURE AFTER SCHEDULER ACCEPTANCE CONSUMES THE AUTHORIZATION, including failure before
# the script starts. So every gate here refuses BEFORE `sbatch` is reached.
set -u -o pipefail

# BOUND TO ITS REVIEWED COMMIT, with the limit of that binding stated rather than implied.
#
# ⚠ THE PIN WAS STALE AND THIS IS THE FIX. It read ad0ab9e0, but 9ad0439d subsequently MODIFIED
# this file (the binding gate and the F7 completion), so the pin named a revision whose content
# was not what runs -- exactly the defect the pin exists to prevent, produced by the commit that
# added it. Re-pinned to 9ad0439d, where this file's EXECUTABLE content settled: the diff
# `git diff 9ad0439d -- nd-unfolding/submit_z_pilot_a5.sh` must contain the REVIEWED_COMMIT line
# and THIS COMMENT BLOCK and no other change -- zero executable lines. (An earlier wording here
# claimed "the only difference is the pin line", which this very comment falsified. Checkable
# form: strip comments from both sides and the diff must be exactly the pin assignment.)
# A commit pin cannot name the commit that contains it, for the same reason a file cannot contain
# its own digest.
# This procedure is transferred standalone to a login node -- the reviewed deployment at
# fb9ec356 predates it and MUST NOT CHANGE -- so there is no git checkout beside it to diff
# against. Therefore:
#   * the LIBRARY it depends on is pinned BY DIGEST and verified below. That is the part that
#     was broken, is now tested, and carries no self-reference.
#   * this file records its OWN digest into the submission record for audit. It does NOT
#     verify it: a file cannot contain the digest of itself, and pretending otherwise would be
#     a check that cannot fail. Compare the recorded digest against the reviewed commit.
REVIEWED_COMMIT=9ad0439d5bfa8e755f7106de124931b32eb7fb44
REVIEWED_LIB_SHA256=2e85555a804265369ee86125853fef34d824565840b1dc9530d12904e6dd8f9b
SELF_REL=nd-unfolding/submit_z_pilot_a5.sh

DEPLOY=/pscratch/sd/j/josephrb/zdeploy-fb9ec356
DEPLOY_SHA=fb9ec3560fd6d62295dffc81b5694c9e26667d5b
DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
R="${DATA_ROOT}/nd-unfolding"
NS=/pscratch/sd/j/josephrb/zpilot-20260916
RUN_ID=z-pilot-20260916-a5
PILOT_OUT="${R}/uq_5d/z_pilot_20260916_a5"
LOGDIR="${NS}/logs-a5"
WALL=01:30:00
CPUS=4
MEM=64G
CAP_CPU_TASK_HOURS=1.5

export MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env

# `sha256sum` is GNU-only; the author's local shell has BSD `shasum`. Both are tried so the
# binding gates are exercisable off-target, which is how the incomplete F7 fix was found.
mnv_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d" " -f1
  elif command -v shasum    >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d" " -f1
  else echo ""; fi
}
say()  { echo "[submit] $*"; }
die()  { echo "[submit] REFUSING: $*" >&2; exit "${2:-1}"; }

say "procedure starting $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname)"

# --- binding gate --------------------------------------------------------------------------
# Both halves of the binding refuse here, before `setup_salloc_env.sh` is sourced. Previously
# the library-digest placeholder was checked after that source, so an unbound procedure exited
# 20 ("setup_salloc_env.sh failed") off-target -- a refusal that named the wrong cause.
case "${REVIEWED_COMMIT}" in
  __REVIEWED_*) die "this procedure is not bound to a reviewed commit yet" 10 ;;
  # A provenance claim goes into the record verbatim, so it must be a full revision: `main`,
  # an abbreviation and the empty string were all accepted before.
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) ;;
  *) die "REVIEWED_COMMIT '${REVIEWED_COMMIT}' is not a 40-hex revision" 12 ;;
esac
case "${REVIEWED_LIB_SHA256}" in
  __REVIEWED_*) die "the sanitizer library digest is not pinned yet" 11 ;;
esac
SELF_SHA="$(mnv_sha256 "${BASH_SOURCE[0]}")"
say "procedure self digest ${SELF_SHA:-<unavailable>} (recorded, NOT self-verified)"
say "procedure reviewed at ${REVIEWED_COMMIT}"

# --- 0a. VERIFY AND LOAD THE SANITIZER BEFORE ANYTHING EXTERNAL IS SOURCED ---------------
# F7, completed. The placeholder refusals were moved up but the DIGEST COMPARISON was left
# below `setup_salloc_env.sh`, so off-target a tampered library exited 20 ("setup_salloc_env.sh
# failed") instead of 51 -- a refusal naming the wrong cause, which is the defect F7 was about.
# Nothing here needs the environment: only the file and a digest tool.
LIB_SANITIZE="$(dirname "${BASH_SOURCE[0]}")/lib_mnv_path_sanitize.sh"
[ -f "${LIB_SANITIZE}" ] || die "lib_mnv_path_sanitize.sh not found beside this procedure" 50
LIB_SHA="$(mnv_sha256 "${LIB_SANITIZE}")"
[ -n "${LIB_SHA}" ] || die "no sha256 tool available to verify the sanitizer library" 57
[ "${LIB_SHA}" = "${REVIEWED_LIB_SHA256}" ] \
  || die "sanitizer library digest ${LIB_SHA} != reviewed ${REVIEWED_LIB_SHA256}" 51
say "sanitizer library verified by digest: ${LIB_SHA}"
source "${LIB_SANITIZE}" || die "cannot source ${LIB_SANITIZE}" 52


# --- 0. the environment closure, exactly as the launcher will source it -------------------
set +u
source "${MNV_ENV_ROOT}/setup_salloc_env.sh" || die "setup_salloc_env.sh failed" 20
set -u

# --- 1. SANITIZE PATH, WITHOUT WIDENING THE ALLOWLIST --------------------------------------
# The allowlist is READ FROM THE GUARD LIBRARY, not retyped: a hand-copied copy of a guard
# table in this campaign had already drifted to 9 of 11 names once.
# ⚠ THE LIBRARY DEFERS TO THE ENVIRONMENT, AND A WORD COUNT DOES NOT NOTICE.
# lib_mnv_env_pathcheck.sh:41 is `MNV_ENV_SYSTEM_PREFIXES="${MNV_ENV_SYSTEM_PREFIXES:-...}"`,
# so an ambient value WINS. Measured: exporting
#   MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/homes"
# is 8 words, passed the old count-only gate, and the sanitizer then dropped NOTHING -- a
# silent recurrence of exactly what refused job 58403564. And this is realistic: a sibling
# launcher, sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh:18, documents the variable as the
# submitter-declared allowlist "including required home prefixes" and :35 requires it.
# So: UNSET it, take the library's own default, and compare against the default READ OUT OF
# THE LIBRARY TEXT rather than retyped here.
PATHCHECK_LIB="${DEPLOY}/nd-unfolding/lib_mnv_env_pathcheck.sh"
[ -f "${PATHCHECK_LIB}" ] || die "pathcheck library not found at ${PATHCHECK_LIB}" 21
ALLOW_EXPECTED="$(sed -n 's/^MNV_ENV_SYSTEM_PREFIXES="${MNV_ENV_SYSTEM_PREFIXES:-\(.*\)}"$/\1/p' "${PATHCHECK_LIB}")"
[ -n "${ALLOW_EXPECTED}" ] || die "cannot read the allowlist default out of ${PATHCHECK_LIB}" 22
if [ -n "${MNV_ENV_SYSTEM_PREFIXES:-}" ]; then
  say "⚠ an ambient MNV_ENV_SYSTEM_PREFIXES was set and is being UNSET: ${MNV_ENV_SYSTEM_PREFIXES}"
fi
unset MNV_ENV_SYSTEM_PREFIXES
source "${PATHCHECK_LIB}" || die "cannot source pathcheck lib" 23
[ "${MNV_ENV_SYSTEM_PREFIXES:-}" = "${ALLOW_EXPECTED}" ] \
  || die "allowlist is '${MNV_ENV_SYSTEM_PREFIXES:-}', library default is '${ALLOW_EXPECTED}'" 24
n_allow=$(echo ${MNV_ENV_SYSTEM_PREFIXES} | wc -w)
[ "${n_allow}" -eq 8 ] || die "allowlist is ${n_allow} prefixes, expected 8; the library changed" 55
say "allowlist (library default, ambient value discarded): ${n_allow} -- ${MNV_ENV_SYSTEM_PREFIXES}"

# ONE IMPLEMENTATION, SOURCED -- not a loop here plus a copy in the test. See the header of
# lib_mnv_path_sanitize.sh: the inlined version set IFS=':' for the PATH split while the
# predicate splits the allowlist on WHITESPACE, so the allowlist loop ran ONCE over the whole
# string and dropped /usr/bin, /bin, /opt/cray/pe/bin and /global/common/software/nersc/bin.
# The duplicate in the test never saw that IFS and passed 14/14.
PATH_ORIG="$PATH"
mnv_sanitize_path "$PATH_ORIG"
CLEAN="$MNV_PATH_CLEAN"; DROPPED="$MNV_PATH_DROPPED"
say "PATH entries ${MNV_PATH_N_BEFORE} -> ${MNV_PATH_N_AFTER}; dropped $((MNV_PATH_N_BEFORE-MNV_PATH_N_AFTER))"
for _d in ${DROPPED}; do say "  dropped: ${_d}"; done
[ "${MNV_PATH_N_AFTER}" -gt 0 ] || die "sanitization emptied PATH" 53
export PATH="$CLEAN"

# ⚠ H1: NOTHING PREVIOUSLY STOPPED A SECOND ASSIGNMENT AFTER THIS LINE. A closure check
# appended `export PATH="${PATH}:${HOME}/bin"` here and the suite passed 42/0 -- the executed
# block's anchor ends AT the line above, so anything after it was never run, and the negative
# grep matched only two specific spellings. The measured result re-added a $HOME entry after
# sanitising it away: the exact defect class that refused job 58403564. The test now asserts
# `export PATH=` occurs EXACTLY ONCE in the comment-stripped procedure, and this marker is the
# end anchor for the executed block so the tools check is inside it.
# --- end of the PATH block ---

# The tools this procedure and the job both need must survive sanitization.
for t in sbatch scontrol sacct python3 git; do
  command -v "$t" >/dev/null 2>&1 || die "sanitization removed ${t} from PATH" 54
done
say "tools after sanitization: $(for t in sbatch scontrol sacct python3 git; do printf '%s=%s ' "$t" "$(command -v "$t")"; done)"
# --- PATH handling ends here; the executed-block anchor in the test stops at this marker ---
# MNV_PATH_BLOCK_END

# --- 2. the deployment conditions ----------------------------------------------------------
cd "${DEPLOY}" || die "deployment not reachable" 25
head_now="$(git rev-parse HEAD)"
[ "${head_now}" = "${DEPLOY_SHA}" ] || die "deployment HEAD is ${head_now}, expected ${DEPLOY_SHA}" 26
dirty="$(git status --porcelain | wc -l)"
[ "${dirty}" -eq 0 ] || die "deployment is dirty (${dirty} line(s))" 27
say "deployment ${DEPLOY} HEAD ${head_now} porcelain ${dirty}"
# A count printed and never compared is a report shaped like a check.
_wrap_x=$(find "${DEPLOY}/nd-unfolding/mnv_guard_shim/bin" -type f -perm -u+x | wc -l | tr -d ' ')
_wrap_n=$(find "${DEPLOY}/nd-unfolding/mnv_guard_shim/bin" -type f | wc -l | tr -d ' ')
[ "${_wrap_x}" -eq "${_wrap_n}" ] && [ "${_wrap_n}" -gt 0 ] \
  || die "guard PATH wrappers: only ${_wrap_x} of ${_wrap_n} are executable" 56
say "shim wrappers executable: ${_wrap_x} of ${_wrap_n} (checked, not just reported)"

# --- 3. GENERATE ENV PROVENANCE UNDER THE SANITIZED ENVIRONMENT ----------------------------
mkdir -p "${NS}" "${NS}/inv-a5" "${LOGDIR}" || die "cannot create run directories" 28
ENVPROV="${NS}/env-provenance-a5.json"
SRCMAN="${NS}/source-manifest-a5.json"
python3 "${DEPLOY}/nd-unfolding/mnv_env_provenance.py" --emit "${ENVPROV}" \
  || die "env-provenance --emit failed" 29
say "env provenance emitted under the SANITIZED environment: ${ENVPROV}"

# --- 4. THE CHECKS, IN THIS SHELL ----------------------------------------------------------
python3 "${DEPLOY}/nd-unfolding/mnv_env_provenance.py" --check "${ENVPROV}" \
  || die "env-provenance --check disagrees with the record just emitted" 30
say "env-provenance --check: OK"

mnv_env_pathcheck "${MNV_ENV_ROOT}" "${DEPLOY}" "${DATA_ROOT}" \
  || die "mnv_env_pathcheck refused THIS shell; sanitization is insufficient" 31
say "mnv_env_pathcheck: OK in the submitting shell"
# NOTE, fail-safe and unrepaired: this sanitizer matches prefixes TEXTUALLY while
# mnv_env_pathcheck canonicalizes both sides (lib_mnv_env_pathcheck.sh:83-95). So a path like
# /opt/../tmp/evil is kept here and would be rejected there. The disagreement can only make
# the gate above refuse BEFORE sbatch, never admit something it should not, so it is recorded
# rather than fixed -- fixing it means canonicalizing in two places that must then agree.

python3 "${DEPLOY}/nd-unfolding/mnv_source_manifest.py" --repo "${DEPLOY}" \
  --write "${SRCMAN}" --label zdeploy-fb9ec356-a5 \
  --require-clean --require-checkout --require-no-nested-checkout \
  --require-not-nested --require-readonly || die "A-2 source manifest write/requirements failed" 32
python3 "${DEPLOY}/nd-unfolding/mnv_source_manifest.py" --repo "${DEPLOY}" \
  --compare "${SRCMAN}" --require-clean --require-checkout \
  --require-no-nested-checkout --require-not-nested --require-readonly \
  || die "A-2 source manifest comparison failed" 33
say "A-2 source manifest: written and IDENTICAL"

# --- 5. accounting and admission -----------------------------------------------------------
RECEIPT="${NS}/r5-receipt-a5.json"
python3 "${DEPLOY}/docs/orchestration/r5_meter.py" measure --write "${RECEIPT}" >/dev/null 2>&1 \
  || die "r5_meter measure failed" 34
python3 - "$RECEIPT" <<'PY' || exit 35
import json, sys
d = json.load(open(sys.argv[1])); s = d["spend"]
print("[submit] accounting %s  cpu %.5f headroom %.5f  gpu %.5f headroom %.5f  fired %s"
      % (d["measured_at_utc"], s["cpu_task_hours"], d["headroom"]["cpu_task_hours"],
         s["gpu_task_hours"], d["headroom"]["gpu_task_hours"], d["fired"]))
if d["fired"]["any"]:
    print("[submit] REFUSING: an R5 boundary has fired", file=sys.stderr); sys.exit(1)
PY
python3 "${DEPLOY}/docs/orchestration/r5_meter.py" check --receipt "${RECEIPT}" \
  --cpu-task-hours "${CAP_CPU_TASK_HOURS}" --gpu-task-hours 0 \
  || die "R5 admission refused ${CAP_CPU_TASK_HOURS} CPU task-hours" 36
say "R5 admission: OK for ${CAP_CPU_TASK_HOURS} CPU task-hours, 0 GPU"

# --- 6. freshness, immediately before submission -------------------------------------------
[ -e "${PILOT_OUT}" ] && die "namespace ${PILOT_OUT} already exists" 37
say "namespace ${PILOT_OUT} is fresh"
[ -z "${MNV_Z_PILOT_REHEARSE:-}" ] || die "MNV_Z_PILOT_REHEARSE is set; this is a pilot" 38
for f in "${LOGDIR}/z_pilot5d_a5.out" "${LOGDIR}/z_pilot5d_a5.err"; do
  [ -e "$f" ] && die "log path ${f} already exists" 39
done
# ABSOLUTE and WRITABLE, proven by probe rather than assumed -- a relative --output against a
# read-only CWD is what cancelled 58403491 before its script ran.
probe="${LOGDIR}/.writeprobe.$$"
: > "${probe}" || die "log directory ${LOGDIR} is not writable" 40
rm -f "${probe}"
say "log directory ${LOGDIR} verified writable by probe"

# --- 7. ASSEMBLE the final job settings, then record THOSE ---------------------------------
# Assembled BEFORE being recorded, and executed from the same arrays that were recorded, so the
# record cannot describe a different command than the one submitted. The previous version wrote
# hand-typed `echo` lines describing the intended flags and then submitted a separately spelled
# command -- two spellings that could drift apart silently.
SCRIPT="${DEPLOY}/nd-unfolding/sbatch_z_pilot_5d.sh"
OUT_LOG="${LOGDIR}/z_pilot5d_a5.out"
ERR_LOG="${LOGDIR}/z_pilot5d_a5.err"

SBATCH_ARGS=(
  --parsable
  --chdir="${R}"
  --output="${OUT_LOG}"
  --error="${ERR_LOG}"
  --time="${WALL}"
  --cpus-per-task="${CPUS}"
  --mem="${MEM}"
  --no-requeue
)
MNV_ASSIGNMENTS=(
  MNV_CODE_ROOT="${DEPLOY}"
  MNV_CONDA_PREFIX="${MNV_CONDA_PREFIX}"
  MNV_DATA_ROOT="${DATA_ROOT}"
  MNV_ENV_ROOT="${MNV_ENV_ROOT}"
  MNV_ENV_PROVENANCE="${ENVPROV}"
  MNV_SOURCE_MANIFEST="${SRCMAN}"
  MNV_GUARD_INVENTORY_DIR="${NS}/inv-a5"
  MNV_LAUNCHER_DIR="${DEPLOY}/nd-unfolding"
  MNV_Z_ACTIVE="${R}/active_universe_5d/standard/candidate/std_final5_candidate.root"
  MNV_Z_SUPPORT="${R}/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
  MNV_Z_CENTRAL="${R}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
  MNV_Z_ML="${R}/uq_cov_mlsplit_5d.root"
  MNV_Z_ML_KEY=hCov_mlsplit5d_reported
  MNV_Z_STAT="${R}/uq_cov_stat_5d.root"
  MNV_Z_STAT_KEY=hCov_stat5d_reported
  MNV_Z_PARENT="${R}/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root"
  MNV_Z_PRECURSOR_PRODUCT="${R}/uq_5d/z_precursor_20260914/unified_throw_cov_5d.root"
  MNV_Z_PRECURSOR_SHA256=09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560
  MNV_Z_PILOT_OUT="${PILOT_OUT}"
  MNV_Z_PILOT_RUN_ID="${RUN_ID}"
)

RECORD="${NS}/submission-a5.txt"
{
  echo "recorded_utc          $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host                  $(hostname)"
  echo "procedure_reviewed_at ${REVIEWED_COMMIT}"
  echo "procedure_self        ${SELF_REL}"
  echo "deployment            ${DEPLOY} @ ${DEPLOY_SHA}"
  echo "submitting_cwd        ${R}"
  echo "--- the exact submitted command, from the arrays that execute it ---"
  printf 'env'
  for _a in "${MNV_ASSIGNMENTS[@]}"; do printf ' \\\n  %q' "$_a"; done
  printf ' \\\n  sbatch'
  for _a in "${SBATCH_ARGS[@]}"; do printf ' \\\n  %q' "$_a"; done
  printf ' \\\n  %q\n' "${SCRIPT}"
  echo "--- inline MNV assignments, one per line ---"
  for _a in "${MNV_ASSIGNMENTS[@]}"; do echo "  ${_a}"; done
  echo "--- PATH ---"
  echo "PATH_original         ${PATH_ORIG}"
  echo "PATH_sanitized        ${PATH}"
  # One per line and %q-quoted: space-joined, a single dropped entry containing a space and
  # two dropped entries were indistinguishable in this record.
  echo "PATH_dropped_count    ${MNV_PATH_N_BEFORE} - ${MNV_PATH_N_AFTER}"
  while IFS= read -r _dl; do [ -n "$_dl" ] && printf 'PATH_dropped_entry    %q\n' "$_dl"; done \
    <<< "$(printf '%s' "${DROPPED}" | tr ' ' '\n')"
  echo "--- note: the job inherits the FULL environment via --export=ALL, so the MNV_* list"
  echo "--- below is not the whole story; ${ENVPROV} captures PATH and LD_LIBRARY_PATH."
  echo "--- inherited MNV_* in the submitting shell ---"
  env | grep '^MNV_' | sort | sed 's/^/  /'
} > "${RECORD}" || die "cannot write the submission record" 41
say "final settings assembled and recorded at ${RECORD}"

# --- 8. submit -----------------------------------------------------------------------------
cd "${R}" || die "cannot cd to the submitting directory ${R}" 42
say "submitting from $(pwd)"
# ⚠ NEVER ASSERT NON-ACCEPTANCE BLIND. The previous version ran sbatch in a command
# substitution and, on nonzero status, said "sbatch did not accept the submission" while
# recording nothing -- even though it was holding the id sbatch had just printed. That is the
# step-9 defect (a verdict from no data) mirrored onto the failure side, and "did not accept"
# is the one claim this procedure must never make without evidence.
set +e
SB_OUT="$(env "${MNV_ASSIGNMENTS[@]}" sbatch "${SBATCH_ARGS[@]}" "${SCRIPT}" 2> "${NS}/sbatch-a5.err")"
SB_RC=$?
# ⚠ `set +e` HERE, NOT `set -e`. This pair was written as save/restore, but line 11 sets only
# `-u -o pipefail` -- errexit was NEVER ON -- so `set -e` did not restore, it ENABLED errexit
# for the whole remainder INCLUDING step 9. With `pipefail` also on, step 9's
# `grep ... | head -1` returning nothing (a missing StdOut=/StdErr= key, exactly the Slurm
# spelling difference the comment there anticipates) then KILLED THE SCRIPT at exit 1 with the
# record file EMPTY and the "job WAS ACCEPTED / NO REPLACEMENT AUTHORIZED" banner never printed.
# MEASURED both ways: errexit on -> exit 1, 0 record lines; errexit off -> exit 45, both
# failures recorded, banner printed. For an accepted job that lost the record of a consumed
# authorization -- the failure shape F3 and step 9 both exist to prevent.
set +e
SB_ERR="$(cat "${NS}/sbatch-a5.err" 2>/dev/null || true)"
{
  echo "sbatch_exit_status    ${SB_RC}"
  echo "sbatch_stdout         ${SB_OUT}"
  echo "sbatch_stderr         ${SB_ERR}"
} >> "${RECORD}"
# `--parsable` can return `id;cluster` in a federated setup; the identity grep needs the bare id.
JOBID="${SB_OUT%%;*}"
case "${JOBID}" in
  ""|*[!0-9]*)
    echo "[submit] sbatch exit ${SB_RC}; stdout '${SB_OUT}'; stderr '${SB_ERR}'" >&2
    die "no numeric job id in sbatch stdout -- a job MAY STILL have been accepted; check \`squeue --me\` before concluding anything" 44 ;;
esac
if [ "${SB_RC}" -ne 0 ]; then
  echo "[submit] sbatch exit ${SB_RC} BUT stdout carried job id ${JOBID}; stderr '${SB_ERR}'" >&2
  die "sbatch exited ${SB_RC} while reporting job ${JOBID} -- the job MAY have been accepted; check \`squeue --me\` before concluding, and do NOT resubmit" 43
fi
say "SCHEDULER ACCEPTED: job ${JOBID}"
echo "jobid                 ${JOBID}" >> "${RECORD}"

# --- 9. VERIFY the resulting job settings ---------------------------------------------------
# ⚠ RETRIEVAL AND IDENTITY FIRST. The previous version ran `scontrol ... || true` and then
# grepped the output file. A FAILED retrieval left an error message in that file, `grep -qE
# 'gres/gpu'` found nothing, and the script printed "verified no GPU TRES" -- a success-looking
# line derived from no data at all, followed by "procedure complete". A missing record cannot
# verify the ABSENCE of anything.
SC="${NS}/scontrol-a5.txt"
VERIFY_FAILED=0
VERIFY_LOG=""
# The REASON must reach the durable record, not only the terminal: for a one-shot submission
# whose terminal may not survive, "verification_status FAIL" with no reason is unusable.
vfail()    { echo "[submit] VERIFICATION FAILURE: $*" >&2; VERIFY_LOG="${VERIFY_LOG}
  FAIL     $*"; VERIFY_FAILED=1; }
vverified(){ say "  verified $*"; VERIFY_LOG="${VERIFY_LOG}
  verified $*"; }

if ! scontrol show job "${JOBID}" > "${SC}" 2>&1; then
  vfail "scontrol show job ${JOBID} did not succeed; NO field below can be interpreted"
elif ! grep -qE "(^|[[:space:]])JobId=${JOBID}([[:space:]]|$)" "${SC}"; then
  vfail "the scontrol record does not carry JobId=${JOBID}; identity unconfirmed, fields not interpretable"
else
  say "scontrol retrieved and identity confirmed: JobId=${JOBID}"
  # ⚠ THE EXPECTED VALUES ARE CERTAIN; THE KEY SPELLINGS ARE NOT VALIDATED AGAINST A REAL
  # RECORD FROM THIS CLUSTER. Every value below is what the launcher itself declares
  # (sbatch_z_pilot_5d.sh:4-5) or what this procedure passes, so a VALUE mismatch is a real
  # finding. A missing KEY may instead be a Slurm-version spelling difference -- `NumTasks=`
  # appears nowhere else in this repository. Either way it is reported as a verification
  # failure rather than waved through, and ${SC} is preserved so a human can adjudicate.
  for kv in "Requeue=0" "Restarts=0" "TimeLimit=01:30:00" "NumTasks=1"; do
    if grep -qE "(^|[[:space:]])${kv}([[:space:]]|$)" "${SC}"; then vverified "${kv}"
    else vfail "expected ${kv} not present in the job record"; fi
  done
  # ANCHORED TO THE TRES FIELDS. An unanchored `gres/gpu` matches Command=, WorkDir= or
  # StdOut= too, so a path containing that string would read as a GPU allocation.
  if grep -qE '(^|[[:space:]])(Tres|TRES|TresPerNode|TresPerTask|TresPerJob|ReqTRES|AllocTRES)[^[:space:]]*gres/gpu' "${SC}"; then
    vfail "GPU TRES present in the job record"
  else vverified "no GPU TRES (from a retrieved, identity-matched record)"; fi
  # BOTH log paths. `sbatch_z_pilot_5d.sh:7` declares --output AND --error relative with %j,
  # so the failure that cancelled 58403491 applies identically to stderr.
  for _pair in "StdOut=${OUT_LOG}" "StdErr=${ERR_LOG}"; do
    _key="${_pair%%=*}"
    # `|| true` as well as the errexit fix above: a grep that finds nothing is an EXPECTED
    # outcome here (it is what a spelling difference looks like), not a script-ending error.
    _got="$(grep -oE "${_key}=[^[:space:]]*" "${SC}" | head -1 || true)"
    if [ "${_got}" = "${_pair}" ]; then vverified "${_got}"
    else vfail "${_key} is '${_got}', expected ${_pair}"; fi
  done
fi

{
  echo "verification_utc      $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "verification_status   $([ "${VERIFY_FAILED}" -eq 0 ] && echo PASS || echo FAIL)"
  echo "verification_detail   ${VERIFY_LOG}"
} >> "${RECORD}"

if [ "${VERIFY_FAILED}" -ne 0 ]; then
  echo "[submit] ==============================================================" >&2
  echo "[submit] PROCEDURE FAILED AT VERIFICATION. Job ${JOBID} WAS ACCEPTED by the" >&2
  echo "[submit]   scheduler and may be queued or running; its settings could NOT be" >&2
  echo "[submit]   confirmed. The single-submission authorization is CONSUMED by" >&2
  echo "[submit]   scheduler acceptance, so NO REPLACEMENT SUBMISSION IS AUTHORIZED." >&2
  echo "[submit]   Read ${SC} and ${RECORD}; do not resubmit." >&2
  echo "[submit] ==============================================================" >&2
  exit 45
fi

say "procedure complete AND VERIFIED: job ${JOBID}, settings confirmed against a retrieved record"
