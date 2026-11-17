#!/bin/bash
# The three arms for plot_minerva_landscape.py (note figure style). usage: arms_land.sh <scratch>
S=$1; T=$S/wt-note/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools; R=$S/figrun/land
run() { env -i PATH=$S/figenv/mpl3108/bin:/usr/bin:/bin HOME=$S/cleanenv/home MPLCONFIGDIR=$S/figrun/mplcfg PYTHONDONTWRITEBYTECODE=1 python3 "$@"; }
for arm in before off after; do
  rm -rf $R/out-$arm $R/cap-$arm; mkdir -p $R/out-$arm
  case $arm in before) P=$S/wt-note-base/3d-unfolding/plot_minerva_landscape.py; A="";; off) P=$S/wt-note/3d-unfolding/plot_minerva_landscape.py; A="";; after) P=$S/wt-note/3d-unfolding/plot_minerva_landscape.py; A="--print-style";; esac
  ( cd $R/out-$arm && run $T/capture_any.py $R/cap-$arm $P $A > ../$arm.log 2>&1 ); echo "$arm=$?"
  pdftoppm -r 100 -singlefile $R/out-$arm/minerva_unfolding_landscape.pdf $R/$arm-raster
done
