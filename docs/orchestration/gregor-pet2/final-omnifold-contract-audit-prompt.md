Continue as the same durable `omnifold_contract_auditor`, session
`0d8740dd-23f7-494f-9664-924f5d6bdc34`. This is the required final
post-experiment implementation and writeup audit. Work read-only. Do not edit
files and do not start any delegate, subagent, one-shot provider, or raw CLI
worker.

Audit branch `codex/gregor-pet2-omnifold` through committed HEAD. The
result-bearing commit is `d2bead0`; provider-home reconciliation after it does
not change estimator code or results. Read at minimum:

- `KNOWN_ISSUES.md` #19--21;
- `nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`;
- `docs/orchestration/gregor-pet2/EXPERIMENT_PREREGISTRATION.md`;
- `docs/orchestration/gregor-pet2/CAMPAIGN_LEDGER.md`;
- every source and test under `nd-unfolding/pet2_torch/`;
- `nd-unfolding/pet2_torch/products/final_campaign_summary.json`;
- both `products/synthetic_matched/*aggregate.json`;
- `products/tf_ab_matched/aggregate.json`;
- `products/xps2_practical/aggregate.json`;
- representative per-seed summaries and receipts for every arm;
- `VALIDATION_LEDGER.md` final Gregor entry;
- `docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md`.

Treat all claims as untrusted until checked against receipts. Mechanically
verify:

1. every D/E/muon-token/overflow arm changes Step 1 only and shares the same
   persisted truth-arm fingerprint and exact truth tensors;
2. class direction, class-mass offset, `w_reco`/`w_truth`, native misses,
   background/target treatment, Stay-Positive provenance, full-order
   extraction, cap metrics, and deterministic settings remain coherent;
3. the aggregate really enforces common source, sample, split, seeds, model
   parameter footing and optimizer budget, and that no quarantined pre-fix
   result entered it;
4. TensorFlow and XPS2 evidence downgrades are complete and prevent an invalid
   B-versus-C, typed-object, closure, or publication claim;
5. every feature decision in the assessment respects data/signal/background
   symmetry, miss semantics, detector observability, leakage prohibitions,
   units, padding/masks, and missing/malformed-object behavior;
6. the final recommendation is no stronger than the code-contract,
   synthetic, public-data, recoil-input, and unavailable-G2 compartments
   support.

Classify each finding `BLOCKER`, `MAJOR`, `MINOR`, or `CLEAR`, with exact
file/line or JSON-key evidence. Separate implementation defects, product/
aggregation defects, documentation defects, and unavailable-G2 deferrals.
End with:

- final code-contract verdict;
- whether the result artifacts are admissible as their labeled evidence
  classes;
- exact required revisions before final handoff;
- remaining dissent and G2-only blockers;
- a concise mechanical reassessment checklist for the same-session revision
  round.

Do not infer a scientific winner and do not accept training AUC as evidence.
