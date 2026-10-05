#!/bin/bash
# Cross-device gate coverage at the bucket widths (A3). GPU, short, no retry.
# Consumption so far under the one-GPU-hour ceiling: 911 s across three earlier
# submissions, two of which measured nothing.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:30:00
#SBATCH --job-name=pet-width-gate
set -euo pipefail

checkout=$1
runtime=$2
output=$3
expected_commit=$4
widths=$5

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"

"$runtime/bin/python" - <<'PY'
import hashlib, json, pathlib
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/amended-manifest.json')
for name, digest in json.loads(manifest.read_text())['files'].items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == digest, name
print('manifest bindings intact')
PY

export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

timeout --kill-after=30s 1500s "$runtime/bin/python" \
  nd-unfolding/pet/direct_token_comparison/gate_widths_crossdevice.py \
  --checkout "$checkout" --widths "$widths" \
  --output "$output/width-gate.json" > "$output/gate.log" 2>&1

[[ -z "$(git status --porcelain)" ]]
"$runtime/bin/python" - "$output/width-gate.json" <<'PY'
import json, pathlib, sys
receipt = json.loads(pathlib.Path(sys.argv[1]).read_text())
controls = receipt['controls']
# Both controls must land or every verdict in the receipt is void: a gate that
# cannot fail on the known-failing geometry is not measuring the gate.
assert controls['nominal_measured'] == 'PASS', controls
assert controls['variable_measured'] == 'FAIL', controls
print('controls ok; validated', len(receipt['validated_widths']),
      'failed', len(receipt['failed_widths']))
PY
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
