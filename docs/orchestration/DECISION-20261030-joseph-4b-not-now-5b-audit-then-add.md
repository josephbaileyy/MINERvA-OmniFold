# DECISION 2026-10-30 (later) — Joseph: 4B is not funded now; the 5B run-period block is audited, then added

**Recorded by** the paper-tighten lane, as director.

**What led to it.** It follows [`DECISION-20261030-joseph-fund-1b-with-4a.md`](DECISION-20261030-joseph-fund-1b-with-4a.md).
Joseph asked for the recommendation on 4B and an explanation of the 5B choice. The director gave both before asking
again.
- **4B:** its toys resolve tail fractions only to about 0.01. Every generator χ² (109–272 for 16 d.o.f.) lies beyond
  any draw, and its truths are hybrids. The paper already presents the χ² as distances, so 4B is best reconsidered after
  1B reports.
- **5B:** the three period groups' double ratios differ beyond the bootstrap noise (`FD-CT-5B-REPORT.md`).
  - The 2D covariance already carries a run-period block (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`,
    printed in the paper's 2D section). The 16-cell covariance has none.
  - A block built from 5B has a median of 2.3 % per cell, 0.31 of the reported σ. Added in quadrature it would widen
    the total by about 5 % at the median and about 14 % in the most affected cell (the director's arithmetic).
  - The audit is needed for three reasons: the block may overlap existing flux or detector uncertainties; it rests on
    three periods; and it was chosen after the data were seen.

> 4B: follow the recommendation not to fund it now (reconsider after 1B reports)?

Joseph's answer, verbatim:

> Don't fund now (Recommended)

sha256 of the text plus a final newline begins `ea7bb41bc56ab724`.

> The 5B run-period block: which option?

Joseph's answer, verbatim:

> Audit, then add (Recommended)

sha256 of the text plus a final newline begins `368a9bc5ec9706ff`.

## What is decided

1. **4B is not funded now.** The generator χ² are presented as uncalibrated distances. 4B is reconsidered after 1B
   reports.
2. **The 5B run-period block is audited, then added to the 16-cell reported covariance.**
   - **Now:** the paper and the note print 5B beside the covariance, and state that the reported uncertainties do not
     yet include a dedicated run-period component.
   - **The audit** is declared and bound as usual. It covers:
     - overlap with the existing covariance blocks, especially the flux and detector-response ones;
     - the noise treatment, with ten bootstrap replicas per period;
     - why 5B's cell pattern differs from 5A's projection, although their sizes agree;
     - the rank-two construction.
     It states before it runs what result would stop the addition.
   - **Then:** the block is added unless the audit's stop condition fires. The results are published with and without
     it, and the record states that the decision followed the data.
   - The revised covariance flows through every downstream product: the result table, the generator χ², and the F1 and
     flux-bootstrap readouts where they use the matrix. It reaches the paper through the usual truth and register
     checks.
3. **1B's coverage test uses the covariance as it stands when 1B is declared.** If the block is added later, the
   report says which matrix 1B tested.

## Not changed

- Every claim, until the audited block lands. Nothing is submitted, deposited or tagged.
