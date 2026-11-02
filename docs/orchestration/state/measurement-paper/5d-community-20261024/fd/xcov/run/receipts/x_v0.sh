#!/bin/bash
# GENCMP X, step V0 on a login node in omnifold_py310 (declaration section 2.1, binding ruling 1). Writes only under $R.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=260e299b37e2a82deaeef165b79d0757115e8887
cd "$R/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310"
export TMPDIR=$R/tmp
date -u +%FT%TZ; hostname
/usr/bin/time -v env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py v0 --run-dir "$R"
rc=$?; echo "rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "end"
