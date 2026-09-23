#!/bin/bash
# The seven gates named in REPORT-20260922-review-residue.md section 5, run as one command.
#
# WHY THIS FILE IS TRACKED. From 8f24302f onward this lane's commits say they were "chained behind all
# seven gates with &&". The runner they were chained behind lived in the untracked session scratchpad,
# which independent reviewers share -- and on 2026-09-22 a reviewer's own script overwrote it under the
# same name. That script ignored its arguments and exited 0 unconditionally, so a commit chained behind
# it would have claimed seven green gates that never ran; the reviewer killed it in time (review #12b).
# A claim that cites an untracked, overwritable file maps to no object. This one is tracked.
#
# Usage: probe-20260922-seven-gates.sh        (takes NO arguments)
# Exit 0 only if every gate exits 0. Refuses (exit 2) off `main`, or if given any argument.
# ⚠ IT CHOOSES ITS OWN OPERAND: every TRACKED .md file that differs from HEAD in the index or the working
# tree. In this SHARED checkout that includes another session's uncommitted edits, so the gate can fail on
# a file this commit does not touch (it fails closed). An UNTRACKED new file is not included until it is
# staged, so `git add` a new file before running this (review #14b). An earlier version took the file list
# from its caller and checked only that each was a file, so any file (AGENTS.md, a file outside the
# repo) satisfied it while the default-mode gate was red (review #13b).
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "  *** not in a git work tree"; exit 2; }
[ "$(git branch --show-current)" = "main" ] || { echo "  *** not on main -- refusing"; exit 2; }
[ $# -eq 0 ] || { echo "  *** takes no arguments: it chooses its own operand -- refusing"; exit 2; }
MD=()
while IFS= read -r -d '' f; do [ -f "$f" ] && MD+=("$f"); done < <( { git diff --name-only -z HEAD -- '*.md'; git diff --name-only -z --cached HEAD -- '*.md'; } | sort -zu )
echo "  table gate operand: ${#MD[@]} .md file(s) differing from HEAD"
rc_all=0
run(){ python3 "$@" > /dev/null 2>&1; rc=$?; printf "  exit=%s :: %s\n" "$rc" "$*" | cut -c1-110; [ $rc -ne 0 ] && rc_all=1; }
run docs/orchestration/generate_manifest.py --check --committed-only
run docs/orchestration/control_plane_lint.py
run docs/analysis-note/check_dead_containment.py --source-only
run docs/orchestration/probes/probe-20260922-ledger-reconciles.py
run docs/orchestration/probes/probe-20260922-ledger-guard-mutations.py --regressions
run docs/orchestration/probes/probe-20260922-render-checks.py
run docs/orchestration/probes/probe-20260922-gfm-table-integrity.py --self-test   # gate 7, part 1: the probe still works
if [ ${#MD[@]} -gt 0 ]; then run docs/orchestration/probes/probe-20260922-gfm-table-integrity.py "${MD[@]}"
else echo "  exit=0 :: gfm-table-integrity -- no .md file differs from HEAD, nothing to check"; fi
[ $rc_all -eq 0 ] && echo "  ALL SEVEN GREEN" || echo "  *** A GATE IS RED -- DO NOT COMMIT ***"
exit $rc_all
