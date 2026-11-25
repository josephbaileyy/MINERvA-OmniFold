#!/usr/bin/env bash
# regenA amendment A4: the note's installed layer of each figure, on one input. Laptop, figenv; 0 node-h.
#   bash regenA4_run.sh <producer worktree W> <old|e> <xsec.root> <scratch dir FR, must not exist>
# Each step is the invocation the installed layer's own record ran, with its outputs and records sent under FR:
#   fig2  note-figround3-20261121/tools/run_r3.sh:21 (arm 1): compose_fig2_r3.py -> MEFHC_5iter_xsec_proj_{pt,pz}.pdf
#   fig3  run_r3.sh:74-78 (arm 1): compose_fig3_r3.py over palette_run.py and compare_to_paper_fullcov.py --sd-label
#         -> MEFHC_5iter_pull_full.pdf
#   sl    note-figpass-20261119 chunk E (runs/markers/CHECKS.txt:1, arm 1): compose_slices_markers.py
#         -> MEFHC_5iter_xsec_paper_{pt,pz}_slices.pdf (figs-r2); then note-figround-20261121/tools/strip_stamp.py
#         (figenv/pdfedit) on each -> the installed layer
#   tn    note-figstyle-20261117 tier 2 (~/cov2d-work/figrun/tier2.sh 40e7b0fa, its tension step; arms.sh arm 1):
#         palette_run.py over diagnose_tension.py, under env -i -> tension_{spectrum,chi2_map,mode_maps}.pdf
set -u
W=$1; SET=$2; X=$3; FR=$4
[ -e "$FR" ] && { echo "REFUSE: $FR exists"; exit 2; }
case "$SET" in old|e) ;; *) echo "REFUSE: set must be old or e"; exit 2;; esac
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; T=$M/note-figstyle-20261117/tools
V=${A4_VENV:-$HOME/cov2d-work/figenv/rootmpl3108}; PY=$V/bin/python3; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python
# A4_VENV is set only by tier2_argv_equal.sh, to a stub venv that records each call instead of running it.
A=$HOME/cov2d-work/figfetch/anc
ST=(--style restyle-2026-10 --print-font)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p "$FR"/{fig2/out,fig3/o,sl/out,sl/strip,tn/o,cap,home,"mplcfg-$(basename "$V")"}
rc_all=0
note() { echo "$*" | tee -a "$FR/steps.log"; }
note "# regenA4 $SET ($(date -u +%FT%TZ)): W=$(git -C "$W" rev-parse HEAD) X=$X"

# fig2
( cd "$FR/fig2" && FIG2_ROUND_JSON="$FR/fig2/r2.json" FIG2_R3_JSON="$FR/fig2/r3.json" "$PY" "$T/capture_palette.py" "$FR/cap/fig2" \
    "$T/remap_anc.py" "$A" "$M/note-figround3-20261121/tools/compose_fig2_r3.py" "$X" "$A" "$FR/fig2/out" ) > "$FR/fig2/log.txt" 2>&1
r=$?; note "fig2 rc=$r"; [ $r = 0 ] || rc_all=1

# fig3
( cd "$FR/fig3/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mplcfg-$(basename "$V")" PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 FIG3_ROUND_JSON="$FR/fig3/r2.json" FIG3_R3_JSON="$FR/fig3/r3.json" \
    python3 "$T/capture_palette.py" "$FR/cap/fig3" "$M/note-figround3-20261121/tools/compose_fig3_r3.py" "$T/palette_run.py" \
    "$T/remap_anc.py" "$A" "$W/2d-unfolding/compare_to_paper_fullcov.py" --ours "$X" --out-prefix "$FR/fig3/o/MEFHC_5iter" \
    "${ST[@]}" --sd-label ) > "$FR/fig3/log.txt" 2>&1
r=$?; note "fig3 rc=$r"; [ $r = 0 ] || rc_all=1

# slices: markers layer, then the stamp strip
( cd "$FR/sl" && "$PY" "$T/capture_palette.py" "$FR/cap/sl" "$T/remap_anc.py" "$A" \
    "$M/note-figpass-20261119/tools/compose_slices_markers.py" --pt-ncols 3 --logx --font-floor 7 --pz-top-hundredths 30 \
    --pub-size-percent 100 --pub-edge-hundredths 40 "$X" "$A" "$FR/sl/out" ) > "$FR/sl/log.txt" 2>&1
r=$?; note "slices markers rc=$r"; [ $r = 0 ] || rc_all=1
for f in MEFHC_5iter_xsec_paper_pt_slices MEFHC_5iter_xsec_paper_pz_slices; do
  "$PE" -I "$M/note-figround-20261121/tools/strip_stamp.py" "$FR/sl/out/$f.pdf" "$FR/sl/strip/$f.pdf" "$FR/sl/strip/$f.json" \
    >> "$FR/sl/strip.log" 2>&1
  r=$?; note "strip $f rc=$r"; [ $r = 0 ] || rc_all=1
done

# tension: arms.sh arm 1 as tier2.sh's tension step makes it (tier2_argv_equal.sh checks the equality)
( cd "$FR/tn/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mplcfg-$(basename "$V")" PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH="" \
    python3 "$T/capture_palette.py" "$FR/cap/tn" "$T/palette_run.py" "$T/remap_anc.py" "$A" \
    "$W/2d-unfolding/diagnose_tension.py" --ours "$X" --out-prefix "$FR/tn/o/tension" "${ST[@]}" ) > "$FR/tn/log.txt" 2>&1
r=$?; note "tension rc=$r"; [ $r = 0 ] || rc_all=1

note "# done $SET ($(date -u +%FT%TZ)) rc_all=$rc_all"
exit $rc_all
