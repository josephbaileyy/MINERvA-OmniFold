# PET typed-descriptor status

PET typed descriptors remain diagnostic and method-development infrastructure.

## R1 software smoke

**PASS — trainable-adapter software smoke only.** The uncapped, CPU-only Keras adapter has passed its synthetic contract, gradient, masking, serialization, and fresh-process reload tests. It is not production-integrated, production-normalized, trained, or scientifically evaluated.

## Fixed-sample semantic evidence

**BLOCKED, NARROWED — fixed-sample telemetry and external-source comparison only.** The bounded 16-data plus 16-MC source sample exposes three live contract seams: raw charge code `2` lies outside the declared categories; the current mapper retains prongs that the linked downstream preprocessing filters; and the linked paper/source materials conflict internally on raw prong-PID meaning. No replacement semantic rule is adopted.

The fixed-sample measurements, external source versions, exact digests, and non-claims are recorded in `docs/orchestration/PACKET-20260901-pet-typed-descriptor-semantic-evidence.md`. The deterministic probe and JSON output are archived under `docs/orchestration/runs/pet-typed-semantic-evidence-20260901/`.

The 32-row packet does not support photon three-state rates, cross-playlist claims, blob structural-zero rates, or broad prong findings. Surviving M60 raw artifacts are preserved as a distinct, unrouted layer under `docs/orchestration/runs/pet-typed-semantic-evidence-20260901/m60/`; they are not imported into the fixed-sample result.

## Control contract

- `C0` and `C1` both use `m_reco(num_evt=64)`.
- `C0` disables every typed family, so all 51 descriptor columns are exactly zero.
- `C1` enables the same 51 descriptor columns.
- The 13-wide event-only bypass is contextual only; it is not the footing-matched `C0` control.

## Unresolved gates

- field semantics and calibration;
- raw prong-PID and charge-code provenance;
- raw-row versus filtered-object membership;
- production normalization;
- raw-count scaling;
- multiplicity-dependent segment-sum magnitude.

This status authorizes no training, compute, Gate-6 action, `C_ML` construction, or publication claim.
