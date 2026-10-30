# DECLARATION — OI-74: fast-forward the canonical cluster checkout to `github/main` (2026-10-30)

**By** the close-items session, for the director to bind. **Nothing is written to the cluster before the binding.**

**Under** [`DECISION-20261030-joseph-canonical-checkout-and-table-check.md`](../../DECISION-20261030-joseph-canonical-checkout-and-table-check.md)
(#544), item 1: *"The canonical checkout is fast-forwarded to `main`, under preconditions"*. Joseph's answer:
*"Yes, under preconditions (Recommended)"*. *"The close-items session declares it, and the director binds it before
anything is written."*

**Declares:** one run of [`ff.sh`](ff.sh), sha256 `afe92465b1a7178f06a122365b1a282d9b7daf5ebcf94950a2ea67751360ce52`,
by one ssh to `saul.nersc.gov`. It is tested locally by [`test_ff.sh`](test_ff.sh), sha256 `3d4adfcfc20ea524…` (§5).

**CANNOT AUTHORIZE:**
- any change in the tree beyond the fast-forward and the restore of the two live-state files;
- touching an untracked file, launching a job, or writing to CFS;
- a second run. A STOP is reported to the director, not retried.

## 1. The tree and what reads it

**The tree:** `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, at `32e403b84` (2026-08-29) on `main`. Its remotes are
`github` and `analysis-note`, with no `origin`. Measured on 2026-10-30
([`RECORD-20261030-close-items-oi74-canonical-drift.md`](../../RECORD-20261030-close-items-oi74-canonical-drift.md),
[`RECORD-20261030-close-items-oi74-tracked-changes.md`](../../RECORD-20261030-close-items-oi74-tracked-changes.md)):
- 733 porcelain lines;
- 2 tracked changes, both unstaged edits to `generate_live_state.py`'s outputs.

**What reads it**, so the post-check can say what now loads new code. Counted locally against `origin/main`
`2c0f6ab4d`:
- **Launchers:** 200 `nd-unfolding/*.sh` files name the tree's path at `32e403b84`; 214 do at main. Across all `*.sh`
  and `*.py`, 574 do at main.
- **The 2D driver's hard-coded import (the KI 89 mechanism).** `2d-unfolding/unfold_2d_omnifold_unbinned.py` puts
  this tree's `unbinned_unfolding/python` on `sys.path` in its `main()`: `:1679-1681` at `32e403b84`, `:2059-2061` at
  main. So any run of that driver loads `omnifold.py` from this tree, whichever tree launches it. That file's blob is
  `5966663bfe88` at both commits, so **the fast-forward does not change what this import loads.**
- **A correction, beside the records that made it (none edited).** The #541 record (§3) and #544's "What led to it"
  say that KI 89's toy, `fixed_truth_toy.py`, imports from this tree. KI 89 recorded that. At main the toy derives its
  OmniFold path from its own checkout instead (`fixed_truth_toy.py:46-49`, the OI-136 repair), and it is absent at
  `32e403b84`. The #541 record's *"code 3,692 commits old is what those imports load"* overstates the case for the
  helper, which is unchanged. It holds for the launchers, which run this tree's own files.
- **The change set** at `2c0f6ab4d`: 13,597 paths added, 273 modified, 7 deleted. The run re-counts all of this
  against the main it fetches (C4).

## 2. Preconditions: read-only, each a STOP

Joseph's three, then those this declaration adds. **The additions only add STOPs or a rollback; none relaxes a
condition.**

| | condition | STOP |
|---|---|---|
| P1 | `squeue --me` returns rc 0 and lists **no job at all**, running or pending | 10, 11 |
| P2 | HEAD is `32e403b84e9e8f9d9bc435028749f896653c7a43`, on branch `main`, with no `MERGE_HEAD` or `index.lock` | 12, 13, 14 |
| P3 | the tracked porcelain is exactly ` M docs/orchestration/LIVE-STATE.md` and ` M docs/orchestration/state/live-state-last-known.json` | 15 |
| P4 | the aside directory `/pscratch/sd/j/josephrb/oi74-ff-20261030` does not exist yet | 16 |
| P5 | between the fetch and the merge: no path the merge adds exists in the tree with bytes different from main's, and none exists as an untracked file that is not ignored | 25, 26 |
| P1b | `squeue --me` again, just before the merge: still no job | 27 |
<!-- absence-ok: P4 is a precondition the script tests, not a claim about the tree -->

**Why P1 counts every job, not only those that read the tree.** 214 launchers hard-code the tree's path, so a job
submitted from any directory can read it, and a job's working directory cannot rule that out. Any job is a STOP.

**Why P5 is added.** 1,590 of the 13,597 added paths are matched by the `.gitignore` rules at `32e403b84`. Computed
locally with `git check-ignore --no-index`, against those `.gitignore` files. A product at such a path in the tree
would be **silently overwritten**. Measured on a scratch repository, git 2.39.3: a plain `git merge --ff-only` replaced
a differing ignored file and returned rc 0. P5 compares each existing added path's `git hash-object` with main's blob:
- an identical file proceeds, since the overwrite changes no bytes;
- a different one is STOP 25.

An untracked, not-ignored file at an added path would make git refuse the merge. P5 catches it first, as STOP 26.

## 3. The steps

| | step | on failure |
|---|---|---|
| W1 | `mkdir` the aside directory; copy both files into it with `cp -p`; write `SHA256SUMS`; check it against the originals | STOP 20, 21; the tree is unchanged |
| W2 | `git checkout -- <the two files>`, restoring them to HEAD; the tracked porcelain must then be empty | STOP 22, with rollback |
| W3 | `git fetch github`; `github/main` must descend from `32e403b84` | STOP 23, 24, with rollback |
| W4 | `git merge --ff-only --no-stat <the fetched github/main sha>` | STOP 28, with rollback |

**Rollback**, on any STOP after W2: copy both files back from the aside directory, print both sets of sha256, and check
that the tracked porcelain is again exactly the two files (`rollback_tracked OK`). The only residue is the fetch's: new
objects and updated `refs/remotes/github/*`. The working tree and HEAD are as they were.

**Every git call against the tree** runs with:
- `GIT_OPTIONAL_LOCKS=0`;
- `-c core.hooksPath=/dev/null`, so no hook runs;
- `-c gc.auto=0 -c maintenance.auto=false`, so no automatic gc or maintenance runs.

**The merge names the fetched sha** rather than `github/main`. It is the same commit, and the transcript records which.

## 4. The post-check

| | check | must be |
|---|---|---|
| C1 | HEAD | equal to the fetched `github/main`, on `main` |
| C2 | tracked porcelain | empty |
| C3 | untracked count | not above the count before (P4's `untracked_before`) |
| — | `sha256sum -c` in the aside directory | OK for both |
| C4 | what now loads new code | the A/M/D counts against the fetched main; the `nd-unfolding/*.sh` and `*.sh`/`*.py` counts naming the tree; the three KI-89 blobs, old and new |

**A failed post-check exits 30 and is not undone.** The tree has moved by then, so what follows is the director's call.

## 5. The local test

`bash test_ff.sh <scratch-dir>` builds a scratch `github` remote and a checkout, stubs `squeue`, and runs a copy of
`ff.sh` with only its path and sha constants substituted. Under bash 3.2.57 and git 2.39.3 it reports **11 passed, 0
failed**:
- the good state runs to `DONE` and keeps the untracked files;
- an identical ignored file at an added path proceeds;
- five STOPs fire before any write, leaving HEAD, the tracked porcelain and both files byte-identical: 11, 12, 15
  (twice) and 16;
- four STOPs fire after W2 and roll back to the same state: 25, 26, 23 and 27.

**Not exercised locally:** STOPs 10, 13, 14, 20–22, 24 and 28. Each guards a single call's rc or a simple test, in the
same pattern as the exercised ones.
<!-- absence-ok: a scoping statement about which arms this declaration's own test covers -->

## 6. The transcript plan

After the binding, I tell the director before I connect. Then, from the local side, once:

```
{ echo "\$ ssh saul.nersc.gov 'bash -s' < ff.sh   # ff.sh sha256 afe92465…"; ssh saul.nersc.gov 'bash -s' < ff.sh; echo "ssh_rc $?"; } > run/session.txt 2>&1
```

`run/session.txt` is committed under this directory with a REPORT, and OI-74's row is updated in the same PR.

**The transcript prints:** shas, counts, status codes, the two files' paths and sha256, and at most 20 paths per P5
category. It prints no file contents, logs or waker state. The aside directory stays on pscratch until the director
says otherwise.

## 7. Limits

- **P1 sees only this account's jobs.** A job under another account that reads the tree is not visible to
  `squeue --me`.
- **The window between P1b and W4** is a few seconds. A job submitted inside it is not caught.
- **What the two live-state files said** is kept in the aside copies only, as Joseph's option asked. Their content is
  not read or committed.
