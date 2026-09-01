#!/bin/bash
#SBATCH --job-name=miiSeed5dBKG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32
#SBATCH --time=01:30:00
#SBATCH --array=1-12%8
#SBATCH --export=ALL
#SBATCH --output=uq_5d/miiSeed5dBKG_%a_%A.out --error=uq_5d/miiSeed5dBKG_%a_%A.err
#
# SUBMITTER MUST EXPORT every variable below before emitting MNV_ENV_PROVENANCE and before sbatch:
#   MNV_CODE_ROOT              approved clean, read-only execution checkout
#   MNV_DATA_ROOT              data tree holding inputs and receiving products
#   MNV_ENV_ROOT               verified environment tree outside every checkout
#   MNV_CONDA_PREFIX           conda environment bound by the environment manifest
#   MNV_GUARD_INVENTORY_DIR    new run-scoped directory for guard inventories
#   MNV_SOURCE_MANIFEST        pre-submission source manifest from MNV_CODE_ROOT
#   MNV_ENV_PROVENANCE         pre-submission environment baseline
#   MNV_ENV_SYSTEM_PREFIXES    explicit path allowlist, including required home prefixes
#   MNV_LAUNCHER_DIR           ${MNV_CODE_ROOT}/nd-unfolding for Slurm spool resolution
#
# One array task runs one background-aware CV unfold. The array task id is the only changing
# estimator input. The %8 throttle matches the detector launcher's cap and limits concurrent reads
# of the 171 GB background-aware ROOT input. Combining the 12 members is a separate scheduler task.
set -eo pipefail

export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}
export PYTHONDONTWRITEBYTECODE=1

CODE_ROOT="${MNV_CODE_ROOT:?set MNV_CODE_ROOT to the approved clean execution checkout}"
DATA_ROOT="${MNV_DATA_ROOT:?set MNV_DATA_ROOT to the data tree holding inputs and products}"
ENV_ROOT="${MNV_ENV_ROOT:?set MNV_ENV_ROOT to the verified environment tree outside every checkout}"
ENV_MANIFEST="${MNV_ENV_MANIFEST:-${CODE_ROOT}/nd-unfolding/mnv_env_manifest.tsv}"
: "${MNV_CONDA_PREFIX:?set MNV_CONDA_PREFIX to the conda environment bound by the manifest}"
: "${MNV_ENV_SYSTEM_PREFIXES:?set MNV_ENV_SYSTEM_PREFIXES to the submitter-declared path allowlist}"
: "${MNV_LAUNCHER_DIR:?set MNV_LAUNCHER_DIR to MNV_CODE_ROOT/nd-unfolding for Slurm spool resolution}"
export ROOT628_PREFIX="${MNV_CONDA_PREFIX}"
ND="${DATA_ROOT}/nd-unfolding"

# Bind every tracked shell library before sourcing any of them.
for _mnv_rel in lib/resume_guard.sh \
                nd-unfolding/lib_mnv_env_preflight.sh \
                nd-unfolding/lib_mnv_env_pathcheck.sh; do
  _mnv_head="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_mnv_rel}" 2>/dev/null || true)"
  _mnv_work="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_mnv_rel}" 2>/dev/null || true)"
  if [[ -z "$_mnv_head" || -z "$_mnv_work" ]]; then
    echo "[mii-seed] FAIL: cannot compute git parity for ${_mnv_rel}" >&2
    exit 3
  fi
  if [[ "$_mnv_head" != "$_mnv_work" ]]; then
    echo "[mii-seed] FAIL: ${_mnv_rel} differs from HEAD in ${CODE_ROOT}" >&2
    exit 3
  fi
done
unset _mnv_rel _mnv_head _mnv_work

source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_preflight.sh"
mnv_env_preflight "$ENV_MANIFEST" "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?
source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_pathcheck.sh"
source "${ENV_ROOT}/setup_salloc_env.sh"
mnv_env_pathcheck "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?
source "${CODE_ROOT}/lib/resume_guard.sh"

GUARD="${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py"
PARITY="${CODE_ROOT}/nd-unfolding/pet/verify_executing_copy_is_committed.py"
SRCMAN="${CODE_ROOT}/nd-unfolding/mnv_source_manifest.py"
ENVPROV="${CODE_ROOT}/nd-unfolding/mnv_env_provenance.py"
INVDIR="${MNV_GUARD_INVENTORY_DIR:?set MNV_GUARD_INVENTORY_DIR to a new run-scoped directory}"
SRCMAN_RECORD="${MNV_SOURCE_MANIFEST:?set MNV_SOURCE_MANIFEST to the pre-submission source manifest}"
ENVPROV_RECORD="${MNV_ENV_PROVENANCE:?set MNV_ENV_PROVENANCE to the pre-submission environment baseline}"

for _mnv_tool in "$GUARD" "$PARITY" "$SRCMAN" "$ENVPROV"; do
  [[ -s "$_mnv_tool" && ! -L "$_mnv_tool" ]] || {
    echo "[mii-seed] FAIL: required tool missing or a symlink: $_mnv_tool" >&2
    exit 2
  }
done
mkdir -p "${INVDIR}"
mnv_inv() {
  echo "${INVDIR}/${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.${SLURM_ARRAY_TASK_ID:-na}.$1.jsonl"
}

# These integrity and provenance tools are routed through the same import guard as the science
# process. This launcher therefore adds no preflight exclusion to mnv_preflight_exclusions.json.
# DECLARED PREFLIGHT EXCLUSIONS -- THE THREE CALLS BELOW ARE DELIBERATELY NOT ROUTED THROUGH
# mnv_guarded_run.py, AND THAT IS NOT AN OVERSIGHT. The eight k=0 launchers invoke SRCMAN, PARITY and
# ENVPROV directly (see sbatch_unfold_5d_detector_bkgaware_gpu.sh:204,213,244) and
# mnv_preflight_exclusions.json declares that set with falsifiable counts. Guarding them here instead
# would (a) move the guarded boundary from 14 to 18, and 14 is the number ruling 21 pinned -- see
# OI-185 -- and (b) FAIL test_the_inventories_are_NON_VACUOUS: measured,
# `mnv_guarded_run.py --expect-root <repo> -- mnv_env_provenance.py --self-test` gives checked=12 but
# repo_origin_count=0, because that tool imports only the standard library, and the test asserts
# repo_origin_count > 0 with one exemption that an `env_provenance` tag does not match.
# ONLY THE SCIENCE CALL AT THE BOTTOM IS GUARDED. Measured by the claude-school k=0 lane.
python3 "$SRCMAN" \
  --repo "$CODE_ROOT" --compare "$SRCMAN_RECORD" \
  --require-clean --require-checkout --require-no-nested-checkout \
  --require-not-nested --require-readonly || {
  echo "[mii-seed] FAIL: execution tree does not match the approved source manifest" >&2
  exit 3
}

python3 "$PARITY" \
  --repo "$CODE_ROOT" \
  --pair "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py=nd-unfolding/unfold_nd_omnifold_unbinned.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh=nd-unfolding/sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh" \
  --pair "${CODE_ROOT}/nd-unfolding/lib_member_resume.sh=nd-unfolding/lib_member_resume.sh" \
  --pair "${GUARD}=nd-unfolding/mnv_guarded_run.py" \
  --pair "${PARITY}=nd-unfolding/pet/verify_executing_copy_is_committed.py" \
  --pair "${SRCMAN}=nd-unfolding/mnv_source_manifest.py" \
  --pair "${ENVPROV}=nd-unfolding/mnv_env_provenance.py" || {
  echo "[mii-seed] FAIL: executing copies do not match the approved commit" >&2
  exit 3
}

_mnv_ep=0
python3 "$ENVPROV" \
  --check-inherited "$ENVPROV_RECORD" \
  --record "${INVDIR}/env-provenance.${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.${SLURM_ARRAY_TASK_ID:-na}.json" \
  || _mnv_ep=$?
if [[ $_mnv_ep -ne 0 ]]; then
  echo "[mii-seed] FAIL: submission environment did not reach this task intact" >&2
  exit "$_mnv_ep"
fi
unset _mnv_ep

# Locate the resume library from the real launcher directory, not Slurm's spooled copy.
_mr_lib=""
for _mr_c in "${MNV_LAUNCHER_DIR:-}" "$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"; do
  if [[ -n "$_mr_c" && -r "$_mr_c/lib_member_resume.sh" ]]; then
    _mr_lib="$_mr_c"
    break
  fi
done
if [[ -z "$_mr_lib" && -n "${SLURM_JOB_ID:-}" ]]; then
  _mr_c="$(scontrol show job "$SLURM_JOB_ID" 2>/dev/null \
           | tr ' ' '\n' | sed -n 's/^Command=//p' | head -1)"
  _mr_c="${_mr_c:+$(dirname "$_mr_c")}"
  if [[ -n "$_mr_c" && -r "$_mr_c/lib_member_resume.sh" ]]; then
    _mr_lib="$_mr_c"
  fi
fi
if [[ -z "$_mr_lib" ]]; then
  echo "[mii-seed] FAIL: cannot locate lib_member_resume.sh beside this launcher" >&2
  exit 2
fi
if [[ "$(cd "$_mr_lib" 2>/dev/null && pwd -P)" != "$(cd "${CODE_ROOT}/nd-unfolding" 2>/dev/null && pwd -P)" ]]; then
  echo "[mii-seed] FAIL: lib_member_resume.sh did not resolve under MNV_CODE_ROOT" >&2
  exit 2
fi
source "${_mr_lib}/lib_member_resume.sh"

# This scan varies the direct estimator seed, not the separate M(ii) offset axis.
if [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; then
  echo "[mii-seed] FAIL: MNV_EST_SEED_OFFSET must be unset for the estimator-seed scan" >&2
  exit 2
fi
mr_require_valid_offset

SEED="${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID must identify estimator seed 1 through 12}"
if ! [[ "$SEED" =~ ^([1-9]|1[0-2])$ ]]; then
  echo "[mii-seed] FAIL: SLURM_ARRAY_TASK_ID must be a canonical integer in 1..12" >&2
  exit 2
fi

cd "${ND}"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
FLUX_MC="${DATA_ROOT}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
OUTDIR="$(mr_dir_prefix "${ND}/uq_5d/cause3_mii_20260901/estimator_seed_members")"
mkdir -p "${OUTDIR}"
[[ -s "${OMNIFILE}" ]] || { echo "[mii-seed] FAIL: background-aware omnifile missing" >&2; exit 2; }
[[ -s "${FLUX_MC}" ]] || { echo "[mii-seed] FAIL: baseline flux MC file missing" >&2; exit 2; }

XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_cv_estimator_seed_${SEED}.root"
mr_skip_if_complete "${XSEC_OUT}" && exit 0

echo "[mii-seed] seed=${SEED} node=$(hostname) task=${SLURM_ARRAY_TASK_ID} $(date -u '+%F %T UTC')"
mr_run "${XSEC_OUT}" python3 "$GUARD" --expect-root "$CODE_ROOT" \
  --inventory "$(mnv_inv unfold_nd_cv_seed_${SEED})" -- \
  "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py" \
  --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
  --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm \
  --seed "${SLURM_ARRAY_TASK_ID}" \
  --closure-slack 5000 \
  --out "${XSEC_OUT}"
echo "[mii-seed] done seed=${SEED} $(date -u '+%F %T UTC')"
