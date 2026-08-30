#!/bin/bash
#SBATCH --job-name=pet_g6_gap3_r1
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --no-requeue

# One-shot changed retry for PET-G6-GAP3-RECO-TRUNCATION-20260830.
set -euo pipefail

die() {
  echo "[gap3-r1-launch][FAIL] $*" >&2
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
  echo "[gap3-r1-launch] resource fixture PASS"
  exit 0
fi

: "${GAP3R1_CODE_REPO:?set GAP3R1_CODE_REPO to the immutable audit checkout}"
: "${GAP3R1_DATA_ROOT:?set GAP3R1_DATA_ROOT to the canonical data checkout root}"
: "${GAP3R1_OUTPUT_ROOT:?set GAP3R1_OUTPUT_ROOT to a unique pre-created output directory}"
: "${GAP3R1_EXPECTED_HEAD:?set GAP3R1_EXPECTED_HEAD to the pushed preparation commit}"
: "${GAP3R1_EXPECTED_LAUNCHER_SHA256:?set the committed launcher SHA-256}"
: "${GAP3R1_AUTHORIZATION_TOKEN:?set the changed-retry authorization token}"

[[ "$GAP3R1_AUTHORIZATION_TOKEN" == \
  "PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1-ONE-SCAN" ]] ||
  die "authorization token mismatch"
[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run inside one Slurm job"
[[ -z "${SLURM_ARRAY_TASK_ID:-}" ]] || die "job arrays are forbidden"
[[ "${SLURM_CPUS_PER_TASK:-}" == "18" ]] || die "expected exactly 18 CPUs"
[[ -z "${SLURM_JOB_GPUS:-}" ]] || die "GPU allocation is forbidden"
[[ -z "${SLURM_GPUS_ON_NODE:-}" ]] || die "GPU node allocation is forbidden"

CODE_REPO=$(realpath "$GAP3R1_CODE_REPO")
DATA_ROOT=$(realpath "$GAP3R1_DATA_ROOT")
OUTPUT_ROOT=$(realpath "$GAP3R1_OUTPUT_ROOT")
CORE="$CODE_REPO/nd-unfolding/pet/audit_reco_truncation.py"
WRAPPER="$CODE_REPO/nd-unfolding/pet/audit_reco_truncation_changed_retry1.py"
PREDECL="$CODE_REPO/docs/orchestration/PREDECLARATION-20260830-gate6-gap3-reco-truncation-changed-retry1.md"
PROPOSAL="$CODE_REPO/docs/orchestration/state/gate6-gap3-reco-truncation-changed-retry1-proposal-20260830.json"
TEST="$CODE_REPO/nd-unfolding/pet/test_gap3_reco_truncation_changed_retry1.py"
GUARD="$CODE_REPO/nd-unfolding/mnv_guarded_run.py"
LAUNCHER="$CODE_REPO/nd-unfolding/pet/sbatch_gap3_reco_truncation_changed_retry1.sh"
MERGE_RECEIPT="$DATA_ROOT/nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json"
GATE6_RECEIPT="$CODE_REPO/docs/orchestration/state/gate6-member-trajectories-result-56847059.json"
ORIGINAL_PREDECL="$CODE_REPO/docs/orchestration/PREDECLARATION-20260830-gate6-gap3-reco-truncation-audit.md"
ORIGINAL_LAUNCHER="$CODE_REPO/nd-unfolding/pet/sbatch_gap3_reco_truncation_audit.sh"
ORIGINAL_LAUNCH_RECEIPT="$CODE_REPO/docs/orchestration/state/gate6-gap3-reco-truncation-launch-57727806.json"
ORIGINAL_TERMINAL_RECEIPT="$CODE_REPO/docs/orchestration/state/gate6-gap3-reco-truncation-terminal-57727806.json"
ORIGINAL_TEST="$CODE_REPO/nd-unfolding/pet/test_audit_reco_truncation.py"
RESULT="$OUTPUT_ROOT/result-${SLURM_JOB_ID}.json"

EXPECTED_CORE_SHA256="671531dd6a43a03203d4a8024d5671a7b357edad6e1fa7ab9ad7e44a99ac1e1a"
EXPECTED_WRAPPER_SHA256="078cf8bc7a7fd60671d55a4b23f6619f45f742dbc3aef9612efbb10e7733d852"
EXPECTED_PREDECL_SHA256="fc1772058469a34293ba1d8a162c1fe3b6cd3c2ade6c7bd31a65a39bda06c648"
EXPECTED_PROPOSAL_SHA256="5755e6b324a8a010139139acbab121db8acb113f07f8ac88724fb2de1f9939d0"
EXPECTED_TEST_SHA256="21481a4ff4b2596ebe9f73165afe4d4ffc449b2118c8f3d26c816bee5df6e876"
EXPECTED_GUARD_SHA256="145711eb5a247faf7bb5643a47b0f8be6e7ac2f95de0c43c12d3de1105f544c7"
EXPECTED_MERGE_RECEIPT_SHA256="26ea5561f47599987ebacbf594c606309146a5f23c82af8dd0e2ca299b31efa7"
EXPECTED_GATE6_RECEIPT_SHA256="8f40541f1d8fec92b0e37885b1d24b851843d06f4c220f8de5ad1bc47265b6a5"
EXPECTED_ORIGINAL_PREDECL_SHA256="b69c296a1bd9be426c8acf78bd1232b780bd3c9e2b0b7924d09d241feb8260fc"
EXPECTED_ORIGINAL_LAUNCHER_SHA256="4c23d6a2e2ee770a424c92d8c9eda67ac56dc3c7b8265dfdc3add73fe4325cfe"
EXPECTED_ORIGINAL_LAUNCH_RECEIPT_SHA256="ade8f8755fa8cab04934e3828c651a9b131fe0a029c144533b52a2b671acf8e9"
EXPECTED_ORIGINAL_TERMINAL_RECEIPT_SHA256="4fcb7a58102e2c3e9f41808bc9bb68e8884a24b4602eac79252476e3f42fbb80"
EXPECTED_ORIGINAL_TEST_SHA256="674efffbafe90a115e677a58f475b307feae076b727d30af9a832a3a71fa3293"

[[ -d "$CODE_REPO/.git" || -f "$CODE_REPO/.git" ]] || die "code root is not a git worktree"
[[ "$(git -C "$CODE_REPO" rev-parse HEAD)" == "$GAP3R1_EXPECTED_HEAD" ]] ||
  die "code HEAD mismatch"
[[ -z "$(git -C "$CODE_REPO" status --porcelain)" ]] || die "code checkout is dirty"
[[ "$(sha_of "$CORE")" == "$EXPECTED_CORE_SHA256" ]] || die "audit core hash mismatch"
[[ "$(sha_of "$WRAPPER")" == "$EXPECTED_WRAPPER_SHA256" ]] || die "wrapper hash mismatch"
[[ "$(sha_of "$PREDECL")" == "$EXPECTED_PREDECL_SHA256" ]] || die "predeclaration hash mismatch"
[[ "$(sha_of "$PROPOSAL")" == "$EXPECTED_PROPOSAL_SHA256" ]] || die "proposal hash mismatch"
[[ "$(sha_of "$TEST")" == "$EXPECTED_TEST_SHA256" ]] || die "test hash mismatch"
[[ "$(sha_of "$GUARD")" == "$EXPECTED_GUARD_SHA256" ]] || die "guard hash mismatch"
[[ "$(sha_of "$LAUNCHER")" == "$GAP3R1_EXPECTED_LAUNCHER_SHA256" ]] ||
  die "launcher hash mismatch"
[[ "$(sha_of "$MERGE_RECEIPT")" == "$EXPECTED_MERGE_RECEIPT_SHA256" ]] ||
  die "merge receipt hash mismatch"
[[ "$(sha_of "$GATE6_RECEIPT")" == "$EXPECTED_GATE6_RECEIPT_SHA256" ]] ||
  die "Gate-6 receipt hash mismatch"
[[ "$(sha_of "$ORIGINAL_PREDECL")" == "$EXPECTED_ORIGINAL_PREDECL_SHA256" ]] ||
  die "original predeclaration changed"
[[ "$(sha_of "$ORIGINAL_LAUNCHER")" == "$EXPECTED_ORIGINAL_LAUNCHER_SHA256" ]] ||
  die "original launcher changed"
[[ "$(sha_of "$ORIGINAL_LAUNCH_RECEIPT")" == "$EXPECTED_ORIGINAL_LAUNCH_RECEIPT_SHA256" ]] ||
  die "original launch receipt changed"
[[ "$(sha_of "$ORIGINAL_TERMINAL_RECEIPT")" == "$EXPECTED_ORIGINAL_TERMINAL_RECEIPT_SHA256" ]] ||
  die "original terminal receipt changed"
[[ "$(sha_of "$ORIGINAL_TEST")" == "$EXPECTED_ORIGINAL_TEST_SHA256" ]] ||
  die "original test changed"
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
echo "[gap3-r1-launch] contract=PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1"
echo "[gap3-r1-launch] job=$SLURM_JOB_ID head=$GAP3R1_EXPECTED_HEAD"
echo "[gap3-r1-launch] launcher_sha256=$GAP3R1_EXPECTED_LAUNCHER_SHA256"
echo "[gap3-r1-launch] result=$RESULT"

"$PYTHON_BIN" "$GUARD" --expect-root "$CODE_REPO" -- "$WRAPPER" \
  --code-root "$CODE_REPO" \
  --data-root "$DATA_ROOT" \
  --output "$RESULT" \
  --expected-head "$GAP3R1_EXPECTED_HEAD" \
  --expected-audit-sha256 "$EXPECTED_CORE_SHA256" \
  --expected-wrapper-sha256 "$EXPECTED_WRAPPER_SHA256" \
  --expected-predeclaration-sha256 "$EXPECTED_PREDECL_SHA256" \
  --expected-proposal-sha256 "$EXPECTED_PROPOSAL_SHA256" \
  --expected-guard-sha256 "$EXPECTED_GUARD_SHA256" \
  --threads 18

[[ -s "$RESULT" ]] || die "audit did not publish a result"
echo "[gap3-r1-launch] DONE result_sha256=$(sha_of "$RESULT")"
