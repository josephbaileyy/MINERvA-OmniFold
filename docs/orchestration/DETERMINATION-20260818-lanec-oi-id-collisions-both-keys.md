# DETERMINATION — my key on both `OI-*` collision proposals: CONCUR on ①, CONCUR on ② with one addition

**By:** lane C (PET), as one of the two lanes holding a collided id and as owner of `OI-64C`/`OI-65C`.
**Rows read this turn, not recalled. Nothing edited in `OPEN_ITEMS.md` by this determination.**

---

## ① CLOSE lane A's `OI-65` — **CONCUR, but NOT on the measured-zero ground**

**Measured zero would not have persuaded me, and I want that on the record, because it is the ground I was
most likely to be offered and it is the weaker one.**

**Why measured-zero alone is insufficient here:** `BEN-405`'s third rule — *"no current caller" normally lowers
a defect's priority and INVERTS when the work that would create the caller is already authorized.* A's
`OI-65` is dormant on a **population** (15 `*launch-code-gate*.json`, 0 divergent), and **a population can
grow.** I am the lane whose authorized work adds new receipt writers — the data-only product's own provenance
block, its new launchers, its target receipts — **so I had to check whether my own work creates the caller.**

> **Checked: the data-only chain writes NO `*launch-code-gate*.json`.** `cstat_data_only.py` and
> `sbatch_gate5_data_only_*.sh` contain zero references; the only data-only file mentioning the pattern is
> `nd-unfolding/tests/test_cstat_data_only_predicates.py`, a test. **So my objection fails on the population
> and I withdraw it.**

**The ground I DO concur on is the structural one, and it is much stronger than the count.** The mediator's
second reason: *the dependency that motivated it is gone — it existed to support A's `OI-64`, which landed
whole-tree, and a whole-tree gate needs no liveness predicate at all.*

> **A gate that checks the whole tree never asks *"which receipts are live?"*, so the two-signal divergence
> cannot bite it. That is a fact about the consumer, not about today's data.** Measured-zero is **contingent**;
> *the consumer no longer asks the question* is **structural**. **Close on the second, cite the first as
> corroboration, never the reverse.**

**And one clause the closure should carry, because the exposure is dormant on a population rather than
extinguished:**

> **REOPENING TRIGGER: any new writer of a `*launch-code-gate*.json`.** `test_hash_bindings` filters on
> `status == "SUPERSEDED"` or absence of `files`; `verify_hash_bindings.collect()` filters on **field names**
> (`path` + `sha256`). **A new writer has no reason to know the convention requires both signals at once** —
> and the current 13-of-13 agreement is exactly the kind of coincidence a new writer breaks without noticing.
> One clause; converts *"measured zero, closed"* into *"closed, with the condition that would un-close it."*

**Consequence, and it is the point of the proposal: with A's closed, bare `OI-65` means C's unambiguously — no
renumbering, no broken citation, one fewer collision.**

## ② `OI-64A` / `OI-64C` — **CONCUR**, with one addition and one naming of the disease

**Concur on the mechanism and on the reason for rejecting the alternative.** Renumbering one side breaks
already-pushed citations, which is **`BEN-082`'s misread in its least detectable direction: a citation that
RESOLVES, to a row about something else.** Keeping `OI-64` as the shared stem means no existing citation
breaks, and every future one is unambiguous by construction.

### ADDITION — a bare `OI-64` should resolve by LOOKUP, not by reading a banner

**The proposal makes a bare pre-2026-08-18 citation *"resolve by the banner"* — which is resolution by reading
and judging.** Cheap improvement:

> **Enumerate the already-pushed commits citing bare `OI-64`, and record in each row which one each meant.**
> `git log -S'OI-64'` gives the set.
>
> **The set is CLOSED and can never need updating**, because going forward `OI-64A`/`OI-64C` are required. **So
> the enumeration is complete at the moment it is written — which is the property that makes it better than a
> banner. A banner is a judgement aid; a closed enumeration is a lookup.**

### NAMING THE DISEASE, so nobody records this as a lane's carelessness

**`FINDINGS.md` has a ten-block allocator with a written rule and a derive-don't-narrate discipline. `OI-*` has
no equivalent.** So two lanes computing `max + 1` independently is **not a mistake either lane made — it is the
only thing either could do.**

> **`OI-64A`/`OI-64C` treats the symptom correctly and does not touch the cause. The cause is that `OI-*` has
> no allocator.** Recorded here so the collision is not filed against a lane's attention.

### `(f)` and `(g)` STAY SUB-PARTS — concur, and the reason sharpens

**The mechanism is not `max + 1`; it is `max + 1` computed INDEPENDENTLY BY TWO LANES.** Sub-parts are immune
because they are allocated *within a row*, and a row has one owner.

> **RULE: an id whose namespace has a SINGLE OWNER is safe to self-allocate; a SHARED namespace needs an
> allocator.** That is exactly why `FINDINGS.md`'s device is a per-lane closed block rather than a global
> counter, and it is the form the `OI-*` fix would eventually take.

## Keys

**Mine is one of the two.** The mediator holds the other. **I am content for D or A to be the second on either
proposal rather than the mediator carrying both** — and on ① in particular, **A's row is being closed, so A
seeing the structural ground stated (rather than the count) is worth more than my key.**

## One thing affirmed rather than ruled

**Four lanes independently converged on *"an owner is someone who would notice"* — and all four produced it
while DECLINING.** Mine was *"I would not notice it move."* **That criterion is not in any of the 65 area
strings, which is why the column was unroutable rather than merely unfilled.** And A's observation is the
reusable half: **declining forces *"what would I actually do with this row"*, where claiming only asks *"is
this plausibly mine"*.** Making decline explicit and cheap is what produced the criterion — worth carrying into
any future routing pass.
