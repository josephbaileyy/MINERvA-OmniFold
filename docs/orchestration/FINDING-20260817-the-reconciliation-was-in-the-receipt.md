# The reconciliation was in the receipt, and three lanes reasoned about the gap without opening it

**BEN-397.** Filed 2026-08-17 by the seconding lane (block `390-399`), on a finding dispatched by peer session
`Assistant [28640e]` for landing. **Its `sacct` measurements are relayed and NOT verified here** — this host
has no Slurm. **Its conclusion is refuted, by the receipt it said it had not read**, and it named that check
itself.

## What was dispatched, and what is true

Job `56863958` (`g6_floor`, Gate-6 across-process floor, 2026-08-13). Declared `N = 5` draws; **four** payloads
on disk. Three readings existed in one day:

| reading | held by | verdict |
|---|---|---|
| draw 1 was **lost or discarded** — possibly *selectively*, which would truncate the sample by value and bias `OI-126` toward (a) | two lanes | **false** |
| draw 1 was **never submitted**, so the sample is **4 by construction** | `Assistant` | **half right: never submitted, but the sample is 5** |
| draw 1 **exists and was never a task**, by design | the receipt, all along | **true** |

**`docs/orchestration/state/gate6-floor-replication-active-56863958.json`**, read this turn:

```json
"array_tasks": "2-5",
"inventory": {
  "draw_1": {
    "source": "EXISTING nd-unfolding/pet/fullevent_ml_ensemble/member_1 artifact, reused unmodified, NOT retrained",
    "v_at_iteration_2": 0.9806897311812962,
    "d_at_iteration_2": 0.01931026881870379
  },
  "draws_2_to_5": "four new trainings, identical policy, varying only process/node/GPU"
}
```

**`N = 5` is 1 reused + 4 new. The array is `2-5` because only four needed running. `products on disk = N - 1`
is the DESIGNED state, not an anomaly.** Draw 1's value is recorded in the receipt, so nothing was dropped by
value and **the (a)-biasing worry is closed — but the sample is 5, and the floor's `n` is not 4.**

## The correction that matters, because it points the other way

The dispatched conclusion would have landed *"the sample is 4 by construction."* **A floor computed on `n = 4`
rather than `n = 5` carries a larger fractional uncertainty**, and the `OI-126` (a)-vs-(b) reading depends on
that floor. So the erroneous half was **not** conservative: it would have replaced an unfounded worry about
bias with an unfounded reduction in `n`, in the same quantity, in the same decision.

## The general rule was one step short

The dispatched rule: *"a receipt's declared `N` must be checked against the submitted array range, not against
the count of products on disk."*

**That replaces one proxy with a better proxy. It does not reach the authority.** `sacct` distinguishes *never
launched* from *launched and lost*. **Only the receipt distinguishes *never launched because it was not needed*
from *never launched by mistake*** — and those have the same `sacct` signature, exactly as *missing data* and
*missing intent* have the same product-count signature. The corrected rule:

> **A declared `N`, a submitted array range, and a product count are three different quantities. The receipt is
> the authority that reconciles them — read it before reasoning about a gap between any two.**

And the premise that motivated the dispatch — *"nothing reconciles them"* — **is false for this receipt.** It
carries the array range **and** a two-part inventory naming draw 1's provenance and its measured value. The
reconciliation was there before anyone asked.

## Why this is the day's own species, one more time

`Assistant` stated the boundary honestly and unprompted: *"I have not read the `56863958` receipt itself … If
the receipt in fact declares `N=4`, the mismatch evaporates and only the general rule survives."` **That clause
is the reason this was caught — it is `BEN-396`'s reporter's obligation working exactly as specified**, and it
is the second time today that one lane's declaration of what it had not read is what let another lane close the
question.

But the anticipated branches were *`N=5`, so a real mismatch* or *`N=4`, so no mismatch.* **The actual answer is
a third thing: `N=5` is right, four tasks is right, and both are right at once.** A dispatch that enumerates two
outcomes invites the reader to pick one — and the receipt's own words *"reused unmodified, NOT retrained"* were
never in either branch. Same shape as `BEN-391`'s instance 1: **the question was well-posed and the answer was
outside the space the question offered.**

## What is verified here and what is not

- **Verified here:** the receipt's `array_tasks`, its two-part inventory, draw 1's source and its recorded `v`
  and `d`. All from the tracked JSON at
  `docs/orchestration/state/gate6-floor-replication-active-56863958.json`.
- **Relayed, NOT verified:** every `sacct` fact — the four `COMPLETED` rows, the elapsed times, the single
  submit timestamp, the covering scan finding nothing else. **This host has no Slurm**, and a null `which
  sbatch` here is a fact about the host, not the cluster. They are `Assistant`'s and are re-derivable from the
  two commands it quoted.
- **Not chased:** `CSTAT-CLAIMS-20260814.json:95` speaks of *"the floor's `n=4` … draw 5 of `56863958` was
  still …"*, which is a **different** `n=4` — four of five complete at that time. It is adjacent and it is not
  this row's subject; flagged so nobody welds the two together.

## Cross-references

- `BEN-396` — verification allocated by suspicion, and the reporter's obligation whose discharge made this
  catchable.
- `BEN-247` (lane B) — the sibling: `55891346`'s array `[0-18]` with 5 `COMPLETED`, where the missing work was
  done in a *separate* job. **These two resolve oppositely** — there the work happened elsewhere, here it was
  never needed — so the array range is the right *first* read in both and the conclusion differs. `Assistant`
  made this pairing and it is the durable part of the dispatch.
- `BEN-391` — an answer outside the space the question offered.
- `BEN-077` / `BEN-248` — *ship what would let a reader falsify this.* This receipt did: the inventory field is
  the ingredient that refutes the reading.
