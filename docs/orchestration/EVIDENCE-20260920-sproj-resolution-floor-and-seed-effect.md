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
