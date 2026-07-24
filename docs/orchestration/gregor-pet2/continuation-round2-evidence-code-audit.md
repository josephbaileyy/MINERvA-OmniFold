# Conditional continuation: preregistration/aggregation implementation audit

Resume the existing durable `evidence_ablation_auditor` session
`4be5058b-7e1a-49f2-a102-04fe530e5f3a`. Read-only only: do not edit, delegate,
submit compute, commit, or start another role.

Read:

- `docs/orchestration/gregor-pet2/CONDITIONAL_STRESS_PREREGISTRATION.md`;
- `nd-unfolding/pet2_torch/{conditional_fixtures.py,conditional_stress_cli.py,aggregate_conditional_stress.py,sbatch_pet2_conditional_delta.sh}`;
- `nd-unfolding/tests/test_pet2_conditional_fixtures.py`;
- the current assessment diff and campaign-ledger continuation entries.

Audit whether the code faithfully implements the frozen design without
outcome-dependent selection:

- exactly five families x three modes x three estimator seeds, with matched
  100k/10k rows, split seed, two iterations, eight epochs, optimizer and
  budget;
- exact 0.5/1.5 signal, unity sham, within-split shuffled carrier, matched
  parent/enriched footing and truth-frozen Step 2;
- mechanically justified parent chance and enriched positive controls;
- the complete fixed signal and negative-control gates, including all-seed
  direction, ESS/tails, projections, cap-10/cap-30 telemetry and no
  post-outcome threshold;
- aggregation rejection of duplicates, omissions, dirty source, mixed
  commits, rows, truth, parameters, model/preprocessing or custom smoke runs;
- evidence containment: channel capacity only, no real MINERvA benefit,
  adoption, G2, architecture or pretrained claim.

Identify BLOCKER/MAJOR/MINOR findings with exact symbols and repairs. State
whether the implementation is statistically admissible for the frozen Delta
matrix after repairs. This is not the required post-result evidence/writeup
audit; that will return to this same session after the aggregate exists.
