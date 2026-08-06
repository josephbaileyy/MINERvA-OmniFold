I worked through the code, the report, the artifact, the source dump, and the six surviving training histories. **CLAIM A is right in functional form and wrong in the number it produces — and the error inverts one of its two consequences. CLAIM B is refuted: the asymmetry is in p∥, not in tilt direction.** Details, with the checks.

---

## 1. CLAIM A: the bound transfers, as an *equality*, and with a different acceptance

### It does transfer — derivation

`RunStep1` pins the non-accepted rows: `new_weights = np.ones_like(...)`, then `new_weights[self.mc.pass_reco] = ...`, then `weights_pull = weights_push * new_weights` (`omnifold_nn/omnifold/omnifold.py:198-200`). Step 2 regresses the pull onto truth (`:218-220`), so in the ideal-classifier limit ν_k(x) = E[ρ_k | gen=x], and because ν_{k-1} is itself a function of gen it factors out:

```
ν_k(x) = a(x)·C_k·t(x) + (1-a(x))·ν_{k-1}(x)
```

With **x-independent** a, C_k ≡ 1 and ν_k − t = (1−a)^k(1−t) pointwise. Since u_k ∝ p·ν_k, the L1 follows exactly:

```
residual = (1-a)^k · gap      ⇒   recovery = 1 - (1-a)^k
```

So the transfer to a spectral L1 is real. But note what it is: **an equality in the ideal limit, not a ceiling.** Framing it as a ceiling let 0.547 read as "68% of the way to a structural limit" when the ideal limit *predicts* 0.804 and the estimator missed it by 0.257. Under the correct reading the same formula makes the result look *worse*, not partly excused.

### The number is wrong, because a(x) is wildly non-constant

Under heterogeneity the aggregate is not `1-(1-ā)^k`. Writing r_b for per-bin recovery and w_b = |q_b−p_b|/gap:

```
recovery = 1 - E_w[|1 - r_b|]        (verified exactly: 0.546853, matches the report)
```

so the prediction is `1 − E_w[(1−a_b)^k]`, and by Jensen the global-a form is only an upper bound. I measured a_b from the dump (`truth_scalars`, `pass_reco`, `pass_truth`, `w_truth`, over the artifact's `dump_rows_b`, weighted as `mcB.pass_reco = s1_b` at `closure_powered_truth_reweight.py:248`):

| p∥ (GeV) | acceptance a_b | ideal 1−(1−a_b)³ | measured r |
|---|---|---|---|
| 0.00–0.75 | **0.003** | 0.008 | 0.208 |
| 0.75–1.50 | **0.012** | 0.034 | 0.202 |
| 3.00–3.50 | 0.396 | 0.599 | 0.551 |
| 4.50–5.00 | 0.603 | 0.859 | 0.826 |
| 5.00–6.00 | 0.655 | 0.905 | 0.906 |
| 7.00–8.00 | 0.693 | 0.930 | 0.953 |

a_b runs 0.003 → 0.81. This is the MINOS match threshold — p∥ < 0.75 GeV means the muon never reaches MINOS — and it is physically correct, not an artifact. **35 bins with a_b < 1% carry 23.2% of the injected displacement mass.**

Running the exact recursion (including C_k and the final renormalization, not just the closed form) per bin:

| k | exact recursion | closed form 1−E_w[(1−a_b)^k] | global-a claim |
|---|---|---|---|
| 1 | 0.426 | 0.438 | 0.419 |
| 2 | 0.572 | 0.576 | 0.662 |
| **3** | **0.635** | 0.633 | **0.804** ← wrong |
| 4 | 0.657 | 0.663 | 0.886 |
| 8 | 0.686 | 0.708 | 0.987 |

**Measured: 0.5469 against an achievable 0.6347.** And the model is confirmed, not fitted: over the 121 bins carrying the top 90% of displacement mass, measured vs predicted per-bin recovery has **Pearson 0.862, Spearman 0.879**, mean 0.712 vs 0.696. In the displacement-weighted signed mean the agreement is 0.63129 vs 0.63296 — 0.3%.

### Verdicts on the two consequences

**(i) survives, for a stronger reason.** niter=2's ideal is 0.572, not 0.662 — further below 0.80. `56355818` could not have passed. Keep it.

**(ii) must be retracted and reversed.** `docs/OPEN_ITEMS.md:221-225` says the bar sits 0.36 pp *under* the ceiling. It sits **16.5 pp above the achievable value.** Reaching 0.80 on this domain needs k of order 100 in the closed form (0.780 at k=50, 0.815 at k=100), more in the exact recursion. The bar was not tight — it was unreachable at any practical k. Same species as the inert-tolerance defect, opposite sign.

That also kills `OPEN_ITEMS.md:233` and CLM-010's "if the cause is too-few iterations, this argues k>3" (`docs/orchestration/CLAIMS.md:21`). k=3→4 buys 0.023. No k fixes this.

---

## 2. CLAIM B: refuted — the cited bins confound tilt direction with p∥

The seven bins in the claim decode as: 242/243/244 → i_pp = 14/15/16 (p∥ 10–40 GeV, a_b ≈ 0.64–0.71); 38/57/76/95 → **all four at i_pp = 0** (p∥ < 0.75 GeV, a_b = 0.003). The quoted 0.72–0.91 vs 0.17–0.24 contrast is the p∥ acceptance gradient read off at two different p∥ values. It is not a measurement of tilt direction.

Marginalizing properly — pT recovery averaged over all 19 p∥ cells, which is the only way to isolate the tilt since the tilt is a function of pT alone:

| pT bin | tilt ratio | ideal | measured |
|---|---|---|---|
| 0–6 (**down**, 0.56–0.80×) | <1 | 0.61–0.65 | **0.65–0.75** |
| 10–13 (**up**, 1.26–2.60×) | >1 | 0.53–0.85 | **0.55–0.71** |

No down-tilt deficit. If anything the sign is **opposite** to the claim: down-tilted pT bins slightly *exceed* their ideal, the up-tilted extremes (pT 12: 0.575 vs 0.737; pT 13: 0.712 vs 0.854) fall short. The pT-8 outlier (−0.467) is the tilt pivot (ratio 0.977, w-mass 0.016) — a ratio of two near-zero numbers, and the main source of the 29 wrong-way bins.

**So there is no under-fitting to chase, and the epochs=8 hypothesis is dead too.** The surviving training histories in `powered_closure/weights.slurm-56381674/` (all six; their `val_loss[0]` match the log lines exactly) show step-2 train loss moving **3.2e-5** across 8 epochs in iteration 2 and 3.0e-5 in iteration 3, with iteration 2's val_loss getting *worse* (0.829560 → 0.829612, best at epoch 1). That is a fit with no remaining gradient signal, not one starved of steps. Combined with measured ≈ pointwise-ideal in every well-accepted p∥ bin, the fit is fine where information exists.

Two related notes. `omnifold.py:303` logs `hist.history['val_loss'][0]` under the label **"Last val loss"** — it prints epoch 1. Anyone judging convergence from the log is reading the first epoch; that is plausibly how the under-fitting hypothesis formed without the pickles being opened. And `ModelCheckpoint(save_best_only=True)` (`:272-275`) saves best-val-loss weights while `reweight` uses the last-epoch in-memory model — so on-disk checkpoints are not bit-identical to what the run used.

What *is* unexplained: per-bin scatter, rms 0.212 about the ideal curve. It costs 0.084 of the aggregate through the absolute value (9.3% of residual/gap is overshoot, r>1 bins; E_w[r] = 0.631 vs aggregate 0.547). That, not bias, is the whole remaining gap to 0.635. It is a variance question, so it needs an ensemble, not a longer run.

---

## 3. Next steps, in order

**0 — free, today. Retract and record.** Fix `OPEN_ITEMS.md:213,221-225,233` and CLM-010's caveat (i)/(ii): 0.6347 replaces 0.80364, consequence (ii) reverses. Commit the per-bin acceptance map as a tracked product — it is the most reusable number produced today and it is derivable from the dump in ~20 lines.

**1 — free. Confirm with the checkpoints before spending any GPU.** Recompute recovery at k=1,2,3 by inference only from `OmniFold_fe_powered_iter{0,1,2}_step2.weights.h5`. Push weights are not cumulative (`omnifold.py:220`), so each checkpoint alone gives ν_k. Predicted 0.426 / 0.572 / 0.635. Calibrate on k=3 first (expect near-0.547, not exact, per the checkpoint caveat above). This closes the acceptance model end-to-end for minutes of GPU.

**2 — the criterion, predeclared, before the next run.** Do not lower 0.80. Add the soundness assertion the B1 tolerance got (`FINDING-20260806-...md:117-119`, prescription 8): the gate must **fail closed if the bar is not below the ideal computed from the acceptance map at the frozen k**. That converts an unachievable absolute bar into a criterion with power. My recommendation for the primary criterion is `recovery / ideal_recovery(a_b, k) ≥ θ` on the full declared domain — dimensionless, no phase-space cherry-picking, and it fails when the estimator underperforms its own limit. **Derive θ from the measured noise floor, not from today's 0.862**, or you have tuned on the result. That requires step 3 first. Note `residual_over_gap_max` lives in `FROZEN` at `validate_pet_nominal_gate4.py:115`, so this is a Gate-4 re-issue.

**3 — the one real GPU spend: a seed ensemble, not a longer run.** 8 estimator seeds of the powered closure at k=3 (2h each, embarrassingly parallel in `shared_gpu`). This measures whether the 0.212 per-bin scatter averages down — if it does, the criterion belongs on the ensemble mean and θ follows from the ensemble; if it doesn't, it is bias and needs a separate explanation. Running 8 more at k=4 also discharges item (e)'s genuinely-owed #1 (per-bin spread vs k). Needs an `--estimator-seed` override, which trips `EXPECTED_DRIVER_SHA` in `sbatch_powered_closure.sh` — a launcher constant update, not a gate re-issue.

**4 — demote the k=4 B1 arms.** `56400517` and `56400519` are both PENDING (reason Priority, 4 h, QOS `gpu_shared`, partition `shared_gpu`; checked 15:02Z). Don't cancel — they're queued and they still close item (e) #2 on the scalar. But they are **not** load-bearing, contrary to `OPEN_ITEMS.md:233`: the differential gain k=3→4 is 0.023 and saturates by k=8.

**5 — (d) unchanged in priority, with one addition.** The low-p∥ region is prior-dominated, so its covariance is a *prior/model* uncertainty and cannot be estimated from unfolded spread alone. Fold that into the J28 joint plan.

---

## 4. What I think everyone has missed

**The test grades the wrong thing, and a PASS would be bad news.**

The injection is a function of truth pT only. The acceptance gradient is almost entirely in p∥. Those are orthogonal — so an estimator that pools across p∥ scores well on this closure whether or not the pooling is justified. And the PET net *is* pooling: it recovers 0.208 in cells where the detector sees 0.3% of events, ~25× the pointwise-optimal 0.008. Getting from 0.635 to 0.80 requires *more* of exactly that extrapolation into near-zero-efficiency cells — which `OPEN_ITEMS.md` item 6 already declares must not be trusted ("cannot create detector information in zero-efficiency cells").

So the FAIL is arguably the correct outcome for a correctly-behaving estimator, and a future PASS on this criterion should be treated as suspicious rather than reassuring. **The test that has the power you actually want is a second injection with p∥ dependence** — that breaks the degeneracy between "recovered the tilt" and "smoothed across the unmeasured region." One 2 h run, plus a predeclared protocol.

**And the publication-level fact underneath it: 21.1% of the declared fiducial truth population sits at p∥ < 1.5 GeV with 0.3–1.2% reco acceptance.** `KNOWN_ISSUES.md:17` (#5) records a *data/MC ratio* gradient in exactly this region and says it "matters more for FPS (p∥<1.5 region)" — but the absolute acceptance is nowhere in the repo that I could find. Two independent problems land on the same fifth of phase space and the campaign is tracking only one.

On your worry about convergence: it was real here. All three prior readings shared the framing "the estimator under-performed, find the mechanism." Nobody computed a(x). The convergence was on a framing, and the framing was the error.

---

## 5. Errors in your summary

1. **"median per-bin recovery is 0.84"** — 0.8233. (`OPEN_ITEMS.md` has it right; the prompt rounded up.)
2. **CLAIM A's ceilings** are arithmetically correct for the formula but use the global acceptance where the displacement-weighted heterogeneous one is required. Corrected: k=1 0.426, k=2 0.572, k=3 **0.635**, k=4 0.657.
3. **Consequence (ii) is backwards**, not merely unproven — see above.
4. **CLAIM B's bins are confounded** — all four "down" bins at i_pp=0, all three "up" bins at i_pp=14–16.
5. **"the aggregate is dominated by large-displacement bins that recover worst"** — half the story. The other half is the absolute value: overshoot bins (r>1) contribute 9.3% of residual/gap. E_w[r] = 0.631 vs aggregate 0.547; the signed mean hides it.
6. Everything else reproduced: gap 0.234270, floor 0.010747, residual 0.106159, floor/gap 0.045876, residual/gap 0.453147, `recovery == 1 − residual/gap` exactly (bit-for-bit), 89% right-direction (1 − 29/262 = 0.8893), top-10/20/50 at 26.5/44.8/75.1%, tilt range 0.5487–2.6540, a = 837494/1999920 = 0.418764, 0.546853/0.80364 = 68%, and 0.5469 does sit between the k=1 and k=2 *global-a* values. Your refutation of the logit cap also holds — zero saturation is consistent with `REWEIGHT_LOGIT_CAP` at `omnifold.py:41` spanning 1e±13.

I wrote nothing, staged nothing, submitted nothing. The acceptance-map computation is reproducible from the committed report plus the on-scratch artifact and the source NPZ; if you want it as a tracked product I can hand you the script rather than run it.
