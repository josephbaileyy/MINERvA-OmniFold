#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 03:00:00
#SBATCH -A m3246
#SBATCH -J gencmp-x-boot
# GENCMP X, step BOOT (FD-GENCMP-X-DECLARATION.md section 2.3): eight lanes of 32 threads on one node, as S1's seed job
# packed them. Lane 1 runs control B0 (the unreplaced bootstrap_replica at b = 1, which must reproduce S1's
# data_b1_j101.npz bitwise) and then replicas 1-13; lanes 2-8 run the rest of 1-100 with the mapped draws.
# From the deploy at the bound commit with empty porcelain; writes only under $R. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=${BOUND:?set BOUND to the bound commit}
cd "$R/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not the bound commit"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$R/tmp
PY="env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py boot --run-dir $R --threads 32"
date -u +%FT%TZ; hostname
( $PY --native --replicas 1:1 > $R/logs/boot-native.log 2>&1; echo "native rc=$?" >> $R/logs/boot-native.log
  $PY --replicas 1:13 > $R/logs/boot-1.log 2>&1; echo "rc=$?" >> $R/logs/boot-1.log ) &
i=2
for r in 14:26 27:39 40:52 53:64 65:76 77:88 89:100; do
  ( $PY --replicas $r > $R/logs/boot-$i.log 2>&1; echo "rc=$?" >> $R/logs/boot-$i.log ) &
  i=$((i+1))
done
wait
grep -H "rc=" $R/logs/boot-*.log
date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
