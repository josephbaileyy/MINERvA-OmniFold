#!/bin/bash
# Local adler32 vs dCache-reported adler32 for size-identical files. Read-only on inputs.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
L=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC
B=/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC
for f in Playlist1P/MasterAnaDev_mc_AnaTuple_run00112000_Playlist.root Playlist1D/MasterAnaDev_mc_AnaTuple_run00111100_Playlist.root Playlist1A/MasterAnaDev_mc_AnaTuple_run00110001_Playlist.root; do
  echo "$f remote: $(timeout 60 xrdfs root://fndca1.fnal.gov:1095 query checksum $B/$f)"
  echo "$f local: $(xrdadler32 $L/$f)"
done
