# The GPU floor's shape-noise is heterogeneous across the OI-126 tail — and the ceiling test that appeared to corroborate it has no power

**Status: MEASURED, on `central_vector` (shape) only. NOT a claim about the tail's composition.**
Filed by the mediator. Every figure below was computed by the filer from artifacts on `/pscratch`,
not relayed. Supersedes nothing; complements `VL130` and lane C's
`RULING-20260817-lanec-floor-vs-family-coherence.md`, which governs the interpretation.

## What this is and is not

`VL130`'s per-cell floor is computed on `central_vector`, which **sums to 1 by construction** and is
therefore blind to normalization — `VL130`'s own text says it **understates** the absolute noise. The
`C_stat` family's spread is on `xsec`. Lane C's ruling establishes that this makes any floor/family
**ratio** an upper bound and disqualifies it from travelling.

**So the result below is a statement about SHAPE-noise heterogeneity, which is weaker and different
from a statement about the tail's composition.** It is filed because the shape axis is the one
`VL130` lives on, and a heterogeneity structure there is a real fact about the floor.

**On expressing this as a variance share — DO NOT, without the qualifier.** Lane C reframed the
comparison as a quadrature variance share (~2%), which is arithmetically right and rhetorically
dangerous: **it asserts a decomposition we have explicitly declined to assert.** `VL130`'s own words:

> **ASSUMPTION, stated not proved:** `f/√k` presumes the scatter is independent across processes;
> for GPU reduction-order non-determinism that is an empirical claim about run-to-run behaviour,
> and `n=4` cannot test it.

Squaring an sd ratio into a variance share **requires the floor to be an independent quadrature
component of the family**. Trap 3 says we have not established that: **different component** (GPU
non-determinism vs refit noise), **different observable** (shape-only `central_vector` vs `xsec`),
and — see below — **different domain**. You cannot quadrature-decompose quantities measured on
different bases. Note also the direction: **~2% *sounds* negligible in a way *a seventh* does not**,
which is precisely the shape nobody checks.

**THE DEFENSIBLE FORM IS A CORRELATION BRACKET, AND IT NEEDS NOTHING UNMEASURED.** Lane C's
rev-4 supersedes both the variance share and the bare sd comparison. Solve `s² + 2ρsf + f² = T²`
for the residual `s` at `T = 67.1164%`, `f = 8.6088%`, over the whole range of `ρ` — re-derived by
the filer:

| `ρ` | residual | reduction | floor / residual |
|---|---|---|---|
| `+1` (sds subtract linearly) | **58.5076%** | 12.83% | 0.1471 |
| `+0.5` | 62.3966% | 7.03% | 0.1380 |
| `0` (quadrature — the `~2%` case) | 66.5620% | 0.83% | 0.1293 |
| `−0.5` | 71.0054% | −5.79% | 0.1212 |
| `−1` | 75.7252% | −12.83% | 0.1137 |

**Residual `58.5%`–`75.7%` for ANY correlation; the floor is `11%`–`15%` of it throughout.** So
**the floor is not the explanation for the tail spread** holds with no independence assumption at
all — which is stronger than earning the assumption would have been.

**And this partially vindicates the sd ratio rather than disqualifying it.** The `ρ=+1` reduction is
exactly `f/T` — `12.8267%`, the reciprocal of the `7.80×` sd ratio, verified to four decimals. **So
the sd ratio is the MAXIMUM-CORRELATION BOUND on the floor's share, not a meaningless quantity.**
"About a seventh" was right as a *bound* and wrong as an *explanatory share*: a value attained only
at perfect correlation, presented as a decomposition. `Do not quote the ratio` was too broad on this
axis — the ratio is disqualified by §2(a)'s cross-key units defect (`central_vector` vs `xsec`),
which is untouched by any of this, and merely **relabelled** by the correlation argument. Two
objections that had been entangled.

**What would overturn the conclusion is a CONJUNCTION, and neither leg is measured:** a `4×`
understated floor (`34.44%`) **and** `ρ ≈ +1` gives residual `32.68%` with `floor/residual = 1.054`
— the only corner of the space where the floor rivals what is left. Either extreme alone leaves it
intact: `4×` at `ρ=0` gives `57.61%`; the measured floor at `ρ=+1` gives `58.51%`.

**Note the direction of the earlier error, because it is the day's species:** the `~2%` quadrature
figure was obtained by choosing the most favourable `ρ`, and `~2%` *sounds* negligible in a way
"a seventh" does not. The honest form is the bracket, not either endpoint.

**A fourth incommensurability axis, from `VL130`'s own row.** The floor vectors carry **259** nonzero
cells — the training artifact's `reported_bin_mask`, `h_prior > 0` on the 2M subsample — while the
`C_stat` family's domain is **257** (all-members-positive within 262). `VL130` states outright that
**"no consumer may take a training artifact's mask as the reporting domain."** The 63 tail cells are
confirmed live on both, so *this* comparison is on a common set — but no general statement of the
form *"the floor is X of the family spread"* is licensed, because it spans two domains that are not
the same and are not claimed to nest.

`VL130` is itself **PROVISIONAL** and shape-only; the normalization axis needs the extraction stage,
which was not authorized.

## Sample: five draws, not four — and never write `n=4` bare

The receipt declares `N=5`; the submitted array is `2-5`; the tail probe used 4. **Three counts,
three different correct values**, which is the reconciliation `BEN-397`/`BEN-400`/`BEN-401` cover:

- `draw_1` is `fullevent_ml_ensemble/member_1`, **reused unmodified, NOT retrained** — bookkeeping
  about the leg, not provenance about the artifact.
- **Its per-cell product EXISTS**, contrary to an intermediate reading: `member_1/pet_fullevent_ml_member1_weights.npz`
  carries `central_vector`, shape `(285,)`, **sum 1.000000, 259 nonzero** — identical in shape,
  normalization and live-cell count to `draw_2`…`draw_5`. The filer opened it and recomputed with it.
- Lane C's criterion decides membership: **population membership is set by the EXECUTION'S
  CONFIGURATION, not by which leg launched it.** `VL130` is `n=5` TERMINAL and
  `probe-oi120a-csyst-k-20260814.py:16` already lists `draw1_member1` as `FILES[0]`, co-equal.
  **The tail probe's `n=4` is the deviation.**
- Its membership rests on an **unevaluated premise** (`BEN-401`): the validity inventory reports
  `draws_valid [1,2,3,4,5]`, `n=5`, while only draws 2–5 carry clauses. Clause `8_execution_environment`
  — **the axis the floor measures** — was never run on draw 1, which is from job `56847059` against
  the others' `56863958`.

**`VL130` is `n=5` of 5, TERMINAL** — the project already includes draw 1 and says so, and records
the per-sd fractional uncertainty as `1/sqrt(2*4)` = **35.36%** (was 40.82% at n=4). An intermediate
reading called `n=4` a "deliberate exclusion of a non-controlled replicate"; **that was invented, not
found, and is withdrawn.** The correct line is simply **`n=5`, per `VL130`**. Where the probe's four
are specifically meant, say so and name the fifth — a reader who sees `N=5` and a statistic on 4
otherwise concludes a draw was dropped.

**The generalisable error:** when an enumeration is refuted, **find the authority — do not author a
better branch.** `VL130` had answered this four days earlier.

## Result: the heterogeneity is real and is not an n-artifact

Per-cell `floor_rel_sd[c] / family_rel_sd[c]` over the 63 tail cells (`ratio > 1.5`, all in p‖ bins
10–15), floor bias-corrected:

| | n=4 (probe) | n=5 (full sample) |
|---|---|---|
| floor median | 9.3440% | **8.7302%** |
| median-of-ratios | 0.1591 | **0.1581** |
| cells > 0.5 | 4 of 63 | **3 of 63** |
| max | 0.9381 | **0.8924** |

Ratio-of-medians at `n=4` is `0.1392` against a median-of-ratios of `0.1591` — **a summary statistic
standing in for a distribution**, which is why the distribution is reported.

**Null test** — all 63 cells share one true ratio, only sampling noise, `s ~ chi_{n-1}/sqrt(n-1)/c4`,
50,000 trials at the correct `n=5` (4 dof), true ratio `0.1581`:

```
cells > 0.5    expected mean 0.00   p95 = 0        P(>= 3 observed)      < 0.0001
cells > 0.25   expected mean 4.12   p95 = 8
max ratio      median 0.304  p95 0.366            P(>= 0.8924 observed) < 0.0001
```

**The homogeneous null is rejected.** The floor's share of local shape-noise genuinely varies across
the tail — it is not manufactured by small-sample noise.

## THE COUNT IS WELL-SUPPORTED. THE LIST IS NOT.

**Winner's curse**: the high cells are selected *because* they are the highest of 63, so their true
ratios regress toward the mean and the `0.8924` cell is where selection bites hardest. This supports
*"the tail is heterogeneous"* and **does not** support *"exclude cells [a,b,c,d]"*. **The list is
exactly what a physics owner reaches for, so this belongs in the sentence, not a footnote.**

## A check that could not have failed, recorded because it favoured the filer

It was observed that **no cell's ratio exceeds 1.0**, and offered as evidence that the floor is a
scale-comparable sub-component — a true sub-component cannot exceed its total. **It is worth exactly
zero.** Under the *commensurable* null, reaching 1.0 from a median of `0.1581` needs a `6.3×`
excursion: `chi_3 > 10.03`, `P(one cell) ≈ 1.15e-21`, `P(any of 63) ≈ 7e-20`. **Both hypotheses
predict zero cells above 1.0**, so the observation separates nothing.

Power curve — the ceiling only becomes informative above a median of about **0.4**:

```
median ratio 0.16 -> P(any of 63 > 1.0) = 0.0000   <- where we are
             0.40 -> 0.0717
             0.60 -> 0.9894
```

**Generalisable form: a bounded statistic evaluated far from its bound carries no information beyond
the location statistic.** All the scale information already lives in the median; the ceiling is the
same datum read through a second statistic, so reporting it double-counts. **Cheap pre-check: compute
the power before reporting a ceiling as a consistency result.**

This is `BEN-391`'s third instance today and a **distinct sub-species**: the two before it were checks
whose *construction* made failure impossible (a domain defined as all-present, queried for
all-present). This one's construction is sound and its **operating point** makes failure impossible.
**Harder to see — nothing in the query looks tautological; you have to compute the power.**

## What this does not touch

It does **not** decompose the family spread, and it does **not** distinguish OI-126's (a) from (b).
The floor bounds GPU nondeterminism; the family's spread is data resampling plus refit noise; and
**(b) was never the claim that the spread is GPU noise** — it is a claim about bootstrap validity, on
which a floor is silent. Lane C's ruling stands: **the floor is not the explanation for the tail
spread**, and that survives every defect above, since even a `4×` understatement leaves the tail
above `57%`.
