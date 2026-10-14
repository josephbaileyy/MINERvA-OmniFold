#!/bin/bash
# Full 1A scan: pair.py on every 1A Data (253) or MC (41) file, local copy vs current public copy.
# Usage: scan_all.sh data|mc. Writes only under $OUT/scan_<kind>/.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
OUT=/pscratch/sd/j/josephrb/tmp-1a-triage-20261014
kind=$1
if [ "$kind" = data ]; then
  L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1A
  R=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/Data/Playlist1A
  MAN=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/playlist_manifests/1A_Data.txt
else
  L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A
  R=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC/Playlist1A
  MAN=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/playlist_manifests/1A_MC.txt
fi
mkdir -p $OUT/scan_$kind
cd $OUT
while read -r p; do
  f=$(basename "$p")
  [ -s scan_$kind/$f.json ] && continue
  timeout 1800 python -I pair.py "$L/$f" "$R/$f" scan_$kind/$f.json > scan_$kind/$f.log 2>&1
  echo "$f rc=$?"
done < "$MAN"
echo DONE
