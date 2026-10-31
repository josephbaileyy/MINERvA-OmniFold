# DECISION 2026-10-31 (later) — Joseph: J1 and J2 as recommended; the protections split into "meaning fixed, wording reviewable"

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The paper lane's presentation proposal ([`PROPOSAL-20261031-5b-with-without.md`](PROPOSAL-20261031-5b-with-without.md),
  #609) and the independent referee consult on it
  ([`state/2d-closeout/stageF/methods/secondary-results/astra-consult-5b-presentation-20261031/REPORT.md`](state/2d-closeout/stageF/methods/secondary-results/astra-consult-5b-presentation-20261031/REPORT.md),
  #610).
- The independent editor's consult on the remaining protections
  ([`state/2d-closeout/stageF/methods/secondary-results/astra-consult-protections-20261031/REPORT.md`](state/2d-closeout/stageF/methods/secondary-results/astra-consult-protections-20261031/REPORT.md),
  #612).

> J1: how should the paper state the fake-data result? (Independent referee and I both recommend stating both.)

Joseph's answer, verbatim:

> State both (Recommended)

sha256 of the text plus a final newline begins `403cc75bd8bf272d`.

> J2: Table IV generator χ². (Referee and I both recommend adding the without-block columns.)

Joseph's answer, verbatim:

> Add without-block columns (Recommended)

sha256 of the text plus a final newline begins `767f3478cf9d596e`.

> Remaining protections: adopt the referee's split (keep meaning/truth/title/holds/credit strict; make DA wording, abstracts, claim-scoping wording, the frozen coverage sentence and the build-checked phrases 'meaning fixed, wording reviewable')?

Joseph's answer, verbatim:

> Adopt the split (Recommended)

sha256 of the text plus a final newline begins `8edfe3992c501799`.

## What is decided

1. **J1: both fake-data lists are stated.**
   - The body names the truths listed under the reported covariance: the GiBUU hybrid and the q3 tilt. It adds that
     without C_PL,5D the GiBUU E_avail shape is also listed, in R06 (z = 2.01 without, 1.76 with). The listing criterion
     sits beside it.
   - The abstract says "at a GiBUU-like truth or at a synthetic q3 tilt", phrased as the bias exceeding the stated
     thresholds, never as coverage.
   - The note's abstract and executive summary match.
   - The referee's corrections apply: a median rise of about 7.8 %, total χ² falls of 3.6–30.5 %, the geometry sentence
     marked as inference, and "the other 10 truths" under the reported covariance.
2. **J2: Table IV gains without-block columns.**
   - Two column groups, "reported covariance" and "without C_PL,5D", each with χ² and shape-only χ², both including V_g.
   - Option B's 16-cell and 8-cell blocks are kept, with ndf given once per block. The caption is amended.
   - The note's Table 16 matches.
3. **The protections split:**
   - **Strict, unchanged:** scientific meaning and claims (A7) in substance, the truth guardrail, the title (A5),
     `\pubhold`, the acknowledgments and named credit, and the C items' mandatory publication.
   - **Meaning fixed, wording reviewable:**
     - **A1 Data Availability:** editorial changes are checked against the package manifest. Joseph approves any
       release commitment.
     - **A4 abstracts:** Joseph approves the complete revised abstract, not each edit.
     - **A7 claim-scoping sentences:** equivalent wording is allowed after a documented equivalence review (populations,
       assumptions, uncertainty, strength and conclusion unchanged). Anything unresolved goes to Joseph.
     - **The FROZEN coverage sentence:** an equivalent formulation is allowed, with its meaning and placement kept.
     - **B4 gate-bound phrases:** they may be reworded together with their gate updates, keeping receipt-linked
       numbers, units, scope and citation targets.
   - This resolves the record inconsistency the editor flagged on Data Availability (DECISION-20261028 against the
     10-30 pinned-pair requirement) in favour of this rule.

## Not changed

- Every number. Nothing is submitted, deposited or tagged.
