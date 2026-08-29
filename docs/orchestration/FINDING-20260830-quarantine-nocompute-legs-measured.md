# FINDING 2026-08-30 — the 2026-07-12 quarantine's three no-compute legs, measured at HEAD `32e403b8`

**Filed by the stale blocker sweep lane, on a task scoped to the no-compute legs of the quarantine
(cause 3 `P-i`/`P-ii`, cause 1, cause 4 `M`).** **ADOPTS NOTHING. DISCHARGES NOTHING. LIFTS NOTHING.**
`docs/analysis-note/` untouched, `values.tex` untouched, no ROOT read or written, no Slurm job
submitted, queued or scheduled. No quarantined magnitude is quoted here.

**NO LEG IS REGRADED BY THIS DOCUMENT.** `BEN-381` — the lane that measured a leg must not grade it —
and this lane measured all three. Every cell that this document's measurements bear on is **routed**
to a non-measuring lane or to the delegated authority, and the existing cells are left as written.

---

## 0. The three legs, and what each turned out to be

| leg | how it read on entry | what it is at HEAD | remedy | needs compute? |
|---|---|---|---|---|
| cause 3 `P-ii` — *"the dominant arm has nowhere to put a seed stamp"* | live blocker; a **new write site** required | **PREMISE FALSE.** Four write sites exist; they landed 2026-08-18 … 2026-08-20 | none — already built | no |
| cause 3 `P-i` — *"no product or receipt records the seed value"* | live; remedy *"add a stamp"*, **"needs compute? no"** | **STILL OPEN for every artifact in play, and its CLASSIFICATION HAS FLIPPED.** The stamp exists; putting a *value* in a product now requires a producing run | rebuild | **YES** — the "no" is stale |
| the reported multiplier — *"one edit closes the provenance leg for 2, 3 and 4 at once"* | relied on by two records | **DOES NOT HOLD**, in three independent ways | — | — |
| cause 1 — `C` MET, `P` PARTIAL, `M` OPEN | two legs open | **All four legs have content for X**; what remains is **one routed physics-presentation judgement** and nothing else | a decision | no |
| cause 4 `M` — the recorded `1.539` is a different ensemble | recoverable-from-bytes vs needs-a-run | **NEITHER.** The deflation never entered a stored object on X's path; the question is a **specification** question | a decision, then possibly a run | no, to answer it |

**The single most useful sentence for a reader in a hurry:** *two of the three legs this task was
scoped to were already discharged or already misclassified, and the third is not the kind of problem
its cell says it is.* That is the fifth instance this week of a blocker sentence outliving its
blocker, and the first three are in `OI-160`, `OI-161` and `OI-162`.

---

## 1. Cause 3 `P-ii` — the premise is false at HEAD, and was already false when three records restated it

### 1.1 The claim, quoted rather than paraphrased

`SCOREBOARD-20260817-quarantine-seven-causes.md:499`, which is where `P-ii` was split out as its own
defect:

> **P-ii** | **nothing COULD record it on the dominant arm** — `sweep_bank_5d.py` and
> `analyze_universes_5d.py` have **nowhere to put one** | a **new write site**, not a stamp |
> **YES — P-ii survives P-i's fix**

and `:485-487`:

> `analyze_universes_5d.py`, **which writes `combined_source` itself**, contains `seed` **zero** times and
> writes no `TParameter`; … `sweep_bank_5d.py` contains `seed` **exactly once** — `:252`, the hardcoded `42`.

`DECISION-20260822-joseph-b1-lift-and-clause-c.md:568`, ruling 24's table:

> | **P-ii** | the dominant arm has **nowhere to put one** — `analyze_universes_5d.py` contains `seed` zero
> times. **Survives P-i's fix** | a new write site | **no** |

and `:561-562`:

> `X`'s dominant term is the 188-universe systematic sweep, computed at a **hardcoded seed 42** —
> `sweep_bank_5d.py:252`, the only occurrence of `seed` in that file.

`WALKDOWN-20260822-one-pass.md:75-79`, on why the leg was not started:

> - **Cause 3's `P-i` and `P-ii`** — cheap, no compute, and identified in ruling 24 as independent of
>   the family. **Not started because they edit production estimator code**
>   (`analyze_universes_5d.py` needs a new write site) …

### 1.2 Measured at HEAD `32e403b8`

Every count below is from `git grep` at HEAD, and every write site was read in source rather than
inferred from a grep count.

| module | role in the g1/g2 chain | seed-bearing lines at HEAD | write site |
|---|---|---|---|
| `nd-unfolding/sweep_bank_5d.py` | per-universe producer (the **dominant** 188-universe sweep) | **13** (was *"exactly one"*) | `:309-311` — `TParameter("int")` for `estimator_seed`, `est_seed_offset_declared`, `est_seed_offset`. `:358` adds `--estimator-seed`; `:365-367` makes it **required with `--run`, with no default**, on the stated ground that *"a silent estimator seed is what gate 1 removed"*. The literal `42` at the old `:252` is gone — `:277` now passes `seed=args.estimator_seed` |
| `nd-unfolding/analyze_universes_5d.py` | writes `combined_source`, i.e. the g1 combined covariance | **8** (was **zero**) | `:273-278` — `_assert_universe_identity_is_coherent(...)` then a `TParameter("int")` per identity key, plus `n_universes`. `:134-149` collects the three keys from every universe it reads; `:152-169` **fails closed** with distinct messages for ABSENT-from-all, MIXED, and DISAGREEING, and states *"An absent stamp is not a weak yes."* |
| `nd-unfolding/unified_throw_cov.py` | g2 throw root | — | `:569-575` — `estimator_seed`, `draw_seed`, `est_seed_offset{,_declared}`. The dual-role `--seed` is split; `:634` makes `--estimator-seed` **required** |
| `nd-unfolding/mii_adopt_unified_5d_stamped.py` | remedy-(A) wrapper on the adopt writer | — | `:168` `LEG_IDENTITY_KEYS = ("estimator_seed", "est_seed_offset", "est_seed_offset_declared")`; `:799-800` reads them from **both** legs. **Wired into the only declared-member adoption path** at `sbatch_finalize_5d_bkgaware_gpu.sh:557` and `:563` |

`nd-unfolding/adopt_unified_5d.py` itself still writes no seed key — correctly, and by ruling: lane C
ruled remedy (A) gets a **wrapper** and that file is not touched, because `BEN-106`'s receipt binds its
digest (`DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md` §25). The launcher's own
comment records the consequence at `:507-510`: *"(A) HAS NOW LANDED, BY MY HAND, on all three writers …
So the original expiry, 'remedy (A) landing', IS TECHNICALLY MET."*

### 1.3 The landings, and the dates that make this a stale-blocker instance rather than a race

| commit | UTC-5/-4 timestamp | what it landed |
|---|---|---|
| `3dd5e66e` | 2026-08-18 01:16:53 -0400 | gate 1: `unified_throw_cov.py`'s `--seed` split into `--draw-seed` + `--estimator-seed`; `--estimator-seed` added to `sweep_bank_5d.py` |
| `214acdbb` | 2026-08-18 08:51:17 -0400 | the `TParameter("int")("estimator_seed", …)` write in `sweep_bank_5d.py` |
| `5afb7947` | 2026-08-19 01:27:33 -0400 | `_collect_universe_identity` + the three-key write in `analyze_universes_5d.py` — *"Remedy (A) lands on TWO of three writers"* |
| `bd72112b` | 2026-08-20 | the two declared-member adoption call sites rewired onto the wrapper |

Against:

| record | landed | still states the premise as live |
|---|---|---|
| `DECISION-20260822-joseph-b1-lift-and-clause-c.md` (`01b88de9`) | 2026-08-22 00:26:49 -0500 | yes — ruling 24's table and `:561-562` |
| `WALKDOWN-20260822-one-pass.md` (`0e13cf87`) | 2026-08-22 19:35:35 -0500 | yes — and **declines to start the leg on that ground** |

So the write site `WALKDOWN` says the leg needs had been in `main` for **three days** when the
`WALKDOWN` gave it as the reason not to start, and for **two and a half days** when ruling 24's table
was written down. **This is not a criticism of the rulings' substance** — ruling 24's operative content
(cause 3 is `N/A` for the 2D ML block and APPLICABLE to X, and its discriminator is the dominant block)
is unaffected, and so is `WALKDOWN`'s ordering. What is stale is one factual cell and one stated reason.

### 1.4 What `P-ii` therefore is

`P-ii` is a statement about **code capability**, not about an artifact, so it is the one cell in this
family that is not (cause × artifact)-scoped. As a code property it is **satisfied at HEAD for the
dominant arm and for both legs.** The regrade is routed — this lane measured it — and is filed as
`OI-170`.

**One thing that survives and is worth keeping:** the write sites exist but have **never produced a
stamped 5D product**. The wrapper's first and only real execution (`RUNS.tsv:308`, job `57294218`,
2026-08-20, `REMEDYA-SMOKE-PASS`) recorded, in its own words, *"identity keys absent in both legs ->
upstream_estimator_seed_{g1,g2}_checked=0 recorded as ABSENCE, not as a pass"*, because its **inputs**
predate the producers. `runs/clausec-rerun-20260821/logs/gate_A1.log.txt:7` says the same from the
gate's side: *"UNCOMPARABLE est_seed_offset: PROVENANCE -- NOT COMPARABLE on this artifact; the archive
predates the writer (landed: lane D 2026-08-18)."* So the capability is real and the record is still
empty — which is exactly `P-i`, below.

---

## 2. Cause 3 `P-i` — still open for every artifact, and no longer a no-compute leg

`CRITERIA` §2's `P` for cause 3 has two clauses; clause (i) is *"X's receipt records the single seed
value"*. Measured at HEAD:

* `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` — the receipt that establishes the candidate's
  provenance — has **34** `seed`-bearing lines and **every one of them is a `fixed_seed_null_*` key**.
  There is no `estimator_seed`, no `draw_seed`, no `est_seed_offset`. So clause (i) is **NOT MET for
  CAND** at HEAD, unchanged from `SCOREBOARD` §2d.
* A covering search over the tracked data corpus (517 tracked `*.json`/`*.tsv`/`*.txt`) for
  `est_seed_offset` or `upstream_estimator_seed` returns hits only in **run records and gate logs that
  record the keys as ABSENT** — plus one unrelated positive control that proves the search works,
  `state/annealed-nominal-complete-56563761.json:87` `"estimator_seed": 42` inside a step-1
  `seed_policy` block, which is a 2D/step-1 object and not on X's path.

**And the classification has flipped.** `DECISION-20260822` ruling 24's table gives `P-i`'s remedy as
*"add a stamp"* and *"needs compute? **no**"*. That was right when written. It is wrong at HEAD, and the
reason is that its own remedy landed: **the stamp now exists, so the only thing left is to write a
value into a product, and that is a producing run.** For the two artifacts actually in play it is worse
than expensive:

| artifact | can `P-i` close on it? |
|---|---|
| **QUOTED** — the July products behind `\gbdtFiveAdoptTrace` / `\gbdtFiveCVTrace` | **No, ever.** They predate the stamping entirely; `SCOREBOARD` §1's *"X gets replaced, not repaired"* holds unchanged |
| **CAND** — `stamped_bkgaware_meancentered_20260812.root` `4f168e83…` and its CV arm | **No.** Its inputs predate the producers, which is what job `57294218` measured |
| a future member product | **Yes** — and only by being built |

So cause 3's remaining `P` work is not cheap-and-unstarted; it is **carried entirely by whatever
producing run creates the next 5D product**, and it needs no separate leg. Filed as `OI-171`.

---

## 3. The reported multiplier does not hold, and it fails in three independent ways

### 3.1 The claim, verbatim

`MAP-20260817-gbdt-note-section-blockers.md:62`, cause 3's "what would discharge it" cell:

> **Provenance in the adopted product** — `BEN-106`'s stamp propagation, **one edit, which closes this
> leg for 2, 3 and 4 at once**. Already done for the candidate.

`:63`, cause 4: *"The same stamp propagation, **plus its magnitude on the right ensemble.** No cluster
time."* `:71`: *"Causes 3 and 4 share one edit."* And
`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:386-387`:

> causes 2, 3 and 4 need only **provenance in the adopted product**, which is one edit — BEN-106's stamp
> propagation — closing the same leg for all three at once.

### 3.2 Failure 1 — the one edit could not carry cause 3's key, because the key existed nowhere upstream

`BEN-106`'s stamp propagation is a **hop**: `adopt_unified_5d.py:198-210` re-writes keys it read out of
the throw root. It can only propagate what a producer already wrote. Measured:

| cause | the key its `P` needs | who wrote it before `BEN-106` | edits needed to make the hop useful |
|---|---|---|---|
| 2 | `joint_mean_shift_norm` (+ `centering_convention`) | `unified_throw_cov.py`, already | **one** — the hop |
| 4 | `fixed_seed_null_norm` (+ `_checked`) | `unified_throw_cov.py`, already | **one** — the hop |
| 3 | a **seed value** | **nobody, on either leg** | **four** producers plus a policy module |

The four, measured in §1.3: the g2 two-role split (`3dd5e66e`), the g1 per-universe write
(`214acdbb`), the g1 combined write (`5afb7947`, the writer *"NOBODY HAD ENUMERATED"* in
`analyze_universes_5d.py:198-204`'s own words), and the wrapper that reads both legs
(`mii_adopt_unified_5d_stamped.py`, wired `bd72112b`) — plus `nd-unfolding/seed_offset_policy.py`,
38,048 bytes, which did not exist on 2026-08-17. **The multiplier conflated two keys that already
existed one hop upstream with a key that existed nowhere at all**, and the measured cost of the
difference is four commits across three days.

### 3.3 Failure 2 — on the candidate, there were no two other halves left to close

At the moment the claim was written, `SCOREBOARD`'s board already graded cause 2's `P` **MET** for CAND
(job `56720356`, path + sha256) and cause 4's `P` **MET** for CAND (`receipt_candidate_stamps_5d.json`,
branch S1). So *"closes this leg for 2, 3 and 4 at once"* offered to close two legs that were already
closed and one it could not reach. Re-verified at HEAD: the receipt is present, 19,258 bytes, and
carries the `fixed_seed_null_*` and `upstream_*` families.

### 3.4 Failure 3 — on the quoted artifact, no edit closes any of the three

`SCOREBOARD` §1 is right and this lane confirms it applies here without qualification: X predates the
stamping, so no code edit moves cause 2's, 3's or 4's `P` for the artifact `values.tex` quotes.

**Verdict on the claim as asked: it does not hold. Two of the three legs it names were already
satisfied where it could act, the third needed four producer edits rather than one, and in the column
that gates the note it can act on nothing.** The narrow true residue is: *the `BEN-106` hop was one
edit and it did serve causes 2 and 4.* Routed as `OI-171`; the `MAP` cells are left as written with a
pointer.

---

## 4. Cause 1 — what actually remains is one routed judgement

### 4.1 The state, re-derived from the committed receipt rather than from any table

The entry framing (`C` MET, `P` PARTIAL, `M` OPEN) is `CRITERIA` §3's row, which predates the work that
closed two of those cells. `nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json` is present at
HEAD (40,488 B) and records:

* `census.summary` — `n_pm_pair_bands: 42`, `pair_bands_missing_an_endpoint: []`,
  `flux_exactly_100_contiguous: true`; the two non-pair entries named rather than smoothed
  (`2p2h: 3`, `Flux: 100`), and the one non-matching file named in
  `skipped_files_not_matching_UNI_RE`. **That is cause 1's `P` criterion verbatim** — *"both ± endpoints
  present for every band and an exact contiguous 100-universe flux bank"*.
* `magnitude_M` — the one-sided-vs-mean-centered counterfactual **on X's own bank**, both endpoints
  computed, reported as a per-band distribution; `all_targets_reproduced: true` against the eight
  committed summary numbers as a positive control.
* `inputs.glob` — `uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root`. **This is X's bank**, i.e.
  the census is about the QUOTED artifact, not about CAND.

`DETERMINATION-20260817-cause1-census-and-magnitude-measured.md` (recoverable at
`evidence/prepublication-2026-08-20-0b329e8a`, 14,979 B) states the resulting position and the one
question left, and this lane quotes rather than restates it:

> **Does a `+3.1%`/`+5.9%` √Tr difference with a `1.7–2.0×` median per-band ratio constitute `M` MET
> under §0's *"measured, not necessarily small"* rule — or does a difference this size mean the
> construction choice is material enough to need its own statement in the note?**

### 4.2 The `T`-leg defect that was routed away is already fixed

`DETERMINATION` §5 filed a live defect against cause 1's own `T`-leg guard: the allow-list in
`test_the_only_outer_product_on_X_path_is_the_documented_norm_band` asserted `analyze_universes_5d.py:109`
and went red on a comment-only edit. It declined to fix it under `BEN-381`. **Measured at HEAD: fixed
2026-08-18.** `nd-unfolding/tests/test_uq_remediation.py:787-820` now pins on **content** — exactly one
`np.outer(` on X's path, in `analyze_universes_5d.py`, symmetric (`lhs == rhs`), with `add_norm` and
`cv_rep` asserted in the three preceding lines — and reports the line number instead of asserting it,
with the reasoning recorded in place: *"the number locates, the content survives the edit."* So the
work this lane could legitimately have done on cause 1 was already done by another.

### 4.3 The one correction this lane does have to file about cause 1

`SCOREBOARD` §1's headline — *"THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION … Every `P` cell in the
QUOTED column is `OPEN` for one reason"*, the absent stamps — **is sound for causes 2, 3 and 4 and does
not extend to cause 1.** Cause 1's `P` criterion (`CRITERIA` §2) does not ask for a stamp; it asks for
a **bank inventory**, and the receipt that satisfies it was computed on X's own bank and pinned to X by
reproducing eight of X's own committed summary numbers to 4 significant figures. Identity by numerical
reproduction of the artifact's published values is a *stronger* binding than a stamp, not a weaker one.

**So for X — the artifact the four `\gbdtFive*` macros quote — cause 1 has content on all four legs,
and the only thing between it and a four-MET reading is the §6 judgement above.** This lane is
**not** declaring that, is **not** regrading the board's cell, and notes the opposite risk explicitly:
if the judgement comes back *"a +12% to +19% relative shift is material enough to need its own
statement in the note"*, the leg does not close and the note acquires a new obligation. Either way it
is a decision, it is free, and it is the cheapest item anywhere in this quarantine. Filed as `OI-172`.

---

## 5. Cause 4's `M` — not recoverable from retained bytes, and a run would not recover it either

The task asked whether the correct value is recoverable from retained bytes or genuinely needs a run.
**Measured answer: neither, and the reason sits upstream of both.**

### 5.1 The specification exists and the value never did

Exactly **one** version of `nd-unfolding/unified_throw_cov.py` was in force between `a0cdc019`
(2026-06-08) and `07c18aee` (2026-07-14) — `git log a0cdc019..07c18aee -- <file>` returns only
`07c18aee` itself. At `a0cdc019`, read this turn rather than taken from the retraction that reported it:

* `:224-230` carries the derivation in the comment: *"With two CV unfolds at different seeds,
  `E||x_cv2 - x_cv1||^2 = 2*sum_bin sigma_jit^2` … the jitter-free systematic trace is
  `tr(C_uni) - ||Dcv||^2`."*
* `:232-236` computes it under `--null` only:
  `x_cv2 = _xsec_for_weights(..., args.seed + 7)`, `jit_trace = float(np.sum((x_cv2 - base) ** 2))`,
  `tr_uni_corr = max(tr_uni - jit_trace, 0.0)`.
* `:238-239` and `:251-252` **print** it. Nothing else consumes it.

`jit_trace` occurs **0** times at HEAD; `git log -S` over all refs returns exactly `a0cdc019` (added)
and `07c18aee` (removed by an in-place edit). So the method is a committed record and the value is not:
it was a runtime stdout quantity.

### 5.2 The subtraction never entered a stored object on X's path — which is the part nobody had measured

This is the finding, and it is derivable entirely from committed bytes:

| object | what `a0cdc019`'s writer put in it | deflated? |
|---|---|---|
| `C_unified` (TH2D) | raw `C_uni` (`:265`) | **no** |
| `C_blocksum` (TH2D) | raw `C_block` (`:265`) | **no** |
| `C_cross` (TH2D) | `C_uni - C_block` (`:242`, `:265`) | **no** |
| `sqrt_tr_unified` (TParameter) | `st_uni` — the **raw** root-trace (`:271`) | **no** |
| `tr_uni_corr` / `st_uni_corr` | printed only (`:236-239`, `:251-252`) | — |

and on the consumer side, `nd-unfolding/adopt_unified_5d.py:89-90`:

```
vu = np.clip(_diag(fu.Get("C_unified")), 0, None)
vb = np.clip(_diag(fu.Get("C_blocksum")), 0, None)
```

with the inflation built as `g = sqrt(max(vu, vb)) / sqrt(vb)` at `:108-113` and applied as
`C_new = C_comb + (g_i g_j - 1) C_vert` at `:143-145`. **`sqrt_tr_unified` is never read.**
`git log --all -S "sqrt_tr_unified" -- nd-unfolding/adopt_unified_5d.py` returns **nothing**, against a
positive control on `C_unified` that returns two commits (`923d8de6` 2026-07-02, `07c18aee` 2026-07-14)
— so the module existed in that form at the 2026-07-01/02 adoption and read the raw matrices then too.

**Consequence.** On X's path the retired subtraction reached exactly one class of object: **reported
prose ratios** — the *"jitter-corrected unified/block sqrt-trace"* figures, of which the recorded 5D
value is the `1.539` in `VALIDATION_LEDGER.md:1158-1159` and `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:1182`.
It did not reach `C_unified`, `sqrt_tr_unified`, the inflation `g`, or any adopted covariance.

**A scope limit stated so this is not over-read:** for the **4D** arm the jitter-corrected ratio was
not merely reported. `docs/HIGHER_DIM_OMNIFOLD_DESIGN.md:153-157` records the `2.01` as *"**adopted** as
the published 4D systematic via PSD-safe fractional-inflation transfer (`adopt_unified_4d.py`)"*. This
lane did **not** audit `adopt_unified_4d.py` and makes no claim about the 4D arm's exposure; it is
flagged because it means cause 4 may bind differently on 4D than on X, and the (cause × artifact) rule
says that has to be graded separately rather than inherited.

### 5.3 So what is cause 4's `M` for X?

Three candidate readings, and the measurement above rules out the first two:

1. **A historical value to recover.** Ruled out. `SCOREBOARD` §3 already established that no surviving
   durable log carries one — with the methodological point that the durable corpus `.gitignore`s
   `*.log`/`*.out`/`*.err`, so a null there is *"0 reachable, not 0 hits"* — and that the one value lane
   D found (`uthrow5d_comb_55286276.out`, 2026-07-01, purgeable scratch) belongs to a product
   overwritten twelve days later. **This lane adds a content-based reason that does not depend on log
   retention at all:** the deflation was never written into any object, so there is nothing to recover
   *from an artifact* even in principle, for any product.
2. **A number a run would produce.** Ruled out as *the* value, for the reason `SCOREBOARD` §3 gives and
   this lane verified in the source: `jit_trace = float(np.sum((x_cv2 - base) ** 2))` from **one**
   second CV unfold is a **one-sample estimate of a variance** whose expectation the comment itself
   writes as `E||x_cv2 - x_cv1||^2`. A recomputation is a different draw, on a different environment.
3. **A specification question.** This is what it is. `CRITERIA` §0 forbids an *unmeasured* difference,
   and `CRITERIA` §2 rules that *"a bound is not the `M` leg"*, a ruling `SCOREBOARD` §2c's block
   extended to cause 3 and checked on the merits. Neither text says what `M` means when **the defective
   construction was never applied to the artifact's stored inputs**. That is a gap of the same species
   as the `M(ii)` referent gap, which the campaign resolved by **choosing** a specification rather than
   reading one — and by the rule adopted there, *do not let measurability choose the specification.*

**The honest cell state is therefore unchanged — `OPEN` — and this lane declines to move it in either
direction**, including the direction that would be convenient. Naming the argument this lane is *not*
making, because its payoff would be its own premise: *"the subtraction never touched X, so cause 4 is
`N/A` for X on the merits"* is available, is superficially the same move that settled cause 5, and
should be resisted here — cause 5's `N/A` rested on a traced construction path with a named falsifier,
whereas this would rest on X's inputs being pre-deflation, which is a claim about how X was built and
not about whether cause 4's defect is on its path. The right next move is the specification decision,
not a lane's `N/A`. Filed as `OI-173`.

### 5.4 One inconsistency surfaced in passing, recorded rather than resolved

`FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md:112` records
`nd-unfolding/uq_5d/unified_throw_cov_5d.root` — X's g2 input — as `2,677,168,123` bytes, mtime
**`Jul 13 02:15`**, **9 keys**. Those two fields disagree about which writer made the file:

* at `a0cdc019` the `--out-root` block writes **6** objects (3 TH2D + `sqrt_tr_unified`,
  `sqrt_tr_block`, `n_throws`);
* at `07c18aee` it writes **8**, or **9 with `--null`** (adding `joint_mean_shift_norm`,
  `fixed_seed_null_norm`, `hJointMeanShift`);
* `07c18aee` is dated **2026-07-14 14:43:19 -0700**, i.e. **after** the recorded mtime.

A 9-key inventory can only have come from the post-retirement writer **run with `--null`**, which is
consistent with `BEN-106` reading `fixed_seed_null_norm = 1.9706e-50` off that same file, and
inconsistent with a Jul 13 mtime. The most likely explanation is the ordinary one in this repo — the
cluster tree and `main` fork, so code can execute a day before its commit lands — and it does not
change any grade. It matters for two reasons worth one paragraph: **(a)** it is the discriminator that
proves X's throw root was **not** built by the jitter-subtracting code, strengthening §5.2 from *"the
deflation was not propagated"* to *"the deflation was not in the code that built X's g2 input"*; and
**(b)** a key inventory dates an artifact's writer more reliably than its mtime, and here only one of
the two is right. **Limit:** this lane did **not** read the ROOT (no cluster access from this session);
the 9 is taken from three in-repo measurements that agree (`ENUMERATION-20260818-mii-root-payload-three-classes.md:22`,
`FINDING-20260822…:112`, `HANDOFF-20260820-2154Z-publication-closeout.md:125`) and agreement across
three documents is not proof of three independent measurements. Anyone with a login node can settle it
in one `TFile.Open`.

---

## 6. What this lane changed, and what remains

**Changed:** this record; a pointer beside `CRITERIA` §3's table, `SCOREBOARD`'s board and `MAP` §2,
each leaving the existing text as written per this repo's convention; `VALIDATION_LEDGER.md`'s
seven-causes section; `OI-170`–`OI-173`; the router and manifest rows this document needs to be
findable.

**Remains, with its owner:**

| # | item | owner | cost |
|---|---|---|---|
| `OI-170` | regrade cause 3's `P-ii` cell on the measurements in §1 | a non-measuring lane | minutes |
| `OI-171` | strike the multiplier from `MAP` §2's remedy cells and reclassify `P-i` as run-carried | a non-measuring lane | minutes |
| `OI-172` | the cause-1 §6 physics-presentation judgement, for **X** | Joseph / the delegated authority | free |
| `OI-173` | the cause-4 `M` specification decision | Joseph / the delegated authority | free |
| — | cause 3's `M(ii)` | unchanged — needs the unauthorized member family; **out of this task's scope** | — |
| — | cause 6 | unchanged — the only cause needing a rebuild it has never had | — |
| — | cause 7 for X | unchanged — built is not adopted | — |

**Counts are unchanged by this document. CAND stands at 1 of 7 (cause 2, by Joseph's 2026-08-12
decision) and QUOTED at 0 of 7.** Nothing here makes adoption nearer.

## 7. Limits

* **Nothing is regraded and nothing is discharged here.** Four cells are routed.
* **No test was executed in this session.** `python3 -m pytest` was not permitted in this sandbox, so
  every claim about `nd-unfolding/tests/test_uq_remediation.py` in §4.2 is from **reading the source at
  HEAD**, not from a green run. A reader who needs the `T` leg re-verified must run it.
* **No cluster read.** `ssh` was not permitted in this sandbox. Consequences are stated inline: §5.4's
  9-key figure is second-hand, and this lane did not re-check whether
  `uthrow5d_comb_55286276.out` still exists on pscratch. That check would not change §5's answer,
  because the value it holds belongs to a product that no longer exists — but it is not measured here
  and is not claimed to be.
* **§5.2's inference that X's g2 input was built by a given code version** rests on a commit-range
  measurement plus the key-count discriminator in §5.4, not on reading the file. The cluster/`main`
  fork is the reason the mtime cannot settle it either way.
* **The 4D arm is not audited.** §5.2's flag about `adopt_unified_4d.py` is a routing note, not a
  finding about 4D.
* **This document is about causes 1, 3 and 4 only**, for the two artifacts named in `SCOREBOARD`'s
  column table. It says nothing about causes 2, 5, 6, 7, about PET, or about adoption.

## 8. LANDING DEBT — this record was written in a session that could not commit it, and the coupled generated files are NOT regenerated

**Read this before treating anything above as live.** The filing session could execute no repo script
and no `git` write: `python3 <script>`, `git add`, and `ssh` were each refused by the session's
permission mode, in a non-interactive session with no route to approval. Consequences, all of them the
landing lane's to discharge:

1. **`docs/orchestration/MANIFEST.tsv` is NOT regenerated.** `MANIFEST-overrides.tsv` gained a row for
   this document and `VALIDATION_LEDGER.md`, `docs/OPEN_ITEMS.md`, `CATALOG.md`, `CRITERIA-20260811…`,
   `SCOREBOARD-20260817…` and `MAP-20260817…` were edited, so **F-14 / section 7.0.7 coupling applies**:
   stage the sources first, then `python3 docs/orchestration/generate_manifest.py --committed-only`,
   then `--check`, and commit in ONE pass.
2. **`docs/orchestration/control-plane/source-record-inventory.tsv` is NOT regenerated** for
   `OI-170`–`OI-173`. It is digest-bound to the `OPEN_ITEMS.md` rows, so `control_plane_lint` will
   refuse until it is. **Read the regenerated ROWS, not the exit code** — a `--write` run has silently
   demoted an `OI` queue cell before, and none of these four rows may be reclassified off `NOW` by a
   regeneration.
3. **No pre-commit check was run**, so `whose_row.py --check-oi-ids` has not confirmed the block. The
   four ids were verified free by hand — `git grep -ohE "OI-16[0-9]"` plus an untracked sweep returned
   only `OI-160`, `OI-161`, `OI-162` — and `160-169` is the `stale blocker sweep` lane's self-allocated
   block, so **commit as `git -c user.name='stale blocker sweep'`**; the hook keys the block off the
   committer name and any other name falls back to the exhausted `120-139`.
4. **Two peer rows in `MANIFEST-overrides.tsv` lost an inert trailing tab**, disclosed rather than
   hidden: `FINDING-20260824-gate2-preparation-and-four-open-rulings.md` and `FINDINGS.md` are now
   three-column instead of four-with-an-empty-fourth. The session's editing tools strip a trailing tab
   and it could not be restored. **This is inert by the generator's own design** —
   `generate_manifest.py:396-404` reads `override["canonical_successor"] or ""` with a comment recording
   that the three `CONVENTION-*` rows are already three-column — but it is a change to bytes this lane
   had no business changing, and a landing lane that prefers the original shape should restore both tabs.
5. **Nothing above is live until it is in a pushed commit**, per this repo's own rule. Until then this
   file is a working-tree draft on `lane/quarantine-nocompute` and every `OI-170`–`OI-173` reference in
   the pointers is a forward reference.
