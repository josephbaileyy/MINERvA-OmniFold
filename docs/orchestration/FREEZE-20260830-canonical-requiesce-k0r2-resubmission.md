# FREEZE 2026-08-30 — the canonical checkout is RE-QUIESCED for the k=0 re-submission window

**CITABLE FOR:** the rule below, its scope, its expiry condition, and the measured state at the
moment it opens. **NOT CITABLE FOR:** any gate movement; discharge of `F-17(a)` or `F-17(b)`;
ratification of `OI-177`; a `PACKET-20260823` correction; or any adoption. **Gate 2 remains FAIL.**

## Why a SECOND quiesce record exists

The first window, `FREEZE-20260830-canonical-quiesce-k0-7ac0edec.md`, **expired by its own terms**
when submission was authorized — recorded at
`CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md`, which also **released the dashboard lane**
and states it may land the `OI-175` fix. That fix removes files from the canonical working tree and
takes porcelain **726 → 725**.

That submission then failed for an unrelated reason — the submitter allowlist was never declared,
`FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md` and `OI-179` — and Joseph has
authorized a re-submission (`PROPOSAL-20260830-k0r2-resubmission.md`). **So a new operand window
opens with no hold in force and one lane explicitly released to move the count.**

**THE DISTINCTION THAT MATTERS, and the earlier handoff got it the other way round.** Nothing has
drifted. Re-measured at **2026-08-30T20:43:52Z** on `saul`, immediately before this record was
written — and note that this is **just under five hours after the 15:46Z submission**, so the values
below are a five-hour hold, not a single lucky read:

| property | at 15:46Z submission | measured now | |
|---|---|---|---|
| canonical HEAD | `32e403b8` | `32e403b8` | unchanged |
| canonical porcelain | 726 | **726** | unchanged |
| canonical status digest | `d429f0f3…8146a` | **`d429f0f3daa5efe43519…`** | unchanged |
| `mii/member_k000000` | 0 entries, 0 `.done` | **0 entries** | unchanged |
| porcelain composition | — | **726 untracked, 0 modified** | the population is untracked-not-ignored |

So the existing `F-17(a)` operands still describe their subject, and this record is **not** repairing
a violation. It is closing a window that is currently open. The risk is **permitted future drift**,
not drift that occurred — which is a weaker claim than the one that motivated the first freeze, and
it is stated as the weaker claim on purpose.

## THE RULE

> **For the k=0 re-submission authorized at `PROPOSAL-20260830-k0r2-resubmission.md` only, the
> canonical cluster checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is RE-QUIESCED from the
> commit that carries this record until that re-submission is authorized-and-issued or abandoned.**
>
> **No lane may create, modify or delete any path under it that `git status --porcelain` would
> report** — tracked or untracked-and-not-ignored. Committing to the repository from a DIFFERENT
> checkout is unaffected; it is the working tree at that path that must not change.
>
> **Gitignored runtime state is EXCLUDED and may continue**, in particular the waker's
> `state/waker/` ticks, which do not enter the porcelain population.
>
> **THE DASHBOARD LANE'S `OI-175` FIX IS HELD AGAIN.** `CLOSE-20260830` released it; this record
> asks for that release to pause until the window shuts. The fix is agreed and is not being
> withdrawn — only deferred, for the same reason it was deferred the first time: landing it moves
> 726 → 725 mid-window.
>
> **It expires when the re-submission is issued or abandoned — not when any capture finishes**,
> because the operand must still describe its subject at `sbatch` time, which is the property
> `F-17(a)` actually tests.

## Enforcement is by convention, and this is said out loud

This is a **prose hold**, preventive by convention and detective by `F-17(a)` — the same shape as the
first window and with the same limits. Nothing prevents a lane from writing. `F-17(a)` will *catch* a
violation rather than *prevent* it.

**AND A HOLD PEERS CANNOT SEE IS NOT A HOLD.** The first record says this and it applies harder here,
because the lane being asked to pause was explicitly released by a record that is already committed.
So this record is **pushed before any operand is read**, and the dashboard lane is asked **directly**
by message rather than assumed to have noticed. If that request is not acknowledged, the correct
reading is that the window is unprotected, not that it is protected by this file.

## What opens and closes it

- **Opens:** the commit carrying this file, pushed.
- **Closes:** the re-submission being issued, or abandoned — recorded either way. A `CLOSE-*` record
  is owed on both branches, and closing it silently is the failure mode the first window's close
  record exists to prevent.
