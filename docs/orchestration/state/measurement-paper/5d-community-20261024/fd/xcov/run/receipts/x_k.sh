#!/bin/bash
# GENCMP X, step K (FD-GENCMP-X-DECLARATION.md section 2.4; addendum X-A2, binding #684 ruling 1): once, on a login node,
# in omnifold_py310, from $R/deploy-a2 at M''' with empty porcelain, after the full V1 wrote $R/v1-a2/v1.json. Writes
# only under $R ($R/k/, $R/logs/k.log). A stop is written into k/k.json and is final. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=b2e2d23263d379e8d5affc1f27aaea18175bb66c
[ -e "$R/k" ] && { echo "STOP: $R/k exists (K runs once)"; exit 2; }
[ -f "$R/v1-a2/v1.json" ] || { echo "STOP: no full V1 readout in $R/v1-a2"; exit 2; }
cd "$R/deploy-a2" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'''"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310"
export TMPDIR=$R/tmp
{ hostname; date -u +%FT%TZ; } > "$R/receipts/k-host.txt"
/usr/bin/time -f "k wall %e s rss %M KB" env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py k --run-dir "$R" > "$R/logs/k.log" 2>&1
rc=$?; echo "k rc=$rc"; date -u +%FT%TZ; tail -3 "$R/logs/k.log"
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
exit $rc
