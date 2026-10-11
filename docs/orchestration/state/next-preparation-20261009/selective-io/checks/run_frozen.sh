#!/bin/bash
# usage: run_frozen.sh TREE LOG : the frozen SB1 and XR package checks on TREE
T=$1; LOG=$2; : > $LOG
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/c5961a1c-c2f8-4299-b73b-907c4dff568b/scratchpad/selio
export TMPDIR=$SP/tmp OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
RP=$(root-config --libdir); PY=$SP/venv313/bin/python
Q=docs/orchestration/state/next-preparation-20261009
cd $T
echo "tree $T head $(git rev-parse HEAD) driver-sha256 $(shasum -a 256 2d-unfolding/unfold_2d_omnifold_unbinned.py|cut -c1-64) dirty-files $(git status --porcelain | wc -l | tr -d ' ')" >> $LOG
for c in d4335d3b 07428e5d; do echo "git diff --quiet $c HEAD on its package: $(git diff --quiet $c HEAD -- $([ $c = d4335d3b ] && echo $Q/sb1-prep || echo $Q/two-d-followup/xr) && echo identical || echo DIFFERS)" >> $LOG; done
run() { name=$1; shift; s=$(date +%s); out=$("$@" 2>&1); rc=$?; e=$(( $(date +%s)-s )); [ -n "${FULL:-}" ] && { mkdir -p "$FULL"; echo "$out" > "$FULL/$(echo $name | tr '/ ' '__').txt"; }; summ=$(echo "$out" | grep -E "^(Ran |OK|FAILED|manifest|OUT OF DATE|CURRENT)" | tr '\n' ' '); echo "$name | rc=$rc | ${e}s | $summ" >> $LOG; echo "$out" | grep -E "^(FAIL|ERROR):|refus|Refus|OUT OF DATE|differ" | head -12 | sed 's/^/    /' >> $LOG; }
for t in test_package_consistency test_branch_select test_sb1_guarded test_launch_chain; do run "sb1-prep/$t" env PYTHONPATH=$RP $PY -m unittest discover -s $Q/sb1-prep/tests -t $Q/sb1-prep/tests -p $t.py; done
run "xr manifest --check" python3 $Q/two-d-followup/xr/xr_admit.py manifest --check
run "xr tests/test_xr.py" env PYTHONPATH=$RP $PY -m unittest discover -s $Q/two-d-followup/xr/tests -t $Q/two-d-followup/xr/tests -p test_xr.py
