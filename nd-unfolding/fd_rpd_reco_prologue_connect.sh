#!/bin/bash
# Run lane only: checked MAT setup and data-free dictionary/import trace.
# This command supplies no scientific run permission and submits no job.
set -euo pipefail
if [ "$#" -ne 5 ]; then
  echo 'usage: bash fd_rpd_reco_prologue_connect.sh CHECKOUT READY_CONFIG CONFIG_SHA RUN MAT_PYTHON' >&2
  exit 4
fi
reco_checkout=$1
reco_config=$2
reco_config_sha=$3
reco_run=$4
reco_python=$5
"$reco_python" -c 'from pathlib import Path; import sys; p=Path(sys.argv[1]).resolve(); c=Path("/global/cfs"); sys.exit(4 if p==c or c in p.parents else 0)' "$reco_run" || { echo 'STOP OUTPUT_LOCATION' >&2; exit 4; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export FD_RPD_RECO_CONNECT_ID
FD_RPD_RECO_CONNECT_ID=$("$reco_python" -c 'import uuid;print(uuid.uuid4())')
# This must precede source. Existing instrument pins the shared setup and all scripts it sources.
"$reco_python" "$reco_checkout/nd-unfolding/fd_rpd_inputs.py" check-mat-setup --r "$reco_run"
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
# The setup changes TMPDIR to shared scratch; restore the run-local directory afterwards.
export TMPDIR="$reco_run/tmp"
mkdir -p "$TMPDIR"
cd "$reco_checkout"
nice -n 19 "$reco_python" nd-unfolding/fd_rpd_reco_prologue.py \
  --config "$reco_config" --config-sha256 "$reco_config_sha" --run "$reco_run"
