# PET typed-descriptor status

PET typed descriptors remain diagnostic and method-development infrastructure.

## R1 software smoke

**PASS — trainable-adapter software smoke only.** The uncapped, CPU-only Keras adapter has passed its synthetic contract, gradient, masking, serialization, and fresh-process reload tests. It is not production-integrated, production-normalized, trained, or scientifically evaluated.

## Semantic evidence

**BLOCKED, NARROWED — prong definitions documented; implementation and broader
representation gates remain open.** Reconstruction-side correspondence recorded
2026-09-10 supplies PID meanings (`3 = Muon`, `8 = Proton`, `13 = EMLikeShower`),
raw muon charge codes, units, hypothesis-dependent score/mass semantics and the
primary-lepton role of prong zero. Definitions, source qualifications, code
impact and follow-up questions live in
[PRONG_BRANCH_SEMANTICS.md](PRONG_BRANCH_SEMANTICS.md). Exact source-release
applicability remains unverified, and highest-score hypothesis selection is
explicitly tentative. No code or training result changes with this record.

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

- implementation of the documented prong units, charge applicability and
  field-specific missingness;
- release-specific provenance, hypothesis selection, and remaining photon/blob
  semantics and calibration;
- raw-row versus filtered-object membership, primary-lepton treatment, and
  associations/overlap between object families;
- production normalization;
- raw-count scaling;
- multiplicity-dependent segment-sum magnitude.

## Next bounded task

**Prepare and verify the prong contract repair on a dedicated PET branch.**
The prior adapter branch (`pet-typed-keras-adapter`, head `9064d59f`) and semantic
evidence integration branch (head `462d68be`) are both ancestors of the measured
integration base `d147880f`. Continue from that integrated work rather than
reviving the older Gate-6 branch. This documentation change is on
`pet-prong-semantics`; branch position is a discovery aid, not scientific evidence.

The implementation proposal has the following acceptance criteria:

1. Preserve raw PID identities and unexpected-code diagnostics. Encode raw
   charge codes `0, 1, 2` with an explicit muon-applicability mask; distinguish
   undetermined muon charge from non-muon fills.
2. Document the supplied prong units and mask undefined mass and unfilled score.
   Preserve valid zeros and token presence. State how score handling depends on
   hypothesis type and how redundant hypothesis masses are treated.
3. Specify the primary-lepton role and raw-row membership policy before changing
   either. Keep the unconfirmed hypothesis-selection algorithm out of code.
   Version the semantic contract and reject incompatible saved normalization or
   model metadata rather than silently reinterpreting it.
4. Use synthetic fixtures to verify charge applicability, field-specific
   missingness, unexpected codes, primary-role behavior if introduced, and
   serialization/reload compatibility. Exercise the NumPy and Keras paths;
   preserve all-masked behavior and the matched `C0/C1` control. If the schema
   width changes, update both controls and their documented contract together.

A passing local repair establishes software semantics only. Production
normalization, representative source validation, remaining family semantics,
count scaling and pooling behavior still precede a training comparison. A later
source check or training proposal must name its source identities, measurement,
budget and terminal non-claims and obtain the corresponding run authorization.
Do not repeat the completed bootstrap/containment probes to advance this task.

The 2026-09-10 request authorizes recording the correspondence and continuation
plan. The implementation above is the recommended next task, not a claim that
the contract has already been repaired or that a scientific run is authorized.

This status authorizes no training, compute, Gate-6 action, `C_ML` construction, or publication claim.
