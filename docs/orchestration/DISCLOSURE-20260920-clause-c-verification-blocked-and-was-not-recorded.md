# DISCLOSURE 2026-09-20 — the §6.4 clause-(c) verification returned BLOCK, and the adoption record did not say so

**CITABLE FOR:** the existence, verdict and location of the independent verification requested to
discharge §6.4 sub-clause (c), and the fact that `main`'s adoption record omitted it.
**NOT CITABLE FOR:** any re-grade, any withdrawal of the adoption, or any scientific claim in the
verification itself. This record discloses; it decides nothing.

Subject: [`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`](DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
and [`AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md`](AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md).

## 1. The condition

§6.4 sub-clause **(c)**, verbatim from the amendment:

> **(c)** **Adoption of this digest may proceed notwithstanding (a)** if and only if the remaining
> required evidence is complete and independently verified. **(c) is a permission to decide, not a
> decision, and not evidence.**

It is an **iff**. The independent verification is a precondition of the adoption, not a follow-up to it.

## 2. The verification exists, and its verdict is BLOCK

`VERIFICATION-20260918-scalar5d-adopt-clause-c.md`, owner `z-independent-assessor`, base `5be86f55`.

| branch | `lane/z-criteria-independent-assessment-20260910` |
|---|---|
| head | `935b75585a7b9cc39cd52d4aa001df4edbea875f` |
| reach it without a merge | `git fetch origin 935b75585a7b9cc39cd52d4aa001df4edbea875f` |

| question | verdict |
|---|---|
| **(1) Is the required evidence complete?** | **BLOCK.** Originally on three grounds; `V1` was closed (verified in an artifact) and `V3` reclassified to a disclosure. **The BLOCK stands on `V2` alone.** |
| **(2) Are the load-bearing claims true as measured?** | **PASS on everything the assessor could reach**, with two wording defects (`V5`) and six claims named individually as not reproduced (`V6`). |

## 3. What `V2` is — and what it is not

`V2` is a **who-may-sign** block. **C5's and C7's evidence in the blocker table is the assessor's own
work**: C5's *"falsifier NEGATIVE across the 15 modules Z invokes"* is their finding committed at
`80b464ca`, and C7's *"all four weight-only bands present in R"* is their own `X5` scope clarification
from the same commit. Their words:

> **I cannot independently verify my own findings.** … It applies to me on C5 and C7, and it makes
> clause (c) inert for those two rows if I sign them. … **Nothing about them is suspect; the routing is.**

The assessor drew the distinction deliberately: re-measuring **a digest or a count** they previously
measured is fine, because independence is about **judgement**, not arithmetic. What they cannot do is
certify their own **verdicts**.

**So the BLOCK is not a finding against the science.** It reports that the independence half of an
**iff about independence** was not satisfiable by that assessor for two of the rows. Question (2)
returned PASS on everything reachable, and `V4` exercised the guards on the real path with a working
positive control — six refusals fired and the control proceeded, so the refusals discriminate.

## 4. THE OMISSION — Joseph's, and stated as his

**Joseph's adoption of 2026-09-20 proceeded without this verification, its BLOCK, or clause (c)
being recorded anywhere in the adoption record.** Measured on `main` at the time of writing: the
string `independent`, the string `clause (c)` and the string `BLOCK` each occur **zero** times in
`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`.

`main` is not silent about the verification file — `OPERATIVE-SHEET-scalar5d.md` names it and
resolves a dispute about which commit it was measured against. But that is its **base**, not its
**verdict**, and no file on `main` carried the verdict until this one.

**This is Joseph's omission to disclose and he is disclosing it.** The record exists so that an
auditor reading only `main` finds the iff, the adoption, **and** the fact that the iff's independence
half was tested and came back BLOCK — rather than finding the first two and having to discover the
third from a branch.

## 5. ⚠ ONE SCOPING CAVEAT ON THIS RECORD'S OWN FOOTING

`clause (c)` is **overloaded** in this repository. There is an expiry clause (c) — *"Clause (c) of the
B1 steps 4-5 pause"*, `VERDICT-20260821-expiry-c-real-path-present-seed.md`, with its own verifier —
and the B1-lift clause (c) of `DECISION-20260822-joseph-b1-lift-and-clause-c.md`. Both are from
2026-08 and concern the B1 pause and the identity axis.

**The 2026-09-18 assessment never quotes §6.4's clause-(c) text and cites no `SPEC` section.** Its
only clause citation is its own header, which carries the **requester's** framing. The identification
above is therefore made **by content, not by citation**, on four grounds, each checkable:

1. it is scoped to the scalar-5D publication blocker table (`C1`–`C7`, `R5`, `NULL`), which is the
   set `DECISION-PACKET-20260918` §2 titles *"required deliverables only"*;
2. it is framed throughout as *"ahead of a scalar-5D **ADOPT**"*;
3. its base `5be86f55` is the commit that landed the §6.4 amendment itself;
4. `V2`'s entire argument is about **independence** — the word clause (c) turns on — and nothing in
   the B1-pause clause concerns independence.

The amendment's *"the remaining required evidence"* is a **definite description**; the amendment does
not enumerate it or route it to the packet. **The link from clause (c) to the §2 table is an
inference, stated here as one.** If that link is wrong, §4's omission claim narrows to *"an
independent verification of the required set returned BLOCK and was not recorded"*, which is still
true and still worth disclosing.

## 5b. ⚠ DISPOSED 2026-09-20 — read this before acting on anything above

**Clause (c) has since been disposed of:**
[`DECISION-20260920-joseph-rules-clause-c-disposition.md`](DECISION-20260920-joseph-rules-clause-c-disposition.md).
`V2` — the sole surviving ground of the `BLOCK` — is **discharged** by a third lane
([`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md)),
`V6` is **ruled outside** clause (c)'s scope, and the ordering defect this record discloses is
**ratified retrospectively and NOT cured**.

**Everything this record states remains true as of the moment it was written, and §4's omission
happened.** What has changed is that it is now answered. The two limitations that survive are
carried at that decision's §5, and the sentence in §6 below — *"Only a lane that authored none of
C5's or C7's evidence can"* — is exactly what was done.

## 6. What this record does NOT do

- It does not withdraw or qualify the adoption. That is Joseph's and he has not made it.
- It does not discharge clause (c). **Only a lane that authored none of C5's or C7's evidence can**,
  and routing that is open — see §3's *"C5 and C7 need a third lane."*
- It does not adjudicate `V5` or `V6`. Those are on the branch and are reachable by the SHA above.

**Co-Authored-By: Claude Opus 5 (1M context)**
