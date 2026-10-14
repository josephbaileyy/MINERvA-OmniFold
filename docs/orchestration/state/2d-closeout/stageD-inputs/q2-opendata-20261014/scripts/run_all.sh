#!/bin/bash
# Full-entry metadata + key joins for the chosen files. Read-only on inputs; writes only under $OUT.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
OUT=/pscratch/sd/j/josephrb/tmp-q2-opendata-20261014
cd $OUT
L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC
R=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC
for spec in 1A:00110001 1A:00110000 1P:00112000 1D:00111100; do
  p=${spec%%:*}; r=${spec##*:}; tag=${p}_${r}
  f=Playlist$p/MasterAnaDev_mc_AnaTuple_run${r}_Playlist.root
  [ -f meta_local_$tag.json ] || python -I meta.py $L/$f meta_local_$tag.json
  [ -f meta_remote_$tag.json ] || timeout 900 python -I meta.py $R/$f meta_remote_$tag.json
  python -I meta_diff.py meta_local_$tag.json meta_remote_$tag.json > meta_diff_$tag.txt 2>&1
  for t in Truth MasterAnaDev; do
    timeout 3000 python -I key_join.py $L/$f $R/$f $t join_${t}_$tag.json > join_${t}_$tag.log 2>&1
    echo "$tag $t rc=$?"
  done
done
