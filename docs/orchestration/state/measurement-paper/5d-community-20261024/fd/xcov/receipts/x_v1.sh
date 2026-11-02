#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -A m3246
#SBATCH -J gencmp-x-v1
# GENCMP X, step V1 (FD-GENCMP-X-DECLARATION.md section 2.2): MODE=probe (-t 00:15:00; one band and Flux 0-9, then the
# price) or MODE=full (-t 01:45:00). Set by the submission: sbatch -t ... --export=ALL,MODE=probe x_v1.sh.
# From the deploy at the bound commit with empty porcelain; writes only under $R. No set -u (conda).
# Addendum X-A2: V1 runs again from $R/deploy-a2, the clone at the addendum's merge commit (BOUND), and writes
# $R/v1-a2; the failed full run (60679146) from $R/deploy wrote no readout.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=${BOUND:?set BOUND to the bound commit}
mkdir -p "$R/logs" "$R/tmp" || exit 2
cd "$R/deploy-a2" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not the bound commit"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310"
export TMPDIR=$R/tmp
date -u +%FT%TZ; hostname
if [ "$MODE" = probe ]; then F=--probe; else F=; fi
env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py v1 --run-dir "$R" $F
rc=$?; echo "rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
exit $rc
