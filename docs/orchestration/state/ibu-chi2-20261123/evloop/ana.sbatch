#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --mem=96G
#SBATCH -t 01:30:00
#SBATCH -J ibuchi_ana
#SBATCH -o /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/ana_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/ana_%j.err
# ibuchi merge + offline pass. Reads ROOT/out only; writes ROOT/out/..._MEFHC.root and ROOT/products.
set -eo pipefail
ROOT=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
set +u; source $REPO/setup_salloc_env.sh
cd $ROOT/out; ls runEventLoopOmniFold_1?.root | wc -l | grep -qx 12 || { echo "REFUSED: not 12 playlist outputs"; exit 2; }
[ ! -e runEventLoopOmniFold_MEFHC.root ] || { echo "REFUSED: merged output exists"; exit 2; }
hadd -f runEventLoopOmniFold_MEFHC.root runEventLoopOmniFold_1A.root runEventLoopOmniFold_1B.root runEventLoopOmniFold_1C.root runEventLoopOmniFold_1D.root runEventLoopOmniFold_1E.root runEventLoopOmniFold_1F.root runEventLoopOmniFold_1G.root runEventLoopOmniFold_1L.root runEventLoopOmniFold_1M.root runEventLoopOmniFold_1N.root runEventLoopOmniFold_1O.root runEventLoopOmniFold_1P.root
mkdir -p $ROOT/products && /usr/bin/time -v python3 $ROOT/scripts/ana.py > $ROOT/products/ana.json
sha256sum $ROOT/out/runEventLoopOmniFold_MEFHC.root $ROOT/products/*
