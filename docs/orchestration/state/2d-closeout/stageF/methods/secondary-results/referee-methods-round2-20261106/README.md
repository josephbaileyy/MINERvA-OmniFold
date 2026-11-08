# The second methods-draft referee round, 2026-11-06

**Asked for by** Joseph's revision-round decision (`DECISION-20261106-joseph-methods-revision-round.md`, #853, item 3).

## What was read

**The draft:** `draft/methods-framing-20261106` at `0de103f7de9ef76ba661e5595fcde58415193d5c`. It is unmerged, and no
wording is approved. The director rebuilt its rater copy from a `git archive` of that commit and got bytes identical
to the drafter's (`manuscript-methods-r2.blind.txt`, 10,280 words). The copy holds Tables I–VII and Figs. 1–4.

**Its changes from round 1:**
- the sixteen-cell output, the generator χ² and the C_model sensitivities move to Appendix A, marked "not for fitting
  or for constraining models";
- the 2D eigenmode breakdown is brought in;
- so are the reported estimator's closure, the iteration-count evidence, the exact binned comparison and the coverage
  gate;
- Fig. 2 is labelled a development diagnostic;
- the abstract leads with the findings.

## Procedure

It is the same as round 1 (`../referee-framing-comparison-20261106/`):
- the prompt `referee-prompt-neutral.txt`, sha256 `b67be0e8…`;
- Sonnet as read-only subagents. Their transcripts show only Reads of their two files: two calls for one, and three for
  the other, which read the paper twice;
- Gemini via agy (`gemini-3.8-flash-high`, `--sandbox`), from an empty directory, with the round-1 preamble
  (`82d13a5a…`). Both reads succeeded on the first attempt;
- two reads per referee.

## Scores

| version | Sonnet | Gemini | mean | recommendations |
|---|---|---|---|---|
| methods round 2 (`0de103f7`) | 3, 4 | 3, 3 | **3.25** | Sonnet: reject in present form, and major revision; Gemini: reject, and reject |
| methods round 1 (`09ef9ebb`) | 4, 4 | 4, 4 | 4.0 | all four major revision |
| measurement, with appendix | 3, 3 | 4, 4 | 3.5 | all four major revision |

The restructuring didn't raise the score. Gemini moves from major revision to reject in both reads, and the one-point
steps are about the size of the spread between repeat reads.

**The reason all four give.** With the measurement demoted, the paper's content is a set of failures whose causes are
not found. The referees then judge it as a methods paper against that standard. Sonnet read 2: "As written, the paper
can neither be read as 'OmniFold works on neutrino data' nor as 'OmniFold fails for this reason'."

## What the four reads ask for

These are requests, not records.
1. **The coverage pre-check's 0.70–2.30 ratios.** Diagnose them band by band, then run the coverage test. Every read
   says this looks like a fixable harness defect.
2. **The rounding instability.** Find its mechanism. Define the estimator as an ensemble mean over perturbations, or
   use exact-split trees, and measure the spread on the sixteen reported cells.
3. **Prior retention.** Unfold the same pseudo-data from two or three priors and show convergence. Run an iteration
   scan at the sixteen-cell level.
4. **A binned IBU on the same sixteen cells and the same fake-data tests** (both Sonnet reads). REF-G1 is that
   head-to-head, and it reads `differ` (`OUTCOME-20261106-ref-g1-r1-differ.md`).
   - REF-C2C1's c2 (a binned IBU on the 2D inputs, K = 10) also reads `differ`, with ρ unresolved, and c1 reads
     `equivalent` (`OUTCOME-20261106-ref-c2c1-read.md`).
   - Both are on record but not in the draft, because their paper text waits for Joseph and a PRD read.
5. **The run-period step at reconstruction level.** RPD-RECO is running.
6. **The 2D benchmark:**
   - a well-conditioned statistic, fixed in advance;
   - the published configuration's ten iterations;
   - the "earlier production" of the open data quantified as a candidate cause.

   Sonnet read 1 notes a tension between "differs … over many eigenmodes" and the 73 best-determined directions'
   χ²/ndf of 0.66.
7. **The target treatment.** Native-CH NuWro as the prediction, and the GiBUU CH comparison fixed or dropped. Detector
   response varied in the fake-data tests, including neutron response.

**Venues named:** JINST, Computing and Software for Big Science, Computer Physics Communications, EPJ C, and Machine
Learning: Science and Technology.

**CITABLE FOR:** these referees' reports on the round-2 rater copy, and the scores they gave.

**NOT CITABLE FOR:** any physics claim, a decision, or approval of any wording.
