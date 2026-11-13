#!/bin/bash
# The three arms for the gbdt producer (note figure style). usage: arms_gbdt.sh <scratch>
S=$1; T=$S/wt-note/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools; R=$S/figrun/gbdt
mkdir -p $R
run() { env -i PATH=$S/figenv/mpl3112/bin:/usr/bin:/bin HOME=$S/cleanenv/home MPLCONFIGDIR=$S/figrun/mplcfg PYTHONDONTWRITEBYTECODE=1 python3 "$@"; }
run $T/capture_any.py $R/cap-before $S/wt-note-base/nd-unfolding/gbdt_model_dependence/analyze.py --out $R/out-before > $R/before.log 2>&1; echo before=$?
run $T/capture_any.py $R/cap-off $S/wt-note/nd-unfolding/gbdt_model_dependence/analyze.py --out $R/out-off > $R/off.log 2>&1; echo off=$?
run $T/capture_any.py $R/cap-after $S/wt-note/nd-unfolding/gbdt_model_dependence/analyze.py --out $R/out-after --print-style > $R/after.log 2>&1; echo after=$?
