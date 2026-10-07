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

## Before removing a local checkout or scratch directory

Age, ignored status and a merged branch are not evidence of disposability. Remove a worktree only when
all of these hold, and record each measurement:

1. `git status --porcelain --untracked-files=all` is empty.
2. After `git fetch --prune origin`, `git rev-list HEAD --not --remotes=origin` is empty, and HEAD is an ancestor
   of a ref inside a stored, checksummed bundle. Local tags and stale remote-tracking refs are not proof.
3. No process has it as cwd (`lsof -d cwd`), and no session that is still writing has used it. Search
   session transcripts (`~/.claude*/projects/**/*.jsonl`, `~/.codex*/sessions/**/*.jsonl`) for `"cwd"`,
   `cd` or `git -C` with the path. A bare mention in `git worktree list`
   output is not a use.
4. Its ignored non-cache files are archived. They are the only bytes Git does not hold.
5. The archive is checksummed, mirrored, and a restoration from it matches the tree's pre-removal manifest.

Then remove it with `git worktree remove <path>`. That deletes neither the branch nor any commit. Do not
use `git gc --prune=now` or `git stash drop` as cleanup: stashes and dangling objects are shared by every
worktree, and a dangling commit can be another session's only copy.

**Test scratch is the largest local consumer.** `nd-unfolding/tests/test_s5c_coverage.py` writes up to
about 1.75 GB of synthetic NPZ per case into `TMPDIR` and does not delete it (`test_s5c_meter.py` also
leaks `s5c-meter-*`). Twelve leaked cases held 14.1 GB on 2026-10-07. Run suites with `TMPDIR` set to a dated scratch directory, and delete that
directory once the run's logs are copied out.

## Local cleanup records

### 2026-10-07 batch — state: PROPOSED, not executed

What it covers, why each item is removable, the preserved bytes, the restoration proof and the recovery
commands are in `evidence-epochs/housekeeping-20261007/RECOVERY.md` and `inventory.json`, local and NERSC
copies. Change the state line above when the batch is executed (record the execution log) or declined.
