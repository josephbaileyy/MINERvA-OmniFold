#!/usr/bin/env bash
# Part (b), eavail_marginal_vs_paper_pull_full.pdf: one arm of its installed recipe, then the stamp strip.
#   bash run_eavail.sh <worktree W> <f17|main> <HOUSEFONT 0|1> <3D xsec root> <scratch dir FR, must not exist>
# The installed file (7f272d26, make_figures.sh install_current_fig from note-figpins-20261122) is note-figround-
# 20261121's strip_stamp.py of note-figpass-20261119's arm 1 of f17 (runs/f17/CHECKS.txt: arms_layout.sh with ARM0=plain,
# so arm 1 = layout_run.py with LAYOUT_PALETTE=0 over remap_anc.py <anc> compare_to_paper_fullcov.py --ours <3D>
# --out-prefix <dir>/eavail_marginal_vs_paper). This runs that command with housefont_run.py in layout_run.py's place
# (HOUSEFONT=0 makes it layout_run.py exactly), not arms_layout.sh itself, which rewrites note-figpass-20261119/runs/.
# The producer:
#   f17   compare_to_paper_fullcov.py and its helper uq/reported_cells.py as f17 ran them, read from the f17 receipt
#         commit 59963f09b: the control, which reproduces the installed file;
#   main  W's own: since 430b42db2 the producer labels the heat map's cell boundaries and axes in GeV/c, as Fig. 3
#         prints them (Joseph 2026-11-28: "we should match them"). FIG3_LABELS=1 is then set, and housefont_run.py drops
#         the two texts.tsv rows that renamed the old "p_|| bin" / "p_T bin" labels, which the producer no longer draws.
# technote_style.py and restyle_2026_10.py come from W in both (technote_style is the same blob at 59963f09b;
# restyle_2026_10 acts only under --style, which neither arm passes).
set -u
W=$1; PROD=$2; HF=$3; X=$4; FR=$5
[ -e "$FR" ] && { echo "REFUSE: $FR exists"; exit 2; }
case "$HF" in 0|1) ;; *) echo "REFUSE: HOUSEFONT must be 0 or 1"; exit 2;; esac
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; T=$M/note-figstyle-20261117/tools; C=$M/note-figfonts-20261128/tools
V=$HOME/cov2d-work/figenv/rootmpl3108; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python; A=$HOME/cov2d-work/figfetch/anc
B=59963f09b
mkdir -p "$FR"/{o,cap,home,mplcfg,strip,producer/2d-unfolding/uq}
P=$FR/producer
case "$PROD" in
  f17)  git -C "$W" show "$B:2d-unfolding/compare_to_paper_fullcov.py" > "$P/2d-unfolding/compare_to_paper_fullcov.py"
        git -C "$W" show "$B:2d-unfolding/uq/reported_cells.py" > "$P/2d-unfolding/uq/reported_cells.py"; F3=0 ;;
  main) cp "$W/2d-unfolding/compare_to_paper_fullcov.py" "$P/2d-unfolding/"
        cp "$W/2d-unfolding/uq/reported_cells.py" "$P/2d-unfolding/uq/"; F3=1 ;;
  *)    echo "REFUSE: producer must be f17 or main"; exit 2 ;;
esac
cp "$W/technote_style.py" "$P/technote_style.py"; cp "$W/2d-unfolding/restyle_2026_10.py" "$P/2d-unfolding/"
[ "$(git -C "$W" rev-parse "$B:technote_style.py")" = "$(git -C "$W" hash-object "$P/technote_style.py")" ] \
  || { echo "REFUSE: technote_style.py differs from $B's"; exit 2; }
shasum -a 256 "$P/2d-unfolding/compare_to_paper_fullcov.py" "$P/2d-unfolding/uq/reported_cells.py" "$P/technote_style.py" \
  "$P/2d-unfolding/restyle_2026_10.py" "$X" > "$FR/inputs.sha256"
( cd "$FR/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mplcfg" PYTHONDONTWRITEBYTECODE=1 \
    HOUSEFONT=$HF FIG3_LABELS=$F3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    PYTHONPATH="" python3 "$T/capture_palette.py" "$FR/cap" "$C/housefont_run.py" "$T/remap_anc.py" "$A" \
    "$P/2d-unfolding/compare_to_paper_fullcov.py" --ours "$X" --out-prefix "$FR/o/eavail_marginal_vs_paper" ) \
    > "$FR/log.txt" 2>&1
r=$?; echo "eavail producer=$PROD HOUSEFONT=$HF rc=$r" | tee "$FR/steps.log"
[ $r = 0 ] || exit $r
"$PE" -I "$M/note-figround-20261121/tools/strip_stamp.py" "$FR/o/eavail_marginal_vs_paper_pull_full.pdf" \
  "$FR/strip/eavail_marginal_vs_paper_pull_full.pdf" "$FR/strip/eavail_marginal_vs_paper_pull_full.json" > "$FR/strip.log" 2>&1
r=$?; echo "strip rc=$r" | tee -a "$FR/steps.log"; cat "$FR/strip.log"
exit $r
