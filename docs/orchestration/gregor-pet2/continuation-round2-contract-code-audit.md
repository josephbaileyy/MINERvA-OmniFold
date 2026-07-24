# Conditional continuation: post-implementation contract/code audit

Resume the existing durable `omnifold_contract_auditor` session
`0d8740dd-23f7-494f-9664-924f5d6bdc34`. This is a read-only audit. Do not
edit files, delegate, start providers, submit compute, commit, or touch another
checkout.

Read the current uncommitted continuation implementation and tests:

- `docs/orchestration/gregor-pet2/CONDITIONAL_STRESS_PREREGISTRATION.md`;
- `docs/orchestration/gregor-pet2/CAMPAIGN_LEDGER.md`;
- `nd-unfolding/pet2_torch/{conditional_fixtures.py,conditional_stress_cli.py,aggregate_conditional_stress.py,g2_memmap.py,g2_memmap_cli.py,features.py,sbatch_pet2_conditional_delta.sh,README.md}`;
- `nd-unfolding/tests/{test_pet2_conditional_fixtures.py,test_pet2_g2_memmap.py}`;
- `docs/GREGOR_PET2_CHECKPOINT_COMPATIBILITY_DESIGN.md`;
- the current `git diff`.

Mechanically audit the implementation against your prior binding ruling,
including:

1. exclusive parent-invisible carriers and exact parent tensor ties;
2. within-split pairing/balance/shuffle chance bounds and absence of
   bookkeeping leakage;
3. actual full truth-tensor/inventory hashing, frozen Step 2, native misses,
   fake prohibition, D/S/B symmetry, literal background and signed/refined
   target semantics;
4. additive muon-token relational coordinates and overflow conservation;
5. signal/unity/shuffle controls, matched rows/seeds/budgets, pull/push/ESS,
   tails, projections, cap-10/cap-30 count and weight-mass telemetry;
6. whether aggregate gates exactly implement the frozen preregistration and
   reject dirty/incomplete/mixed-footing runs;
7. production-size G2 ZIP streaming, content-verified resume, crash/concurrent
   locking, atomic publish, units, row and identity hashes, mutation/staleness
   rejection, and readonly windowed memmaps;
8. checkpoint-design separation, exactness, licensing and no-evidence
   boundaries.

Distinguish BLOCKER/MAJOR/MINOR. Give exact file/line or symbol evidence and
specific repairs. State whether a clean source commit and matched Delta
execution are authorized after repairs. Do not assess experiment outcomes;
none exist yet.
