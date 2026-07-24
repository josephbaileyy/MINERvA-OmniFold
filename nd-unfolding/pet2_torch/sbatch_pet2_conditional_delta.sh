#!/bin/bash
#SBATCH --job-name=pet2cs
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4-interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64g
#SBATCH --time=00:45:00
#SBATCH --output=pet2cs_%j.out
#SBATCH --error=pet2cs_%j.err
#
# One-A100 matched parent/enriched conditional-information stress job.
set -eo pipefail

die() { echo "[pet2cs][FAIL] $*" >&2; exit 1; }

REPO="${PET2_REPO:-}"
OUT_BASE="${PET2_OUT_BASE:-}"
FAMILY="${PET2_FAMILY:-}"
CONTROL_MODE="${PET2_CONTROL_MODE:-}"
ESTIMATOR_SEED="${PET2_ESTIMATOR_SEED:-}"
[[ -n "${REPO}" && -d "${REPO}/nd-unfolding/pet2_torch" ]] \
  || die "set PET2_REPO to the isolated reviewed campaign checkout"
git -C "${REPO}" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || die "PET2_REPO is not a git worktree"
[[ -n "${OUT_BASE}" ]] || die "set PET2_OUT_BASE to isolated campaign work"
[[ "${FAMILY}" =~ ^(view|type|rich|muon-token|overflow)$ ]] \
  || die "invalid PET2_FAMILY=${FAMILY}"
[[ "${CONTROL_MODE}" =~ ^(signal|unity-sham|carrier-shuffle)$ ]] \
  || die "invalid PET2_CONTROL_MODE=${CONTROL_MODE}"
[[ "${ESTIMATOR_SEED}" =~ ^(101|202|303)$ ]] \
  || die "PET2_ESTIMATOR_SEED must be 101, 202, or 303"

repo_real=$(realpath "${REPO}")
out_real=$(python3 -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' \
  "${OUT_BASE}")
case "${repo_real}" in
  /u/jbailey2/MINERvA-OmniFold|/u/jbailey2/MINERvA-OmniFold/*)
    die "forbidden active checkout: ${repo_real}" ;;
esac
case "${out_real}" in
  /u/jbailey2/MINERvA-OmniFold|/u/jbailey2/MINERvA-OmniFold/*|\
  *active_universe_5d*|*fullevent_nominal*|*products/pet*)
    die "forbidden active/shared output namespace: ${out_real}" ;;
esac
case "${out_real}" in
  "${repo_real}"|"${repo_real}"/*) die "output must be outside source checkout" ;;
esac

if [[ "${PET2_DELTA_SELFTEST:-0}" == "1" ]]; then
  echo "[pet2cs-selftest] repo=${repo_real}"
  echo "[pet2cs-selftest] out=${out_real}"
  echo "[pet2cs-selftest] family=${FAMILY} mode=${CONTROL_MODE} seed=${ESTIMATOR_SEED}"
  echo "[pet2cs-selftest] no submit, module load, or training"
  exit 0
fi

[[ "${SLURM_JOB_ID:-}" =~ ^[0-9]+$ ]] || die "run with sbatch"
[[ -z "$(git -C "${repo_real}" status --porcelain --untracked-files=normal)" ]] \
  || die "matched execution requires a clean committed source checkout"
module load pytorch-conda/2.8
export PYTHONPATH="${repo_real}/nd-unfolding${PYTHONPATH:+:${PYTHONPATH}}"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONHASHSEED="${ESTIMATOR_SEED}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8

if [[ -n "${PET2_VENV:-}" ]]; then
  [[ -x "${PET2_VENV}/bin/python" ]] || die "invalid PET2_VENV=${PET2_VENV}"
  PYTHON="${PET2_VENV}/bin/python"
else
  PYTHON=python3
fi

family_slug="${FAMILY//-/_}"
mode_slug="${CONTROL_MODE//-/_}"
RUN_OUT="${out_real}/pet2cs_${family_slug}_${mode_slug}_seed${ESTIMATOR_SEED}_job${SLURM_JOB_ID}"
[[ ! -e "${RUN_OUT}" ]] || die "refusing to overwrite ${RUN_OUT}"
mkdir -p "${out_real}"

srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK:-8}" \
  "${PYTHON}" -m pet2_torch.environment --require-delta \
  || die "Delta environment gate failed"
srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK:-8}" \
  "${PYTHON}" -m pet2_torch.conditional_stress_cli \
    --out "${RUN_OUT}" \
    --family "${FAMILY}" \
    --mode "${CONTROL_MODE}" \
    --recipe matched-conditional-v1 \
    --events 100000 \
    --background-events 10000 \
    --max-tokens 7 \
    --fixture-seed 424242 \
    --split-seed 424242 \
    --estimator-seed "${ESTIMATOR_SEED}" \
    --iterations 2 \
    --epochs 8 \
    --batch-size 512 \
    --learning-rate 1e-4 \
    --weight-decay 1e-2 \
    --device cuda \
  || die "conditional stress failed"
echo "[pet2cs] complete ${RUN_OUT}"
