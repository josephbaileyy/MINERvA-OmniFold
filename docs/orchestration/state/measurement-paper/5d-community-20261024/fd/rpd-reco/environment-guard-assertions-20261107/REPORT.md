# RPD-RECO: recorded-value and environment comparison tests

The [round-1 audit](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6716924364) is **NO-GO at `3da5ee12a`**. It reproduced 170 passing tests and 159 killed required mutants, but its additional mutants showed that those checks did not establish the recorded values or non-protected-key coverage. That verdict supersedes any readiness inference from the earlier counts. AUDIT-C1-C2.txt preserves the full audit, including its held lows and run-lane condition.

The repair changes only the contract tests and mutation harness. The executable verification head is `91dbf0a7aacd5c3b8beafcd3c4cecc76441c70fd`. SOURCE-IDENTITIES.json binds the eight executable files. PRODUCTION-BYTE-CHECK.json compares the six production/instrument-check files with `3da5ee12a`; they are unchanged. No production predicate, exclusion, ROOT import order, launcher or scientific function is modified.

## Exact recorded values: 848-R1-C1

The named-guard test uses a fixed clock, synthetic environment and independent expected values. It compares the complete STOP details for missing and legacy receipts, wrong run, missing connect ID, different connect ID, expired age and changed environment. This checks the prepared and observed run paths, both connect identities, presence values, timestamps, age, bounds, required and observed field lists, and every environment-diff section.

The legacy case has the field layout of the pre-snapshot prepare used in #881. It requires MAT_PREPARE_PRESENT and the exact required/observed field lists; a KeyError is a failure. Environment tests require the exact observed value for added keys, prepared value for removed keys and both values for changed keys. The credential case requires the redacted display string on both sides and rejects exposure of either dummy secret.

| Audit counterfactual | Required mutant |
| --- | --- |
| X01: run observed side | REQUIRED_PREPARE_RUN_OBSERVED |
| X02: connect observed side | REQUIRED_PREPARE_CONNECT_OBSERVED |
| X03: connect prepared side | REQUIRED_PREPARE_CONNECT_PREPARED |
| X04: current timestamp | REQUIRED_PREPARE_NOW_RECORDED |
| X05: measured age | REQUIRED_PREPARE_AGE_RECORDED |
| X06: changed observed side | REQUIRED_DIFF_CHANGED_OBSERVED |
| X07: added value | REQUIRED_DIFF_ADDED_VALUE |
| X08: removed value | REQUIRED_DIFF_REMOVED_VALUE |
| X17: legacy receipt without snapshot | REQUIRED_PREPARE_LEGACY_SNAPSHOT_REQUIRED |

Additional required mutants corrupt the presence field list, connect-presence value, prepare timestamp and changed prepared-side value. The harness requires exactly one transformed AST site for every new mutant.

## Non-protected keys: 848-R1-C2

Nine comparison-site cases add, remove and change HOME, NERSC_PYMON_UUID and an otherwise unlisted environment key. Each requires MAT_PREPARE_ENVIRONMENT and the exact diff. Each also verifies a silent control in which only `_` changes. The test calls the real comparison through check_prepare_receipt; pinning the exclusion constant alone cannot satisfy it.

| Audit counterfactual | Required mutant |
| --- | --- |
| X11: added values only for protected families | REQUIRED_DIFF_ADDED_NONPROTECTED |
| X12: silently omit NERSC_* | REQUIRED_DIFF_NERSC_COVERED |
| X13: silently omit HOME | REQUIRED_DIFF_HOME_COVERED |

The sixteen new required mutants extend the earlier 159. The earlier protected-family rejection, credential comparison, guard, custody and scientific checks remain in the full run. The exclusion list stays exactly `{_}`. Key coverage in a synthetic test is not evidence that NERSC_PYMON_UUID caused the real platform refusal.

## Run-lane fingerprint condition

Do not commit the raw prologue-prepare.json or fingerprint entries for credential-redacted environment keys. The canonical prepare must stay intact, private and digest-pinned for the worker comparison. Share redacted STOP diagnostics and environment display values instead. If an exported prepare view is needed, identify it as a filtered derivative, name the omitted fields, and record both its digest and the private original's digest. Do not alter the worker's canonical input to make it publishable.

## Scope and next gate

Owner: Codex2 for tests and local verification; independent reviewer: coverage-5b-audit; platform executor: limitation-resolver. This bounded repair answers the two audit blockers: whether changed recorded values and silent non-protected-key filters are detected. Its terminal condition is the full runner outputs, committed receipts and the delta audit; its review budget is this requested repair and concrete findings. No closure of the held lows is claimed.

After GO, the run lane repeats the fresh prologue for the actual worker diff. Round 2 follows that evidence and the cited setter source; no new exclusion is inferred here. The production config remains DRAFT and the full flux connect stays held. This lane made no cluster contact or scientific production run.

## Local verification

At the frozen executable head, the suite printed **185 passed in 324.56s**, the comment-only custody control printed **185 passed in 320.74s**, and the harness printed **175 required, 175 executed, 175 killed, complete/all_killed true**. All returned 0. Black and Ruff passed on the changed tests and harness. Production typing and shell checks are unaffected by exact byte identity with the audited baseline. The source commit passed 21 repository hooks. These are local code measurements and do not establish native MAT startup, the actual environment diff, real MnvH1D shutdown or flux-connect readiness.
