# REPORT — OI-74: the bound run of `ff.sh` stopped at STOP 26 and rolled back (2026-10-30)

**By** the close-items session. **Reports** the one run that [`BINDING.md`](BINDING.md) authorizes, of
[`ff.sh`](ff.sh) (sha256 `afe92465b1a7178f06a122365b1a282d9b7daf5ebcf94950a2ea67751360ce52`) under
[`DECLARATION.md`](DECLARATION.md). The director said "go" after I told them I was about to connect.

**Outcome: STOP 26, after the fetch.** Four paths that main adds already exist in the tree as untracked files that are
not ignored, so `git merge --ff-only` would refuse them. The rollback ran and passed. **The tree is as it was before the
run:** HEAD `32e403b84` on `main`, and the same two tracked changes with the same bytes. Nothing was retried or repaired.

**CITABLE FOR:** what the transcript prints: the preconditions, the fetch, P5's counts and the four paths, and the
rollback's sha256 and HEAD.

**NOT CITABLE FOR:**
- C1–C4. The post-check never ran, because W4 never ran;
- who wrote the four untracked files, or when. No mtimes or contents were read on the cluster;
- an authorization to remove, move or overwrite them.
<!-- absence-ok: scoping statements about what this run's own transcript covers -->

## 1. The run

**One ssh to `saul.nersc.gov`,** answered by `login37` from 21:02:48Z to 21:03:13Z. The command was the declaration's §6
command, run once from this directory. Transcript: [`run/session.txt`](run/session.txt), 89 lines, sha256
`b2bc85d821bdc3dd190680bb654f6e4b3f300dc61e310a896f680af3f1746a85`. Local rc 0, `ssh_rc 26`. The cluster's git is
2.51.0; the local test ran under 2.39.3.

| step | printed | result |
|---|---|---|
| P1 | `squeue_me_jobs 0` | pass; no job under `--me`, scron included |
| P2 | head `32e403b84e9e8f9d9bc435028749f896653c7a43`, branch `main` | pass |
| P3 | `tracked_rc 0`; exactly ` M docs/orchestration/LIVE-STATE.md`, ` M docs/orchestration/state/live-state-last-known.json` | pass |
| P4 | `untracked_before 731` | pass; the aside directory did not exist |
| W1 | aside `/pscratch/sd/j/josephrb/oi74-ff-20261030`, `SHA256SUMS` below | done |
| W2 | `checkout_rc 0`, `tracked_after_restore 0` | done |
| W3 | `fetch_rc 0`; `github/main` `eac51ab2eae896c802d58aae03b42cad0c02cabe`; behind 3726, ahead 0 | done |
| P5 | added 13646, present 6, identical 6, differ 0, untracked_not_ignored 4 | **STOP 26** |
| P1b, W4, C1–C4 | — | not reached |
<!-- absence-ok: rows of a table of the transcript's own steps -->

**The aside copies,** as `SHA256SUMS` in the aside directory holds them:

```
568ea13f22b580e804583b061983431253f7fd28941e5b84a4d8de148f4943e1  LIVE-STATE.md
73727bb932d2ce23fd4f08dbdc96fceb87f7c01e1085a727bb0b1e1b58331aca  live-state-last-known.json
```

## 2. What stopped it

**The four paths,** as P5 printed them:

| path | added on main by |
|---|---|
| `docs/orchestration/dashboard.html` | `a8000d1c5` (2026-08-30) |
| `docs/orchestration/dashboard_collector.py` | `a8000d1c5` (2026-08-30) |
| `docs/orchestration/test_dashboard_collector.py` | `a8000d1c5` (2026-08-30) |
| `nd-unfolding/tests/test_cstat_100rep.py` | `c60f3a3f2` (2026-09-23) |

The second column is counted locally: `git log --diff-filter=A 32e403b84..eac51ab2e -- <path>`.

**All six present paths are byte-identical to main's blobs** (`identical 6`, `differ 0`), and so are these four. So the
merge would change no bytes at these paths. git refuses it anyway, because the files are untracked and not ignored.
P5 caught that before W4, as the declaration's §2 intended.

**Cross-checked locally** against the fetched sha: `git rev-list --count 32e403b84..eac51ab2e` is 3,726, and
`git diff --name-only --diff-filter=A 32e403b84 eac51ab2e` lists 13,646 paths. Both match the transcript.
`eac51ab2e` is the merge of #548 and descends from the binding's merge `def9acb70`.

## 3. The rollback, and what the run left behind

**The rollback passed.**
- `rollback_cp_rc 0`.
- The two files in the tree have the same sha256 as their aside copies (above).
- `rollback_head 32e403b84…`.
- `rollback_tracked OK (the two files, as before)`.

**What the run left, as the declaration's §3 named:**
- the fetch's objects;
- `refs/remotes/github/main`, moved from `9e78a8cfa` to `eac51ab2e`;
- 48 new `refs/remotes/github/*` branches and 4 new tags;
- the aside directory `/pscratch/sd/j/josephrb/oi74-ff-20261030`. It stays until the director says otherwise. A second
  run of this `ff.sh` would stop at STOP 16 because of it.

The untracked files were not touched, and no job was launched. Nothing was written to CFS.

## 4. What goes next

**The fast-forward is not done, and this binding cannot finish it.** It authorized one run, and that run has happened.
It forbids touching untracked files, and the four blocking files are untracked. Finishing needs a new declaration and
binding. Whether, and how, to handle the four files is the director's call, or Joseph's. This report proposes none.

OI-74 stays `active` `WAITING-JOSEPH`, owner `joseph`.

## 5. A correction to `BINDING.md` §1, beside it (that record is not edited)

§1 lists "a failed squeue" among the five pre-write STOPs that `test_ff.sh` exercises. `test_ff.sh` has no such case,
and STOP 10 is unexercised (DECLARATION §5). The fifth pre-write case is "only one of the two live-state edits",
STOP 15 (`test_ff.sh:71`). This changes nothing that was bound.
<!-- absence-ok: a correction naming a test case that test_ff.sh does not contain, checked against its eleven cases -->
