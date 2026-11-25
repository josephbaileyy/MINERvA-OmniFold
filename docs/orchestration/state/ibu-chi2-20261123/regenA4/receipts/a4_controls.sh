#!/usr/bin/env bash
# regenA amendment A4's controls, after regenA4_run.sh has run on OLD (FR_OLD) and E (FR_E).
#   bash a4_controls.sh <producer worktree W> <FR_OLD> <FR_E> <scratch dir for the strip control, must not exist>
# C-OLD: OLD's fig2, fig3 and tension PDFs against the installed files at W (bytes_but_date.py: EQUAL-BUT-DATE).
# C-SL-a: OLD's markers-layer slices against note-figpass-20261119/figs-r2 (bytes_but_date.py).
# C-SL-b: strip_stamp.py on the committed figs-r2 slices reproduces the installed slices byte for byte (sha256).
# Then the sha256 of every figure on both grids. Exit 0 only if every control passes.
set -u
W=$1; FO=$2; FE=$3; SC=$4
[ -e "$SC" ] && { echo "REFUSE: $SC exists"; exit 2; }
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; BBD=$M/note-figstyle-20261117/tools/bytes_but_date.py
P=$HOME/miniconda3/bin/python3; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python; F=$W/docs/analysis-note/figures
sha() { shasum -a 256 "$1" | cut -c1-64; }
ok=1; mkdir -p "$SC"
echo "== C-OLD: OLD against the installed files ($F)"
for p in fig2/out/MEFHC_5iter_xsec_proj_pt fig2/out/MEFHC_5iter_xsec_proj_pz fig3/o/MEFHC_5iter_pull_full \
         tn/o/tension_spectrum tn/o/tension_chi2_map tn/o/tension_mode_maps; do
  "$P" -I "$BBD" "$F/$(basename $p).pdf" "$FO/$p.pdf" || ok=0
done
echo "== C-SL-a: OLD's markers layer against figs-r2"
for f in MEFHC_5iter_xsec_paper_pt_slices MEFHC_5iter_xsec_paper_pz_slices; do
  "$P" -I "$BBD" "$M/note-figpass-20261119/figs-r2/$f.pdf" "$FO/sl/out/$f.pdf" || ok=0
done
echo "== C-SL-b: strip_stamp.py on the committed figs-r2 against the installed slices"
for f in MEFHC_5iter_xsec_paper_pt_slices MEFHC_5iter_xsec_paper_pz_slices; do
  "$PE" -I "$M/note-figround-20261121/tools/strip_stamp.py" "$M/note-figpass-20261119/figs-r2/$f.pdf" "$SC/$f.pdf" "$SC/$f.json" > "$SC/$f.log" 2>&1 || ok=0
  a=$(sha "$SC/$f.pdf"); b=$(sha "$F/$f.pdf"); [ "$a" = "$b" ] && echo "BYTE-EQUAL $f.pdf $a" || { echo "DIFFER $f.pdf $a vs installed $b"; ok=0; }
done
echo "== figures, sha256 (installed; OLD rerun; paper's edges)"
for p in fig2/out/MEFHC_5iter_xsec_proj_pt fig2/out/MEFHC_5iter_xsec_proj_pz fig3/o/MEFHC_5iter_pull_full \
         sl/strip/MEFHC_5iter_xsec_paper_pt_slices sl/strip/MEFHC_5iter_xsec_paper_pz_slices \
         tn/o/tension_spectrum tn/o/tension_chi2_map tn/o/tension_mode_maps; do
  b=$(basename $p); echo "$b.pdf installed $(sha "$F/$b.pdf") old $(sha "$FO/$p.pdf") e $(sha "$FE/$p.pdf")"
done
[ $ok = 1 ] && echo "A4-CONTROLS :: PASS" || echo "A4-CONTROLS :: FAIL"
[ $ok = 1 ]
