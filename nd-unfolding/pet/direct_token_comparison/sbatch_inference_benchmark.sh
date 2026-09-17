#!/bin/bash
# Bounded per-arm inference benchmark, authorized 2026-09-17. Cost only: it opens
# saved trained models read-only, retrains nothing, and cannot alter the frozen
# comparison or its receipts. It gates nothing -- the matrix result is reported
# whether or not this runs or succeeds.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:40:00
#SBATCH --job-name=pet-inference-benchmark
set -euo pipefail

checkout=$1
runtime=$2
matrix_output=$3
output=$4
expected_commit=$5
approval=$6
approval_sha=$7

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
"$runtime/bin/python" - "$approval" "$approval_sha" <<'PY'
import hashlib, json, pathlib, sys
payload = pathlib.Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(payload).hexdigest() == sys.argv[2]
authority = json.loads(payload)
assert authority['status'] == 'AUTHORIZED'
assert authority['scope'] == 'synthetic-only'
assert authority['automatic_retry'] is False
benchmark = authority['inference_benchmark']
assert benchmark['runs_after_matrix'] is True
assert benchmark['gates_the_matrix_report'] is False
spec = pathlib.Path(benchmark['specification'])
assert hashlib.sha256(spec.read_bytes()).hexdigest() == authority['inference_benchmark_specification_sha256']
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/amended-manifest.json')
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == authority['manifest_sha256']
for name, digest in json.loads(manifest.read_text())['files'].items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == digest, name
PY

mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

# Read-only over the matrix output; the benchmark writes only into its own directory.
timeout --kill-after=30s 2100s "$runtime/bin/python" \
  nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
  --inventory "$output/guard.json" \
  -- nd-unfolding/pet/direct_token_comparison/benchmark_inference.py \
  --checkout "$checkout" --matrix-output "$matrix_output" \
  --output "$output/inference-benchmark.json" > "$output/benchmark.log" 2>&1

[[ -z "$(git status --porcelain)" ]]
# The matrix receipts must be untouched: this is a read-only measurement.
[[ -z "$(find "$matrix_output" -newer "$output/allocation.txt" -name '*.json' -print -quit)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
