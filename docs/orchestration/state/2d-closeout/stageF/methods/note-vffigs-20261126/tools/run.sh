#!/bin/bash
# The V_F redraw of fived16_headline and fived16_genresidual (README.md). Local, 0 node-h.
#   bash tools/run.sh <worktree>
# For each figure:
#   control: the UNCHANGED producer on the OLD inputs, run as the installed file was made; its PDF must be byte-equal
#            to the installed file at the base of this branch (git show <base>:docs/analysis-note/figures/<name>.pdf).
#   vf:      this record's copy (tools/), input-only edits; run twice, the two PDFs and values files byte-equal.
# The headline runs as round 4 of note-figredraw-20261123 did (miniconda3 base, capture_palette.py, LAYOUT_PALETTE=1);
# the genresidual as note-genresid-20261120 did (cov2d's figenv/mpl3108). env -i, an empty HOME and MPLCONFIGDIR,
# BLAS threads 1. Everything goes to runs/CHECKS.txt; the V_F outputs are copied to figs/. Exit 0 only if every check holds.
set -u
W=$1
BASE=362011d24428f848746a43fc126661708cffbbe1
S=$W/docs/orchestration/state/2d-closeout/stageF/methods
N=$S/note-vffigs-20261126; PT=$S/note-figstyle-20261117/tools
R=$N/runs; F=$N/figs
rm -rf "$R" "$F"; mkdir -p "$R" "$F"; CK=$R/CHECKS.txt
TMPH=$(mktemp -d); trap 'rm -rf "$TMPH"' EXIT
CONDA=/Users/josephbailey/miniconda3
MPL=/Users/josephbailey/cov2d-work/figenv/mpl3108
envrun() { local V=$1; shift; env -i PATH="$V/bin:/usr/bin:/bin" HOME="$TMPH" MPLCONFIGDIR="$TMPH/mpl" \
  PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 "$@"; }
sha() { shasum -a 256 "$1" | cut -c1-64; }
ok=1
check() { if [ "$1" = "$2" ]; then echo "  OK   $3"; else echo "  FAIL $3: $1 != $2"; ok=0; fi; }
{
echo "# run.sh ($(date -u +%Y-%m-%dT%H:%M:%SZ)); worktree HEAD $(git -C "$W" rev-parse HEAD); base $BASE"
for V in $CONDA $MPL; do echo "env $V: $("$V/bin/python3" -c 'import sys,matplotlib,numpy;print("python",sys.version.split()[0],"matplotlib",matplotlib.__version__,"numpy",numpy.__version__)')"; done
for t in tools/make_fig_fived16_headline.py tools/make_fig_fived16_genresidual.py; do echo "copy $t sha256 $(sha "$N/$t")"; done

echo "== fived16_headline"
H0=$S/note-figredraw-20261123/tools/make_fig_fived16_headline.py
want=$(git -C "$W" show "$BASE:docs/analysis-note/figures/fived16_headline.pdf" | shasum -a 256 | cut -c1-64)
for arm in control vf1 vf2; do
  O=$R/headline/$arm; mkdir -p "$O/out" "$O/cap"
  if [ $arm = control ]; then P=$H0; else P=$N/tools/make_fig_fived16_headline.py; fi
  (cd "$O/out" && envrun $CONDA LAYOUT_PALETTE=1 $CONDA/bin/python3 -I "$PT/capture_palette.py" "$O/cap" "$P" --variant P \
     --out "$O/out" > "$O/log.txt" 2>&1) || { echo "  FAIL $arm rc $?"; ok=0; }
  sed "s#$W#<wt>#g" "$O/log.txt" | grep -v "timestamp seems very low" | sed 's/^/   | /'
done
check "$(sha "$R/headline/control/out/fived16_headline.pdf")" "$want" "control: the unchanged producer on the OLD record = the installed PDF ($want)"
for x in fived16_headline.pdf fived16_headline_values.json fived16_headline_data.json; do
  check "$(sha "$R/headline/vf1/out/$x")" "$(sha "$R/headline/vf2/out/$x")" "V_F two runs byte-equal: $x"
done

echo "== fived16_genresidual"
G0=$S/note-genresid-20261120/tools/make_fig_fived16_genresidual.py
want=$(git -C "$W" show "$BASE:docs/analysis-note/figures/fived16_genresidual.pdf" | shasum -a 256 | cut -c1-64)
for arm in control vf1 vf2; do
  O=$R/genresidual/$arm; mkdir -p "$O/out"
  if [ $arm = control ]; then P=$G0; else P=$N/tools/make_fig_fived16_genresidual.py; fi
  (cd "$W" && envrun $MPL $MPL/bin/python3 -I "$P" --out "$O/out" > "$O/log.txt" 2>&1)
  rc=$?
  sed "s#$W#<wt>#g" "$O/log.txt" | grep -v "timestamp seems very low" | sed 's/^/   | /'
  if [ $arm = control ]; then
    # main's producer checks the printed C_e-era carbon chi2; on this branch values_fived16.tex prints the V_F ones,
    # so the unchanged producer must refuse here (the check that keeps the figure and the table together)
    if [ $rc != 0 ] && grep -q "chi2 .* vs printed" "$O/log.txt"; then
      echo "  OK   control: the unchanged producer refuses on this branch, its printed-chi2 check firing (V_F table, C_e-era record)"
    else echo "  FAIL control: rc $rc without the printed-chi2 refusal"; ok=0; fi
  elif [ $rc != 0 ]; then echo "  FAIL $arm rc $rc"; ok=0; fi
done
# the byte control runs at main's values_fived16.tex (the file the installed figure was checked against): a temporary
# worktree at the base's merge-base with origin/main
MB=$(git -C "$W" merge-base "$BASE" origin/main)
TW=$TMPH/mainwt; git -C "$W" worktree add -q --detach "$TW" "$MB"
O=$R/genresidual/control-main; mkdir -p "$O/out"
(cd "$TW" && envrun $MPL $MPL/bin/python3 -I "$TW/docs/orchestration/state/2d-closeout/stageF/methods/note-genresid-20261120/tools/make_fig_fived16_genresidual.py" \
   --out "$O/out" > "$O/log.txt" 2>&1) || { echo "  FAIL control-main rc $?"; ok=0; }
sed "s#$TW#<main-wt>#g" "$O/log.txt" | grep -v "timestamp seems very low" | sed 's/^/   | /'
git -C "$W" worktree remove --force "$TW"
echo "  control-main ran at merge-base $MB"
check "$(sha "$O/out/fived16_genresidual.pdf")" "$want" "control: the unchanged producer on the OLD records at main = the installed PDF ($want)"
for x in fived16_genresidual.pdf fived16_genresidual_values.json; do
  check "$(sha "$R/genresidual/vf1/out/$x")" "$(sha "$R/genresidual/vf2/out/$x")" "V_F two runs byte-equal: $x"
done

echo "== outputs"
cp "$R/headline/vf1/out/fived16_headline.pdf" "$R/headline/vf1/out/fived16_headline_values.json" \
   "$R/headline/vf1/out/fived16_headline_data.json" "$F/"
cp "$R/genresidual/vf1/out/fived16_genresidual.pdf" "$R/genresidual/vf1/out/fived16_genresidual_values.json" "$F/"
(cd "$F" && shasum -a 256 * > SHA256SUMS && sed 's/^/  /' SHA256SUMS)
rm -f "$R"/*/*/out/*.png
[ $ok = 1 ] && echo "RUN :: PASS" || echo "RUN :: FAIL"
} 2>&1 | tee "$CK"
grep -q "^RUN :: PASS$" "$CK"
