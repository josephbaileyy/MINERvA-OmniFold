#!/bin/bash
# OI-74, second run: fast-forward the canonical cluster checkout to github/main, moving the four byte-identical
# untracked files that stopped the first run (STOP 26, REPORT.md) aside first. Under DECLARATION-2.md in this directory.
# Run once, from the local side, as:  ssh saul.nersc.gov 'bash -s' < ff2.sh
# Every STOP exits non-zero with its own code. Nothing in the tree is written before W2; every STOP from W2 on
# restores all six files (the two live-state files from the first run's aside copies, and any of the four already
# moved) and re-verifies them.
set -u

R=/pscratch/sd/j/josephrb/MINERvA-OmniFold
A=/pscratch/sd/j/josephrb/oi74-ff-20261030
OLD=32e403b84e9e8f9d9bc435028749f896653c7a43
F1=docs/orchestration/LIVE-STATE.md
F2=docs/orchestration/state/live-state-last-known.json
LAUNCHER_PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold
U=$A/untracked-at-added-paths
FOUR="docs/orchestration/dashboard.html docs/orchestration/dashboard_collector.py docs/orchestration/test_dashboard_collector.py nd-unfolding/tests/test_cstat_100rep.py"
export GIT_OPTIONAL_LOCKS=0

# No hooks, no automatic gc or maintenance, for every git call against the tree.
G() { git -C "$R" -c core.hooksPath=/dev/null -c gc.auto=0 -c maintenance.auto=false "$@"; }
now() { date -u +%FT%TZ; }
stop() { echo "STOP $1: $2"; echo "date_utc_end $(now)"; exit "$1"; }
tracked() { G status --porcelain --untracked-files=no; }
untracked_count() { G status --porcelain | grep -c '^??'; }
sums() { (cd "$1" && sha256sum "$2" "$3" | awk '{print $1}'); }
EXPECTED_TRACKED=$(printf ' M %s\n M %s' "$F1" "$F2")
MOVED=""

rollback() {
  echo "ROLLBACK: restoring the two live-state files from $A and any moved file from $U"
  cp -p "$A/LIVE-STATE.md" "$R/$F1" && cp -p "$A/live-state-last-known.json" "$R/$F2"
  echo "rollback_cp_rc $?"
  (cd "$R" && sha256sum "$F1" "$F2")
  for p in $MOVED; do
    if [ -e "$R/$p" ] || [ -L "$R/$p" ]; then echo "rollback_move $p TARGET-EXISTS (left in $U)"
    else mv -n "$U/$p" "$R/$p"; echo "rollback_move $p rc $?"; fi
  done
  for p in $FOUR; do echo "rollback_four $p $( [ -e "$R/$p" ] && G hash-object -- "$p" || echo absent)"; done
  t=$(tracked); echo "rollback_head $(G rev-parse HEAD)"
  if [ "$t" = "$EXPECTED_TRACKED" ] && [ "$(sums "$R" "$F1" "$F2")" = "$(sums "$A" LIVE-STATE.md live-state-last-known.json)" ]
  then echo "rollback_tracked OK (the two files, as before)"; else
    echo "rollback_tracked MISMATCH"; printf '%s\n' "$t" | sed 's/^/  tracked| /'; fi
}

echo "host $(hostname)"; echo "date_utc $(now)"; echo "git $(git --version)"

# ---- Preconditions: read-only. Each is a STOP. ----
q=$(squeue --me -h -o '%i|%T|%j|%Z'); rc=$?
[ "$rc" -eq 0 ] || stop 10 "squeue --me rc=$rc, so the job check could not be made"
n=$(printf '%s' "$q" | grep -c .); echo "P1 squeue_me_jobs $n"; printf '%s' "$q" | sed 's/^/  job| /'; [ -n "$q" ] && echo
[ "$n" -eq 0 ] || stop 11 "$n job(s) running or pending under --me"

h=$(G rev-parse HEAD); echo "P2 head $h"
[ "$h" = "$OLD" ] || stop 12 "HEAD is not $OLD"
b=$(G symbolic-ref -q --short HEAD); echo "P2 branch ${b:-DETACHED}"
[ "$b" = "main" ] || stop 13 "not on branch main"
[ ! -e "$R/.git/MERGE_HEAD" ] && [ ! -e "$R/.git/index.lock" ] || stop 14 "a merge or index lock is in progress"

t=$(tracked); rc=$?; echo "P3 tracked_rc $rc"; printf '%s\n' "$t" | sed 's/^/  tracked| /'
[ "$rc" -eq 0 ] && [ "$t" = "$EXPECTED_TRACKED" ] || stop 15 "tracked porcelain is not exactly the two live-state files"
U0=$(untracked_count); echo "P4 untracked_before $U0"

# The first run's aside directory, handled explicitly: it must hold exactly that run's three files, they must still
# check, and the two live-state files in the tree must still be the bytes those copies hold.
[ ! -e "$U" ] || stop 17 "the subdirectory $U already exists"
listing=$( [ -d "$A" ] && (cd "$A" && ls -A | LC_ALL=C sort | tr '\n' ' ') )
echo "P6 aside_listing ${listing:-MISSING}"
[ "$listing" = "LIVE-STATE.md SHA256SUMS live-state-last-known.json " ] \
  || stop 16 "the aside directory $A is missing or does not hold exactly the first run's three files"
(cd "$A" && sha256sum -c SHA256SUMS > /dev/null) || stop 18 "the first run's aside copies no longer match their SHA256SUMS"
s_tree=$(sums "$R" "$F1" "$F2"); s_aside=$(sums "$A" LIVE-STATE.md live-state-last-known.json)
echo "P6 tree_equals_aside $( [ "$s_tree" = "$s_aside" ] && echo YES || echo NO)"
[ "$s_tree" = "$s_aside" ] || stop 19 "the two live-state files in the tree differ from the first run's aside copies"

# ---- W2: restore the two files to HEAD. This is the first write. ----
G checkout -- "$F1" "$F2"; rc=$?; echo "W2 checkout_rc $rc"
t=$(tracked)
if [ "$rc" -ne 0 ] || [ -n "$t" ]; then rollback; stop 22 "restore to HEAD failed or left tracked changes"; fi
echo "W2 tracked_after_restore 0"

# ---- W3: fetch github. ----
timeout 3600 git -C "$R" -c core.hooksPath=/dev/null -c gc.auto=0 -c maintenance.auto=false fetch github; rc=$?
echo "W3 fetch_rc $rc"
[ "$rc" -eq 0 ] || { rollback; stop 23 "git fetch github failed"; }
NEW=$(G rev-parse refs/remotes/github/main); echo "W3 github_main $NEW"
G merge-base --is-ancestor "$OLD" "$NEW" || { rollback; stop 24 "github/main does not descend from $OLD"; }
echo "W3 behind $(G rev-list --count "$OLD..$NEW") ahead $(G rev-list --count "$NEW..$OLD")"

# ---- P5: what the fast-forward would land on. Read-only, between fetch and merge. ----
# Any added path present with bytes different from NEW's blob is a STOP. The untracked, not-ignored ones must be
# exactly the four this run is allowed to move.
present=0; identical=0; differ=0; blocking=0; blocking_set=""
while IFS= read -r -d '' p; do
  if [ -e "$R/$p" ] || [ -L "$R/$p" ]; then
    present=$((present + 1))
    want=$(G rev-parse "$NEW:$p"); have=$(G hash-object -- "$p" 2>/dev/null || echo unreadable)
    if [ "$want" = "$have" ]; then identical=$((identical + 1)); else
      differ=$((differ + 1)); [ "$differ" -le 20 ] && echo "  differs| $p"; fi
    if ! G check-ignore -q -- "$p"; then blocking=$((blocking + 1)); blocking_set="$blocking_set$p "
      [ "$blocking" -le 20 ] && echo "  untracked-not-ignored| $p"; fi
  fi
done < <(G diff --name-only -z --diff-filter=A "$OLD" "$NEW")
echo "P5 added $(G diff --name-only --diff-filter=A "$OLD" "$NEW" | grep -c .) present $present identical $identical differ $differ untracked_not_ignored $blocking"
[ "$differ" -eq 0 ] || { rollback; stop 25 "$differ added path(s) exist in the tree with different bytes"; }
want_set=$(printf '%s\n' $FOUR | LC_ALL=C sort | tr '\n' ' '); have_set=$(printf '%s\n' $blocking_set | LC_ALL=C sort | tr '\n' ' ')
[ "$have_set" = "$want_set" ] || { rollback; stop 26 "the untracked, not-ignored added paths are not exactly the four"; }

# ---- W5: move the four aside. Each is re-hashed against NEW's blob immediately before it moves. ----
mkdir "$U" || { rollback; stop 31 "could not create $U"; }
for p in $FOUR; do
  want=$(G rev-parse "$NEW:$p"); have=$(G hash-object -- "$p" 2>/dev/null || echo unreadable)
  echo "W5 rehash $p want $want have $have"
  [ "$want" = "$have" ] || { rollback; stop 29 "$p no longer matches the fetched main's blob"; }
  before=$(cd "$R" && sha256sum "$p" | awk '{print $1}')
  mkdir -p "$U/$(dirname "$p")" && mv -n "$R/$p" "$U/$p" && [ ! -e "$R/$p" ] && [ -e "$U/$p" ] \
    || { rollback; stop 31 "moving $p aside failed"; }
  MOVED="$MOVED$p "
  after=$(cd "$U" && sha256sum "$p" | awk '{print $1}')
  [ "$before" = "$after" ] || { rollback; stop 31 "the moved copy of $p does not have the bytes it had in the tree"; }
done
(cd "$U" && sha256sum $FOUR > SHA256SUMS)
echo "W5 moved $U"; sed 's/^/  moved| /' "$U/SHA256SUMS"

# A last job check, immediately before the tree moves.
q=$(squeue --me -h -o '%i|%T|%j|%Z'); rc=$?; n=$(printf '%s' "$q" | grep -c .)
echo "P1b squeue_rc $rc squeue_me_jobs $n"
[ "$rc" -eq 0 ] && [ "$n" -eq 0 ] || { printf '%s\n' "$q" | sed 's/^/  job| /'; rollback; stop 27 "a job appeared, or squeue failed"; }

# ---- W4: the fast-forward. ----
echo "W4 start $(now)"
G merge --ff-only --no-stat "$NEW"; rc=$?; echo "W4 merge_rc $rc end $(now)"
if [ "$rc" -ne 0 ]; then
  echo "W4 head_after_failed_merge $(G rev-parse HEAD)"; rollback; stop 28 "git merge --ff-only failed"
fi

# ---- Post-check. ----
h2=$(G rev-parse HEAD); echo "C1 head $h2"; echo "C1 branch $(G symbolic-ref -q --short HEAD || echo DETACHED)"
POST_FAIL=0
[ "$h2" = "$NEW" ] && echo "C1 head_equals_fetched_main YES" || { echo "C1 head_equals_fetched_main NO"; POST_FAIL=1; }
t=$(tracked); echo "C2 tracked_changes $(printf '%s' "$t" | grep -c .)"; printf '%s' "$t" | sed 's/^/  tracked| /'; [ -z "$t" ] || POST_FAIL=1
U1=$(untracked_count); echo "C3 untracked_after $U1 before $U0"
[ "$U1" -le "$U0" ] && echo "C3 untracked_not_grown YES" || { echo "C3 untracked_not_grown NO"; POST_FAIL=1; }
(cd "$A" && sha256sum -c SHA256SUMS | sed 's/^/  aside_check| /')
(cd "$U" && sha256sum -c SHA256SUMS | sed 's/^/  moved_check| /')
# The four are now tracked, recreated by the merge with the bytes of the copies moved aside.
for p in $FOUR; do
  a=$(cd "$U" && sha256sum "$p" | awk '{print $1}'); b=$(cd "$R" && sha256sum "$p" 2>/dev/null | awk '{print $1}')
  l=$(G ls-files -- "$p")
  if [ "$a" = "$b" ] && [ "$l" = "$p" ]; then echo "C5 $p tracked_and_equal YES"; else echo "C5 $p tracked_and_equal NO"; POST_FAIL=1; fi
done

# What now loads new code from this tree.
echo "C4 changed_paths A $(G diff --name-only --diff-filter=A "$OLD" "$NEW" | grep -c .) M $(G diff --name-only --diff-filter=M "$OLD" "$NEW" | grep -c .) D $(G diff --name-only --diff-filter=D "$OLD" "$NEW" | grep -c .)"
echo "C4 nd_unfolding_sh_naming_tree old $(G grep -l -F "$LAUNCHER_PATH" "$OLD" -- 'nd-unfolding/*.sh' | grep -c .) new $(G grep -l -F "$LAUNCHER_PATH" "$NEW" -- 'nd-unfolding/*.sh' | grep -c .)"
echo "C4 sh_py_naming_tree new $(G grep -l -F "$LAUNCHER_PATH" "$NEW" -- '*.sh' '*.py' | grep -c .)"
for p in 2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py 2d-unfolding/unfold_2d_omnifold_unbinned.py \
         unbinned_unfolding/python/omnifold.py; do
  echo "C4 blob $p old $(G rev-parse -q --verify "$OLD:$p" || echo absent) new $(G rev-parse -q --verify "$NEW:$p" || echo absent)"
done
echo "date_utc_end $(now)"
# A failed post-check is reported, not undone: the tree has moved, and what happens next is the director's call.
[ "$POST_FAIL" -eq 0 ] || { echo "POST-CHECK FAILED"; exit 30; }
echo "DONE"
