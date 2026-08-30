# CLOSE 2026-08-30 — the canonical quiesce window has expired on its own terms

**CITABLE FOR:** the fact that the window opened by
`FREEZE-20260830-canonical-quiesce-k0-7ac0edec.md` is closed, and for the independent sbatch-time
verification recorded below.
**NOT CITABLE FOR** any gate movement, for the post-path `F-17(b)` operands, or for a general policy
about the canonical checkout. Gate 1 is **PASS** (round 2, `22fc4e84`); **Gate 2 remains FAIL**; no
scalar-5D covariance is adopted; leg 6 was not submitted.

## Authority — the freeze closes itself

No new authorization is claimed here. The freeze's own rule states:

> *"It expires when submission is authorized or the rehearsal is abandoned — not when the capture
> finishes, because the operand must still describe its subject at `sbatch` time, which is the
> property `F-17(a)` actually tests."*

Submission was authorized by Joseph, 2026-08-30 — *"submit it"* — and was executed at `15:46:01Z`
through `15:48:04Z` (`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md`, `2094371b`). Both
limbs of the expiry clause are satisfied. This record only observes that the stated condition
occurred, and measures what the clause says must be measured.

## The property the clause names, verified independently of the producer

The producer reports the operand held across five reads. This lane did not take that on report. It
remeasured the canonical checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold` directly, after the
seventh arm was queued:

| field | operand | independent remeasure |
|---|---|---|
| HEAD | `32e403b8` | `32e403b8` |
| porcelain count | 726 | **726** |
| `git status --porcelain` sha256 | `d429f0f3…c08146a` | **`d429f0f3…c08146a`** |
| `?? nd-unfolding/mii/` present | yes | **yes** |

The digest is the strong form: not the count but the exact status bytes.

## The quarantine executed inside the window without disturbing it

Independently remeasured at the destination
`/pscratch/sd/j/josephrb/quarantine/20260830-k0-aa67c426-failed-rehearsal/`:
**517 files**, **189 `.root` / 185 `.npz` / 143 `.done`**, zero symlinks, source namespace `0` files
with the directory retained, both sibling members present.

**The two byte figures reconcile exactly.** `du -sb` on the destination returns **2,733,153,357**
against an authorized **2,733,149,261**, a difference of **4,096** — one directory inode for the
added `20260830-…/` wrapper level. The producer's decomposition (2,733,087,821 regular-file bytes
plus 61,440 directory-inode bytes) accounts for the authorized figure, and adding one wrapper
directory to it reproduces this lane's independent measurement. Two lanes measuring different
quantities arrived at consistent arithmetic.

The three quarantine generations also reconcile: this lane measured **938** files across the whole
`quarantine/` tree, and 517 + 415 + 6 = 938 — the 2026-08-22 and 2026-08-23 dispositions are intact
at the counts the producer reports.

## The seven arms, with array specifications read untruncated

| arm | job id | tasks | time limit | account | dependency |
|---|---|---:|---|---|---|
| `boot5dG` | `57742557` | `[1-100]` | 3:00 | `m3246_g` | — |
| `ssplit5d` | `57742558` | `[1-24]` | 3:00 | `m3246` | — |
| `det5dBKG` | `57742559` | `[0-18%8]` | 4:00 | `m3246_g` | — |
| `uthrow5d_runF` | `57742560` | `[0-39%40]` | 6:00 | `m3246` | — |
| `uthrow5d_block` | `57742561` | `[0-20%10]` | 12:00 | `m3246` | — |
| `sweep5dBKGrun` | `57742633` | `[1-169%48]` | 1:30 | `m3246_g` | `afterok:57742559_*` |
| `uthrow5d_combF` | `57742635` | 1 | 3:00 | `m3246` | `afterok:57742560_*`, `afterok:57742561_*` |

374 tasks. `uthrow5d_combF` carries **two comma-separated `afterok` terms**, which Slurm ANDs — the
conjunctive dependency the proposal requires, not a chain of one. Both joins depend on whole arrays
(`_*`), so a single failed task blocks the join rather than letting it run on partial input.

**The running code is the graded code.** The arms' `Command` resolves under
`/pscratch/sd/j/josephrb/k0r2/clean`, whose HEAD is
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`, detached, **porcelain 0**, with
`measure_m1_m6.py` at the pinned `ce52ff77…`. `WorkDir` is tagged
`k0-7ac0edec-20260830T000215Z`.

## A correction to the producer's budget arithmetic

`RECORD-20260830-…` states the walltime-request envelope maxes at **253.5**. Recomputed here as
tasks × time limit: 300 / 72 / 76 / 240 / 252 / **253.5** / 3. The maximum is **300**
(`boot5dG`, 100 × 3:00), not 253.5 — 253.5 is the largest of the *other six*. **The verdict is
unaffected**: every arm remains far under the 500 GPU-h and 500 CPU-h per-arm ceilings Joseph set.
The `OI-177` question about §6's per-arm CPU estimate column is separate and remains open.

## What is now permitted, and what is not

Lanes may write to the canonical checkout again. **The dashboard lane is released** and may land the
collector-output fix routed by `OI-175`, expected to move porcelain **726 → 725**; that lane held
off on this lane's word.

**The deployment tree is NOT released.** `/pscratch/sd/j/josephrb/k0r2/clean` stays frozen detached
at `7ac0edec` under `§7.0.19` for the life of this run.

**The post-path `F-17(b)` comparison is NOT covered by this record.** Its operands are captured
fresh after the run, against a canonical tree that will by then have moved — including by the
dashboard fix this record releases. Whether that capture needs its own quiesce is **not decided
here**; it is the same shape that produced the round-1 BLOCK, and assuming it away would repeat it.
Routed as `OI-178`.
