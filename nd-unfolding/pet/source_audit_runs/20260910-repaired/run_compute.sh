#!/bin/bash
set -eo pipefail
AUDIT_CHECKOUT=$1
AUDIT_PYTHON=$2/bin/python
AUDIT_RUN_ROOT=$3
AUDIT_AUTH_SHA256=$4
export TF_ENABLE_ONEDNN_OPTS=1
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1
cd "$AUDIT_CHECKOUT"
exec "$AUDIT_PYTHON" nd-unfolding/mnv_guarded_run.py \
  --expect-root "$AUDIT_CHECKOUT" --inventory "$AUDIT_RUN_ROOT/guard.json" \
  -- nd-unfolding/pet/launch_typed_descriptor_source_audit.py \
  --authorization "$AUDIT_RUN_ROOT/authorization.json" \
  --authorization-sha256 "$AUDIT_AUTH_SHA256" \
  --expected-commit ca34a03a9f04ec16b56064c5bc6faaf85b9ebf17 \
  --output "$AUDIT_RUN_ROOT/audit"
