#!/bin/bash
# Capture one bundle and four separate processes; never call a training runner.
set -euo pipefail
checkout=$1
runtime=$2
output=$3
device=$4
[[ "$device" == cpu || "$device" == gpu ]]
[[ ! -e "$output" ]]
mkdir -p "$output"
cd "$checkout"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8
base=nd-unfolding/pet/direct_token_comparison
run_guarded() {
  label=$1
  shift
  "$runtime/bin/python" nd-unfolding/mnv_guarded_run.py \
    --expect-root "$checkout" --inventory "$output/$label-guard.json" \
    -- "$@" > "$output/$label.log" 2>&1
}
run_guarded prepare "$base/numerical_diagnostic.py" prepare \
  --device cpu --output "$output/bundle"
for cell in on-0 off-0 off-1 on-1; do
  run_guarded "$cell" "$base/numerical_diagnostic.py" capture \
    --bundle "$output/bundle" --device "$device" --tf32 "${cell%-*}" \
    --output "$output/$cell"
done
run_guarded analysis "$base/analyze_numerical_diagnostic.py" "$output" \
  --device "$device" --output "$output/analysis"
