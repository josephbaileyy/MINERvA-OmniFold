#!/bin/bash
set -eo pipefail
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1
cd /pscratch/sd/j/josephrb/pet-v2-source-audit-58832843
exec /pscratch/sd/j/josephrb/pet-v2-source-audit-runtime/bin/python nd-unfolding/mnv_guarded_run.py \
 --expect-root "$PWD" \
 --inventory /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910-preflight/source-guard.jsonl \
 -- nd-unfolding/pet/launch_typed_descriptor_source_audit.py \
 --authorization /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910-preflight/authorization.json \
 --authorization-sha256 "$(sha256sum /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910-preflight/authorization.json | cut -d ' ' -f 1)" \
 --expected-commit 588328438e096680a2295bebc7cc93ad9fccc3ed \
 --output /pscratch/sd/j/josephrb/pet-v2-source-audit-20260910
