You are the existing independent Gate-2 promotion verifier. Preserve your role and UUID.
This is a read-only scientific gate review: do not edit files, commit, dispatch workers,
or start PET/Gate 3.

The corrected exact target-only runtime completed successfully. Independently inspect:

- nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
- nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy
- docs/orchestration/state/g2-gate2-runtime-independent-validation-20260719.json
- nd-unfolding/pet/validate_gate2_target_receipt.py
- nd-unfolding/pet/gate2_target_runtime.py
- nd-unfolding/pet/fullevent_fps_dataloader.py
- nd-unfolding/PET_UQ_REMEDIATION_STATUS.md, Gate 2 only
- docs/orchestration/state/g2-gate1b-npz-validation-20260719.json

Verify the hash-bound input/code/configuration chain, exact learned
u2d.refine_stay_positive backend, complete literal data-plus-negative-background inventory,
normalization/finiteness/non-negativity/row alignment, signed-target identity, and independent
15x19 binned telemetry. Pay special attention to whether bypassing the TensorFlow-dependent
package initializer loads the exact NumPy dataloader source without changing scientific behavior.
Do not invent a threshold requiring the learned target to differ from the cellwise clipped target;
the exact telemetry must nevertheless be internally consistent and honestly interpreted.

Return exactly one decision-ready verdict:

- PASS: Gate 2 may be promoted and committed; or
- BLOCK: list the exact defect and smallest changed repair.

Also state explicitly whether Agent-B's owner receipt needs correction. Do not promote PET or
authorize Gate 3 yourself; those remain orchestrator decisions after a committed Gate-2 PASS.
