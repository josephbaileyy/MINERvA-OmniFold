# The framing comparison: methods draft against the measurement paper, 2026-11-06

**Asked for by** Joseph (2026-11-06): "can we get a prd referee on the methods paper and see if it scores way better?"
(`DECISION-20261106-joseph-relax-12h-job-limit.md` records the message, sha256 `c0e22726…`).

## What was compared

- **Methods draft:** branch `draft/methods-framing-20261106` at `09ef9ebb08a742248c97dd9b23c8cba171a10da6`. It is
  unmerged, and no wording is approved. The director rebuilt its rater copy from a `git archive` of that commit and got
  bytes identical to the drafter's: `manuscript-methods.blind.txt`, 9,983 words.
- **Measurement paper with its appendix:** main at `e08c16f41`, plus the same layout-only `\clearpage` at the end of
  `paper_body.tex` that the draft adds. The change was made in a scratch copy only. File:
  `manuscript-measurement-appendix.blind.txt`, 9,439 words.
- **Measurement paper as main builds it:** `manuscript-measurement-noappendix.blind.txt`, 8,802 words.
  - Here `make_rater_copy.sh` drops Appendix A's group list and Tables V–VI. pdftotext emits them after reference [1],
    and the blind cut removes everything from [1] on.
  - The drafter found this. Earlier referee rounds' copies may also lack those tables.

## Procedure

- **The prompt:** `referee-prompt-neutral.txt` (sha256 `b67be0e8…`). It is the 11-01/11-04/11-05 prompt (`a24a34a1…`)
  with four minimal edits, so that it doesn't presuppose a measurement:
  - "claims and measures" becomes "claims and does";
  - "deficiency of the measurement" becomes "of the paper's claims";
  - "a PRD measurement may publish with" becomes "a PRD paper of this kind";
  - "Is the measurement publishable" becomes "Is the paper publishable in PRD, as the kind of paper it presents itself
    as".

  It also adds item 7: a 1–10 score, the main contribution, and a better-suited journal. It isn't byte-comparable with
  the earlier rounds.
- **Sonnet:** read-only subagents, each with only its prompt and paper (`sonnet-referee-task.txt`). Each transcript
  shows exactly two tool calls, both Reads of those files.
- **Gemini:** via agy (`gemini-3.8-flash-high`, `--sandbox`), run from an empty directory, which was still empty
  afterwards (`gemini-run.sh`).
  - The first measurement read without a preamble succeeded, and is kept in `attempts/nopreamble-*`.
  - The second failed four times: agy tried a tool, the sandbox denied it, and no output was produced
    (`attempts/empty-*`, `attempts/err-*`).
  - From then on, every Gemini input starts with `gemini-preamble.txt` ("Answer in text only…"), and both measurement
    reads were rerun with it.
- **Repeats:** two reads per referee per version, at one sample each. Model referees are advice, not peer review.

## Scores (item 7, "SCORE: n/10")

| version | Sonnet | Gemini | mean |
|---|---|---|---|
| methods draft | 4, 4 | 4, 4 | **4.0** |
| measurement, with appendix | 3, 3 | 4, 4 | **3.5** |
| measurement, as main builds it | 4, 3 | 4, 3 (no-preamble read: 3) | **3.5** |

- **Recommendation:** every read is major revision.
- **The difference:** the methods draft scores about +0.5. Sonnet moves by 1 point, and Gemini doesn't move. The
  difference is about the size of the spread between repeat reads, so this round doesn't show the methods framing
  scoring much better.

## What the referees say about the methods draft

All four reads say what the measurement reads also said, that a methods and validation paper is the kind of paper the
evidence supports. They add that the draft isn't yet that paper. The points they share:

1. **Its failures are reported but not diagnosed.**
   - Sonnet read 2 lists five unexplained anomalies:
     - the stopped coverage pre-check;
     - the fake-data prior retention;
     - the rounding instability;
     - the run-period step;
     - the 2D shape difference.
   - It then says: "a paper that says 'here are five things that do not work and we do not know why' does not give a
     reader a transferable lesson. It may be considered a progress report."
   - Sonnet read 1 and both Gemini reads say the same in other words.
2. **The sixteen-cell table, its covariance and the generator χ² sit awkwardly in a methods paper.** All four ask that
   they be removed, demoted to a supplement marked "not for fitting", or kept as an illustration only.
3. **The paper is not self-contained.** About 60 pointers go to a companion note that is not deposited, and the release
   package is not deposited either.
4. **The validation attaches to estimators other than the reported one.** Fig. 2's development variant and the
   earlier covariance's band are the examples given.

**What the referees propose instead.** Both Sonnet reads propose, as an alternative, a shorter paper with three parts:
the 2D benchmark with its non-independence stated; the prior-dependence and stability findings, from controlled
simulation studies, as the main result; and no sixteen-cell table.

**Venues named for a methods version:** JINST, Machine Learning: Science and Technology, Computer Physics
Communications, EPJ C, Physical Review Research, and Computing and Software for Big Science.

## The analyses the referees name for the methods paper

These are requests, not records, and none has been declared or run:
- the cause of the coverage pre-check's disagreement, block by block;
- a controlled prior-retention study, separating iteration count, capacity, cross-fitting and the number of observables;
- an ensemble average over rounding perturbations, as a stability remedy;
- a data/simulation comparison of the run-period step at reconstruction level, before unfolding;
- an eigenmode decomposition of the 2D shape difference.

**CITABLE FOR:** these referees' reports on the three rater copies above, and the scores they gave.

**NOT CITABLE FOR:** any physics claim, a decision, or approval of any wording.
