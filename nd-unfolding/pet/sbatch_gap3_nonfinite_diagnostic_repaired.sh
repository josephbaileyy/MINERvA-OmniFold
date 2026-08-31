#!/bin/bash
#SBATCH --job-name=pet_g6_gap3_nfdr
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --no-requeue

set -euo pipefail

die() {
  echo "[gap3-nfd-repaired][FAIL] $*" >&2
  exit 3
}

sha_of() {
  sha256sum "$1" | awk '{print $1}'
}

validate_job_spec() {
  local job_spec=$1
  grep -Eq '(^| )NumCPUs=18( |$)' <<<"$job_spec" ||
    die "Slurm allocation is not exactly 18 CPUs"
  grep -Eq '(^| )CPUs/Task=18( |$)' <<<"$job_spec" ||
    die "Slurm CPUs per task is not exactly 18"
  grep -Eq '(^| )TimeLimit=02:00:00( |$)' <<<"$job_spec" ||
    die "Slurm time limit is not exactly two hours"
  grep -Eq 'ReqTRES=[^ ]*cpu=18([, ]|$)' <<<"$job_spec" ||
    die "Slurm request does not contain cpu=18"
  grep -Eq 'ReqTRES=[^ ]*mem=32G([, ]|$)' <<<"$job_spec" ||
    die "Slurm request does not contain mem=32G"
  grep -Eq 'TresPerTask=[^ ]*cpu=18([, ]|$)' <<<"$job_spec" ||
    die "Slurm task TRES does not contain cpu=18"
  grep -Eq '(^| )Features=cpu( |$)' <<<"$job_spec" ||
    die "Slurm allocation is not constrained to CPU nodes"
  if grep -Eiq '(ReqTRES|AllocTRES|TresPerTask)=[^ ]*gpu|Gres=[^ ]*gpu' \
    <<<"$job_spec"; then
    die "Slurm job carries a GPU resource"
  fi
}

if [[ "${1:-}" == "--validate-job-spec-file" ]]; then
  [[ $# -eq 2 ]] || die "resource-fixture mode requires exactly one path"
  [[ -f "$2" ]] || die "resource fixture is missing"
  validate_job_spec "$(<"$2")"
  echo "[gap3-nfd-repaired] resource fixture PASS"
  exit 0
fi

PREFLIGHT_ONLY=0
if [[ "${1:-}" == "--preflight-only" ]]; then
  [[ $# -eq 1 ]] || die "preflight mode accepts no additional arguments"
  PREFLIGHT_ONLY=1
elif [[ $# -ne 0 ]]; then
  die "unknown launcher arguments"
fi

: "${GAP3NFDR_CODE_REPO:?set GAP3NFDR_CODE_REPO to the immutable checkout}"
: "${GAP3NFDR_DATA_ROOT:?set GAP3NFDR_DATA_ROOT to the canonical data checkout root}"
: "${GAP3NFDR_OUTPUT_ROOT:?set GAP3NFDR_OUTPUT_ROOT to the unique output directory}"
: "${GAP3NFDR_EXPECTED_HEAD:?set GAP3NFDR_EXPECTED_HEAD to the pushed preparation commit}"
: "${GAP3NFDR_EXPECTED_LAUNCHER_SHA256:?set the committed launcher SHA-256}"
: "${GAP3NFDR_AUTHORIZATION_TOKEN:?set the one-scan authorization token}"

[[ "$GAP3NFDR_AUTHORIZATION_TOKEN" == \
  "PET-G6-GAP3-NONFINITE-DIAGNOSTIC-REPAIRED-20260831-ONE-SCAN" ]] ||
  die "authorization token mismatch"

CODE_REPO=$(realpath "$GAP3NFDR_CODE_REPO")
DATA_ROOT=$(realpath "$GAP3NFDR_DATA_ROOT")
OUTPUT_ROOT=$(realpath "$GAP3NFDR_OUTPUT_ROOT")
DIAGNOSTIC="$CODE_REPO/nd-unfolding/pet/diagnose_gap3_nonfinite_energy.py"
PREDECL="$CODE_REPO/docs/orchestration/PREDECLARATION-20260831-gate6-gap3-nonfinite-diagnostic-repaired.md"
PROPOSAL="$CODE_REPO/docs/orchestration/state/gate6-gap3-nonfinite-diagnostic-repaired-proposal-20260831.json"
TEST="$CODE_REPO/nd-unfolding/pet/test_gap3_nonfinite_diagnostic_repaired.py"
GUARD="$CODE_REPO/nd-unfolding/mnv_guarded_run.py"
LAUNCHER="$CODE_REPO/nd-unfolding/pet/sbatch_gap3_nonfinite_diagnostic_repaired.sh"

EXPECTED_DIAGNOSTIC_SHA256="e4db4f96ff6e8a03171d2402c0e87972262ea393f414dbba13cb8d59975a7a1d"
EXPECTED_PREDECL_SHA256="787fb636533a05fec62eab9f7aecc59d878f4d32e047e2b13bc381f700c3dd9a"
EXPECTED_PROPOSAL_SHA256="73af7db6b06edf2cc53ccc2d6e18e48730d57f0190719ad48229e7987ce686d5"
EXPECTED_TEST_SHA256="ed63797fa6b4f3d8dde6d154ae11c20de87d09d3253fc97841848681f5dffe66"
EXPECTED_GUARD_SHA256="145711eb5a247faf7bb5643a47b0f8be6e7ac2f95de0c43c12d3de1105f544c7"
EXPECTED_DUMPER_SHA256="c8fa219f0ca2537bddc8ad824a0d225c3b67cd76cab1cab1bc391f5bdd7cac5d"
EXPECTED_LOADER_SHA256="e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
EXPECTED_MODEL_SHA256="f793e53749d5754e11a7877a743ed6090b45e941c29c6162927fce74894cb953"
EXPECTED_GATE6_RECEIPT_SHA256="8f40541f1d8fec92b0e37885b1d24b851843d06f4c220f8de5ad1bc47265b6a5"
EXPECTED_PRIOR_PREDECL_SHA256="fc1772058469a34293ba1d8a162c1fe3b6cd3c2ade6c7bd31a65a39bda06c648"
EXPECTED_PRIOR_LAUNCHER_SHA256="ffadc05bd186d950b718be3f7e4e8d9e9a9563b771ea2cb3097cc6e933cd16db"
EXPECTED_PRIOR_LAUNCH_RECEIPT_SHA256="48a638a593eed9e3ebe9c9fc62da6c6e721816aa1bf4c49c4c2a18e229403015"
EXPECTED_PRIOR_TERMINAL_RECEIPT_SHA256="42e2609ebc8c7cf4c0a9b501935b9df94a18549f5deae9e78c12b1a9cd1d09ef"
EXPECTED_PRIOR_RESULT_SHA256="7c8ff0dc0baa4fd03d29534a2a24558f7705d2e9cd914aa219e528071e0cbf6e"
EXPECTED_MAPPING_REPAIR_PROPOSAL_SHA256="b59569787c088f80f5c03d3e356cc212e823ba010f7bc4c89a5c2f84d667c358"
EXPECTED_FAILED_DIAGNOSTIC_PREDECL_SHA256="679ea7f9d10f1c5f5fa1e6b9fd4ca818175070dadd69c5073a8bf63a435ecf59"
EXPECTED_FAILED_DIAGNOSTIC_PROPOSAL_SHA256="3229afc3828e3b3e9db356ce685bdc0c3156ff79118f5e82e62814288e66ebf9"
EXPECTED_FAILED_DIAGNOSTIC_LAUNCHER_SHA256="c84871436a9f03a0c1f6b927a3a321c682b497d0d0473b8b1101cc3e551951d7"
EXPECTED_FAILED_DIAGNOSTIC_LAUNCH_RECEIPT_SHA256="f43a8c45c1ca5e8a35cd1da4dcfa5e62363b78c75a21395b7f09b8f9412c696e"
EXPECTED_FAILED_DIAGNOSTIC_TERMINAL_RECEIPT_SHA256="a0220ef3fcb375fdc783ef550922816669cc785a06683b569a5e9668171cbdd0"

[[ -d "$CODE_REPO/.git" || -f "$CODE_REPO/.git" ]] || die "code root is not a git worktree"
[[ "$(git -C "$CODE_REPO" rev-parse HEAD)" == "$GAP3NFDR_EXPECTED_HEAD" ]] ||
  die "code HEAD mismatch"
[[ -z "$(git -C "$CODE_REPO" status --porcelain)" ]] || die "code checkout is dirty"
[[ "$(sha_of "$DIAGNOSTIC")" == "$EXPECTED_DIAGNOSTIC_SHA256" ]] ||
  die "diagnostic hash mismatch"
[[ "$(sha_of "$PREDECL")" == "$EXPECTED_PREDECL_SHA256" ]] ||
  die "predeclaration hash mismatch"
[[ "$(sha_of "$PROPOSAL")" == "$EXPECTED_PROPOSAL_SHA256" ]] ||
  die "proposal hash mismatch"
[[ "$(sha_of "$TEST")" == "$EXPECTED_TEST_SHA256" ]] || die "test hash mismatch"
[[ "$(sha_of "$GUARD")" == "$EXPECTED_GUARD_SHA256" ]] || die "guard hash mismatch"
[[ "$(sha_of "$LAUNCHER")" == "$GAP3NFDR_EXPECTED_LAUNCHER_SHA256" ]] ||
  die "launcher hash mismatch"
[[ -d "$OUTPUT_ROOT" ]] || die "output root must be pre-created"

set +u
source "$DATA_ROOT/setup_salloc_env.sh"
set -u
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "python3 is not executable"
"$PYTHON_BIN" -c 'import ROOT; assert not ROOT.IsImplicitMTEnabled()' ||
  die "ROOT import or implicit-multithreading preflight failed"

export OMP_NUM_THREADS=1
export ROOT_MAX_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1

DIAGNOSTIC_ARGS=(
  --code-root "$CODE_REPO"
  --data-root "$DATA_ROOT"
  --expected-head "$GAP3NFDR_EXPECTED_HEAD"
  --expected-diagnostic-sha256 "$EXPECTED_DIAGNOSTIC_SHA256"
  --expected-predeclaration-sha256 "$EXPECTED_PREDECL_SHA256"
  --expected-proposal-sha256 "$EXPECTED_PROPOSAL_SHA256"
  --expected-test-sha256 "$EXPECTED_TEST_SHA256"
  --expected-guard-sha256 "$EXPECTED_GUARD_SHA256"
  --expected-dumper-sha256 "$EXPECTED_DUMPER_SHA256"
  --expected-loader-sha256 "$EXPECTED_LOADER_SHA256"
  --expected-model-sha256 "$EXPECTED_MODEL_SHA256"
  --expected-gate6-receipt-sha256 "$EXPECTED_GATE6_RECEIPT_SHA256"
  --expected-prior-predeclaration-sha256 "$EXPECTED_PRIOR_PREDECL_SHA256"
  --expected-prior-launcher-sha256 "$EXPECTED_PRIOR_LAUNCHER_SHA256"
  --expected-prior-launch-receipt-sha256 "$EXPECTED_PRIOR_LAUNCH_RECEIPT_SHA256"
  --expected-prior-terminal-receipt-sha256 "$EXPECTED_PRIOR_TERMINAL_RECEIPT_SHA256"
  --expected-prior-result-sha256 "$EXPECTED_PRIOR_RESULT_SHA256"
  --expected-mapping-repair-proposal-sha256 "$EXPECTED_MAPPING_REPAIR_PROPOSAL_SHA256"
  --expected-failed-diagnostic-predeclaration-sha256 "$EXPECTED_FAILED_DIAGNOSTIC_PREDECL_SHA256"
  --expected-failed-diagnostic-proposal-sha256 "$EXPECTED_FAILED_DIAGNOSTIC_PROPOSAL_SHA256"
  --expected-failed-diagnostic-launcher-sha256 "$EXPECTED_FAILED_DIAGNOSTIC_LAUNCHER_SHA256"
  --expected-failed-diagnostic-launch-receipt-sha256 "$EXPECTED_FAILED_DIAGNOSTIC_LAUNCH_RECEIPT_SHA256"
  --expected-failed-diagnostic-terminal-receipt-sha256 "$EXPECTED_FAILED_DIAGNOSTIC_TERMINAL_RECEIPT_SHA256"
  --threads 1
)

if [[ "$PREFLIGHT_ONLY" == "1" ]]; then
  [[ -z "${SLURM_JOB_ID:-}" ]] || die "preflight mode must run before submission"
  PREFLIGHT="$OUTPUT_ROOT/preflight.json"
  [[ ! -e "$PREFLIGHT" && ! -L "$PREFLIGHT" ]] || die "preflight output is occupied"
  TEMP_PREFLIGHT="$OUTPUT_ROOT/.preflight.$$.tmp"
  trap 'rm -f "$TEMP_PREFLIGHT"' EXIT
  "$PYTHON_BIN" "$GUARD" --expect-root "$CODE_REPO" -- "$DIAGNOSTIC" \
    "${DIAGNOSTIC_ARGS[@]}" --preflight-only >"$TEMP_PREFLIGHT"
  mv "$TEMP_PREFLIGHT" "$PREFLIGHT"
  trap - EXIT
  echo "[gap3-nfd-repaired] preflight PASS sha256=$(sha_of "$PREFLIGHT")"
  exit 0
fi

[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run inside one Slurm job"
[[ -z "${SLURM_ARRAY_TASK_ID:-}" ]] || die "job arrays are forbidden"
[[ "${SLURM_CPUS_PER_TASK:-}" == "18" ]] || die "expected exactly 18 allocated CPUs"
[[ -z "${SLURM_JOB_GPUS:-}" ]] || die "GPU allocation is forbidden"
[[ -z "${SLURM_GPUS_ON_NODE:-}" ]] || die "GPU node allocation is forbidden"

RESULT="$OUTPUT_ROOT/result-${SLURM_JOB_ID}.json"
[[ ! -e "$RESULT" && ! -L "$RESULT" ]] || die "refuse occupied result path"
JOB_SPEC=$(scontrol show job -o "$SLURM_JOB_ID")
validate_job_spec "$JOB_SPEC"
printf '%s\n' "$JOB_SPEC" >"$OUTPUT_ROOT/job-spec-${SLURM_JOB_ID}.txt"

echo "[gap3-nfd-repaired] contract=PET-G6-GAP3-NONFINITE-DIAGNOSTIC-REPAIRED-20260831"
echo "[gap3-nfd-repaired] job=$SLURM_JOB_ID head=$GAP3NFDR_EXPECTED_HEAD"
echo "[gap3-nfd-repaired] source_identity_threads=1 implicit_multithreading=false"
echo "[gap3-nfd-repaired] result=$RESULT"

"$PYTHON_BIN" "$GUARD" --expect-root "$CODE_REPO" -- "$DIAGNOSTIC" \
  "${DIAGNOSTIC_ARGS[@]}" --output "$RESULT"

[[ -s "$RESULT" ]] || die "diagnostic did not publish a result"
echo "[gap3-nfd-repaired] DONE result_sha256=$(sha_of "$RESULT")"
