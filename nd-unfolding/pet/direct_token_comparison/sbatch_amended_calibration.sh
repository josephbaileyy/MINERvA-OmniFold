#!/bin/bash
# Requires the bound single-attempt authorization before any compute stage.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=01:40:00
#SBATCH --job-name=pet-amended-calibration
set -euo pipefail

checkout=$1
runtime=$2
output=$3
expected_commit=$4
approval=$5
approval_sha=$6
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
assert authority['decision'] == 'amended-preflight-calibration-and-conditional-matrix'
assert authority['prior_jobs'] == ['58198332', '58201775', '58240587', '58277208', '58301971', '58320923']
assert authority['precision_policy'] == {'tf32_enabled': False, 'determinism_enabled': True, 'mixed_precision_policy': 'float32', 'floatx': 'float32'}
assert authority['prior_charged_seconds'] >= 742
assert authority['wall_seconds'] == 6000
assert authority['preflight_seconds'] == 1200
assert authority['calibration_seconds'] == 4800
assert authority['profile'] == {'gpus': 1, 'cpus': 32, 'memory_GiB': 56}
assert authority['total_gpu_hours'] == 290
assert authority['total_cpu_core_hours'] == 9296
assert authority['storage_GiB'] == 200
assert authority['scope'] == 'synthetic-only'
assert authority['automatic_retry'] is False
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/amended-manifest.json')
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == authority['manifest_sha256']
for name, digest in json.loads(manifest.read_text())['files'].items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == digest, name
PY
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
"$runtime/bin/python" - "$output/allocation.txt" <<'PY'
import pathlib, re, sys
allocation = pathlib.Path(sys.argv[1]).read_text()
assert int(re.search(r'NumCPUs=(\d+)', allocation)[1]) == 32
assert int(re.search(r'NumNodes=(\d+)', allocation)[1]) == 1
assert 'TimeLimit=01:40:00' in allocation
assert 'MinMemoryNode=56G' in allocation or 'mem=56G' in allocation
PY
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

stages() (
  # One shared 20-minute preflight budget includes tests, model checks and reload.
  deadline=$((SECONDS + 1200))
  CUDA_VISIBLE_DEVICES=-1 timeout --kill-after=10s 1200s "$runtime/bin/python" \
    nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
    --inventory "$output/tests-guard.json" \
    -- nd-unfolding/pet/direct_token_comparison/run_amended_tests.py \
     --output "$output/tests" > "$output/tests.log" 2>&1
  remaining=$((deadline - SECONDS))
  (( remaining > 0 ))
  timeout --kill-after=10s "${remaining}s" "$runtime/bin/python" \
    nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
    --inventory "$output/initialization-guard.json" \
    -- nd-unfolding/pet/direct_token_comparison/freeze_preflight_initialization.py \
    --output "$output/initialization" > "$output/initialization.log" 2>&1
  remaining=$((deadline - SECONDS))
  (( remaining > 0 ))
  timeout --kill-after=10s "${remaining}s" "$runtime/bin/python" \
    nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
    --inventory "$output/preflight-guard.json" \
    -- nd-unfolding/pet/direct_token_comparison/amended_preflight.py \
    --bundle "$output/initialization" --device gpu --output "$output/preflight" > "$output/preflight.log" 2>&1
  [[ -z "$(git status --porcelain)" ]]
  # A fresh process restores the frozen training seed and excludes smoke weights.
  timeout --kill-after=10s 4800s "$runtime/bin/python" \
    nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
    --inventory "$output/guard.json" \
    -- nd-unfolding/pet/direct_token_comparison/calibration_measure.py \
    --preflight "$output/preflight" --output "$output/measurement" \
    > "$output/calibration.log" 2>&1
)
stages &
worker=$!
while kill -0 "$worker" 2>/dev/null; do
  bytes_kib=$(du -sk "$output" | cut -f1)
  printf '%s %s\n' "$(date -u +%FT%TZ)" "$bytes_kib" >> "$output/storage-meter.log"
  if (( bytes_kib > 4194304 )); then
    echo STORAGE_LIMIT > "$output/terminal.txt"
    scancel "$SLURM_JOB_ID"
    exit 1
  fi
  sleep 30
done
wait "$worker"
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
# Scheduler completion, guard receipts and headroom are evaluated after exit.
# This launcher cannot submit full jobs or retry itself.
