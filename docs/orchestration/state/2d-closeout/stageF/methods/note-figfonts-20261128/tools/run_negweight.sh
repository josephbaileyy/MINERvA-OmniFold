#!/usr/bin/env bash
# Part (b), negweight_ratio_2d.pdf: one arm of its producer on the fetched inputs.
#   bash run_negweight.sh <worktree W> <PRINT_STYLE 0|1> <inputs dir> <scratch dir FR, must not exist>
# The recipe is make_figures.sh's line `run ../docs/analysis-note/figures/negweight_ratio_2d.pdf 2d-unfolding python
# plot_negweight_ratio.py` (defaults --est hist --seed 1), which reads HANDOFF_bkg_negweight/runs/ under its working
# directory. <inputs dir> holds the two ROOT files fetched by fetch/nw_fetch.sh (inputs/SHA256SUMS: the inventory shas);
# they are copied into FR's working directory under that relative path and checked again. PRINT_STYLE=1 adds
# --print-style. Under capture_palette.py, env -i, an empty HOME, figenv/rootmpl3108, BLAS threads 1.
set -u
W=$1; PS=$2; I=$3; FR=$4
[ -e "$FR" ] && { echo "REFUSE: $FR exists"; exit 2; }
case "$PS" in 0) EXTRA=();; 1) EXTRA=(--print-style);; *) echo "REFUSE: PRINT_STYLE must be 0 or 1"; exit 2;; esac
T=$W/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/tools
V=$HOME/cov2d-work/figenv/rootmpl3108
RUNS=$FR/cwd/HANDOFF_bkg_negweight/runs
mkdir -p "$FR"/{o,cap,home,mplcfg} "$RUNS"
cp "$I"/2d_xsec_purity_seed1_hist5.root "$I"/2d_xsec_negweight_seed1_hist5.root "$RUNS/"
( cd "$RUNS" && shasum -a 256 -c "$I/SHA256SUMS" ) > "$FR/inputs-check.txt" 2>&1 || { echo "REFUSE: inputs differ"; exit 2; }
( cd "$FR/cwd" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mplcfg" PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH="" \
    python3 "$T/capture_palette.py" "$FR/cap" "$W/2d-unfolding/plot_negweight_ratio.py" --out "$FR/o/negweight_ratio_2d.pdf" \
    ${EXTRA[@]+"${EXTRA[@]}"} ) > "$FR/log.txt" 2>&1
r=$?; echo "negweight PRINT_STYLE=$PS rc=$r: $(tail -1 "$FR/log.txt")" | tee "$FR/steps.log"
exit $r
