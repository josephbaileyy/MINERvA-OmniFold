# FINDING 2026-08-06 — should the PET nominal move to `niter=4`? Measured answer: **not now**

*Joseph asked directly ("What do you think about moving the PET nominal to niter=4? If you think its a
good idea, do it"). The answer is **no, not now** — and the reason is not caution, it is that the thing
`k=4` would plausibly buy is measurably not on offer. Everything below is measured this turn from
committed products, not predicted.*

Owning items: `CLAIMS.md` CLM-010 (this discharges its open item **(ii)**); `OPEN_ITEMS.md` (e);
`FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md` (the 2→3 switch).

## 1. The bias-variance case for `k=4` is real and now measured

The k=4 B1 rate-injection arm **ran and completed** — jobs `56400517` (16 seeds, 1h34m) and `56400519`
(32 seeds, 3h16m), both `COMPLETED 0:0`. Pooling to 48 seeds per arm, from
`products/pet/b1_closure/closure_b1_rate_injection_scan{16,32}_measured_N240k_niter4*.json`:

| k | n | mean `dev_from_R` | sd | closed form `(1-a)^k (R-1)/R` | realized exceedance @ tol 0.05 |
|---|---|---|---|---|---|
| 2 | 48 | 0.038008 | 0.008153 | 0.037318 | **6/48** |
| 3 | 48 | 0.021876 | 0.008444 | 0.021698 | 0/48 |
| 4 | 48 | **0.014256** | **0.008023** | 0.012616 | 0/48 |

**Paired on all 48 shared seeds** (the design is paired — BEN-025's instrument lesson): mean change
`−0.007620`, se `0.000915`, `t = −8.33`, 95% CI **[−0.009413, −0.005827]**, which excludes 0. Bias falls
by **1.535×** and the **sd ratio is 0.9502** — variance did not grow, it fell slightly.

So `k=4` is genuinely better on bias at flat variance. That is a measured improvement. It is not,
however, a measured *requirement*, and the rest of this finding is why that distinction decides it.

One caution: the closed form **starts under-predicting** at k=4 — measured 0.014256 against 0.012616
(+13%), where k=3 agreed to 0.018 pp. The clean asymptotic story is beginning to degrade, which argues
against extrapolating to larger k without measuring.

## 2. The decisive point: `k=4` does **not** fix the powered closure, and nothing does

The real blocker is the D2 powered closure, `FAIL` at `niter=3` (job `56381674`, recovery 0.5469 against
a predeclared 0.80). If `k=4` moved that to PASS it would be worth almost any cost. It does not.

`closure_powered_truth_reweight.py:280` defines
`recovery = 1 − L1(h_unfold, h_target) / L1(h_prior, h_target)`, and `:28` states the injection is
**rate-preserving**. So it is a per-bin **shape** criterion, which fixes the right ceiling: under
acceptance dilution `ν_b = (1-(1-a_b)^k) t_b + (1-a_b)^k p_b`, so `|ν_b − t_b| = (1-a_b)^k |p_b − t_b|`
and therefore

    residual(k) = Σ_b (1-a_b)^k · |p_b − t_b|,     recovery(k) = 1 − residual(k)/gap

weighted by the **injected tilt** `|p_b − t_b|` — not by truth mass, and not evaluated at the global
acceptance.

**The model is anchored, not assumed.** Recomputing `gap` from the report's own `h_prior`/`h_target`
gives 0.234270 against the report's 0.234270, confirming the acceptance map and the closure report cover
the same 285 cells. And it is **validated as an upper bound**: at k=3 it predicts residual 0.085929
against the measured 0.106159, i.e. the trained estimator does **19.1% worse** than the ideal ceiling,
which is the direction it must err.

| k | ideal residual | **ideal recovery** | vs the 0.80 bar |
|---|---|---|---|
| 2 | 0.099358 | 0.5759 | fails |
| 3 | 0.085929 | 0.6332 | fails (measured: 0.5469) |
| 4 | 0.078976 | **0.6629** | **still fails** |
| 5 | 0.074772 | 0.6808 | fails |
| 6 | 0.071941 | 0.6929 | fails |

**No `k ≤ 39` reaches 0.80 under this model**, and the measured value sits ~19% below the ideal. So the
0.80 bar is unreachable at any practical iteration count: `k=4` buys **2.97 pp** of ideal recovery
against a **~19 pp** gap. This is now a validated statement rather than the estimate recorded earlier,
and it strengthens the existing conclusion that **the criterion needs redesign**, not more iterations.

## 3. What `k=4` would cost

- **The queue position.** `56415634` is `PENDING` with **10h14m** queued at priority 67871. Switching
  means cancelling it and starting over.
- **The whole pin cascade, again.** The 2→3 switch required a Gate-4 re-issue, `validate_pet_nominal_gate4`
  `FROZEN["seed_policy"]`, `train_fullevent_nominal.NOMINAL_SEED_POLICY`, and three test files. All of it
  repeats for 3→4.
- **Wall time.** The 12 h wall was sized for k=3; k=4 is ~33% more training.
- **The literature default is 3** (`LITERATURE_NOTES.md:65`). Deviating is defensible only with a stated
  reason, and a measured improvement that nothing needs is a weak one.

## 4. Decision, and the condition that would change it

**Do not switch now.** At `k=3` the fold-forward bias is 2.19% against a 5% tolerance with **0/48**
realized exceedance — a 2.3× margin. `k=4` takes that to 1.43%. Nothing in the campaign currently
requires the difference, and the one thing that would justify the disruption (rescuing the powered
closure) is measurably out of reach at every `k`.

**Adopt `k=4` opportunistically instead.** If a re-train happens for any other reason — most likely the
powered-closure criterion redesign — do it at `k=4` then. The marginal cost is ~33% of one training
rather than a cascade plus a lost queue position, and §1 shows the bias-variance trade is favourable.

**This discharges CLM-010 item (ii)**, which required that if the k=4 spread were also flat, "the record
must state the stopping point is set by cost and the literature default of 3, NOT chosen by measurement."
The spread *is* flat (sd ratio 0.9502). So the record now states exactly that: **`k=3` is chosen by cost
and convention, not by measurement — measurement prefers `k=4` and is overridden deliberately.**

## 5. A Jensen bug this exposed in my own product

`acceptance_map_fullevent_fps.py:155` computed `ideal_recovery_global_by_k` as `1-(1-a)^k` at the
**global** acceptance. Because `1-(1-a)^k` is concave, that **overstates** achievable differential
recovery by **+19.9 pp at k=3** (0.8084 vs 0.6095 truth-mass-weighted per cell). The published value read
**0.8084 at k=3** — essentially exactly the 0.80 bar — so a reader would conclude the bar was achievable
and the estimator broken, the precise opposite of §2.

Fixed by renaming rather than deleting (it shipped in v1 and a reader needs to know what they read):
`ideal_recovery_from_global_acceptance_by_k__OVERSTATES_DIFFERENTIAL`, plus a new per-cell curve
`ideal_recovery_percell_truthmass_weighted_by_k`, and a `corrected_20260806` note in the product. The
per-cell field is flagged as a **reference curve, not the closure's ceiling**, because the closure's
weight is the injected tilt (§2) — recording it without that caveat would swap one wrong ceiling for
another. Third instance of this error class on this campaign after the CLM-011 magnitudes
(cell-by-cell 122.6× vs aggregate 2.36×); logged as such.
