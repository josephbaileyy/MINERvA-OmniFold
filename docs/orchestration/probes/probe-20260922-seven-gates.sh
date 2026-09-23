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
# Usage: probe-20260922-seven-gates.sh FILE...   (the .md files the commit edits, for the table probe)
# Exit 0 only if every gate exits 0. Refuses (exit 2) off `main`, or when given no files.
# Call it with a real argument list: in zsh, `$F` holding several paths is ONE argument unless split.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "  *** not in a git work tree"; exit 2; }
[ "$(git branch --show-current)" = "main" ] || { echo "  *** not on main -- refusing"; exit 2; }
[ $# -gt 0 ] || { echo "  *** no files given for the table probe -- refusing"; exit 2; }
for f in "$@"; do [ -f "$f" ] || { echo "  *** not a file: '$f' -- refusing"; exit 2; }; done
rc_all=0
run(){ python3 "$@" > /dev/null 2>&1; rc=$?; printf "  exit=%s :: %s\n" "$rc" "$*" | cut -c1-110; [ $rc -ne 0 ] && rc_all=1; }
run docs/orchestration/generate_manifest.py --check --committed-only
run docs/orchestration/control_plane_lint.py
run docs/analysis-note/check_dead_containment.py --source-only
run docs/orchestration/probes/probe-20260922-ledger-reconciles.py
run docs/orchestration/probes/probe-20260922-ledger-guard-mutations.py --regressions
run docs/orchestration/probes/probe-20260922-render-checks.py
run docs/orchestration/probes/probe-20260922-gfm-table-integrity.py "$@"
[ $rc_all -eq 0 ] && echo "  ALL SEVEN GREEN" || echo "  *** A GATE IS RED -- DO NOT COMMIT ***"
exit $rc_all
