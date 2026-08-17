# Comparable on one axis is not comparable — and a validity inventory that never evaluated its criteria

**Rows:** `BEN-400`, `BEN-401` (lane C, PET — first filings into the newly self-allocated block `400-409`).
**Date:** 2026-08-17. **Object:** the Gate-6 fixed-seed floor vs the Gate-5 `C_stat` family tail comparison.
**Ruling:** [`RULING-20260817-lanec-floor-vs-family-coherence.md`](RULING-20260817-lanec-floor-vs-family-coherence.md).

---

## `BEN-400` — a comparability check on one axis licenses nothing on another

`docs/orchestration/state/probe-oi126-tail-floor-20260817.py` compares a floor to a family spread. **Its
docstring is titled `COMPARABILITY`** and it does real work under that heading:

> *"COMPARABILITY: the family figure is median RELATIVE SD (0.6712). My earlier floor numbers were
> range/mean, which is a DIFFERENT statistic. Both are reported here, and **only rel_sd is comparable to
> the family's**."*

**That check is correct and it caught a real defect.** And in the same file:

```
:21   X = np.array([np.load(p)["xsec"].ravel(order="C") for p in ... GATE5_REPLICA_XSEC.npz])   # family
:30   F.append(np.asarray(z["central_vector"]))                                                  # floor
:38   rsd = A.std(0, ddof=1) / mu                                                                # same fn, both
```

**The statistic was made comparable. The QUANTITY was never checked.** `central_vector` sums to 1 by
construction — `VL130`: *"**SHAPE ONLY** … blind to normalization and **understates** the absolute
noise"* — while `xsec` is a density carrying normalization (`CSTAT-D0`). **A `rel_sd` of a different key is
still not comparable, however carefully the `rel_sd` was matched.**

**Why this is worse than an unchecked comparison: the heading advertises coverage the check does not
have.** A file with no `COMPARABILITY` docstring invites the question. One that has it, and passes,
answers a question nobody asked and closes the topic. **A named check narrows attention to its own axis.**

**And the direction is what made it disqualifying rather than imprecise:** the understated denominator
inflates the ratio, and the inflated ratio was being read as *"the floor explains only one seventh, so the
estimator is honestly unstable"* — **the defect biased toward the branch already being taken.**

**THE RULE.** State the axes a comparability claim covers, and treat every axis it does not name as open.
For a ratio of two spreads that is at minimum: **statistic** (`rel_sd` vs `range/mean`), **quantity**
(which key), **normalization** (does either side sum to a constant), **domain** (which mask), **sample**
(`n`, and which members), and **stratification** (what each side's magnitude depends on). This comparison
matched one of six and read as matched.

**Related, not the same:** `BEN-386` — the file an edit lives in is not the file that validates it.
`BEN-235` — an inference from absence is only as strong as the search behind it. **Both are about a check
whose reach is narrower than its conclusion; this one is about a check that ANNOUNCES its reach and is
still narrower than its title.**

## `BEN-401` — a validity inventory listed a member VALID with zero of its eight criteria evaluated

`docs/orchestration/state/gate6-floor-replication-result-56863958.json`, read this turn:

| field | value |
|---|---|
| `draws` | **4 entries**, ids `[2, 3, 4, 5]`, **8 clauses each** — 32 evaluations |
| `draw_1` | keys are exactly `source`, `trajectory_receipt`, `v`. **No clauses.** |
| `inventory.draws_valid` | **`[1, 2, 3, 4, 5]`** |
| `inventory.n` | **`5`** |
| `VALIDITY.clauses_failing` | *"none on any of draws **2,3,4,5**"* |

**So draw 1 is counted VALID, and included in `n`, with none of the eight criteria that define validity
ever evaluated on it.** The receipt is not lying — `clauses_failing` names exactly the draws it covers,
and `draw_1.source` says *"EXISTING `member_1` artifact, reused unmodified, NOT retrained."* **Every
statement is true and the aggregate reads as five checked draws.**

**The eight clauses are:** `1_completed`, `2_target_provenance`, `3_realized_policy`, `4_class_ratio`,
`5_mc_indices`, `6_gates`, `7_checkpoints`, `8_execution_environment`.

**Three of them are exactly the premises `VL130`'s ledger text asserts across all five draws** — *"identical
`inputs_sha256`, identical 2,000,000-row `mc_indices`, `bootstrap_seed = -1`"* — namely `2`, `3` and `5`.
**Asserted for five, evaluated for four.**

**And `8_execution_environment` is the axis the floor MEASURES.** The floor's estimand is residual
GPU/process non-determinism at a pinned seed. `member_1` came from job `56847059`; draws 2–5 from
`56863958` on 2026-08-14. **If the software stack or node type differed, draw 1 is a draw from a different
process population at identical configuration — and clause 8 is the clause that would have said so.**

**THE RULE.** A validity inventory must distinguish **checked** from **admitted**. `draws_valid` and
`draws_present` were distinct fields and both listed `[1,2,3,4,5]`; **the field the receipt needed and did
not have is `draws_checked`.** Where a reused artifact is admitted without the clause battery, say so in
the inventory, not only in the item's `source` string — because the inventory is what a consumer reads and
the `source` string is what an author writes.

**This is `CONVENTION-receipt-ingredients.md` / `BEN-077` applied to a VALIDITY CLAIM rather than a
number:** the receipt shipped enough to be contradicted, and the contradiction is only visible if you
count the `draws` array against `inventory.n`. **Nobody did, for three days, including me while ruling on
this exact object.**

## What it changed, and what it did not

**The population question resolves in favour of inclusion.** Membership in the process-noise population is
determined by the **execution's configuration**, not by which leg launched it — so *"not retrained"* is
bookkeeping about the leg, not provenance about the artifact, and `VL130` (`n=5` TERMINAL) already treats
`member_1` as a co-equal draw (`probe-oi120a-csyst-k-20260814.py:16`, `FILES[0]`). **`n=5` is right and
lane C's `"n=4 is correct"` was a claim about what the committed probe did, stated as a claim about what
the data supports. Withdrawn.**

**A second axis nobody named:** `probe-oi120a-csyst-k-20260814.py:36` takes the domain from
`masks[tags[0]]` — **`member_1`'s own `reported_bin_mask`.** So dropping draw 1 changes `n` **and** changes
which artifact supplies the reporting domain. `n=4` vs `n=5` was never a sample-size choice.

**None of it moves the conclusion it was serving.** The floor's share of the tail spread is a **variance**
share of roughly **2%** on every pairing (`1.938% → 1.692%` bias-corrected, `1.645% → 1.495%` raw), and it
survives a `4×` error in the floor. **The floor is not the explanation for the tail spread** either way.
