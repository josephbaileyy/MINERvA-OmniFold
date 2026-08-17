# A correction site inherits the trust of the index and none of its scrutiny

**BEN-393.** Filed 2026-08-17 by the seconding lane (block `390-399`). **Caught by lane B, reading my
correction** — the framing is B's suggestion that this belongs in its own row rather than inside `BEN-392`,
and B is right: *a reader looking for "how do retractions fail" will not find it filed under a transport
defect.*

## The defect

> **The entry that records a supersession is written by the party most convinced the old value is wrong, is
> read by parties who have already discharged their diligence by consulting it, and is checked by nobody.**

I added a row to `INDEX-retracted-and-superseded-values.md` to stop `28.50 A100-h` propagating. Its *what
supersedes it* column said **`39.078`, bare.** `39.078` is the **GPU column only** — the full cost of one
additional estimator seed across all four blocks is `39.223` A100-h **plus `55.337` CPU task-hours
(`2,764.7` CPU-core-hours)**, and the CPU half is the larger one, in a unit the `24 A100-h` grant does not
reach at all.

**So the mechanism added to stop one unqualified number propagating was propagating the successor's scoping
defect instead** — and doing it from the file whose own header says *READ THIS AT WRITE TIME, NOT ONLY AT
QUOTE TIME* and *treat it as a checklist for writers.*

## Why this is structurally worse than an ordinary wrong number, and not merely embarrassing

Three properties, none of which depend on this instance:

1. **An index is consulted at WRITE time by its own instruction.** A wrong number in an ordinary document
   sits there until someone quotes it. A wrong number in the supersession index is handed to authors *as they
   commit new numbers*, so its errors propagate forward into documents that do not exist yet, and they arrive
   stamped as the corrected value.
2. **It satisfies the reader's stopping condition.** Consulting the index *is* the diligence step. A reader
   who reaches it has done the thing the rule asked and stops — which is `BEN-247`'s mechanism (a partial
   success satisfies the stopping condition without satisfying the question) and `BEN-390`'s (exit `0` and a
   non-empty file are both satisfied by a dispatch that did nothing) arriving in the correction layer.
3. **The author is the worst-placed person to re-scope the successor.** A correction entry is written in the
   moment of being convinced the *old* value is wrong. All of the attention is on the delta; none is on
   whether the replacement carries its own qualifiers. That is not carelessness — it is where the writer's
   attention necessarily is.

**And nothing checks a correction.** `findings_row_lint.py` checks that a long row has a pointer;
`verify_hash_bindings.py` checks digests; the pre-commit hook runs nine checks. **None of them asks whether a
superseding value is as well-qualified as the value it replaces.** The verification effort in this repo is
aimed at first-order claims, and a correction is second-order.

## The rule

> **A supersession entry gets the same scrutiny as the value it replaces. Record the successor's scope, its
> units, and what it is NOT — and if the successor has a near-coincident sibling, name the sibling in the same
> cell.**

The last clause is what this instance needed. `39.078` (`C_syst` per seed) and `39.223` (one seed, all four
blocks) **differ by `0.37 %`, because `C_syst` is `99.63 %` of the GPU column.** A reader meeting them in
adjacent documents will assume rounding. The risk is not that someone misreads one figure; it is that **the
two become interchangeable**, which is the *"two quantities that have historically agreed at the printed
precision"* hazard the index itself already describes — now demonstrated inside the index.

## Not written as a check, deliberately

The obvious executable form — lint the *what supersedes it* column for a bare number with no unit or scope
marker — **would be a false-positive generator**, because plenty of superseded values are legitimately
unitless (a sha256, a verdict string, a count) and "carries its qualifiers" is semantic. `BEN-381` is the
precedent for refusing that trade: a check that fires on the healthy case gets switched off, and a switched-off
check is worse than a written rule. `BEN-390`'s own tool shipped exactly that defect and had to have it removed.

**What is available instead is a cheap human check with a definite answer:** for each superseding value, ask
*what unit is this in, and is there a second unit?* That question has an answer in every case, needs no
tooling, and is the one that was not asked here.

## The instance, verified

The figures, re-derived from lane B's table rather than quoted:

| | GPU (A100-h) | CPU (task-h) | CPU (core-h) |
|---|---|---|---|
| `C_syst` per seed, 189 tasks | **39.078** | 0 | 0 |
| `uthrow`, 71 tasks | 0 | **55.182** | **2759.1** |
| `C_stat` / `C_ML`, 1 task each | 0.1458 | 0.1550 | 5.58 |
| **one seed, all four blocks** | **39.223** | **55.337** | **2764.7** |
| **one COMPOSITE arm** (both seeds) | **39.078** | **55.182** | **2759.1** |

`39.078 + 0.1458 = 39.2238`; `55.182 + 0.1550 = 55.337`; `2759.1 + 5.58 = 2764.68`; `39.223 / 24 = 1.63x` the
grant; `39.078 / 39.223 = 99.63 %`.

**A composite arm cannot reuse the `uthrow` leg, and the code refuses rather than merely discourages it** —
traced by B, verified here at `nd-unfolding/unified_throw_cov.py`: `args.seed` fans out at `:244`, `:281`,
`:297`, is stamped into each slab at `:254`, `:285`, `:302`, and `:417-419` is a hard
`raise SystemExit("[FAIL] slabs carry estimator seed(s) … refusing mixed-seed combine")`. So the composite
arm's **defining move is the leg carrying essentially the whole CPU bill**, and a GPU-only figure fails
hardest exactly where it was quoted.

*(Incidental, and it closes a loop: `:416` — the comment inside that guard, `"Seed is stamped by
do_throws/do_blockunits"` — is the single surviving `jitter` mention in that file, the one `BEN-391` recorded
as the residue proving the procedure is genuinely retired. The same six lines are a verification mechanism
(`BEN-246`), a scheduling constraint (this row), and that residue.)*

## Cross-references

- `BEN-302` — a retraction reaches only as far as the corrector's map of the corpus. **This is its
  complement: even inside the map, the correction itself is unaudited.** `BEN-302` is about reach; this is
  about the quality of what arrives.
- `BEN-247` (lane B) and `BEN-390` — the stopping-condition mechanism, of which this is the correction-layer
  instance.
- `BEN-392` — the transport row this was extracted from; instance 3 there is the parent.
- `BEN-077` / `CONVENTION-receipt-ingredients.md` — the ingredients rule, whose boundary `BEN-247` named:
  every figure reconciles perfectly inside a scope that is too small.
