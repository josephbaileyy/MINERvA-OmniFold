#!/bin/bash
# OI-74: fast-forward the canonical cluster checkout to github/main, under DECLARATION.md in this directory.
# Run once, from the local side, as:  ssh saul.nersc.gov 'bash -s' < ff.sh
# Every STOP exits non-zero with its own code. Nothing in the tree is written before W1; every STOP after W2
# restores the two live-state files from the aside copies and re-verifies them.
set -u

R=/pscratch/sd/j/josephrb/MINERvA-OmniFold
A=/pscratch/sd/j/josephrb/oi74-ff-20261030
OLD=32e403b84e9e8f9d9bc435028749f896653c7a43
F1=docs/orchestration/LIVE-STATE.md
F2=docs/orchestration/state/live-state-last-known.json
LAUNCHER_PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export GIT_OPTIONAL_LOCKS=0

# No hooks, no automatic gc or maintenance, for every git call against the tree.
G() { git -C "$R" -c core.hooksPath=/dev/null -c gc.auto=0 -c maintenance.auto=false "$@"; }
now() { date -u +%FT%TZ; }
stop() { echo "STOP $1: $2"; echo "date_utc_end $(now)"; exit "$1"; }
tracked() { G status --porcelain --untracked-files=no; }
untracked_count() { G status --porcelain | grep -c '^??'; }
EXPECTED_TRACKED=$(printf ' M %s\n M %s' "$F1" "$F2")

rollback() {
  echo "ROLLBACK: restoring the two live-state files from $A"
  cp -p "$A/LIVE-STATE.md" "$R/$F1" && cp -p "$A/live-state-last-known.json" "$R/$F2"
  echo "rollback_cp_rc $?"
  (cd "$A" && sha256sum LIVE-STATE.md live-state-last-known.json)
  (cd "$R" && sha256sum "$F1" "$F2")
  t=$(tracked); echo "rollback_head $(G rev-parse HEAD)"
  if [ "$t" = "$EXPECTED_TRACKED" ]; then echo "rollback_tracked OK (the two files, as before)"; else
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

[ ! -e "$A" ] || stop 16 "the aside directory $A already exists"

# ---- W1: copy the two files aside, with their sha256. ----
mkdir "$A" && cp -p "$R/$F1" "$A/LIVE-STATE.md" && cp -p "$R/$F2" "$A/live-state-last-known.json" \
  || stop 20 "copy aside failed; the tree is unchanged"
(cd "$A" && sha256sum LIVE-STATE.md live-state-last-known.json > SHA256SUMS)
echo "W1 aside $A"; sed 's/^/  aside| /' "$A/SHA256SUMS"
s1=$(cd "$R" && sha256sum "$F1" "$F2" | awk '{print $1}'); s2=$(awk '{print $1}' "$A/SHA256SUMS")
[ "$s1" = "$s2" ] || stop 21 "aside copies do not match the originals; the tree is unchanged"

# ---- W2: restore the two files to HEAD. ----
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
# A path the merge ADDS that already exists in the tree: git refuses if it is untracked and not ignored,
# and silently overwrites it if it is ignored. Either one that is not byte-identical to NEW's blob is a STOP.
present=0; identical=0; differ=0; blocking=0
while IFS= read -r -d '' p; do
  if [ -e "$R/$p" ] || [ -L "$R/$p" ]; then
    present=$((present + 1))
    want=$(G rev-parse "$NEW:$p"); have=$(G hash-object -- "$p" 2>/dev/null || echo unreadable)
    if [ "$want" = "$have" ]; then identical=$((identical + 1)); else
      differ=$((differ + 1)); [ "$differ" -le 20 ] && echo "  differs| $p"; fi
    if ! G check-ignore -q -- "$p"; then blocking=$((blocking + 1)); [ "$blocking" -le 20 ] && echo "  untracked-not-ignored| $p"; fi
  fi
done < <(G diff --name-only -z --diff-filter=A "$OLD" "$NEW")
echo "P5 added $(G diff --name-only --diff-filter=A "$OLD" "$NEW" | grep -c .) present $present identical $identical differ $differ untracked_not_ignored $blocking"
[ "$differ" -eq 0 ] || { rollback; stop 25 "$differ added path(s) exist in the tree with different bytes"; }
[ "$blocking" -eq 0 ] || { rollback; stop 26 "$blocking added path(s) exist as untracked, not-ignored files"; }

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
