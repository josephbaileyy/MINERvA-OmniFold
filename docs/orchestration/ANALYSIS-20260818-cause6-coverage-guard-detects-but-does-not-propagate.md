# ANALYSIS 2026-08-18 — cause 6's coverage guard detects correctly and propagates nothing

**Lane D (verifier), read-only.** Dispatched by the mediator to answer one question: *would the
repair as the map describes it produce a guard that can fail in the direction it claims?* Everything
below re-derived from the tree this turn; **every ledger citation re-found by content**, per
constraint ①.

## Answer, up front

**No. And the item is not the one the map describes — not instead of it, in addition to it.**

The guard's detection is **correct**. Its propagation is **absent**. It claims to prevent
*"nobody could tell the bin had no support"*, and the only medium it uses is the one place no
downstream consumer looks. **Rebuilding `P` with the guard as it stands produces a product carrying
the original defect intact**, plus a log line. So the map's three requirements are right and its
*ordering* is missing: **the code repair must precede the cluster rebuild, or the rebuild is spent.**

## Constraint ① — the map's ledger citation is rotted

`MAP-20260817-gbdt-note-section-blockers.md` cites the quarantine at `VALIDATION_LEDGER.md:60-88`.
Measured: **`:60` is a Gate-6 table header, `:88` is `VL114`**, and the quarantine content is at
**`:135-173`** (`:173` — *"NOTHING IS ADOPTED. The 2026-07-12 quarantine stands at zero of seven for
this artifact…"*). `BEN-254`'s subject, live in the document being worked from.

## What the guard does — `nd-unfolding/eavailW_covariance.py:331-356`

```
:349   _ew_empty = np.nonzero(~Mew.any(axis=1))[0]
:350   print(f"[stat] (Eavail,W) cells receiving NO reported 5D bin: {_ew_empty.size} of {n}" …)
:353   if _ew_empty.size:
:354       print("[stat] WARNING: those bins get an exactly-zero variance … they are unsupported.")
```

The detection is right, and I checked it rather than assuming: `Mew` is `(n, report5.size)`, so
`~Mew.any(axis=1)` is per-`(Eavail,W)`-cell emptiness — the destination direction, which is the one
that matters. Entries are `dpt*dpz*dq3`, strictly positive, so `.any()` is a sound emptiness test.
The deliberate choice **not** to fail closed is also right and well argued: the `(Eavail,W)` plane is
kinematically constrained, so an empty row can be physically correct, and aborting would make a
legitimate geometry unrunnable.

## What it does not do

The guard's own comment states three verbs:

> *"So: **count it, name it, and put it in the output**, because the failure this prevents is not
> 'the code ran' but 'nobody could tell the bin had no support'."*

**`_ew_empty` appears at `:349`–`:353` and nowhere else in the file.** The output block at `:492-508`
opens `args.out` and writes histograms only — `wr_th2` for `C_syst`/`C_stat`/`C_lateral`/`C_total`,
then `hData_ew`. **No `TParameter`, no vector, no JSON. The empty-row set never reaches the
artifact.** The third verb is unimplemented.

So a downstream consumer opening the covariance has **no channel** to learn which bins are
unsupported. The zero rows are still in `C_stat`, still indistinguishable from precision, still
divided by in any χ² or per-bin ratio. The only thing that changed on 2026-08-11 is that a human
reading the job log *at run time* could have noticed — and on this filesystem `CLAUDE.md`/`BEN-028`
records stdout block-buffering at 4 MiB, so even that is not guaranteed during the run.

> **The guard cannot fail in the direction it claims.** Its claim is about what a downstream reader
> can know; its output is a print. Detection without propagation is a checked box, not a barrier.

## The test leg (`T` MET) is met by a static assertion that computation happened

`nd-unfolding/tests/test_uq_remediation.py:589-602`, `test_eavailW_detects_orphan_rows` — docstring
*"the module computes the empty-row set **and says something about it**"* — asserts exactly three
things: some `np.nonzero(...)` call exists, the string `"Mew.any(axis=1)"` is present, the string
`"_ew_empty"` is present. **Its own failure message says *"must be bound to a name and reported"* and
nothing tests reporting.**

Two things worth saying in its favour, because the suite is better than this one gap suggests:
`test_an_all_zero_projection_row_yields_a_silently_ZERO_variance` (`:567`) demonstrates the hazard
numerically and explicitly shows **PSD cannot catch it**; and `test_the_prefix_source_would_fail`
(`:604`) is a real positive control that reconstructs the pre-fix source and requires the assertions
to fail on it. **But a positive control on a static test controls only the static property.** Strip
the two `print` calls and leave `_ew_empty` computed and unused: **every test in the class still
passes.** That is the mutation nobody wrote, and it is the one the repair has to make fail.

## The repair, specified rather than applied

Lane D is read-only under a standing dispatch — *write the finding, not the change* — so this is the
diff to apply, not an applied diff. Three parts; the third is what makes the first two evidence.

1. **Write the empty-row set into `args.out`**, in the `:492-508` block, so it travels with the
   covariance rather than with the log.
2. **Write the count UNCONDITIONALLY, including zero** — and this is not a style preference, it is
   an in-repo precedent from *the same quarantine, closed on the same date*.
   `unified_throw_cov.py:482-489`:

   > *"NULL-AS-ABSENT, closed 2026-08-11 (quarantine cause 4) … Without that flag, a product built
   > without `--null` carries no null key at all, and a downstream criterion phrased as 'the null
   > norm is not large' **PASSES ON IT VACUOUSLY: absence is indistinguishable from zero.**"*

   Identical here: if `n_ew_unsupported` is written only when non-zero, a consumer cannot separate
   *"no unsupported bins"* from *"produced by a build that did not check"*. Write
   `n_ew_unsupported` and `n_ew_total` always; write the index list when non-empty.
3. **A test that asserts PROPAGATION, with the mutation that kills it.** The existing static test
   survives deleting both `print`s. The new one must open the written artifact (or the write call in
   the AST, given the ROOT/142 GB constraint the class already documents) and require the count key
   to be present — with a positive control that removes the write and requires the test to **fail**.
   *A filter needs a test in the direction it acts.*

## Consequences for the map, which is the operational half

- **The map's three requirements are correct.** Cluster rebuild, corrected upstream input, code
  repair to the coverage guard.
- **The map does not carry the ordering, and the ordering is load-bearing.** `(c)` must land before
  `(a)`. A rebuild today produces a covariance whose unsupported bins are unmarked inside the
  artifact — the exact defect cause 6 names — while `C` and `T` read as addressed.
- **`P` being open is not only "no product rebuilt."** Even after a rebuild, `P` would need the
  guard's output to exist in the product before the product could discharge the cause.

## Compute

**Nothing to price and nothing submitted.** I did not reach a runnable job: the repair is code, and
the job is `P`'s rebuild, which is not mine to specify. Per constraint ②, if it becomes runnable the
cost goes to the mediator before submission with its unit named — and note CPU is the tighter
allocation (79.9 % consumed, ~4,014 node-hours) against GPU at 64.3 %. **The ordering finding above
is a reason not to submit that rebuild yet regardless of authorization.**

## Scope note

The dispatch asked for a code repair; my standing dispatch is read-only with *"write the finding, not
the change"*, authored by a different session. I have not resolved that in the direction of action —
**the repair above is fully specified and is one commit for any lane that holds write scope.** If the
constraint's author releases it, or Joseph does, I will apply it; a peer dispatch cannot.

**A `BEN-*` row is warranted for the detects-without-propagating shape and I cannot file one: the
lane-D block `250-259` is exhausted.** Requesting a range rather than borrowing one.
