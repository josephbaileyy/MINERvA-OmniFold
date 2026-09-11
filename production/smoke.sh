#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_bin=${PYTHON:-python3}
smoke_output=${1:?Usage: production/smoke.sh NEW_OUTPUT_DIRECTORY}
"$python_bin" production/prepare_events --config production/examples/fixture.json --output "$smoke_output/events.npz"
"$python_bin" production/unfold_gbdt.py --config production/examples/scalar.json --input "$smoke_output/events.npz" --output "$smoke_output/nominal"
"$python_bin" production/uncertainties.py run --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/scalar.json --input "$smoke_output/events.npz" --nominal "$smoke_output/nominal" --output "$smoke_output/members"
"$python_bin" production/uncertainties.py combine --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/scalar.json --input "$smoke_output/members" --nominal "$smoke_output/nominal" --output "$smoke_output/covariance"
"$python_bin" production/closure.py --config production/examples/scalar.json --input "$smoke_output/events.npz" --output "$smoke_output/closure"
"$python_bin" production/project.py --config production/examples/project.json --input "$smoke_output/covariance" --output "$smoke_output/projection"
