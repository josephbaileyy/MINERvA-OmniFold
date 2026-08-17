# COST derivation for cause 3's `M(ii)` seed scan — and two corrections to my own blocking report

**Lane B, 2026-08-17. Read-only: `sacct` and code reads only. No job submitted, cancelled or requeued.**

**Headline: the total is NOT derivable from the record as it stands, and I will not manufacture one.** What
*is* measured is below, together with two corrections to my previous message and a **third blocker that is
larger than cost**.

---

## 1. CORRECTION — I said "it is CPU, not GPU." That is WRONG.

I blocked the run partly on the ground that the mediator's grant is GPU-denominated while the work is CPU.
**Measured, every actual bkgaware production job ran on GPU:**

```
55885596  uthrow5dBKG     shared_gpu_ss11   gres/gpu:a100=1  cpu=32
55885597  uthrow5dBKGb    shared_gpu_ss11   gres/gpu:a100=1  cpu=32
55891028  chkbkgbr        shared_gpu_ss11   gres/gpu:a100=1
55891346  det5dBKG        shared_gpu_ss11   gres/gpu:a100=1
55912230  fin5dBKG        shared_gpu_ss11   gres/gpu:a100=1
```

My claim came from the **tracked launcher** `sbatch_uthrow_run_5d.sh` (`--constraint=cpu`, 20 tasks × 8
throws). **The bkgaware production did not use that launcher** — it used GPU variants with a different task
decomposition (40 × 4). **So the grant is in the right unit and the unit objection is withdrawn.** The
block stands on **cost**, not on units.

**The generalisable error: I read a tracked launcher as a description of what ran.** The launcher is the
committed intent; `sacct` is what happened. Same class as reading `--time` as a cost.

## 2. CORRECTION — the candidate was NOT built by "160 throws + 124 block re-unfolds"

I costed that structure. **It was abandoned.** `CORRECTED_UQ_PRODUCTION_STATUS.md:598`:

> *"the OLD B5 throw-combine plan is **SUPERSEDED** (throws/blocks **cancelled** — redundant)."*

and `:542` — *"B5 REFRAME (#13 fix is the **VERTICAL SWEEP**, not the throw)."* The candidate came from the
**B5′** path: **188 universes = 169 vertical bank-sweep + 18 lateral direct-driver + 1 CV**, finalized by
`55912230` (`:703`).

**Confirmed by `sacct`: `55885596` and `55885597` show only 12 COMPLETED tasks each plus 2 CANCELLED** —
they are truncated attempts, not a production. **Quoting their scaled total would have been the cost of a
path nobody took.**

## 3. WHAT IS MEASURED — realized elapsed × GPUs, per task

| job | leg | COMPLETED tasks | elapsed/task | A100-h measured |
|---|---|---|---|---|
| `55885596` | throws (abandoned path) | 12 of ~40 | 32.4–33.5 min | 6.56 |
| `55885597` | blocks (abandoned path) | 12 of ~32 | 15.7–16.3 min | 3.20 |
| `55891028` | branch-check | 1 | 1.3 min | 0.02 |
| **`55891346`** | **`det5dBKG` (lateral leg)** | **5** | **41.6–45.6 min** | **3.63** |
| **`55912230`** | **finalize** | **1** | **61.8 min** | **1.03** |

**All single-node, `cpu=32`, `gres/gpu:a100=1`.**

## 4. WHY NO TOTAL — and why I am not scaling to one

**Every job id the status log names for the SWEEP legs is `CANCELLED`:**

```
55891356  sweep5dBKGdump   array [2-7]        CANCELLED by 112498
55891357  sweep5dBKGrun    array [1-169%48]   CANCELLED by 112498     <- the 169 vertical universes
```

So the surviving vertical sweep ran under an id the log does not name at those lines, and **the dominant
leg's realized rate is not in hand.**

**I will not multiply `55891357`'s task count (169) by `55891346`'s per-task rate (~43.5 min) to get
~123 A100-h.** A bank *sweep* and a detector *re-unfold* are different operations; assuming a common
per-task rate is precisely the *"different shape, same factor"* error C warned about and that made AI1 look
like 18 GPU-h. **The honest statement is: the sweep leg's cost is unmeasured, and finding the surviving id
is the next step.** It is cheap — one `sacct -u` window scan — and I will do it on your word rather than
guess now.

**Wall-clock and queue, separately from node-hours, as asked:** throw tasks ran ~33 min with a `%10`
throttle (≈4 waves ≈ 2.2 h wall); block tasks ~16 min; `det5dBKG` ~45 min at 5-wide. **Queue latency is a
first-order factor, not a rounding term** — the log records `gpu_shared` repeatedly fairshare-sticking
(*"55871150 STUCK pending (fairshare 0.09)"*, *"gpu_shared stuck"*) and escalating to interactive
`salloc`. **A session-length estimate cannot be made from node-hours alone here.**

## 5. REUSABILITY ACROSS SEEDS — the answer is NO, and it is code-derived

The mediator asked whether the slab set can be reused, warning that taking *"a sweep per seed"* at face
value would be over-reading in the opposite direction. **Checked, and it cannot:**

* `unified_throw_cov.py:281` — the block leg calls
  `_xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed)`, and
  `compare_unified_throw.py:110-126` passes that straight into `omnifold_loop(..., kind="lgbm", seed=seed)`.
  **The estimator seed enters every block unfold.**
* `:285` stamps `seed=np.int64(args.seed)` into each block slab.
* `:244`, `:314` — the throw and CV legs call the same helper with the same seed.

**So both halves are seed-dependent and neither is reusable.** *"A sweep per seed"* is accurate, not
rhetorical.

## 6. ⚠ A THIRD BLOCKER, LARGER THAN COST: `--seed` IS NOT AN ESTIMATOR-ONLY KNOB

**`unified_throw_cov.py` has exactly ONE seed flag** — `:525`, `--seed`, default `1000` — **driving two
distinct roles:**

1. **the estimator seed** for every lgbm unfold (`→ omnifold_loop(seed=seed)`);
2. **the throw realization**, `:223` `rng = np.random.default_rng(args.seed + gj)`, which selects **which
   band shifts and which flux universes are drawn** (`:224`, `:232`).

**So varying `--seed` changes the drawn universes at the same time as the estimator.** A `--seed` scan on
this footing measures **estimator noise convolved with throw-resampling noise** — which is not `M(ii)`, and
**directly violates run condition (b)** (*"varies only the estimator seed with the draw held fixed"*).

**And the irony is exact: this is the axis on which AI1's design was praised.** The run conditions say
*"AI1's fixed-draw design was right on that axis, keep it"* — AI1 could keep it because it had **two** flags
(`--seed` and `--fixed-data-seed`). **The candidate's producer has one.** So the property we required cannot
be kept on the footing we required it on.

**Consequence:** `M(ii)` is **not measurable on the candidate footing** until the two roles are separated —
a small, testable, *committed* change to `unified_throw_cov.py` (e.g. `--estimator-seed` defaulting to
`--seed`, with the throw RNG pinned). That is a change to a shared, provenance-heavy module and must be
predeclared and reviewed, **not slipped in**. `verify_hash_bindings.py` reports `ALL BINDINGS INTACT` and
that module is in no `state/*.json` receipt, so no repin is implicated — but the guard at `:417-419` that
the whole criterion leans on lives in the same file.

## 7. WHAT GOES TO JOSEPH

1. **The sweep leg's cost is unmeasured** — one `sacct` window scan away, not an estimate.
2. **It is GPU, not CPU** (my correction), so his grant's unit applies; whether it clears 24 A100-h depends
   on (1).
3. **A code change is required before any measurement means `M(ii)`** — §6. **This is the decision he
   should see first**, because it is not a cost question and it does not go away by funding it.
4. Measured per-task costs (§3) so the eventual proposal quotes realized elapsed rather than a `--time`
   ceiling.

**Nothing run. `OI-130`'s preservation condition binds whatever any eventual run produces.**
