# Agent-B P5B follow-up 05 — Gate-2 literal negweight-refined construction

Resume your existing Agent-B UUID. Work from committed HEAD `e071d1c`, where G2
Gate 1 is now PASS. The hash-bound production input is
`nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz`; its tracked producer and
independent receipts are committed. Do not modify or regenerate that NPZ.

Take only the next dependency-ready Gate-2 construction action. Repair
`nd-unfolding/pet/fullevent_fps_dataloader.py` and focused login-safe tests so
the publication-default `bkg_mode=negweight-refined` path:

1. derives the data row count from the G2 data inventory (`measured_pc`), not
   absent legacy/purity `measured_weights`;
2. constructs the complete signed measured inventory as positive data rows plus
   aligned background clouds/event features with weights
   `-w_bkg * pot_scale` (and applies coherent data/background factors before
   refinement for a replica);
3. applies Stay-Positive refinement to the complete signed inventory and returns
   finite non-negative weights aligned to the concatenated data/background
   features; never silently substitutes all-ones purity weights;
4. records decision-ready target telemetry: input identity hashes, raw
   positive/negative sums, POT scale, refinement mode/config/fingerprint,
   refined normalization and floor/clipping/cancellation information, output
   row counts, and target mode `negweight-refined`;
5. fails closed on missing/misaligned background clouds/scalars/weights,
   mismatched identities, invalid POT, non-finite weights, old schema, and any
   attempt to reuse a nominal refined target for a bootstrap replica; and
6. adds a small end-to-end fixture that reaches the loader boundary without
   running PET training, plus independent binned signed/refined checks and
   negative/tamper cases.

Resolve explicitly whether the current binned closed-form Stay-Positive helper
is fixture-only while production must call the learned refinement. Do not claim
Gate 2 PASS if learned production refinement is not yet wired and tested.

No GPU/PET training, endpoint, covariance, full-NPZ materialization on the login
node, provider migration, new role, commit, push, or unrelated edits. Preserve
all existing files and UUIDs. Run proportionate focused tests, report exact
files/diff/tests and remaining blocker, and leave changes uncommitted for
orchestrator review.
