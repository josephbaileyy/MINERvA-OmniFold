#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 03:00:00
#SBATCH -A m3246
#SBATCH -J gencmp-b
#SBATCH -o /pscratch/sd/j/josephrb/gencmp-20261101/logs/b-%j.out
#SBATCH -e /pscratch/sd/j/josephrb/gencmp-20261101/logs/b-%j.err
B=/pscratch/sd/j/josephrb/gencmp-20261101
M=3410ed0c2a1847ddf590d3869f624bd974f2dce7
cd $B/deploy
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
export TMPDIR=$B/tmp
date -u +%FT%TZ; hostname
python -B nd-unfolding/fd_gencmp_rebuild.py --out $B/b/out --nproc 64
rc=$?
echo "rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
exit $rc
