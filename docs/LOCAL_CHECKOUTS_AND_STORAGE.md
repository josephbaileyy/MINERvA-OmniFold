# Local checkouts, scratch and out-of-repo archives

**CITABLE FOR:** where local copies of this repository and its out-of-repo archives live, the rules for
removing a local checkout or scratch directory, and the recovery route for anything already removed.
**NOT CITABLE FOR:** any scientific result, cluster state, or authorization. Re-measure before acting;
paths and sizes below are dated observations.

This file covers machine-local state. The tracked tree's own removals (families A2, A3) are in
`docs/POST_PUBLICATION_REORG_PLAN.md`.

## Where things live (Joseph's laptop)

| path under `/Users/josephbailey/local-research/` | what it is |
|---|---|
| `MINERvA-OmniFold/` | the shared primary checkout. Several Claude and Codex sessions run here at once, so its `main` can lag `origin/main`. Its `.githooks` dispatcher serves every linked worktree (`core.hooksPath` is absolute). |
| `MINERvA-OmniFold-<topic>/` | linked worktrees, one per lane or review |
| `MINERvA-OmniFold/.claude/worktrees/agent-*` | worktrees created by the Claude harness for subagents |
| `/private/tmp/minerva-*` | short-lived review and documentation worktrees. macOS may clear `/private/tmp`, so nothing unique should live there. |
| `MINERvA-OmniFold-Analysis-Note/` | checkout of the standalone note repository (see `AGENTS.md`, deliverable synchronization) |
| `minerva-ml-gregor-audit/`, `gregor-audit/` | read-only clones of Gregor Krzmanc's `minerva-ml` and the two audit write-ups |
| `evidence-epochs/<epoch>/` | out-of-repo preservation archives (next section); immutable, never cleanup targets |

On NERSC the epoch mirrors are under `/global/homes/j/josephrb/evidence/repository-epochs/`. Cluster
checkouts and frozen run worktrees on `/pscratch` are governed by their own run records, not this file.

## Out-of-repo evidence epochs

| epoch | NERSC mirror | what it preserves | read first |
|---|---|---|---|
| `prepublication-2026-08-20-0b329e8a` | yes | the pre-compaction tree: all-ref bundle, inventories, recovery proofs for tag `evidence/prepublication-2026-08-20-0b329e8a` | its `RECOVERY.md`; `docs/POST_PUBLICATION_REORG_PLAN.md` |
| `preparation-2026-09-24-bf34a12c` | yes | the preparation-pass boundary for tag `evidence/preparation-2026-09-24-bf34a12c` (A2's removal boundary) | `docs/orchestration/RECOVERY-MANIFEST-20260924-preparation-epoch.md` |
| `housekeeping-20260929` | **no** (local only when checked 2026-10-07) | 23 retired worktrees (`retired-worktrees.jsonl`, `worktree-caches/*.tar.gz`), the primary checkout's untracked root files (`shared-files/`, `main-update.json`), and a pre-cleanup all-ref bundle | `main-update.json`, `retired-worktrees.jsonl` (no README) |
| `simplification-2026-10-07-fc97eaf9` | yes | family A3 (674 PET final-design dev outputs) and an all-ref bundle for tag `evidence/simplification-2026-10-07-fc97eaf9` | its `RECOVERY.md` |
| `housekeeping-20261007` | yes | every unique byte of the 2026-10-07 local cleanup batch (below), with manifests and a byte-level restoration proof | its `RECOVERY.md` |
| `tmpdir-leaks-20261007` | yes | validation logs, measurement tools and a complete-history bundle for PR #48 (test temp-directory leaks), and the pre-removal tree listing of its retired worktree `MINERvA-OmniFold-tmpdir-leaks-20261007` | its `RECOVERY.md` |

## Before removing a local checkout or scratch directory

Age, ignored status and a merged branch are not evidence of disposability. Remove a worktree only when
all of these hold, and record each measurement:

1. `git status --porcelain --untracked-files=all` is empty.
2. After `git fetch --prune origin`, `git rev-list HEAD --not --remotes=origin` is empty, and HEAD is an ancestor
   of a ref inside a stored, checksummed bundle. Local tags and stale remote-tracking refs are not proof.
3. No process has it as cwd (`lsof -d cwd`), and no running session has used it. Liveness is a running
   process: check the Claude Code pid files (`~/.claude*/sessions/<pid>.json`) with `ps -p`. A recent
   transcript write is not proof, because idle sessions also write. Search
   session transcripts (`~/.claude*/projects/**/*.jsonl`, `~/.codex*/sessions/**/*.jsonl`) for `"cwd"`,
   `cd` or `git -C` with the path. A bare mention in `git worktree list`
   output is not a use.
4. Its ignored non-cache files are archived. They are the only bytes Git does not hold.
5. The archive is checksummed, mirrored, and a restoration from it matches the tree's pre-removal manifest.

Then remove it with `git worktree remove <path>`. That deletes neither the branch nor any commit. Do not
use `git gc --prune=now` or `git stash drop` as cleanup: stashes and dangling objects are shared by every
worktree, and a dangling commit can be another session's only copy.

**Test scratch was the largest local consumer.** Until PR #46, `nd-unfolding/tests/test_s5c_coverage.py` left up to
about 1.75 GB of synthetic NPZ per case in `TMPDIR` (twelve leaked cases held 14.1 GB on 2026-10-07). PR #46 and
PR #48 made 18 test files remove their temp directories. Two known leaks remain, both small:
`KNOWN_ISSUES.md` rows 86 (the frozen s5p recovery tests, 4.7 MiB per run) and 87 (`mnv_guarded_run.py`'s
per-process tool directories). Still run suites with `TMPDIR` set to a dated scratch directory, and delete that
directory once the run's logs are copied out.

## Local cleanup records

### 2026-10-07 batch 1 — state: EXECUTED 2026-10-07T23:35Z

Joseph approved it on 2026-10-07. The guarded script removed all 33 items (24 worktrees, eight test
TMPDIRs and `.developer-tooling-backup/`) with 0 refusals, and the measured free space rose by
20,312,960 KiB (19.4 GiB), to 35 GiB (92% used). The scope, preserved bytes, restoration proof and
recovery commands are in `evidence-epochs/housekeeping-20261007/RECOVERY.md` and `inventory.json`. The
per-item log is `execution-log.txt` in the same directory. The archive has local and NERSC copies.

### 2026-10-07 batch 2 — state: EXECUTED 2026-10-07T23:45Z

Batch 1 held back 15 worktrees as in use, because a session transcript using each one had been written in
the last hour. Joseph pointed out that those sessions had stopped, and the Claude Code pid files confirmed
that every one had exited. Joseph approved batch 2 on 2026-10-07.

The guarded script removed 14 worktrees and freed 5,009,088 KiB (4.8 GiB), leaving 40 GiB free. It refused
the 15th, this lane's own `MINERvA-OmniFold-navigation-20261007`, because its HEAD had moved to the
PR #44 branch. That worktree was removed separately once its last commit was on `origin`.

The `scalar-successor` draft commit `eeeaad78` remains on its local branch and in the archive bundle.
Scope, proofs and recovery are in `evidence-epochs/housekeeping-20261007-b/RECOVERY.md` and its `execution-log.txt`.

Together the two batches freed 24.2 GiB. The remaining linked worktrees are the harness worktrees of
running sessions, if any.
