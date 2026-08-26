# TESTED-SHA AND ENVIRONMENT ANCHORING
Recorded by claude-school-main (the AUTHOR of the graded commits), NOT by the grader.
Reason: the grader did not self-report tested shas, and the running window cannot be
instructed mid-flight without interrupting it (its role lock is held by the active send).
This anchors each arm log to the exact tree it was produced from. It is provenance only --
it is NOT a verdict and it grades nothing.

recorded_utc: 2026-08-26T21:56:36Z
grader: agy-g2-gate-verifier  conversation dc93a0f8-6863-48c8-9b7b-76f22f6deae2

| worktree | log prefix | tested sha (verified now) | detached | porcelain |
|---|---|---|---|---|
| `base` | `base_*` | `3ae656951734bc90371bd64c56ccc4ce970b1470` | HEAD | 0 |
| `merge` | `merge_*` | `1aa055d9cd40964cff3b3d0d63ea616d26d5f515` | HEAD | 0 |
| `pin` | `pin_*` | `57508b319a184cd968b191448aeaafb1bd8ed4b7` | HEAD | 3 |
| `probe` | `probe_*` | `d0decbd35b0c4986dc31286a221220d3a29555d1` | HEAD | 2 |

NOTE on porcelain: `pin` and `probe` carry the grader's own UNTRACKED scratch harness
(test_ratchet.py, tmp_inv/, tmp_pins.json). Zero TRACKED files are modified in any worktree.

## Environment required and verified for every arm
PATH prefix : /global/u2/j/josephrb/.conda/envs/root_6_28/bin
python3     : /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
version     : Python 3.11.14
TMPDIR      : /tmp/grade-stack-20260826/tmp

## Reachability at the time of this record
- `base` nd-unfolding: PRESENT 217540 B Ran 1646 tests FAILED (failures=8, errors=18, skipped=11)
- `merge` nd-unfolding: PRESENT 30664 B
- `pin` nd-unfolding: NOT REACHED
- `probe` nd-unfolding: NOT REACHED
