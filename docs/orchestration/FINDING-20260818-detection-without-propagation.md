# FINDING 2026-08-18 — detection without propagation, and the test that cannot see the difference

**BEN-450.** Lane D (verifier), read-only. First filing in block `450-459`. **The instance and its
evidence live in
[`ANALYSIS-20260818-cause6-coverage-guard-detects-but-does-not-propagate.md`](ANALYSIS-20260818-cause6-coverage-guard-detects-but-does-not-propagate.md)**
and are not re-narrated here; this row is the transferable shape.

## The shape

> A guard computes the right thing, reports it to a channel **no downstream consumer reads**, and is
> then recorded as closing the hazard. **Detection without propagation is a checked box, not a
> barrier** — and the artifact still carries the defect the guard was written to make visible.

The tell is a mismatch between what the guard's own comment promises and what its code does with the
value. `eavailW_covariance.py`'s guard promises three verbs — *"count it, name it, and **put it in
the output**"* — and implements the first two to `stdout`. The name is computed at `:349`, printed,
and **never referenced again**; the output block writes histograms only.

**A guard whose claim is about what a reader can know, delivered through a channel the reader does
not read.** Here the channel is worse than merely unread: `BEN-028` records that on this Lustre
filesystem `stdout` block-buffers at 4 MiB, so the line is not guaranteed to appear even to someone
watching the job.

## Why the test could not catch it

The test asserts that the value is **computed** — a `np.nonzero` call exists, two source strings are
present — while its own failure message says the value *"must be bound to a name **and reported**"*.
Nothing tests reporting.

> **Delete both `print`s, leave the value computed and unused, and every test in the class passes.**

That is the mutation nobody wrote. And the class is otherwise *good*: it demonstrates the hazard
numerically, shows explicitly that a PSD check cannot catch it, and carries a pre-fix positive
control that reconstructs the unguarded source and requires the assertions to fail on it. So:

> **A positive control on a static test controls only the static property.** It proves the string
> would be absent before the fix. It cannot prove the string does anything.

This is `BEN-258`'s third category reached from the other side — there, a live guard that had never
fired; here, a *test* that has never been exercised against the behaviour it names.

## The ordering consequence, which is the operational half

**A detect-only guard makes the rebuild that consumes it a waste.** Cause 6's map lists three
requirements — cluster rebuild, corrected upstream input, code repair — and does not order them.
**The repair must precede the rebuild**, or the rebuild produces an artifact whose unsupported bins
are unmarked *inside the artifact*, which is the defect the cause names, while the `C` and `T` legs
read as addressed.

Generalised: **when a guard's output is meant to travel with a product, the guard is a precondition
of producing the product, not a check on it.** Ordering a detect-only guard after its product is
spending the compute twice.

## The rules

1. **A guard that reports must name its consumer.** *Who reads this, from where?* If the answer is
   "a person watching the log", the guard closes nothing durable.
2. **Write the negative case unconditionally.** In-repo precedent from the *same quarantine, closed
   the same date* — `unified_throw_cov.py:482-489`, `fixed_seed_null_checked`: *"absence is
   indistinguishable from zero"*, so a criterion phrased as *"the count is not large"* **passes
   vacuously** on a product built without the check. `n_ew_unsupported` must be written even when
   it is `0`.
3. **A guard's test must assert PROPAGATION, with the mutation that kills it** — remove the write,
   require the test to fail. *A filter needs a test in the direction it acts.*

## Family

- `BEN-250` — a check whose strongest statement could not fail.
- `BEN-255` — a check evaluated on the wrong population.
- `BEN-258` — `cannot-fail` is a two-place predicate; amendment 1's third category is the sibling of
  the test gap above.
- `BEN-259` — a promise whose precondition carries the same exposure as the thing it justifies.
- **`BEN-450`** — a check that is **correct, and mute where it counts.** The computation is right; the
  result does not leave the process.
