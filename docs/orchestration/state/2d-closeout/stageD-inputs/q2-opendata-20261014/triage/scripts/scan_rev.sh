#!/bin/bash
# Second worker for the 1A Data scan: manifest in REVERSE order, own output dir, stops when it meets
# a file the forward worker (scan_data/) has started (its .log exists).
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
OUT=/pscratch/sd/j/josephrb/tmp-1a-triage-20261014
L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1A
R=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/Data/Playlist1A
MAN=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/playlist_manifests/1A_Data.txt
mkdir -p $OUT/scan_data_rev
cd $OUT
tac "$MAN" | while read -r p; do
  f=$(basename "$p")
  [ -e scan_data/$f.log ] && { echo "met forward worker at $f"; break; }
  timeout 1800 python -I pair.py "$L/$f" "$R/$f" scan_data_rev/$f.json > scan_data_rev/$f.log 2>&1
  echo "$f rc=$?"
done
echo DONE
