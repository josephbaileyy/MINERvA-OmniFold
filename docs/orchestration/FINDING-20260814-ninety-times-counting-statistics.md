# FINDING 2026-08-14 — Ninety times counting statistics, a wrong explanation, and a grep that could not have found the truth

**`BEN-232`** (the measurement and the retracted explanation) and **`BEN-235`** (the reusable mechanism).
Lane C (PET). **Status: the explanation is REFUTED — by me, the same day, after the mediator flagged it.**
**Evidence:** [`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json)
and the scripts and verbatim stdout in
[`state/gate5-cstat-spec-measurements-20260814/`](state/gate5-cstat-spec-measurements-20260814/).

> **Read this first.** This file originally argued that the Gate-5 replica network was **unseeded**, that
> the covariance was therefore `C_stat + C_train` and inseparable, and — in a later commit — that
> `C_total` **double-counts** `C_ML`. **Every one of those conclusions was false.** The measurement they
> rested on is fine. What was wrong was a single factual premise that two greps would have settled, and
> the interesting content of this finding is now **why my search could not have found it**, plus **what
> the measurement means once the wrong explanation is removed.**

---

## 1. The measurement, which is unaffected

| quantity | value |
|---|---|
| relative sd of `total_sigma_cm2_per_nucleon` across members | **4.478 %** |
| Poisson expectation, `n_data = 4,116,128` | **0.0493 %** |
| **ratio** | **≈ 90×** |
| (max − min) / mean | 18.187 % |
| median abs deviation / mean | 1.676 % |
| per-cell relative sd, median / max | 0.151 / 0.794 |

Nothing here is retracted. An integrated quantity over 4.1M data events fluctuating by 4.5% is a real,
large, and initially surprising number, and it deserved the attention it got.

## 2. The explanation I gave, and its refutation

**I claimed:** `set_seed` appears nowhere in `nd-unfolding/` or `omnifold_nn/`, so weight initialization,
batch shuffling and reduction order are free-running; each member therefore differs by its Poisson draw
**and** by training stochasticity; the object is `C_stat + C_train`, inseparable from this family.

**The estimator seed is pinned at 42 for every member.** Verified three ways, the third being the one that
settles it:

1. `sbatch_gate5_replica_train_array.sh:63-71` passes **only** `--bootstrap-seed` and `--replica-index`.
2. `train_fullevent_replica.py:236` calls `nominal.main([...])` **without** `--estimator-seed` — so
   `train_fullevent_nominal.py:335` takes its default `NOMINAL_SEED_POLICY["estimator_seed"]` = **42**
   (`:69`), and `:376` executes `tf.keras.utils.set_random_seed(42)`. The seeding *is* on the replica path:
   the replica driver monkey-patches three nominal functions and then delegates to nominal's own `main()`.
3. **Measured from the artifacts.** All **50** `GATE5_REPLICA_WEIGHTS.npz` carry exactly **one**
   `seed_policy`, containing `estimator_seed: 42`. And `train_fullevent_replica.py:275` is
   `if seed_policy != nominal.NOMINAL_SEED_POLICY: raise SystemExit` — so the agreement is **enforced per
   member**, not coincidental.

So the members differ in **one** way, not two, and `C_stat` is correctly named.

## 3. `BEN-235` — why the search could not have found it, which is the transferable part

I ran:

```
grep -rln "set_seed" nd-unfolding/ omnifold_nn/          -> no output
```

and reported *"`set_seed` appears **nowhere**."* The call is **`tf.keras.utils.set_random_seed`**, and

```
"set_random_seed".find("set_seed")  ->  -1
```

**`"set_random_seed"` does not contain the substring `"set_seed"`.** The intervening `random_` breaks it.
My other patterns were no better: `tf.random` misses `tf.keras.utils.*`; `np.random.seed` is a different
library; `TF_DETERMINISTIC_OPS` and `PYTHONHASHSEED` are environment knobs that were never the mechanism.
**Not one of my patterns could have matched the line that refutes me.**

That is the generalisable defect, and it is sharper than "I made a typo":

> **An inference from absence is only as strong as the search that would have refuted it.** A negative
> result is evidence *about the search*, and only becomes evidence about the world once the search is
> known to cover the thing being denied. Mine did not, so the silence carried no information at all — and
> I converted it into a headline finding, a long-form document, an `OI` addressed to Joseph, and
> eventually a claim that the published covariance double-counts another component.

**Two cheap habits that would each have caught it:**

- **Grep the API family, not the API.** `grep -rn "seed" nd-unfolding/pet/train_fullevent_nominal.py` is
  noisier and would have returned `:69`, `:335`, `:376` immediately. When the conclusion is *"X is
  absent"*, widen until the search would obviously find X if present, then narrow.
- **Prefer asserting the positive from an artifact.** The weights NPZ recorded
  `estimator_seed: 42` on all 50 members the entire time. **The refutation was sitting inside the very
  files I had already been measuring all day** — I had read `seed_policy` out of them for a different
  check. A claim about what the code does is best settled by what the products record.

There is an uncomfortable symmetry worth keeping: **`BEN-234`, filed hours earlier, is that tagging a
claim UNVERIFIED is not the same as not relying on it.** This is the same failure with the label removed —
I did not even tag this one, because a `grep` returning nothing *feels* like a measurement. It is not.

## 4. What survives, and it is a physics question

With training held fixed, the 4.478% is the **statistical draw propagated through the unfolding** — i.e.
**the unfolding amplifies the fluctuation by ~90× over naive counting.** That was always the alternative
reading this file named and declined to rule out; it is now the surviving one.

**This is not a defect claim.** Every varying input is a legitimate statistical draw — the data Poisson
factor, the signal and background factors, and the per-replica Stay-Positive target rebuild — so a spread
exceeding `1/√n_data` is expected, and amplification is what an iterative, flexible-estimator unfolding
does. **What is not established is whether ~90× is the right size**, and that question lands squarely on
`niter = 3` as a regularization choice — which `docs/OPEN_ITEMS.md` items (d)/(e) already record as owing
a **bias-variance** justification rather than a gate-behaviour one. A regularization parameter chosen
because closure passed is exactly what an amplification factor would expose. **`OI-94`.**

Ingredient, not a derivation: in the same family `R` spans **1.1225–1.1253** (a 0.25% range) while the
total spans **4.5%** — roughly **18×** between the class-ratio input and the extracted total.

## 5. What also survives: the pair really had no disjointness proof

The double-count claim was wrong, but the observation under it was not. **`C_stat` + `C_ML` is the one
component pair in this chain with no written disjointness proof**, while
`assemble_ctotal_bkgsub.py:10-20` carries an explicit one for `C_syst + C_retrain` — including a statement
of the construction that *would* have failed. That standard existed and this pair had not met it.
`SPEC` `CSTAT-D4` now supplies it: `C_stat` varies the Poisson draw with the estimator seed pinned and
**enforced**; `C_ML` varies the estimator seed with the draw fixed (`RUNBOOK:223-224`); disjoint inputs,
so the sum does not double-count. **Enforced rather than lucky** — `:275` would abort a member whose seed
policy drifted, so a future edit that started varying the seed per replica would fail the family instead
of silently corrupting the sum.

## 6. Residual, and the test that is still worth running

`set_random_seed` does **not** defeat GPU non-determinism (cuDNN atomics, non-deterministic reductions)
unless determinism ops are enabled, and they are not. So some training variance still leaks into `C_stat`
despite the pin, and its size is **unmeasured**.

**`CSTAT-O2a` therefore keeps its cost and changes its justification.** Re-**train** one index twice at
the same `bootstrap_seed` and extract both: a fully deterministic pipeline returns bit-identical results,
and the departure from that measures the **non-determinism floor** — a number `C_ML` wants independently
as the floor its crossed-seed spread must clear, and which bounds how much of the 4.478% is not the draw.
Extraction is deterministic given weights, so the repeat must be of **training**. ~5 tasks, ~14.5 min each.

## 7. Disposition

- **`OI-92` CLOSED.** `C_stat` is correctly named; no decision needed from Joseph.
- **`OI-94` OPEN** — the ~90× amplification, coupled to the `niter = 3` regularization justification.
- **`BEN-235` filed** for the search-vs-absence mechanism, which is the part with reuse value.
- **`CSTAT-D4` written** into the spec, converting the disjointness from an unstated construction into a
  documented and enforced one.
- **Nothing was retracted from the measurement**, and nothing about the family's own validation changed:
  the 50/50 `FAMILY_COMPLETE_PASS` never depended on any of this.
