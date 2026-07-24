# Conditional-information continuation: implementation ownership and review

You are the existing durable `pet2_implementation_lead`, session
`019f8f08-9e4f-7de0-bfe2-98c63be814c4`. Resume this role; do not delegate,
start another provider, submit compute, commit, push, or touch another
checkout.

Read:

- `docs/orchestration/gregor-pet2/CAMPAIGN_LEDGER.md`;
- `docs/orchestration/gregor-pet2/CONDITIONAL_STRESS_PREREGISTRATION.md`;
- all continuation design/audit prompts and raw responses, including the
  Round-2 contract/evidence code audits and checkpoint-design reassessment;
- `docs/GREGOR_PET2_CHECKPOINT_COMPATIBILITY_DESIGN.md`;
- the current uncommitted diff under `nd-unfolding/pet2_torch/` and
  `nd-unfolding/tests/`.

The root prepared a starting implementation while this preserved account was
at its documented reset boundary. You now own its implementation review and
may edit only the in-scope experimental package, tests, launcher, README, and
checkpoint design. Preserve every frozen original product.

The latest root/auditor hardening computes rather than asserts truth
immutability, parent chance AUC, and bookkeeping exclusion; labels synthetic
overflow consistency separately from real pre-truncation conservation; checks
both global and tail ESS in the unity control; preserves the literal NPY
Fortran-order header bit; closes the output-publication/lock race; and tests
truncated/trailing ZIP members. Audit those changes rather than reverting
them.

Mechanically audit and, where needed, repair:

1. five split-local counterfactual fixtures whose materialized direct-parent
   tensors are byte-identical and whose sole enriched carrier decodes the
   hidden sign;
2. signal, unity-sham and carrier-shuffle controls; exact 0.5/1.5 pair mass;
3. unchanged truth inventory across families/modes, matched split/budgets,
   literal background/signed provenance, misses/fakes/full order, and
   truth-frozen Step 2;
4. additive `E-muon-global-plus-token` semantics that retain the parent
   globals and use nonzero audited synthetic relational coordinates;
5. pull/push, ESS/tail, cap, projection, resource and fingerprint receipts;
6. aggregate inventory and frozen gates for all 45 jobs / 90 arm results;
7. the G2 ZIP-to-NPY streaming converter and read-only memmap loader:
   receipt-bound input, object rejection, bounded reads, units, row/identity
   hashes, content-based resume, atomic publish, stale/partial/mutated
   rejection, and no G2 claim;
8. launcher isolation and fail-closed behavior;
9. the Gregor checkpoint-compatible design's exact source/tensor/state-dict
   facts, legacy/corrected separation, strict manifest, licensing, and
   no-pretraining-evidence boundary.

Pay particular attention to whether:

- the carrier can leak through parent token count/order/missingness or target
  bookkeeping;
- pair members always remain in the same split;
- the truth hash claim covers actual tensor bytes, not only row indices;
- a shuffled carrier remains chance-bounded in every split;
- the muon relation is actually expressible by this model's coordinate/KNN
  mechanism;
- the aggregate's pass/fail rules exactly match the frozen continuation
  preregistration rather than adding outcome-dependent rules;
- raw ZIP member streaming preserves NPY order and detects truncation/trailing
  bytes;
- resume cannot bless an unverified partial array or stale source.

Run the full login-safe PET2 test suite, Python compilation, launcher syntax
and self-test, and `git diff --check`. Add focused tests for any correction.
Return:

- code-review findings by severity;
- exact files changed;
- test counts;
- whether the implementation is ready for one clean commit and isolated Delta
  execution;
- any experiment gate that remains blocked.
