#!/bin/bash
# Size survey: local scratch MC AnaTuples vs current public open-data (xrdfs ls -l). Read-only.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
OUT=/pscratch/sd/j/josephrb/tmp-q2-opendata-20261014
H=root://fndca1.fnal.gov:1095
B=/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC
L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC
for p in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  timeout 120 xrdfs $H ls -l $B/Playlist$p > $OUT/remote_ls_$p.txt 2>&1; echo "$p xrdfs_rc=$?"
  stat -c '%n %s %y' $L/Playlist$p/*.root > $OUT/local_stat_$p.txt
done
