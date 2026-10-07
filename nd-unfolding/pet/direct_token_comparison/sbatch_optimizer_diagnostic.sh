#!/bin/bash
# A fresh authorization is required; this launcher cannot run calibration.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:20:00
#SBATCH --job-name=pet-optimizer-diagnostic
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
assert authority['decision'] == 'optimizer-numerical-diagnostic-only'
assert authority['failed_job'] == '58301971'
assert authority['prior_charged_seconds'] >= 523
assert authority['wall_seconds'] == 1200
assert authority['profile'] == {'gpus': 1, 'cpus': 32, 'memory_GiB': 56}
assert authority['automatic_retry'] is False
assert authority['calibration_authorized'] is False
assert authority['full_matrix_authorized'] is False
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/optimizer-manifest.json')
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == authority['manifest_sha256']
for name, expected in json.loads(manifest.read_text())['files'].items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == expected, name
PY
mkdir -p "$output"
trap 'status=$?; printf "%s\n" "$status" > "$output/exit-code.txt"; if (( status != 0 )); then echo TECHNICAL_FAILURE > "$output/terminal.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
"$runtime/bin/python" - "$output/allocation.txt" <<'PY'
import pathlib, re, sys
allocation = pathlib.Path(sys.argv[1]).read_text()
assert int(re.search(r'NumCPUs=(\d+)', allocation)[1]) == 32
assert int(re.search(r'NumNodes=(\d+)', allocation)[1]) == 1
assert 'TimeLimit=00:20:00' in allocation
assert 'MinMemoryNode=56G' in allocation or 'mem=56G' in allocation
PY
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8
# Leave one minute for receipt closure and cleanup.
timeout --kill-after=10s 1140s "$runtime/bin/python" \
  nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
  --inventory "$output/diagnostic-guard.json" \
  -- nd-unfolding/pet/direct_token_comparison/optimizer_diagnostic.py \
  --device gpu --output "$output/capture" > "$output/diagnostic.log" 2>&1 &
worker=$!
while kill -0 "$worker" 2>/dev/null; do
  bytes_kib=$(du -sk "$output" | cut -f1)
  printf '%s %s\n' "$(date -u +%FT%TZ)" "$bytes_kib" >> "$output/storage-meter.log"
  if (( bytes_kib > 1048576 )); then
    echo STORAGE_LIMIT > "$output/terminal.txt"
    scancel "$SLURM_JOB_ID"
    exit 1
  fi
  sleep 5
done
wait "$worker"
[[ -z "$(git status --porcelain)" ]]
echo COMPLETE_DIAGNOSTIC > "$output/terminal.txt"
# Numerical mismatches are measurements, never permission to run calibration.
