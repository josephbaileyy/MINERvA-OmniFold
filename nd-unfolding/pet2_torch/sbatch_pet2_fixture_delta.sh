#!/bin/bash
#SBATCH --job-name=pet2x_onearm
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64g
#SBATCH --time=02:00:00
#SBATCH --output=pet2x_onearm_%j.out
#SBATCH --error=pet2x_onearm_%j.err
#
# One-A100, one-arm/one-seed synthetic pilot for the independent PET2 backend.
# It never consumes publication G2 and never writes to the active MINERvA
# production checkout or product namespaces.
set -eo pipefail

die() { echo "[pet2-delta][FAIL] $*" >&2; exit 1; }

REPO="${PET2_REPO:-}"
OUT_BASE="${PET2_OUT_BASE:-}"
ARM="${PET2_ARM:-}"
ESTIMATOR_SEED="${PET2_ESTIMATOR_SEED:-}"
MODE="${PET2_MODE:-matched-pilot}"
[[ -n "${REPO}" ]] || die "set PET2_REPO to this reviewed campaign checkout"
[[ -d "${REPO}/nd-unfolding/pet2_torch" ]] || die "PET2_REPO lacks pet2_torch: ${REPO}"
[[ -n "${OUT_BASE}" ]] || die "set PET2_OUT_BASE to a new isolated Delta scratch/work path"
[[ -n "${ARM}" ]] || die "set PET2_ARM to exactly one declared arm"
[[ "${ARM}" =~ ^(C|D-view|D-typed|E-muon|E-rich-no-charge|E-rich)$ ]] \
  || die "unsupported PET2_ARM=${ARM}"
[[ "${ESTIMATOR_SEED}" =~ ^[0-9]+$ ]] || die "set integer PET2_ESTIMATOR_SEED"
[[ "${MODE}" == "matched-pilot" || "${MODE}" == "smoke" ]] \
  || die "PET2_MODE must be matched-pilot or smoke"
if [[ "${MODE}" == "matched-pilot" ]]; then
  [[ "${ESTIMATOR_SEED}" == "101" || "${ESTIMATOR_SEED}" == "202" || \
     "${ESTIMATOR_SEED}" == "303" ]] \
    || die "matched pilot seed must be 101, 202, or 303"
fi

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
  "${repo_real}"|"${repo_real}"/*) die "output must be outside the source checkout" ;;
esac

if [[ "${PET2_DELTA_SELFTEST:-0}" == "1" ]]; then
  echo "[pet2-delta-selftest] repo=${repo_real}"
  echo "[pet2-delta-selftest] out_base=${out_real}"
  echo "[pet2-delta-selftest] module=pytorch-conda/2.8 gpu=1 cpus=8"
  echo "[pet2-delta-selftest] mode=${MODE} arm=${ARM} seed=${ESTIMATOR_SEED}"
  echo "[pet2-delta-selftest] no submit, no module load, no training"
  exit 0
fi

[[ -n "${SLURM_JOB_ID:-}" ]] || die "run with sbatch; this launcher never submits itself"
module load pytorch-conda/2.8

export PYTHONPATH="${repo_real}/nd-unfolding${PYTHONPATH:+:${PYTHONPATH}}"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONHASHSEED="${ESTIMATOR_SEED}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8

arm_slug="${ARM//-/_}"
RUN_OUT="${out_real}/pet2x_${MODE}_${arm_slug}_seed${ESTIMATOR_SEED}_job${SLURM_JOB_ID}"
[[ ! -e "${RUN_OUT}" ]] || die "refusing to overwrite ${RUN_OUT}"
mkdir -p "${out_real}"

# The module supplies torch/numpy. Activate an optional isolated venv containing
# safetensors==0.5.3 without modifying the module or any analysis environment.
if [[ -n "${PET2_VENV:-}" ]]; then
  [[ -x "${PET2_VENV}/bin/python" ]] || die "invalid PET2_VENV=${PET2_VENV}"
  PYTHON="${PET2_VENV}/bin/python"
else
  PYTHON=python3
fi

srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK:-8}" \
  "${PYTHON}" -m pet2_torch.environment --require-delta \
  || die "isolated Delta environment gate failed"

if [[ "${MODE}" == "matched-pilot" ]]; then
  cli_args=(
    --recipe matched-pilot
    --fixture known-ratio
    --events "${PET2_SIGNAL_EVENTS:-100000}"
    --background-events "${PET2_BACKGROUND_EVENTS:-10000}"
    --max-tokens "${PET2_MAX_TOKENS:-12}"
    --fixture-seed 424242
    --estimator-seed "${ESTIMATOR_SEED}"
    --split-seed 424242
    --iterations 2
    --epochs 8
    --batch-size 512
    --learning-rate 1e-4
    --weight-decay 1e-2
  )
else
  cli_args=(
    --recipe smoke
    --fixture known-ratio
    --events "${PET2_SIGNAL_EVENTS:-512}"
    --background-events "${PET2_BACKGROUND_EVENTS:-40}"
    --max-tokens "${PET2_MAX_TOKENS:-7}"
    --fixture-seed "${PET2_FIXTURE_SEED:-424242}"
    --estimator-seed "${ESTIMATOR_SEED}"
    --split-seed "${PET2_SPLIT_SEED:-424242}"
    --iterations "${PET2_ITERATIONS:-1}"
    --epochs "${PET2_EPOCHS:-1}"
    --batch-size "${PET2_BATCH_SIZE:-128}"
    --learning-rate "${PET2_LEARNING_RATE:-1e-4}"
    --weight-decay "${PET2_WEIGHT_DECAY:-1e-2}"
  )
fi

srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK:-8}" \
  "${PYTHON}" -m pet2_torch.cli \
    --out "${RUN_OUT}" \
    --device cuda \
    --arms "${ARM}" \
    "${cli_args[@]}" \
  || die "${MODE} ${ARM} seed ${ESTIMATOR_SEED} fixture pilot failed"

echo "[pet2-delta] complete: ${RUN_OUT}"
