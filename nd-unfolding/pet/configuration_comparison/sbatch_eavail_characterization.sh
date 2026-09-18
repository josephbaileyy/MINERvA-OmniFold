#!/bin/bash
# Bounded CPU characterization of the CANDIDATE E_avail endpoint. Reads ONLY the existing
# G2 input npz -- no tuple, no new branch, no training, no estimator. Ratifies nothing.
# Routed through mnv_guarded_run.py per OI-136 (a hardcoded cluster root at sys.path[0]
# silently imports another checkout's modules while parity reports every file CURRENT).
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=00:40:00
#SBATCH --job-name=pet-eavail-characterization
set -euo pipefail

checkout=$1
runtime=$2
inputs=$3
output=$4
expected_commit=$5

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
[[ -f "$inputs" ]]

# The candidate choices must already be committed: this job characterizes a
# pre-declared candidate, and a choice made after seeing these numbers would not be one.
candidates=nd-unfolding/pet/configuration_comparison/CANDIDATE_ENDPOINT_CHOICES-20260918.json
[[ -f "$candidates" ]]
git log -1 --format=%H -- "$candidates" >/dev/null

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
cp "$candidates" "$output/candidate-choices.json"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8

timeout --kill-after=30s 2100s "$runtime/bin/python" \
  nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
  --inventory "$output/guard.json" \
  -- nd-unfolding/pet/configuration_comparison/characterize_eavail_endpoint.py \
  --repo "$checkout" --inputs "$inputs" \
  --output "$output/eavail-characterization.json" > "$output/characterization.log" 2>&1

[[ -s "$output/eavail-characterization.json" ]]
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
