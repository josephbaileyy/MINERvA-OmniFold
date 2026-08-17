# PREDECLARATION — cause 3's `M(ii)` seed scan

**Committed BEFORE execution. Lane B, 2026-08-17.** Bar confirmed by a second lane (C) via the mediator;
the three amendments it returned are incorporated below, one of which retracts a conclusion of mine.

**⚠ AND THE RUN IS BLOCKED ON COST AND AUTHORITY — see §6. `n = 1` as scoped is not a cheap probe, and
that is a measured finding, not a caveat.** This file is committed anyway: a predeclaration's value is that
it exists before the run, whenever the run happens.

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
