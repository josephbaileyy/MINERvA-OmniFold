#!/bin/bash
# Run the integration test set on the worktree; one log per suite, with user+sys time and rc.
set -u
W=<worktree>
S=$(dirname "$0"); TAG=$1; L=$S/logs/$TAG; mkdir -p "$L"
export TMPDIR=$S/tmp-$TAG; mkdir -p "$TMPDIR"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
RL=$(root-config --libdir)
PYR="env PYTHONPATH=$RL $S/venv313/bin/python"   # PyROOT + matplotlib + numpy
PY3=python3                                       # conda 3.12, no ROOT
cd "$W"
run() { local name=$1; shift; local t0=$(date +%s); /usr/bin/time -p "$@" > "$L/$name.txt" 2>&1; local rc=$?; echo "$name rc=$rc wall=$(( $(date +%s)-t0 ))s $(grep -E '^(user|sys) ' "$L/$name.txt" | tr '\n' ' ')"; }
N2=2d-unfolding/uq/coverage_fixed_truth/n2
run producer   $PYR -m unittest discover -s $N2 -p 'test_producer*.py' -v
run inventory  $PY3 docs/orchestration/state/next-preparation-20261009/guard/inventory.py $W $L/inventory.json
run harness    $PY3 -m unittest discover -s $N2 -p 'test_n2*.py' -v
run coverage   $PY3 -m pytest -q -p no:cacheprovider 2d-unfolding/uq/coverage_fixed_truth/test_coverage_fixed_truth.py
run ratchets   $PY3 -m unittest nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py -v
run cells_root $PYR -m pytest -v -p no:cacheprovider -rs 2d-unfolding/tests/test_reported_cells.py
run rollup     $PY3 -m pytest -v -p no:cacheprovider -rs 2d-unfolding/tests/test_final_rollup_full_refusal.py
run ki84       $PYR -W error::ResourceWarning -m unittest 2d-unfolding/tests/test_bootstrap_completeness_ki84.py -v
run bindings   $PY3 docs/orchestration/verify_hash_bindings.py
run hashtests  $PY3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_hash_bindings.py
rmdir "$TMPDIR" 2>/dev/null || { echo "TMPDIR not empty:"; ls -A "$TMPDIR" | head; }
