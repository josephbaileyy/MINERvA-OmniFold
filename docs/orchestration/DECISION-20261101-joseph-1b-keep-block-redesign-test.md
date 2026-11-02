# DECISION 2026-11-01 (later) — Joseph: keep the full-simulation block; redesign the coverage test, then run coverage

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The investigation's result.** The 1B gate-D investigation's I2 step read H1 → O1 (#650, merged at `da277773`).
Gate D's pseudo-experiments realize a response-only shift at fixed truth. S1's reported interaction block is the
full-universe shift: the response and the prior move together, and the data are re-unfolded. So gate D compared unlike
objects.

**What it left open.** Additivity A ≈ B + C failed. R00 and R05 are not explained by the interaction group.

**The review and consult.** The director's review and an independent Sonnet consult are in
[`FD-1B-INV-I2-DIRECTOR-REVIEW.md`](state/measurement-paper/5d-community-20261024/FD-1B-INV-I2-DIRECTOR-REVIEW.md) and
its consult files (#652). The consult recommended two things:
- keep the full-universe block;
- test a redesigned toy that realizes the same object, then the held-out-tune coverage ensemble.

The director agreed.

## Joseph's answers, verbatim

1. Asked which interaction uncertainty the reported covariance should carry:

   > Keep full-simulation block (Recommended)

   sha256 of the text plus a final newline begins `1bf7e92dea50d952`.
2. Asked what to do next to try to remove the "coverage not validated" qualification:

   > Redesigned test, then coverage (Recommended)

   sha256 begins `07aa097395374e40`.

## What is decided

1. **The reported covariance is unchanged.** Its interaction block stays S1's full-universe block.
   - The response-only spread B goes to the note as a sensitivity. It is a median 1.65× larger in σ (range
     0.42–6.50).
   - Its label says it depends on the fine-cell grid and is not a bound.
2. **Binding condition (a)'s question is answered:** the intervals do not carry var(r). The first-order algebra the
   question rested on was not shown by I2. That is recorded beside the answer.
3. **Next: a redesigned test (mode D).** coverage-5b declares it, coverage-5b-audit reviews it, and the director binds
   it before anything runs.
   - **The pseudo-data.** Each pseudo-dataset is the simulation with each universe's event weights applied to truth,
     reconstruction and background together. Nature is the universe.
   - **The unfolding.** They are unfolded with the nominal simulation.
   - **The comparison.** The resulting block is compared with S1's block, cell by cell, in the same [0.9, 1.1]
     window. The outcome table is fixed before any number is read.
   - **The grid check rides along.** It reruns B and C for a few universes on a coarser and a finer fine-cell grid.
   - **Cost.** The run is priced from measured per-unfold costs. Its cap is set in the declaration under
     `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`.
4. **If mode D passes, the coverage ensemble follows.** It uses held-out tunes and full-universe draws at a data-like
   truth.
   - It is declared, priced and bound before it runs.
   - It is graded against the reported covariance, at a window fixed in advance.
   - Only this ensemble can remove the qualification.
5. **If mode D fails, the result comes back to Joseph.** No toy, window or covariance change follows from a failure
   without him.
6. **Unchanged:**
   - the paper's wording, until a result lands (the disclosure of the stopped attempt stays);
   - gate D's verdict, the diagnosis and I0;
   - every claim and number.

Nothing is submitted, deposited or tagged.
