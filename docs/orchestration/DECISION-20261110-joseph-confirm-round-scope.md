# DECISION 2026-11-10 — Joseph: the confirming round's revision covers writing, structure and cheap diagnostics from existing products before submission; the pipeline tests follow LL5D; the V-PRIOR withholding sentence moves to the Supplement

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The confirming referee round** on #977 at `53514740`
  (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-confirm-20261110/`, PR #1029): gpt-6.1-sol
  scored it 5/10 and a fresh blind Claude Opus 4/10, both recommending major revision. Both judged the paper
  publishable in JINST as a diagnostic methods study after revision, with no limitation disqualifying.
- **The director sorted the points both readers share into four tiers:**
  - Tier 1, writing and structure from existing results;
  - Tier 2, cheap new diagnostics from existing products: the two-dimensional coverage failure split into bias and
    fluctuation parts in the covariance eigenbasis, the fake-data grading without C_model and with statistical-only
    uncertainty, and the ensemble average's result on data with the size of its one deficit;
  - Tier 3, new noise-free pipeline tests of why more iterations and capacity raise the retained fraction (oracle
    miss weights, the refinement disabled, a weighted miss regressor, a reconstruction-level closure per iteration);
  - Tier 4, a persistent public deposit, which is Joseph's.
- **Both readers would take the V-PRIOR withholding sentence out of the main text.** GPT would keep a short statement
  in the Supplement; Claude would drop it entirely. `DECISION-20261110-joseph-vprior-withhold.md` item 1 had put the
  sentence in §5.4.

## Joseph's answers, verbatim

On scope:

> Tiers 1+2 but add 3 into the after LL5D tasks, remember that if usage allows, we should start working on those tasks too

(sha256 of the text plus a final newline begins `4a98c4d4d82ce0d9`). On the withholding sentence:

> Move to Supplement (Recommended)

(sha256 begins `8f35ee1ad2a5d8e1`).

## What is decided

1. **Before submission, #977 takes Tier 1 and Tier 2.** Each Tier 2 diagnostic is declared before it is computed and
   read once, under its own short declaration and the director's binding, from existing products only. Each enters the
   paper only within its record's licence, with a meaning read on the changed pairs.
2. **Tier 3 joins the post-LL5D task list.** If usage allows, its design and declaration start earlier, but no Tier 3
   job runs before the LL5D readout without the director's go. Until Tier 3 reports, the paper states each untested
   cause as a limitation, with the tests as recommended future work.
   <!-- absence-ok: this decision's own instruction for the paper's wording until Tier 3 runs, not a claim that a result does not exist -->

3. **The V-PRIOR withholding sentence moves from §5.4 to the Supplement (S11).** §5.4 reports only the rules that have
   results. This amends item 1 of `DECISION-20261110-joseph-vprior-withhold.md` in placement only; the withholding and
   its reason stand.
4. **Tier 4 (the deposit) is unchanged:** it waits for Joseph's separate release decision.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the revision's scope; the Tier 3 deferral; the sentence's new placement.
- **Not citable for:** any Tier 2 or Tier 3 result, any paper sentence, or a release decision.

Nothing is submitted, deposited or tagged.
