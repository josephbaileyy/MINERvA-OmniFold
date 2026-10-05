#!/bin/bash
set -eo pipefail
checkout=$1
runtime=$2
output=$3
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1
cd "$checkout"
exec "$runtime/bin/python" nd-unfolding/mnv_guarded_run.py \
  --expect-root "$checkout" --inventory "$output/guard.json" \
  -- nd-unfolding/pet/check_source_audit_runtime.py \
  --with-root --output "$output/audit"
