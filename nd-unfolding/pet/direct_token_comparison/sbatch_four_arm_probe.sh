#!/bin/bash
# A3: gate the realizable bucket widths and measure per-arm GPU cost. Approved by
# Joseph on 2026-09-18 with a ceiling of one GPU-hour; 50 minutes on one GPU caps it
# below that. No training to convergence, no closure statistic, no retry.
#
# The bound freezer and preflight require at least eight application CPUs and exactly
# one A100, so the allocation provides both. The probe changes only the fixtures those
# bound artifacts run on; their gate logic and tolerances are untouched.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:50:00
#SBATCH --job-name=pet-four-arm-probe
set -euo pipefail

checkout=$1
runtime=$2
source_receipt=$3
output=$4
expected_commit=$5

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
[[ -f "$source_receipt" ]]
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"

# Every manifest-bound file must still hash to its bound digest: this probe drives
# bound artifacts, so a drifted one would invalidate the gate it reports.
"$runtime/bin/python" - <<'PY'
import hashlib, json, pathlib
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/amended-manifest.json')
for name, digest in json.loads(manifest.read_text())['files'].items():
    actual = hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()
    assert actual == digest, name
print('manifest bindings intact')
PY

export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

timeout --kill-after=30s 2700s "$runtime/bin/python" \
  nd-unfolding/pet/direct_token_comparison/probe_four_arm_geometry_and_cost.py \
  --checkout "$checkout" --source-receipt "$source_receipt" \
  --output "$output/four-arm-probe.json" > "$output/probe.log" 2>&1

[[ -z "$(git status --porcelain)" ]]
"$runtime/bin/python" - "$output/four-arm-probe.json" <<'PY'
import json, pathlib, sys
receipt = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert receipt['gpu_devices'], 'no GPU was used'
assert receipt['gate_records'], 'no width was gated'
assert set(receipt['cost_summary']) == {'A', 'B', 'C', 'D'}, 'not every arm was timed'
print('gate_complete', receipt['gate_complete'],
      'validated', len(receipt['validated_widths']),
      'failed', len(receipt['failed_widths']))
PY
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
