# CLOSE 2026-08-30 — the re-submission quiesce window has closed on its own terms

**CITABLE FOR:** the fact and time of closure, and the release it grants. **NOT CITABLE FOR:** any
gate movement; discharge of `F-17(a)` or `F-17(b)`; the round-2 outcome; or adoption. **Gate 2 remains
FAIL.**

## The condition, quoted from the record it closes

`FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md`:

> **It expires when the re-submission is issued or abandoned — not when any capture finishes**,
> because the operand must still describe its subject at `sbatch` time, which is the property
> `F-17(a)` actually tests.

**The re-submission was ISSUED** at `20:47:32Z`–`20:47:38Z` — seven job ids `57753239`, `57753243`,
`57753244`, `57753245`, `57753246`, `57753247`, `57753248`, recorded at
`RECORD-20260830-k0r2-round2-submission.md`. **So the window is closed by its own terms**, on the
same branch and by the same wording as the first window's close record.

The window held for its whole life. Three operand reads at `20:47:32Z`, `20:47:37Z` and `20:47:38Z`
each returned porcelain **726** and status digest `d429f0f3`, and the abort arm — `exit 9` with no
`sbatch` — never fired.

**The hold was never mechanically enforced and this record does not claim it was.** It was a prose
hold, and the lane it most needed to reach was not reachable: no dashboard-lane session was live to
acknowledge the request. Per the freeze record's own terms — *"if that request is not acknowledged,
the correct reading is that the window is unprotected, not that it is protected by this file"* — the
window was treated as **UNPROTECTED** throughout, and the protection actually relied on was the
armed abort arm re-reading the operand immediately before each `sbatch`. **That is what held, not the
prose.** A future window should not read this closure as evidence that a prose hold works.

## What is released

- **Lanes may write to the canonical checkout again**, `/pscratch/sd/j/josephrb/MINERvA-OmniFold`.
- **The dashboard lane is released and may land the `OI-175` fix**, taking porcelain **726 → 725**.
  **That release is safe now for a reason that was decided, not assumed:** `OI-178` was settled on
  2026-08-30 (`DECISION-20260830-joseph-f17b-post-path-drift-is-a-filed-finding.md`) — canonical
  drift between the pre- and post-path `F-17(b)` captures is a **FILED FINDING** yielding exit 20
  with the finding retained, not a block. Joseph chose that option explicitly. So 726 → 725 during
  the run is the outcome that ruling already contemplates.

## What is NOT released

**The deployment tree is NOT released.** `/pscratch/sd/j/josephrb/k0r2/clean` stays frozen detached at
`7ac0edec` with porcelain 0 and read-only modes for the life of the run, under §7.0.19. Nothing here
touches it.

**And the run is not graded.** No task had started when this record was written. The round-2 outcome
is owed as its own record.
