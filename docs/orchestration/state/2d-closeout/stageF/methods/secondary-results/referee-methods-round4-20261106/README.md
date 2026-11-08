# The fourth methods-draft referee round, PRD and JINST, 2026-11-06

**What was read.** `draft/methods-framing-20261106` at `33cdc4e596bdf2179860a12c8cc19ac5222fc704`. It is unmerged, and
no wording is approved. The director rebuilt its rater copy from a `git archive` of that commit and got bytes identical
to the drafter's: `manuscript-methods-r4.blind.txt`, 11,079 words, Tables I–VII and Figs. 1–4.

**What rounds 3 and 4 added:**
- the IBU head-to-heads (REF-G1 #821, REF-C2C1 #845);
- the gate-D diagnosis (#633, #645, #650, #667, #858);
- the divisor fix for χ²/205;
- the 2D run-period step at reco level (#135, #122);
- I0's 16-cell rounding spread;
- the result at ten iterations;
- cross-fitting worse at three truths;
- the eight-cell sensitivity;
- D-ID's identifiability;
- the 1A triage.

"Not for fitting" was cut from eight places to two. The sources are `../referee-request-map-20261106/MAP.md` (#859).

**Procedure.** The same as rounds 2 and the JINST test:
- `../referee-framing-comparison-20261106/referee-prompt-neutral.txt` (`b67be0e8…`) for PRD, and
  `../referee-jinst-test-20261106/referee-prompt-jinst.txt` (`fa84ae14…`) for JINST;
- Sonnet as read-only subagents (Reads of their two files only), and Gemini via agy (`--sandbox`, empty directory, the
  round-1 preamble).

All eight reads succeeded on the first attempt.

## Scores

| draft | PRD: Sonnet | PRD: Gemini | PRD mean | JINST: Sonnet | JINST: Gemini | JINST mean |
|---|---|---|---|---|---|---|
| round 4 (`33cdc4e5`) | 3, 4 | 3, 4 | **3.5** | 4, 4 | 5, 4 | **4.25** |
| round 2 (`0de103f7`) | 3, 4 | 3, 3 | 3.25 | 4, 4 | 5, 5 | 4.5 |
| round 1 (`09ef9ebb`) | 4, 4 | 4, 4 | 4.0 | — | — | — |

Every read in this round recommends major revision.

**The finding.** The score has reached a plateau. Bringing the existing records into the paper, as rounds 3 and 4 did,
changes it by less than the spread between repeat reads. Each of the eight reads names the same remaining items. These
are analyses, not text:
1. **The rounding instability.** Its mechanism, and an ensemble average over perturbations as the estimator.
2. **A repaired coverage test, run.** The like-for-like control exists for the interaction group (#667). Running any
   coverage test of 1B is governed by rule (iii) (DECISION-20261102-joseph-1b-redesign.md:78).
3. **The prior retention's mechanism.** A one-factor-at-a-time simulation study (observables, W, iterations, capacity),
   or truth recovery by IBU and OmniFold on the same fake data.
4. **The 2D benchmark per run period.** New in this round (Sonnet JINST read 2; Sonnet JINST read 1, issue 6). The
   run-period step near p∥ = 8 GeV/c and the shape difference at high p∥ may be connected. No record on main compares
   each period group with the published result. Search: period-unfold REPORT, `per-period.*publish` @ `3b01c4ad`.
5. **Self-containment.** The note, or a citable home for the records the paper relies on, deposited.

**CITABLE FOR:** these referees' reports on the round-4 rater copy, and the scores they gave.

**NOT CITABLE FOR:** any physics claim, any venue decision, or approval of any wording.
