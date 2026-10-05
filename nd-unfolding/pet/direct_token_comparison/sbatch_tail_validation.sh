#!/bin/bash
# Tail validation of the four-arm execution path. Authorized 2026-09-18:
# <=1.5 GPU-hours, <=4 submissions, <=45 minutes each, <=5 GiB, repaired submissions
# counting as retries. No automatic retry of any kind happens here.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:44:00
#SBATCH --job-name=pet-tail-validation
set -euo pipefail

checkout=$1
runtime=$2
output=$3
expected_commit=$4
widths=$5
criteria_sha=$6

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"

criteria=nd-unfolding/pet/direct_token_comparison/VALIDATION_CRITERIA-20260918.json
# The criteria are frozen. Verifying the digest here means a threshold edited between
# freezing and execution stops the job rather than quietly taking effect.
actual=$("$runtime/bin/python" -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('$criteria').read_bytes()).hexdigest())")
[[ "$actual" == "$criteria_sha" ]] || { echo "criteria digest $actual != frozen $criteria_sha"; exit 3; }

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

timeout --kill-after=30s 2400s "$runtime/bin/python" \
  nd-unfolding/pet/direct_token_comparison/run_four_arm_experiment.py \
  --checkout "$checkout" --criteria "$criteria" --validate-only 4 \
  --widths "$widths" --rows 1024 --batch-size 256 --samples 10 \
  --output "$output/validation.json" > "$output/validation.log" 2>&1

[[ -z "$(git status --porcelain)" ]]
"$runtime/bin/python" - "$output/validation.json" "$criteria_sha" <<'PY'
import json, pathlib, sys
receipt = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert receipt['criteria_sha256'] == sys.argv[2], 'receipt records different criteria'
assert receipt['gpu_devices'], 'no GPU was used'
assert receipt['records'], 'no width was validated'
print('released', len(receipt['released_widths']),
      'hard stops', receipt['hard_stop_checks'],
      'complete', receipt['complete'])
PY
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
