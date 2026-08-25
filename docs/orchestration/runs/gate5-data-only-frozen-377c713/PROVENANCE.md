# `gate5-data-only-frozen-377c713` — surviving artifact of a removed worktree

This directory holds the one **untracked** file that lived in the frozen deployment tree
`/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713`, which was **removed 2026-08-25T03:16:21Z**
under an authorization from Joseph recorded in
`docs/orchestration/state/gate5-do-train-array-active-57266000.json`
(key `REMOVAL_OF_THE_FROZEN_DEPLOYMENT_TREE`).

## Why this file is here and the other 2422 are not

The tree's tracked contents are recoverable from git — it was a worktree at
`377c713d1790d96d15f7d115d9c903fd556c5943`, which is an ancestor of pushed `main`, carrying 2422
tracked entries. **`logs/log_fe_nominal_nominal.txt` was never tracked**, so it was not in that
commit and the sha was not a route to it. Recreating the tree from the sha alone yields something
2422/2422 correct and missing this file.

That gap was found by the lane that performed the removal, and the phrasing worth keeping is:
**a surviving reconstruction route is not a surviving reference.**

## What it is

667 bytes, `md5 9ad538c385e98adfe74114ce305129e0`. Training log for job **57266000**
(`gate5-do-train`, data-only C_stat smoke), which **FAILED**. It is a **forensic witness**: the
message wording in this class of log is what distinguished which code emitted a failure during the
run-3/run-4 diagnosis. It is not a result, not a validation, and asserts nothing about correctness.

## Provenance of this copy

Archived to `$HOME/retired-worktree-archive-20260824/.../untracked/` on `/global/u2` at removal
time by the removing lane, md5-verified against the live tree; committed here after Joseph
authorized it, md5 re-verified on arrival. Until this commit the archive was the **sole** copy and
nothing enforced its retention — see the receipt's
`WHAT_ENFORCES_THE_ARCHIVE_PROTECTION__NOTHING_DOES` block, which this commit partially retires.

## Path convention

Follows `docs/orchestration/runs/clausec-rerun-20260821/`, the one prior instance of a removed
worktree whose artifacts were preserved this way (35 tracked files, including `logs/*.log.txt`).
Measured: of the twelve worktrees removed on 2026-08-24, that was the only one with anything under
`runs/`. **n=1 — a precedent, not established practice.** This `PROVENANCE.md` has no counterpart
there; it is added because a single log file, unlike that directory's 35, does not explain itself.
