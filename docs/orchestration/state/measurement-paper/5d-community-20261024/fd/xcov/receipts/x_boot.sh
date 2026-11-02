#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 03:00:00
#SBATCH -A m3246
#SBATCH -J gencmp-x-boot
# GENCMP X, step BOOT (FD-GENCMP-X-DECLARATION.md section 2.3): control B0 first, alone (the unreplaced
# bootstrap_replica at b = 1 must reproduce S1's data_b1_j101.npz bitwise); only if it holds, eight lanes of 32 threads,
# as S1's seed job packed them, run replicas 1-100 with the mapped draws. If B0 fails, no mapped replica is made and the
# statistical stream falls back to route A.
# From the deploy at the bound commit with empty porcelain; writes only under $R. No set -u (conda).
# Addendum X-A1: BOOT reads the amended V0 ($R/v0-a1), so it runs from $R/deploy-a1, the clone at the addendum's
# merge commit (BOUND); $R/deploy stays at M for V1, whose code the addendum does not change.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=${BOUND:?set BOUND to the bound commit}
mkdir -p "$R/logs" "$R/tmp" || exit 2
cd "$R/deploy-a1" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not the bound commit"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$R/tmp
PY="env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py boot --run-dir $R --threads 32"
date -u +%FT%TZ; hostname
$PY --native --replicas 1:1 > $R/logs/boot-native.log 2>&1
rc=$?; echo "native rc=$rc" >> $R/logs/boot-native.log
[ $rc = 0 ] || { echo "B0 failed (rc $rc): no mapped replicas; route A"; exit 0; }
i=1
for r in 1:13 14:26 27:39 40:52 53:64 65:76 77:88 89:100; do
  ( $PY --replicas $r > $R/logs/boot-$i.log 2>&1; echo "rc=$?" >> $R/logs/boot-$i.log ) &
  i=$((i+1))
done
wait
grep -H "rc=" $R/logs/boot-*.log
date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
