#!/usr/bin/env bash
# Recompute from count histograms and selected event rows in a fresh directory.
set -euo pipefail
source_dir=$(cd "$(dirname "$0")" && pwd)
output_dir=$(mktemp -d "${TMPDIR:-/tmp}/minerva-charge.XXXXXXXX")
run="$output_dir/precharge-20261125"
figures="$output_dir/ibu-chi2-20261123"
mkdir -p "$run/modes" "$figures/fig2" "$figures/resp/extract" "$figures/regenA5/out"
cp -R "$source_dir/inputs" "$run/"
cp "$source_dir"/*.py "$run/"
cp "$source_dir"/modes/{before.root,projections.py} "$run/modes/"
original="$source_dir/../ibu-chi2-20261123"
cp "$original/fig2/fig2_points.csv" "$figures/fig2/"
cp "$original"/resp/extract/{fig3,fig5}.csv "$figures/resp/extract/"
cp "$original"/regenA5/out/readout_{old,e}.json "$figures/regenA5/out/"
cd "$run"
export PRECHARGE_EVENTS="$run/inputs/events" OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
py=${PYTHON:-python3}
echo "Replay output in $run"
"$py" inputs/replay/replay.py > inputs/replay/baseline.txt
"$py" inputs/control/score.py > control-results.json
"$py" inputs/control/fine_score.py > inputs/control/fine-results.json
"$py" modes/projections.py > modes/projections.txt
"$py" score.py
"$py" threshold.py
"$py" verify.py "$PRECHARGE_EVENTS" > direct-verification.txt
"$py" display.py
"$py" width.py > width.txt
"$py" curvature_scale.py > curvature-scale.txt
"$py" compare_replay.py "$source_dir"
