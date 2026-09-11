# N-D OmniFold run log

## 2026-09-11 — CFS preservation and documentary follow-up

The completed PET source-audit output at `30de7f64` now has a verified CFS copy.
All 16,915 files (283,225,129 bytes) were copied after checking all 16,899
receipt-bound artifacts and four accounting-bound auxiliary files. Destination
readback hashes equal the complete source inventory both before and after the
copy. Scratch was retained; no ROOT source was opened. Exact paths, executable
preserver, inventory hashes and recovery procedure are in
`pet/SOURCE_AUDIT_PRESERVATION-20260911.md` and its linked committed records.

`pet/SOURCE_AUDIT_SEMANTIC_FOLLOWUP-20260911.md` traces the 10,000 ns premise to
the curated correspondence and notes that the existing proposed group split
already keeps repeated keys together. It includes an unsent producer inquiry
for time semantics, row granularity, release and object provenance. No bounds,
verdicts, grouping rule, selection, normalization or training changed. Mapping
PASS, semantic DISCREPANCY and the unresolved release/object-family gates stand.


## 2026-09-10 — repaired PET real-source audit

Under Joseph's single-attempt grant, recorded verbatim in
`pet/SOURCE_AUDIT_REPAIRED_AUTHORIZATION-20260910.md`, the audit ran from a clean detached clone
of `ca34a03a` (bindings `fea412de…`, authorization JSON `4e1b9b85…`). It ran on Perlmutter
allocation `58186616`: `shared_interactive`, 2 CPUs requested and 6 reserved, 8 GiB, 15 minutes.
The step used two CPUs. Allocation and step are both `COMPLETED 0:0`, elapsed 7 minutes 55
seconds. Before source access, cluster-main freshness was `FRESH`, the queue was empty,
`--check-preparation` passed, and the runtime pins and output-root absence were verified.

The audit read the data and MC sources over entries `[0,4096)` with 75 branches: 8,192 rows and
512 chunks, no exceptions, empty logs. Peak observed usage was four threads and 1,219,506,176
bytes RSS; output was 283,206,787 bytes. Verdicts:

- `mapping=PASS`: all six mandatory checks.
- `semantic=DISCREPANCY`: five finite `prong_time` values above 10,000, at data entries 2121,
  2704, 3418 and 3867 and at MC entry 3654. Every other correspondence check passes.
- `release=RELEASE_UNVERIFIED`.
- All four object families `UNRESOLVED`.

Records:

- `accounting.json` SHA-256: `3bb911e6be1e83209c94a0d47ed6f79ddaddd85d84998444913cfcd591a49543`.
- `receipt.json` SHA-256: `5e8d545b6a8b45ed1872852417c13518472b0fbb07832faf78c39406e153b3da`.
- All 16,899 receipt-bound artifacts were rehashed remotely with no mismatch.
- The transferred subset matches its remote digests. It is preserved under
  `pet/source_audit_runs/20260910-repaired/` with `preservation-manifest.json`.

This is fixed-source diagnostic telemetry. No normalization, training, covariance, retry or
Gate-6 action followed. The grant is consumed. `VALIDATION_LEDGER.md` is unchanged because no
ledger-class quantity was measured.

## 2026-09-10 — complete synthetic runtime preflight

Preparation `ca34a03a` installs the authorized four-thread ceiling and compares
identical prepared features and weights against float64 rounding budgets. Linux
allocation `58178592` and its two-CPU step both complete with exit `0:0`; all
8,192 fake rows and 512 typed chunks pass. Peak observed process resources are
four threads and 993,112,064 bytes RSS. The scheduler rounds the two-CPU request
to six reserved CPUs with 8 GiB memory, within the standing reservation ceiling.
Elapsed allocation time is 5 minutes 11 seconds. The unchanged import guard
reports no foreign-checkout imports. ROOT is imported but no ROOT source opens.

`pet/runtime_runs/20260910/linux-roundoff/preservation-manifest.json` binds the
closed receipts, runtime summary, launcher scripts, scheduler and clean-checkout
records. Transfer digests and complete contiguous entry lists were checked;
`verification.json` records that scope. The source launcher's final accounting
writer is not exercised by this fake-reader probe. The 67-test audit suite and
source lint, formatting and targeted strict typing checks pass. This completes
synthetic runtime validation only; another source run still needs a separately
bound authorization. PET pairing, covariance and Gate-6 restrictions are unchanged.


## 2026-09-10 — synthetic runtime investigation

`f59d8170` adds a full fake-reader runtime preflight; `10deb714` reports
numerical differences and samples resources after failed forward checks. The
local SciPy 1.16.3 environment completes all 8,192 synthetic rows. Linux job
`58168872` clears imports but fails forward agreement; job `58174544` measures
the same discrepancy with both oneDNN settings and four process threads against
the two-thread ceiling. Both allocations are terminal. The original thresholds
and guard remain intact; no source-read or scientific acceptance follows.

`pet/SOURCE_AUDIT_RUNTIME-20260910.md` records the diagnosis, exact synthetic
qualification and pending contract decision. Receipts, guard inventories and
scheduler observations are preserved under `pet/runtime_runs/20260910/`, bound
by its preservation manifest. No ROOT source access, fitting or training occurred.


## 2026-09-10 — bounded PET v2 source audit interrupted

The attempt at `58832843`, authorized by
`pet/SOURCE_AUDIT_EXECUTION-20260910.md`, stopped at the first data row when the
import guard refused NumPy testing utilities launching `lscpu`. No complete
receipt, accounting file or typed shard exists. Allocation `58164405` is
`COMPLETED`; source step `.2` is `FAILED`, exit `3:0`.

The original partial artifacts, remote hash comparison and scheduler observation
are bound by `pet/source_audit_runs/20260910/recovery-manifest.json` and explained
in `pet/SOURCE_AUDIT_INTERRUPTION-20260910.md`. The runtime repair and its tests
are local software preparation; there was no additional ROOT read, allocation,
normalization or training. Further source execution requires a newly bound grant.


The complete pre-compaction chronology is frozen at
`evidence/prepublication-2026-08-20-0b329e8a` under this exact path:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md
```

Read `ND_OMNIFOLD_STATUS.md` for current scalar/PET/FPS state,
`PET_UQ_REMEDIATION_STATUS.md` for the live PET DAG, and `VALIDATION_LEDGER.md` for verified
numbers. The tag is historical evidence, not scientific adoption.

## Post-freeze chronology

Append only committed post-2026-08-20 events here; keep current state in the owning STATUS file.

### 2026-09-10 — Prong correspondence and typed-descriptor continuation

Recorded Carlos Pernas's reconstruction-side explanation in
[PRONG_BRANCH_SEMANTICS.md](pet/PRONG_BRANCH_SEMANTICS.md), preserving the
difference between stated definitions and tentative expected code support,
hypothesis selection and release applicability. The record explains the PID
and charge conflict, missing-value handling, score/mass interpretation,
primary-lepton role, dedicated particle branches and P7/P8 provenance.

[TYPED_DESCRIPTOR_STATUS.md](pet/TYPED_DESCRIPTOR_STATUS.md) routes the next
proposed task: repair the prong contract and validate it locally with synthetic
fixtures before source validation or training. The older fixed-sample packet
gains a forward pointer; its measurements and scope remain unchanged. The
adapter and semantic-evidence branches were measured as already integrated at
base `d147880f`, so the documentation continues on `pet-prong-semantics` from
that base.

Documentation only: no source access, probe, training, covariance construction,
schema implementation or scientific result. No validation-ledger row is added.
The scalar publication task and the `OI-126` PET disposition are unchanged.

### 2026-09-10 — Prong contract v2 local repair

Implemented the next task recorded at `ae9dfee5` on `pet-prong-semantics`:
muon-only raw charge applicability, charge categories `0/1/2`, independent
undefined-mass/unfilled-score masks, documented prong units and native score
scaling alongside PID. Raw-row membership, raw PID storage and the default
51-column descriptor contribution are preserved. Schema v2 rejects v1 shards,
normalization and saved-model semantics instead of silently reinterpreting them.

The synthetic suite passes 52 tests and 10 subtests, including NumPy/Keras
agreement, mask behavior, matched controls, gradients and fresh-process model
reload. Test command, environment and static-check limitations are recorded in
[the typed-descriptor status](pet/TYPED_DESCRIPTOR_STATUS.md). Strict source
mypy has 54 diagnostics both at the parent and after repair, with none added.
No ROOT data were read and no scientific training or compute was launched.

The next proposed preparation is the v2 source-validation and normalization
protocol. This software result does not alter scalar results, the existing
PET statistical pairing decision or publication adoption. No numerical physics
result is added to the validation ledger.

### 2026-09-10 — Typed-descriptor source and normalization protocol

Prepared [SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md](pet/SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md)
from software base `529f26ae` on `pet-prong-semantics`. It binds the two
historical source identities, proposes 4,096 entries per file, separates
mapping acceptance from semantic/release evidence, and states the remaining
photon/blob, hypothesis and overlap questions. The normalization pilot specifies
a single-file reco-MC inventory, historical-anchor reservation, deterministic
event-group split, valid-only fitting and frozen score identity scaling.

The required detector-selection sidecar does not yet have a bound producer;
the 75-branch source mapper cannot supply `pass_reco`. Current raw counts and
sum pooling remain implemented. The proposed mean/log-count representation
needs separate implementation and validation. Source, normalization and later
matched C0/C1 stages have explicit proposed resource ceilings and terminal
non-claims; no execution authorization is inferred from this preparation.

Local checks confirmed the two manifest SHA-256 values, source bindings,
ordered 75-branch digest, v2 schema digest, document links and exact Gate-6
restriction keys. The existing five-file synthetic suite passed 52 tests and
10 subtests in 6.56 seconds in the repair's CPU test environment. These test
results validate the existing adapter, not the proposed pooling implementation
or an inventory-aware fitter. No ROOT file was opened, scientific training
performed or cluster job submitted. Documentation only; no new physics result
or validation-ledger row, and no change to OI-126 or Gate 6.

### 2026-09-10 — Bounded PET source-audit implementation preparation

Implemented the raw-preserving checker and launcher from `34fec047` on
`pet-prong-semantics`. [SOURCE_AUDIT_RUNBOOK.md](pet/SOURCE_AUDIT_RUNBOOK.md)
contains the exact future command, separate authorization-file contract,
metadata acceptance rules, resource limits, digest framing and terminal receipt
specification. [SOURCE_AUDIT_BINDINGS.json](pet/SOURCE_AUDIT_BINDINGS.json)
freezes the implementation dependencies, protocol, branch/schema/source identities,
structural metadata contract and synthetic tests.

The checker enforces the two pinned sources, ordered 75 branches and entries
`[0,4096)` per source. It archives numeric observations before mapping, retains
malformed rows and exceptions, checks typed values/masks against a separate
field table, and keeps mapping, semantic, release and object-family verdicts
separate. Diagnostic forward checks use identity normalization and fixed
reference projectors, with no fitting. A partial failure never backfills,
retries, filters rows or promotes an incomplete shard.

Local CPU synthetic validation: 112 tests and 10 subtests passed across the new
checker tests and the five existing typed-descriptor suites. This includes the
complete 8,192-entry fake-reader path, pre-payload identity/metadata failures,
raw non-finite bytes, malformed counts/vectors/keys, v2 masks, serialization,
NumPy/Keras C0/C1 checks, resource failures and launcher accounting. Black and
Ruff pass for all three new Python files; targeted mypy with
`--follow-imports=silent` passes for the two new source modules. This is not a
whole-package strict-typing claim. The preparation-only launcher check also
passes against the committed-manifest bytes.

No ROOT source was accessed, scientific training performed, GPU used or cluster
compute launched. Native ROOT compatibility and the combined dependency
footprint under the proposed ceilings remain unmeasured. Source execution still
requires its named authorization; normalization and later training retain their
separate prerequisites. No physics result or validation-ledger row is added.
OI-126 and all five exact Gate-6 prohibition keys remain unchanged.


## 2026-09-11 — PET pooled/direct representation preparation

Prepared from remote `pet-prong-semantics` at `57b707b737ce817c1ef8d8bd0f0a39ce4becb7ba`
in a separate checkout, preserving the occupied local branch and its staged changes.
The [report for Ben](pet/direct_token_comparison/REPORT_FOR_BEN.md) separates
measured source telemetry and historical synthetic receipts from proposed choices.
The evidence reproducer verifies 30 historical signal-arm receipt digests.

The new Keras candidate and pooled attention bridge reuse the current family
encoders, field masks and normalization, with identical trainable parameter
shapes. A separate synthetic runner exercises two-step unfolding with ordinary,
injected and shuffled targets. The [setup](pet/direct_token_comparison/README.md)
and preparation validation record bind the local software checks; those checks
are not a scientific closure acceptance or a real-input performance result.

The [bounded execution proposal](pet/direct_token_comparison/EXECUTION_PROPOSAL.md)
is pending approval. No ROOT payload, cluster allocation, real-source fitting,
correspondence, covariance, publication adoption or Gate-6 work occurred.
Release applicability and all four object-family questions remain unresolved.


## 2026-09-11 — PET execution grant recorded; scheduler preflight blocks allocation

Joseph approved the synthetic campaign and the preparation commit/push. The
reviewed package was frozen and pushed at `9d598c083bca742944e30b4079c7390ece2be9d1`
on `pet-direct-token-comparison`, with 12 commit checks passing.

The [preflight evidence](pet/direct_token_comparison/execution_runs/20260911-preflight/)
records that Perlmutter rejects one GPU/eight CPUs/64 GiB, adjusts memory to 38
CPUs, and requires exactly 32 CPUs per GPU for this queue. An eight-CPU control
with lower memory also fails. One GPU/32 CPUs/56 GiB passes `sbatch --test-only`;
no test-only number is a submitted job. No calibration or training allocation
was submitted; campaign GPU spend remains zero.

[Execution status](pet/direct_token_comparison/EXECUTION_STATUS-20260911.md) holds
execution for the [specific resource amendment](pet/direct_token_comparison/RESOURCE_AMENDMENT-20260911.md).
The GPU limit, events, seeds, algorithm and acceptance criteria remain frozen.
The original CPU reservation estimate was wrong; it has not been silently
reinterpreted as an application-thread limit. No source access, covariance,
adoption, real-input training or Gate-6 work occurred.


## 2026-09-11 — Corrected PET resource envelope authorized

Joseph explicitly approved the amendment at `41a21654`: one A100, 32 reserved
CPUs, 56 GiB, total ceilings 290 GPU-hours / 9,296 CPU-hours / 200 GiB, and two
concurrent full jobs. [Exact authorization](pet/direct_token_comparison/RESOURCE_AUTHORIZATION-20260911.md).
Calibration is next; full jobs remain conditional on the existing integrity and
20% headroom gates. All scientific restrictions and no-retry stops remain.


## 2026-09-11 — PET calibration 58198332: technical stop before training

Executed the authorized corrected profile from `106ba9a8`: one A100, 32 reserved
CPUs and 56 GiB. Slurm records `FAILED`, exit `1:0`, 79 seconds: 0.021944 GPU-hours
and 0.702222 reserved CPU-hours. The Linux suite passed 49 tests and 10 subtests
in 39.64 seconds. The calibration process then failed at package metadata lookup
under the unchanged import guard, before GPU validation or training.

[Terminal evidence and accounting](pet/direct_token_comparison/execution_runs/20260911-calibration/terminal.json).
All 13 files / 51,619 bytes were preserved on CFS with matching source-before,
source-after and destination hashes, then independently verified in the local
committed copy. A guard-compatible imported-module version check passes locally.
No full jobs or retry were submitted. The [118-minute retry proposal](pet/direct_token_comparison/RETRY_PROPOSAL-20260911.md)
requires an explicit exception to the agreed no-retry stop. No synthetic learning
comparison, real-data representation conclusion, source access, covariance,
adoption or Gate-6 action resulted.
