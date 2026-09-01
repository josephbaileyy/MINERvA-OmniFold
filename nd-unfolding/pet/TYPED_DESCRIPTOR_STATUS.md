# PET typed-descriptor status

PET typed descriptors remain diagnostic and method-development infrastructure.

## R1 software smoke

**PASS — trainable-adapter software smoke only.** The uncapped, CPU-only Keras adapter has passed its synthetic contract, gradient, masking, serialization, and fresh-process reload tests. It is not production-integrated, production-normalized, trained, or scientifically evaluated.

## Control contract

- `C0` and `C1` both use `m_reco(num_evt=64)`.
- `C0` disables every typed family, so all 51 descriptor columns are exactly zero.
- `C1` enables the same 51 descriptor columns.
- The 13-wide event-only bypass is contextual only; it is not the footing-matched `C0` control.

## Unresolved gates

- field semantics and calibration;
- raw prong-PID provenance;
- production normalization;
- raw-count scaling;
- multiplicity-dependent segment-sum magnitude.

This status authorizes no training, compute, Gate-6 action, `C_ML` construction, or publication claim.
