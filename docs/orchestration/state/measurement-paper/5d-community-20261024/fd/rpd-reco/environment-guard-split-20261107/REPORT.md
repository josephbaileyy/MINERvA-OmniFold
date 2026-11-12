# RPD-RECO prepare-receipt diagnostics, round 1

The platform prologue at `2cfa1a1e` refused its combined MAT_PREPARE predicate before classification. [Receipt #881](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/881), head `dda96f73`, preserves the parent environment and worker trace, but explicitly says the worker environment was not captured. The actual differing keys cannot be reconstructed from that receipt. This patch records the comparisons for the next fresh prologue; it does not identify or remove the platform mismatch. <!-- absence-ok: Diagnostic availability is explicitly recorded in #881, not inferred from a search for scientific results. -->

The same receipt settles C4a: the real MAT setup returned with errexit, nounset and pipefail enabled. [The combined audit](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6703512638) closed C1–C4. Both shell wrappers remain unchanged by this round.

The executable verification head is `7a1b5d0cd415a739a2bef0588446593be185e95d`. SOURCE-IDENTITIES.json binds all eight executable files to that head. The full runner outputs and their counts are recorded in VERIFICATION.json, SUITE.txt, MUTATIONS.txt and MUTATIONS.json.

## Named comparisons

The combined predicate is split into six independently tested guards:

| Guard | Recorded comparison |
| --- | --- |
| MAT_PREPARE_PRESENT | Required receipt fields and observed fields |
| MAT_PREPARE_RUN | Prepared and current run paths |
| MAT_PREPARE_CONNECT_PRESENT | Required presence and observed presence of the current connect ID |
| MAT_PREPARE_CONNECT | Prepared and current connect IDs |
| MAT_PREPARE_AGE | Prepare timestamp, current timestamp, measured age and exclusive bounds |
| MAT_PREPARE_ENVIRONMENT | Reviewed exclusions and added, removed and changed keys, with both display values for changed keys |

All available comparisons are collected before a predicate refuses. Refused carries the diagnostic values into ordinary step STOP records. The traced prologue worker also writes prologue-worker.STOP.json and prints the redacted details to captured stderr before exiting. It still cannot publish a passing prologue receipt after refusal.

Environment snapshots retain the existing credential-redacted display values and per-value SHA-256 fingerprints. The fingerprints compare the exact values even when both display strings are redacted; changed credentials therefore refuse without printing their contents. A separate display-consistency diff detects inconsistent display fields within a receipt.

## Full environment, fixed exclusion policy

The exclusion list remains exactly `{_}`. Its code comment identifies the shell-maintained last-command value. There is no include-list and no newly excluded key. Every other added, removed or changed key refuses. Loader, Python, ROOT/cling and cppyy families are explicitly forbidden in the exclusion policy; required mutants attempt to add LD_PRELOAD, PYTHONPATH and ROOT_INCLUDE_PATH.

The recorded duplicate PlotUtils segment in ROOT_INCLUDE_PATH and the recorded NERSC_PYMON_UUID are hypotheses about the platform failure, not findings. This round leaves ROOT import order and process launching unchanged. If the next real diff identifies a repeated protected path, that path must be fixed at its source rather than excluded. A process-local monitoring-key exclusion would require both the diff and its setter source, followed by review.

Tests exercise an identical environment with a changed excluded key, changed LD_LIBRARY_PATH, added LD_PRELOAD, removed PLOTUTILSROOT and changed credential values. Each named sub-guard has a required mutant. The original MAT_PREPARE presence and trace-policy checks retain explicit missing-receipt and altered-policy tests. The comment-only custody control remains part of the full harness.

The new fingerprint field requires a fresh prepare at this head. Reusing the earlier #881 prepare refuses MAT_PREPARE_PRESENT; that earlier evidence is preserved unchanged. After delta audit, the run lane reruns the complete prologue wrapper in a fresh run directory with reviewed configuration paths. This produces the worker diff that round 2 will use.

## Scope and terminal conditions

Owner: Codex2 for code and local fixtures; independent reviewer: coverage-5b-audit; platform executor: limitation-resolver. The decision for round 1 is whether each boundary records its compared values and preserves strict environment coverage. Its terminal condition is passing local verification, committed receipts and the delta audit. The review budget is this requested diagnostic round plus concrete findings. Round 2 depends on the platform diff and is a separate code decision.

SCIENTIFIC-AST-CHECK.json compares the ten previously pinned scientific functions with `2cfa1a1e`. AST identity is a code-scope check, not scientific validation. The producer's RNG, stream layout, aggregation, readings and P-F meaning retain their bound definitions. No cluster contact or scientific production run is part of this lane. The production config remains DRAFT, and the full flux connect stays held for the ordered review and platform gates.

## Local verification

At the frozen executable head, the suite printed **170 passed in 389.15s**, the comment-only custody control printed **170 passed in 389.12s**, and the harness printed **159 required, 159 executed, 159 killed, complete/all_killed true**. All returned 0. Black, Ruff, strict mypy and both shell syntax checks passed. The current source commit passed 24 repository hooks; its record-checks CI passed. These are local code measurements and do not establish native MAT startup, the actual environment diff, real MnvH1D shutdown or flux-connect readiness.
