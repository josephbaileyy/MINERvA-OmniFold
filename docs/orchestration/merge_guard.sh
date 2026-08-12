#!/bin/bash
# Merge gate for a lane worktree: refuse a merge that resolves another lane's ledger row.
#
# WHY THIS FILE EXISTS, and it is not a convenience wrapper.
# BEN-163. `whose_row.py` grew from one exit code to three (0 pass / 1 refused / 2 cannot-check) across
# seven return sites, and `CONVENTION-lane-worktrees.md` went on saying `# exit 1 if a contested row is
# not yours` and `# 42 checks` against a suite that runs 58. That document is the only place an operator
# learns the contract -- and BEN-117's own text says the empty-`--lane` case "is how any wrapper or hook
# will invoke this", so THE READER MOST LIKELY TO WRITE THAT WRAPPER WAS READING THE LINE THAT OMITS
# EXIT 2. A wrapper written faithfully from the convention tests `[ $? -eq 1 ]`, and exit 2 -- the code
# added precisely because a misconfigured caller had been told it passed -- reads as success. The hole
# was not closed; it moved from the script to the prose describing the script, which is worse, because
# the script has a self-test and the prose has none.
#
# So the convention now cites this PATH instead of quoting a command. This file cannot drift from the
# exit codes because it IS their only interpreter. Same remedy, same reason, as
# `waker_fired_but_unread.sh` (BEN-097): a remedy of the form "write it down and read it" must be assumed
# to fail. BEN-084(B) is the precedent that settles it -- a literal command in a header, annotated with
# its own failure mode, was re-derived wrongly anyway.
#
# FOURTH INSTANCE of Session D's rule, and the first where it crosses artifacts:
#   `lane_matches` rebuilt, `conflicted_line_numbers` not          (BEN-162)
#   predicate tested, call path not                                (BEN-117)
#   code fixed, published contract not                             (BEN-163, this)
# Every repair correct, complete, and bounded to the exact object that had failed.
#
# Usage, from inside your lane worktree:
#     bash docs/orchestration/merge_guard.sh <LANE>       e.g. B | C | D | A
#
# Run it BEFORE resolving any conflict. Exit 0 means you may resolve; anything else means stop.

set -uo pipefail
cd "$(dirname "$0")/../.." || exit 3

LANE="${1:-${MNV_LANE:-}}"
if [[ -z "$LANE" ]]; then
  echo "  FAIL no lane given. Usage: bash docs/orchestration/merge_guard.sh <LANE>"
  echo "       An empty lane is fatal by design (BEN-117): '--lane \"\$LANE\"' with LANE unset used to"
  echo "       print every foreign row as OTHER and exit 0."
  exit 3
fi

GATE=docs/orchestration/whose_row.py

# The gate's own power test runs FIRST, so a broken gate fails the merge rather than passing everything.
# Same ordering as build_all.sh running check_dead_containment.py --self-test before the check itself.
# The suite prints its own check count; this file deliberately does NOT restate it, because a number in
# prose beside a suite that reports its own total is a second copy that can only drift -- which is the
# defect this file exists to close.
if ! python3 "$GATE" --self-test; then
  echo
  echo "  BLOCKED :: the attribution gate's own self-test FAILS. Nothing it says about ownership can be"
  echo "             trusted, so this is not a merge you may resolve. Fix the gate first."
  exit 3
fi

echo
python3 "$GATE" --conflicts --lane "$LANE"
rc=$?

echo
case "$rc" in
  0) echo "  PASS :: every contested ledger row is yours. You may resolve this merge." ;;
  1) echo "  REFUSED :: a contested row belongs to another lane. ROUTE IT TO THE NAMED AUTHOR AND DO"
     echo "             NOT RESOLVE IT. Joseph's rule, 2026-08-12: no lane's ledger row is merged by"
     echo "             anyone but its author." ;;
  2) echo "  CANNOT CHECK :: the gate examined nothing, so nothing was verified. This is NOT a pass."
     echo "             Either there is no conflict to attribute -- in which case you are gating an"
     echo "             empty set and the merge auto-resolved, which is fine but unverified -- or the"
     echo "             lane argument was empty, or git could not enumerate unmerged files."
     echo "             A conflict in VALIDATION_LEDGER.md also lands here: it has no per-row id"
     echo "             scheme and CANNOT be attributed, and it is the file with the second-most"
     echo "             absorptions. Route those by hand." ;;
  *) echo "  BLOCKED :: unexpected exit $rc from the gate. Treat as a refusal." ;;
esac

# Exit codes are passed through unchanged, so a caller reading THIS file's status sees the gate's own
# verdict. Do not collapse 2 into 0: that collapse is the entire defect BEN-163 records.
exit "$rc"
