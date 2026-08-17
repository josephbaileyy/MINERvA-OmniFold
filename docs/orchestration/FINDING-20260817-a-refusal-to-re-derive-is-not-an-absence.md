# A refusal to re-derive is not an absence — evidence sitting unread behind a correctly-stated refusal

**Row:** `BEN-239` (lane C, PET — the id that exhausts block `230-239`).
**Date:** 2026-08-17. **Artifacts:** `SCOREBOARD-20260817-quarantine-seven-causes.md` §4;
`VALIDATION_LEDGER.md` `VL66`, declaration landed at `d1c5f90`.
**Class:** the **inverse** of every other cell on the quarantine scoreboard. Those are claims outrunning
their evidence. This is **evidence outrunning its readers**.

---

## 1. What happened

Lane C — **cause 5's owner** — graded cause 5 `N/A for X — UNDECLARED` on the seven-cause scoreboard. The
grade's content was precise and, as a grade, correct in form: *nobody outside the owning lane had said the
cause does not reach X, and a quorum containing the owner is thin.*

**The answering document already existed.** `DETERMINATION-20260811-cause5-binding-half.md` §7
(`:233-237`, *"What this determination does not do"*) states that the §3 magnitudes are recoil and
therefore **"a different estimator."** Assistant then traced the one route by which cause 5 could reach X
and found it absent:

- X's background is **MC-derived** — `sweep_bank_5d.py:171-177`, `f.Get("mc_background")` plus the
  per-universe `w_bkg_{band}_{i}` branches;
- the estimator is **`lgbm` on every leg**;
- the recoil-PET budget is a **downstream consumer** of the shared bkgaware bank, **not an input to it**.

Declared in `VL66` at `d1c5f90`, by a non-owner lane, landed by a third.

## 2. The mechanism

Lane C graded `UNDECLARED` **partly because** the routing map's §2 said, of the determination:

> *"I did not re-derive it and do not summarise its verdict."*

**Two documents declining to RE-DERIVE cause 5 compounded into the appearance of an evidentiary gap where
there was a READING gap.** The determination declined to extend its scope; the map declined to summarise
it; the board inherited the appearance and graded absence.

**`"not re-derived"` and `"not read"` got conflated, and only the second is free to fix.**

## 3. Why it recurs by construction, and is not a lane's carelessness

`CLAUDE.md`'s stated convention is that a fact is **"written once and indexed elsewhere, never
re-narrated."** So *"I did not re-derive it"* is **what a correct lane emits constantly.** It is a
statement about **the writer's scope** and carries **zero information** about whether the answer exists.

A grader who reads it as *unavailable* has silently converted a **discipline into a gap** — and the more
faithfully a repo follows the write-once convention, the more often that conversion is available. **This
failure is a cost of the convention, not a deviation from it**, which is why it needs a rule of its own
rather than more care.

## 4. The operative distinction — what makes this actionable

| statement | what it is a claim about | what discharges it |
|---|---|---|
| *"no document answers this"* | the **corpus** | a **covering search** (`BEN-235`'s bar) |
| *"no document I read answers this"* | the **reader** | **opening the document the index already points at** |

**Before grading a cause `UNDECLARED`, open the document the index points at and read it AGAINST THE
QUESTION.** The index entry is not the evidence, and a lane's refusal to summarise is not a report that
there is nothing to summarise.

## 5. Relation to `BEN-235` / `BEN-391` — related, and distinct

Those are **searches that were run and could not have refuted the conclusion drawn from them**
(`set_seed` cannot match `set_random_seed`; `--diff-filter=D` cannot match a method retired by editing).
**Here no search was run at all.** The failure was upstream of search: a *refusal to summarise* was read
as *the absence of a verdict*, so no query was ever formed. Both families end in an unsupported
`ABSENT`; only one of them leaves a command you can inspect afterwards.

## 6. Rider — the same class, committed in the paragraph recording it

The board's §4, written to record this lesson, cited the corroboration as **"`OPEN_ITEMS` item 6."**

- **`OI-6` is the standard-P4 purity decision** (`docs/OPEN_ITEMS.md:74`) and says nothing about
  transferability.
- The claim's live home is **`OI-3`** (`docs/OPEN_ITEMS.md:71`) — *"Recoil-only covariance cannot be
  transferred and the joint full-event construction is not built."*
- Its **original phrasing is archived** at `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:834`
  (*"…automatically transferable to the new estimator."*) — the sentence the `DETERMINATION` quotes.
- A covering `grep -ciE 'transferab' docs/OPEN_ITEMS.md` returns **`0`**, so the bare ordinal had **no
  referent there at all** to be mis-numbered against.

**A renumbered/archived item plus a bare ordinal is `CLAUDE.md`'s own rule broken in transit** — *item ids
are prefixed with their document's short name* — and the same decay class as this board's `POINTER 3` on
`CRITERIA-20260811`'s line-range header citation. Found by **lane B** while landing the declaration, and
**recorded as failed rather than silently repaired**, which is the only reason it reached the party
repeating it.

## 7. And the weight caveat, which protects the grade rather than weakening it

**`OI-3`'s owner cell reads `PET / cause 5 owner`.** So the transferability claim is **the owning lane's
own statement.** It corroborates the declaration's background and **cannot be the second outside voice
the `UNDECLARED` grade was asking for** — the grade's whole content was that no non-owner had spoken.

**The outside evidence is Assistant's `sweep_bank_5d.py` trace, and it stands alone.** That is a **thinner
footing than the two-source reading**, and it is the correct one. Lane B's, and right.

## 8. Scope of the declaration, so it can be falsified

Stated by the declarer: the trace covered the **bank build** (`sweep_bank_5d.py`), the **three block
producers**, and the **background source**. It did **not** exhaustively audit `analyze_universes_5d.py`
or `adopt_unified_5d.py` for every input. **The falsifier is specific: a PET-derived product consumed by
either of those two modules.** `N/A` on the construction path traced — not `N/A` absolutely.
