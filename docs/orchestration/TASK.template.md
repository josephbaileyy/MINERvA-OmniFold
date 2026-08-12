# Task `[ID]`: `[bounded question]`

## Required reading

`docs/orchestration/FINDINGS.md` — the `BEN-*` ledger of how agents on this campaign fail. One line per
finding, ~13k tokens; read it in full. For the full text of any row:
`grep -n 'BEN-0XX' docs/orchestration/FINDINGS-ARCHIVE-2026-08.md`.

**Name here the specific `BEN-*` ids this task is most likely to re-trigger.** Across the 83 dispatch
prompts committed before 2026-08-12, `FINDINGS.md` was cited zero times and no finding was ever cited to
a worker — while the ledger accumulated repeat entries (`BEN-138` reached a fifth instance, `BEN-094`
recurred as `BEN-134`, `BEN-115` was amended three times). A ledger nobody is pointed at does not
prevent anything. (BEN-200.)

## Proposition

State one falsifiable claim.

## Inputs and owned paths

List exact read-only inputs and the worker's unique writable worktree/output directory.

## Required method

Specify the method or independent formalism so parallel workers do not merely duplicate one another.

## Acceptance and kill tests

Give numerical tolerances and the observation that would refute the claim.

## Required report

Use the repository `AGENTS.md` final-report format. Include exact reproduction commands and provenance.

