#!/usr/bin/env bash
# The Supplement editor's push gate (the director, 2026-11-12). usage: gate.sh <worktree> <new empty log dir>
# Runs every step, records each exit status unpiped, and exits 0 only if all pass and the tree is clean.
set -u
WT=$(cd "$1" && pwd); L=$2
mkdir "$L" || { echo "log dir $L exists"; exit 9; }
M=$WT/docs/orchestration/state/2d-closeout/stageF/methods
RC=$M/rater-calibration
export PAR_GLOBAL_TEMP=$L/par; mkdir -p "$PAR_GLOBAL_TEMP"
fail=0
step() {  # step <name> <cmd...>
  local name=$1; shift
  "$@" > "$L/$name.log" 2>&1
  local rc=$?
  printf '%-22s rc=%s\n' "$name" "$rc" | tee -a "$L/summary.txt"
  [ "$rc" -eq 0 ] || fail=1
}
echo "head $(git -C "$WT" rev-parse HEAD) $(date -u +%FT%TZ)" | tee "$L/summary.txt"
step fill-test        python3 -I "$M/methods-short-20261109/check_round.py" "$WT" --fill-test
step make-values-self bash -c "cd '$WT' && python3 -I docs/analysis-note/make_values_fived16.py --self-test"
if [ -f "$WT/docs/analysis-note/check_style.py" ]; then
  step check-style    bash -c "cd '$WT/docs/analysis-note' && python3 -I check_style.py"
else
  STYLE=$(git -C "$WT" ls-files | grep -E '(^|/)check_style\.py$' | head -1)
  if [ -n "$STYLE" ]; then step check-style bash -c "cd '$WT' && python3 -I '$WT/$STYLE' . --part supplement"
  else echo "check-style            ABSENT (helper-3's hand-off pending)" | tee -a "$L/summary.txt"; fail=1; fi
fi
step supp-pointers    bash -c "cd '$WT/docs/analysis-note' && python3 -I check_supp_pointers.py"
step supp-constants   python3 -I "$M/methods-short-20261109/literals-20261112/check_supplement_constants.py" "$WT"
step values-check     bash -c "cd '$WT' && python3 -I docs/analysis-note/make_values_fived16.py --check"
step supp-rater-copy  bash "$RC/make_supp_rater_copy.sh" "$WT" "$L/supp.txt"
step rater-copy       bash "$RC/make_rater_copy.sh" "$WT" "$L/paper.txt"
if [ -f "$L/paper.holddiff.txt" ]; then
  # make_rater_copy.sh's own rule: the word-level holddiff passes ("VERDICT: PASS"), or, if it fails on order alone
  # (a layout reflow), the order-insensitive multiset check passes ("multiset VERDICT: PASS"). Both are recorded.
  last=$(tail -1 "$L/paper.holddiff.txt")
  strict=$(grep -m1 -E '^VERDICT: ' "$L/paper.holddiff.txt")
  echo "holddiff: word-level [$strict]; final [$last]" | tee -a "$L/summary.txt"
  case "$last" in "VERDICT: PASS"|"multiset VERDICT: PASS") ;; *) fail=1 ;; esac
else echo "holddiff: missing" | tee -a "$L/summary.txt"; fail=1; fi
grep -E 'DESYNC|SYNC' "$L/fill-test.log" | tail -5 >> "$L/summary.txt"
links=$(find "$RC/build" -type l 2>/dev/null | wc -l | tr -d ' ')
st=$(git -C "$WT" status --short | wc -l | tr -d ' ')
echo "build symlinks left: $links; git status lines: $st" | tee -a "$L/summary.txt"
[ "$st" -eq 0 ] || fail=1
echo "GATE $([ $fail -eq 0 ] && echo PASS || echo FAIL)" | tee -a "$L/summary.txt"
exit $fail
