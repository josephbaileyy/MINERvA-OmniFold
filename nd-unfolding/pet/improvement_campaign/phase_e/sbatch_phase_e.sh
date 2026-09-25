#!/bin/bash
# Phase E1: one guarded CPU entrypoint per job (or array task), the B1 pattern.
#
#   sbatch [--array=...] [--cpus-per-task=N --mem=M --time=T] sbatch_phase_e.sh \
#       <checkout> <python> <output-dir> <expected-commit> <script.py> [script args...]
#
# Runs from a CLEAN checkout pinned to <expected-commit>, through nd-unfolding/mnv_guarded_run.py
# (OI-136), with the guard inventory written beside the outputs. `ARRAY_TASK` in the script
# arguments is replaced by $SLURM_ARRAY_TASK_ID. Reads only signal-MC members of the closure
# inventory and never writes under the historical campaign directory (the Python side refuses that
# too). Simulation only: PET is diagnostic method development.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --job-name=pet-e1
set -eo pipefail

checkout=$1
python=$2
output=$3
expected_commit=$4
script=$5
shift 5

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ -x "$python" ]]
case "$output" in
  /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2 ;;
esac

tag="${SLURM_JOB_ID}"
[[ -n "${SLURM_ARRAY_TASK_ID:-}" ]] && tag="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
args=()
for a in "$@"; do args+=("${a//ARRAY_TASK/${SLURM_ARRAY_TASK_ID:-}}"); done

mkdir -p "$output"
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation-$tag.txt"
unset MNV_REPO
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK \
       MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK

"$python" nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
  --inventory "$output/guard-$tag.json" --label "phaseE1:$script" \
  -- "nd-unfolding/pet/improvement_campaign/phase_e/$script" "${args[@]}" \
  > "$output/log-$tag.txt" 2>&1

[[ -z "$(git status --porcelain)" ]]
echo COMPLETE > "$output/terminal-$tag.txt"
