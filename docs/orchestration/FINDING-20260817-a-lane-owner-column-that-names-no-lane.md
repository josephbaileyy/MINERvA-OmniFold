# A column named `lane/owner` whose cells are mostly not owners

**BEN-395.** Filed 2026-08-17 by the seconding lane (block `390-399`), answering the mediator's request to
establish which lane `OI-58`'s hop-1 fix routes to — **by reading the row, not by inferring from who has been
active near it.**

## The answer to the routing question

**`OI-58` routes its hop-1 fix to nobody.**

`docs/OPEN_ITEMS.md:61` — the table header — is:

```
| id | state | lane/owner | blocker | next action | detail | as_of |
```

**`OI-58`'s `lane/owner` cell is `PET / Gate 5 quoting`.** An area and a topic. No lane, no person. The only
lane names anywhere in the row are *attributions of findings*, not assignments: `(Session D; publication path
and refusal both verified by the mediator.)` for the original defect, and `CONFIRMED INDEPENDENTLY 2026-08-17
(lane E)` for the pin claim. **Neither is an owner**, and reading either as one is the error the request was
written to avoid.

## Measured across the table, because one row is an anecdote

`oi_owner_report.py` (committed beside this file):

| classification | rows |
|---|---|
| names a lane or person — **routable from the row** | 25 |
| explicitly `unowned` | 2 |
| closed | 1 |
| **area only — cannot be routed from the row** | **65** |
| total | 93 |

**So 70 % of the table cannot be routed from its own row, and `OI-58` is not specially orphaned — it is
typical.** `OI-57`, the hop-1 row `OI-58` points at, is in the same bucket.

## The predicted outcome was different, and the real one is cheaper to fix

The request anticipated *"the row names a lane that no longer exists as a live session — that is the more
likely outcome and it is the actual finding."* It does not. **The field names no lane at all.**

That difference matters because of what it does to a reader: **a populated cell in a column called
`lane/owner` reads as ownership.** An obviously blank owner sends you looking; `PET / Gate 5 quoting` does
not. **This is `BEN-247`'s mechanism in the control plane — a non-empty cell satisfies the check that an empty
one would have forced** — and it is the third instance of that shape filed today, after a partially-`COMPLETED`
job id and a delegate exiting 0 with 303 bytes of prose.

## The convention exists and is not applied

All three states already have vocabulary **in this table**:

- **a lane or person** — `C (PET)`, `lane D`, `Joseph`, `peer session B`
- **explicitly none** — `OI-130`: *"analysis-note evidence / unowned"*
- **subject vs filer**, in the newest rows — `OI-124`: *"lane D (subject — probe owner); verdict-repair lane
  (filing)"*; `OI-126`: *"PET lane / Joseph (subject); peer session `B` (filing only)"*

So nothing needs inventing. And `OI-130`'s `unowned` is what makes `OI-58`'s cell **distinguishable from a
deliberate non-assignment** rather than merely ambiguous: the table can say "nobody owns this," and `OI-58`
does not say it.

## The cost, measured rather than asserted

Lane E declined this item — graded the best-evidenced cheap item on the PET list, reproducing on two
independent instruments — because *"its row routes it to another lane and I would not take it unowned."*
**The row does not route it to another lane.** E reached the right outcome (do not take an unowned item) from
a premise the row does not support, and the mediator then left the routing ambient for a session, by its own
account.

**A correct outcome from a false premise, twice in one day** — `BEN-394`'s `DO NOT WIRE IT` hook comment,
which was right while the `THE TRIGGER FIRED` clause beside it was false, is the other. Both were harmless
this time. Neither mechanism generalises.

## `%an` is not a lane field either

The second half of the request, and it is the reason none of this can be recovered from git. Some commits
carry `Lane C (PET)` or `Lane B (Gate 6)` as the author; others carry `Joseph Bailey` because the shared
identity was used, with the lane self-declared in the commit **body** (`SCOPE: lane = …`). **So neither the
ledger's owner column nor the git author answers *whose is this*, and the only reliable source is a `SCOPE:`
line somebody chose to write.** `BEN-214` and `BEN-330` are the prior instances of attribution drift under a
shared identity; this row adds that the *designated* owner field is no better.

## Report shipped, deliberately not a gate

`oi_owner_report.py` classifies every row and will list the 65 with `--list-area-only`. **It must not become a
hook check until the backlog is dispositioned:** it fails on 65 pre-existing rows, so a committer editing an
unrelated row could not make it pass, which violates the dispatcher's admitting rule at
`.githooks/pre-commit:11` — *a check belongs here iff a committer who did nothing wrong can always make it
pass* (lane D, `OI-64`). **That constraint is written in the script's docstring rather than left for whoever
tries it**, which is the only part of this that is cheap to get wrong later.

## `OI-58` not taken, and why beyond ownership

**A row that assigns nobody is not thereby assigned to whoever reads it.** Three further reasons, none of
which depend on the routing answer:

1. **Lane E's caveat travels with any cell from that table: a pin sweep can tell you an item is expensive and
   can never tell you it is cheap.** *"Clean on both instruments"* is a statement about hashes, not
   feasibility. `OI-61(b)` was clean on both and was refuted by an `argparse` `choices=` list in the pinned
   callee within minutes (`BEN-386`).
2. **The row's own next-action column carries an unresolved design choice**, not just an edit: mirror
   `:99-101` (proves *file == receipt*) versus bind to `GATE5_EXPECTED_INPUT_SHA`, the frozen canonical
   constant that `submit_gate5_replica_n50.sh:48` exports and **no Python reads**. The row recommends
   requiring both. That is a decision, and picking it silently is how an unowned item becomes an owned defect.
3. **It reaches production only when `CODE_ROOT` syncs, which `OI-74` blocks**, and the row says the fix
   *must not motivate a Gate-5 re-issue — it should ride one.*

Routed back to the mediator for an explicit assignment or an explicit `unowned`.

## Cross-references

- `BEN-247` (lane B) — a partial success satisfies the stopping condition without satisfying the question.
- `BEN-244` — a decision that reached its own record and nowhere else; the `OI-*` namespace's prior
  addressing failure, and the row noting `OI-*` ids have no block table and no addressing convention.
- `BEN-380` — a definite description is not a citation. An area in an owner field is the same defect: it
  denotes until you try to act on it.
- `BEN-394` — a correct conclusion resting on a false premise, the other instance from today.
- `BEN-386` (lane E) — the caveat that must travel with any "cheap" grading from the pin sweep.
