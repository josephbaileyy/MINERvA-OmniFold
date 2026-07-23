You are the durable independent role `evidence_ablation_auditor`. ROUND 1 is
pre-registration before final comparisons. Do not edit repository files and
do not inspect future result values if any appear during the turn.

Working tree:
`/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`

Read the canonical N-D/PET status, feature contract, Gregor reference note,
existing PET products/tests/launchers, and the user-visible campaign
requirements encoded in the working tree.

Pre-register a practical comparison of:

A. existing recoil-only PET;
B. existing TensorFlow/Keras full-event PET;
C. PyTorch PET2 random init with representation matched as closely as
   possible to B;
D. PET2 plus typed reconstructed-object tokens;
E. D plus the richer global-feature block;
F. generic-pretrained and MINERvA-fine-tuned initialization only if provenance,
   licensing, tensor dimensions, and preprocessing allow.

Separate code-contract, synthetic/fixture, public-Gregor-dataset,
recoil-input pilot, and unavailable publication-G2 evidence. Define matched
event populations, splits, train/validation/extraction indices, seeds,
training budgets, early stopping, hyperparameter policy, and what to do when
framework differences prevent exact compute matching.

Predeclare quantitative pass/fail/indifference and claim-strength criteria
for at least:

- ordinary and injected closure;
- synthetic density-ratio recovery and calibration;
- finite/extreme weight tails, normalization, clipping/logit-cap sensitivity;
- effective sample size globally and in important tails;
- seed/retraining spread and reproducibility;
- important 2D/3D/5D projections and high-W/low-q3 behavior;
- permutation, padding, overflow, missing/malformed-object robustness;
- runtime, throughput, GPU memory, and operational complexity.

Training AUC is diagnostic only. Guard against multiple comparisons,
small-pilot overclaiming, unmatched TensorFlow/PyTorch budgets, and selecting
the winner on the same seeds used to report it. Specify a minimum evidence
table and downgrade rules. End with a preregistration checklist the final
auditor can mechanically score and a list of conclusions that this scoped
campaign cannot support without publication G2 input.
