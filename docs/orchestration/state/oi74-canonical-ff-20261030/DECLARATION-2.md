# DECLARATION 2 — OI-74: the second fast-forward run, moving the four byte-identical untracked files aside (2026-10-30)

**By** the close-items session, for the director to bind. **Nothing is written to the cluster before the binding.**

**Under** [`DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md`](../../DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md)
(#558), item 1. Joseph's answer: *"Yes, move the 4 aside (Recommended)"*. The option it accepts: *"A new declaration I
bind: only those 4 byte-identical files move aside (with checksums), then the ff-only merge recreates them from main.
Nothing else is touched."*

**Declares:** one run of [`ff2.sh`](ff2.sh), sha256 `c0e393b08daaf20738b0657a6acea62083579d67a1f6c28f1f9a3186523fb851`,
by one ssh to `saul.nersc.gov`. It is tested locally by [`test_ff2.sh`](test_ff2.sh), sha256
`c9c9ddf651f2a8e29ff4e0161c809ffe49cf2a7a04ed02f0bda273d8cff00c06` (§5).

**CANNOT AUTHORIZE:**
- moving, removing or editing any untracked file other than the four named in §1;
- any change in the tree beyond the fast-forward, the restore of the two live-state files and that move;
- launching a job, or writing to CFS;
- a second run of `ff2.sh`. A STOP is reported to the director, not retried.

## 1. What is different from the first run

The first run is [`DECLARATION.md`](DECLARATION.md), bound by [`BINDING.md`](BINDING.md) and reported in
[`REPORT.md`](REPORT.md). It stopped at STOP 26 and rolled back. **Every precondition and step of it stands**, as the
decision says, with these changes:

**The four files.** They are the only untracked, not-ignored files the first run found at paths main adds:
- `docs/orchestration/dashboard.html`
- `docs/orchestration/dashboard_collector.py`
- `docs/orchestration/test_dashboard_collector.py`
- `nd-unfolding/tests/test_cstat_100rep.py`

`ff2.sh` names them as a constant. Their blobs on main are unchanged from `eac51ab2e`, the first run's fetch, to
`190e6cf99`: `26993f76`, `f08b12e8`, `e10f5972` and `5ce3dbdf`.

**The aside directory exists, and is handled explicitly.** `ff.sh`'s STOP 16 required it to be absent. `ff2.sh`
instead requires it to hold exactly the first run's three files. The four move into a subdirectory,
`untracked-at-added-paths/`, which keeps their relative paths and gets its own `SHA256SUMS`. **The first run's two
live-state copies are neither rewritten nor recopied.** The run checks that the tree's two files still have those
copies' bytes; otherwise it stops (STOP 19).

**The first write is now W2,** the restore of the two live-state files. W1 is gone, because the copies already exist.
**From W2 on, every STOP rolls back all six files:**
- the two live-state files are copied back from the first run's aside copies;
- any of the four already moved is moved back with `mv -n`, which never overwrites.

## 2. Preconditions: read-only, each a STOP

| | condition | STOP |
|---|---|---|
| P1 | `squeue --me` returns rc 0 and lists no job at all, scron included | 10, 11 |
| P2 | HEAD is `32e403b84…` on branch `main`, with no `MERGE_HEAD` or `index.lock` | 12, 13, 14 |
| P3 | the tracked porcelain is exactly the two live-state files, both ` M` | 15 |
| P6a | the subdirectory `/pscratch/sd/j/josephrb/oi74-ff-20261030/untracked-at-added-paths` does not exist | 17 |
| P6b | the aside directory holds exactly `LIVE-STATE.md`, `SHA256SUMS` and `live-state-last-known.json` | 16 |
| P6c | `sha256sum -c SHA256SUMS` passes in the aside directory | 18 |
| P6d | the tree's two live-state files have the same sha256 as the aside copies | 19 |
| P5 | after the fetch, no added path present in the tree differs from main's blob, and the untracked, not-ignored ones are **exactly** the four | 25, 26 |
| W5 | each of the four is re-hashed against the fetched main's blob immediately before it moves | 29 |
| P1b | `squeue --me` again, just before the merge: still no job | 27 |
<!-- absence-ok: P6a is a precondition the script tests, not a claim about the tree -->

**Why P5 asks for exactly the four.** A fifth untracked file at an added path would make git refuse the merge, and
moving it is outside the decision. A missing one would mean the tree changed since the first run. Either way it is
STOP 26.

## 3. The steps

| | step | on failure |
|---|---|---|
| W2 | `git checkout -- <the two files>`, restoring them to HEAD; the tracked porcelain must then be empty | STOP 22, with rollback |
| W3 | `git fetch github`; `github/main` must descend from `32e403b84` | STOP 23, 24, with rollback |
| P5 | as in §2, read-only | STOP 25, 26, with rollback |
| W5 | `mkdir` the subdirectory. Then for each of the four: re-hash it against main (STOP 29); `mv -n` it into the subdirectory under its relative path; check that its sha256 there equals its sha256 just before the move. Then write `SHA256SUMS` | STOP 29, 31, with rollback |
| P1b | as in §2 | STOP 27, with rollback |
| W4 | `git merge --ff-only --no-stat <the fetched github/main sha>` | STOP 28, with rollback |

**Rollback**, on any STOP from W2 on:
- copy both live-state files back from the aside directory;
- move back each of the four that was already moved, with `mv -n`. A target that already exists is reported and left;
- print the four paths' blob ids and HEAD;
- check that the tracked porcelain is again exactly the two files, with the aside copies' sha256 (`rollback_tracked OK`).

The only residue is the fetch's (objects and `refs/remotes/github/*`), plus the subdirectory if it was made. A
subdirectory left by a rollback holds at most its `SHA256SUMS`.

**Every git call against the tree** runs, as before, with `GIT_OPTIONAL_LOCKS=0`, `-c core.hooksPath=/dev/null` and
`-c gc.auto=0 -c maintenance.auto=false`.

## 4. The post-check

C1–C4 are as in the first declaration. C5 is new.

| | check | must be |
|---|---|---|
| C1 | HEAD | equal to the fetched `github/main`, on `main` |
| C2 | tracked porcelain | empty |
| C3 | untracked count | not above the count before |
| — | `sha256sum -c` in the aside directory and in the subdirectory | OK for all six |
| C5 | each of the four | tracked (`git ls-files`), with the same sha256 as its moved copy |
| C4 | what now loads new code | the A/M/D counts, the launcher counts and the three KI-89 blobs, as before |

**A failed post-check exits 30 and is not undone.**

**C3, measured locally.** Between `32e403b84` and `190e6cf99`, the `.gitignore` files gain 61 lines and lose 1, and the
one lost is a comment. So the new rules can only ignore more. Moving the four, which become tracked, lowers the count by
4.

## 5. The local test

`bash test_ff2.sh <scratch-dir>` builds a scratch `github` remote holding the old and new commits. Its checkout has
the two live-state edits, the four files byte-identical to the new commit's, and an aside directory exactly as the
first run left it. It stubs `squeue` and runs a copy of `ff2.sh` with only its path and sha constants substituted.
Under bash 3.2.57 and git 2.39.3 it reports **16 passed, 0 failed**:

- **Good state:**
  - it runs to `DONE`, with the four tracked and their moved copies checked;
  - the aside copies are untouched and the other untracked files are kept;
  - an identical ignored file beside the four also proceeds.
- **Eight STOPs fire before any write**, leaving HEAD, the tracked porcelain, all six files and the aside directory
  byte-identical:
  - 11: a job under `--me`;
  - 12: a different HEAD;
  - 15: a third tracked change;
  - 16 (twice): the aside directory missing, and an extra file in it;
  - 17: the subdirectory already exists;
  - 18: an aside copy fails its sums;
  - 19: a live-state file differs from its aside copy.
- **Six STOPs fire after W2 and roll back all six files to the same state, with no file left in the subdirectory:**
  - 25: one of the four differs from main;
  - 26 (twice): a fifth untracked file at an added path, and one of the four missing;
  - 23: a failed fetch;
  - 29: a file changed between P5 and its move. A stub `mv` alters the second file during the first move, so the
    rollback must move the first one back;
  - 27: a job appears after all four have moved.

**Mutation checks.** Each mutant was run against the test in a fresh scratch directory, and each made the test fail:

| mutant | test cases that fail |
|---|---|
| no re-hash before the move | 1 (STOP 29) |
| no exactly-the-four check | 2 (both STOP 26 cases) |
| a rollback that does not move files back | 2 (STOPs 29 and 27) |
| no tree-equals-aside check | 1 (STOP 19) |
| no subdirectory check | 1 (STOP 17) |

**Not exercised locally:** STOPs 10, 13, 14, 22, 24, 28 and 31. Each guards a single call's rc or a simple test, in the
same pattern as the exercised ones. The cluster's git is 2.51.0 (REPORT.md); the local one is 2.39.3.
<!-- absence-ok: a scoping statement about which arms this declaration's own test covers -->

## 6. The transcript plan

After the binding, I tell the director before I connect. Then, from the local side, once:

```
{ echo "\$ ssh saul.nersc.gov 'bash -s' < ff2.sh   # ff2.sh sha256 c0e393b0…"; ssh saul.nersc.gov 'bash -s' < ff2.sh; echo "ssh_rc $?"; } > run2/session.txt 2>&1
```

`run2/session.txt` is committed under this directory with `REPORT-2.md`, and OI-74's row is updated in the same PR.

**The transcript prints:** shas, counts, status codes, paths and sha256, and at most 20 paths per P5 category. It
prints no file contents, logs or waker state. The aside directory and the subdirectory stay on pscratch until the
director says otherwise.

## 7. Limits

- **P1 sees only this account's jobs**, as before.
- **The window between P1b and W4** is a few seconds, as before.
- **Main will have moved by the run.** P5 and C4 measure against whatever `github/main` the fetch returns. A newly
  added path with an untracked file on the cluster would be STOP 26 again.
- **The four files' mtimes and authors are not read.** They are moved with `mv`, which keeps their mtimes, so they can
  still be read later.
