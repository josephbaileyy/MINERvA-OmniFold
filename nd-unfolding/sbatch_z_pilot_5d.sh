#!/bin/bash
#SBATCH --job-name=z_pilot5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=64G --time=01:30:00
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/z_pilot5d_%j.out --error=uq_5d/z_pilot5d_%j.err
# Z assembly/spectrum pilot. Transcribes the precursor's persisted ROOT null operands into the
# build reader's NPZ slab, builds BOTH centering variants through the existing z_build CLI, and
# persists both eigenvalue spectra. Construction only: the outcome is permanently NON-PASSING and
# NON-ADOPTABLE, and nothing here grades, adopts or projects anything.
set -eo pipefail

# --- `#SBATCH --no-requeue` IS PRESENT HERE, AND THAT DIFFERS FROM THE FOUR PRECURSOR LAUNCHERS ---
# Those four are SHARED -- archive reproduction and the member-axis path call them -- so adding the
# header there would have changed behaviour for callers the authorization did not cover, which is
# why they carry the refusal as a submission flag and a recorded note instead. THIS launcher is new
# and has exactly one caller, so the header changes nothing but this pilot and cannot surprise a
# non-Z caller. Joseph's Stage-1 scope names `--no-requeue` as a property of the guarded launcher.
# STILL VERIFY IT ON THE JOB. `scontrol show job <id> | grep Requeue=` is the only thing that
# establishes the setting took effect; a header in a file is an intention. Re-measure the site
# default (`scontrol show config | grep JobRequeue`) rather than quoting any number from a comment.

CODE_ROOT="${MNV_CODE_ROOT:?set MNV_CODE_ROOT to the approved clean execution tree -- a checkout at a named sha with git status --porcelain empty. It is NOT the data root.}"
DATA_ROOT="${MNV_DATA_ROOT:?set MNV_DATA_ROOT to the tree holding the inputs for this leg and receiving its products. Nothing is executed or imported from it.}"
ENV_ROOT="${MNV_ENV_ROOT:?set MNV_ENV_ROOT to the verified environment tree -- a real directory OUTSIDE every repository checkout, holding the activation closure named by nd-unfolding/mnv_env_manifest.tsv. It has NO default.}"
ENV_MANIFEST="${MNV_ENV_MANIFEST:-${CODE_ROOT}/nd-unfolding/mnv_env_manifest.tsv}"
: "${MNV_CONDA_PREFIX:?set MNV_CONDA_PREFIX to the conda env whose activate.d scripts the manifest binds. It has no default.}"

# ⚠ NO APOSTROPHE MAY APPEAR INSIDE ANY `${VAR:?...}` MESSAGE IN THIS BLOCK. On bash 4.4.23
# (Perlmutter; a local 3.2 cannot see it) an apostrophe inside `${VAR:?word}` within double quotes
# opens a single-quote context THAT SPANS NEWLINES. Job 58347943 died in 4 s because line 34's
# "that product's" swallowed line 35 whole and closed on line 36's "run's", consuming the
# PILOT_OUT and Z_RUN_ID assignments outright -- so their `:?` guards never evaluated, the
# variables were unset rather than refused, and the first symptom was `mkdir -p ''` forty-seven
# lines downstream. Measured with a three-line reproducer: put an apostrophe in the FIRST
# guard message and the SECOND and THIRD variables come back empty; remove it and all three
# bind. The example is described rather than written out, because a comment containing the
# literal pattern would trip any detector for it -- the same decoy problem that let a prose
# mention of `#SBATCH --no-requeue` satisfy a test for the directive.
# apostrophe Y binds. The guards below are only load-bearing while this line stays true, and
# tests/test_z_pilot_launcher_init.py enforces it by EXECUTING this block, not by reading it.
# The pilot operands. All have no default, for the same reason the precursor operands do not:
# a defaulted output namespace would put one run over another, and a defaulted input would let this
# run choose its own evidence.
PRODUCT="${MNV_Z_PRECURSOR_PRODUCT:?set MNV_Z_PRECURSOR_PRODUCT to the completed precursor combine product (unified_throw_cov_5d.root). No default: the pilot must not select its own input.}"
PRODUCT_SHA="${MNV_Z_PRECURSOR_SHA256:?set MNV_Z_PRECURSOR_SHA256 to that product authorized sha256. No default: a digest computed here would compare the file to itself.}"
PILOT_OUT="${MNV_Z_PILOT_OUT:?set MNV_Z_PILOT_OUT to a FRESH output directory for this pilot. No default, and it must not already contain pilot artifacts.}"
Z_RUN_ID="${MNV_Z_PILOT_RUN_ID:?set MNV_Z_PILOT_RUN_ID to this pilot run identifier, recorded in the manifest. No default.}"

# The four remaining source roles Z needs and the precursor does NOT supply. Each is an existing
# digest-bound artifact; none is produced here, and none may be defaulted.
Z_CENTRAL="${MNV_Z_CENTRAL:?set MNV_Z_CENTRAL to the declared production CV file (hXSecND_flat).}"
Z_SUPPORT="${MNV_Z_SUPPORT:?set MNV_Z_SUPPORT to the V/R support file carrying hCov_universe5d_<band> keys.}"
Z_ACTIVE="${MNV_Z_ACTIVE:?set MNV_Z_ACTIVE to the five-band active file carrying the candidate band keys and the active total.}"
Z_STAT="${MNV_Z_STAT:?set MNV_Z_STAT to the statistical covariance file.}"
Z_ML="${MNV_Z_ML:?set MNV_Z_ML to the ML covariance file.}"
Z_PARENT="${MNV_Z_PARENT:?set MNV_Z_PARENT to the parent candidate file. Its lineage stays UNVERIFIED; only its identity is bound.}"
Z_STAT_KEY="${MNV_Z_STAT_KEY:?set MNV_Z_STAT_KEY to the exact covariance key inside MNV_Z_STAT.}"
Z_ML_KEY="${MNV_Z_ML_KEY:?set MNV_Z_ML_KEY to the exact covariance key inside MNV_Z_ML.}"

# --- FRESH OUTPUTS, REFUSED RATHER THAN CLEANED -------------------------------------------------
# Non-emptiness REFUSES. The same rule the precursor's namespace check uses: a pilot that cleared
# its own output directory would destroy the evidence of whatever ran there before, and "it was
# probably mine" is not a property of a filesystem.
# CANNOT-LOOK IS NOT EMPTY. The first version ended `ls -A ... 2>/dev/null`, so a directory this
# job may enter and write but not READ (mode 300) produced empty output and the check PROCEEDED --
# a zero that means "I could not look" read as "there is nothing there". The status is read from
# `ls` directly and NOT through a pipe, because a pipe would hand back the pipe's status instead.
if [ -e "${PILOT_OUT}" ] && [ ! -d "${PILOT_OUT}" ]; then
  echo "[z-pilot] FAIL: ${PILOT_OUT} exists and is not a directory." >&2
  exit 3
fi
if [ -d "${PILOT_OUT}" ]; then
  # ⚠ THE `if !` FORM IS LOAD-BEARING UNDER `set -e`. Written as
  #     _mnv_listing=$(ls -A "$PILOT_OUT"); _mnv_ls_rc=$?
  # bash aborts AT THE ASSIGNMENT when the substitution fails, so `_mnv_ls_rc` was never read: the
  # refusal happened (fail-closed) but with `ls`'s status instead of 3 and with the operator
  # diagnostic never printed. Worse, GNU `ls` documents status 2 for an unreadable directory named
  # as an argument -- the same integer this launcher just established as "construction complete,
  # science NON-PASSING". A condition is exempt from `set -e`, so the status is ours again.
  if ! _mnv_listing=$(ls -A "${PILOT_OUT}"); then
    echo "[z-pilot] FAIL: cannot list ${PILOT_OUT}. That is CANNOT-LOOK, not" >&2
    echo "[z-pilot]   empty, and it must not be read as a fresh namespace." >&2
    exit 3
  fi
  if [ -n "$_mnv_listing" ]; then
    echo "[z-pilot] FAIL: ${PILOT_OUT} exists and is NOT empty. Name a fresh directory." >&2
    echo "[z-pilot]   It is not cleaned: removing another run's products to make room is not" >&2
    echo "[z-pilot]   this launcher's call, and an emptied directory cannot be told from a new one." >&2
    exit 3
  fi
fi
unset _mnv_listing
mkdir -p "${PILOT_OUT}"

# (1)-(4) THE SAME ENVIRONMENT CLOSURE THE PRECURSOR USED. Not re-derived: these are the existing
# libraries, called with the existing arguments. NO `set -u` -- the closure reaches conda's
# activate-binutils_linux-64.sh, which references unset variables.
source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_preflight.sh"
mnv_env_preflight "$ENV_MANIFEST" "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?
source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_pathcheck.sh"
source "${ENV_ROOT}/setup_salloc_env.sh"
mnv_env_pathcheck "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 7) else 9)' 2>/dev/null; then
  echo "[z-pilot] FAIL: the active interpreter cannot run the preflight tools (need 3.7+)." >&2
  echo "[z-pilot]   $(command -v python3 || echo '<none on PATH>'): $(python3 -V 2>&1 || true)" >&2
  echo "[z-pilot]   This is an ENVIRONMENT fault, not a wrong-tree fault. Do not read it as one." >&2
  exit 3
fi
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# --- BLAS THREAD CAP, AND IT IS NOT COSMETIC -----------------------------------------------------
# MEASURED on a 244-core login node at n=2800: 0.480 s with OMP_NUM_THREADS=16 against 4.248 s with
# it UNSET -- ~9x, the wrong way, because an OpenBLAS that reads the node's core count rather than
# the cgroup spawns a thread per visible core onto the few this job was given and thrashes. Every
# cost estimate for this pilot assumes the capped rate, so leaving it unset would make the wall
# limit a measurement of oversubscription. 32 sibling launchers in this directory set these three.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export OPENBLAS_NUM_THREADS="${OMP_NUM_THREADS}"
export MKL_NUM_THREADS="${OMP_NUM_THREADS}"
cd "${DATA_ROOT}/nd-unfolding"

GUARD="${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py"
PARITY="${CODE_ROOT}/nd-unfolding/pet/verify_executing_copy_is_committed.py"
SRCMAN="${CODE_ROOT}/nd-unfolding/mnv_source_manifest.py"
ENVPROV="${CODE_ROOT}/nd-unfolding/mnv_env_provenance.py"
INVDIR="${MNV_GUARD_INVENTORY_DIR:?set MNV_GUARD_INVENTORY_DIR to a run-scoped directory for the OI-136 resolved-origin records.}"
SRCMAN_RECORD="${MNV_SOURCE_MANIFEST:?set MNV_SOURCE_MANIFEST to the A-2(f) source manifest recorded from MNV_CODE_ROOT before this sbatch.}"
ENVPROV_RECORD="${MNV_ENV_PROVENANCE:?set MNV_ENV_PROVENANCE to the submission-environment baseline written by mnv_env_provenance.py --emit BEFORE this sbatch.}"
for _t in "$GUARD" "$PARITY" "$SRCMAN" "$ENVPROV"; do
  [ -f "$_t" ] || { echo "[z-pilot] FAIL: missing preflight tool $_t" >&2; exit 3; }
done
mkdir -p "${INVDIR}"
mnv_inv() { echo "${INVDIR}/${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.${SLURM_ARRAY_TASK_ID:-na}.$1.jsonl"; }

# A-2(f) + A-2(c)(d)(e)(g): whole-tree question, against a snapshot recorded BEFORE this run.
python3 "$SRCMAN" --repo "$CODE_ROOT" --compare "$SRCMAN_RECORD" \
  --require-clean --require-checkout --require-no-nested-checkout \
  --require-not-nested --require-readonly || {
  echo "[z-pilot] FAIL: the execution tree is not the tree that was approved (see above)." >&2
  exit 3; }

# A-3: bind what EXECUTES. The pilot's own four modules are named here; omitting one would leave the
# file that does the work unbound while the launcher reported parity.
python3 "$PARITY" --repo "$CODE_ROOT" \
  --pair "${CODE_ROOT}/nd-unfolding/z_pilot.py=nd-unfolding/z_pilot.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_pilot_manifest_cli.py=nd-unfolding/z_pilot_manifest_cli.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_null_bridge.py=nd-unfolding/z_null_bridge.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_build.py=nd-unfolding/z_build.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_assembly.py=nd-unfolding/z_assembly.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_receipt.py=nd-unfolding/z_receipt.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_contract.py=nd-unfolding/z_contract.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_statistics.py=nd-unfolding/z_statistics.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_validator.py=nd-unfolding/z_validator.py" \
  --pair "${CODE_ROOT}/nd-unfolding/z_build_path.py=nd-unfolding/z_build_path.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_z_pilot_5d.sh=nd-unfolding/sbatch_z_pilot_5d.sh" \
  --pair "${GUARD}=nd-unfolding/mnv_guarded_run.py" \
  --pair "${PARITY}=nd-unfolding/pet/verify_executing_copy_is_committed.py" \
  --pair "${SRCMAN}=nd-unfolding/mnv_source_manifest.py" \
  --pair "${ENVPROV}=nd-unfolding/mnv_env_provenance.py" || {
  echo "[z-pilot] FAIL: deployment parity -- the executing copies are not the committed ones in $CODE_ROOT" >&2
  exit 3; }

# ⚠ THE FLAG IS `--check-inherited`, NOT `--compare`, AND JOB 58354056 DIED ON EXACTLY THAT.
# `mnv_source_manifest.py` takes `--compare`; `mnv_env_provenance.py` does not -- its verbs are
# --emit / --check / --check-inherited / --self-test. Two tools invoked four lines apart with
# different interfaces, and the first one's flag was carried onto the second. argparse rejected it,
# and the launcher then printed "the submission environment did not reach this task intact" -- a
# claim about the ENVIRONMENT when the environment was fine and the INVOCATION was malformed. A
# wrong diagnosis of a right refusal is worse than no diagnosis, so the three outcomes are now
# reported as the different things they are.
set +e
_envprov_err=$(mktemp)
python3 "$ENVPROV" --check-inherited "$ENVPROV_RECORD" \
  --record "${INVDIR}/env-provenance.${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.json" \
  2> >(tee "$_envprov_err" >&2)
_envprov_rc=$?
set -e
# ⚠ KEYED ON THE TOOL'S OWN DOCUMENTED CONTRACT, NOT ON A GUESS.
# `mnv_env_provenance.py:65` declares `EXIT_OK, EXIT_CANNOT_LOOK, EXIT_DRIFT = 0, 2, 3`.
# A REVIEWER CAUGHT THE FIRST VERSION OF THIS BLOCK GETTING TWO OF THREE WRONG, and both
# misattributions were confident:
#   * it mapped rc=2 to "MALFORMED INVOCATION". But 2 is ALSO the tool's CANNOT-LOOK -- returned
#     when the baseline is absent or unreadable (`:232-243`), which is the single most likely real
#     fault here, because MNV_ENV_PROVENANCE is emitted on a login node and read from a compute
#     node. The operator would have been sent to re-audit flags that were correct.
#   * its `*)` catch-all announced "This IS a measured mismatch" for ANY other code. The tool never
#     returns 1; a python-level crash lands there and the launcher would assert a comparison that
#     never happened.
# argparse's 2 and the tool's 2 ARE THE SAME INTEGER. The only thing that separates them is what
# was printed, so stderr is captured and read rather than guessed at.
case "$_envprov_rc" in
  0) : ;;
  3) echo "[z-pilot] FAIL: MEASURED ENVIRONMENT MISMATCH (env-provenance DRIFT, exit 3)." >&2
     echo "[z-pilot]   The tool looked and the environment disagreed with the recorded baseline:" >&2
     echo "[z-pilot]   a declared MNV_* variable was dropped or changed between submission and here." >&2
     rm -f "$_envprov_err"; exit 3 ;;
  2) if grep -q "^usage:" "$_envprov_err"; then
       echo "[z-pilot] FAIL: MALFORMED INVOCATION of mnv_env_provenance.py (argparse usage, exit 2)." >&2
       echo "[z-pilot]   NOT an environment mismatch and NOT a failure to look: the command itself" >&2
       echo "[z-pilot]   was wrong. Check the flags against THAT tool -- its verbs are --emit," >&2
       echo "[z-pilot]   --check, --check-inherited, --self-test. Job 58354056 died exactly here." >&2
       rm -f "$_envprov_err"; exit 9
     elif grep -q "COULD NOT LOOK" "$_envprov_err"; then
       echo "[z-pilot] FAIL: COULD NOT LOOK (env-provenance exit 2)." >&2
       echo "[z-pilot]   The baseline at MNV_ENV_PROVENANCE is absent or unreadable from this node." >&2
       echo "[z-pilot]   This is NOT a measured mismatch and must never be read as a clean check:" >&2
       echo "[z-pilot]   nothing was compared. Emit the baseline before sbatch and confirm the" >&2
       echo "[z-pilot]   compute node can read it." >&2
       rm -f "$_envprov_err"; exit 10
     else
       echo "[z-pilot] FAIL: env-provenance exit 2 with neither a usage block nor a" >&2
       echo "[z-pilot]   COULD-NOT-LOOK line. The outcome is INDETERMINATE and is reported as" >&2
       echo "[z-pilot]   such rather than assigned to whichever branch looks plausible." >&2
       rm -f "$_envprov_err"; exit 11
     fi ;;
  *) echo "[z-pilot] FAIL: mnv_env_provenance.py DID NOT COMPLETE (exit ${_envprov_rc})." >&2
     echo "[z-pilot]   Its contract is 0/2/3, so this is neither a measured mismatch nor a" >&2
     echo "[z-pilot]   refusal -- the tool itself failed. No claim is made about the environment." >&2
     rm -f "$_envprov_err"; exit 11 ;;
esac
rm -f "$_envprov_err"
unset _envprov_rc _envprov_err

# --- STEP 1: transcribe the precursor's ROOT null operands into the NPZ slab --------------------
NULL_SLAB="${PILOT_OUT}/z-null-source.npz"
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv z_null_bridge)" -- \
  "${CODE_ROOT}/nd-unfolding/z_null_bridge.py" \
  --product "$PRODUCT" --sha256 "$PRODUCT_SHA" --out-null "$NULL_SLAB" \
  --record "${PILOT_OUT}/bridge.json" || {
  echo "[z-pilot] FAIL: the null bridge refused. Its stderr envelope is above." >&2
  exit 4; }
[ -s "$NULL_SLAB" ] || { echo "[z-pilot] FAIL: bridge reported success and wrote no slab." >&2; exit 4; }

# --- STEP 2: the digest-bound manifest ----------------------------------------------------------
MANIFEST="${PILOT_OUT}/z-manifest.json"
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv z_manifest)" -- \
  "${CODE_ROOT}/nd-unfolding/z_pilot_manifest_cli.py" \
  --out "$MANIFEST" --provenance "${PILOT_OUT}/z-provenance.json" \
  --producing-revision "$(git -C "$CODE_ROOT" rev-parse HEAD)" \
  --run-id "$Z_RUN_ID" --run-step assembly --input-kind real \
  --parent "$Z_PARENT" --central "$Z_CENTRAL" --support "$Z_SUPPORT" --active "$Z_ACTIVE" \
  --stat "$Z_STAT" --ml "$Z_ML" --throw "$PRODUCT" --throw-sha256 "$PRODUCT_SHA" \
  --null "$NULL_SLAB" --stat-key "$Z_STAT_KEY" --ml-key "$Z_ML_KEY" || {
  echo "[z-pilot] FAIL: the manifest could not be built and bound." >&2
  exit 5; }

# --- REHEARSAL STOP POINT, AND IT DEFAULTS TO A FULL RUN ----------------------------------------
# `MNV_Z_PILOT_REHEARSE=manifest` stops here, AFTER null transcription and manifest creation and
# BEFORE any covariance assembly. Authorized 2026-09-15 for one bounded startup rehearsal, because
# three attempts had been spent on startup faults that no test reached -- the sequence above is the
# part that kept failing, and rehearsing it needs the REAL launcher rather than a reconstruction.
#
# IT WEAKENS NOTHING. Every check above still runs in full; the variable only decides whether to
# CONTINUE. Unset or any other value means a complete run, so a forgotten variable cannot silently
# truncate a production pilot, and there is a test asserting the default. A rehearsal that stopped
# here is NOT a pilot: it writes no covariance, no spectra and no pilot receipt, and says so.
if [ "${MNV_Z_PILOT_REHEARSE:-}" = "manifest" ]; then
  # ⚠ TWO HARDENINGS A REVIEWER REQUIRED, AND BOTH MATTER MORE THAN THE STOP ITSELF.
  #
  # (1) A REHEARSAL MAY ONLY RUN IN A NAMESPACE NAMED FOR ONE. `#SBATCH --export=ALL` carries the
  #     submitter's environment, so an operator who exports MNV_Z_PILOT_REHEARSE for the rehearsal
  #     and then submits the PILOT from the same shell would silently get a truncated run. The
  #     variable alone is therefore not enough: the output namespace must also say "rehearsal", so
  #     a stale variable in a pilot namespace REFUSES loudly instead of truncating quietly.
  # (2) IT EXITS NON-ZERO. Exiting 0 would make `sacct` record COMPLETED 0:0 for a run that built
  #     no covariance -- the exact state this launcher's own reviewer blocker forbids for the
  #     pilot. 12 means "rehearsal completed"; it is deliberately not 0 and not 2, because 2 is
  #     "construction complete, science NON-PASSING" elsewhere in this file.
  case "$(basename "$PILOT_OUT")" in
    *rehears*) : ;;
    *) echo "[z-pilot] FAIL: MNV_Z_PILOT_REHEARSE=manifest but the output namespace" >&2
       echo "[z-pilot]   $(basename "$PILOT_OUT") is not named for a rehearsal. Refusing rather" >&2
       echo "[z-pilot]   than truncating: a stale exported variable must not silently shorten a" >&2
       echo "[z-pilot]   pilot. Name the namespace *rehearsal* or unset the variable." >&2
       exit 13 ;;
  esac
  [ -s "$NULL_SLAB" ] || { echo "[z-pilot] FAIL: rehearsal has no null slab." >&2; exit 4; }
  [ -s "$MANIFEST" ] || { echo "[z-pilot] FAIL: rehearsal has no manifest." >&2; exit 5; }
  echo "[z-pilot] REHEARSAL STOP: startup sequence complete through manifest creation."
  echo "[z-pilot]   Verified: environment closure, source manifest, executing-copy parity,"
  echo "[z-pilot]   environment provenance, null transcription, digest-bound manifest."
  echo "[z-pilot]   NOT RUN: covariance assembly, spectra, pilot receipt. This is NOT a pilot"
  echo "[z-pilot]   result and establishes NOTHING about the science."
  echo "[z-pilot] rehearsal artifacts: $(basename "$NULL_SLAB"), $(basename "$MANIFEST")"
  echo "[z-pilot] exiting 12 = REHEARSAL COMPLETED (deliberately non-zero; a rehearsal must never"
  echo "[z-pilot]   be recorded by the scheduler as a completed pilot)."
  exit 12
fi

# --- STEP 3: build both variants and persist both spectra ---------------------------------------
# EXIT 2 IS THE COMPLETION CODE AND IT IS NOT CONVERTED. z_pilot.py validates the artifacts and
# their receipts before returning it; 1 is a refusal. Any other code is a fault in this launcher's
# own assumptions and is reported as such rather than mapped onto one of the two.
set +e
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv z_pilot)" -- \
  "${CODE_ROOT}/nd-unfolding/z_pilot.py" \
  --manifest "$MANIFEST" --out-dir "$PILOT_OUT" \
  --receipt "${PILOT_OUT}/z-pilot-receipt.json"
PILOT_RC=$?
set -e
# ⚠ TWO DIFFERENT 2s, AND THEY MUST NOT BE CONFLATED. `mnv_guarded_run.py` uses exit 2 for
# CANNOT-LOOK ("2 is deliberately not 3, so 'we could not look' can never be read as 'we checked
# and it was clean'"), and it can return 2 WITHOUT EVER RUNNING the payload. `z_pilot.py` uses 2
# for "construction complete, science NON-PASSING". Same integer, opposite meanings, and the guard
# wraps the pilot -- so the receipt the pilot writes LAST is required before 2 is read as
# completion. Without this, a refused guard prints a completed-construction line for a run that
# never happened.
case "$PILOT_RC" in
  2)
    if [ ! -s "${PILOT_OUT}/z-pilot-receipt.json" ]; then
      echo "[z-pilot] FAIL: exit 2 with no pilot receipt. That is the GUARD's CANNOT-LOOK 2, not" >&2
      echo "[z-pilot]   the pilot's completion 2 -- the payload may never have run." >&2
      exit 8
    fi
    echo "[z-pilot] construction COMPLETE, science NON-PASSING (exit 2, as specified)." ;;
  1) echo "[z-pilot] FAIL: the pilot refused (exit 1). Nothing is validated." >&2; exit 1 ;;
  *) echo "[z-pilot] FAIL: unexpected exit ${PILOT_RC}. Not mapped onto 1 or 2." >&2; exit 6 ;;
esac

# --- RECEIPT-LAST COMPLETION, CHECKED HERE TOO --------------------------------------------------
# The exit code said the pilot believed it finished. This asks the filesystem. Scheduler success
# alone is insufficient, and so is a process's own report about itself.
for _f in z-pilot-receipt.json z-receipt-cv.json z-receipt-mean.json z-cv.npz z-mean.npz z-null.npz; do
  [ -s "${PILOT_OUT}/${_f}" ] || {
    echo "[z-pilot] FAIL: exit 2 but ${_f} is absent or empty." >&2; exit 7; }
done
python3 - "$PILOT_OUT" <<'PY' || exit 7
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
r = json.loads((out / "z-pilot-receipt.json").read_text())
assert r["scientific_acceptance"] == "NON-PASSING", r["scientific_acceptance"]
assert r["adoptable"] is False, r["adoptable"]
assert r["build_returncode"] == 2, r["build_returncode"]
assert set(r["spectra"]) == {"cv", "mean"}, sorted(r["spectra"])
for v, s in r["spectra"].items():
    assert s["clipped"] is False and s["regularized"] is False, v
# The receipt must be the LAST file written: newer than every artifact it names.
rt = (out / "z-pilot-receipt.json").stat().st_mtime_ns
for name, stamp in r["artifacts"].items():
    assert Path(stamp["path"]).stat().st_mtime_ns <= rt, name
print("[z-pilot] receipt-last verified; NON-PASSING and NON-ADOPTABLE recorded.")
PY
echo "[z-pilot] done. Outputs in ${PILOT_OUT}. Nothing here is adopted, graded or projected."

# --- THE JOB'S EXIT STATUS IS THE PILOT'S, AND THIS LINE IS THE WHOLE POINT ----------------------
# ⚠ REVIEWER BLOCKER. Without it the script's last statement was an `echo`, so the script exited 0
# and `sacct` recorded COMPLETED / ExitCode 0:0 for a construction whose science is permanently
# NON-PASSING. `z_pilot.py` goes to real trouble to preserve 2 -- "returning 0 would tell a
# launcher the science passed" -- and the launcher then threw it away at the last hop, which is
# worse than never having preserved it, because the inner discipline made the outer artifact look
# trustworthy. The guard test that was supposed to forbid this asserted `"exit 0" not in text`: a
# SPELLING check, blind to an exit code arrived at by falling off the end of the file.
exit "$PILOT_RC"
