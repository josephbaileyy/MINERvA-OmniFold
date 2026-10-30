# RECORD — OI-74 re-measured: the canonical checkout is 3,692 commits behind main, and reconciling it is Joseph's (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30 (backlog candidate 2): one read-only connect
for HEAD, porcelain and merge-base, then a classification of the row. The director approved the connect exactly as
planned: `GIT_OPTIONAL_LOCKS=0`, counts and shas only, nothing fetched or written, no logs, no waker state, no
`squeue`. Local reads at `origin/main` `197ba685b`.

**CHANGES:** OI-74's register row moves to `WAITING-JOSEPH`, owner `joseph`, with a dated prefix in `OPEN_ITEMS.md`.
Nothing on the cluster is changed.

**CITABLE FOR:** the canonical checkout's HEAD, branch, porcelain counts and distance from main at 2026-10-30T16:07Z,
and the records that govern it.

**NOT CITABLE FOR:**
- which two tracked paths are changed, or what any untracked path is. The connect counted lines, and printed no names;
- an authorization to fetch, pull, reset or otherwise write to that checkout;
- whether any job was reading the tree at the time. `squeue` was not run.
<!-- absence-ok: a scoping statement about this record's own read, which the director limited to exclude squeue -->

## 1. The measurement

**One ssh to `saul.nersc.gov`,** answered by `login37` from 16:07:09Z to 16:07:12Z
([`state/oi74-canonical-drift-20261030/connect-session.txt`](state/oi74-canonical-drift-20261030/connect-session.txt),
sha256 `1feee9be42274e22…`, which holds the script and its output). Every git call ran with `GIT_OPTIONAL_LOCKS=0`,
so `git status` could not refresh `.git/index`. Every call returned rc 0.

| quantity | value |
|---|---|
| `HEAD` | `32e403b84e9e8f9d9bc435028749f896653c7a43`, committed 2026-08-29T23:47:01+02:00 |
| branch | `main`, attached |
| `git status --porcelain` lines | 733 |
| of them, tracked changes (`--untracked-files=no`) | 2 |

**Computed locally** from that sha, since the checkout has no `origin` remote (its remotes are `github` and
`analysis-note`, `HANDOFF-20260902-operational-baseline-snapshot.md:358-361`):
- `32e403b84` is present here and is an ancestor of `origin/main` `197ba685b`;
- it is **3,692 commits behind and 0 ahead**. The checkout is behind main, not forked from it.

## 2. The row's numbers over time

| date | HEAD | porcelain | tracked changes | behind main | source |
|---|---|---:|---:|---|---|
| 2026-08-15 | `683bdcc` | 751 | not split | 3 days, one required commit | OI-74's blocker cell |
| 2026-08-17 | `7ac36ac` | 725 | 4 | 11 commits | OI-74's state cell, after the sync run under Joseph's authorization |
| 2026-08-30 | `32e403b8` | 726 | 0 modified | not stated | `GATE1-VERDICT-ROUND2-20260830-k0-7ac0edec.md:98-99` |
| 2026-09-02 | `32e403b84e9e` | 726 | 0 | 116 commits | `HANDOFF-20260902-operational-baseline-snapshot.md:352` |
| 2026-10-29 | `32e403b84` | not read | not read | | `state/oi160-tolerance-20261029/run/logs/removal-session.txt:80` |
| **2026-10-30** | **`32e403b84`** | **733** | **2** | **3,692 commits** | §1 |

The earlier rows are quoted from their records, not re-measured. **Two things changed since 2026-09-02:** the
checkout has stayed at the same commit for two months while main moved 3,576 commits, and it now has 2 tracked
changes where it had none.

## 3. What governs the checkout

- **No hold is in force on it.** Its two quiesce windows closed by their own terms on 2026-08-30
  (`CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md`, `CLOSE-20260830-canonical-requiesce-k0r2-window.md`).
  The two deployment freezes, `DECISION-20260824-joseph-deployment-freeze-until-f1b.md` and
  `FREEZE-20260830-k0-deployment-7ac0edec.md`, cover `/pscratch/sd/j/josephrb/k0r2/clean`, a different tree.
  Search: `ls docs/orchestration | grep -i -E "FREEZE|QUIESCE|canonical"` and `git grep -l 32e403b8` @ `776bc811b`.
- **The last stated reason it stayed at `32e403b8`** is `OUTCOME-20260921-L2-probe-blocked-at-stage-4.md:174-175`:
  *"the deployed checkout, which stays at `32e403b8` because PET's array `58692544` runs from it"*. That was true on
  2026-09-21. Whether it still binds was not checked.
- **`docs/LOCAL_CHECKOUTS_AND_STORAGE.md:24-25`** defers cluster checkouts to their own run records.
- **The last reconciliation**, on 2026-08-17, was run by the mediator session under Joseph's direct authorization
  (OI-74's state cell). A reconciliation is a write to the canonical checkout, which this lane may not make.

**Why the drift still matters.** OI-74's blocker cell, of 2026-08-15, says `AGENTS.md` named this tree as `MNV_REPO`;
today's `AGENTS.md` does not mention `MNV_REPO`. Launchers still name the tree: 214 `nd-unfolding/*.sh` files contain its
path (`git grep -l -F "/pscratch/sd/j/josephrb/MINERvA-OmniFold" -- 'nd-unfolding/*.sh'` @ `197ba685b`). `KNOWN_ISSUES.md` row 89 records that `fixed_truth_toy.py` imports the OmniFold helper
from the canonical checkout whichever tree launches it. So code 3,692 commits old is what those imports load.

## Classification

**OI-74 stays open, and moves to `WAITING-JOSEPH` with owner `joseph`.** Its 2026-08-15 headline is true again in a
larger form: the checkout is behind main and read by launchers. Its 2026-08-17 correction, *"the drift is gone"*, was
true then and is not now. Nothing else on the backlog can act on it: the remedy is a write to the canonical
checkout, and the last one was Joseph's to authorize.

**What a reconciliation would need, from the row and the records above.** This is a list of preconditions, not a
proposal:
1. the two tracked changes named and dispositioned first. They are new since 2026-09-02;
2. no job reading the tree when it moves. Several launchers pin files inside it by sha256, OI-74's next-action
   cell; the PET array reason of 2026-09-21 would need re-checking;
3. the right remote. `git pull --ff-only origin main` fails there, because there is no `origin` (OI-74's state cell).

## Limits

- The two tracked paths and the 731 untracked ones were counted, not named.
- 733 is the default `-u` count. The `-uall` count, 3,473 on 2026-09-02, was not read.
- Whether a job reads the tree now was not measured.
<!-- absence-ok: a scoping statement about this record's own read, which the director limited to exclude squeue -->
