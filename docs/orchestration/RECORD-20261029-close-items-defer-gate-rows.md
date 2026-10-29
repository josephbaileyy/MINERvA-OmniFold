# RECORD — Gate-4/5/6 conditional rows deferred to named triggers; OI-65#2 retired (2026-10-29)

The close-items session applies backlog candidate 1, on the director's ruling of 2026-10-29. These 12 rows were active
(`NOW` or `BLOCKED-EXTERNAL`) although each one's action matters only at a future gate event that no authorization now
schedules: Gate 4, 5 and 6 are not being re-issued, and PET is diagnostic (`AGENTS.md`). Each is deferred with its
trigger. A first-pass read of all 37 conditional rows was made by a read-only subagent. Every trigger below was then
phrased from the row, and five were checked against the row's own text before use. Measured at `a310bb352`.

## Deferred

| item | trigger | from the row |
|---|---|---|
| OI-25 | the next required Gate-4 re-issue | the row: Joseph deferred the repair until another Gate-4 re-issue is otherwise required |
| OI-26 | the next required Gate-4 re-issue | the row: the successor receipt changes ride the next required re-issue |
| OI-27 | the next Gate-4 re-issue | the row's owner is whoever re-issues Gate 4 |
| OI-142 | the next PET Gate-4 code-gate re-run and receipt re-issue | the row: re-run the owning PET Gate-4 code gate and re-issue its receipt, then apply the preserved one-line narrowing; `atomic_write.py` is still at `71527c2a…` |
| OI-57 | the next Gate-5 launch | the code repair is on main (`a764a72`); the row records that it reaches production only once `CODE_ROOT` is synced or the launch is from a checkout containing it |
| OI-58 | the next Gate-5 re-issue | the row: a future Gate-5 re-issue would restamp the same copied claim, so the fix must ride it; its note-side half is discharged (`app_provenance_pet.tex:44`) |
| OI-61 | whatever Gate-5 re-issue OI-60 rides | the row: both halves ride whatever re-issue OI-60 rides; re-costed 2026-08-17 as touching a hash-pinned file |
| OI-64#2 | the next Gate-5 launcher, or the next edit to `reconcile_gate5_family.py` | the row asks for the parity check to be called by those two; neither calls it yet, though other launchers have called it since `d0c42bddf` |
| OI-94 | the PET extraction-stage subtraction landing, and only if PET C_stat is reconsidered | the row's action is 'once the subtraction lands'; reconsideration needs estimator-equivalence plus coverage (`DECISION-20260902` R6) |
| OI-133 | the next data-only launch, or a ruling on the artifact-schema change | the row: the durable fix is awaiting a ruling because it changes the artifact schema |
| OI-138 | Gate 6 being picked up again | the row's owner is whoever picks Gate 6 up next; Gate 6 is BLOCKED (`AGENTS.md`) |
| OI-182 | the next legitimate change to `extract_fullevent_fps.py` | the row: bundle the rename with that change; the file is still at `de0f044b…` with 23 pins |

## OI-65#2 (lane C's) — retired

The row's live remainder was that the repaired `reconcile_gate5_family.py` *"has never run against the campaign, because
that needs a deployment"*. That stopped being true on 2026-08-14:
`state/gate5-family-complete-pass-20260814.json` (`bed45a359`) records deployment parity *"2 of 2 CURRENT"*,
checked in the same turn as the run, and a full-strength run with verdict `FAMILY_COMPLETE_PASS`: 50 of 50 targets and
50 of 50 trainings passing. Its R1–R4 repairs are each marked DONE in the row. The receipt itself says it neither
constructs `C_stat` nor promotes Gate 5, and that boundary stands.
<!-- absence-ok: the paragraph quotes the row's superseded claim in order to refute it with the 2026-08-14 receipt -->

## Dependency check

`git grep -E "OI-<n>([^0-9]|$)"` over KNOWN_ISSUES, the DECISION, RULING, AUTHORIZATION and OPERATIVE records, and
`docs/publication/` returns 0 hits for every item here (for OI-64 and OI-65, using the bare number).

No row text is deleted. Each changed row gains a dated prefix pointing here.
