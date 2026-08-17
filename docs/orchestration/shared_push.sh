#!/usr/bin/env bash
# Push from a checkout a PEER IS WORKING IN, without disturbing their working tree.
#
# THE HAZARD, measured 2026-08-16 in the main checkout. `origin/main` had moved, so the push needed a
# rebase -- and `git pull --rebase` (or `--autostash`) stashes the OTHER lane's uncommitted edits out
# from under it. That night the foreign dirty set was four files on the 20-path standard-P4 execution
# surface plus a new test, belonging to a lane that was mid-run. Stashing them even briefly can make a
# running process read HEAD's version of a file its author has edited, and a conflict on restore leaves
# someone else's work in a stash they did not create.
#
# CONVENTION-lane-worktrees.md already covers COMMIT-time absorption (pathspec commits sweeping a
# peer's edits to the same file). This is the PUSH-time sibling and it is not the same window: nothing
# you stage or name protects you here, because the operation that hurts is the one that rewrites the
# working tree.
#
# WHAT THIS DOES: if a rebase is needed, it cherry-picks your commits into a THROWAWAY DETACHED
# WORKTREE at origin/<branch>, pushes from there, and removes it. Your local branch is deliberately
# left BEHIND origin -- resetting it would touch the shared tree, which is the thing being avoided.
# The foreign dirty set is digested before and after, and a difference is a REFUSAL, so "I did not
# disturb anything" is a measurement rather than a claim (the discipline this lane demanded of a peer
# on the same night: read-only made falsifiable, not asserted).
#
# Exit codes are the contract. This script is their only interpreter; do not restate them in prose
# (BEN-163 -- the hole moved from merge_guard.sh into the document describing it).
#
#   0  PUSHED        your commits are on the remote, and the foreign dirty set is byte-identical
#   1  REFUSED       nothing pushed: cherry-pick conflicted, or the foreign dirty set CHANGED
#   2  CANNOT CHECK  nothing was examined, so nothing was verified. NOT a pass
#   3  BLOCKED       bad usage, not a git repo, or the self-test failed
#
set -u
BRANCH="${1:-main}"
REMOTE="${2:-origin}"

say() { printf '%s\n' "$*"; }
die() { say "BLOCKED :: $*"; exit 3; }

# --- the instrument: a digest of every dirty (unstaged/untracked) path and its CONTENT -------------
# Paths alone are not enough. A peer editing a file it had already edited changes content and not the
# path list, and that is exactly the case a path-only check would call clean.
dirty_digest() {
    local root="$1" out="" f
    ( cd "$root" 2>/dev/null || return 1
      git status --porcelain -z 2>/dev/null | tr '\0' '\n' | while IFS= read -r line; do
          [ -n "$line" ] || continue
          f="${line:3}"
          if [ -f "$f" ]; then
              printf '%s %s\n' "${line:0:2}" "$(shasum -a 256 "$f" 2>/dev/null | cut -d' ' -f1)"
          else
              printf '%s %s DIR-OR-GONE\n' "${line:0:2}" "$f"
          fi
      done | LC_ALL=C sort
    )
}

# --- SELF-TEST: the comparator must be shown able to report DIFFERENT, in this run ------------------
# BEN-344's rule applied to this script's own instrument: a null result ("nothing changed") is worth
# nothing unless the same instrument, in the same run, is shown capable of returning non-null. Run on
# a scratch repo, never on the caller's tree.
self_test() {
    local t; t="$(mktemp -d)" || return 1
    ( cd "$t" && git init -q . && git config user.email t@t && git config user.name t \
      && echo base > tracked.txt && git add tracked.txt && git commit -qm base ) || { rm -rf "$t"; return 1; }
    local clean dirty1 dirty2
    clean="$(dirty_digest "$t")"
    [ -z "$clean" ] || { rm -rf "$t"; say "self-test: a clean tree did not digest empty"; return 1; }
    echo modified > "$t/tracked.txt"
    dirty1="$(dirty_digest "$t")"
    [ -n "$dirty1" ] || { rm -rf "$t"; say "self-test: a MODIFIED file was not detected"; return 1; }
    echo modified-differently > "$t/tracked.txt"
    dirty2="$(dirty_digest "$t")"
    [ "$dirty1" != "$dirty2" ] || { rm -rf "$t"
        say "self-test: two DIFFERENT contents digested identically -- the comparator is path-only"
        return 1; }
    echo new > "$t/untracked.txt"
    [ "$(dirty_digest "$t")" != "$dirty2" ] || { rm -rf "$t"
        say "self-test: an UNTRACKED file was not detected"; return 1; }
    rm -rf "$t"
    return 0
}

git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository"
ROOT="$(git rev-parse --show-toplevel)" || die "cannot find the worktree root"
case "$BRANCH" in -*|"") die "usage: shared_push.sh [branch] [remote]";; esac

self_test || die "self-test failed -- the instrument is not trustworthy, so nothing was attempted"
say "self-test :: PASS (comparator detects modified, re-modified, and untracked)"

git fetch -q "$REMOTE" "$BRANCH" || { say "CANNOT CHECK :: fetch failed"; exit 2; }
HEAD_SHA="$(git rev-parse HEAD)" || { say "CANNOT CHECK :: no HEAD"; exit 2; }
REM_SHA="$(git rev-parse "$REMOTE/$BRANCH")" || { say "CANNOT CHECK :: no $REMOTE/$BRANCH"; exit 2; }

if [ "$HEAD_SHA" = "$REM_SHA" ]; then say "nothing to push (HEAD == $REMOTE/$BRANCH)"; exit 0; fi
N_AHEAD="$(git rev-list --count "$REM_SHA..$HEAD_SHA")"
[ "$N_AHEAD" -gt 0 ] || { say "CANNOT CHECK :: HEAD is not ahead of $REMOTE/$BRANCH; nothing to push"; exit 2; }

BEFORE="$(dirty_digest "$ROOT")"
say "foreign/local dirty entries before: $(printf '%s' "$BEFORE" | grep -c . || true)"

verify_untouched() {
    local after; after="$(dirty_digest "$ROOT")"
    if [ "$after" != "$BEFORE" ]; then
        say "REFUSED :: the working tree's dirty set CHANGED during this operation."
        say "  This script exists to make that impossible; investigate before doing anything else."
        diff <(printf '%s\n' "$BEFORE") <(printf '%s\n' "$after") | sed 's/^/    /' || true
        return 1
    fi
    say "dirty set byte-identical before and after :: verified, not asserted"
    return 0
}

if git merge-base --is-ancestor "$REM_SHA" "$HEAD_SHA"; then
    say "fast-forward available; pushing directly ($N_AHEAD commit(s))"
    if git push -q "$REMOTE" "HEAD:$BRANCH"; then
        verify_untouched || exit 1
        say "PUSHED :: $(git rev-parse --short HEAD) -> $REMOTE/$BRANCH"; exit 0
    fi
    verify_untouched || exit 1
    say "REFUSED :: push rejected"; exit 1
fi

# Diverged. Do NOT rebase in this tree -- that is the whole point of this script.
say "DIVERGED from $REMOTE/$BRANCH; using a throwaway detached worktree (this tree is not modified)"
WT="$(mktemp -d)/wt"
cleanup() { git worktree remove --force "$WT" >/dev/null 2>&1 || true; git worktree prune >/dev/null 2>&1 || true; }
trap cleanup EXIT
git worktree add --detach -q "$WT" "$REM_SHA" || { say "CANNOT CHECK :: could not create the worktree"; exit 2; }
if ! git -C "$WT" cherry-pick "$REM_SHA..$HEAD_SHA" >/dev/null 2>&1; then
    git -C "$WT" cherry-pick --abort >/dev/null 2>&1 || true
    cleanup; trap - EXIT
    verify_untouched || exit 1
    say "REFUSED :: cherry-pick conflicted onto $REMOTE/$BRANCH. Resolve deliberately;"
    say "  run docs/orchestration/merge_guard.sh <lane> before touching a contested row."
    exit 1
fi
NEW="$(git -C "$WT" rev-parse --short HEAD)"
if ! git -C "$WT" push -q "$REMOTE" "HEAD:$BRANCH"; then
    cleanup; trap - EXIT
    verify_untouched || exit 1
    say "REFUSED :: push rejected (the remote moved again). Re-run."; exit 1
fi
cleanup; trap - EXIT
verify_untouched || exit 1
say "PUSHED :: $N_AHEAD commit(s) as $NEW -> $REMOTE/$BRANCH"
say "NOTE :: your local $BRANCH is intentionally BEHIND $REMOTE/$BRANCH."
say "  Resetting it would write the shared tree, which is what this script avoids."
say "  A stale local HEAD is not a lost push -- confirm with: git branch -r --contains $NEW"
exit 0
