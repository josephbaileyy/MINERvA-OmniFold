#!/bin/bash
set -eo pipefail
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONPATH=/pscratch/sd/j/josephrb/pet-v2-source-audit-58832843/nd-unfolding/pet
cd /pscratch/sd/j/josephrb/pet-v2-source-audit-58832843
exec /pscratch/sd/j/josephrb/pet-v2-source-audit-runtime/bin/python nd-unfolding/mnv_guarded_run.py --expect-root "$PWD" --inventory /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910-preflight/runtime-guard.jsonl -- /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910-preflight/check_runtime.py
