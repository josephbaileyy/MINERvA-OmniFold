# RECORD — four unassigned tooling items retired from the backlog (2026-10-28)

The close-items session retires four unassigned backlog rows whose next actions are already done
in code. All four are repository tooling, none is promoted, and none touches publication. This
follows the backlog triage the director routed to this session on 2026-10-28. Measured at
`c3a812087`.

| Item | Next action in the source row | Discharged by | Measured now |
|---|---|---|---|
| OI-10 | Rename `hasTruthOnlyMisses` or give it the correct merge mode | `bce7fa4b` + `af542919` (2026-09-23); `KNOWN_ISSUES.md` row 8 **FIXED** | row 8: all 13 event-loop TParameters are classified, and `hasTruthOnlyMisses` stays summed by design, with its count readers pinned by `nd-unfolding/tests/test_evloop_tparameter_merge_modes.py`. The rename is recorded there as cosmetic. |
| OI-180 | Repair the auditor's docstring stripper, then triage what the repair reveals | the repair: `docs/orchestration/audit_gates_that_cannot_fail.py:36` imports `tokenize`; the triage: the `OI-182` row | `OI-182`'s row records the triage of the four findings (filed 2026-08-31 *"while triaging the four findings the `OI-180` stripper repair revealed"*). `OI-182` stays open for the one real finding. |
| OI-64#1 (lane A's) | `verify_hash_bindings.py` guards nothing; sub-parts (f) erosion and (g) the zero-margin launch-code floor | the gate runs in the hook (`.githooks/pre-commit`, "receipt+shell hash bindings") and in CI (`record-checks.yml`). (f): `84607aa3b` replaced the scalar floor with an exact count-and-digest identity (`verify_hash_bindings.py:189-199`). (g): `test_hash_bindings.py:75` records `_LAUNCH_CODE_FLOOR = 2` replaced 2026-08-13 by a per-family assertion. | `test_gate3_and_gate4_launch_code_freezes_specifically` asserts every launch-code family has a live receipt |
| OI-65#1 (lane A's) | Two receipt-retirement predicates could diverge | its own 2026-08-13 update: the dependency is gone, because a whole-tree gate needs no liveness predicate | the row ends: *"Remains an exposure with no known instance and no live dependency: close it or leave it, but do not spend on it."* |

**Dependency check.** `git grep -E "OI-<n>([^0-9]|$)" -- KNOWN_ISSUES.md 'docs/known-issues/*'
'docs/**/DECISION-*' 'docs/**/RULING-*' 'docs/**/AUTHORIZATION-*' 'docs/**/OPERATIVE-*'
'docs/publication/**'` returns 0 hits for OI-10, OI-180, OI-64 and OI-65. `KNOWN_ISSUES.md` row 8 cites
the OI-10 subject by its own number and is FIXED.

**Collision rows.** OI-64 and OI-65 each have two rows: lane A's (`#1`) and lane C's (`#2`). Only
lane A's are retired here. Lane C's `OI-64#2` (the deployment-parity check with no caller) and
`OI-65#2` (the `reconcile_gate5_family.py` audit repair) stay active and are not judged here.

No row text is deleted. Each retired row gains a dated prefix pointing here.
