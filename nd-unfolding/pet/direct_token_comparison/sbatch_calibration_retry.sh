#!/bin/bash
# Retry preparation only; requires explicit authorization after job 58198332 failed.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=01:58:00
#SBATCH --job-name=pet-routing-calibration
set -eo pipefail

checkout=$1
runtime=$2
output=$3
expected_commit=$4
approval=$5
approval_sha=$6
cd "$checkout"
actual_commit=$(git rev-parse HEAD)
[[ "$actual_commit" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
"$runtime/bin/python" - "$approval" "$approval_sha" <<'PY'
import hashlib, json, pathlib, sys
payload = pathlib.Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(payload).hexdigest() == sys.argv[2]
authority = json.loads(payload)
assert authority['status'] == 'AUTHORIZED'
assert authority['retry_status'] == 'AUTHORIZED'
assert authority['retry_of'] == '58198332'
assert authority['calibration_wall_seconds'] == 7080
assert authority['profile'] == {'gpus': 1, 'cpus': 32, 'memory_GiB': 56}
assert authority['calibration_gpu_hours'] == 2
assert authority['total_gpu_hours'] == 290
assert authority['total_cpu_core_hours'] == 9296
PY
mkdir -p "$output"
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
"$runtime/bin/python" - "$output/allocation.txt" <<'PY'
import pathlib, re, sys
allocation = pathlib.Path(sys.argv[1]).read_text()
assert int(re.search(r'NumCPUs=(\d+)', allocation)[1]) == 32
assert int(re.search(r'NumNodes=(\d+)', allocation)[1]) == 1
assert 'TimeLimit=01:58:00' in allocation
assert 'MinMemoryNode=56G' in allocation or 'mem=56G' in allocation
PY
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

# Tests run in a separate CPU process so their GPU-disable fixture cannot affect calibration.
CUDA_VISIBLE_DEVICES=-1 "$runtime/bin/python" nd-unfolding/mnv_guarded_run.py \
  --expect-root "$checkout" --inventory "$output/tests-guard.json" \
  -- nd-unfolding/pet/direct_token_comparison/calibration_measure.py \
  --tests-only --output "$output/tests" > "$output/tests.log" 2>&1
[[ -z "$(git status --porcelain)" ]]

"$runtime/bin/python" nd-unfolding/mnv_guarded_run.py \
  --expect-root "$checkout" --inventory "$output/guard.json" \
  -- nd-unfolding/pet/direct_token_comparison/calibration_measure.py \
  --output "$output/measurement" > "$output/calibration.log" 2>&1 &
calibration_pid=$!
while kill -0 "$calibration_pid" 2>/dev/null; do
  bytes_kib=$(du -sk "$output" | cut -f1)
  printf '%s %s\n' "$(date -u +%FT%TZ)" "$bytes_kib" >> "$output/storage-meter.log"
  if (( bytes_kib > 4194304 )); then
    kill -TERM "$calibration_pid"
    wait "$calibration_pid" || true
    echo 'STORAGE_LIMIT' > "$output/terminal.txt"
    exit 1
  fi
  sleep 30
done
set +e
wait "$calibration_pid"
status=$?
set -e
printf '%s\n' "$status" > "$output/exit-code.txt"
if (( status != 0 )); then
  echo 'FAILED' > "$output/terminal.txt"
  exit "$status"
fi
echo 'COMPLETE' > "$output/terminal.txt"
