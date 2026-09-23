# Active process-evidence index

The complete pre-freeze casebook and every long-form finding live at
`evidence/prepublication-2026-08-20-0b329e8a`. Recover an indexed row with:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDINGS.md | rg '<BEN-ID>'
```

This file retains only BEN identifiers used by the active generated playbook. `PLAYBOOK.md` owns the
current operating rule and observable check; the tag owns the complete evidence and chronology.

The allocation table remains machine-readable because the merge guard derives ownership from it. Full
allocation rationale is frozen at the evidence tag; new allocations still require a fetched-remote
freeness check and a closed ten-block claimed with its first filing.

**`530-539` freeness check, 2026-08-24.** `git fetch origin`, then this file's own allocation tail
read at every one of the 43 refs under `refs/heads`, `refs/remotes` and `refs/tags` — all 43 carry a
`FINDINGS.md`, so the search covers the ref set rather than a sample. 39 refs read `unallocated 520+`
and 4 read `unallocated 530+`; none allocates any id in `530-539`. The block is claimed here with its
first filing (`BEN-530`).

| lane | block |
|---|---|
| pre-block era | `001-089` |
| D — verifier | `090-099` |
| B — uncertainty | `100-129` |
| C — PET | `130-159` |
| D — verifier successor | `160-189` |
| A — orchestrator | `190-199` |
| repository infrastructure | `200-209` |
| A — orchestrator continued | `210-229` |
| C — PET continued | `230-239` |
| B — uncertainty continued | `240-249` |
| D — verifier continued | `250-259` |
| receipt repair | `260-269` |
| Gate-6 Leg 0 | `270-279` |
| P5A extraction repair | `280-289` |
| OI-120(c) repair | `290-299` |
| mediator | `300-309` |
| executor | `310-319` |
| propagation correction | `320-329` |
| OI-124 disposition | `330-339` |
| diagnostic review | `340-349` |
| PET verification | `350-359` |
| fold-forward closure | `360-369` |
| hook dispatch | `370-379` |
| quarantine provenance | `380-389` |
| seconding | `390-399` |
| C — PET third block | `400-409` |
| quarantine provenance second block | `410-419` |
| C — PET fourth block | `420-429` |
| mediator second block | `430-439` |
| seconding second block | `440-449` |
| D — verifier second block | `450-459` |
| C — PET fifth block | `460-469` |
| quarantine provenance third block | `470-479` |
| B — uncertainty third block | `480-489` |
| storage migration | `490-499` |
| fixture-decoy block — do not allocate without exact review | `500-509` |
| remedy-(A) verification | `510-519` |
| review-round governance | `520-529` |
| C — PET sixth block | `530-539` |
| unallocated | `540+` |

## Long-form findings index

All pre-freeze long forms are indexed by the frozen `FINDINGS.md` at the evidence tag.

Four pre-freeze long forms remain in the live checkout: three because the canonical-designation guard inventories
their paths, and one because hash-pinned runtime diagnostics route to it. All other long forms are
recovered from the frozen index.

| retained long form | route |
|---|---|
| `FINDING-20260730-event-feature-nonfinite.md` | Retained for hash-pinned runtime diagnostics; exact full evidence also exists at the evidence tag. |
| `FINDING-20260807-checkpoint-is-not-the-trained-model.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-step1-under-achieves.md` | Full evidence row at the evidence tag. |
| `FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md` | Full evidence row at the evidence tag. |

Post-freeze long forms (filed after the 2026-08-20 evidence tag) live only in the live checkout and
are indexed here. Each row is a title, not a summary of its result: read the file's own `CITABLE FOR`
/ `NOT CITABLE FOR` lines before quoting it.

| post-freeze long form | subject |
|---|---|
| `FINDING-20260822-a-hold-that-instructed-its-own-deletion.md` | A governing hold document instructed its own deletion and was router-inert for its whole life; the hold file it concerns is preserved unchanged as evidence. |
| `FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md` | Clause (c) of the B1 steps (4)/(5) member pause cannot be satisfied through the real launcher path as written. |
| `FINDING-20260824-five-rules-from-the-r5-night.md` | Evidence home for `BEN-530`–`BEN-534`: five process defects from the OI-126 R5 night and the playbook amendments they justify. |
| `FINDING-20260824-gate2-preparation-and-four-open-rulings.md` | Gate-2 clause list with per-clause settling instruments, and four questions about what Gate 2 means that a lane may not answer. |
| `FINDING-20260828-ben-citations-resolve-only-at-the-evidence-tag.md` | Measurement of how many source `BEN-*` citations resolve only at the evidence tag. |
| `FINDING-20260828-oi136-guard-provenance.md` | Provenance of the `OI-136` import guard (`nd-unfolding/mnv_guarded_run.py`), moved out of its docstring. |
| `FINDING-20260828-polish-pass-residue.md` | What the 2026-08-28 polishing pass did not touch, and why. |
| `FINDING-20260829-f17b-deferred-surfaces-and-stale-freeze-prose.md` | Surfaces the 2026-08-29 F-17(b) test-hardening pass deferred, and freeze prose the freeze's expiry stranded. |
| `FINDING-20260830-k0-member-namespace-blocks-submission.md` | Measured state of the k=0 member namespace after the `aa67c426` rehearsal and its consequence for the seven-arm submission. |
| `FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md` | Why the seven k=0 arms of run `k0-7ac0edec-20260830T000215Z` died on `env-pathcheck`. |
| `FINDING-20260830-quarantine-nocompute-legs-measured.md` | The 2026-07-12 quarantine's no-compute legs measured at `32e403b8`; regrades nothing. |
| `FINDING-20260831-ben039-detector-is-triple-bound.md` | The `BEN-039` `tautological-datum` detector is bound on three axes; folded into `OI-179`. |
| `FINDING-20260831-strip-noncode-inverts-on-a-closing-triple-quote.md` | `audit_gates_that_cannot_fail.py`'s comment stripper misreads a closing triple quote; corrects the triple-bound finding above. |
| `FINDING-20260901-cause4-jitter-floor-recovered.md` | Cause 4's jitter floor recovered, and a ledger value that describes a product no longer present. |
| `FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md` | The F7 predeclared test measured on the candidate, with the seed-ensemble pull. |
| `FINDING-20260901-k0r2-redeploy-precondition-delta.md` | Per-launcher precondition delta of the `7ac0edec` → `main` redeploy for the remaining k=0 arms. |
| `FINDING-20260901-p-leg-status-measured-against-the-candidate.md` | Status of the quarantine `P` leg read off committed receipts for the candidate. |
| `FINDING-20260901-pscratch-read-stalls-block-a2b.md` | Intermittent pscratch read stalls make `A-2(b)` unmeasurable. |
| `FINDING-20260906-cause3-scan-execution-composition.md` | The cause-3 fixed-draw scan's execution declaration composes into defects; remedies are proposals only. |
| `FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` | The R5 spend meter under-counted requeued execution attempts; the required `sacct` query and receipt schema 2. |
| `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md` | The two projection builders agree on weights and disagree on refusal; amended the same day. |
| `FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md` | `R5` attempt identity is not stable across `sacct` queries; an accounting-instrument finding. |
| `FINDING-20260919-build-time-cv-held-fixed-is-not-the-spec-condition.md` | The build-time `cv_held_fixed` test measures a different proposition than its name; disclosure, not a repair. |

| id | frozen evidence |
|---|---|
| BEN-023 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-025 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-026 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-027 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-028 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-035 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-074 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-077 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-080 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-082 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-119 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-191 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-193 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-199 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-205 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-214 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-228 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-300 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-304 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-305 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-312 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-322 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-323 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-328 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-331 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-335 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-383 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-387 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-392 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-398 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-410 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-454 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-455 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-456 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-468 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-476 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-477 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-478 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-482 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-483 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-484 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-520 | Post-freeze. Evidence: `docs/orchestration/GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`, `docs/orchestration/GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md`, `docs/orchestration/GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md`, `docs/orchestration/DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md`. |
| BEN-530 | Post-freeze. A bar calibrated against one noise source is silent about a second, not conservative about it. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-530); `docs/orchestration/state/RECEIPT-20260823-oi126-r5-loss-interpolation-sweep.json` per-member `dL_rowset_max_dev`; retraction at `7da3b3d6`, strike at `74cee642`. |
| BEN-531 | Post-freeze. A discriminating test publishes its endpoint separation, the residual it must resolve, and its size under its own null BEFORE it runs. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-531); `docs/orchestration/state/RECEIPT-20260823-oi126-r5-loss-interpolation-sweep.json` key `C2_DISCRIMINATOR_20260824`; job `57507676`. |
| BEN-532 | Post-freeze. ssh ControlMaster multiplexing pins repeated connections to one login node, so a process list answers about that node and reads as corroborated. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-532). |
| BEN-533 | Post-freeze. Another lane's scheduler state is not yours to act on, and `squeue --me` returns the whole shared account. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-533); duplicate job `57506433`; foreign job `57275989` in the same `--me` output. Ruled by Joseph 2026-08-24. |
| BEN-534 | Post-freeze. A hold is a property of the branch, not of restraint: five commits described as held published as ancestors of another lane's push. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-534); `9a881c03`, `82cac45f`, `87310615`, `bc76ac6c`, `0e53f962` under `origin/main`. |
| BEN-535 | Post-freeze. A power or leverage gate can be valid in ONE direction and written as if symmetric, and then it blocks the correct read: a small separation-to-spread ratio is evidence FOR consistency and forbids only the opposite conclusion. Found by the very next run after the rule requiring such gates landed. Evidence: `docs/orchestration/state/RECEIPT-20260824-oi126-c-permutation-ensemble.json` key `READING_20260824.MY_PREDECLARED_POWER_GATE_IS_ONE_DIRECTIONAL_AND_IT_OVER_REFUSED`; job `57517628`, leverage 1.58 against a declared 2.0. |
