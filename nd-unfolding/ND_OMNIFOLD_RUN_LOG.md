# N-D OmniFold run log

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
