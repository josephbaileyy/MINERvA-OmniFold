# FINDING 2026-08-18 — "cannot fail" is a two-place predicate, and deleting a vacuous guard can delete a spec

**BEN-258.** Lane D (verifier). **Lane E found the first instance (`:46`) and owns the launcher-repair
row**; this row is the general claim and the second instance, and it exists because the remedy the
first instance implies is wrong here. Mediator confirmed both halves independently.

## The claim

> **A guard is not vacuous. A guard is vacuous *over a domain*.** `cannot-fail` is a two-place
> predicate — check × input domain — and reporting it as a property of the check alone throws away
> the information that decides what to do about it.

The standard remedy for a check that cannot fail is to delete it. **That is right when the input can
never vary, and wrong when a change already on the table is about to make it vary** — and *you cannot
tell which from the guard*.

## The instance

`submit_gate5_data_only_n50.sh`:

```
:20  DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold          <- a LITERAL
:30  OUTPUT_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50
:31  THREE_STREAM_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
:46  [[ "$OUTPUT_ROOT" != "$THREE_STREAM_ROOT" ]] || die "L1 output root is the three-stream root"
:47  case "$OUTPUT_ROOT" in *fullevent_cstat_data_only_n50) ;; *) die "L1 unexpected output root" ;; esac
```

Both operands of `:46` are `$DATA_ROOT` plus a **fixed differing suffix**, so it cannot fail for any
`DATA_ROOT`. `:47` matches unconditionally, because `:30` appends the very suffix `:47` tests for.
**Two vacuous guards, not one** — and `:47` is the line proposed as *"the one doing real work"* when
only `:46` had been found. The second was invisible until the first was named.

**They are vacuous because `DATA_ROOT` is a literal.** That is a fact about `:20`, not about `:46`
and `:47`.

## Why deletion is the wrong remedy here

The rebuild needs a disjoint tree, and the route chosen is to make `:20` overridable
(`${GATE5_DATA_ROOT:-…}`) rather than to rename the family directory — a rename fails `L2`
(`cstat_data_only.py:266-290` tests a path **component** against `FAMILY_ROOTS`) and would cost an
edit to a deployment-parity-checked module.

**That change creates a failure mode that does not exist today:** `GATE5_DATA_ROOT` set to a path that
itself contains a family-root component. Then

```
GATE5_DATA_ROOT=/…/fullevent_cstat_n50
  -> OUTPUT_ROOT=/…/fullevent_cstat_n50/nd-unfolding/pet/fullevent_cstat_data_only_n50
```

`:46` passes. `:47` passes. The **only** thing that catches it is `L2`'s
`clash = parts & others` (`:285-289`) — in Python, at the builder's first call, after submission.

So the repair is not deletion. It is **the guard the change makes checkable**: *`GATE5_DATA_ROOT` must
contain neither family-root component* — non-vacuous **only after** the override lands, and firing
before submission rather than at the builder.

> **A vacuous guard is not always dead code. Sometimes it is a guard whose input has not yet been
> allowed to vary.**

## The detection question

For each check found unable to fail, ask **what would have to become variable for this to fire.**

- If the answer is *"nothing — the operand is a constant of the design"*, it is dead code. Delete it.
- If the answer **names a change already proposed**, the guard is a **specification**, not dead code,
  and deleting it removes the only written statement of a precondition at the moment that
  precondition starts to matter.

Cheap, because it is asked only of checks already found vacuous — a set someone has just enumerated.

## What this does and does not revise

**Refines `BEN-250`** (*a check whose strongest statement could not fail*) by making its domain
explicit: every `cannot-fail` verdict in that family should name the domain it was evaluated over.
`BEN-256`'s Rule 2 is the same idea from the other side — a value that is a sentinel at one site and
legitimate input at another.

**It does not revise `BEN-256` amendment 1**, and it is worth saying so rather than leaving the
inference open. I withdrew a recommended limb there for two reasons, and only the first is
domain-relative: no reachable execution separated the operands, *and* the lone hypothetical that could
have — a `chdir` with a relative path — would have been detecting a `chdir`, not a wrong target. **The
second reason survives any widening of the domain**, so widening does not rescue that limb.

## Family

- `BEN-250` — a check whose strongest statement could not fail. **Domain left implicit.**
- `BEN-255` — a check evaluated on the wrong population. *Which rows*, where this is *which values*.
- `BEN-256` — one field, two roles. Rule 2 is this finding's mirror image.
- **`BEN-258`** — a check evaluated over a domain too narrow for it to fire, **where the domain is
  about to widen.** The check is sound and its input is not yet interesting.
