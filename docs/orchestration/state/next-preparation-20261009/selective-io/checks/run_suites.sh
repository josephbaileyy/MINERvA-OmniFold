#!/bin/bash
# usage: run_suites.sh TREE LOG ; runs the driver-adjacent regression suites on TREE
T=$1; LOG=$2; : > $LOG
export TMPDIR=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/c5961a1c-c2f8-4299-b73b-907c4dff568b/scratchpad/selio/tmp
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
RP=$(root-config --libdir)
cd $T
echo "tree $T head $(git rev-parse HEAD) driver-sha256 $(shasum -a 256 2d-unfolding/unfold_2d_omnifold_unbinned.py|cut -c1-64) dirty-files $(git status --porcelain | wc -l)" >> $LOG
run() { name=$1; shift; s=$(date +%s); out=$("$@" 2>&1); rc=$?; e=$(( $(date +%s)-s )); [ -n "${FULL:-}" ] && { mkdir -p "$FULL"; echo "$out" > "$FULL/$(echo $name | tr '/ ' '__').txt"; }; summ=$(echo "$out" | grep -E "^(Ran |OK|FAILED|[0-9]+ (passed|failed)|=+ .*(passed|failed))" | tr '\n' ' '); echo "$name | rc=$rc | ${e}s | $summ" >> $LOG; echo "$out" | grep -E "^(FAIL|ERROR):" | sed 's/^/    /' >> $LOG; }
for t in 2d-unfolding/tests/test_selective_io.py 2d-unfolding/tests/test_bootstrap_completeness_ki84.py 2d-unfolding/tests/test_reported_cells.py 2d-unfolding/tests/test_final_rollup_full_refusal.py; do [ -f $t ] && run "$t" env PYTHONPATH=$RP python3.13 -m unittest $t; done
for t in test_producer_provenance test_n2_harness test_producer_final_dependencies; do run "n2/$t" env PYTHONPATH=$RP python3.13 -m unittest discover -s 2d-unfolding/uq/coverage_fixed_truth/n2 -t 2d-unfolding/uq/coverage_fixed_truth/n2 -p $t.py; done
for t in test_oi136_rooted_insert_ratchet test_oi136_failopen_inventory_ratchet test_flux_universe_fix; do run "nd/$t" env PYTHONPATH=$RP python3.13 -m unittest nd-unfolding/tests/$t.py; done
run "nd/test_hash_bindings" python3.12 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_hash_bindings.py
run "verify_hash_bindings" python3.12 docs/orchestration/verify_hash_bindings.py
run "verify_receipt_artifacts" python3.12 docs/orchestration/verify_receipt_artifacts.py
