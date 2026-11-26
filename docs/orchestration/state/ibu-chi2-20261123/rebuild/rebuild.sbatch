#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -J ibuchi_rb
#SBATCH -o /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/rb_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/rb_%j.err
# ibuchi rebuild on corrected pT edges. Reads ROOT/out/runEventLoopOmniFold_MEFHC.root only; writes ROOT/products/rebuild only.
set -eo pipefail
ROOT=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
set +u; source $REPO/setup_salloc_env.sh
[ ! -e $ROOT/products/rebuild/rebuild.npz ] || { echo "REFUSED: rebuild output exists"; exit 2; }
/usr/bin/time -v python3 $ROOT/scripts/rebuild.py > $ROOT/products/rebuild.json
sha256sum $ROOT/products/rebuild/rebuild.npz $ROOT/products/rebuild.json
