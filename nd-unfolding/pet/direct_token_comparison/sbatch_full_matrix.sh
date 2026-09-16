#!/bin/bash
# Frozen 24-job paired routing matrix. Requires the bound authorization and a
# passed calibration before any submission; this launcher cannot create either.
# Throttled to two concurrent full jobs by the array specification itself, which
# is the grant's limit expressed where Slurm enforces it rather than in prose.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=12:00:00
#SBATCH --job-name=pet-routing-matrix
#SBATCH --array=0-23%2
set -euo pipefail

checkout=$1
runtime=$2
output=$3
expected_commit=$4
approval=$5
approval_sha=$6

# Run-card order, indices 0..23: ordinary, injected, shuffle x eight seeds.
modes=(ordinary injected shuffle)
seeds=(17 29 43 59 71 89 101 113)
index=${SLURM_ARRAY_TASK_ID:?array task id required}
(( index >= 0 && index < 24 ))
mode=${modes[$((index / 8))]}
seed=${seeds[$((index % 8))]}
stem="${mode}-${seed}"

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
"$runtime/bin/python" - "$approval" "$approval_sha" "$mode" "$seed" <<'PY'
import hashlib, json, pathlib, sys
payload = pathlib.Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(payload).hexdigest() == sys.argv[2]
authority = json.loads(payload)
assert authority['status'] == 'AUTHORIZED'
assert authority['decision'] == 'amended-preflight-calibration-and-conditional-matrix'
assert authority['scope'] == 'synthetic-only'
assert authority['automatic_retry'] is False
assert authority['precision_policy'] == {'tf32_enabled': False, 'determinism_enabled': True, 'mixed_precision_policy': 'float32', 'floatx': 'float32'}
assert authority['profile'] == {'gpus': 1, 'cpus': 32, 'memory_GiB': 56}
assert authority['total_gpu_hours'] == 290
assert authority['total_cpu_core_hours'] == 9296
assert authority['storage_GiB'] == 200
# The 2026-09-16 gate scope and the geometry verification it is paired with.
assert authority['gate_scope']['stress_only_cases'] == ['variable']
assert authority['gate_scope']['production_geometry_verified_each_run'] is True
for key in ('authority_source', 'gate_scope_authority'):
    assert hashlib.sha256(pathlib.Path(authority[key]).read_bytes()).hexdigest() == authority[f'{key}_sha256'], key
manifest = pathlib.Path('nd-unfolding/pet/direct_token_comparison/amended-manifest.json')
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == authority['manifest_sha256']
for name, digest in json.loads(manifest.read_text())['files'].items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == digest, name
# This task must match the frozen run card at its own index, not merely be valid.
card = json.loads(pathlib.Path('nd-unfolding/pet/direct_token_comparison/run-card.json').read_text())
mode, seed = sys.argv[3], int(sys.argv[4])
matching = [j for j in card['jobs'] if j['mode'] == mode and j['seed'] == seed]
assert len(matching) == 1, f'{mode}/{seed} is not exactly one frozen job'
argv = matching[0]['argv']
assert argv[argv.index('--rows') + 1] == '1000000'
assert argv[argv.index('--test-rows') + 1] == '250000'
assert argv[argv.index('--iterations') + 1] == '3'
assert argv[argv.index('--epochs') + 1] == '5'
assert argv[argv.index('--batch-size') + 1] == '1024'
PY

mkdir -p "$output"
# Refuse only this task's own products, so 24 tasks may share one directory while
# none can overwrite another's. Every artifact name is prefixed by its stem.
for existing in "$output/$stem.json" "$output/$stem".*.npz "$output/$stem".*.keras; do
  [[ ! -e "$existing" ]]
done
mkdir -p "$output/logs"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/logs/$stem.terminal"; printf "%s\n" "$status" > "$output/logs/$stem.exit"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/logs/$stem.allocation"
"$runtime/bin/python" - "$output/logs/$stem.allocation" <<'PY'
import pathlib, re, sys
allocation = pathlib.Path(sys.argv[1]).read_text()
assert int(re.search(r'NumCPUs=(\d+)', allocation)[1]) == 32
assert int(re.search(r'NumNodes=(\d+)', allocation)[1]) == 1
assert 'TimeLimit=12:00:00' in allocation
assert 'MinMemoryNode=56G' in allocation or 'mem=56G' in allocation
PY
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
export TF_NUM_INTRAOP_THREADS=7 TF_NUM_INTEROP_THREADS=1 TF_DETERMINISTIC_OPS=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8

run() (
  timeout --kill-after=30s 42900s "$runtime/bin/python" \
    nd-unfolding/mnv_guarded_run.py --expect-root "$checkout" \
    --inventory "$output/logs/$stem.guard.json" \
    -- nd-unfolding/pet/run_typed_token_comparison.py \
    --rows 1000000 --test-rows 250000 --mode "$mode" --seed "$seed" \
    --epochs 5 --iterations 3 --batch-size 1024 \
    --output "$output/$stem.json" > "$output/logs/$stem.log" 2>&1
)
run &
worker=$!
while kill -0 "$worker" 2>/dev/null; do
  # A pipe rewrites the status, so default rather than trusting du's exit code.
  own_kib=$(du -ck "$output/$stem".* 2>/dev/null | tail -1 | cut -f1)
  own_kib=${own_kib:-0}
  shared_kib=$(du -sk "$output" | cut -f1)
  shared_kib=${shared_kib:-0}
  printf '%s own=%s shared=%s\n' "$(date -u +%FT%TZ)" "$own_kib" "$shared_kib" \
    >> "$output/logs/$stem.storage"
  # Per-job 4 GiB, and a shared-directory ceiling well inside the 200 GiB grant.
  if (( own_kib > 4194304 )) || (( shared_kib > 83886080 )); then
    echo STORAGE_LIMIT > "$output/logs/$stem.terminal"
    scancel "$SLURM_JOB_ID"
    exit 1
  fi
  sleep 60
done
wait "$worker"
[[ -z "$(git status --porcelain)" ]]
echo 0 > "$output/logs/$stem.exit"
echo COMPLETE > "$output/logs/$stem.terminal"
# Reduction, gates and any resource accounting happen after the array is closed.
# This launcher cannot submit further jobs, extend the array, or retry itself.
