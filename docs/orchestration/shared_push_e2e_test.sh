#!/usr/bin/env bash
# END-TO-END test for shared_push.sh, against a REAL remote on scratch repos.
#
#     bash docs/orchestration/shared_push_e2e_test.sh
#
# Why an end-to-end suite and not only the script's internal self-test: that self-test proves the
# COMPARATOR can see a change, which is necessary and not sufficient. The thing being claimed is about
# `git push` and `git worktree` behaviour under divergence, and CONVENTION-lane-worktrees.md records
# that the one false pass in `merge_guard.sh` was caught by "an end-to-end merge between two real
# worktrees, not by the self-test -- whose single negative control happened to be a case where the bug
# does not fire." Same lesson, applied on the way in rather than after.
#
# Every test asserts the property the script exists for -- A PEER'S UNCOMMITTED WORK IS BYTE-IDENTICAL
# AFTERWARDS -- and not merely that the push succeeded. Touches nothing outside its own mktemp dir.
#
#   exit 0  all pass          exit 1  a test failed          exit 3  cannot set up
set -u
S="$(cd "$(dirname "$0")" && pwd)/shared_push.sh"
[ -r "$S" ] || { echo "BLOCKED :: cannot read $S"; exit 3; }
T="$(mktemp -d)" || exit 3
trap 'rm -rf "$T"' EXIT
fail=0
chk() { [ "$2" = "$3" ] && echo "  PASS  $1" || { echo "  FAIL  $1 (got '$2' want '$3')"; fail=1; }; }

# A shared checkout diverged from origin, with a PEER's uncommitted edits present:
# one modification to a file the peer's own upstream commit also touched (the case an autostash
# pull corrupts), plus one untracked file.
setup() {
    # cd OUT of the tree first: removing the directory you are standing in leaves the shell with no
    # valid cwd, and git then prints "fatal: this operation must be run in a work tree" while every
    # assertion still passes. A suite that emits alarming errors on a green run teaches its reader to
    # skim the output, which is the state this repo's logs are supposed to be rescued from.
    cd "$T" || return 1
    rm -rf "$T/r" "$T/w" "$T/p"
    git init -q --bare "$T/r"
    git clone -q "$T/r" "$T/w" 2>/dev/null
    ( cd "$T/w" && git config user.email a@a && git config user.name a \
      && echo base > f.txt && git add f.txt && git commit -qm base \
      && git push -q origin HEAD:main && git branch -q -M main ) || return 1
    git clone -q "$T/r" "$T/p"
    ( cd "$T/p" && git config user.email b@b && git config user.name b \
      && echo peer >> f.txt && git commit -qam "peer commit" && git push -q origin HEAD:main ) || return 1
    ( cd "$T/w" && echo mine > mine.txt && git add mine.txt && git commit -qm "my commit" \
      && echo "PEER IN-FLIGHT EDIT" > f.txt && echo "peer new file" > peer_untracked.py ) || return 1
}
dig() { shasum -a 256 "$1" | cut -d' ' -f1; }

echo "TEST 0 -- the HAZARD is real: an autostash pull alters the peer's in-flight file, returning rc=0"
setup || exit 3
cd "$T/w"
B_F="$(dig f.txt)"
git -c rebase.autoStash=true pull --rebase -q >/dev/null 2>&1
chk "autostash pull reported success" "$?" "0"
[ "$(dig f.txt)" != "$B_F" ] && echo "  PASS  and it ALTERED the peer's file (this is what we prevent)" \
    || { echo "  FAIL  the hazard did not reproduce -- re-derive before trusting this suite"; fail=1; }

echo "TEST 1 -- diverged push leaves the peer's dirty tree byte-identical"
setup || exit 3
cd "$T/w"
B_F="$(dig f.txt)"; B_U="$(dig peer_untracked.py)"
bash "$S" main origin >"$T/o1" 2>&1; chk "exit 0" "$?" "0"
chk "peer MODIFIED file untouched" "$(dig f.txt)" "$B_F"
chk "peer UNTRACKED file untouched" "$(dig peer_untracked.py)" "$B_U"
git fetch -q origin; git cat-file -e origin/main:mine.txt 2>/dev/null
chk "my commit reached the remote" "$?" "0"
chk "no leftover worktree" "$(git worktree list | wc -l | tr -d ' ')" "1"
grep -q "verified, not asserted" "$T/o1"; chk "reported the before/after comparison" "$?" "0"

echo "TEST 2 -- REGRESSION: running it twice. The first push landed under a NEW sha, so the local"
echo "          commit is now upstream BY CONTENT. Without patch-id detection this refuses forever."
bash "$S" main origin >"$T/o2" 2>&1; chk "exit 0, not a conflict refusal" "$?" "0"
grep -q "already upstream BY CONTENT" "$T/o2"; chk "recognised patch-equivalence" "$?" "0"
chk "peer file STILL untouched" "$(dig f.txt)" "$B_F"

echo "TEST 3 -- a genuinely new commit still pushes once a duplicate is present"
echo more > mine2.txt; git add mine2.txt; git commit -qm "my second commit"
bash "$S" main origin >"$T/o3" 2>&1; chk "exit 0" "$?" "0"
git fetch -q origin; git cat-file -e origin/main:mine2.txt 2>/dev/null
chk "the new commit reached the remote" "$?" "0"
grep -q "already upstream by content; skipping" "$T/o3"; chk "skipped the duplicate, kept the new one" "$?" "0"

echo "TEST 4 -- fast-forward path is taken when there is no divergence (no worktree needed)"
rm -rf "$T/r" "$T/w"; git init -q --bare "$T/r"; git clone -q "$T/r" "$T/w" 2>/dev/null
cd "$T/w" && git config user.email a@a && git config user.name a
echo x > a.txt && git add a.txt && git commit -qm x && git push -q origin HEAD:main
git branch -q -M main && git fetch -q origin
echo y > b.txt && git add b.txt && git commit -qm y
bash "$S" main origin >"$T/o4" 2>&1; chk "exit 0" "$?" "0"
grep -q "fast-forward available" "$T/o4"; chk "used the fast-forward path" "$?" "0"

echo
if [ $fail -eq 0 ]; then echo "SUITE :: ALL PASS"; else echo "SUITE :: FAILED"; fi
exit $fail
