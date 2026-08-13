# BEN-119 — a power test covered the inputs and not the evidence class the conclusion rested on

Long form of `FINDINGS.md`'s `BEN-119`. Found 2026-08-12 by Lane B **while power-testing its own work**,
not by review. Sharpened by Session D, whose framing of it as a third independent *axis* is the reason it
is worth a row rather than a note.

## What happened

The HPSS residency receipt (`state/hpss-residency-inventory-20260812.json`) rested on one conclusion:
**the 322 GB copy running when the over-allocation notice arrived did not cause the overage.** Twenty
assertions were re-derived from ingredients. Baseline 20/20, exit 0. Three inputs were then corrupted on
purpose:

```
M1  hsi du total +1 MB                 -> 4 checks fail
M2  inject one content duplicate       -> 3 checks fail
M3  drop one manifest entry            -> 8 checks fail
```

All three failed correctly, in the right places, in both directions — presence (M3 sees a missing object)
and absence (M2 makes a reported zero non-zero). By any ordinary standard that is a power-tested battery.

**Every one of those mutations left the attribution checks green.** The attribution rests on
*timestamps* — notice at 06:50:13 PDT, job 06:49:24→07:22:48 PDT — and all three mutations perturbed
*bytes*. So the receipt's entire load-bearing claim was, at that moment, asserted by checks that nothing
had ever made fail. The battery was valid, thorough, and orthogonal to the conclusion.

M4 (move the notice outside the copy window) and M5 (make the big archive non-dominant) were added for
exactly that reason. Both fail. Two directions, both available, both now exercised.

## The transferable part

> **A check that carries the verdict reads as a restatement of the verdict, so it is the check least
> likely to be power-tested.** Mutating it feels like mutating the answer — obviously it fails, why test
> it — and that intuition is wrong, because "obviously it fails" is a prediction about code nobody ran.

The selection bias is systematic, not accidental: mutation candidates get chosen from the *inputs*, and a
conclusion's own checks read as outputs. The countermeasure is cheap and is not "power-test more":

> **Name the axis your battery covers, then name one it does not.** A count is not coverage. Twenty
> assertions and five mutations sounds exhaustive and said nothing about the timestamp leg.

## Three axes, none implying the others

Session D's contribution, and the reason this is distinct from `BEN-108` (which is about the *quality* of
the tests that do get power-tested — fixture, ordering, presence assertion — where this is about *which
checks get selected*):

| axis | battery covered | battery missed | finding |
|---|---|---|---|
| sibling function | the function that failed | the one beside it | `BEN-162` (D) |
| call path | the input space | the path that skips the predicate | `BEN-117` (B) |
| **evidence class** | **the inputs** | **the evidence the conclusion rests on** | **`BEN-119` (B)** |

Three axes, filed within a day by two lanes, and **passing on one says nothing about the other two.**
`BEN-117` is the sharpest precedent: there the predicate was correct *and a self-test asserted it*, and
the gate passed anyway because the answer was never consulted. Here the checks were correct and
consulted, and covered a different axis than the claim. Same family, one level along: correctness of a
check is not coverage by a check.

## What this does not license

It is not an argument for unbounded mutation. M4 and M5 were two mutations, chosen because a one-line
audit of *which checks stayed green under M1–M3* named the gap for free. That audit is the cheap part and
it is the recommendation — read the mutation results for **which assertions never moved**, not only for
whether the mutations were caught.

Also worth recording honestly: M5 overwrites its operand after the byte checks have already run, so it
exercises only the share/dominance claims. And the receipt's exclusion argument — enumerating the possible
accounting-snapshot times and showing the pre-archive case is excluded because residency was 15,694 B —
is prose reasoning with one arithmetic leg checked. **It is the conclusion's other load-bearing leg and it
is not machine-checked at all**, which is this finding pointing at itself.

## Cross-references

- The battery and its five mutations, with per-mutation failed-check lists:
  `state/hpss-residency-inventory-20260812.json`, `POWER_TEST` block (commit `50964f8`).
- `BEN-108` — power-test quality: fixture, ordering, presence assertion. Adjacent, not overlapping.
- `BEN-117`, `BEN-162`, `BEN-163` — the other axes, and the rule they share: *a remedy applied to the
  site of the last failure is not applied to the class.*
- Filed on Session D's routing: a finding about how agents fail belongs in `FINDINGS.md`, not in the
  `POWER_TEST` block of one audit's receipt, which is a record of that audit and not where a future lane
  looks.
