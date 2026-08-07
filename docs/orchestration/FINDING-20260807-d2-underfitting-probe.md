# FINDING 2026-08-07 — the D2 recovery shortfall is 97.8% per-bin SCATTER, and the under-fitting probe measures the right thing only if it is read on that axis

> **POINTER ADDED 2026-08-07 by the orchestrating session — `FINDING-20260807-d2-response-reference-point.md`
> (BEN-041).** §3's split reproduces exactly (`E_w[r] = 0.63129`, penalty `0.08443`, 262 live / 87
> overshooting bins, all gated). Two amendments, neither touching a number here: the **97.8% is measured
> against the dilution ideal**, and against the 0.80 bar's own reference the miss is **81.4% coherent
> under-application** with dispersion the minority term; and **the scatter penalty is not a dispersion
> measure** — reading §6's ladder through it reports a 68.3% collapse ep8→ep16 where the actual spread
> (a weighted MAD) moved 5.5%, because the penalty tracks how many cells straddle `r = 1`. §6's arms landed
> and are analysed there; the ladder moved the coherent term, not the scatter term.

**Status as of 2026-08-07.** §1–§5 are measured from committed products at zero GPU cost and are final.
§6 is the probe: three arms submitted, reading predeclared in code before any arm reported. §7 is
empty until they land and must not be filled in by inference.

**Read §1 first.** The task that produced this file was "test the under-fitting hypothesis, neither
session tested it" (`HANDOFF-20260806-2246Z.md` §4). That instruction was **stale**:
`docs/OPEN_ITEMS.md` (a) had already measured it false. What is genuinely new here is §3's
bias/scatter split of the *criterion itself*, §4, and the fact that the probe is now read on the
scatter axis rather than the aggregate — which is what stops it confirming the wrong thing.

Owning items: `docs/OPEN_ITEMS.md` (a); `CLAIMS.md` CLM-010 (i). Agent-process lesson: BEN-037.

---

## 1. Prior art, and the correction to the instruction that produced this file

`docs/OPEN_ITEMS.md` (a) already contains, from 2026-08-06:

- **"(ii) `epochs=8` optimization-limited: measured false."** From the same six history pickles, with
  the same conclusion — a fit with no remaining gradient signal, not one starved of steps.
- The **retraction of the tilt-direction structure** as confounded with `p_parallel`, including the
  marginalisation that isolates a pT-only tilt. So the handoff's §2.1 "asymmetric in tilt direction"
  was *already* superseded when the handoff repeated it.
- The **per-bin acceptance model**, `1-(1-a_b)^k` per cell with the exact recursion, giving k=3
  ≈ 0.635, the `a_b ∈ [0.003, 0.81]` range, the MINOS-threshold explanation, and the census that
  **cells with `a_b < 1%` carry 23.2% of the injected displacement**.
- The **scatter diagnosis**: `E_w[r] = 0.631` against an aggregate of `0.547`, rms 0.212 about the
  ideal curve, "a **variance** question, so it needs a **seed ensemble**, not a longer run."

Everything I recomputed agrees with it, including `E_w[r] = 0.63129` to five decimals. **This finding
does not claim any of that.** It is recorded here because a session routed through the handoff alone
would re-derive it — and would have spent ~14 GPU-hours confirming a null the repo had already
written down. That divergence is the real process failure and is filed as BEN-037.

---

## 2. The ceiling reproduces exactly, from committed products

`residual(k) = Σ_b (1−a_b)^k |p_b − t_b|` over `acceptance_map_fullevent_fps.json`'s
`acceptance_cells_pt_major` and `56381674`'s own spectra (bin orders checked equal; 285 cells both
sides): **0.575885 / 0.633208 / 0.662886** at k=2/3/4, matching
`FINDING-20260806-niter4-decision.md`. `gap`, `floor`, `residual` and `recovery` reproduce to 1e−9
against the report's metrics block. So `gap_to_ceiling = 0.633208 − 0.546853 = **0.086354**` is the
live quantity, and 0.80 is not.

---

## 3. THE RESULT: the shortfall is scatter, not bias — 97.8% of it

The closure's metric is an L1, and **an absolute value turns symmetric per-cell noise into a one-sided
penalty**. Splitting it, with `r_b = (u_b − p_b)/(t_b − p_b)` and weights `w_b = |t_b − p_b|`:

| quantity | value |
|---|---|
| aggregate L1 recovery `1 − E_w[\|1−r\|]` | 0.54685 |
| **signed mean response** `E_w[r]` | **0.63129** |
| dilution ideal `E_w[1−(1−a_b)^k]` | **0.63321** |
| bias vs ideal | **−0.00192** |
| **scatter penalty** `E_w[\|1−r\|] − \|1−E_w[r]\|` | **0.08443** |
| weighted rms of `r − r_ideal` | 0.32239 |
| overshoot bins (`r > 1`) | **87 of 262**, carrying 24.1% of displacement |

**The estimator's mean per-bin response already matches the ideal to 0.19 pp, and the scatter penalty
(0.08443) is 97.8% of the entire 0.086354 distance to the ceiling.** There is essentially no bias left
to remove. The powered closure is, as currently defined, a **per-cell variance** measurement wearing
the clothes of a bias measurement.

Decomposed by per-cell acceptance — and note this is where my own first draft went wrong, by reading
the L1 column as undershoot when the signed column says otherwise:

| a_b band | cells | share | signed `E_w[r]` | ideal | **bias** | rms(r−ideal) | L1 recovery |
|---|---|---|---|---|---|---|---|
| [0.00, 0.01) | 34 | 0.2316 | 0.1525 | 0.0082 | **+0.1443** | 0.1845 | 0.1525 |
| [0.01, 0.10) | 13 | 0.0636 | 0.2840 | 0.0981 | **+0.1859** | 0.2192 | 0.2840 |
| [0.10, 0.30) | 12 | 0.0746 | 0.3603 | 0.4933 | −0.1330 | 0.1888 | 0.3603 |
| [0.30, 0.50) | 19 | 0.1252 | 0.5340 | 0.7845 | **−0.2505** | 0.3902 | 0.5230 |
| [0.50, 0.70) | 32 | 0.1922 | 0.8376 | 0.9378 | −0.1002 | 0.4048 | 0.7108 |
| [0.70, 1.01) | 152 | 0.3127 | 1.0333 | 0.9905 | +0.0428 | 0.3566 | 0.8456 |
| **pooled a_b ≥ 0.50** | **184** | **0.5050** | **0.9588** | **0.9704** | **−0.0116** | **0.3757** | **0.7943** |

Two things to take from it, and one trap.

**(a) The high-acceptance half is not undershooting.** Cells with `a_b ≥ 0.50` carry half the injected
displacement and their signed bias is **−0.0116** — essentially none — while their rms scatter is
0.3757 and their L1 recovery reads 0.7943 against a 0.9704 ceiling. The gap in the L1 column there is
**entirely** the absolute value eating scatter. The top band (`a_b ≥ 0.70`) actually **overshoots** on
average (`E_w[r] = 1.0333`). *An earlier draft of this file read the L1 column as "the estimator
undershoots where the information is present" and that was wrong; it is recorded because the L1 column
is exactly what an unwary reader will look at.*

**(b) The one real bias is transport, and it shows the ceiling is not a bound.** Cells with
`a_b < 0.01` reach a signed response of **+0.1525** against an independence ideal of **0.0082** — 19×.
That is the smooth-transport effect (`omnifold.py:218-220` evaluates the truth classifier on all
`pass_gen` rows while the injection is smooth in pT and the acceptance gradient lives on p∥),
**observed, not hypothesised**. Their per-cell sampling floor is 0.00212 against a residual of 0.04599,
so it is not noise. **Consequently 0.6332 is a reference curve and must not be quoted as proof of
impossibility.** The genuinely biased band is `[0.30, 0.50)` at −0.2505.

---

## 4. Saturation and global shrinkage are ruled out, free, from the push weights

`POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz` carries all 2,000,000 `weights_push`: finite, spanning
**[0.562076, 2.832002]**, mean 1.066147, largest implied logit **1.041** against
`REWEIGHT_LOGIT_CAP = 30.0`. **Zero rows are near saturation.** And the injection asks for weights
spanning **[0.548710, 2.653992]** (the coordinate clip binds only on the low side, `z ∈ [−3.00,
+1.50]`), which the push distribution covers and slightly exceeds. So the estimator produces weights
of the **correct dynamic range** and misallocates them per cell — consistent with §3's scatter
diagnosis, and inconsistent with both a clipped and a globally under-responding estimator. Stated as
the marginal-distribution argument it is: it excludes two failure modes, it does not establish the
per-row correlation with the true tilt.

---

## 5. What the histories say, extending the record rather than repeating it

All six of `56381674`'s Keras histories (`KNOWN_ISSUES.md` §"Last val loss" already records iterations
2–3; this is the full set):

| training | train loss e1 → e8 | Δ | val argmin (of 8) | val spread |
|---|---|---|---|---|
| iter0 step1 | 0.482886 → 0.481757 | −1.13e−3 | 5th | 3.51e−4 |
| iter0 step2 | 0.827370 → 0.826934 | −4.36e−4 | 5th | 3.57e−4 |
| iter1 step1 | 0.475559 → 0.475467 | −9.2e−5 | 7th | 1.63e−4 |
| iter1 step2 | 0.829577 → 0.829545 | −3.2e−5 | **1st** | 2.44e−4 |
| iter2 step1 | 0.486674 → 0.486597 | −7.7e−5 | 6th | 2.27e−4 |
| iter2 step2 | 0.844740 → 0.844710 | −3.0e−5 | 5th | 2.67e−4 |

The plateau is a property of the **whole run**, not of iteration 2. Two mechanical consequences, both
verified against the installed Keras 2.15 rather than assumed: `EarlyStopping(patience=10,
restore_best_weights=True)` **cannot fire** inside 8 epochs, and Keras restores best weights **only**
inside the `wait >= patience` stop branch (`on_train_end` merely prints) — so every run on this
campaign has used **last-epoch** weights. `ReduceLROnPlateau` sits at `patience=1000`
(`omnifold.py:263-265`) and `get_optimizer` returns a bare Adam at a flat LR (`:376-380`, `num_steps`
accepted and unused), so no schedule ever engages. "More budget" in this engine means strictly more
steps at 1e−4.

**Why a converged loss is still not the end of the argument.** A plateau in a *classifier's* BCE is
compatible with the *reweighting function* still moving: per-event discrimination here is nearly
impossible, the loss is dominated by irreducible noise, and a 3e−5 loss change can carry a meaningful
change in the learned ratio. `OPEN_ITEMS.md` (a)'s refutation is an inference from that plateau. The
probe converts it into a direct measurement — which is the only thing §6 adds to the record, and it
is worth ~14 GPU-hours precisely because the conclusion is load-bearing for redesigning a gate
criterion.

---

## 6. The probe: three arms, read on the scatter axis

Sized from the run being sized (BEN-030), off `weights.slurm-56381674/*.pkl` mtimes: **2.00 min/epoch**
step 1, **2.79 min/epoch** step 2, so one epoch across all `niter=3 × 2` trainings costs **14.4 min**,
and 8 epochs → 115 min reproduces the job's measured 1h58m with ~5 min of load and hashing.

| arm | job | budget | est. | wall |
|---|---|---|---|---|
| `ctl8` | 56431649 | epochs=8, engine-default `early_stop` | ~2h | 4h |
| `ep16` | 56431650 | epochs=16, `early_stop=1000` | ~4h | 7h |
| `ep32` | 56431651 | epochs=32, `early_stop=1000` | ~8h | 11h |

`ctl8` re-runs the baseline configuration exactly: it measures the run-to-run scale (op determinism is
**not** enabled, and no spread has ever been published for this closure), independently reproduces
0.546853, and doubles as the regression test for the `--epochs` flag — 8 *is* the policy value, so a
correct implementation must stamp `is_nominal_configuration: true` and an empty
`configuration_overrides`. A three-point **ladder under one selection rule** gives a trend;
`early_stop=1000` on the probe arms guarantees the full budget is actually spent.

**No fourth "early stopping finally works" arm**, having nearly built one: Keras restores best weights
only in the stop branch (§5), so with this flat noisy val curve the callback most likely never fires
and the arm silently becomes a redundant copy of `ep32` for ~8 GPU-hours — and the question is
answerable free from `ep32`'s own histories.

**Predeclared reading**, in `analyze_powered_closure_budget_probe.py:PREDECLARED`, committed before any
arm reported (all three were `PENDING` when it was written; `git log` against their `Submit` timestamps
is the check):

- **The scatter penalty is the primary target**, because §3 shows it *is* the shortfall. CONFIRMED
  requires the aggregate to close ≥50% of `gap_to_ceiling`, the move to exceed 3× the control's own
  displacement, **and** the scatter penalty to fall by ≥50%.
- An aggregate rise with a flat scatter penalty returns the distinct verdict
  **`AGGREGATE_MOVED_BUT_NOT_VIA_SCATTER`** rather than confirmation. This is not hypothetical: a
  synthetic bias-shift arm used to unit-test the rule triggers exactly that branch, where the
  aggregate-only rule called it CONFIRMED.
- REFUTED at ≤10% of `gap_to_ceiling`, or inside the run-to-run scale. AMBIGUOUS otherwise, reported
  as such.
- The control is **one pair**, so it is a scale and **not a sigma**; the 3× factor is crude on purpose
  (BEN-025).

**No threshold is touched.** `recovery_min = 0.80` is unchanged, is not a target, and is not evaluated
by the analyzer.

---

## 7. What this probe cannot settle, and what OPEN_ITEMS says to do next

It varies **steps at a fixed learning rate**, nothing else. It cannot separate "needs more
optimization" from "needs a different optimization" (a schedule that engages, a warmup), and it cannot
address capacity — the PET is pinned at `num_transformer=2, num_heads=2, projection_dim=32`
(`closure_powered_truth_reweight.py:261-264`). A null licenses "more of the same training does not
help", **not** "no estimator can do better".

And per §3 the residual is a **variance** quantity, so `OPEN_ITEMS.md` (a) is right that the
instrument it most needs is a **seed ensemble** at the nominal configuration — which this probe is
not. The driver still reads `estimator_seed` from the policy with no override, so that ensemble needs
one more flag (`--estimator-seed`) before it can be run; deliberately not added in this commit,
because the three arms already queued pin the driver's sha at submission and editing it now would
kill them. **Recommended next step once the ladder lands.**

---

## 8. Results

*(empty by design until the arms land)*
