# RULING — the `M(ii)` offset grid is `k_j = 1200·j`; the member count is **50**; and the priced grid **exceeds both ceilings**

**By:** lane C (PET), as `(B)`'s owner, answering the mediator's dispatch. **Three things, and they are
different KINDS of thing, which is why they are separated:**

| | | authority |
|---|---|---|
| **§1 the grid SHAPE** | `k_j = 1200·j` | **RULED.** Mine as `(B)`'s owner. |
| **§2 the member COUNT** | **`n = 50`**, `n = 20` floor, and the count is not independent of where `f` lands | **RULED**, with the cliff stated. |
| **§3 the COST** | **`1,921.9` GPU-h = `9.61×` the 200 GPU-h ceiling** | **REPORTED, NOT AUTHORIZED.** Not mine. |

> **THE HEADLINE, because it is the operand the mediator said it would not infer: `39.223` A100-h + `55.337`
> CPU task-h is the cost of ONE MEMBER.** The predeclaration says so in those words — *"`39.223` is one seed
> across **all four** blocks"* (`PREDECLARATION-20260817-mii-seed-scan-cause-3.md:32`). **So the figure that
> predates the grid decision assumed `n = 1`, which is not a scan.** Every grid with `n ≥ 6` exceeds the GPU
> ceiling, and the honest grid exceeds it by an order of magnitude.

**Everything below is derived this turn from the launchers and modules at `HEAD`, not recalled.**

> **⚠ LINE CITATIONS REPOINTED ONE COMMIT AFTER THIS RULING LANDED, AND THE REASON IS WORTH THE THREE LINES.** The measurements were taken at `808a028b`, where the throw-seed derivation was `unified_throw_cov.py:239` and the block-unit call `:295`. Merging `origin/main` (`214acdbb`, +19 lines in that file) moved them to **`:245`** and **`:306`** — same code, different coordinates. **Re-verified by content, not by offset**: `grep -n 'default_rng(args.draw_seed'` → `245`. *Recorded rather than silently corrected: this is `measure after the rebase, not before` arriving inside a document whose whole argument is a set of line-anchored facts, and a reader who checks `:239` today finds unrelated code.* **The three seed RANGES — `[1,100]`, `[1,24]`, `[1000,1159]` — are unchanged; they come from `--array` specs and a `--throws` count, neither of which the merge touched.**

---

## 1. THE GRID — `k_j = 1200·j`, `j = 0 … n−1`

```
g1 (sweep_bank_5d, bootstrap_nd, seedscan_split)   42 + 1200j  ->    42,  1242,  2442, …, 58842
g2 (unified_throw_cov: throws, blocks, combine)  1000 + 1200j  ->  1000,  2200,  3400, …, 59800
```

**`k = 0` is in it and is the archive.** `958 mod 1200 = 958 ≠ 0`, so **cross-group aliasing is impossible for
ANY `n`** — not checked at `n = 50` and hoped for beyond it. `42 mod 1200 ≠ 1000 mod 1200`, so **no `g1` value
ever equals a `g2` value, for any `n`.** Both are residue arguments, and that property is the one the grid
needed most: **§2's answer is a LADDER, so the grid has to stay legal when it is EXTENDED.** A hand-audited
grid is legal only at the `n` it was audited at.

### 1a. ⚠ AND THE `±958` PAIRWISE RULE IS NECESSARY AND **NOWHERE NEAR SUFFICIENT** — `BEN-462`

**Two of the four legs derive their per-unit seeds by ADDING SMALL INTEGERS TO THE SAME TWO BASELINES THE
OFFSET MOVES.** Measured at `HEAD`:

| leg | site | derived seed | range |
|---|---|---|---|
| `C_stat` | `sbatch_bootstrap_5d_gpu.sh:5,34` | `--seed ${SLURM_ARRAY_TASK_ID}`, `--array=1-100` | **`[1, 100]`** |
| `C_ML` | `sbatch_seedscan_split_5d.sh:5,19` | `--split-seed ${SLURM_ARRAY_TASK_ID}`, `--array=1-24` | **`[1, 24]`** |
| `C_syst` throws | `unified_throw_cov.py:245` | `default_rng(draw_seed + gj)`, `gj = 0…159` | **`[1000, 1159]`** |

*(The block-unit path takes `estimator_seed` only — `:306` — so `[1000,1159]` is the whole derived range, not a
lower bound on it. `160` global throws: `sbatch_uthrow_run_5d_fast.sh:5,9` — 40 tasks × 4 throws, union 0-159.)*

> **So the forbidden set is not `{±958}`. It is every offset that lands EITHER group's estimator seed inside
> ANY of those three ranges — and it is large: `361` forbidden values in `[−200, 1400]`, spanning
> `[−41, 1117]`. The smallest strictly-positive clean offset is `160`.**

**THE ILLUSTRATIVE GRID `k = 0…7` IS DIRTY AT EVERY NON-ANCHOR MEMBER, ON BOTH GROUPS — 14 coincidences among
7 members:**

```
k=1  g1 -> 43   in bootstrap [1,100]      g2 -> 1001  in uthrow [1000,1159]
k=2  g1 -> 44   in bootstrap [1,100]      g2 -> 1002  in uthrow [1000,1159]
…    identically through k=7
```

**What that means concretely: at `k = 5`, `bootstrap_nd` replica 47 draws its Poisson weights from seed 47
while the estimator inside that same unfold is seeded 47** — one value serving two roles in one job. And
`unified_throw_cov` at `k = 5` seeds its estimator `1005`, which **is throw 5's data-draw seed.** The
coincidence SITE MOVES WITH `k`, so it is not a constant shared by all members: it is a **per-member
structural difference**, which is exactly the confound §3 of
[`DETERMINATION-20260818-lanec-Bs-coherent-variation-is-an-offset.md`](DETERMINATION-20260818-lanec-Bs-coherent-variation-is-an-offset.md)
imposed the pairwise rule to prevent. **`build_plan` would pass all of it.**

**AND `k = 958` IS DIRTY FOR A SECOND, INDEPENDENT REASON:** `g1@958 → 1000`, which is throw 0's draw seed.
**The one value the existing guard catches, it catches for one of the two reasons it is bad.**

### 1b. Why `1200` and not `1000`, `997`, or `2000` — all three FAIL, and the near-misses are the argument

```
s=1000  FAIL   g1@1000 -> 1042  in uthrow [1000,1159]     (and its max seed lands exactly on 50000)
s= 997  FAIL   g1@997  -> 1039  in uthrow [1000,1159]
s= 500  FAIL   g1@1000 -> 1042  at j=2
s= 160  FAIL   g1@960  -> 1002  at j=6
s=2000  FAIL   g1@50000 -> 50042 (j=25), inside the PET gate-5 family's own base band [50000,50049]
s=1118+ OK
s=1200  OK     zero failures, and clean for ALL j because every seed at j>=1 exceeds 1159
```

**The general condition, stated so a later lane can re-derive rather than trust:** the interval `[958, 1117]` is
where a `g1` seed lands inside the throw range, so `s` must be large enough that no multiple of it falls there —
**concretely `s ≥ 1118`** — while any `s ≤ 160` puts some multiple inside it. **`1200` is the smallest round
number above that, and it also clears the `50000+i` band at every `j`.**

> **`50000+i` is the PET Gate-5 `C_stat` family's seed base (`build_cstat_gate5_n50.py:64`), a DIFFERENT
> pipeline and out of this scan's scope. It is checked anyway — excluding an out-of-scope range costs one line
> and discovering a collision with it afterwards would be indefensible.**

### 1c. The constraint to WRITE, superseding my own generalisation

**`seed_offset_policy.py`'s pairwise check is correct and should stay.** What it needs beside it:

> **CLEAN-OFFSET PREDICATE: for every `k ≠ 0` in the grid and every baseline `b`, `b + k` must lie outside
> every seed range the four legs derive by addition. The three ranges are `[1,100]`, `[1,24]`, `[1000,1159]`,
> each derived from a launcher's `--array` and from `unified_throw_cov.py:245` — so the predicate must READ
> them, not hardcode them, or it rots the first time an array widens.**
>
> **⚠ SUPERSEDED IN PART — this clause asserted the exemption without giving a REASON, and lane B correctly
> declined to wire a predicate on a fiat. The reason, the conditional disposition it implies, and the form the
> exemption must take are in
> [`DETERMINATION-20260818-lanec-anchor-confound-is-declarable-by-direction.md`](DETERMINATION-20260818-lanec-anchor-confound-is-declarable-by-direction.md) (`BEN-463`). The exemption
> stands; *"declare rather than repair"* is now conditional on the verdict's direction, and the exemption is a
> two-entry allowlist rather than a member skip.** *(Pointer added under this ruling's own linkage rule,
> `BEN-460`: a document must index what supersedes any of its rows.)*
>
> **`k = 0` is EXEMPT and must be: it is dirty on two of the three ranges, and that is a property of the
> PUBLISHED ARCHIVE, not of the scan.** The exemption is the honest shape — the anchor differs structurally
> from every other member, this cannot be fixed without abandoning the anchor, and **it is a limitation of
> `M(ii)` to declare rather than a defect to repair.**

## 2. THE MEMBER COUNT — **`n = 50`**, and the reason is a CLIFF, not a preference

**The bar is a one-sided negligibility test on a fractional sd** (`PREDECLARATION:80-86`): leg A
`f_agg = sd(block_sum)/block_sum ≤ 4.15 %`, leg B `f_med = median over bins of sd(σ_i)/σ_i ≤ 2.74 %`, **both
required.** The burden is therefore on smallness, and **the verdict must be taken on a BOUND, not on a point
estimate** — MET needs the upper one-sided 95 % bound under the bar; UNMET needs the lower bound over it, at
2.5 % per leg, because UNMET is a union over two legs while MET is an intersection.

**What each `n` can conclude** — `σ̂` bounds from `χ²_{n−1}`, exact, not the `1/√(2(n−1))` approximation:

| `n` | leg B MET if `f_med ≤` | leg B UNMET if `f_med ≥` | leg A MET if `f_agg ≤` | exceedance `1/(n+1)` | `c4(n)` |
|---|---|---|---|---|---|
| 4 | `0.94 %` | `4.84 %` | `1.42 %` | 20.0 % | 0.9213 |
| **6** *(the ceiling's grid)* | **`1.31 %`** | **`4.39 %`** | `1.99 %` | 14.3 % | 0.9515 |
| **20** *(floor)* | **`2.00 %`** | **`3.60 %`** | `3.03 %` | 4.8 % | 0.9869 |
| **50** *(ruled)* | **`2.28 %`** | **`3.28 %`** | `3.45 %` | **2.0 %** | 0.9949 |
| 100 | `2.42 %` | `3.12 %` | `3.66 %` | 1.0 % | 0.9975 |

### 2a. THE CLIFF — `n` required to reach ANY verdict, as a function of where `f` lands

```
true f_med   verdict      n     new runs      GPU-h       x200
   0.50 %      MET        3          2          78.4      0.4x
   1.30 %      MET        6          5         196.1      1.0x
   2.00 %      MET       21         20         784.5      3.9x
   2.50 %      MET      180        179       7,020.9     35.1x
   2.60 %      MET      524        523      20,513.6    102.6x
   2.70 %      MET    6,364      6,363     249,575.9   1247.9x
   -------------------- bar = 2.74 % --------------------
   2.90 %    UNMET      564        563      22,082.5    110.4x
   2.9969 %  UNMET      219        218       8,550.6     42.8x
   3.30 %    UNMET       47         46       1,804.3      9.0x
   4.40 %    UNMET        6          5         196.1      1.0x
```

> **THIS IS THE ANSWER TO *"how many members does `M(ii)` need to be a MEASUREMENT rather than an anecdote?"*
> and it is not a single number: the required `n` DIVERGES at the bar.** Far from the bar a handful of members
> settles it; within `±0.05 %` of it, no affordable `n` does. **A grid is not sized against a variance — it is
> sized against a DISTANCE TO A THRESHOLD that nobody has measured yet.**

**AND THE ONLY VALUE ANYONE HAS EVER QUOTED FOR THIS QUANTITY SITS IN THE DIVERGENT REGION.** AI1's
`2.9969 %`: `219` members to declare UNMET, `8,551` GPU-h, `42.8×` the ceiling. **It is inside `n = 50`'s
inconclusive band `[2.28 %, 3.28 %]` and inside `n = 100`'s `[2.42 %, 3.12 %]`.**

> **The predeclaration WITHDREW `2.9969 %` as evidence of reachability (§4), and I am not reinstating it.**
> Using it to LOCATE A DECISION PROBLEM is a weaker use than using it to predict an outcome, and the weaker use
> is licensed: it says *this decision may be near its threshold*, not *it will be*. **If it is admitted for
> nothing else, it is admitted for the observation that the affordable grid's inconclusive band contains it.**

### 2b. So why `50` rather than `100`, or `20`

**`50` is ruled on three grounds, none of them cost:**

1. **`1/(n+1) = 2.0 %` realized exceedance.** `BEN-025`'s rule is *prefer realized exceedance over a fitted
   gaussian tail*, and exceedance resolution is `1/(n+1)` **exactly** — distribution-free, no normality
   anywhere. `n = 20` buys `4.8 %`; `n = 6` buys `14.3 %`, which is not a tail.
2. **COMMENSURABILITY with the Gate-5 `C_stat` family, which is `N = 50`.** Any statement of the form *"the
   estimator-seed spread is small next to the statistical spread"* compares two sd estimates, and **comparing a
   6-member sd against a 50-member sd is an asymmetric comparison — this lane's own most-repeated failure.**
   Equal `n` makes the two spreads' sampling errors equal and the ratio's bias cancel to first order.
3. **`n = 20` is the FLOOR, not the target**: it is the smallest `n` whose exceedance statement reaches 5 %,
   and where leg B's decisive region first covers the plausible range `[2.00 %, 3.60 %]`. Below 20 the
   inconclusive band is wider than the range of values anyone would call interesting.

**`100` is NOT ruled**, and the reason is measured rather than budgetary: doubling the spend moves leg B's MET
threshold from `2.28 %` to `2.42 %` — **`+0.14` percentage points for `+1,922` GPU-h.** That is where the cliff
makes further members poor value.

## 3. THE COST — reported, in both units, and **a unit ambiguity that decides whether even ONE member fits**

**Per member:** `39.223` A100-h GPU; `55.337` CPU **task**-hours. And a task-hour is not a CPU-hour:

```
cores per task = 2759.1 core-h / 55.182 task-h = 50.00
one member = 55.337 task-h = 2,766.8 CORE-hours = 21.62 NODE-hours (128c)
```

| `n` | new runs | GPU-h | `/200` | task-h | `/500` | core-h | node-h |
|---|---|---|---|---|---|---|---|
| 6 | 5 | `196.1` | **`0.98×`** | `276.7` | `0.55×` | 13,834 | 108.1 |
| 20 | 19 | `745.2` | **`3.73×`** | `1,051.4` | **`2.10×`** | 52,570 | 410.7 |
| **50** | **49** | **`1,921.9`** | **`9.61×`** | **`2,711.5`** | **`5.42×`** | 135,576 | 1,059.2 |

*(`k = 0` costs nothing — the archive supplies it, subject to `P-ANCHOR` in §4. `n` members = `n−1` new runs.)*

> **⚠ THE `500 CPU HOURS` CEILING CANNOT BE APPLIED UNTIL ITS UNIT IS FIXED, AND THE READINGS DIFFER BY THREE
> ORDERS OF MAGNITUDE:**
>
> | reading of *"500 CPU hours"* | members it buys |
> |---|---|
> | task-hours *(the relay's table)* | **`n ≤ 10`** |
> | node-hours | `n ≤ 24` |
> | **core-hours** | **`n ≤ 1` — ONE MEMBER DOES NOT FIT** (`2,766.8 > 500`) |
>
> **The relay's table set `55.337 CPU task-h` against `500 CPU-h` and reported `~9×` headroom. Under the
> core-hour reading the headroom is `0.18` of a single member and the scan is unauthorized at `n = 2`.**
> **This lane cannot resolve it — it is what Joseph meant, and it must be asked rather than assumed.** The
> standing rule is *surface any run with its unit*; here the unit IS the verdict.

**Both ceilings are exceeded by the ruled grid on every reading.** Per the mediator's own operative rule this
goes to Joseph **before** submission, with the real number: **`1,921.9` GPU-h and `2,711.5` CPU task-h
(`135,576` core-h / `1,059` node-h) at `n = 50`; `745.2` / `1,051.4` at the `n = 20` floor.**

### 3a. And I am naming the shape the mediator warned about, because MY OWN affordable stage has it

**The mediator: *"a grid that lands at exactly 199 GPU-hours would worry me more than one at 400."*** **The
ceiling-affordable grid is `n = 6` at `196.1` GPU-h — `98.0 %` of the ceiling.** That is exactly the shape, and
the reason it has that shape is that **the ceiling was set at about five members and five members is what it
buys.** So:

> **I do NOT propose `n = 6` as the grid, and I decline to propose any `n` chosen to fit.** `n = 6` reaches a
> verdict only if `f_med ≤ 1.31 %` or `≥ 4.39 %` — **it cannot resolve anything in `[1.31 %, 4.39 %]`, a band
> `3.1` percentage points wide around a `2.74 %` bar, containing the only datum in evidence.** Buying it would
> most likely purchase an ensemble that cannot answer the question it was built for, **leaving `M(ii)`
> UNRESOLVED with 200 GPU-hours spent** — worse than every other outcome available, including not running.

## 4. WHAT I DO RECOMMEND RUNNING UNDER THE CEILING NOW — `0.013` GPU-h

**F-VALIDITY (`PREDECLARATION` §5) requires the per-seed outputs be shown mutually distinct with digests
recorded, and it is the one falsifier that can be discharged for nothing.** *"On this quantity the vacuous
outcome is indistinguishable from the desired one"* — a hook that silently fails to plumb gives spread zero,
which reads as the best possible result.

> **The `C_stat` leg is `+0.1458` of the `39.223` GPU-h member. Three offsets `{0, 1200, 2400}` × a 3-task
> subarray of `sbatch_bootstrap_5d_gpu.sh` ≈ `0.013` A100-h — `0.007 %` of the GPU ceiling.** It exercises the
> real hook, the real launcher, the driver's fan-out, the digest recording and the distinctness predicate, and
> it is the first submission of a driver that has never been submitted.
>
> **One detail for whoever runs it: pick subarray tasks that are NOT `42`.** At `k = 0`, task 42's bootstrap
> seed equals the estimator seed (§1a), so task 42 is the single task whose two roles coincide, and it is the
> worst available choice for a distinctness fixture.

**And a precondition I am flagging rather than assuming — `P-ANCHOR`.** `k = 0` costs nothing **only if the
archive's four-leg products are all present and the block sum is computable from them as they stand.** B made
*env-unset ≡ archive* structural in the launchers; that is a claim about the CODE. **Whether the archived
PRODUCTS are readable at `HEAD` is a separate check, it is cheap, and if it fails the anchor costs `39.223`
GPU-h and every figure in §3 moves up by one member.**

## 5. THE SEQUENTIAL RULE, pre-registered here because it cannot be written afterwards

If Joseph authorizes a range rather than a number:

1. **The verdict is computed ONCE, on the final ensemble.** Intermediate stages are triage, not tests, and
   their `f` may not be quoted.
2. **Early stopping is permitted for UNMET ONLY.** Extending only ever helps the MET side, so a
   stop-when-you-like rule inflates spurious METs and leaves spurious UNMETs alone. **The asymmetry is not
   fastidiousness — it is the direction the bar's burden already points.**
3. **INCONCLUSIVE resolves to NOT MET.** The bar asks whether the omitted contribution *cannot* change a
   published value; a bound that fails to exclude the change has not established that. **Pre-registered so
   "inconclusive" cannot become "pass" by exhaustion.**
4. **The ladder is `20 → 50`, and `1200·j` stays legal at every rung** (§1), so extension needs no re-audit.

## 6. `c4` — the sd estimator is biased **toward PASS**, and leg B's median does not average it away

`E[s] = c4(n)·σ`, so a raw sd **understates** the spread: `c4(6) = 0.9515`, `c4(20) = 0.9869`,
`c4(50) = 0.9949`. **At `n = 6` a true `f_med` of exactly `2.74 %` reads as `2.61 %` — a PASS on the bar it
sits on.**

> **And the bias does not wash out of leg B.** `f_med` is a median **over bins** of per-bin sds, all computed
> from the SAME `n` members, so `c4(n)` multiplies **every** bin identically: the median of biased estimates is
> the biased median. **More bins reduce the noise and not the bias.** So `c4(n)` is divided out explicitly on
> both legs and the correction stated in the receipt with its own `1/√(2(n−1))` uncertainty. **At `n = 50` it
> is a `0.51 %` relative effect and still worth writing down; at `n = 6` it is `5.1 %` and would move a
> verdict.**

## 7. Scope

- **RULED: the grid is `k_j = 1200·j`.** Mine as `(B)`'s owner. **D should review against this, not `0…7`.**
- **RULED: `n = 50`; `n = 20` is the floor; `n = 6` is refused as a grid.** With the cliff stated, so the
  ruling is falsifiable by the first measurement rather than by taste.
- **NEW CONSTRAINT, a finding rather than a preference: `BEN-462`.** The clean-offset predicate of §1c belongs
  beside `seed_offset_policy.py`'s pairwise check. **I am not writing it — that file is B's**, and a second
  author's guard inside another lane's module is how two disagreeing parsers get written.
- **REPORTED, NOT AUTHORIZED: the cost.** `9.61×` GPU / `5.42×` CPU-task at `n = 50`. **Mine to price, not to
  approve.**
- **RAISED, NOT RESOLVED: the CPU ceiling's unit.** Joseph's to answer.
- **NOT RULED: whether `M(ii)` is worth `1,922` GPU-h at all.** The cliff means the spend buys a *probable*
  verdict rather than a certain one — and *measured is not acceptable* still stands downstream of all of it.

*Second sought: lane B on §1c (its module, its `build_plan`) and on `P-ANCHOR`; lane A on §2's statistics,
which are the load-bearing part and which no second pair of eyes has yet touched.*
