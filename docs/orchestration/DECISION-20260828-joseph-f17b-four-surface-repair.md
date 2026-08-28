# DECISION 2026-08-28 — approve the bounded F-17(b) four-surface repair

## Authority and scope

Joseph approved `PROPOSAL-20260828-f17b-four-surface-repair.md` in the Codex task on 2026-08-28:
*“I approve this.”* The approval authorizes exactly the four repair surfaces in that proposal, their
tests, the required pin supersessions and MANIFEST coupling, and the required fresh independent
full-chain grade.

It does **not** authorize a far-end run, a new rehearsal, scientific compute, scheduler mutation,
covariance construction or adoption, a Gate-2 status change, or a publication claim. Even a
post-repair **FIT** authorizes only a proposal for a new forward-only rehearsal. Gate 2 remains
**FAIL**, readiness remains **NOT READY**, and no scalar-5D covariance is adopted.

## Implemented surfaces

| # | Surface | Implementation |
|---|---|---|
| 1 | Real measurement wall-clock | `measure_m1_m6.py` emits `started_utc` and `completed_utc`; `compare_m1_m6.py` requires, validates and carries the interval. |
| 2 | Detached-or-branch identity | The measurer emits structured `branch` / `detached` / `not-a-git-checkout` state; the comparator requires, validates and carries it without re-observing the tree. |
| 3 | Preserver digest bracket | The shell takes full sha256 values immediately around the preserver invocation and refuses on movement. |
| 4 | Immediate measurer short-circuit | A nonzero measurer rc now exits inside the loop before another measurement or the comparator can run. |

The comparison record schema and instrument version move from `1` to `2`. Predecessor measurement
documents lacking the producer-captured identity fields are refused rather than silently upgraded.
The measuring-instrument digest remains an explicit input-schema gap because it was outside the
approved repair.

## Dated pin supersessions

These are successor rows, not edits to the historical pins. Both old values remain where originally
recorded so they continue to identify the bytes to which those records referred.

| Date | Pin location | Old content sha256 / bytes | New content sha256 / bytes | Reason |
|---|---|---|---|---|
| 2026-08-28 | `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` §11 | `c40e6b54…` / 15722 | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` / 16358 | Approved surfaces 3 and 4 changed `measure_k0_farend_f1b_f17b.sh`. |
| 2026-08-28 | `receipts/RECEIPT-20260825-terminal-watch-f17b-durability.json` `files` | `2132194fe1a3ed7a420f19b7b8b7d2f23fed873c12c316fc525a85b11a1253a2` / not recorded | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` / 16358 | The older receipt pin was already superseded in fact; this approved repair supplies the dated successor without rewriting it. |

The other repaired instrument hashes for the independent grade are:

| Artifact | Post-repair content sha256 / bytes |
|---|---|
| `measure_m1_m6.py` | `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51` / 14108 |
| `compare_m1_m6.py` | `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242` / 67440 |

## Validation and remaining gate

The implementer ran the named affected suites: **100 tests, OK**; Python compilation, `bash -n`,
and `git diff --check` also passed. These are implementation controls, not the independent grade.

The repair is not fit for prospective use until a fresh reviewer who is neither the implementer nor
`agy-capacity-probe` grades the whole coupled chain against
`SPEC-20260825-f17b-tree-comparison-instrument.md`. The grade must use fixtures only and must not run
`measure_k0_farend_f1b_f17b.sh`, submit a rehearsal, launch compute, or change a gate.
