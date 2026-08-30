#!/bin/bash
#SBATCH --job-name=pet_g6_gap3_trunc
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00

# One-shot CPU-only launcher for PET-G6-GAP3-RECO-TRUNCATION-20260830.
set -euo pipefail

die() {
  echo "[gap3-launch][FAIL] $*" >&2
  exit 3
}

sha_of() {
  sha256sum "$1" | awk '{print $1}'
}

: "${GAP3_CODE_REPO:?set GAP3_CODE_REPO to the clean committed audit checkout}"
: "${GAP3_DATA_ROOT:?set GAP3_DATA_ROOT to the canonical data checkout root}"
: "${GAP3_OUTPUT_ROOT:?set GAP3_OUTPUT_ROOT to a unique pre-created output directory}"
: "${GAP3_EXPECTED_HEAD:?set GAP3_EXPECTED_HEAD to the committed audit revision}"
: "${GAP3_EXPECTED_LAUNCHER_SHA256:?set the committed launcher SHA-256}"
: "${GAP3_AUTHORIZATION_TOKEN:?set the one-shot authorization token}"

[[ "$GAP3_AUTHORIZATION_TOKEN" == "PET-G6-GAP3-RECO-TRUNCATION-20260830-ONE-SCAN" ]] ||
  die "authorization token mismatch"
[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run inside one Slurm job"
[[ -z "${SLURM_ARRAY_TASK_ID:-}" ]] || die "job arrays are forbidden"
[[ "${SLURM_CPUS_PER_TASK:-}" == "8" ]] || die "expected exactly 8 CPUs"
[[ -z "${SLURM_JOB_GPUS:-}" ]] || die "GPU allocation is forbidden"

CODE_REPO=$(realpath "$GAP3_CODE_REPO")
DATA_ROOT=$(realpath "$GAP3_DATA_ROOT")
OUTPUT_ROOT=$(realpath "$GAP3_OUTPUT_ROOT")
AUDIT="$CODE_REPO/nd-unfolding/pet/audit_reco_truncation.py"
PREDECL="$CODE_REPO/docs/orchestration/PREDECLARATION-20260830-gate6-gap3-reco-truncation-audit.md"
GUARD="$CODE_REPO/nd-unfolding/mnv_guarded_run.py"
LAUNCHER="$CODE_REPO/nd-unfolding/pet/sbatch_gap3_reco_truncation_audit.sh"
MERGE_RECEIPT="$DATA_ROOT/nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json"
GATE6_RECEIPT="$CODE_REPO/docs/orchestration/state/gate6-member-trajectories-result-56847059.json"
RESULT="$OUTPUT_ROOT/result-${SLURM_JOB_ID}.json"

EXPECTED_AUDIT_SHA256="671531dd6a43a03203d4a8024d5671a7b357edad6e1fa7ab9ad7e44a99ac1e1a"
EXPECTED_PREDECL_SHA256="b69c296a1bd9be426c8acf78bd1232b780bd3c9e2b0b7924d09d241feb8260fc"
EXPECTED_GUARD_SHA256="145711eb5a247faf7bb5643a47b0f8be6e7ac2f95de0c43c12d3de1105f544c7"
EXPECTED_MERGE_RECEIPT_SHA256="26ea5561f47599987ebacbf594c606309146a5f23c82af8dd0e2ca299b31efa7"
EXPECTED_GATE6_RECEIPT_SHA256="8f40541f1d8fec92b0e37885b1d24b851843d06f4c220f8de5ad1bc47265b6a5"

[[ -d "$CODE_REPO/.git" || -f "$CODE_REPO/.git" ]] || die "code root is not a git worktree"
[[ "$(git -C "$CODE_REPO" rev-parse HEAD)" == "$GAP3_EXPECTED_HEAD" ]] ||
  die "code HEAD mismatch"
[[ -z "$(git -C "$CODE_REPO" status --porcelain)" ]] || die "code checkout is dirty"
[[ "$(sha_of "$AUDIT")" == "$EXPECTED_AUDIT_SHA256" ]] || die "audit hash mismatch"
[[ "$(sha_of "$PREDECL")" == "$EXPECTED_PREDECL_SHA256" ]] || die "predeclaration hash mismatch"
[[ "$(sha_of "$GUARD")" == "$EXPECTED_GUARD_SHA256" ]] || die "guard hash mismatch"
[[ "$(sha_of "$LAUNCHER")" == "$GAP3_EXPECTED_LAUNCHER_SHA256" ]] ||
  die "launcher hash mismatch"
[[ "$(sha_of "$MERGE_RECEIPT")" == "$EXPECTED_MERGE_RECEIPT_SHA256" ]] ||
  die "merge receipt hash mismatch"
[[ "$(sha_of "$GATE6_RECEIPT")" == "$EXPECTED_GATE6_RECEIPT_SHA256" ]] ||
  die "Gate-6 receipt hash mismatch"
[[ -d "$OUTPUT_ROOT" ]] || die "output root must be pre-created"
[[ ! -e "$RESULT" && ! -L "$RESULT" ]] || die "refuse occupied result path"

JOB_SPEC=$(scontrol show job -o "$SLURM_JOB_ID")
grep -q 'NumCPUs=8' <<<"$JOB_SPEC" || die "Slurm allocation is not 8 CPUs"
grep -q 'TimeLimit=04:00:00' <<<"$JOB_SPEC" || die "Slurm time limit is not 4 hours"
if grep -Eiq 'gres/gpu=[1-9]|Gres=gpu(:|=)' <<<"$JOB_SPEC"; then
  die "Slurm job carries a GPU resource"
fi
printf '%s\n' "$JOB_SPEC" >"$OUTPUT_ROOT/job-spec-${SLURM_JOB_ID}.txt"

# Conda activation reads optional variables that may be unset. Limit nounset
# suspension to the trusted environment setup, then restore fail-closed mode.
set +u
source "$DATA_ROOT/setup_salloc_env.sh"
set -u
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "python3 is not executable"
"$PYTHON_BIN" -c 'import ROOT' || die "python3 cannot import ROOT"

export OMP_NUM_THREADS=8
export ROOT_MAX_THREADS=8
echo "[gap3-launch] contract=PET-G6-GAP3-RECO-TRUNCATION-20260830"
echo "[gap3-launch] job=$SLURM_JOB_ID head=$GAP3_EXPECTED_HEAD"
echo "[gap3-launch] launcher_sha256=$GAP3_EXPECTED_LAUNCHER_SHA256"
echo "[gap3-launch] result=$RESULT"

"$PYTHON_BIN" "$GUARD" --expect-root "$CODE_REPO" -- "$AUDIT" \
  --code-root "$CODE_REPO" \
  --data-root "$DATA_ROOT" \
  --output "$RESULT" \
  --expected-head "$GAP3_EXPECTED_HEAD" \
  --expected-audit-sha256 "$EXPECTED_AUDIT_SHA256" \
  --expected-predeclaration-sha256 "$EXPECTED_PREDECL_SHA256" \
  --expected-guard-sha256 "$EXPECTED_GUARD_SHA256" \
  --threads 8

[[ -s "$RESULT" ]] || die "audit did not publish a result"
echo "[gap3-launch] DONE result_sha256=$(sha_of "$RESULT")"
