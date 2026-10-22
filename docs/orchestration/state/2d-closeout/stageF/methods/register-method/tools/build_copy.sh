#!/usr/bin/env bash
# usage: build_copy.sh <name> [worktree]   -- builds all four PDFs from the worktree's docs/analysis-note in a scratch copy
set -u
S=${SCRATCH:?set SCRATCH to a scratch directory}   # builds go to $SCRATCH/plain-language/builds/<name>
WT=${2:-$S/wt-plain}
B=$S/plain-language/builds/$1
rm -rf "$B"; mkdir -p "$B/repo/docs/orchestration"
rsync -a --exclude archive/ "$WT/docs/analysis-note/" "$B/repo/docs/analysis-note/"
ln -s "$WT/docs/orchestration/state" "$B/repo/docs/orchestration/state"
cd "$B/repo/docs/analysis-note" && bash build_all.sh > "$B/build.log" 2>&1
rc=$?
echo "build_all rc=$rc  log=$B/build.log"
grep -E 'written by this run|PASS|FAIL|undefined|rror' "$B/build.log" | tail -20
for p in main_note main_paper main_primer pet_note main_records; do printf '%s pages=%s\n' $p "$(pdfinfo $p.pdf 2>/dev/null | awk '/^Pages/{print $2}')"; done
exit $rc
