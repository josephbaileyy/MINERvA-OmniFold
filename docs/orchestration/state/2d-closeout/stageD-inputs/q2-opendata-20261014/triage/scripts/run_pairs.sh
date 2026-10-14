#!/bin/bash
# Paired old-vs-current comparisons for chosen 1A Data and MC files. Writes only under $OUT.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
OUT=/pscratch/sd/j/josephrb/tmp-1a-triage-20261014
cd $OUT
LD=/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1A
RD=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/Data/Playlist1A
for r in 00006133 00006038 00006253 00008007; do
  f=MasterAnaDev_data_AnaTuple_run${r}_Playlist.root
  timeout 1800 python -I pair.py $LD/$f $RD/$f pair_data_$r.json > pair_data_$r.log 2>&1; echo "data $r rc=$?"
done
LM=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A
RM=root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC/Playlist1A
f=MasterAnaDev_mc_AnaTuple_run00110001_Playlist.root
timeout 5400 python -I pair.py $LM/$f $RM/$f pair_mc_00110001.json > pair_mc_00110001.log 2>&1; echo "mc 00110001 rc=$?"
