# DECISION 2026-11-16 — Joseph: the batch of paper, Supplement and note decisions (A5, A6, B, C, E2, F); A1–A4 reopened

**Recorded by** the paper-tighten lane, as director.

## What led to it

The director put a batch of decisions to Joseph (`~/director-tools/BATCH-joseph-20261116.md`, not tracked). Each item
gave the director's recommendation and, where one existed, a codex-school referee's:
- **A, the five-observable (LL5D) coverage result:**
  - A1, the label;
  - A2, the §6.3 repair sentence;
  - A3, the abstract;
  - A4, the table words;
  - A5, §7;
  - A6, the GEANT4 bound sentence.
- **B:** the §5.3 prior-retention sentence.
- **C3 and C4:** the AI-use statements.
- **E2:** the note's sentences that rest on unreleased records.
- **F1–F6:** items from an independent referee read.

## Joseph's answer, verbatim

> A1. Keep A2. I feel like we didn't look at the actual results right? So we don't need to call it descriptive. Maybe we should redefine descriptive to mean the something along the lines of influenced by results, which is less strong of a description but maybe more honest? Can you ask a referee A3 & A4 this probably needs to be reevaluated based on A2. A5 I like the recommendation A6. yes looks good B. Looks good C3. no for now but I will look into it C4. agree E2. agree F1. looks good F2. qualify but add this as an open item right? F3. agree F4. can we just see what it looks like? F5. agree F6. agree

sha256 of the text plus a final newline begins `9c5c7fb1afab1163`.

## What is decided

1. **A1, A2, A3 and A4 are open.**
   - Joseph questions whether the "Descriptive" status applies, since no coverage result had been seen when the repair
     was chosen, and asks for a referee's view.
     <!-- absence-ok: reports Joseph's premise, which the referee read tests; not a claim of this record -->
   - A codex-school referee is reading the question against these records:
     - `DECISION-20261109-joseph-coverage-case-wording.md` item 2;
     - `LL5D-DECLARATION.md`, the STOP rule and §3.6;
     - the gate STOP receipt;
     - amendment A1a.2.
   - The abstract (A3) and the table words (A4) are re-read under the answer. Joseph decides all four after the read.
   - Until then, the "Descriptive" status and its caption stand as `DECISION-20261109-joseph-coverage-case-wording.md`
     item 2 fixed them.
2. **A5.** §7 is accepted, with this sentence added: "Whether the joint failure persists with the response and
   run-period terms included remains untested."
   <!-- absence-ok: quoted paper wording approved by Joseph; its support is the LL5D readout, not this record -->
3. **A6.** The §6.3 sentence on the GEANT4 bands' covariance block is approved as the batch gives it: "Removing the two
   bands' block from the covariance graded with them raises the chi-square of any fixed set of residuals by at most a
   factor of 1.071 at G18 and 1.095 at AR23, a bound set by the largest fraction of that covariance, in any direction,
   that the block carries. The bound applies to the block's place in the covariance only, not to the bands'
   pseudo-data draws, and what separates the bands' pseudo-experiment and simulation-side blocks remains
   unclassified."
4. **B.** §5.3 takes the alternative with the clause: "Reducing the iteration count from five to two increased ρ beyond
   the threshold at the q3 tilt. Reducing capacity to 25 trees and four leaves, or restricting all three learners to
   (pT, p∥), increased ρ beyond the threshold at both flagged truths. These settings also newly flagged 3, 3 and 6 of
   the other ten graded truths, respectively, in the noise-free study. Dropping W alone, or W and q3, changed ρ by less
   than 0.03."
5. **C3.** The delegation sentence stays in both AI-use statements as `DECISION-20261114-joseph-ai-use-statement.md`
   gives them. **No Methods paragraph for now.** Joseph will look into APS's expectation, which stays an open item.
6. **C4.** The cross-developer review sentence stays in the note only, as "Reviews included models from multiple
   developers". It is dropped from the paper.
7. **E2.** The note's sentences resting on unreleased records are handled selectively:
   - the support for the current results, plus a compact timestamped decisions record, goes into the deposit;
   - the superseded history is shortened, not deposited;
   - the release-status narration is replaced by the deposit identifier and checksums, filled at the freeze;
   - "a priori" becomes "No hyperparameter search was performed on data."
8. **F1.** The Data availability sentence becomes: "Playlist 1A is from an earlier production of that release; the
   other playlists match the current release."
9. **F2.** Finite-replica covariance noise is qualified, with no new study. The text says:
   - the false-flag rates are conditional on a fixed-covariance null;
   - covariance estimation can inflate spread in weak eigenmodes;
   - the verdicts stand.

   It is also an **open item**: a row in the limitations register, status open.
10. **F3.** The 2D shape difference is not attributed to the unfolding method.
11. **F4.** Joseph asks to see Fig. 1 with a pull histogram in place of its text panel before deciding. The director
    makes a mock-up outside the repository. The pinned figure is unchanged until Joseph decides.
12. **F5.** One bounded editorial pass on §7 and §5.4 only, after the prep branches are merged into the draft.
13. **F6.** The note's executive summary is aligned with the paper's framing: the sixteen-cell output is an
    illustration of the method, not "the principal result".

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the wording choices above as Joseph's; A1–A4 as open.
- **Not citable for:**
  - any coverage, bias or covariance result;
  - a referee's view as a finding;
  - a locked wording. Every sentence stays open to the remaining referee reads and to Joseph.

Nothing is submitted, deposited or tagged.
