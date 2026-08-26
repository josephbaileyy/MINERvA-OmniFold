grader role       : agy-capacity-probe
conversation uuid : dc2b899d-a8b0-40a4-aa8d-707c49b391a3
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/grade-stack-20260826/tmp
$ command -v python3
/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
$ python3 -V
Python 3.11.14

### TREES
BEFORE /tmp/grade-stack-20260826/base
  SHA: 3ae656951734bc90371bd64c56ccc4ce970b1470
  HEAD is DETACHED: YES
  porcelain count: 0
AFTER /tmp/grade-stack-20260826/merge
  SHA: 1aa055d9cd40964cff3b3d0d63ea616d26d5f515
  HEAD is DETACHED: YES
  porcelain count: 0

### ITEM P6
BASE tree (3ae656951734bc90371bd64c56ccc4ce970b1470):
  len(KNOWN_UNREPAIRED): 52
  scanner finds count: 52
  STALE count: 0
  NEW count: 0

MERGE tree (1aa055d9cd40964cff3b3d0d63ea616d26d5f515):
  len(KNOWN_UNREPAIRED): 46
  scanner finds count: 46
  STALE count: 0
  NEW count: 0

Verdict: REFUTED. The claim that there are 6 STALE entries at base is incorrect. In BASE, 52 are listed and 52 are found (STALE 0, NEW 0). In MERGE, 46 are listed and 46 are found (STALE 0, NEW 0). The 6 items removed from KNOWN_UNREPAIRED in merge are:
  - nd-unfolding/bootstrap_nd.py
  - nd-unfolding/seedscan_split.py
  - nd-unfolding/sweep_bank_5d.py
  - nd-unfolding/unfold_nd_omnifold_unbinned.py
  - nd-unfolding/unified_throw_cov.py
  - nd-unfolding/unified_throw_cov_5d.py

### ITEM P7
BASE tree (3ae656951734bc90371bd64c56ccc4ce970b1470):
  total LINES: 98
  BODY ROWS: 97
  DISTINCT first-column paths: 97

MERGE tree (1aa055d9cd40964cff3b3d0d63ea616d26d5f515):
  total LINES: 102
  BODY ROWS: 101
  DISTINCT first-column paths: 101

Verdict: No unit makes them consistent with '104 -> 101 BODY ROWS'. The earlier grader's '98 / 102' matches total LINES, but the direction is an increase (98 -> 102), directly contradicting a decrease (104 -> 101). Furthermore, there are no duplicate first-column paths remaining in either tree.

### REACHABILITY
Completed items: P6, P7.
Unreached items: None.
