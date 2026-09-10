# PET typed-descriptor status

PET typed descriptors remain diagnostic and method-development infrastructure.

## R1 software smoke

**PASS — trainable-adapter software smoke only.** The uncapped, CPU-only Keras adapter has passed its synthetic contract, gradient, masking, serialization, and fresh-process reload tests. It is not production-integrated, production-normalized, trained, or scientifically evaluated.

## Prong contract repair — schema v2

**PASS — local synthetic software validation, 2026-09-10.** The prong contract
now uses raw charge categories `0, 1, 2`, applicable only when raw PID is valid
and equals 3. Muon code 0 stays valid and means undetermined; non-muon fills are
masked. Unexpected codes remain in raw storage and use the unknown-category
channel when applicable. Mass -1 and score -1 are masked independently of token
presence. Prong position/time/four-momentum/dE/dx units are documented from the
correspondence. No physical-unit conversion is performed.

Scores retain their native scale and enter the token model alongside raw PID;
there is no pooled score standardization or common probability interpretation.
Frozen score normalization must be identity. Hypothesis mass remains a
redundant, standardized input with undefined values excluded from fitting;
it is not an independent measurement. The vocabulary retains code 9 without
asserting that released tuples emit it.

**Membership policy for this repair:** retain every raw prong row, including
prong zero and unknown/unfilled rows, with field masks and the existing
structural presence flag. Prong zero stays in the permutation-invariant pool;
the event-level muon remains separate. No role feature, primary-prong removal,
energy/score cut, or hypothesis-selection algorithm is introduced. Choosing a
different representation requires a later declared comparison. The default
output remains 13 event columns plus 51 descriptor columns in both controls.

`pet-typed-descriptors-v2` binds these semantics in the schema digest. The
reader rejects v1 shards and frozen normalization; Keras rejects stale schema
digests in configs and saved models even when tensor widths agree. Existing
v1 evidence remains historical and must be read with its original contract.
No v1 artifact or receipt was rewritten, relabeled, or replayed as v2 evidence.

Validation: 52 tests and 10 subtests passed on synthetic inputs, including
NumPy/Keras feature agreement, raw-row preservation, masks, native scores,
serialization, fresh-process reload, trainable gradients and matched controls.
The source-smoke tests use fake readers, not ROOT payloads. Test environment:
Python 3.11, NumPy 1.26.4, TensorFlow 2.16.2, Keras 3.15.1, CPU only.
All four new NumPy semantic regressions fail against parent `ae9dfee5` and pass
with the repair; they detect the changed behavior rather than merely checking
the new declaration.

```bash
python -m pytest -q nd-unfolding/tests/test_typed_descriptors.py \
  nd-unfolding/tests/test_typed_descriptor_keras.py \
  nd-unfolding/tests/test_typed_descriptor_source_smoke.py \
  nd-unfolding/tests/test_typed_descriptor_compatibility.py \
  nd-unfolding/tests/test_prong_semantics.py
```

Ruff passes on changed Python files. New test files pass Black and strict
mypy; changed lines in existing files follow Black. Whole-file Black and
strict source typing have pre-existing debt: strict mypy reports the same
54 diagnostics at parent `ae9dfee5` and with this repair, with no added
diagnostics. This is not a claim of a clean whole-package typing check.

## Semantic evidence

**BLOCKED, NARROWED — prong contract repaired; source and broader representation
gates remain open.** Reconstruction-side correspondence recorded
2026-09-10 supplies PID meanings (`3 = Muon`, `8 = Proton`, `13 = EMLikeShower`),
raw muon charge codes, units, hypothesis-dependent score/mass semantics and the
primary-lepton role of prong zero. Definitions, source qualifications, code
impact and follow-up questions live in
[PRONG_BRANCH_SEMANTICS.md](PRONG_BRANCH_SEMANTICS.md). Exact source-release
applicability remains unverified, and highest-score hypothesis selection is
explicitly tentative. The local repair above supplies no training result.

The bounded 16-data plus 16-MC source sample had exposed a charge-vocabulary
mismatch, raw-row versus filtered-object membership differences, and conflicting
downstream PID interpretations. The correspondence explains the charge codes
and supplies a reconstruction-side PID dictionary; it does not choose the
object membership policy. The historical packet remains evidence for its exact
observations, not the source of the new definitions.

The fixed-sample measurements, external source versions, exact digests, and non-claims are recorded in `docs/orchestration/PACKET-20260901-pet-typed-descriptor-semantic-evidence.md`. The deterministic probe and JSON output are archived under `docs/orchestration/runs/pet-typed-semantic-evidence-20260901/`.

The 32-row packet does not support photon three-state rates, cross-playlist claims, blob structural-zero rates, or broad prong findings. Surviving M60 raw artifacts are preserved as a distinct, unrouted layer under `docs/orchestration/runs/pet-typed-semantic-evidence-20260901/m60/`; they are not imported into the fixed-sample result.

## Control contract

- `C0` and `C1` both use `m_reco(num_evt=64)`.
- `C0` disables every typed family, so all 51 descriptor columns are exactly zero.
- `C1` enables the same 51 descriptor columns.
- The 13-wide event-only bypass is contextual only; it is not the footing-matched `C0` control.

## Unresolved gates

- release-specific provenance, hypothesis selection, and remaining photon/blob
  semantics and calibration;
- raw-row versus filtered-object membership, primary-lepton treatment, and
  associations/overlap between object families;
- production normalization;
- raw-count scaling;
- multiplicity-dependent segment-sum magnitude.

## Next bounded task

**Protocol prepared, 2026-09-10; source execution remains unapproved.**
[SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md](SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md)
pins the data/MC identities and proposes entries `[0,4096)` from each file,
with explicit mechanical, semantic and release verdicts. It specifies a
single-file training reco-MC normalization pilot, historical-anchor exclusion,
event-group split, valid-only statistics, score identity scaling and acceptance
thresholds. A bound `pass_reco` sidecar is still required; the source mapper's
75 branches do not supply that selection.

Current raw-row membership and sum/raw-count pooling remain implemented.
Masked-mean pooling with a scaled log count is proposed for a later diagnostic
pilot; it requires versioned configuration, implementation and synthetic checks
before real-input use. No production normalization or pooling readiness is
claimed. Photon/blob provenance, overlap and primary-lepton redundancy remain
explicit questions.

The next decision is the named, bounded source-audit authorization in the
protocol's budget table, after its launcher and raw-preserving checker are
prepared and bound. The existing fixed 16-entry smoke runner is not a launcher
for the proposed 4,096-entry audit. Normalization and matched C0/C1 training
have separate prerequisites, proposed ceilings and authorization boundaries.
Preparation does not permit ROOT access or scientific training. Do not repeat
the prong repair or completed bootstrap/containment probes, or revive Gate 6.

This status authorizes no training, compute, Gate-6 action, `C_ML` construction, or publication claim.
