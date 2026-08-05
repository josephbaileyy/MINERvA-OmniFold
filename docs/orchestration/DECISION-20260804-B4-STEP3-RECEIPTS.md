# Decision record — B-4 weights, RESTORE Step 3 architecture, and Gate-2 receipt lifecycle

**Decision date:** 2026-08-04

**Status:** DECIDED; implementation and gate re-issues remain pending

**Authority:** the user delegated all three choices to Codex and then requested that the decisions
be recorded in the repository

**Scope:** publication full-event estimator `pet-fullevent-fps-v1`

This file is the canonical home for the three coupled decisions below. It authorizes a repair; it
is **not** a Gate-2/Gate-4 receipt, does not certify the present code, and does not authorize
publication training before the affected gates are re-issued. The measurements that forced the
decisions remain in the two 2026-08-04 finding files linked below.

## D1 — B-4: use the weight belonging to each OmniFold leg

**Decision:** Step 1's reconstructed-MC leg uses `w_reco`. Step 2 and every truth-space prior,
denominator, unfolded yield, and final truth-level event yield use `w_truth`.

This follows the estimator's sample semantics: Step 1 compares measured detector-level events to
the reconstructed MC ensemble actually observed, while Step 2 transports the learned correction
onto the truth-level MC prior. It also matches the established 2D contract, which keeps the two
weights distinct while correlating their bootstrap draw because they are two views of the same MC
event (`2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, Python-contract item 6 and bootstrap item 2).

The measured consequence and the old behavior are evidence, not repeated here as a second source
of numbers; see
[`FINDING-20260804-b4-is-active-gate2-cannot-be-reissued.md`](FINDING-20260804-b4-is-active-gate2-cannot-be-reissued.md).

Implementation requirements:

1. Do **not** replace the single PET `mc.weight` wholesale with `w_reco`: the current engine uses
   that one array in both legs, so a wholesale substitution would merely move the defect from
   Step 1 to Step 2.
2. Plumb distinct reconstructed- and truth-leg MC weights through the loader/engine boundary.
   Step 1 must consume `w_reco[pass_reco]`; Step 2 must consume `w_truth` on its truth population.
3. Under a coherent MC bootstrap or systematic universe, the reco and truth weights for one event
   ride the same event draw/universe while retaining their distinct nominal values.
4. Recompute B1's class-ratio denominator with the weight actually supplied to Step 1:
   `pot_scale * sum(w_reco[pass_reco])`. The measured-side normalization target remains `1e6 * R`.
5. Add mutation tests that independently perturb `w_reco` and `w_truth` and prove that only the
   intended leg and truth-yield calculation move.

This is one receipt-bound loader/engine repair and requires a Gate-2 and Gate-4 re-issue. The old
2026-07-19 Gate-2 target remains historical; it is not promoted by this decision.

## D2 — RESTORE Step 3: separate target ownership from MC closure construction

**Decision:** do not establish a combined ROOT/TF environment as publication provenance, and do
not split the ordinary closure into a ROOT refinement process plus a TensorFlow process.

Instead, make the two consumers honest:

- The **publication nominal** must consume the exact precomputed Gate-2 array
  `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy`. In publication mode the path is mandatory and must
  fail closed on target hash, owning runtime-receipt identity, source-NPZ identity, row count/order,
  finiteness, non-negativity, normalization, or feature/target fingerprint drift. There is no
  silent fallback to rebuilding the refiner in process.
- The **ordinary MC closure** must use an MC-only construction path that builds the same MC clouds,
  event features, masks, subsample, and D1 dual-leg weights as the nominal, but does not construct
  data/background rows, invoke Stay-Positive, import ROOT, or claim to test the
  `negweight-refined` measured target. It runs in the established TF 2.15 environment.

This corrects the premise in the original environment finding: the nominal launcher says it
consumes the literal target, but the current driver still calls `build_fullevent_loaders` without
a target path and silently rebuilds the refinement. That existing defect is audit finding J04.
The current closure also binds the returned `data` loader and never uses it; its pseudo-data is
built from MC reco rows and MC weights. Therefore making that closure read the Gate-2 target would
add an artifact dependency without exercising the artifact.

Closure semantics are part of the decision:

1. Rename/relabel the present identity test as an **MC self-consistency smoke**. It is useful for
   plumbing but cannot certify the measured target or distinguish a correct estimator from a
   constant/null estimator.
2. Before closure evidence can gate publication, add the already-specified nontrivial injected
   truth-reweight recovery test, run with the nominal estimator configuration and predeclared
   recovery criteria. Gate-2 separately certifies construction of the measured target; Gate-4
   must certify that the nominal consumes that exact target.
3. Gate-4 reports and receipts must state which assertion each artifact supports. They must not
   label an MC-only closure `bkg_mode=negweight-refined` or imply that it exercised refinement.

The environment survey remains useful diagnostic evidence in
[`FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md`](FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md),
but its three-option recommendation is superseded by this decision. A combined conda environment
may be used for non-receipt diagnostics only.

## D3 — retire the construction attestation; keep only live gates live

**Decision:** `state/g2-gate2-construction-20260719.json` is a historical construction
attestation, not a live gate receipt. Supersede it using the repository's existing receipt
lifecycle convention. Do not rewrite its hashes, add its paths to `KNOWN_PREEXISTING`, delete it,
or leave its bindings permanently live.

The receipt's at-issue status was `CONSTRUCTION_PASS_RUNTIME_PENDING` and its verdict was
`GATE_2_NOT_YET_PASS`. The later canonical runtime receipt overtook it and owns the live Gate-2
freeze. Accordingly:

1. Set the construction receipt's status to `SUPERSEDED` and point `superseded_by` to the extant
   Gate-2 canonical runtime receipt.
2. Preserve the entire at-issue binding block under `files_at_issue` and change every inner
   `sha256` key to `sha256_at_issue`. No digest changes.
3. Leave mismatches from the still-live Gate-2 runtime/launcher receipts red until the D1/D2
   repair is implemented and those gates actually run again.

`KNOWN_PREEXISTING` is not appropriate here. Its current implementation exempts by repository
path rather than by `(source receipt, path, expected hash)`, so adding the loader or test would
also suppress a future mismatch from a live receipt. If exemptions are needed in the future,
they must be source-qualified before being used for receipt-lifecycle cleanup.

## Transaction and completion gate

Implement D1 and D2 as one coordinated patch set because they meet at the receipt-bound loader and
the PET engine boundary. Then, in order:

1. run the login-safe/unit/mutation tests;
2. re-issue Gate 2 and publish a new precomputed target plus its self-pinning receipt;
3. prove the nominal consumes that exact target;
4. run the MC smoke and powered injected-reweight closure under TF 2.15;
5. re-issue Gate 4 with truthful closure/target semantics; and
6. rerun `verify_hash_bindings.py` and require no unexplained live mismatch.

Until those steps land in a commit with their required receipt/status/run-log evidence,
`nominal_pet_training_allowed` remains false.
