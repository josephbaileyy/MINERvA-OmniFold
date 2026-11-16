# DECISION 2026-11-10 — Joseph: the methods paper withholds V-PRIOR's results, because its generator spread uses the CH-corrected NuWro and GiBUU predictions that referee item B5 removes

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **Referee item B5** (interim round, #1025; `secondary-results/referee-methods-interim-20261110/gpt.txt:70-74`): the
  GiBUU free-proton sample failed its sampling-closure check and its deep-inelastic events do not conserve energy;
  the NuWro hydrogen supplement has unbounded losses from generator aborts. The referee asked the authors to repair and
  validate the samples, bound their effect, or remove the affected corrected predictions and χ² values. Under Joseph's
  approval of the director's recommendations for groups A, B and C, #977 removes the CH-corrected NuWro and GiBUU
  predictions from the generator comparison (S10) and keeps both generators on carbon only, labelled.
- **The claim sweep for B5** (director-helper-3, on #977) found that V-PRIOR, the second per-cell validity rule, builds
  its generator spread S_g from the same predictions:
  `state/2d-closeout/valid-region-20261107/DECLARATION.md:120` (input I3, "with NuWro and GiBUU corrected to CH") and
  `:135-139` (NuWro on all 16 cells, GiBUU on 8). Its results print in the paper's §5.4 and Supplement S11.
- **The director measured** from `fd/gencmp/readout/defs.json` that carbon/CH − 1 runs from +0.2 % to +4.7 % per cell for
  NuWro and from −0.8 % to +5.5 % for GiBUU, the largest in R08. So a carbon rerun was possible locally from committed
  records, but it would put a carbon-versus-CH target difference into the spread.
- **An independent consult** at Joseph's request (codex-school2 `gpt-6.1-sol`, high, read-only at #977 `78ab386e0`;
  [`consult-sol-vprior-20261110/`](state/2d-closeout/stageF/methods/secondary-results/consult-sol-vprior-20261110/))
  recommended withholding. Its reasons:
  - keeping the predictions in a validity rule after removing them from S10 would be inconsistent;
  - the carbon–CH difference is a sensitivity that uses the suspect sample, not a bound;
  - a carbon substitution mixes target composition into S_g, and from the recorded departures it would lower R08's raw
    S_g, so it could not change R08's class;
  - a referee would not object, because V-PRIOR is not the basis of the paper's main findings.
  The consult checked the departures; it did not compute V-PRIOR.
- **The director recommended** withholding.

## Joseph's answers, verbatim

Asked to choose among withholding, a carbon rerun and keeping V-PRIOR labelled, Joseph first asked:

> can you explain it more and what is its cost?

and then, after the costs:

> can you ask a gpt 6.1 sol high session what it recommends?

(sha256 of the text plus a final newline begins `65b805d58dca03cc`). Given the consult's recommendation, he chose:

> Withhold (Recommended)

(sha256 begins `922615251ce4994b`).

## What is decided

1. **The methods paper (#977) withholds V-PRIOR's results.** §5.4 and S11 drop V-PRIOR's counts, ratios and the
   "under both" count, and keep V-ATLAS and V-HALF. One sentence says why, in the consult's terms: V-PRIOR's
   CH-corrected NuWro and GiBUU inputs rely on free-proton samples with unresolved validation problems. The paper lane
   sweeps every downstream use of V-PRIOR by claim, not only the headline count, and runs the meaning read on the pairs.
2. **The result package (#981)** drops its V-PRIOR (`prior_*`) rows at the post-fill re-pin, or marks them withheld,
   so that it ships no V-PRIOR number the paper does not print.
3. **Nothing is deleted from the records.** The V-PRIOR declaration, binding, outcome and readout stay as they are.
   They remain the historical calculation, under their own licences.
4. **Deferred to the follow-up paper:** V-PRIOR on repaired and validated free-proton samples. That needs its own
   declaration and decision. No carbon-only rerun is run.
5. **The companion note** is out of scope here; its V-PRIOR text waits for the note lane, and the Supplement–note sync
   mapping records the divergence.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** withholding V-PRIOR's results from the methods paper and the result package; the deferral; the
  reason.
- **Not citable for:** any claim that V-PRIOR's classification is wrong or right, any carbon-only V-PRIOR result, or a
  bound on the free-proton samples' effect.

Nothing is submitted, deposited or tagged.
