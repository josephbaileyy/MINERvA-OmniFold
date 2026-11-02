#!/bin/bash
# GENCMP amendment E: E-S, E-M, then the chain (E-R0 gate, E-1), on a login node in root_6_28 (binding ruling 1).
# No set -u (conda). Writes only under $B.
B=/pscratch/sd/j/josephrb/gencmp-e-20261101
M=6cd095d6773a45c8deef47d298245ea270a636ae
cd "$B/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$B/tmp
PY="env -u PYTHONPATH python -B"
$PY -c "import sys,numpy,matplotlib;print('env',sys.version.split()[0],numpy.__version__,matplotlib.__version__)"
hostname; date -u +%FT%TZ
for step in stage materialize chain; do
  echo "== $step $(date -u +%FT%TZ)"
  $PY nd-unfolding/fd_gencmp_e.py $step --run-dir "$B" > "$B/logs/e-$step.out" 2> "$B/logs/e-$step.err"
  rc=$?
  echo "$step rc=$rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { echo "STOP at $step"; break; }
done
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "end $(date -u +%FT%TZ)"
