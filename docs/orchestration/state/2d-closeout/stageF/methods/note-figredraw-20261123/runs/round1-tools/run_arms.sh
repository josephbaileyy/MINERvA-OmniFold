#!/bin/bash
# The two arms of the note figure redraw (2026-11-23; README.md "Method"), for one figure.
#   bash run_arms.sh <worktree> <fig: bkg | cov | f16>
# Arm 0: the UNCHANGED producer, run exactly as the installed file was made (note-figpass-20261119):
#   bkg  layout_run.py (palette edits, then layout_lib edits) on methods_m3/fig_m3_background.py
#   cov  layout_run.py with LAYOUT_PALETTE=0 (layout edits only) on methods_m3/fig_m3_coverage.py
#   f16  the figure pass's tools/make_fig_fived16_headline.py, plain (python3 -I), as installed
#   each under note-figstyle-20261117/tools/capture_palette.py (records every data artist's arrays), env -i, the laptop
#   base conda (miniconda3), an empty HOME and MPLCONFIGDIR in a temp dir, BLAS threads 1.
#   Its PDF is compared with the installed file: bytes_but_date.py, and raster.py at 300 dpi.
# Arm 1: this record's copy (tools/<producer>), run plainly under the same environment; it draws the new layout itself
#   and dumps every plotted array to <stem>_data.json beside its PDF.
# Then tools/check_data.py compares arm 1's dump against arm 0's captured artists (per functional/cell name).
# Every command and its output go to runs/<fig>/CHECKS.txt. Exit 0 only if every check passes.
set -u
W=$1; FIG=$2
S=$W/docs/orchestration/state/2d-closeout/stageF/methods
N=$S/note-figredraw-20261123; FP=$S/note-figpass-20261119; PT=$S/note-figstyle-20261117/tools
M3=$W/docs/analysis-note/figures/methods_m3
VENV=/Users/josephbailey/miniconda3
P=$VENV/bin/python3
R=$N/runs/$FIG; mkdir -p "$R"; CK=$R/CHECKS.txt
TMPH=$(mktemp -d); trap 'rm -rf "$TMPH"' EXIT
ENV=(env -i PATH="$VENV/bin:/usr/bin:/bin" HOME="$TMPH" MPLCONFIGDIR="$TMPH/mpl" PYTHONDONTWRITEBYTECODE=1
     OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1)
case $FIG in
  bkg) STEM=m3_fig1_background; INST=paper_fig_bkg_residual; LP=1
       A0=("$FP/tools/layout_run.py" "$M3/fig_m3_background.py" --repo "$W" --outdir @OUT@)
       A1=("$N/tools/fig_m3_background.py" --repo "$W" --outdir @OUT@);;
  cov) STEM=m3_fig3_coverage; INST=paper_fig_coverage; LP=0
       A0=("$FP/tools/layout_run.py" "$M3/fig_m3_coverage.py" --repo "$W" --outdir @OUT@)
       A1=("$N/tools/fig_m3_coverage.py" --repo "$W" --outdir @OUT@);;
  f16) STEM=fived16_headline; INST=fived16_headline; LP=1
       A0=("$FP/tools/make_fig_fived16_headline.py" --out @OUT@)
       A1=("$N/tools/make_fig_fived16_headline.py" --out @OUT@);;
  *) echo "usage: run_arms.sh <worktree> bkg|cov|f16"; exit 2;;
esac
ok=1
{
echo "# $FIG ($(date -u +%Y-%m-%dT%H:%M:%SZ)): run_arms.sh <wt> $FIG; worktree HEAD $(git -C "$W" rev-parse --short HEAD);" \
     "env: $("$P" -c 'import sys,matplotlib,numpy;print("python",sys.version.split()[0],"matplotlib",matplotlib.__version__,"numpy",numpy.__version__)')"
for arm in arm0 arm1; do
  O=$R/$arm/out; C=$R/$arm/capture
  rm -rf "$O" "$C"; mkdir -p "$O" "$C"
  if [ $arm = arm0 ]; then src=("${A0[@]}"); else src=("${A1[@]}"); fi
  args=(); for a in "${src[@]}"; do args+=("${a//@OUT@/$O}"); done
  echo "== $arm: capture_palette.py <capture> ${args[*]//$W/<wt>}  (LAYOUT_PALETTE=$LP)"
  (cd "$O" && "${ENV[@]}" LAYOUT_PALETTE=$LP "$P" -I "$PT/capture_palette.py" "$C" "${args[@]}" > "$O/log.txt" 2>&1)
  rc=$?
  sed "s#$W#<wt>#g" "$O/log.txt" | sed 's/^/   | /'
  [ $rc = 0 ] || { echo "FAIL $arm: rc $rc"; ok=0; }
done
echo "== arm 0 against the installed docs/analysis-note/figures/$INST.pdf (sha256 $(shasum -a 256 "$W/docs/analysis-note/figures/$INST.pdf" | cut -c1-16)…)"
"$P" -I "$PT/bytes_but_date.py" "$W/docs/analysis-note/figures/$INST.pdf" "$R/arm0/out/$STEM.pdf" || ok=0
ras=$("$P" -I "$S/fig-restyle-20261031/tools/raster.py" "$W/docs/analysis-note/figures/$INST.pdf" "$R/arm0/out/$STEM.pdf"); rrc=$?
echo "raster 300 dpi: $ras (rc $rrc)"; [ $rrc = 0 ] || ok=0
echo "== arm 1 data against arm 0's captured artists (check_data.py $FIG)"
"$P" -I "$N/tools/check_data.py" "$FIG" "$R" || ok=0
echo "== text sizes and overlaps per arm (capture_palette.py .texts; overlaps are capture_any.py's box measure)"
"$P" -I - "$R" <<'PY' || ok=0
import json, statistics, sys
from pathlib import Path
bad = 0
for p in sorted(Path(sys.argv[1]).glob("arm*/capture/*.pdf.texts")):
    d = json.loads(p.read_text())
    s = [z for z, _ in d["texts"]]
    small = [t for z, t in d["texts"] if z < 7.0]
    arm = p.parts[-3]
    print(f"  {arm} {p.name[:-6]}: canvas {d['size_in'][0]:.2f} x {d['size_in'][1]:.2f} in; {len(s)} texts, font size "
          f"min {min(s):.2f}, median {statistics.median(s):.2f} pt; under 7 pt: {len(small)}; text overlaps "
          f"{len(d['text_overlaps'])}" + (f" {[o[:2] for o in d['text_overlaps']]}" if arm == "arm1" and d["text_overlaps"] else ""))
    if arm == "arm1" and small:
        bad = 1
sys.exit(bad)
PY
if [ $ok = 1 ]; then
  echo "== install arm 1 into figs/ (PDF, PNG at 150 dpi by pdftoppm)"
  mkdir -p "$N/figs"
  if [ $FIG = f16 ]; then pairs="fived16_headline_A:fived16_headline_A fived16_headline_B:fived16_headline_B"
  else pairs="$STEM:$INST"; fi
  for pr in $pairs; do
    src=${pr%%:*}; dst=${pr##*:}
    cp "$R/arm1/out/$src.pdf" "$N/figs/$dst.pdf"
    pdftoppm -r 150 -png -singlefile "$N/figs/$dst.pdf" "$N/figs/$dst"
    echo "  figs/$dst.pdf sha256 $(shasum -a 256 "$N/figs/$dst.pdf" | cut -d' ' -f1); figs/$dst.png"
  done
fi
echo "RUN-ARMS $FIG :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
} 2>&1 | tee "$CK"
grep -q "RUN-ARMS $FIG :: PASS" "$CK"
