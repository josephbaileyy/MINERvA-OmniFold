#!/usr/bin/env bash
# Part (c) arm: regenA4/receipts/regenA4_run.sh's tension step (2d5246a1; palette_run.py over diagnose_tension.py under
# env -i), with fontsize_run.py in palette_run.py's place. Everything else is that step's argv and environment.
#   bash run_tension_c.sh <producer worktree W> <xsec.root> <scratch dir FR, must not exist>
set -u
W=$1; X=$2; FR=$3
[ -e "$FR" ] && { echo "REFUSE: $FR exists"; exit 2; }
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; T=$M/note-figstyle-20261117/tools
C=$M/note-figfonts-20261128/tools
V=$HOME/cov2d-work/figenv/rootmpl3108; A=$HOME/cov2d-work/figfetch/anc
mkdir -p "$FR"/{tn/o,cap,home,mplcfg}
( cd "$FR/tn/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mplcfg" PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH="" \
    python3 "$T/capture_palette.py" "$FR/cap/tn" "$C/fontsize_run.py" "$T/remap_anc.py" "$A" \
    "$W/2d-unfolding/diagnose_tension.py" --ours "$X" --out-prefix "$FR/tn/o/tension" --style restyle-2026-10 --print-font ) \
    > "$FR/tn/log.txt" 2>&1
r=$?; echo "tension (c) rc=$r" | tee "$FR/steps.log"
exit $r
