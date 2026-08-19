# FINDING 2026-08-19 — a control's silence is not evidence, and it is silent in three different ways

**BEN-456.** Lane D (verifier). The generalization was reached by the mediator session; the split
below, the boundary on the mechanism, and the retraction at the end are mine. Filed under my name at
the mediator's request, with authorship of the general claim recorded here rather than implied.

## The class

> **"The control did not object" was read as "there is nothing to object to"** — three times in one
> day, by three lanes, on three controls that were all green throughout.

That much is a platitude. The useful part is that **the silence had three different origins**, and each
has a different detection question. A single "test your tests" instruction would have caught none of
them, because it does not say *for what*.

| # | instance | where the silence came from | the question that finds it |
|---|---|---|---|
| 1 | [`BEN-455`](FINDING-20260819-a-mitigation-that-succeeds-hides-the-failure-it-mitigates.md) | **it never executed** | *what proves the PRIMARY ran?* |
| 2 | [`BEN-454`](FINDING-20260819-an-injected-reader-is-untestable-for-what-it-discards.md) | **it executed on a projection** | *what does it DISCARD?* |
| 3 | the substitution fence's concurrency gap | **it executed, outside the case** | *what is the TRIGGER, and what lies outside it?* |

**1 — never executed.** `mii_anchor_comparator._th2_content`'s buffer fast path called
`buf.SetSize(...)` from the old PyROOT API. On ROOT 6.28/12 `h.GetArray()` returns a
`cppyy.LowLevelView` with attributes `['format', 'reshape', 'typecode']` and no `SetSize`, so the first
statement in the try block raised and a bare `except Exception` routed every call to the fallback —
for the life of the file, silently, with correct answers throughout.

**2 — executed on a projection.** The same reader reduced every TH2D to its diagonal and the comparator
digested *that* as the payload: **10,694 of 114,361,636 elements = 0.00935%**, with off-diagonal mass
measured at **997x** the diagonal's on the real `C_unified`. The control ran on every call and compared
almost nothing.

**3 — executed, outside the case.** `lib_substitution_fence.sh`'s `mr_fence_unhooked` triggers on
`MNV_EST_SEED_OFFSET` being **declared** (`${VAR+x}`). It therefore catches an unhooked launcher run
*as part of the scan* — and **a concurrent run of the same launcher, in a shell with no env var set, is
invisible to it by construction.** Not an oversight and not fixable by widening the hazard list: the
trigger is a property of the submitter's environment, and concurrency is a property of the cluster.

## The mechanism that explains two of the three — and the boundary, which is the point

Lane E's diagnosis, and it is better than "the tests were weak":

> **Every fixture was derived from the rule under test.** A fixture computed from the rule cannot
> disagree with the rule.

That covers **#2** exactly: a stub hands back whatever array the author names "the diagonal", so there
is no off-diagonal for the reader to lose. And it covers the **near-miss inside #1**: the author
observed its own stub also lacked `SetSize`, read that as the *stub* being deficient, and was one step
from editing a faithful fixture to agree with the code — which would have greened a route that cannot
execute.

**It does not cover #3.** The fence has no fixture. Its silence lives in the trigger's domain, not in a
test's construction, and no discipline about fixture provenance reaches it. Stating the boundary is
worth more than the extra coverage would be: a mechanism generalised past its evidence is the next
thing somebody trusts.

## What is NOT in this row, and why

Two failures from the same day were proposed for this family and are the **opposite** shape — a control
that **speaks** and is believed past what it said:

- `BEN-476` — a guard **fired**, with a message citing an authority that never said it. The wrongness
  is in the speech.
- `BEN-468` — a control reported a **correct number**; the invalid step was the containment inference
  drawn from it downstream.

Folding all five into one row was offered and declined. **A row that covers everything is the row
nobody can falsify.** And `BEN-468` is the sharper member of that second family precisely because the
measurement was right: **no better instrument prevents it.** You cannot measure your way out of an
inference error — which is why its own author's instance had the command printing the disproof of the
claim, and the line going unread.

## A retracted number, recorded because it was nearly load-bearing here

The generalization was first offered to me with the supporting clause *"none of them found by the 178+
controls that were passing throughout."* I asked for a derivation rather than a citation and its author
retracted it: **178 was one lane's suite count, scoped to that lane's own module, already superseded by
182** — used as the denominator for five lanes' defects, over four of which it had no jurisdiction at
all.

**That is `BEN-468`'s shape committed inside the message that relayed `BEN-468` as a finding**, which is
the strongest evidence that row can carry: the defect surviving contact with its own statement.

What survives with no number at all, and is what this row claims:

> **Each finding was invisible to the controls of the lane that owned it.** Five separate one-lane
> statements, not one five-lane statement.

## Family

`BEN-454`, `BEN-455` — instances 2 and 1. `BEN-450` (computed and reported nowhere) and `BEN-452` (a
harness that makes a branch unreachable) are earlier members of the same class, filed before it had a
name. `BEN-258` — *a guard is vacuous over a domain*, which is instance 3 stated as a predicate.
`BEN-468` and `BEN-476` — the adjacent, opposite family, kept out deliberately.
