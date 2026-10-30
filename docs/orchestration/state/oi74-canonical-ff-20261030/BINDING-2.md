# Binding 2: OI-74, the second fast-forward run (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md` (#558), item 1.

**Binds** [`DECLARATION-2.md`](DECLARATION-2.md), merged in PR #562. Its file sha256 begins `adf0cf7ab77e564a`. The
script is [`ff2.sh`](ff2.sh), sha256 `c0e393b08daaf20738b0657a6acea62083579d67a1f6c28f1f9a3186523fb851`, the same on
`main` after the merge (`8ff3aa40`).

**AUTHORIZES:** exactly one run of `ff2.sh` against `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, by one ssh, with its
transcript in `run2/session.txt`.

**CANNOT AUTHORIZE:**
- a third run, or any repair after a STOP;
- touching any untracked file other than the four the decision names;
- any write outside the tree and its aside directory;
- launching a job;
- writing to CFS.

## 1. What the director checked at the PR head `464f15b8`

- `ff2.sh`'s digest equals the declaration's.
- `test_ff2.sh` gives **16 passed, 0 failed**: 2 good paths, 8 STOPs before any write, and 6 rollbacks. One of them is
  STOP 29: a file changed just before its move stops the run, and the one already moved comes back.
- `ff2.sh` contains no `rm`.

## 2. Rulings

1. **The aside directory is handled as declared.** The new subdirectory must not exist, the first run's three files
   must be present with good sums, and the tree's two live-state files must still equal those copies. Each check is a
   STOP.
2. **The four files:**
   - after the fetch, the untracked, not-ignored added paths must be exactly those four;
   - each is re-hashed against `main`'s blob just before its own move;
   - each moves by `mv -n` and is re-hashed after the move;
   - any STOP after the first write restores all six files.
3. **The untested STOPs** (10, 13, 14, 22, 24, 28 and 31) are accepted as written. Each stops before or instead of a
   write, and the report says which fired, if any.
   <!-- absence-ok: refers to the declaration's own list of STOP paths not exercised by test_ff2.sh; a scoping statement about the test, not a result -->
4. **Post-check C5:** the four are tracked after the merge, with the bytes of their moved copies.

## 3. The report

`REPORT-2.md` gives:
- the transcript;
- HEAD before and after, and the fetched main;
- the tracked count, which must be 0, and the untracked count before and after;
- the aside subdirectory with its SHA256SUMS;
- the A/M/D counts.

It comes as a PR, with OI-74's row updated, and goes to Joseph through the director.

The run may start once this record is on `main`. Tell the director before connecting.
