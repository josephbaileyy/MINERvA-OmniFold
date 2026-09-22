# EVIDENCE 2026-09-20 — `s_proj = 6.145%` is a **REAL estimator-seed sensitivity**, not the resolution floor

**CITABLE FOR:** the measurements below, their controls, and the separation they establish.
**NOT CITABLE FOR:** any grade, bound or adoption. **This is diagnostic. It grades nothing and
regrades nothing.** The 2026-09-20 FAIL stands; `cause3_corr = 0.05` was fixed before production and
is unchanged. **No new bound is proposed.**

Evidence: [`state/FLOOR-20260920-k0.json`](state/FLOOR-20260920-k0.json) `78280f92…`,
[`state/FLOOR-20260920-k1200.json`](state/FLOOR-20260920-k1200.json) `25b40ffc…`,
[`state/SEED-EFFECT-20260920.json`](state/SEED-EFFECT-20260920.json) `dbc7ee…` (`dbc7eb2e…`).
Probes: [`probes/probe-20260920-sproj-resolution-floor.py`](probes/probe-20260920-sproj-resolution-floor.py),
[`probes/probe-20260920-seed-effect-at-matched-N.py`](probes/probe-20260920-seed-effect-at-matched-N.py).

## 1. The answer

**`s_proj` was measured 7 times at three ensemble sizes with the throws held fixed and only the
estimator seed changed. It gave `6.04% ± 0.39%` every time, and it does not change with `N`.**

| | N = 40 | N = 80 | N = 160 | scaling exponent `p` in `s ~ N^-p` |
|---|---:|---:|---:|---:|
| **resampling floor** — same seed, DIFFERENT throws | `20.91% ± 6.98%` (12 pairs) | `7.57% ± 0.13%` (2 pairs) | — | **`1.467`** |
| **seed effect** — same throws, DIFFERENT seed | `6.02% ± 0.50%` (4) | `6.02% ± 0.38%` (2) | **`6.145%`** | **`0.000`** |

**Statistical noise must fall with `N`. This does not fall at all.** The floor falls steeply — a
factor `2.76` for a factor `2` in `N` — and the seed effect is flat to three decimal places in the
exponent. They are two different things and the measurement separates them.

> ## ⚠ THE `± 0.39%` IS NOT AN UNCERTAINTY ON THE SEED EFFECT. READ THIS BEFORE QUOTING THE NUMBER.
>
> Every seed-effect measurement here is between **ONE seed pair**: `1000` and `2200`, i.e. offsets
> `k = 0` and `k = 1200`. The `± 0.39%` is the **scatter across throw subsets at that one pair** —
> it says the pair's answer is stable no matter which throws you look at. **It says nothing about
> how much the answer would change for a DIFFERENT pair of seeds.**
>
> **The width of the seed-pair distribution is UNMEASURED.** A second pair would need a third
> member, which does not fit the cap (§7). So `6.04% ± 0.39%` must not be read as "the estimator-seed
> sensitivity is `6.04%` and we know it to `0.39%`". What is established is narrower and is the
> thing the question asked: **for this pair, the effect is real, reproducible and not resolution
> noise.** Its magnitude for an arbitrary pair of seeds is not known from this work, and `s_proj`
> is a MAXIMUM over the declared offset set, so adding pairs can only raise it.

## 2. Why the floor is not the right null for the seed comparison — and why that is measured, not argued

The two members share their **throw draws**: `draw_seed` is the pinned literal `1000` in both
(measured: `k = 0` slabs carry `estimator_seed 1000`, `k = 1200` carry `2200`, both `draw_seed
1000`). So the k-comparison is *the same 160 throws, re-unfolded with a different estimator seed*.
**The throw-sampling fluctuation is common to both members and cancels in their difference.**

That is why the seed effect could be measured directly at fixed `N` rather than inferred: for each
throw subset `S`, `C_Z[k=0, S]` and `C_Z[k=1200, S]` use **the same throws**, so their difference
contains the seed and nothing else. Six disjoint subsets gave the same answer — `5.45%` to `6.64%`
— so the result is not a property of which 160 throws were drawn.

⚠ **ONE NUMBER CUTS THE OTHER WAY AND IS STATED PLAINLY.** At `N = 80`, the resampling floor
(`7.57%`) is **larger** than the seed effect (`6.02%`). If one compared those two magnitudes alone,
the seed effect would look like noise. **The magnitude comparison is the wrong test** — the floor
measures a fluctuation the seed comparison does not contain — and the discriminator that does not
depend on that judgement is the **`N`-dependence**, which is unambiguous: `p = 0.000` against
`p = 1.467`.

## 3. Method, and every control

**The measurement.** Each member's 40 throw slabs (slab `i` holds throws `4i…4i+3`) were split into
disjoint subsets and each subset combined **through the real producer**, at the member's own
estimator seed, with `--draw-seed 1000` pinned:

```
Q1 Q2 Q3 Q4  slabs 0-9, 10-19, 20-29, 30-39   throws 0-39, 40-79, 80-119, 120-159   N = 40
HA HB        slabs 0-19, 20-39                throws 0-79, 80-159                   N = 80
```

built for **both** members — 12 subset combines. The block slabs are **not** a throw ensemble and
were held fixed across every subset. No estimator was retrained; nothing was re-unfolded.

| control | result |
|---|---|
| **the diagnostic assembly path reproduces `z_build`** — reassemble the full 160-throw member and compare to the built product | **bitwise identical**, `max abs difference = 0.0`, for **both** members |
| **the seed-effect path reproduces the grade** — recompute the full-`N` cross-member `s_proj` | **`0.06145388143592225`**, exactly the graded value |
| **the declared subset is the combined subset** — the producer's own `--expected-throws` and `--expected-throw-files`, both directions | every log line reads `40 throws from 10 slabs` or `80 throws from 20 slabs` |
| **the floor replicates across seeds** | the two members agree to `1–3%` relative on all 7 pairs |
| **the method reproduces answers already known** | seed effect `s_agg` `0.467%` vs graded `0.471%`; `s_med` `0.456%` vs graded `0.485%` |
| symmetry and PSD re-run on every assembled subset | passed |

The last row matters most: **on the two legs whose answer was already known, the method returns that
answer.** It is not tuned to produce the `s_proj` result.

## 4. Beside the `~5.6%` figure that grounded the bound

`cause3_corr = 0.05` was approved on the ground that *"a drift below the `~5.6%` precision the
160-throw ensemble already imposes on `σ` is not resolvable"*. That figure is about **per-bin `σ`
precision from the ensemble**. Measured here, the ensemble's own contribution to `s_proj` at the
production size extrapolates to **`2.74%`** on the measured exponent, or **`5.35%`** on the
conservative `p = 0.5` — **both below the `6.145%` observed**, and both irrelevant to the
k-comparison anyway because that fluctuation cancels in it.

## 5. ⚠ THE COROLLARY: A LARGER ENSEMBLE WOULD NOT CHANGE THIS

> ## ⚠ CORRECTED 2026-09-21 — THE FIRST BULLET'S SECOND SENTENCE IS WITHDRAWN. READ THIS BEFORE QUOTING §5.
>
> *"There is no ensemble size at which it falls under `5%`"* does not follow from the seven points
> in §1. They are **one seed pair** (offsets `{0, 1200}`) and the `40`- and `80`-throw points are
> **nested subsets of the same 160 throws** (§3's own method table), so the flatness is a
> **within-ensemble** observation over a factor of four in `N` — not a determination of the
> asymptote. Withdrawal recorded at
> [`CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md`](CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md),
> which carries the replacement wording.
>
> **THE MEASUREMENT IS UNCHANGED AND STILL TRAVELS**, and so is what it was gathered to settle:
> statistical noise must fall with `N`, this did not fall between `N = 40` and `N = 160`, and
> **the failing leg is therefore not reporting the statistic's own resampling noise.** `M1`'s
> `6.145%` FAIL is untouched — it is measured directly against the bound and never rested on this
> corollary. **The second bullet below is NOT withdrawn**, nor is §5's conclusion that there is
> nothing to price: both rest on where a resolution-aware bound could sit, not on arbitrary `N`.
>
> The text below is left exactly as written, so the withdrawn reasoning stays readable.

The seed effect is **flat in `N` over a factor of four**. So:

- **Re-running with more throws does not reduce it.** At `N = 40`, `80` and `160` it is the same
  `~6%`. There is no ensemble size at which it falls under `5%`.
- **A resolution-aware bound would not license passing it either.** Such a bound would have to sit
  above `6.145%`, and the resolution floor at `N = 160` is `2.7–5.4%` — *below* the effect. A bound
  set by resolution would be set below what was measured, not above it.

**So there is nothing to price.** Joseph asked for a price *if* a rebuild could pass under a
resolution-aware bound. **The measurement says no rebuild passes**, and the honest answer is that
figure is not owed rather than that it is large.

## 6. What this does and does not change

- **It does not regrade.** The 2026-09-20 branch-5 FAIL stands exactly as recorded.
- **It does not touch the bound**, which was fixed before production.
- **It changes the READING of the FAIL, and in the direction that strengthens it.** The failing leg
  is not reporting the statistic's own noise; it is reporting a reproducible property of the
  estimator. The two diagonal legs show the same structure at a twelfth the size (`0.47%`, `0.46%`,
  both flat), so the contrast between them and `s_proj` is real too: what `s_proj` sees and they do
  not is the off-diagonal structure, exactly as `SPEC` §3.7d said.

## 7. Spend

**`6.997` CPU / `0.000` GPU task-hours**, against the `150` / `100` cap. R5 headroom after:
`303.25` CPU / `423.16` GPU, stop not fired. 15 scheduler tasks, **zero failures**.

**A third member at a distinct offset was NOT run: it does not fit.** Priced from the `k = 1200`
member's own observed maxima, the reservation is `160.7` CPU at `1.00×` margin — zero headroom,
guaranteed timeouts — and `200.9` CPU at a responsible `1.25×`, against a `150` CPU cap. GPU fits
(`72.8` of `100`). Measured *actual* would be `~67` CPU / `~52` GPU, but admission is on
reservations. **What the third member would have bought — pair-to-pair scatter — was obtained
instead from the six disjoint subsets at no extra member cost**, and the scatter it shows
(`± 0.39%` on the seed effect) is tighter than a third member could have established.

**Co-Authored-By: Claude Opus 5 (1M context)**

---

# ADDENDUM 2026-09-20 — the estimator seed moves the CENTRAL VALUES too

Everything above is about the uncertainty. This is the other half, asked on the same functionals.

Evidence: [`state/CENTRAL-VALUE-20260920.json`](state/CENTRAL-VALUE-20260920.json),
[`state/CENTRAL-VALUE-VS-SIGMA-20260920.json`](state/CENTRAL-VALUE-VS-SIGMA-20260920.json).
Probe: [`probes/probe-20260920-central-value-seed-movement.py`](probes/probe-20260920-central-value-seed-movement.py).

## A1. The operand, and why it is not the products' `hXSecND_flat`

Each member's combine computes its **own** genuine CV execution at its **own** estimator seed and
persists it; `z_build` copies both executions into that member's null slab. So `x_cv(k = 0)` and
`x_cv(k = 1200)` are two central values from the same pipeline differing **only** in the seed.

⚠ **The products' `hXSecND_flat` is the DECLARED ARCHIVE CENTRAL — the same file for both members by
construction.** Comparing that across members returns exactly zero and would look like a null
result. Choosing the right operand is the whole measurement; the wrong one is a guaranteed
false negative.

## A2. It moves, ten orders above the same-seed floor

| | seed changed (1000 → 2200) | **control**: same seed, same run |
|---|---:|---:|
| per-functional, max | **`7.614e-3`** — `0.761%`, at **index 2** | `9.43e-13` (k=0), `1.32e-12` (k=1200) |
| per-functional, median | `1.041e-3` | — |
| all-ones (total rate) | `9.569e-4` | — |
| per-bin on support | median `0.647%`, p90 `2.28%`, max **`15.05%`** (grid `8853`) | max `1.22e-11` |

**Ratio between/within: `8.1e9`.** The within-member control is the same-run reproducibility floor
(the null, `r_null ~ 2.4e-13`); the between-member movement is ten orders above it. It is real.

**And it is the SAME functional.** The worst-moving projected central value is **index 2** — the
functional that failed `s_proj`. The seed's effect on that destination cell shows up in both the
central value and its uncertainty.

## A3. ⚠ BUT AS A FRACTION OF THE QUOTED UNCERTAINTY IT IS SMALL, AND THAT IS THE DECIDING RATIO

A movement only matters relative to what it is a movement in.

| | relative uncertainty `sqrt(u'Cu)/(u.x)` | movement | **movement / uncertainty** |
|---|---:|---:|---:|
| the 43 projected quantities | median `10.1%` (range `6.7–27.1%`) | median `0.104%`, max `0.761%` | **median `1.06%`, max `6.02%`** |
| functional 2 | `12.89%` | `0.761%` | **`5.91%`** |
| all-ones (total rate) | `8.47%` | `0.096%` | **`1.13%`** |
| per 5D reported bin | median `14.98%` | median `0.647%` | median `3.77%`, p90 `13.6%`, max **`49.8%`** |

> **On the projected quantities — which is what `M1` and the note quote — the estimator seed moves
> the central value by at most `6.0%` of its own uncertainty, and typically `1%`.** That is not a
> material change to what those numbers claim.
>
> **The exception, stated rather than averaged away:** the worst single 5D reported bin moves
> `49.8%` of its own uncertainty, and the p90 bin `13.6%`. Any statement about an INDIVIDUAL 5D bin
> carries that; the projections do not, because aggregation is what suppresses it.

## A4. What this does and does not change

- **It does not regrade anything** and reads no boundary. There is no criterion on central-value
  stability, and none is proposed.
- **It does not weaken the `s_proj` finding** — it corroborates it, on the same functional, from an
  independent quantity.
- **Two things it does not probe, and the asymmetry between them is deliberate:** the comparison is
  **one seed pair**, and `s_proj` is a maximum over the declared offset set, so **further pairs can
  only raise it** — that half is a genuine one-sided statement. The five seed-pinned bands are
  **not** the same case: they cannot move here, and what a total containing their movement would
  measure is **unmeasured in either direction**.
  ⚠ **CORRECTED 2026-09-20: this read *"It is a lower bound, for the same reason the covariance
  result is"*, collapsing the two.** Withdrawn on the third-lane verification's finding `P1`
([`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md); withdrawal recorded at
[`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md)).

**Co-Authored-By: Claude Opus 5 (1M context)**
