#!/bin/bash
# GENCMP amendment E, rerun under addendum E-A1: a fresh clone at M' into $R, then E-S, E-M and the chain (R0 gating),
# on a login node in root_6_28. The first run's directory is not touched. No set -u (conda).
B=/pscratch/sd/j/josephrb/gencmp-e-20261101
R=$B/rerun1
M=1d936338d55645a5204c39ff9b02ea3290496003
[ -e "$R" ] && { echo "STOP: $R exists"; exit 2; }
mkdir -p "$R"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$R/receipts/deploy-host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$R/deploy" > "$R/logs/clone.log" 2>&1 || { echo clone failed; exit 3; }
cd "$R/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
want="07899d161bdb84fe6e6b549a3b8ee5886dde77a7 nd-unfolding/fd_gencmp_e.py
9e0272fab22643749df64ea91a6727130a77c9f5 nd-unfolding/fd_gencmp.py
4e760ef762467204ae1b7d306df82938a7b94bbf nd-unfolding/fd_g_figures.py
e938eeaa4abf4d33a31c96589d8f3c230db5ee90 nd-unfolding/fd_g_figures_check.py
e16c168778b60519d2d06159455d92ca43aad684 nd-unfolding/tests/test_fd_gencmp_e.py
728e7812efe47b71da102f7a180fd7870e2cfb60 docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/INPUTS.sha256"
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done <<< "$want" > "$R/receipts/deploy-blobs.txt"
[ $bad = 0 ] || { echo "STOP: a blob differs"; cat "$R/receipts/deploy-blobs.txt"; exit 9; }
echo "deploy ok at $M"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$R/tmp
PY="env -u PYTHONPATH python -B"
$PY -c "import sys,numpy,matplotlib;print('env',sys.version.split()[0],numpy.__version__,matplotlib.__version__)"
(cd nd-unfolding/tests && $PY -m unittest test_fd_gencmp_e > "$R/logs/tests-root_6_28.log" 2>&1; echo "tests rc=$? $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests-root_6_28.log" | tr '\n' ' ')")
for step in stage materialize chain; do
  echo "== $step $(date -u +%FT%TZ)"
  $PY nd-unfolding/fd_gencmp_e.py $step --run-dir "$R" > "$R/logs/e-$step.out" 2> "$R/logs/e-$step.err"
  rc=$?
  echo "$step rc=$rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { echo "STOP at $step"; break; }
done
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "end $(date -u +%FT%TZ)"
