# DECISION 2026-11-05 — Joseph: #765's abstract sentence and 2D-choices disclosure take the PRD reviewer's wording; merge after the director's check

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The referee presentation round, PR #765.** The paper lane addressed PRD read 1 (`prd-read-1/`, answer sha256
`69374629…`) at head `36b903c46`. That left two wording choices for Joseph:
- **R3, the abstract's "fixed in advance".** The flagging criteria (p < 0.01, or a cell with |z| > 2) are fixed in
  `state/measurement-paper/5d-community-20261024/FD-DIRECTOR-RULINGS.md` §2. It was committed at `092702292`,
  2026-10-25 10:32 −0700, before F0's declaration (`7d7dac1d3`, 13:43) and its report (`28c4870f4`, 15:04). The
  director re-read §2 at that commit: "|z| > 2 per cell; or a χ² with P(χ²_16 > χ²_T) < 0.01 per truth".
- **R4, the disclosure of the two 2D choices made with the published comparison in view.** The learner
  implementation is already in IV B. The refined background treatment is the new one:
  - it was chosen on the simulation closure (`DECISION-20261023-joseph-2d-refined-integrate-ci.md`, RE1-REPORT-2's
    C2 FLAG);
  - it was formally adopted on 10-24 after RE-2 part C gave χ²/ndf 2.27, against 2.65 before
    (`DECISION-20261024-joseph-adopt-re2-2d-refined.md`).

**The first question went to Joseph before any reviewer had read the options.** One option was the director's own
reordering, not read by a reviewer, and the R4 option was the lane's chronological draft. Joseph answered:

> has a PRD reviewer suggested the wording yet? remember that I would prefer if wording decisions has gone through a reviewer first

> what does the referee say? I thought its not advised to use this chronological framing

To the third question, whether #765 may merge with the answers applied, he answered:

> Merge after your check

sha256 of the text plus a final newline begins `fa779bedbac686fa`.

**The PRD-referee read on the exact sentences** (Sonnet) is in
`state/2d-closeout/stageF/methods/referee-presentation-20261104/consult-wording-20261105/`, verbatim with SHA256SUMS.
- **R3:** keep the claim, but tie it to the body's fact, that the criteria were fixed before the tests were graded,
  and reorder so it cannot read as "fixed at a GiBUU truth".
- **R4:** a bare chronology is not enough. State the sequence as evidence, and its consequence: the 2D comparison is
  not an independent test. Note-only is not acceptable beside the paper's "No learner setting … was tuned on data".
  "Are not learner settings" reads as a carve-out.

## Joseph's answers, verbatim

Asked which abstract wording to use:

> Reviewer's, with criteria (Recommended)

sha256 of the text plus a final newline begins `02ed316d7be2e2a7`.

Asked which disclosure to use:

> Reviewer's framing (Recommended)

sha256 of the text plus a final newline begins `b60aa9ab615d52d9`.

## What is decided

1. **The abstract's sentence** becomes the reviewer's: "Fake-data studies at a GiBUU-like truth and at a synthetic
   momentum-transfer tilt find residual bias exceeding uncertainty-based criteria (p < 0.01, or any cell with
   |z| > 2) that were fixed before the tests were graded." IV G's sentence stays as drafted at `36b903c46`.
2. **Sec. III** keeps "No learner setting … was tuned on data". The lane's "Two choices … are not learner settings"
   sentence is replaced by the reviewer's: "Two other choices for the two-dimensional result were made with the
   comparison to the published result in view: the learner implementation and the background-subtraction treatment
   (Sec. IV B). That comparison is therefore not an independent test of the method."
3. **IV B** keeps the existing LightGBM sentence. The refined-background sentence takes the reviewer's framing:
   - the closure evidence;
   - that the choice was made on that closure before the refined result's published comparison was computed (records
     of 10-23 and 10-24);
   - "It was formally adopted after its distance from the published result was known, and the change lowered χ²/ndf
     from 2.65 to 2.27";
   - "The χ²/ndf values quoted for the two-dimensional comparison are therefore conditional on both choices, and the
     comparison should be read as a consistency check, not a blind validation." The lane merges this with IV B's
     existing "a consistency benchmark, not a blind validation", so it is not stated twice.
4. **The lane checks the reviewer's precision points** against the producers. It changes text only where the record
   supports the change:
   - whether only two implementations were compared;
   - that 5.9 and 0.44 are the same statistic, over the same cells;
   - the 3.66 → 2.65 → 2.27 sequence with ndf;
   - "statistical σ" defined.
5. **The process.** The lane applies items 1–4 with its ledger and checks, and builds a reading copy. The director
   checks the built PDF against this record and merges #765 on CI. Then Overleaf is re-synced.

Nothing is submitted, deposited or tagged.
