# PREDECLARATION — cause 3's `M(ii)` seed scan

**Committed BEFORE execution. Lane B, 2026-08-17.** Bar confirmed by a second lane (C) via the mediator;
the three amendments it returned are incorporated below, one of which retracts a conclusion of mine.

**⚠ AND THE RUN IS BLOCKED ON COST AND AUTHORITY — see §6. `n = 1` as scoped is not a cheap probe, and
that is a measured finding, not a caveat.** This file is committed anyway: a predeclaration's value is that
it exists before the run, whenever the run happens.

> **NAVIGATION NOTE added 2026-08-17 to the header, NOT to any predeclared text: `28.50 A100-h` at `:88`
> and `:92` is SUPERSEDED. A COMPOSITE ARM — this document's own subject — COSTS
> `39.078` A100-HOURS *PLUS* `55.182` CPU TASK-HOURS (`2,759.1` CPU-core-hours), IN TWO UNITS.**
> The `39.078` alone (`+37.1 %` on `28.50`; the lateral term had costed 5 of 19 universes, missing job
> `55894759`) is the **`C_syst` path only** — and quoting it bare here would reintroduce, in the successor,
> exactly the omission `:88-92` exists to warn about. Corrected on lane A's challenge; see the annotation for
> why the CPU term is not optional.
>
> **Why a composite arm necessarily carries the CPU term, and the code does not merely imply it — it
> REFUSES the alternative.** A composite arm moves **both** seeds, and the second of them is
> `unified_throw_cov.py`'s `--seed`, i.e. the `uthrow` leg. That seed threads into **every** throw unfold
> (`:244`), **every** knob block endpoint (`:281`) and **every** flux block unit (`:297`); it is **stamped**
> into each slab (`:254`, `:285`, `:302`); and the F2 guard at **`:417-419` raises `SystemExit` on a
> mixed-seed combine** — *"refusing mixed-seed combine"*, with the comment giving the reason as *"else
> `C_uni`/`C_block` would mix estimator jitter across slabs."* **So no slab can be reused across a seed
> change: the 71 CPU tasks (40 throw + 31 block, `55821660`/`56427580`/`55821661`) re-run in full.** The
> `uthrow` leg is `0` A100-hours and `2,759.1` CPU-core-hours, so **the composite arm's defining move is
> precisely the leg that carries essentially all of the CPU bill** — which is why a GPU-only figure fails
> hardest at this site rather than most harmlessly.
>
> **Do not read `39.078` and `39.223` as the same number rounded.** They are different quantities that
> nearly coincide because `C_syst` is `99.63 %` of the GPU column: `39.078` is the `C_syst` re-seed,
> `39.223` is one seed across **all four** blocks (`+ 0.1458` for `C_stat`). The four-block CPU total is
> `55.337` task-hours (`+ 0.1550` for `C_ML`). Against the `24` A100-h grant: `1.63x`, **on the GPU column
> alone**, with the CPU column outside the grant's unit entirely.
>
> The predeclared *claim* at `:88-92` held on measurement — only its operand moved, and the direction it
> predicted was right. Full record in the **POST-HOC ANNOTATION at the end of this file**, which leaves
> everything above it untouched. This pointer is in the header because a reader who greps to `:88` would
> otherwise never reach an annotation 150 lines below it, and a predeclaration is the one document class
> where the body must not be edited to fix that (`BEN-244`). `BEN-247`;
> [`EXTENT-20260817-2850-a100h-scope-and-missing-legs.md`](EXTENT-20260817-2850-a100h-scope-and-missing-legs.md) §0.

---

## 1. THE BAR (confirmed)

> **`M(ii)` is MET if the omitted seed contribution cannot change any published value at the precision it
> is printed to.**
>
> **`f ≡ sd(block_sum across seeds) / block_sum ≤ 0.027`**, i.e. **`sd(block_sum) ≤ 1.177e-39`** against
> block sum **`4.357790406860002e-38`** — σ inflation `0.0364 %`.

### 1a. INVALIDATION CONDITION (amendment 1)

**Anchored to `\gbdtFiveBlockMedian = 13.36` at FOUR significant figures
(`docs/analysis-note/values.tex:57`). If that macro's printed PRECISION changes, THIS BAR IS VOID and must
be re-derived. A change in its VALUE does not void it.**

Re-derived independently rather than taken from the amendment:

| printed | s.f. | ⇒ bar |
|---|---|---|
| `13.36` | 4 | `f ≤ 2.7361 %` |
| `13.57` | 4 | `f ≤ 2.7149 %` — **value moves the third digit only** |
| `13.4` | 3 | `f ≤ 8.6467 %` — **precision multiplies the bar by 3.16×** |

**Insensitive to the value, highly sensitive to the precision** — so the trigger is written down rather
than left as reasoning. Rule 4b's pattern applied to a threshold: a binding with a stated scope, which
**dies loudly instead of re-pointing quietly**.

## 2. THE `[2.74 %, 4.15 %]` BAND IS REMOVED, NOT GIVEN A CONSTANT (amendment 2)

Amendment 2 required a **number** rather than *"report as bar-dependent"*, which was correctly identified
as *"decide after seeing the number"* wearing a caveat — the thing I rejected on cause 4.

**The band was an artifact of my own construction, and the fix removes it rather than arbitrating it.** It
arose because I tested **two** published quantities (`13.36` at 4 s.f., `5.81e-38` at 3 s.f.) against **one**
aggregate noise figure. Each published quantity is moved by **its own** noise, so each is tested against
**its own** precision:

| leg | quantity measured across seeds | must satisfy | because |
|---|---|---|---|
| **A** | `f_agg = sd(block_sum)/block_sum` | **`≤ 4.15 %`** | moves `\gbdtFiveAdoptTrace`, 3 s.f. |
| **B** | `f_med = median over bins of sd_i(σ_i)/σ_i` | **`≤ 2.74 %`** | moves `\gbdtFiveBlockMedian`, 4 s.f. |

**MET requires BOTH. There is no band, no uniformity assumption, and no concentration constant to argue
about** — if the contribution is concentrated, leg B is small and leg A binds; if it is uniform, both move
together. **The measurement selects the binding leg by construction.**

**This is STRICTLY STRICTER than the single-leg falsifier as sketched** (leg A alone would permit up to
`4.15 %`), so it cannot smuggle a pass. **Flagged prominently as a change from the sketch, for objection**
— it implements the confirmed anchor rather than replacing it, but the mediator and C should say so if they
disagree.

**Headline bar remains `f ≤ 2.7 %`** as the tighter of the two legs and the number to quote.

### 2a. RE-DERIVED AGAINST THE COMPOSITE (C's ruling, 2026-08-17) — the legs SURVIVE, the object is restated, and the COST DOES NOT

C deferred rather than denied, on the ground that *"a falsifier whose object changed under it must be
re-derived, not re-confirmed"*. Re-derived:

**The BAR is unchanged, and unchanged for a reason that matters: it comes from PUBLISHED PRECISION, not
from the noise source.** `13.36` at 4 s.f. and `5.81e-38` at 3 s.f. are the same numbers whichever seeds
vary, so `0.0374 %`/`2.74 %` and `0.0861 %`/`4.15 %` stand. **A precision anchor is invariant under a
change of what is being varied — which is the second time tonight it has outperformed the analogue-based
one.**

**The LEGS survive** — each published quantity is still tested against its own precision by its own noise,
so there is still no band and no concentration constant.

**The OBJECT is restated, and this is the substantive change:** `sd` is now taken over arms in which
**both** estimator seeds vary **jointly** — `sweep_bank_5d.py`'s (currently `42`) and
`unified_throw_cov.py`'s (currently `1000`). So:

| | before (single-leg reading) | after (composite) |
|---|---|---|
| what an arm is | one `--seed` value | one **pair** of seeds, both moved |
| `f_agg`, `f_med` | over `--seed` arms | over **joint** arms |
| decomposable per leg? | n/a | **NO** — joint variation gives the joint contribution and cannot be split without separate scans, and `M(ii)` does not ask for a split |

**⚠ AND THE `28.50 A100-h` FIGURE DOES NOT COVER A COMPOSITE ARM. Stated before it can be quoted as if it
did.** That figure is *sweep run + lateral + finalize*, i.e. the **`C_syst` path only**. The block sum is
`C_syst + stat + ML`, and the **stat** (`boot5d`, 100 replicas) and **ML** (`ssplit5d`) blocks are unfolds
too, so they are very likely seed-dependent as well — **I have not measured whether they are, or what they
cost.** A composite arm may therefore cost materially more than `28.50`. **The number going to Joseph must
carry that scope**, or it is the same error as pricing the abandoned throw/block path: a real measurement
of the wrong extent.


## 3. AMENDMENT 3 ACCEPTED — MY "THE CAUSES DO NOT SHARE A SCALE" IS WITHDRAWN

I compared an **input-level** quantity (`f`, a fractional *contribution*) against an **effect-level** one
(cause 4's `<0.1 %`, an *effect on the sqrt-trace*), and dividing both by `9.35 %` carried the mismatch
through instead of fixing it. **Re-derived from scratch here, not taken from either lane:**

```
matched, effect vs effect:   0.1000 % / 0.0374 %  =  2.672x     <- the causes DO share a scale
mismatched, my withdrawn form:                       27.4x
```

**So the cross-cause form revealed no structural gap — it revealed one more instance of the
commensurability error this entire thread has been about, at the meta level, inside the check I wrote to
compare the checks.** Cause 3's bar is `2.67×` tighter than cause 4's, which is mild and defensible. **No
change to cause 4's framing is needed.** The underlying physics stands (a bias adds linearly, a spread in
quadrature); the conclusion overreached.

## 4. `n`, AND THE REASONING THAT FIXES IT

**`n = 2` is the minimum informative value, and it costs ONE new seed** — the candidate is already a
one-seed product (`unified_throw_cov_5d.py --seed 1000`, `sbatch_uthrow_run_5d.sh:20`), so it supplies the
first point and one new seed supplies the second.

**`n` beyond 2 follows from the measured spread, not from a prior:** choose `n` so the spread's own
uncertainty is narrow *relative to the bar*, by **realized exceedance rather than a fitted tail**
(`BEN-025`). **12 inherited from a July scan with different purposes is a number, not a design**, and is
not adopted.

**Attainability is an OBSERVATION at `n = 2`, not an argument.** The revision-1 use of AI1's `2.9969 %` as
evidence of reachability is withdrawn: a quantity that cannot inform the expectation cannot bound the
reachable range either.

## 5. FALSIFIERS — both, and the second is the one that gets skipped

**F-RESULT.** Either leg exceeded ⇒ **`M(ii)` UNMET**: `f_agg > 4.15 %` **or** `f_med > 2.74 %`.

**F-VALIDITY.** The per-seed outputs must be shown **mutually distinct, with digests recorded.** If the
seed is not plumbed through, every block sum is identical, **the spread is zero for the wrong reason — and
a zero spread reads as the best possible result.** `BEN-181` + `BEN-344`: **on this quantity the vacuous
outcome is indistinguishable from the desired one.** Required at every `n ≥ 2` stage:

* `sha256` of each per-seed slab set and of each per-seed combined product, all recorded;
* the seed **read back out of the products** (`do_throws`/`do_blockunits` stamp `seed`; `unified_throw_cov.py:328-331,368-372` collect it and `:417-419` reject a mixed-seed combine) and shown to differ between arms;
* **all digests pairwise distinct.** Any collision ⇒ **no result may be reported.**

**At `n = 1` distinctness cannot be shown**, so `n = 1` may report **cost only** and **no bar verdict**.

## 6. ⚠ THE RUN IS BLOCKED ON COST AND AUTHORITY — measured, not estimated

> **⚠ CORRECTED 2026-08-17 by its own author, before any run. TWO CLAIMS BELOW ARE WRONG and the
> superseded text is retained beneath this notice per convention.**
>
> **(1) "It is CPU, not GPU" is FALSE.** Measured by `sacct`: every actual bkgaware production job ran
> `shared_gpu_ss11` with `gres/gpu:a100=1`. My claim came from the *tracked* launcher's
> `--constraint=cpu`; **the production did not use that launcher.** So the mediator's GPU-denominated
> grant is in the RIGHT unit and my unit objection is withdrawn — I read a committed launcher as a
> description of what ran, which is the same class of error as reading `--time` as a cost.
>
> **(2) "One seed = 160 throws + 124 block re-unfolds" describes an ABANDONED path.**
> `CORRECTED_UQ_PRODUCTION_STATUS.md:598`: *"the OLD B5 throw-combine plan is SUPERSEDED (throws/blocks
> cancelled — redundant)"*; `:542` reframes it as **the vertical sweep, not the throw**. The candidate
> came from **188 universes** (169 vertical + 18 lateral + 1 CV), finalized `55912230`.
>
> **What survives, and is now the primary blocker: `--seed` is not an estimator-only knob.**
> `unified_throw_cov.py:525` has one `--seed`; it drives both the estimator (`→ omnifold_loop(seed=)`)
> and the throw realization (`:223 default_rng(args.seed + gj)` selecting which universes are drawn).
> **So a `--seed` scan cannot isolate estimator noise and violates run condition (b).** A committed code
> change separating the roles is required before any measurement means `M(ii)`.
>
> Full derivation, per-task measured costs, and what remains unmeasured:
> [`COST-20260817-mii-seed-scan-derivation.md`](COST-20260817-mii-seed-scan-derivation.md).


**The seed is a PRODUCTION parameter on this footing, not a scan parameter.** Measured:

* `unified_throw_cov.py:417-419` **refuses a mixed-seed combine**; the seed is *"stamped by
  `do_throws`/`do_blockunits`"*.
* `sbatch_uthrow_run_5d.sh` hardcodes **`--seed 1000`** at `:20`, and runs **20 CPU tasks × 8 throws = 160
  throws**, `--constraint=cpu --cpus-per-task=32 --mem=80G --time=12:00:00`.
* **`do_combine` REQUIRES the block slabs** — *"throws-only NOT supported — aborts 'no block-unit slabs …
  run `--blockunits` first'"* (`CORRECTED_UQ_PRODUCTION_STATUS.md:483`).
* **The blocks are the long pole:** *"blocks (124 reunfolds) are the true long pole, not throws"* (`:453`).
* A complete slab set is **542 slabs / 8.1 GiB** (`AUTONOMOUS_LOG_20260805.md:38`).

**So one additional seed = re-producing the full slab set: 160 throws + 124 block re-unfolds + a combine.**
**C's structural worry is confirmed by the code and by the production log: it is "a sweep per seed", not
"a draw per seed."**

**Three consequences:**

1. **`n = 1` is not a cheap probe.** The staging assumption inherited AI1's shape (12 lightweight bootstrap
   draws on one `npz`). It does not transfer.
2. **It is CPU, not GPU.** `--constraint=cpu`. **The 24-GPU-h grant is in the wrong unit and does not
   authorize this**, and CPU is this campaign's scarce resource.
3. **Therefore it is not the mediator's to approve.** It needs a derived CPU-node-hour cost and Joseph.
   **I have not run it and will not on the present authority.**

**What I did NOT do:** quote the `--time=12:00:00` ceiling as a cost (that would be the same error as
reading AI1's `--time=01:30:00` as 18 GPU-h — the ceiling overstates by an unknown factor), and I did not
derive a total from the 4D analogue, whose task shape differs.

## 7. WHAT THIS RUN CANNOT ESTABLISH

* **It measures seed contribution at ONE fixed draw on the candidate input.** Nothing about **seed × draw
  interaction** — the draw is held fixed deliberately, because otherwise seed variation is conflated with
  draw variation.
* **Nothing about any other cause**, and nothing about cause 3's other legs.
* **It is NOT an admission of the number into the budget.** The ledger excluded AI1 from the candidate
  budget; **a commensurable replacement must not smuggle itself in by being commensurable.** A MET verdict
  discharges a criterion; it does not add a block.
* **It does not revisit the footing finding** — `\gbdtAiEstTrace` remains disqualified, on the input ground
  (seed sensitivity is a function of the input) independently of J28.

## 8. RUN CONDITIONS (binding)

**(a)** consumes the **candidate's input** — the bkgaware bank/sweep, not `of_inputs_5d.npz`;
**(b)** varies **only** the estimator seed with the draw held fixed;
**(c)** reports the spread **against the candidate's own block sum**, so commensurability is by
construction;
**(d)** the **input digest is stamped at run time** and recorded in the receipt — named here as the
bkgaware bank and the candidate combined product, and deliberately **not** pre-filled from memory;
**(e)** **whatever the run produces is tracked or preserved off scratch from the moment it exists** —
`OI-130`. *"Copying fixes the instance and leaves the class"*; this run will not recreate the
`uq_cov_ai1est_5d.root` exposure with a fresher date;
**(f)** no repinning of receipt-bound launchers. **CHECKED RATHER THAN LEFT OPEN:**
`sbatch_uthrow_run_5d.sh` is named in **no** `state/*.json` receipt and
`verify_hash_bindings.py` reports `ALL BINDINGS INTACT`, so it is **not hash-bound** and a seed
override or a sibling launcher is permissible without a repin. **The seed is nevertheless hardcoded at
`:20`**, so varying it is an explicit code change and must be committed before the run, not passed as an
undeclared environment override — otherwise the arm's seed is unprovable from the tree.

---

## POST-HOC ANNOTATION, 2026-08-17 — appended, and the predeclared body above is UNTOUCHED

**Nothing above this line was edited.** A predeclaration's whole value is that it was written before the
measurement, so a correction to it goes here or nowhere (`BEN-244` records two stale references sitting
inside frozen predeclarations for exactly this reason). This block records what later measurement did to
one **operand** in the text above; it changes no predeclared criterion, threshold or branch.

**`28.50 A100-h` at `:88` and `:92` is SUPERSEDED. For a COMPOSITE ARM the figure is `39.078` A100-hours
PLUS `55.182` CPU task-hours (`2,759.1` CPU-core-hours).** The `39.078` alone (`+37.1 %` on `28.50`) is the
`C_syst` path: its lateral term had costed a **truncated attempt** — 5 of 19 universes (job `55891346`), with
the completion run `55894759` missing — and corrected from all 19 measured productions is
`23.840 + 14.2075 + 1.030 = 39.078` over **189** tasks.

**⚠ MY FIRST VERSION OF THIS ANNOTATION QUOTED `39.078` BARE, AND LANE A CAUGHT IT — the same defect a
fourth time, in the correction to the correction.** A declined to assert it, having not traced whether a
composite arm re-runs the `uthrow` leg or reuses it, and offered to withdraw. **It does not reuse, and the
code does not merely imply that — it refuses the alternative.** A composite arm's second seed is
`unified_throw_cov.py`'s `--seed`, which threads into every throw unfold (`:244`), every knob block endpoint
(`:281`) and every flux block unit (`:297`), is stamped into each slab (`:254`, `:285`, `:302`), and is
enforced by the F2 guard at **`:417-419`**, which raises `SystemExit` — *"refusing mixed-seed combine"* —
because *"else `C_uni`/`C_block` would mix estimator jitter across slabs."* **So all 71 CPU tasks re-run
(40 throw + 31 block: `55821660`, `56427580`, `55821661`), and that leg is `0` A100-hours against `2,759.1`
CPU-core-hours.** A's chain holds and is confirmed rather than withdrawn: **the composite arm's defining
move is the leg carrying essentially the whole CPU bill**, so a GPU-only successor fails *hardest* at the one
site whose predeclared point is that the figure omits composite scope. **The omission I introduced was
larger than the one I was fixing.**

`BEN-247`;
[`EXTENT-20260817-2850-a100h-scope-and-missing-legs.md`](EXTENT-20260817-2850-a100h-scope-and-missing-legs.md) §0.

**THE PREDECLARED CLAIM AT `:88-92` WAS RIGHT, AND MORE RIGHT THAN IT KNEW.** It says the figure covers the
`C_syst` path only, that the stat and ML blocks *"are unfolds too, so they are very likely seed-dependent as
well — I have not measured whether they are, or what they cost"*, and that **a composite arm may therefore
cost materially more than `28.50`**. All three held on measurement. The stat and ML legs **are**
seed-dependent, and one seed across all four blocks is `39.22` A100-h **plus `55.34` CPU task-hours**
(`2,764.7` CPU-core-hours) — a second unit the GPU grant does not reach, and the larger half.

**One predeclared expectation was WRONG in a way worth recording, because it was wrong in my favour.** The
text infers the stat/ML legs are *"very likely seed-dependent"* and treats that as raising the cost. They
are seed-dependent, but they are **nearly free** to scan — `0.1458` A100-h and `0.1550` CPU task-hours per
estimator seed — because `bootstrap_nd.py:19,21` and `seedscan_split.py:36` **already carry the two-role
`--estimator-seed`/`--fixed-data-seed` separation** that the `C_syst` path lacks. So the composite costs more
than `28.50` for a reason the predeclaration did not anticipate: not because the extra legs are expensive,
but because **the leg already counted was undercounted**, and because the extra legs are denominated in CPU.
**"Materially more" was the right call reached through a partly wrong mechanism**, which is the kind of thing
a predeclaration exists to expose and is recorded rather than smoothed over.

**`:88`'s closing instruction is unchanged and now has a number that satisfies it:** *"The number going to
Joseph must carry that scope."* It is **`39.22` A100-hours plus `55.34` CPU task-hours for one additional
estimator seed across all four blocks of the candidate** — and per §2b's own finding, funding does not make
the run possible: `sweep_bank_5d.py:252` and `unified_throw_cov.py`'s dual-role `--seed` still block it.
