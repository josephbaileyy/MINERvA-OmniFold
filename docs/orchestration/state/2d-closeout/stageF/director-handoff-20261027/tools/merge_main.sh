#!/bin/bash
# usage: merge_main.sh <worktree> <remote-branch>; merges origin/main into it, resolves generated files, commits, pushes; prints new head
# Run it in a clean worktree of its own; it works on a detached HEAD and pushes HEAD:<branch>.
set -u
W=$1; B=$2
cd "$W" || exit 3
# Detached, not a named temp branch: a branch name shared by several worktrees moves under the others (2026-10-28).
git fetch -q origin "$B" && git fetch -q origin && git checkout -q --detach "origin/$B" || exit 3
git -c user.name="paper-tighten lane (Claude)" -c user.email="paper-tighten@minerva-omnifold.invalid" merge --no-commit origin/main >/dev/null 2>&1
for f in docs/orchestration/MANIFEST-overrides.tsv docs/orchestration/CATALOG.md; do
  if git diff --name-only --diff-filter=U | grep -qx "$f"; then
    sed -i '' -e '/^<<<<<<< /d' -e '/^=======$/d' -e '/^>>>>>>> /d' "$f"; git add -- "$f"
  fi
done
if git diff --name-only --diff-filter=U | grep -qx docs/orchestration/MANIFEST.tsv; then git checkout --ours docs/orchestration/MANIFEST.tsv; git add -- docs/orchestration/MANIFEST.tsv; fi
# The generated records_*.tex files are regenerated below, so main's copy is a safe start. A conflicted registry TSV is
# NOT: a lane may have re-cited rows that main's copy would silently drop (seen 2026-10-28 on #413). Stop for a hand
# resolution: take the side whose rows are current, then `check_registry.py --repoint` and rerun the steps below.
for f in $(git diff --name-only --diff-filter=U); do case $f in docs/analysis-note/records_*) git checkout --theirs -- "$f" && git add -- "$f";; esac; done
left=$(git diff --name-only --diff-filter=U); if [ -n "$left" ]; then echo "UNRESOLVED: $left"; exit 4; fi
if grep -q -E '^(<<<<<<<|>>>>>>>)' docs/orchestration/CATALOG.md docs/orchestration/MANIFEST-overrides.tsv; then echo "MARKERS LEFT"; exit 4; fi
git add -u -- docs/orchestration/registry >/dev/null 2>&1
python3 tools/registry/check_registry.py --repoint >/dev/null 2>&1; git add -u -- docs/orchestration/registry
python3 tools/registry/results_index.py --write >/dev/null 2>&1; git add -u -- docs/orchestration/registry docs/analysis-note/records_results_index.tex docs/analysis-note/records_estimators.tex; python3 tools/registry/results_index.py --write >/dev/null 2>&1
git add -u -- docs/orchestration/registry docs/analysis-note/records_results_index.tex docs/analysis-note/records_estimators.tex
python3 docs/orchestration/generate_manifest.py >/dev/null && git add -- docs/orchestration/MANIFEST.tsv
bash .githooks/pre-commit > ${TMPDIR:-/tmp}/mm-hook.txt 2>&1; rc=$?; tail -1 ${TMPDIR:-/tmp}/mm-hook.txt; grep FAIL ${TMPDIR:-/tmp}/mm-hook.txt | head -5
[ $rc -eq 0 ] || { echo "HOOK FAILED"; exit 5; }
git -c core.hooksPath=.githooks -c user.name="paper-tighten lane (Claude)" -c user.email="paper-tighten@minerva-omnifold.invalid" commit -q -m "Merge origin/main into $B

Generated files resolved and regenerated.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 6
python3 docs/orchestration/generate_manifest.py --check --at-sha HEAD >/dev/null 2>&1 || { echo "MANIFEST CHECK FAILED"; exit 7; }
git push -q origin "HEAD:$B" 2>&1 | grep -v remote
git rev-parse HEAD
