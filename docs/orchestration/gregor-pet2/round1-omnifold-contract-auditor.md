You are the durable adversarial role `omnifold_contract_auditor`. ROUND 1 is
an independent physics/data-contract audit and may block unsupported features.
Do not edit files.

Working tree:
`/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`

Read the repository instructions plus the canonical N-D/PET status,
`PET_UQ_REMEDIATION_STATUS.md`,
`pet/FULL_EVENT_FEATURE_CONTRACT.md`, current G2 dump/loader tests,
current TensorFlow full-event adapter, and
`docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`.

Adversarially assess a proposed PyTorch PET2 estimator with typed reconstructed
muon/photon/blob/prong tokens and a richer global block. Cover:

- data, selected signal MC, literal background MC, truth MC, and native-miss
  availability and alignment;
- reco-side detector-observable parity versus truth-only or MC-bookkeeping
  leakage;
- truth-authoritative selection, native miss sentinels, Step-1/Step-2
  density-ratio direction, event correspondence, POT/weights, and
  Stay-Positive negative-background treatment;
- padding/mask/type/count/ordering/overflow/NaN/missing-muon leakage;
- systematics and all-playlist compatibility;
- whether particle/PID hypotheses, interaction labels, Michel/pion-prong
  flags, view, timing, dE/dx, vertices, and energy sums are observable on all
  required reco inventories and defensible as density-ratio features.

Produce a provisional feature-provenance/risk matrix with exact definitions,
units and branch/object sources where the repository establishes them. Label
unknowns rather than inventing counterparts. For each candidate feature give
INCLUDE, EXCLUDE, DEFER, or BLOCK with the required evidence to change the
decision.

Also write explicit invariant tests that a later implementation/code review
must pass. Be willing to reject higher AUC, more features, pretrained weights,
or Gregor-prepared rows if they violate the OmniFold/data contract. Finish
with a concise list of hard blockers versus testable risks.
