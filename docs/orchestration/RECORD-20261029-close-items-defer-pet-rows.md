# RECORD — PET full-event and other conditional rows deferred to named triggers (2026-10-29)

Backlog candidate 1, batch B, on the director's ruling of 2026-10-29. It follows
`RECORD-20261029-close-items-defer-gate-rows.md` (batch A). Each of these 12 rows was active although its action
matters only at a future event. Most depend on PET full-event work toward publication, which Joseph's demotion of PET
to diagnostic status (2026-08-20; `AGENTS.md`) took off the path. The rest wait on an authorized rerun, the
publication freeze, or the next k=0 rehearsal. A read-only subagent made the first pass. Each trigger here is
phrased from the row, and three were checked against the row's text. Measured on top of batch A.

## Deferred

| item | trigger |
|---|---|
| OI-4 | PET full-event work resuming toward publication: the row's full-event nominal and coherent ensemble are its prerequisites, and neither exists |
| OI-14 | PET closure-test work resuming (the row: re-offer to whoever owns the closure tests) |
| OI-19 | PET full-event publication training being reinstated (the row needs the finalized full-event FPS input for publication training) |
| OI-20 | PET full-event publication work resuming (the row: the publication full-event input and end-to-end nominal are not complete) |
| OI-22 | PET full-event input being used for publication again (the row verifies tests against the final publication input) |
| OI-24 | the PET feature, measurement, nominal and closure gates freezing (the row's own precondition) |
| OI-28 | the full-event FPS measurement and its acceptance diagnostics finishing (the row's own precondition) |
| OI-33 | a decision to run full per-universe PET lateral retraining, meaningful only if PET UQ is reconsidered |
| OI-36 | the next authorized event-loop rerun (the row: add the true-neutrino-energy branch during a future authorized rerun) |
| OI-39 | the PET 5D unified/block covariance comparison being revived (the row names no trigger; the ratio is flagged and not adopted) |
| OI-42 | the publication freeze (the row: classify the untracked cluster paths after the freeze) |
| OI-174 | the next F-17/k=0 rehearsal, or a deliberate decision to edit the pin-bound `measure_m1_m6.py` |

**Not in this batch,** and going to the director as proposals instead:
- touching publication: OI-2, OI-32, OI-34, OI-40;
- waiting on Joseph: OI-3, OI-35, OI-37, OI-60, OI-188;
- read as moot or actionable by the first pass: OI-121, OI-132, OI-47.

## Dependency check

`git grep -E "OI-<n>([^0-9]|$)"` over KNOWN_ISSUES, the DECISION, RULING, AUTHORIZATION and OPERATIVE records, and
`docs/publication/` returns 0 hits for OI-4, 14, 19, 20, 22, 24, 28, 33, 36, 39 and 42. OI-174 has one hit:
`DECISION-20260830-joseph-presubmission-operand-staleness.md:11`, which cites it to explain why `M-3` takes 46 m 40 s.
That is a mention; nothing there waits on OI-174 staying active.

No row text is deleted. Each changed row gains a dated prefix pointing here.
