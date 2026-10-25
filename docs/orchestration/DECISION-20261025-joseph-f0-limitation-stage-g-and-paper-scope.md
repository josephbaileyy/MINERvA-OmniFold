# DECISION 2026-10-25 — Joseph: accept the F0 limitation, run Stage G, skip F1, open the abstract and scope the paper's secondary results and the assigned uncertainties

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The director put six questions to Joseph:
- the F0 report (`state/measurement-paper/5d-community-20261024/FD-F0-REPORT.md`, PR #362) and its reading;
- the caveat study (`state/2d-closeout/stageF/methods/caveat-study/REPORT.md`, PR #361): R-P8, R-P9, R-N7 and the §6
  options.

**F0, in the director's reading.** The report draws no conclusion; this reading is the director's.
- The reported 5D uncertainty, without each truth's own C_model vertex, reaches the bias at the default, untuned
  GENIE, GENIE+MEC and most NuWro-like truths.
- It does not reach the bias at the GiBUU-like truths or at the synthetic q3 tilt.
- Most of the reach comes from C_e's systematic blocks, not from C_model.

Joseph's answer, verbatim:

> 1. Yes I accept the limitation but coordinate with the paper rewriter to make sure its presented in a typical way for PRD. 2. Yes go ahead. 3. skip F1 for now. 4. yes r18 can propose a change to the abstract 5. I think this is something that should be seriously considered, since caveats matter in a close read, which is what the note is for, but would people reading the short paper care about them? 6. I think it doesn't hurt to have these measurements right? Unless there are higher priority things to do? As for if we report them on their own versus adding them into the other ucnertainties, what is typical?

sha256 of the text plus a final newline begins `f7ce800538e024d4`.

## What is decided

1. **The F0 limitation is accepted.** The 5D measurement states that its reported uncertainty does not cover the
   fake-data bias at GiBUU-like truths or at the q3 tilt, with the fake-data results as support.
   - **Presentation** follows PRD practice, under the caveat-study rules: a short fake-data study in the uncertainty or
     validation discussion, with a table of the truths and their χ², the limitation stated once where the result is
     described, and the detail in the note.
   - **The paper rewrite lane drafts the wording as a proposal** for when the 5D result is integrated into the
     documents. The draft is not printed now: integrating the S1 result is its own step, and its wording needs
     Joseph's approval.
   - Nothing rescales C_model. κ = 1 stands, and no cell is merged.
2. **Stage G is approved.** It compares the data result with the five generator predictions on R00–R15, with GiBUU
   on the eight p_∥ < 4.5 cells, as FD-PLAN §4 and `FD-DIRECTOR-RULINGS.md` §5 describe.
   - It runs at 0 node-h, on a login node, through a declaration and a binding.
   - This is the first data-against-generator comparison on these cells, and Joseph's approval covers that read
     (DECISION-20261025, `-scope-5d-fake-data-test`, item 2).
3. **F1 is skipped for now,** and F1-W is deferred with it.
4. **r18 may propose a change to the abstract** under R-P8. The proposal comes to Joseph, and the abstract does not
   change without his approval of the wording.
5. **Moving the paper's secondary results to the note is to be seriously considered** (R-P9, R-N7). The paper rewrite
   lane lists the candidate secondary results, each with:
   - its caveats;
   - where it would print in the note;
   - the one-line pointer left in the paper;
   - what the paper would stop claiming.

   The list comes to Joseph for a decision before any round acts on it.
6. **The assigned-uncertainty options (caveat study §6) are to be scoped,** at about 0 node-h, as a costed plan for
   Joseph before anything runs:
   - the purity non-closure;
   - a model-dependence covariance for the residual regularization bias;
   - the hadronic-response band;
   - a seed ensemble;
   - statistical-band scaling.

   The plan states the usual practice of comparable papers for each, ranks the options by value against cost, and
   places them against the work already queued. In that practice an assigned uncertainty is a named component in the
   uncertainty breakdown, included in the total covariance.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
- No GPU and no premium QOS.
- Publication needs Joseph's and Ben's review and MINERvA collaboration review, which is Joseph's act.
