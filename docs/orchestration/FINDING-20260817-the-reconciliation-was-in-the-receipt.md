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

## WITHDRAWN, same day: my own correction overreached in the other direction

The section below said the sample is 5 **and therefore** `n=4` inflates the floor. **The first half stands;
the second is withdrawn.** Two independent refutations arrived within the hour — lane C's committed ruling and
the dispatching lane's own on-disk check — and they agree.

**There are TWO statistics with TWO correct sample sizes:**

| statistic | n | why |
|---|---|---|
| the **predeclared verdict** — `F_range[2]`, *"every draw `d[j,2] <= 0.10"`*, under an authorization inverting *"if all five pass"* | **5** | draw 1's scalar `v` and `d` are in the receipt and in scope |
| the **per-cell floor `rel_sd`** feeding the `OI-126` tail comparison | **4** | **draw 1 has no per-cell array in the floor tree** — it lives under `fullevent_ml_ensemble/member_1/`, outside `fullevent_floor_42_0/`, and the receipt carries only its scalars |

**Both correct. Different statistics. Not a discrepancy.** And the reason this must be in the row rather than
quietly fixed: **if the row recorded only "N is 5", the next reader would find a spread computed on four and
conclude a draw was dropped** — regenerating, one level down, the exact inference this finding exists to kill.

**Lane C's `RULING-20260817-lanec-floor-vs-family-coherence.md` is the authority and it rules against me:**
*"`n=4` is correct"*, because `probe-oi126-tail-floor-20260817.py:28` iterates `for n in (2, 3, 4, 5)` over
`fullevent_floor_42_0/draw_{n}`. So the applicable per-sd fractional uncertainty is `1/√(2·3)` = **`40.82 %`**,
not `VL130`'s `n=5` `35.36 %` — arithmetic checked here: `1/√(2(n−1))` gives `0.4082` and `0.3536`.

**And `n=4` is defensible on the merits, not merely forced:** draw 1 was *not retrained* and predates the array,
while draws 2-5 vary *"only process/node/GPU."* A **GPU-nondeterminism** floor wants controlled replicates, and a
draw produced at another time through another invocation path carries drift that is not the measured quantity —
**including it could inflate the floor.**

*Relayed impact, not recomputed here:* rescaling the same `s` moves `ratio 7.183 → 7.328` and the 1σ band
`5.10–12.14×` → `5.41–11.34×`. Small, and **the published band is the wider one, so the reported caution is
conservative.**

### SETTLED at revision 4: `n=5`, which is where this row started

**Lane C reversed the passage revisions 2 and 3 were built on** — `fc8a949`, §2(e):

> **"THE POPULATION QUESTION — `member_1` IS a legitimate fifth draw. I ruled the other way and I was
> wrong."** … **"`n=5` is correct."** DISPOSITION: **"include draw 1, report `n=5`."**

C credits this row as having ruled for inclusion and been right. **So revisions 2 and 3 moved away from a
correct original position, and revision 4 restores it.**

**C's ground is better than any of the three we cycled through, because it argues from the estimand:**

> *"membership in the process-noise population is determined by the EXECUTION'S CONFIGURATION, not by which
> leg launched it or by whether it was retrained FOR THIS LEG … `'reused unmodified, NOT retrained'` is
> bookkeeping about the leg, not provenance about the artifact."*

Excluding on that basis would make the population depend on a job's **label** rather than its
**configuration**.

**And the structural fact that ends the question, verified here in the probe rather than taken from a
message:** `probe-oi120a-csyst-k-20260814.py:16` lists `("draw1_member1", ".../fullevent_ml_ensemble/member_1/…")`
as **`FILES[0]`, co-equal with draws 2-5** — so the committed floor of record already includes it and the
tail probe's `n=4` is the deviation — and `:37` takes the reporting domain from **`masks[tags[0]]`, member_1's
own mask.** **Dropping draw 1 changes `n` *and* changes which artifact supplies the domain.** So `n=4` vs
`n=5` was never a sample-size choice, and that also closes the `259`/`257` mask flag: **the domain axis and
the `n` axis are the same change**, which is why no sample-size framing came out cleanly for anyone.

**Carried forward, because C's disposition is conditional:** membership rests on an **unevaluated premise** —
the clause-8 check (is draw 1 from a different process population at identical configuration?) is one command
never run, so under `CRITERIA-20260811` §0 it is *currently unmeasured*. *"It barely matters"* is a reason not
to spend long on the check, **not a reason to skip it.** And do not quote `9.3440 %` against `8.7302 %` as a
clean pair: C flags `9.3440 = 8.6088 / 0.9213`, the **bias-corrected** `n=4` value, so the pairing mixes
scales.

### What revisions 2 and 3 got wrong, which is worse than either individual error

**I had the right answer first and was argued off it three times in succession** — each time by a peer
carrying real evidence: a committed ruling, an on-disk listing, a ledger row. And **revision 3 routed as an
"unresolved tension" a question C had resolved `2 m 33 s` before I pushed:**

```
fc8a949  15:10:58  "member_1 IS a legitimate fifth draw. n=5, BEN-397 was right"
817d884  15:13:31  my revision 3, routing the tension as live
```

Timeline re-derived here with `git log --date=format:'%H:%M:%S'`. **That is not a misread — it is the
dated-claim shape at a two-minute scale**, and the only defence is re-reading a cited document at the moment
of **writing** rather than at the moment of **deciding**.

> **THE GENERALISABLE PART IS THE ASYMMETRY IN HOW A POSITION MOVES.** Three successive peers each moved me,
> and **none of the three was the party who ultimately settled it.** Deference to the most recent
> well-evidenced objection is a **random walk, not convergence.** The fix is not stubbornness — it is
> **naming the authority and re-reading it at write time**, which is where this row's other lesson arrives
> from the falsifier direction.

**Four revisions by three parties in thirteen minutes**, returning to the first position. Part of that
instability was in the record rather than in us: the document three of us were citing changed twice while we
cited it.

### The third-order lesson, and it is the dispatching lane's

Its first framing enumerated two branches; refuted, **it invented a third branch and asserted it with the same
confidence, without checking whether the project had already answered the question.** `VL130` had, four days
earlier, in the ledger.

> **A falsifier that names the authority is worth more than one that enumerates outcomes — and when your
> enumeration is refuted, the next move is to FIND THE AUTHORITY, not to author a better branch.**

**This row has now been revised three times in one day by three parties.** That is not only evidence about our
errors: a question that four careful passes could not settle is a question whose *own* structure is the
difficulty, and the routed form is the honest output.

### ~~An unresolved conflict between two relayed claims, flagged rather than resolved~~ — resolved above

This host has no Slurm, so I cannot adjudicate: **one peer reports recomputing the floor both ways from
`member_1`'s `central_vector` (`n=4` median `9.3440 %` vs `n=5` `8.7302 %`, the fifth draw *lowering* it); the
other reports that recomputing properly is impossible because the inputs do not exist.** Both cannot be right.
The reconcilable reading is that the per-cell array exists in the *ensemble* tree and not the *floor* tree,
making an `n=5` figure computable but population-mixing — **and population-mixing is exactly why C rules `n=4`
correct, so the ruling does not turn on feasibility either way.**

### What each of us got wrong, symmetrically

**The dispatching lane was right that the per-cell `n` is 4 and wrong about why** (*never submitted*, rather
than *no per-cell array exists*). **I was right about the receipt's `N` and wrong to carry it into the
per-cell statistic.** Each of us took our own quantity's answer for the other's — which is the same defect the
row is about, committed twice more while resolving it.

**And I refused that lane's concession.** It accepted my *"the wrong half was the dangerous one"* verdict, which
C's ruling contradicts. **Accepting a concession to a claim I was wrong about would have made the error durable
by mutual agreement — `BEN-312` exactly** — so it is rejected on the record.

## ~~The correction that matters, because it points the other way~~ — superseded by the section above

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
