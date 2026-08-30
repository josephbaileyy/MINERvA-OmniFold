#!/bin/bash
#SBATCH --job-name=pet_g6_gap3_nfd
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
  echo "[gap3-nfd-launch][FAIL] $*" >&2
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
  echo "[gap3-nfd-launch] resource fixture PASS"
  exit 0
fi

: "${GAP3NFD_CODE_REPO:?set GAP3NFD_CODE_REPO to the immutable diagnostic checkout}"
: "${GAP3NFD_DATA_ROOT:?set GAP3NFD_DATA_ROOT to the canonical data checkout root}"
: "${GAP3NFD_OUTPUT_ROOT:?set GAP3NFD_OUTPUT_ROOT to a unique pre-created output directory}"
: "${GAP3NFD_EXPECTED_HEAD:?set GAP3NFD_EXPECTED_HEAD to the pushed preparation commit}"
: "${GAP3NFD_EXPECTED_LAUNCHER_SHA256:?set the committed launcher SHA-256}"
: "${GAP3NFD_AUTHORIZATION_TOKEN:?set the diagnostic authorization token}"

[[ "$GAP3NFD_AUTHORIZATION_TOKEN" == \
  "PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830-ONE-SCAN" ]] ||
  die "authorization token mismatch"
[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run inside one Slurm job"
[[ -z "${SLURM_ARRAY_TASK_ID:-}" ]] || die "job arrays are forbidden"
[[ "${SLURM_CPUS_PER_TASK:-}" == "18" ]] || die "expected exactly 18 CPUs"
[[ -z "${SLURM_JOB_GPUS:-}" ]] || die "GPU allocation is forbidden"
[[ -z "${SLURM_GPUS_ON_NODE:-}" ]] || die "GPU node allocation is forbidden"

CODE_REPO=$(realpath "$GAP3NFD_CODE_REPO")
DATA_ROOT=$(realpath "$GAP3NFD_DATA_ROOT")
OUTPUT_ROOT=$(realpath "$GAP3NFD_OUTPUT_ROOT")
DIAGNOSTIC="$CODE_REPO/nd-unfolding/pet/diagnose_gap3_nonfinite_energy.py"
PREDECL="$CODE_REPO/docs/orchestration/PREDECLARATION-20260830-gate6-gap3-nonfinite-diagnostic.md"
PROPOSAL="$CODE_REPO/docs/orchestration/state/gate6-gap3-nonfinite-diagnostic-proposal-20260830.json"
TEST="$CODE_REPO/nd-unfolding/pet/test_gap3_nonfinite_diagnostic.py"
GUARD="$CODE_REPO/nd-unfolding/mnv_guarded_run.py"
LAUNCHER="$CODE_REPO/nd-unfolding/pet/sbatch_gap3_nonfinite_diagnostic.sh"
RESULT="$OUTPUT_ROOT/result-${SLURM_JOB_ID}.json"

EXPECTED_DIAGNOSTIC_SHA256="55028da1c32fce58e9dcf20eda84846b050fc65ed972558f17a7616e6886f98f"
EXPECTED_PREDECL_SHA256="679ea7f9d10f1c5f5fa1e6b9fd4ca818175070dadd69c5073a8bf63a435ecf59"
EXPECTED_PROPOSAL_SHA256="3229afc3828e3b3e9db356ce685bdc0c3156ff79118f5e82e62814288e66ebf9"
EXPECTED_TEST_SHA256="4550242e56e7f83d87b8cbcf4b8632dea0f73fe8690f1759909248472bf330b9"
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

[[ -d "$CODE_REPO/.git" || -f "$CODE_REPO/.git" ]] || die "code root is not a git worktree"
[[ "$(git -C "$CODE_REPO" rev-parse HEAD)" == "$GAP3NFD_EXPECTED_HEAD" ]] ||
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
[[ "$(sha_of "$LAUNCHER")" == "$GAP3NFD_EXPECTED_LAUNCHER_SHA256" ]] ||
  die "launcher hash mismatch"
[[ -d "$OUTPUT_ROOT" ]] || die "output root must be pre-created"
[[ ! -e "$RESULT" && ! -L "$RESULT" ]] || die "refuse occupied result path"

JOB_SPEC=$(scontrol show job -o "$SLURM_JOB_ID")
validate_job_spec "$JOB_SPEC"
printf '%s\n' "$JOB_SPEC" >"$OUTPUT_ROOT/job-spec-${SLURM_JOB_ID}.txt"

set +u
source "$DATA_ROOT/setup_salloc_env.sh"
set -u
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "python3 is not executable"
"$PYTHON_BIN" -c 'import ROOT' || die "python3 cannot import ROOT"

export OMP_NUM_THREADS=18
export ROOT_MAX_THREADS=18
echo "[gap3-nfd-launch] contract=PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830"
echo "[gap3-nfd-launch] job=$SLURM_JOB_ID head=$GAP3NFD_EXPECTED_HEAD"
echo "[gap3-nfd-launch] launcher_sha256=$GAP3NFD_EXPECTED_LAUNCHER_SHA256"
echo "[gap3-nfd-launch] result=$RESULT"

"$PYTHON_BIN" "$GUARD" --expect-root "$CODE_REPO" -- "$DIAGNOSTIC" \
  --code-root "$CODE_REPO" \
  --data-root "$DATA_ROOT" \
  --output "$RESULT" \
  --expected-head "$GAP3NFD_EXPECTED_HEAD" \
  --expected-diagnostic-sha256 "$EXPECTED_DIAGNOSTIC_SHA256" \
  --expected-predeclaration-sha256 "$EXPECTED_PREDECL_SHA256" \
  --expected-proposal-sha256 "$EXPECTED_PROPOSAL_SHA256" \
  --expected-test-sha256 "$EXPECTED_TEST_SHA256" \
  --expected-guard-sha256 "$EXPECTED_GUARD_SHA256" \
  --expected-dumper-sha256 "$EXPECTED_DUMPER_SHA256" \
  --expected-loader-sha256 "$EXPECTED_LOADER_SHA256" \
  --expected-model-sha256 "$EXPECTED_MODEL_SHA256" \
  --expected-gate6-receipt-sha256 "$EXPECTED_GATE6_RECEIPT_SHA256" \
  --expected-prior-predeclaration-sha256 "$EXPECTED_PRIOR_PREDECL_SHA256" \
  --expected-prior-launcher-sha256 "$EXPECTED_PRIOR_LAUNCHER_SHA256" \
  --expected-prior-launch-receipt-sha256 "$EXPECTED_PRIOR_LAUNCH_RECEIPT_SHA256" \
  --expected-prior-terminal-receipt-sha256 "$EXPECTED_PRIOR_TERMINAL_RECEIPT_SHA256" \
  --expected-prior-result-sha256 "$EXPECTED_PRIOR_RESULT_SHA256" \
  --threads 18

[[ -s "$RESULT" ]] || die "diagnostic did not publish a result"
echo "[gap3-nfd-launch] DONE result_sha256=$(sha_of "$RESULT")"
