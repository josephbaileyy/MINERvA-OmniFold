# A one-sided review searches the diff for the defect and never searches the sources for the remedy

**Mediator, 2026-08-18. `BEN-307`.** Reviewing the documentation control-plane migration, I raised a hazard —
*"if any generated view republishes a BEN free-list, there are now two stale-able free-lists instead of one, and
the generated one is worse because it carries an implicit freshness claim"* — and asked the author twice.

**The migration had already anticipated it.** `docs/orchestration/control-plane/playbook.tsv:4`:

> **PB-03** — Derive identifiers, counts, and free ranges in the same turn. Include the command and denominator;
> never copy a narrated free-list or remembered count. *(BEN-027, BEN-080, BEN-228)*

So the change did not create the hazard; it **encoded the rule against it**, cited to the three findings the rule
came from. My review found a risk that the artifact under review had already closed — and I asked about it twice,
in two separate messages, because the second ask was written from the same one-sided reading as the first.

## The shape

**I searched the diff for the presence of a bad thing. I never searched the sources for the presence of the
remedy.** Those are different searches over different corpora:

| question | corpus | what I ran |
|---|---|---|
| does this change introduce the hazard? | the **diff** | grep for a free-list in the changed lines |
| does this change already mitigate the hazard? | the **new sources** | *nothing* |

The second corpus existed, was checked in, and was small — five TSV/JSON files plus one generated markdown. The
mitigation was one line of it.

## Why the reviewer's incentive points this way

A review is framed as *finding problems*, so the search that feels like reviewing is the search for defects. The
search for mitigations feels like the author's job. But **a hazard that the change already closes is not a
finding — it is a false positive with a long tail**, because the author must spend a round-trip proving a
negative, and the reviewer's second ask (mine) arrives with more confidence than the first.

Two costs, and the second is worse:

1. The author answered a question about their own work that their own work already answered.
2. **I passed the un-mitigated version of the hazard to a lane as an instruction** — *"ignore any generated
   free-list on sight"* — which is advice for a world that does not exist. A lane following it would have been
   guarding against a thing the enforced rule already prevents, and would not have known PB-03 existed.

A third lane produced the better instruction from the same facts: **there is no generated free-list, and PB-03 is
why.** That version routes the reader to the mechanism; mine routed them to a vigilance.

## The check

Before raising a hazard against a change, run the second search:

> **Does the change already contain the mitigation?** Grep the *added* sources — not the diff of the files you
> were worried about — for the rule, the constant, or the guard that would close it.

If the change is large, the added-sources corpus is usually the smallest one in the review, because it is exactly
the material the author wrote on purpose.

## What this is not

This is not an argument against raising hazards under uncertainty. My first ask was correct: I could not answer it
from the diff and I said so. **The defect is that I did not run the search that would have answered it**, and then
asked a second time on the same evidence, and then acted on the un-mitigated reading downstream.

## Related

`BEN-305` (a relay launders a hypothesis into a campaign fact — same lane, same day, and the downstream
instruction here is that mechanism again). `BEN-306` (a check whose domain is not the claim's domain).
`BEN-483`'s family — *the domain of the check is not the domain of the claim*; here the domain was right for the
question asked and the **question was one of a pair**.
